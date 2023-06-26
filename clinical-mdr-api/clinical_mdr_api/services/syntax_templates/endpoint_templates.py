from typing import Optional

from clinical_mdr_api.domain_repositories.models.syntax import EndpointTemplateRoot
from clinical_mdr_api.domain_repositories.syntax_instances.endpoint_repository import (
    EndpointRepository,
)
from clinical_mdr_api.domain_repositories.syntax_pre_instances.endpoint_pre_instance_repository import (
    EndpointPreInstanceRepository,
)
from clinical_mdr_api.domain_repositories.syntax_templates.endpoint_template_repository import (
    EndpointTemplateRepository,
)
from clinical_mdr_api.domains._utils import generate_seq_id
from clinical_mdr_api.domains.syntax_templates.endpoint_template import (
    EndpointTemplateAR,
)
from clinical_mdr_api.domains.syntax_templates.template import TemplateVO
from clinical_mdr_api.exceptions import ValidationException
from clinical_mdr_api.models.syntax_templates.endpoint_template import (
    EndpointTemplate,
    EndpointTemplateCreateInput,
    EndpointTemplateVersion,
    EndpointTemplateWithCount,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._utils import service_level_generic_filtering
from clinical_mdr_api.services.syntax_templates.generic_syntax_template_service import (
    GenericSyntaxTemplateService,
)


class EndpointTemplateService(GenericSyntaxTemplateService[EndpointTemplateAR]):
    aggregate_class = EndpointTemplateAR
    version_class = EndpointTemplateVersion
    repository_interface = EndpointTemplateRepository
    instance_repository_interface = EndpointRepository
    pre_instance_repository_interface = EndpointPreInstanceRepository
    root_node_class = EndpointTemplateRoot

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: EndpointTemplateAR
    ) -> EndpointTemplate:
        item_ar = self._set_default_parameter_terms(item_ar)
        cls = (
            EndpointTemplateWithCount if item_ar.study_count != 0 else EndpointTemplate
        )
        item = cls.from_endpoint_template_ar(item_ar)
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
    ) -> GenericFilteringReturn[EndpointTemplate]:
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
        self, template: EndpointTemplateCreateInput
    ) -> EndpointTemplateAR:
        default_parameter_terms = self._create_default_parameter_entries(
            template_name=template.name,
            default_parameter_terms=template.default_parameter_terms,
        )

        template_vo, library_vo = self._create_template_vo(
            template, default_parameter_terms
        )

        # Get indexings for templates from database
        indications, categories, sub_categories = self._get_indexings(template)

        # Process item to save
        try:
            item = EndpointTemplateAR.from_input_values(
                template_value_exists_callback=self.get_check_exists_callback(
                    template=template
                ),
                author=self.user_initials,
                template=template_vo,
                library=library_vo,
                generate_uid_callback=self.repository.generate_uid_callback,
                generate_seq_id_callback=generate_seq_id,
                indications=indications,
                categories=categories,
                sub_categories=sub_categories,
            )
        except ValueError as e:
            raise ValidationException(e.args[0]) from e

        return item

    def _set_default_parameter_terms(
        self, item: EndpointTemplateAR
    ) -> EndpointTemplateAR:
        """This method fetches and sets the default parameter terms for the template

        Args:
            item (EndpointTemplateAR): The template for which to fetch default parameter terms
        """
        # Get default parameter terms
        default_parameter_terms = self.repository.get_default_parameter_terms(item.uid)

        return EndpointTemplateAR(
            _uid=item.uid,
            _sequence_id=item.sequence_id,
            _library=item.library,
            _item_metadata=item.item_metadata,
            _counts=item.counts,
            _study_count=item.study_count,
            _indications=item.indications if item.indications else [],
            _categories=item.categories if item.categories else [],
            _subcategories=item.sub_categories if item.sub_categories else [],
            _template=TemplateVO(
                name=item.template_value.name,
                name_plain=item.template_value.name_plain,
                default_parameter_terms=default_parameter_terms,
                guidance_text=item.template_value.guidance_text,
            ),
        )
