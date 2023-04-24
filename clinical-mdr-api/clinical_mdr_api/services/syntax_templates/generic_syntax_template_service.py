import abc
from typing import Optional, Sequence, Tuple, TypeVar, cast

from neomodel import core, db
from pydantic import BaseModel

from clinical_mdr_api.domain._utils import extract_parameters
from clinical_mdr_api.domain.library.library_ar import LibraryAR
from clinical_mdr_api.domain.library.parameter_term import (
    ParameterTermEntryVO,
    SimpleParameterTermVO,
)
from clinical_mdr_api.domain.syntax_templates.template import (
    TemplateAggregateRootBase,
    TemplateVO,
)
from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryVO,
    VersioningException,
)
from clinical_mdr_api.domain_repositories.syntax_instances.generic_syntax_instance_repository import (
    GenericSyntaxInstanceRepository,
)
from clinical_mdr_api.domain_repositories.template_parameters.complex_parameter import (
    ComplexTemplateParameterRepository,
)
from clinical_mdr_api.exceptions import (
    BusinessLogicException,
    NotFoundException,
    ValidationException,
)
from clinical_mdr_api.models.template_parameter_multi_select_input import (
    TemplateParameterMultiSelectInput,
)
from clinical_mdr_api.models.template_parameter_term import MultiTemplateParameterTerm
from clinical_mdr_api.services._utils import (
    fill_missing_values_in_base_model_from_reference_base_model,
    process_complex_parameters,
)
from clinical_mdr_api.services.generic_syntax_service import GenericSyntaxService

_AggregateRootType = TypeVar("_AggregateRootType")


