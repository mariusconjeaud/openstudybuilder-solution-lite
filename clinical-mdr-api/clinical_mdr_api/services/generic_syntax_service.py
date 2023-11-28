import abc
from datetime import datetime
from typing import Generic, TypeVar

from neomodel import db
from pydantic import BaseModel

from clinical_mdr_api.domain_repositories._generic_repository_interface import (
    GenericRepository,
)
from clinical_mdr_api.domain_repositories.study_definitions.study_definition_repository import (
    StudyDefinitionRepository,
)
from clinical_mdr_api.domains.controlled_terminologies.ct_term_attributes import (
    CTTermAttributesAR,
)
from clinical_mdr_api.domains.controlled_terminologies.ct_term_name import CTTermNameAR
from clinical_mdr_api.domains.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domains.syntax_templates.template import TemplateVO
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemStatus,
    VersioningException,
)
from clinical_mdr_api.exceptions import (
    BusinessLogicException,
    ConflictErrorException,
    NotFoundException,
)
from clinical_mdr_api.models.controlled_terminologies.ct_term import (
    CTTermNameAndAttributes,
)
from clinical_mdr_api.models.dictionaries.dictionary_term import DictionaryTerm
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services._utils import (
    calculate_diffs,
    raise_404_if_none,
    service_level_generic_header_filtering,
)

_AggregateRootType = TypeVar("_AggregateRootType")


