from typing import Callable, Dict, List, Optional

from pydantic import Field, validator

from clinical_mdr_api.domain.concepts.activities.activity import ActivityAR
from clinical_mdr_api.domain.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domain.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domain.concepts.concept_base import ConceptARBase
from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryItemStatus,
    ObjectAction,
)
from clinical_mdr_api.models.concept import Concept, ConceptInput
from clinical_mdr_api.models.library import Library
from clinical_mdr_api.models.utils import BaseModel


class ActivityHierarchySimpleModel(BaseModel):
    @classmethod
    def from_activity_uid(
        cls, uid: str, find_activity_by_uid: Callable[[str], Optional[ConceptARBase]]
    ) -> Optional["ActivityHierarchySimpleModel"]:

        if uid is not None:
            activity = find_activity_by_uid(uid)

            if activity is not None:
                simple_activity_model = cls(uid=uid, name=activity.concept_vo.name)
            else:
                simple_activity_model = cls(uid=uid, name=None)
        else:
            simple_activity_model = None
        return simple_activity_model

    uid: str = Field(
        ...,
        title="uid",
        description="",
    )
    name: Optional[str] = Field(None, title="name", description="")


class ActivityBase(Concept):
    possible_actions: List[str] = Field(
        ...,
        description=(
            "Holds those actions that can be performed on the ActivityInstances. "
            "Actions are: 'approve', 'edit', 'new_version'."
        ),
    )

    @validator("possible_actions", pre=True, always=True)
    # pylint:disable=no-self-argument,unused-argument
    def validate_possible_actions(cls, value, values):
        if values["status"] == LibraryItemStatus.DRAFT.value and values[
            "version"
        ].startswith("0"):
            return [
                ObjectAction.APPROVE.value,
                ObjectAction.DELETE.value,
                ObjectAction.EDIT.value,
            ]
        if values["status"] == LibraryItemStatus.DRAFT.value:
            return [ObjectAction.APPROVE.value, ObjectAction.EDIT.value]
        if values["status"] == LibraryItemStatus.FINAL.value:
            return [
                ObjectAction.INACTIVATE.value,
                ObjectAction.NEWVERSION.value,
            ]
        if values["status"] == LibraryItemStatus.RETIRED.value:
            return [ObjectAction.REACTIVATE.value]
        return []


class ActivitySubGroupSimpleModel(ActivityHierarchySimpleModel):
    class Config:
        orm_mode = True

    uid: str = Field(
        ...,
        title="uid",
        description="",
        source="has_latest_value.in_subgroup.has_latest_value.uid",
    )
    name: Optional[str] = Field(
        None, title="name", description="", source="has_latest_value.in_subgroup.name"
    )


class ActivityGroupSimpleModel(ActivityHierarchySimpleModel):
    class Config:
        orm_mode = True

    uid: str = Field(
        ...,
        title="uid",
        description="",
        source="has_latest_value.in_subgroup.in_group.has_latest_value.uid",
    )
    name: Optional[str] = Field(
        None,
        title="name",
        description="",
        source="has_latest_value.in_subgroup.in_group.name",
    )


class Activity(ActivityBase):
    @classmethod
    def from_activity_ar(
        cls,
        activity_ar: ActivityAR,
        find_activity_subgroup_by_uid: Callable[[str], Optional[ActivitySubGroupAR]],
        find_activity_group_by_uid: Callable[[str], Optional[ActivityGroupAR]],
    ) -> "Activity":
        activity_group_uid = find_activity_subgroup_by_uid(
            activity_ar.concept_vo.activity_subgroup
        ).concept_vo.activity_group
        return cls(
            uid=activity_ar.uid,
            name=activity_ar.name,
            name_sentence_case=activity_ar.concept_vo.name_sentence_case,
            definition=activity_ar.concept_vo.definition,
            abbreviation=activity_ar.concept_vo.abbreviation,
            activity_subgroup=ActivityHierarchySimpleModel.from_activity_uid(
                uid=activity_ar.concept_vo.activity_subgroup,
                find_activity_by_uid=find_activity_subgroup_by_uid,
            ),
            activity_group=ActivityHierarchySimpleModel.from_activity_uid(
                uid=activity_group_uid,
                find_activity_by_uid=find_activity_group_by_uid,
            ),
            library_name=Library.from_library_vo(activity_ar.library).name,
            start_date=activity_ar.item_metadata.start_date,
            end_date=activity_ar.item_metadata.end_date,
            status=activity_ar.item_metadata.status.value,
            version=activity_ar.item_metadata.version,
            change_description=activity_ar.item_metadata.change_description,
            user_initials=activity_ar.item_metadata.user_initials,
            possible_actions=sorted(
                [_.value for _ in activity_ar.get_possible_actions()]
            ),
        )

    activity_subgroup: Optional[ActivityHierarchySimpleModel] = Field(
        None,
        title="Activity Sub Group",
        description="Activity Sub Group",
    )

    activity_group: Optional[ActivityHierarchySimpleModel] = Field(
        None,
        title="Activity Sub Group",
        description="Activity Sub Group",
    )


class ActivityORM(Activity):
    class Config:
        orm_mode = True

    activity_subgroup: Optional[ActivitySubGroupSimpleModel] = Field(
        None,
        title="Activity Sub Group",
        description="Activity Sub Group",
    )

    activity_group: Optional[ActivityGroupSimpleModel] = Field(
        None,
        title="Activity Sub Group",
        description="Activity Sub Group",
    )


class ActivityCommonInput(ConceptInput):
    name: Optional[str] = Field(
        None,
        title="name",
        description="The name or the actual value. E.g. 'Systolic Blood Pressure', 'Body Temperature', 'Metformin', ...",
    )
    name_sentence_case: Optional[str] = Field(
        None,
        title="name_sentence_case",
        description="",
    )


class ActivityInput(ActivityCommonInput):
    activity_subgroup: Optional[str] = None


class ActivityEditInput(ActivityInput):
    change_description: str = Field(None, title="change_description", description="")


class ActivityCreateInput(ActivityInput):
    library_name: str


class ActivityVersion(Activity):
    """
    Class for storing Activity and calculation of differences
    """

    changes: Dict[str, bool] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective (e.g. name, start_date, ..)."
        ),
    )
