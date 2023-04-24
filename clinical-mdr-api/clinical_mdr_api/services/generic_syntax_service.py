import abc
from datetime import datetime
from typing import Generic, Optional, Sequence, Tuple, TypeVar

from neomodel import db
from pydantic import BaseModel

from clinical_mdr_api.domain.controlled_terminology.ct_term_attributes import (
    CTTermAttributesAR,
)
from clinical_mdr_api.domain.controlled_terminology.ct_term_name import CTTermNameAR
from clinical_mdr_api.domain.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domain.syntax_templates.template import TemplateVO
from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryItemStatus,
    VersioningException,
)
from clinical_mdr_api.domain_repositories._generic_repository_interface import (
    GenericRepository,
)
from clinical_mdr_api.domain_repositories.study_definition.study_definition_repository import (
    StudyDefinitionRepository,
)
from clinical_mdr_api.exceptions import (
    BusinessLogicException,
    ConflictErrorException,
    NotFoundException,
)
from clinical_mdr_api.models.ct_term import CTTermNameAndAttributes
from clinical_mdr_api.models.dictionary_term import DictionaryTerm
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services._utils import (
    calculate_diffs,
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
    user_initials: Optional[str]
    root_node_class: type

    def __init__(self, user: Optional[str] = None):
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
        return_study_count: Optional[bool] = True,
    ) -> BaseModel:
        item = self._find_by_uid_or_raise_not_found(
            uid,
            return_study_count=return_study_count,
            return_instantiation_counts=return_instantiation_counts,
        )
        return self._transform_aggregate_root_to_pydantic_model(item)

    @db.transaction
    def get_specific_version(
        self, uid: str, version: str, return_study_count: Optional[bool] = True
    ) -> BaseModel:
        item = self._find_by_uid_or_raise_not_found(
            uid, return_study_count=return_study_count, version=version
        )
        return self._transform_aggregate_root_to_pydantic_model(item)

    def _find_by_uid_or_raise_not_found(
        self,
        uid: str,
        *,
        version: Optional[str] = None,
        at_specific_date: Optional[datetime] = None,
        status: Optional[LibraryItemStatus] = None,
        for_update: bool = False,
        return_instantiation_counts: bool = False,
        return_study_count: Optional[bool] = True,
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
    def get_all(
        self, status: Optional[str] = None, return_study_count: Optional[bool] = True
    ) -> Sequence[BaseModel]:
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
        status: Optional[str] = None,
        search_string: Optional[str] = "",
        filter_by: Optional[dict] = None,
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
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
        self, uid: str, return_study_count: Optional[bool] = True
    ) -> Sequence[BaseModel]:
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
        self, uid: str, return_study_count: Optional[bool] = True
    ) -> Sequence[BaseModel]:
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
        # Get indications
        indications = (
            self._repos.dictionary_term_generic_repository.get_syntax_indications(
                self.root_node_class, item.uid
            )
        )
        if indications:
            item.indications = [
                DictionaryTerm.from_dictionary_term_ar(indication)
                for indication in indications
            ]
        # Get categories
        category_names = self._repos.ct_term_name_repository.get_syntax_categories(
            self.root_node_class, item.uid
        )
        category_attributes = (
            self._repos.ct_term_attributes_repository.get_syntax_categories(
                self.root_node_class, item.uid
            )
        )
        if category_names and category_attributes:
            item.categories = [
                CTTermNameAndAttributes.from_ct_term_ars(
                    ct_term_name_ar=category_name,
                    ct_term_attributes_ar=category_attribute,
                )
                for category_name, category_attribute in zip(
                    category_names, category_attributes
                )
            ]
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
        if sub_category_names and sub_category_attributes:
            item.sub_categories = [
                CTTermNameAndAttributes.from_ct_term_ars(
                    ct_term_name_ar=category_name,
                    ct_term_attributes_ar=category_attribute,
                )
                for category_name, category_attribute in zip(
                    sub_category_names, sub_category_attributes
                )
            ]

    def _get_indexings(
        self, template: BaseModel
    ) -> Tuple[
        Sequence[DictionaryTermAR],
        Sequence[Tuple[CTTermNameAR, CTTermAttributesAR]],
        Sequence[Tuple[CTTermNameAR, CTTermAttributesAR]],
    ]:
        indications: Sequence[DictionaryTermAR] = []
        categories: Sequence[Tuple[CTTermNameAR, CTTermAttributesAR]] = []
        sub_categories: Sequence[Tuple[CTTermNameAR, CTTermAttributesAR]] = []

        if (
            getattr(template, "indication_uids", None)
            and len(template.indication_uids) > 0
        ):
            for uid in template.indication_uids:
                indication = self._repos.dictionary_term_generic_repository.find_by_uid(
                    term_uid=uid
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
                category = (category_name, category_attributes)
                sub_categories.append(category)

        return indications, categories, sub_categories
