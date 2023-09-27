from clinical_mdr_api import models
from clinical_mdr_api.domain_repositories.syntax_instances.activity_instruction_repository import (
    ActivityInstructionRepository,
)
from clinical_mdr_api.domain_repositories.syntax_templates.activity_instruction_template_repository import (
    ActivityInstructionTemplateRepository,
)
from clinical_mdr_api.domains.syntax_instances.activity_instruction import (
    ActivityInstructionAR,
)
from clinical_mdr_api.models.syntax_instances.activity_instruction import (
    ActivityInstruction,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._utils import service_level_generic_filtering
from clinical_mdr_api.services.syntax_instances.generic_syntax_instance_service import (
    GenericSyntaxInstanceService,
    _AggregateRootType,
)


class ActivityInstructionService(
    GenericSyntaxInstanceService[ActivityInstructionAR | _AggregateRootType]
):
    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: ActivityInstructionAR
    ) -> models.ActivityInstruction:
        return models.ActivityInstruction.from_activity_instruction_ar(item_ar)

    aggregate_class = ActivityInstructionAR
    repository_interface = ActivityInstructionRepository
    template_repository_interface = ActivityInstructionTemplateRepository
    template_uid_property = "activity_instruction_template_uid"
    template_name_property = "activity_instruction_template"
    version_class = models.ActivityInstructionVersion

    def get_all(
        self,
        # pylint: disable=unused-argument
        status: str | None = None,
        return_study_count: bool = True,
        sort_by: dict | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        total_count: bool = False,
    ) -> GenericFilteringReturn[ActivityInstruction]:
        all_items = super().get_releases_referenced_by_any_study()

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
