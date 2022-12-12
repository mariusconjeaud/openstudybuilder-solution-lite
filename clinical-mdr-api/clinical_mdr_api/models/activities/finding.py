from typing import Optional

from clinical_mdr_api.models.activities.activity_instance import (
    ActivityInstance,
    ActivityInstanceCreateInput,
    ActivityInstanceEditInput,
    ActivityInstanceVersion,
)
from clinical_mdr_api.models.ct_term import SimpleTermModel


class Finding(ActivityInstance):
    value_sas_display_format: Optional[str]
    specimen: Optional[SimpleTermModel]
    test_code: Optional[SimpleTermModel]


class FindingCreateInput(ActivityInstanceCreateInput):
    value_sas_display_format: Optional[str] = None
    specimen: Optional[str] = None
    test_code: Optional[str] = None


class FindingEditInput(ActivityInstanceEditInput):
    value_sas_display_format: Optional[str]
    specimen: Optional[str]
    test_code: Optional[str]


class FindingVersion(ActivityInstanceVersion, Finding):
    pass
