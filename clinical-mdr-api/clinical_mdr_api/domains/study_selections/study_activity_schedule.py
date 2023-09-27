import datetime
from dataclasses import dataclass


@dataclass
class StudyActivityScheduleVO:
    study_uid: str
    study_activity_uid: str | None
    study_activity_name: str | None
    study_visit_uid: str | None
    study_visit_name: str | None

    # Study selection Versioning
    start_date: datetime.datetime
    user_initials: str | None

    uid: str | None = None
