from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field

from clinical_mdr_api.models.utils import BaseModel


class StudyEpochCreateInput(BaseModel):
    study_uid: str = Field(
        ...,
        title="study_uid",
        description="The uid of the study",
    )
    start_rule: Optional[str] = Field(
        None, title="Start Description", description="Study Epoch Start description"
    )

    end_rule: Optional[str] = Field(
        None, title="End Description", description="Study Epoch end description"
    )

    epoch: Optional[str] = Field(None, title="Epoch", description="Study Epoch epoch")

    epoch_subtype: str = Field(
        ..., title="Epoch Sub Type", description="Study Epoch sub type"
    )

    duration_unit: Optional[str] = Field(
        None, title="Duration Unit", description="Study Epoch duration preferred unit"
    )

    order: Optional[int] = Field(
        None,
        title="order",
        description="The ordering of the selection",
    )
    description: Optional[str] = Field(
        None, title="Description", description="Epoch description"
    )

    duration: Optional[int] = Field(
        None, title="Epoch Duration", description="Calculated epoch duration"
    )
    color_hash: Optional[str] = Field(
        "#FFFFFF", title="Epoch Color Hash", description="Epoch Color for display"
    )


class StudyEpochEditInput(StudyEpochCreateInput):
    # Override epoch from Create Input to make it Optional
    epoch_subtype: Optional[str] = Field(
        None, title="Epoch Sub Type", description="Study Epoch sub type"
    )
    change_description: str = Field(
        ..., title="Change Description", description="Description of change reasons"
    )


class StudyEpochOGM(BaseModel):
    # status = StudyStatus(epoch_neomodel.status),
    # version = epoch_neomodel.version,

    class Config:
        orm_mode = True

    uid: str = Field(..., title="Uid", description="Uid of the Epoch", source="uid")
    study_uid: str = Field(
        ...,
        title="Uid",
        description="Uid of the study",
        source="has_study_epoch.study_root.uid",
    )
    epoch: str = Field(
        ...,
        title="Epoch name",
        description="Name of the epoch based on CT term",
        source="has_epoch.uid",
    )
    epoch_subtype: str = Field(
        ...,
        title="Epoch sub type name",
        description="Name of the epoch sub type based on CT term",
        source="has_epoch_subtype.uid",
    )
    epoch_type: str = Field(
        ..., title="Type", description="Study Epoch type", source="has_epoch_type.uid"
    )
    duration_unit: Optional[str] = Field(
        None,
        title="Duration Unit",
        description="Study Epoch duration preferred unit",
        source="has_duration_unit.uid",
    )

    order: Optional[int] = Field(
        None, title="order", description="The ordering of the selection", source="order"
    )
    description: Optional[str] = Field(
        None, title="Description", description="Epoch description", source="description"
    )

    color_hash: Optional[str] = Field(
        None,
        title="Epoch Color Hash",
        description="Epoch Color for display",
        source="color_hash",
    )
    start_rule: Optional[str] = Field(
        None,
        title="Start Description",
        description="Study Epoch Start description",
        source="start_rule",
    )

    end_rule: Optional[str] = Field(
        None,
        title="End Description",
        description="Study Epoch end description",
        source="end_rule",
    )
    status: str = Field(
        ..., title="Status", description="Study Epoch status", source="status"
    )
    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study epoch was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
        source="has_after.date",
    )
    user_initials: str = Field(
        ...,
        title="User Initials",
        description="Initials of user that created last modification",
        source="has_after.user_initials",
    )


class StudyEpochOGMVer(StudyEpochOGM):
    study_uid: str = Field(
        ...,
        title="Uid",
        description="Uid of the study",
        source="has_after.audit_trail.uid",
    )


class StudyEpoch(StudyEpochCreateInput):
    uid: str = Field(
        ...,
        title="Uid",
        description="Uid of the Epoch",
    )
    epoch_name: str = Field(
        ..., title="Epoch name", description="Name of the epoch based on CT term"
    )
    epoch_subtype_name: str = Field(
        ...,
        title="Epoch sub type name",
        description="Name of the epoch sub type based on CT term",
    )
    epoch_type: str = Field(..., title="Type", description="Study Epoch type")
    start_day: Optional[int] = Field(
        None, title="Start Day", description="Study Epoch start day"
    )
    end_day: Optional[int] = Field(
        None, title="End Day", description="Study Epoch end day"
    )
    start_date: str = Field(
        ..., title="Modification date", description="Study Epoch last modification date"
    )
    status: str = Field(..., title="Status", description="Study Epoch status")
    user_initials: str = Field(
        ...,
        title="User Initials",
        description="Initials of user that created last modification",
    )
    possible_actions: List[str] = Field(
        ..., title="Possible actions", description="List of actions to perform on item"
    )
    change_description: Optional[str] = Field(
        "", title="Change Description", description="Description of change reasons"
    )
    study_visit_count: Optional[int] = Field(
        None, description="Count of Study Visits assigned to Study Epoch"
    )


class StudyEpochVersion(StudyEpoch):
    changes: Dict


class StudyEpochTypes(BaseModel):
    type: str = Field(..., title="Type", description="Study Epoch type")
    type_name: str
    subtype: str = Field(..., title="Subtype", description="Study Epoch subtype")
    subtype_name: str