class GenericSyntaxTemplateService(GenericSyntaxService[_AggregateRootType], abc.ABC):
    object_repository_interface: type

    @property
    def object_repository(self) -> GenericSyntaxInstanceRepository:
        return self.object_repository_interface()

    def get_check_exists_callback(self, template: BaseModel):
        study_uid = getattr(template, "study_uid", None)
        if study_uid:
            return lambda _template_vo: self.repository.check_exists_by_name_in_study(
                name=_template_vo.name, study_uid=study_uid
            )

        return lambda _template_vo: self.repository.check_exists_by_name_in_library(
            name=_template_vo.name, library=template.library_name
        )

    def _create_ar_from_input_values(
        self, template: BaseModel
    ) -> TemplateAggregateRootBase:
        template_vo, library_vo = self._create_template_vo(template)

        # Process item to save
        try:
            item = TemplateAggregateRootBase.from_input_values(
                template_value_exists_callback=self.get_check_exists_callback(
                    template=template
                ),
                author=self.user_initials,
                template=template_vo,
                library=library_vo,
                generate_uid_callback=self.repository.generate_uid_callback,
            )
        except ValueError as e:
            raise ValidationException(e.args[0]) from e

        return item

    def create(self, template: BaseModel) -> BaseModel:
        # This function is not decorated with db.transaction as internal transactions
        # are handled manually by "with" statement.
        try:
            # Transaction that is performing initial save
            with db.transaction:
                item = self._create_ar_from_input_values(template)

                # Save item
                self.repository.save(item)

            return self._transform_aggregate_root_to_pydantic_model(item)
        except core.DoesNotExist as exc:
            raise NotFoundException(
                f"The library with the name='{template.library_name}' could not be found."
            ) from exc
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e

    def _create_template_vo(
        self,
        template: BaseModel,
        default_parameter_terms: Optional[Sequence[ParameterTermEntryVO]] = None,
    ) -> Tuple[TemplateVO, LibraryVO]:
        # Create TemplateVO
        template_vo = TemplateVO.from_input_values_2(
            template_name=template.name,
            template_guidance_text=getattr(template, "guidance_text", None),
            parameter_name_exists_callback=self._parameter_name_exists,
            default_parameter_terms=default_parameter_terms,
        )

        # Fetch library
        try:
            library_vo = LibraryVO.from_input_values_2(
                library_name=template.library_name,
                is_library_editable_callback=(
                    lambda name: (
                        cast(
                            LibraryAR, self._repos.library_repository.find_by_name(name)
                        ).is_editable
                        if self._repos.library_repository.find_by_name(name) is not None
                        else None
                    )
                ),
            )
        except ValueError as exc:
            raise NotFoundException(
                f"The library with the name='{template.library_name}' could not be found."
            ) from exc

        return template_vo, library_vo

    def patch_default_parameter_terms(
        self,
        uid: str,
        set_number: int,
        default_parameter_terms: Sequence[MultiTemplateParameterTerm],
    ) -> BaseModel:
        # Get template AR and use it to parse the default parameter terms
        template = self._find_by_uid_or_raise_not_found(uid, for_update=True)
        parsed_default_parameter_terms = self._create_default_parameter_entries(
            template_name=template.name,
            default_parameter_terms=default_parameter_terms,
        )

        # Patch the set of default parameter terms
        self.repository.patch_default_parameter_terms(
            versioned_object=template,
            parameters=parsed_default_parameter_terms,
            set_number=set_number,
        )

        # Finally, get the complete template object and return it
        return self.get_by_uid(uid)

    def _create_default_parameter_entries(
        self,
        template_name: str,
        default_parameter_terms: Optional[Sequence[MultiTemplateParameterTerm]],
    ) -> Sequence[ParameterTermEntryVO]:
        """
        Creates sequence of Parameter Term Entries that is used in aggregate. These contain:
        parameter name, conjunctions, uids, and terms of parameters
        """
        parameter_terms = []
        # TODO : Replace the loop on allowed parameters for a loop on the template.parameters
        # Or a loop on parameters where a default term is provided
        parameters = extract_parameters(template_name)
        for i, allowed_parameter in enumerate(parameters):
            uids = []
            conjunction = ""
            parameter_name = ""

            # Find default term for parameter using the "position" property
            parameter: Optional[TemplateParameterMultiSelectInput] = None
            if default_parameter_terms is not None and len(default_parameter_terms) > 0:
                parameter = next(
                    filter(
                        lambda param, i=i: param.position - 1 == i,
                        default_parameter_terms,
                    ),
                    None,
                )

            if parameter is None:
                # If we have an empty parameter term selection, send an empty list with default type for the allowed parameters.
                parameter_name = allowed_parameter
            else:
                # Else, iterate over the provided terms, store them and their type dynamically.
                for item in parameter.terms:
                    pv = SimpleParameterTermVO.from_input_values(
                        value=item.name, uid=item.uid
                    )
                    uids.append(pv)
                parameter_name = parameter.terms[0].type
                conjunction = parameter.conjunction

            pve = ParameterTermEntryVO.from_input_values(
                parameter_exists_callback=self._repos.parameter_repository.parameter_name_exists,
                conjunction_exists_callback=lambda _: True,  # TODO: provide proper callback here
                parameter_term_uid_exists_for_parameter_callback=(
                    lambda p_name, v_uid, p_value: (
                        self._repos.parameter_repository.is_parameter_term_uid_valid_for_parameter_name(
                            parameter_term_uid=v_uid,
                            parameter_name=p_name,
                        )
                    )
                ),
                parameter_name=parameter_name,
                conjunction=conjunction,
                parameters=uids,
            )
            parameter_terms.append(pve)
        return parameter_terms

    @db.transaction
    def create_new_version(self, uid: str, template: BaseModel) -> BaseModel:
        try:
            item = self._find_by_uid_or_raise_not_found(uid, for_update=True)

            # fill the missing from the inputs
            fill_missing_values_in_base_model_from_reference_base_model(
                base_model_with_missing_values=template,
                reference_base_model=self._transform_aggregate_root_to_pydantic_model(
                    item
                ),
            )

            template_vo = TemplateVO.from_input_values_2(
                template_name=template.name,
                template_guidance_text=template.guidance_text,
                parameter_name_exists_callback=self._parameter_name_exists,
            )

            item.create_new_version(
                author=self.user_initials,
                change_description=template.change_description,
                template=template_vo,
            )
            self.repository.save(item)
            item = self._transform_aggregate_root_to_pydantic_model(item)
            self._set_indexings(item)
            return item
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e

    @db.transaction
    def approve_cascade(self, uid: str) -> BaseModel:
        try:
            item = self._find_by_uid_or_raise_not_found(uid, for_update=True)
            item.approve(author=self.user_initials)
            related_items_uids = (
                self.object_repository.find_instance_uids_by_template_uid(uid)
            )
            related_items = []
            for r_uid in related_items_uids:
                related_item = self.object_repository.find_by_uid_2(
                    r_uid, for_update=True
                )
                assert related_item is not None
                related_items.append(related_item)
            self.repository.save(item)
            related_items = []
            for r_uid in related_items_uids:
                related_item = self.object_repository.find_by_uid_2(
                    r_uid, for_update=True
                )
                assert related_item is not None
                related_item.cascade_update(
                    author=self.user_initials,
                    date=item.item_metadata.start_date,
                    new_template_name=item.name,
                )
                self.object_repository.save(related_item)

            item = self._transform_aggregate_root_to_pydantic_model(item)
            self._set_indexings(item)
            return item

        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e

    @db.transaction
    def edit_draft(self, uid: str, template: BaseModel) -> BaseModel:
        try:
            template_vo = TemplateVO.from_input_values_2(
                template_name=template.name,
                parameter_name_exists_callback=self._parameter_name_exists,
            )

            item = self._find_by_uid_or_raise_not_found(
                uid, for_update=True, return_study_count=True
            )

            if self.repository.check_exists_by_name_in_library(
                name=template.name, library=item.library.name
            ):
                raise ValueError(
                    f"Duplicate templates not allowed - template exists: {template.name}"
                )

            item.edit_draft(
                author=self.user_initials,
                change_description=template.change_description,
                template=template_vo,
            )
            self.repository.save(item)
            return self._transform_aggregate_root_to_pydantic_model(item)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e

    @db.transaction
    def get_parameters(
        self,
        uid: str,
        study_uid: Optional[str] = None,
        include_study_endpoints: Optional[bool] = False,
    ):
        try:
            parameter_repository_2 = ComplexTemplateParameterRepository()

            parameters = self.repository.get_parameters_including_terms(
                template_uid=uid,
                study_uid=study_uid,
                include_study_endpoints=include_study_endpoints,
            )
            return process_complex_parameters(parameters, parameter_repository_2)
        except core.DoesNotExist as exc:
            raise NotFoundException(
                f"The object  with uid='{uid}' could not be found."
            ) from exc

    @db.transaction
    def validate_template_syntax(self, template_name_to_validate: str) -> None:
        try:
            TemplateVO.from_input_values_2(
                template_name=template_name_to_validate,
                parameter_name_exists_callback=self._parameter_name_exists,
            )
        except ValueError as exc:
            raise ValidationException(exc.args[0]) from exc

    def get_by_uid(
        self,
        uid: str,
        return_instantiation_counts: bool = False,
        return_study_count: Optional[bool] = True,
    ) -> BaseModel:
        item = super().get_by_uid(uid, return_instantiation_counts, return_study_count)
        self._set_indexings(item)
        return item

    def get_specific_version(
        self, uid: str, version: str, return_study_count: Optional[bool] = True
    ) -> BaseModel:
        item = super().get_specific_version(uid, version, return_study_count)
        self._set_indexings(item)
        return item

    def get_all(
        self, status: Optional[str] = None, return_study_count: Optional[bool] = True
    ) -> Sequence[BaseModel]:
        items = super().get_all(status, return_study_count)

        for item in items:
            self._set_indexings(item)
        return items

    def approve(self, uid: str) -> BaseModel:
        item = super().approve(uid)
        self._set_indexings(item)
        return item

    def inactivate_final(self, uid: str) -> BaseModel:
        item = super().inactivate_final(uid)
        self._set_indexings(item)
        return item

    def reactivate_retired(self, uid: str) -> BaseModel:
        item = super().reactivate_retired(uid)
        self._set_indexings(item)
        return item

    def get_version_history(
        self, uid: str, return_study_count: Optional[bool] = True
    ) -> Sequence[BaseModel]:
        items = super().get_version_history(uid, return_study_count)

        for item in items:
            self._set_indexings(item)
        return items

    def get_releases(
        self, uid: str, return_study_count: Optional[bool] = True
    ) -> Sequence[BaseModel]:
        items = super().get_releases(uid, return_study_count)

        for item in items:
            self._set_indexings(item)
        return items
