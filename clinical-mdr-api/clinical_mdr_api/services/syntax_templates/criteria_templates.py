from typing import Optional, Sequence, Tuple

from neomodel import db
from pydantic.main import BaseModel

from clinical_mdr_api.domain_repositories.models.syntax import CriteriaTemplateRoot
from clinical_mdr_api.domain_repositories.syntax_instances.criteria_repository import (
    CriteriaRepository,
)
from clinical_mdr_api.domain_repositories.syntax_pre_instances.criteria_pre_instance_repository import (
    CriteriaPreInstanceRepository,
)
from clinical_mdr_api.domain_repositories.syntax_templates.criteria_template_repository import (
    CriteriaTemplateRepository,
)
from clinical_mdr_api.domains._utils import generate_seq_id
from clinical_mdr_api.domains.controlled_terminologies.ct_term_attributes import (
    CTTermAttributesAR,
)
from clinical_mdr_api.domains.controlled_terminologies.ct_term_name import CTTermNameAR
from clinical_mdr_api.domains.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domains.syntax_templates.criteria_template import (
    CriteriaTemplateAR,
)
from clinical_mdr_api.domains.syntax_templates.template import TemplateVO
from clinical_mdr_api.domains.versioned_object_aggregate import VersioningException
from clinical_mdr_api.exceptions import BusinessLogicException, ValidationException
from clinical_mdr_api.models.controlled_terminologies.ct_term import (
    CTTermNameAndAttributes,
)
from clinical_mdr_api.models.syntax_templates.criteria_template import (
    CriteriaTemplate,
    CriteriaTemplateCreateInput,
    CriteriaTemplateEditInput,
    CriteriaTemplateVersion,
    CriteriaTemplateWithCount,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._utils import (
    raise_404_if_none,
    service_level_generic_filtering,
)
from clinical_mdr_api.services.syntax_templates.generic_syntax_template_service import (
    GenericSyntaxTemplateService,
)


class CriteriaTemplateService(GenericSyntaxTemplateService[CriteriaTemplateAR]):
    aggregate_class = CriteriaTemplateAR
    version_class = CriteriaTemplateVersion
    repository_interface = CriteriaTemplateRepository
    instance_repository_interface = CriteriaRepository
    pre_instance_repository_interface = CriteriaPreInstanceRepository
    root_node_class = CriteriaTemplateRoot

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: CriteriaTemplateAR
    ) -> CriteriaTemplate:
        item_ar = self._set_default_parameter_terms(item_ar)
        cls = (
            CriteriaTemplateWithCount if item_ar.study_count != 0 else CriteriaTemplate
        )
        item = cls.from_criteria_template_ar(item_ar)
        self._set_indexings(item)
        return item

    def get_all(
        self,
        status: Optional[str] = None,
        return_study_count: bool = True,
        sort_by: Optional[dict] = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: Optional[dict] = None,
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
        total_count: bool = False,
    ) -> GenericFilteringReturn[CriteriaTemplate]:
        all_items = super().get_all(status, return_study_count)

        # The get_all method is only using neomodel, without Cypher query
        # Therefore, the filtering will be done in this service layer
        filtered_items = service_level_generic_filtering(
            items=all_items,
            filter_by=filter_by,
            filter_operator=filter_operator,
            sort_by=sort_by,
            total_count=total_count,
            page_number=page_number,
            page_size=page_size,
        )

        return filtered_items

    def _create_ar_from_input_values(
        self, template: CriteriaTemplateCreateInput
    ) -> CriteriaTemplateAR:
        default_parameter_terms = self._create_default_parameter_entries(
            template_name=template.name,
            default_parameter_terms=template.default_parameter_terms,
        )

        template_vo, library_vo = self._create_template_vo(
            template, default_parameter_terms
        )

        # Get indexings for templates from database
        criteria_type, indications, categories, sub_categories = self._get_indexings(
            template
        )

        # Process item to save
        try:
            item = CriteriaTemplateAR.from_input_values(
                template_value_exists_callback=self.get_check_exists_callback(
                    template=template
                ),
                author=self.user_initials,
                template=template_vo,
                library=library_vo,
                generate_uid_callback=self.repository.generate_uid_callback,
                generate_seq_id_callback=generate_seq_id,
                indications=indications,
                criteria_type=criteria_type,
                categories=categories,
                sub_categories=sub_categories,
            )
        except ValueError as e:
            raise ValidationException(e.args[0]) from e

        return item

    def get_check_exists_callback(self, template: BaseModel):
        return lambda _template_vo: self.repository.check_exists_by_name_and_type_in_library(
            name=_template_vo.name,
            library=template.library_name,
            type_uid=template.type_uid,
        )

    @db.transaction
    def edit_draft(
        self, uid: str, template: CriteriaTemplateEditInput
    ) -> CriteriaTemplate:
        try:
            item = self._find_by_uid_or_raise_not_found(uid, for_update=True)

            if (
                self.repository.check_exists_by_name_and_type_in_library(
                    name=template.name,
                    library=item.library.name,
                    type_uid=self.repository.get_criteria_type_uid(uid),
                )
                and template.name != item.name
            ):
                raise ValueError(
                    f"Duplicate templates not allowed - template exists: {template.name}"
                )

            template_vo = TemplateVO.from_input_values_2(
                template_name=template.name,
                template_guidance_text=template.guidance_text,
                parameter_name_exists_callback=self._parameter_name_exists,
            )

            item.edit_draft(
                author=self.user_initials,
                change_description=template.change_description,
                template=template_vo,
            )

            # Save item
            self.repository.save(item)
            return self._transform_aggregate_root_to_pydantic_model(item)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e

    def _set_default_parameter_terms(
        self, item: CriteriaTemplateAR
    ) -> CriteriaTemplateAR:
        """This method fetches and sets the default parameter terms for the template

        Args:
            item (CriteriaTemplateAR): The template for which to fetch default parameter terms
        """
        # Get default parameter terms
        default_parameter_terms = self.repository.get_default_parameter_terms(item.uid)

        return CriteriaTemplateAR(
            _uid=item.uid,
            _sequence_id=item.sequence_id,
            _library=item.library,
            _item_metadata=item.item_metadata,
            _counts=item.counts,
            _study_count=item.study_count,
            _indications=item.indications if item.indications else [],
            _type=item.type,
            _categories=item.categories if item.categories else [],
            _subcategories=item.sub_categories if item.sub_categories else [],
            _template=TemplateVO(
                name=item.template_value.name,
                name_plain=item.template_value.name_plain,
                default_parameter_terms=default_parameter_terms,
                guidance_text=item.template_value.guidance_text,
            ),
        )

    def _set_indexings(self, item: CriteriaTemplate) -> None:
        """
        This method fetches and sets the indexing properties to a template.
        """
        if not hasattr(item, "uid"):
            return None

        # Get type
        criteria_type_name = (
            self._repos.ct_term_name_repository.get_syntax_criteria_type(
                self.root_node_class, item.uid
            )
        )
        criteria_type_attributes = (
            self._repos.ct_term_attributes_repository.get_syntax_criteria_type(
                self.root_node_class, item.uid
            )
        )
        if criteria_type_name is not None and criteria_type_attributes is not None:
            item.type = CTTermNameAndAttributes.from_ct_term_ars(
                ct_term_name_ar=criteria_type_name,
                ct_term_attributes_ar=criteria_type_attributes,
            )

        return super()._set_indexings(item)

    def _get_indexings(
        self, template: BaseModel, template_uid: Optional[str] = None
    ) -> Tuple[
        Optional[Tuple[CTTermNameAR, CTTermAttributesAR]],
        Sequence[DictionaryTermAR],
        Sequence[Tuple[CTTermNameAR, CTTermAttributesAR]],
        Sequence[Tuple[CTTermNameAR, CTTermAttributesAR]],
    ]:
        criteria_type: Optional[Tuple[CTTermNameAR, CTTermAttributesAR]] = None

        criteria_type_term_uid = getattr(
            template, "type_uid", None
        ) or self._repos.criteria_template_repository.get_criteria_type_uid(
            template_uid
        )

        if criteria_type_term_uid is not None:
            criteria_type_name = self._repos.ct_term_name_repository.find_by_uid(
                term_uid=criteria_type_term_uid
            )
            raise_404_if_none(
                criteria_type_name,
                f"Criteria type with uid '{criteria_type_term_uid}' does not exist.",
            )
            criteria_type_attributes = (
                self._repos.ct_term_attributes_repository.find_by_uid(
                    term_uid=criteria_type_term_uid
                )
            )
            raise_404_if_none(
                criteria_type_attributes,
                f"Criteria type with uid '{criteria_type_term_uid}' does not exist.",
            )
            criteria_type = (criteria_type_name, criteria_type_attributes)

        indications, categories, sub_categories = super()._get_indexings(template)

        return criteria_type, indications, categories, sub_categories
