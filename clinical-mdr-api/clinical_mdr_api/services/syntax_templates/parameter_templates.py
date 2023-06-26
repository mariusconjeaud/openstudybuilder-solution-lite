from typing import cast

from neomodel import db
from pydantic import BaseModel

from clinical_mdr_api.domain_repositories.syntax_templates.parameter_template_repository import (
    ParameterTemplateRepository,
)
from clinical_mdr_api.domains.libraries.library_ar import LibraryAR
from clinical_mdr_api.domains.syntax_templates.template import TemplateVO
from clinical_mdr_api.domains.template_parameters import ParameterTemplateAR
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryVO,
    VersioningException,
)
from clinical_mdr_api.exceptions import (
    BusinessLogicException,
    NotFoundException,
    ValidationException,
)
from clinical_mdr_api.models.complex_parameter_template import (
    ComplexParameterTemplate,
    ComplexParameterTemplateCreateInput,
    ComplexParameterTemplateVersion,
)
from clinical_mdr_api.services.syntax_templates.generic_syntax_template_service import (
    GenericSyntaxTemplateService,
)


class ComplexParameterTemplateService(
    GenericSyntaxTemplateService[ParameterTemplateAR]
):
    aggregate_class = ParameterTemplateAR
    version_class = ComplexParameterTemplateVersion
    repository_interface = ParameterTemplateRepository

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: ParameterTemplateAR
    ) -> ComplexParameterTemplate:
        return ComplexParameterTemplate.from_parameter_template_ar(item_ar)

    def create(
        self, template: ComplexParameterTemplateCreateInput
    ) -> ComplexParameterTemplate:
        try:
            # Transaction that is performing initial save
            with db.transaction:
                # TODO: prepare proper validation
                template_vo = TemplateVO.from_input_values_2(
                    template_name=template.name,
                    parameter_name_exists_callback=lambda x: True,
                )

                try:
                    library_vo = LibraryVO.from_input_values_2(
                        library_name=template.library_name,
                        is_library_editable_callback=(
                            lambda name: (
                                cast(
                                    LibraryAR,
                                    self._repos.library_repository.find_by_name(name),
                                ).is_editable
                                if self._repos.library_repository.find_by_name(name)
                                is not None
                                else None
                            )
                        ),
                    )
                except ValueError as exc:
                    raise NotFoundException(
                        f"The library with the name='{template.library_name}' could not be found."
                    ) from exc
                try:
                    item = ParameterTemplateAR.from_input_values(
                        author=self.user_initials,
                        parameter_name=template.parameter_name,
                        library=library_vo,
                        template=template_vo,
                    )
                except ValueError as e:
                    raise ValidationException(e.args[0]) from e

                self.repository.save(item)

            return self._transform_aggregate_root_to_pydantic_model(item)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e

    @db.transaction
    def edit_draft(self, uid: str, template: BaseModel) -> BaseModel:
        try:
            # TODO: find better validation
            template_vo = TemplateVO.from_input_values_2(
                template_name=template.name,
                parameter_name_exists_callback=lambda x: True,
            )

            item = self._find_by_uid_or_raise_not_found(uid, for_update=True)

            item.edit_draft(
                author=self.user_initials,
                change_description=template.change_description,
                template=template_vo,
            )
            self.repository.save(item)
            return self._transform_aggregate_root_to_pydantic_model(item)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e
