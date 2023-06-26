from clinical_mdr_api.models import StudySelectionActivityCreateInput
from clinical_mdr_api.services.studies.study_activity_selection import (
    StudyActivitySelectionService,
)


def create_study_activity(
    study_uid: str, activity_uid="activity_root1", flowchart_group_uid="term_root_final"
):
    return StudyActivitySelectionService(author="test").make_selection(
        study_uid,
        StudySelectionActivityCreateInput(
            flowchart_group_uid=flowchart_group_uid, activity_uid=activity_uid
        ),
    )
