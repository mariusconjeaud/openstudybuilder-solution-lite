from clinical_mdr_api.domains.libraries.timepoints import TimepointAR
from clinical_mdr_api.domains.syntax_instances.timeframe import TimeframeAR
from clinical_mdr_api.models.libraries.timepoint import Timepoint, TimepointVersion
from clinical_mdr_api.services.syntax_instances.generic_syntax_instance_service import (
    GenericSyntaxInstanceService,
)


class TimepointService(GenericSyntaxInstanceService[TimeframeAR]):
    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: TimeframeAR
    ) -> Timepoint:
        return Timepoint.from_timepoint_ar(item_ar)

    aggregate_class = TimepointAR
    version_class = TimepointVersion
    template_uid_property = "timepoint_template_uid"
    template_name_property = "timepoint_template"
