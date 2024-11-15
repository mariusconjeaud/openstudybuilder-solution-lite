import logging
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from consumer_api.shared.common import convert_to_datetime

log = logging.getLogger(__name__)


class SortOrder(Enum):
    ASC = "asc"
    DESC = "desc"


class SortByStudies(Enum):
    UID = "uid"
    ID_PREFIX = "id_prefix"
    NUMBER = "number"


class Study(BaseModel):
    class StudyVersion(BaseModel):
        version_status: str | None = Field(
            None, description="Study Status", nullable=True
        )
        version_number: str | None = Field(
            None, description="Study Version Number", nullable=True
        )
        version_started_at: datetime | None = Field(
            None, description="Study Version Start Time", nullable=True
        )
        version_ended_at: datetime | None = Field(
            None, description="Study Version End Time", nullable=True
        )
        version_author: str | None = Field(
            None, description="Study Author", nullable=True
        )
        version_description: str | None = Field(
            None, description="Study Description", nullable=True
        )

        @classmethod
        def from_input(cls, val: dict):
            log.debug("Create Study Version from input: %s", val)
            return cls(
                version_status=val.get("version_status", None),
                version_number=val.get("version_number", None),
                version_started_at=convert_to_datetime(
                    val.get("version_started_at", None)
                ),
                version_ended_at=convert_to_datetime(val.get("version_ended_at", None)),
                version_author=val.get("version_author", None),
                version_description=val.get("version_description", None),
            )

    uid: str = Field(..., description="Study UID")
    id: str = Field(..., description="Study ID")
    id_prefix: str = Field(..., description="Study ID prefix")
    number: str | None = Field(None, description="Study number", nullable=True)
    acronym: str | None = Field(None, description="Study acronym", nullable=True)
    versions: list[StudyVersion] = Field(description="Study versions")

    @classmethod
    def from_input(cls, val: dict):
        log.debug("Create Study from input: %s", val)
        return cls(
            uid=val["uid"],
            id=val["id"],
            id_prefix=val["id_prefix"],
            number=val["number"],
            acronym=val.get("acronym", None),
            versions=[
                Study.StudyVersion.from_input(version)
                for version in val.get("versions", [])
            ],
        )


class SortByStudyVisits(Enum):
    UID = "uid"
    NAME = "visit_name"
    UNIQUE_VISIT_NUMBER = "unique_visit_number"


class StudyVisit(BaseModel):
    study_uid: str = Field(..., description="Study UID")
    study_version_number: str = Field(..., description="Study Version Number")
    uid: str = Field(..., description="Study Visit UID")
    visit_name: str = Field(..., description="Study Visit Name")
    visit_order: int = Field(..., description="Study Visit Order")
    unique_visit_number: int = Field(..., description="Study Visit Unique Visit Number")
    visit_number: float = Field(..., description="Study Visit Visit Number")
    visit_short_name: str = Field(..., description="Study Visit Visit Short Name")
    visit_window_min: int | None = Field(
        None, description="Study Visit Min Visit Window Value", nullable=True
    )
    visit_window_max: int | None = Field(
        None, description="Study Visit Max Visit Window Value", nullable=True
    )
    visit_type_uid: str = Field(..., description="Study Visit Visit Type UID")
    visit_type_name: str = Field(..., description="Study Visit Visit Type Name")
    visit_window_unit_uid: str | None = Field(
        None, description="Study Visit Visit Window Unit UID", nullable=True
    )
    visit_window_unit_name: str | None = Field(
        None, description="Study Visit Visit Window Unit Name", nullable=True
    )
    study_epoch_uid: str = Field(..., description="Study Visit Study Epoch UID")
    study_epoch_name: str = Field(..., description="Study Visit Study Epoch Name")
    time_unit_uid: str | None = Field(
        None, description="Study Visit Time Unit UID", nullable=True
    )
    time_unit_name: str | None = Field(
        None, description="Study Visit Time Unit Name", nullable=True
    )
    time_value_uid: str | None = Field(
        None, description="Study Visit Time Value UID", nullable=True
    )
    time_value: int | None = Field(
        None, description="Study Visit Time Value", nullable=True
    )

    @classmethod
    def from_input(cls, val: dict):
        log.debug("Create Study Visit from input: %s", val)
        return cls(
            study_uid=val["study_uid"],
            study_version_number=val["study_version_number"],
            uid=val["uid"],
            visit_name=val["visit_name"],
            unique_visit_number=val["unique_visit_number"],
            visit_number=val["visit_number"],
            visit_order=val["visit_number"],
            visit_short_name=val["visit_short_name"],
            visit_window_min=val["visit_window_min"],
            visit_window_max=val["visit_window_max"],
            visit_type_uid=val["visit_type_uid"],
            visit_type_name=val["visit_type_name"],
            visit_window_unit_uid=val["visit_window_unit_uid"],
            visit_window_unit_name=val["visit_window_unit_name"],
            study_epoch_uid=val["study_epoch_uid"],
            study_epoch_name=val["study_epoch_name"],
            time_unit_uid=val["time_unit_uid"],
            time_unit_name=val["time_unit_name"],
            time_value_uid=val["time_value_uid"],
            time_value=val["time_value_value"],
        )


