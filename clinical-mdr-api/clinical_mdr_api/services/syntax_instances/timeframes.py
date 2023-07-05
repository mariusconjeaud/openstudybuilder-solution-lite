from typing import Optional, Union

from clinical_mdr_api.domain_repositories.syntax_instances.timeframe_repository import (
    TimeframeRepository,
)
from clinical_mdr_api.domain_repositories.syntax_templates.timeframe_template_repository import (
    TimeframeTemplateRepository,
)
from clinical_mdr_api.domains.syntax_instances.timeframe import TimeframeAR
from clinical_mdr_api.models.syntax_instances.timeframe import (
    Timeframe,
    TimeframeVersion,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._utils import service_level_generic_filtering
from clinical_mdr_api.services.syntax_instances.generic_syntax_instance_service import (
    GenericSyntaxInstanceService,
    _AggregateRootType,
)


class TimeframeService(
    GenericSyntaxInstanceService[Union[TimeframeAR, _AggregateRootType]]
):
    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: TimeframeAR
    ) -> Timeframe:
        return Timeframe.from_timeframe_ar(item_ar)

    aggregate_class = TimeframeAR
    repository_interface = TimeframeRepository
    template_repository_interface = TimeframeTemplateRepository
    version_class = TimeframeVersion
    template_uid_property = "timeframe_template_uid"
    template_name_property = "timeframe_template"

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
    ) -> GenericFilteringReturn[Timeframe]:
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
