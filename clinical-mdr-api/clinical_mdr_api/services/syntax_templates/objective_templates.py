from clinical_mdr_api.domain_repositories.models.syntax import ObjectiveTemplateRoot
from clinical_mdr_api.domain_repositories.syntax_instances.objective_repository import (
    ObjectiveRepository,
)
from clinical_mdr_api.domain_repositories.syntax_pre_instances.objective_pre_instance_repository import (
    ObjectivePreInstanceRepository,
)
from clinical_mdr_api.domain_repositories.syntax_templates.objective_template_repository import (
    ObjectiveTemplateRepository,
)
from clinical_mdr_api.domains.syntax_templates.objective_template import (
    ObjectiveTemplateAR,
)
from clinical_mdr_api.domains.syntax_templates.template import TemplateVO
from clinical_mdr_api.models.syntax_templates.objective_template import (
    ObjectiveTemplate,
    ObjectiveTemplateCreateInput,
    ObjectiveTemplateVersion,
    ObjectiveTemplateWithCount,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._utils import service_level_generic_filtering
from clinical_mdr_api.services.syntax_templates.generic_syntax_template_service import (
    GenericSyntaxTemplateService,
)


class ObjectiveTemplateService(GenericSyntaxTemplateService[ObjectiveTemplateAR]):
    aggregate_class = ObjectiveTemplateAR
    version_class = ObjectiveTemplateVersion
    repository_interface = ObjectiveTemplateRepository
    instance_repository_interface = ObjectiveRepository
    pre_instance_repository_interface = ObjectivePreInstanceRepository
    root_node_class = ObjectiveTemplateRoot

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: ObjectiveTemplateAR
    ) -> ObjectiveTemplate:
        item_ar = self._set_default_parameter_terms(item_ar)
        cls = ObjectiveTemplateWithCount if item_ar.counts != 0 else ObjectiveTemplate
        item = cls.from_objective_template_ar(item_ar)
        self._set_indexings(item)
        return item

    def get_all(
        self,
        status: str | None = None,
        return_study_count: bool = True,
        sort_by: dict | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        total_count: bool = False,
    ) -> GenericFilteringReturn[ObjectiveTemplate]:
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
        self, template: ObjectiveTemplateCreateInput
    ) -> ObjectiveTemplateAR:
        default_parameter_terms = self._create_default_parameter_entries(
            template_name=template.name,
            default_parameter_terms=template.default_parameter_terms,
        )

        template_vo, library_vo = self._create_template_vo(
            template, default_parameter_terms
        )

        # Get indexings for templates from database
        indications, categories, _ = self._get_indexings(template)

        # Process item to save
        item = ObjectiveTemplateAR.from_input_values(
            author=self.user_initials,
            template=template_vo,
            library=library_vo,
            generate_uid_callback=self.repository.generate_uid_callback,
            next_available_sequence_id_callback=self.repository.next_available_sequence_id,
            is_confirmatory_testing=template.is_confirmatory_testing,
            indications=indications,
            categories=categories,
        )

        return item

    def _set_default_parameter_terms(
        self, item: ObjectiveTemplateAR
    ) -> ObjectiveTemplateAR:
        """This method fetches and sets the default parameter terms for the template

        Args:
            item (ObjectiveTemplateAR): The template for which to fetch default parameter terms
        """
        # Get default parameter terms
        default_parameter_terms = self.repository.get_default_parameter_terms(item.uid)

        return ObjectiveTemplateAR(
            _uid=item.uid,
            _sequence_id=item.sequence_id,
            _library=item.library,
            _item_metadata=item.item_metadata,
            _counts=item.counts,
            _study_count=item.study_count,
            _indications=item.indications if item.indications else [],
            _categories=item.categories if item.categories else [],
            _is_confirmatory_testing=item.is_confirmatory_testing,
            _template=TemplateVO(
                name=item.template_value.name,
                name_plain=item.template_value.name_plain,
                default_parameter_terms=default_parameter_terms,
                guidance_text=item.template_value.guidance_text,
            ),
        )