class SortByStudyOperationalSoA(Enum):
    ACTIVITY = "activity"
    VISIT_UID = "visit_uid"


class StudyOperationalSoA(BaseModel):
    study_uid: str | None = Field(..., description="Study UID", nullable=True)
    study_id: str | None = Field(..., description="Study ID", nullable=True)
    study_version_number: str | None = Field(
        ..., description="Study Version Number", nullable=True
    )
    activity: str | None = Field(..., description="Activity Name", nullable=True)
    activity_uid: str | None = Field(..., description="Activity UID", nullable=True)
    activity_group: str | None = Field(
        ..., description="Activity Group Name", nullable=True
    )
    activity_group_uid: str | None = Field(
        ..., description="Activity Group UID", nullable=True
    )
    activity_subgroup: str | None = Field(
        ..., description="Activity Subgroup Name", nullable=True
    )
    activity_subgroup_uid: str | None = Field(
        ..., description="Activity Subgroup UID", nullable=True
    )
    activity_instance: str | None = Field(
        ..., description="Activity Instance Name", nullable=True
    )
    activity_instance_uid: str | None = Field(
        ..., description="Activity Instance UID", nullable=True
    )
    epoch: str | None = Field(..., description="Epoch Name", nullable=True)
    param_code: str | None = Field(..., description="Param Code", nullable=True)
    soa_group: str | None = Field(..., description="SoS Group Name", nullable=True)
    topic_code: str | None = Field(..., description="Topic Code", nullable=True)
    visit_short_name: str | None = Field(
        ..., description="Visit Short Name", nullable=True
    )
    visit_uid: str | None = Field(..., description="Visit UID", nullable=True)

    @classmethod
    def from_input(cls, val: dict):
        log.debug("Create Study Operational SoA from input: %s", val)
        return cls(
            study_uid=val["study_uid"],
            study_id=val["study_id"],
            study_version_number=val["study_version_number"],
            activity=val["activity"],
            activity_uid=val["activity_uid"],
            activity_group=val["activity_group"],
            activity_group_uid=val["activity_group_uid"],
            activity_subgroup=val["activity_subgroup"],
            activity_subgroup_uid=val["activity_subgroup_uid"],
            activity_instance=val["activity_instance"],
            activity_instance_uid=val["activity_instance_uid"],
            epoch=val["epoch"],
            param_code=val["param_code"],
            soa_group=val["soa_group"],
            topic_code=val["topic_code"],
            visit_short_name=val["visit_short_name"],
            visit_uid=val["visit_uid"],
        )