class GenericSyntaxService(Generic[_AggregateRootType], abc.ABC):
    @abc.abstractmethod
    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: _AggregateRootType
    ) -> BaseModel:
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, template: BaseModel) -> BaseModel:
        raise NotImplementedError

    @abc.abstractmethod
    def edit_draft(self, uid: str, template: BaseModel) -> BaseModel:
        raise NotImplementedError

    aggregate_class: type
    version_class: type
    repository_interface: type
    _repos: MetaRepository
    user_initials: str | None
    root_node_class: type

    def __init__(self, user: str | None = None):
        self.user_initials = user if user is not None else "TODO Initials"
        self._repos = MetaRepository()

    def __del__(self):
        self._repos.close()

    @property
    def repository(self) -> GenericRepository[_AggregateRootType]:
        assert self._repos is not None
        return self.repository_interface()

    @property
    def study_repository(self) -> StudyDefinitionRepository:
        return self._repos.study_definition_repository

    def get_by_uid(
        self,
        uid: str,
        return_instantiation_counts: bool = False,
        return_study_count: bool | None = True,
    ) -> BaseModel:
        item = self._find_by_uid_or_raise_not_found(
            uid,
            return_study_count=return_study_count,
            return_instantiation_counts=return_instantiation_counts,
        )
        return self._transform_aggregate_root_to_pydantic_model(item)

    @db.transaction
    def get_specific_version(
        self, uid: str, version: str, return_study_count: bool | None = True
    ) -> BaseModel:
        item = self._find_by_uid_or_raise_not_found(
            uid, return_study_count=return_study_count, version=version
        )
        return self._transform_aggregate_root_to_pydantic_model(item)

    def _find_by_uid_or_raise_not_found(
        self,
        uid: str,
        *,
        version: str | None = None,
        at_specific_date: datetime | None = None,
        status: LibraryItemStatus | None = None,
        for_update: bool = False,
        return_instantiation_counts: bool = False,
        return_study_count: bool | None = True,
    ) -> _AggregateRootType:
        item = self.repository.find_by_uid_2(
            uid,
            for_update=for_update,
            at_specific_date=at_specific_date,
            version=version,
            status=status,
            return_study_count=return_study_count,
            return_instantiation_counts=return_instantiation_counts,
        )
        if item is None:
            raise NotFoundException(
                f"{self.aggregate_class.__name__} with uid {uid} does not exist or there's no version with requested status or version number."
            )
        return item

    @db.transaction
    def retrieve_audit_trail(
        self,
        page_number: int = 1,
        page_size: int = 0,
        total_count: bool = False,
    ) -> GenericFilteringReturn[BaseModel]:
        ars, total = self.repository.retrieve_audit_trail(
            page_number=page_number,
            page_size=page_size,
            total_count=total_count,
        )

        all_items = [self._transform_aggregate_root_to_pydantic_model(ar) for ar in ars]

        return GenericFilteringReturn.create(items=all_items, total=total)

    @db.transaction
    def get_all(
        self, status: str | None = None, return_study_count: bool | None = True
    ) -> list[BaseModel]:
        if status is not None:
            all_items = self.repository.find_all(
                status=LibraryItemStatus(status), return_study_count=return_study_count
            )
        else:
            all_items = self.repository.find_all(return_study_count=return_study_count)

        # Transform the items into the model expected by pydantic
        return [
            self._transform_aggregate_root_to_pydantic_model(item) for item in all_items
        ]

    def get_distinct_values_for_header(
        self,
        field_name: str,
        status: str | None = None,
        search_string: str | None = "",
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        result_count: int = 10,
    ):
        all_items = self.get_all(status=status, return_study_count=False)

        # Do filtering, sorting, pagination and count
        header_values = service_level_generic_header_filtering(
            items=all_items.items,
            field_name=field_name,
            search_string=search_string,
            filter_by=filter_by,
            filter_operator=filter_operator,
            result_count=result_count,
        )
        # Return values for field_name
        return header_values

    def _parameter_name_exists(self, parameter_name: str) -> bool:
        return self._repos.parameter_repository.parameter_name_exists(parameter_name)

    @db.transaction
    def approve(self, uid: str) -> BaseModel:
        try:
            item = self._find_by_uid_or_raise_not_found(uid, for_update=True)
            uses = self.repository.check_usage_count(uid)
            if uses > 0:
                raise ConflictErrorException(
                    f"Template '{item.name}' is used in {uses} instantiations."
                )
            item.approve(author=self.user_initials)
            self.repository.save(item)

            return self._transform_aggregate_root_to_pydantic_model(item)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e

    @db.transaction
    def create_new_version(self, uid: str, template: BaseModel) -> BaseModel:
        try:
            template_vo = TemplateVO.from_input_values_2(
                template_name=template.name,
                parameter_name_exists_callback=self._parameter_name_exists,
            )
            item = self._find_by_uid_or_raise_not_found(uid, for_update=True)

            item.create_new_version(
                author=self.user_initials,
                change_description=template.change_description,
                template=template_vo,
            )
            self.repository.save(item)
            return self._transform_aggregate_root_to_pydantic_model(item)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e

    @db.transaction
    def inactivate_final(self, uid: str) -> BaseModel:
        item = self._find_by_uid_or_raise_not_found(uid, for_update=True)

        try:
            item.inactivate(author=self.user_initials)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e

        self.repository.save(item)
        return self._transform_aggregate_root_to_pydantic_model(item)

    @db.transaction
    def reactivate_retired(self, uid: str) -> BaseModel:
        item = self._find_by_uid_or_raise_not_found(uid, for_update=True)

        try:
            item.reactivate(author=self.user_initials)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e

        self.repository.save(item)
        return self._transform_aggregate_root_to_pydantic_model(item)

    @db.transaction
    def get_version_history(
        self, uid: str, return_study_count: bool | None = True
    ) -> list[BaseModel]:
        if self.version_class is not None:
            all_versions = self.repository.get_all_versions_2(
                uid, return_study_count=return_study_count
            )
            versions = [
                self._transform_aggregate_root_to_pydantic_model(_).dict()
                for _ in all_versions
            ]

            return calculate_diffs(versions, self.version_class)

        return []

    @db.transaction
    def get_releases(
        self, uid: str, return_study_count: bool | None = True
    ) -> list[BaseModel]:
        releases = self.repository.find_releases(
            uid=uid, return_study_count=return_study_count
        )
        return [
            self._transform_aggregate_root_to_pydantic_model(item) for item in releases
        ]

    @db.transaction
    def soft_delete(self, uid: str) -> None:
        try:
            item = self._find_by_uid_or_raise_not_found(uid, for_update=True)
            item.soft_delete()
            self.repository.save(item)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e

    def _set_default_parameter_terms(self, item: BaseModel) -> BaseModel:
        """
        This method fetches and sets the default parameter terms for a template.
        This method can be template-specific and must be implemented in the template service.
        """
        raise NotImplementedError(
            "Default parameter terms handler is not implemented for this service."
        )

    def _set_indexings(self, item: BaseModel) -> None:
        """
        This method fetches and sets the indexing properties to a template.
        """
        if not hasattr(item, "uid"):
            return

        # Get indications
        indications = (
            self._repos.dictionary_term_generic_repository.get_syntax_indications(
                self.root_node_class, item.uid
            )
        )
        if indications and hasattr(item, "indications"):
            item.indications = sorted(
                [
                    DictionaryTerm.from_dictionary_term_ar(indication)
                    for indication in indications
                ],
                key=lambda x: x.term_uid,
            )
        # Get categories
        category_names = self._repos.ct_term_name_repository.get_syntax_categories(
            self.root_node_class, item.uid
        )
        category_attributes = (
            self._repos.ct_term_attributes_repository.get_syntax_categories(
                self.root_node_class, item.uid
            )
        )
        if category_names and category_attributes and hasattr(item, "categories"):
            item.categories = sorted(
                [
                    CTTermNameAndAttributes.from_ct_term_ars(
                        ct_term_name_ar=category_name,
                        ct_term_attributes_ar=category_attribute,
                    )
                    for category_name, category_attribute in zip(
                        category_names, category_attributes
                    )
                ],
                key=lambda x: x.term_uid,
            )
        # Get sub_categories
        sub_category_names = (
            self._repos.ct_term_name_repository.get_syntax_subcategories(
                self.root_node_class, item.uid
            )
        )
        sub_category_attributes = (
            self._repos.ct_term_attributes_repository.get_syntax_subcategories(
                self.root_node_class, item.uid
            )
        )
        if (
            sub_category_names
            and sub_category_attributes
            and hasattr(item, "sub_categories")
        ):
            item.sub_categories = sorted(
                [
                    CTTermNameAndAttributes.from_ct_term_ars(
                        ct_term_name_ar=category_name,
                        ct_term_attributes_ar=category_attribute,
                    )
                    for category_name, category_attribute in zip(
                        sub_category_names, sub_category_attributes
                    )
                ],
                key=lambda x: x.term_uid,
            )

    def _get_indexings(
        self, template: BaseModel
    ) -> tuple[
        list[DictionaryTermAR],
        list[tuple[CTTermNameAR, CTTermAttributesAR]],
        list[tuple[CTTermNameAR, CTTermAttributesAR]],
    ]:
        indications: list[DictionaryTermAR] = []
        categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] = []
        sub_categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] = []

        if (
            getattr(template, "indication_uids", None)
            and len(template.indication_uids) > 0
        ):
            for uid in template.indication_uids:
                indication = self._repos.dictionary_term_generic_repository.find_by_uid(
                    term_uid=uid
                )
                raise_404_if_none(
                    indication,
                    f"Indication with uid '{uid}' does not exist.",
                )
                indications.append(indication)

        if getattr(template, "category_uids", None) and len(template.category_uids) > 0:
            for uid in template.category_uids:
                category_name = self._repos.ct_term_name_repository.find_by_uid(
                    term_uid=uid
                )
                category_attributes = (
                    self._repos.ct_term_attributes_repository.find_by_uid(term_uid=uid)
                )
                raise_404_if_none(
                    category_name,
                    f"Category with uid '{uid}' does not exist.",
                )
                category = (category_name, category_attributes)
                categories.append(category)

        if (
            getattr(template, "sub_category_uids", None)
            and len(template.sub_category_uids) > 0
        ):
            for uid in template.sub_category_uids:
                category_name = self._repos.ct_term_name_repository.find_by_uid(
                    term_uid=uid
                )
                category_attributes = (
                    self._repos.ct_term_attributes_repository.find_by_uid(term_uid=uid)
                )
                raise_404_if_none(
                    category_name,
                    f"Subcategory with uid '{uid}' does not exist.",
                )
                category = (category_name, category_attributes)
                sub_categories.append(category)

        return indications, categories, sub_categories

    @db.transaction
    def patch_indexings(self, uid: str, indexings: BaseModel) -> BaseModel:
        template_object = self.repository.find_by_uid_2(uid)
        raise_404_if_none(
            template_object,
            f"Template with uid '{uid}' does not exist.",
        )
        try:
            if getattr(indexings, "indication_uids", None):
                self.repository.patch_indications(uid, indexings.indication_uids)
            if getattr(indexings, "category_uids", None):
                self.repository.patch_categories(uid, indexings.category_uids)
            if getattr(indexings, "sub_category_uids", None):
                self.repository.patch_subcategories(uid, indexings.sub_category_uids)
            if hasattr(indexings, "is_confirmatory_testing"):
                self.repository.patch_is_confirmatory_testing(
                    uid, indexings.is_confirmatory_testing
                )
        finally:
            self.repository.close()

        return self.get_by_uid(uid)
