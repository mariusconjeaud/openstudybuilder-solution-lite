from typing import Self

from pydantic import Field, validator

from clinical_mdr_api.domains.biomedical_concepts.activity_item import ActivityItemAR
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemStatus,
    ObjectAction,
)
from clinical_mdr_api.models import Library
from clinical_mdr_api.models.concepts.concept import VersionProperties
from clinical_mdr_api.models.utils import BaseModel


class CompactActivityItemClass(BaseModel):
    class Config:
        orm_mode = True

    uid: str = Field(
        ...,
        title="activity item class uid",
        description="",
        source="has_activity_item_class.uid",
    )
    name: str | None = Field(
        None,
        title="activity item class name",
        description="",
        source="has_activity_item_class.has_latest_value.name",
    )


class CompactCTTerm(BaseModel):
    class Config:
        orm_mode = True

    uid: str | None = Field(
        None,
        title="ct term uid",
        description="",
        source="has_latest_value.has_ct_term.uid",
    )
    name: str | None = Field(
        None,
        title="ct term name",
        description="",
        source="has_latest_value.has_ct_term.has_name_root.has_latest_value.name",
    )


class CompactUnitDefinition(BaseModel):
    class Config:
        orm_mode = True

    uid: str | None = Field(
        None,
        title="unit definition uid",
        description="",
        source="has_latest_value.has_unit_definition.uid",
    )
    name: str | None = Field(
        None,
        title="unit definition name",
        description="",
        source="has_latest_value.has_unit_definition.has_latest_value.name",
    )


class ActivityItem(VersionProperties):
    class Config:
        orm_mode = True

    uid: str = Field(
        None,
        title="uid",
        description="",
        source="uid",
    )
    name: str = Field(
        None, title="name", description="", source="has_latest_value.name"
    )
    activity_item_class: CompactActivityItemClass = Field(...)
    ct_term: CompactCTTerm | None = Field(None)
    unit_definition: CompactUnitDefinition | None = Field(None)
    library_name: str = Field(
        ...,
        title="library_name",
        description="",
        source="has_library.name",
    )
    possible_actions: list[str] = Field(
        ...,
        description=(
            "Holds those actions that can be performed on the ActivityItemClasses. "
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

    @classmethod
    def from_activity_item_ar(
        cls,
        activity_item_ar: ActivityItemAR,
    ) -> Self:
        return cls(
            uid=activity_item_ar.uid,
            name=activity_item_ar.name,
            activity_item_class=CompactActivityItemClass(
                uid=activity_item_ar.activity_item_vo.activity_item_class_uid,
                name=activity_item_ar.activity_item_vo.activity_item_class_name,
            ),
            ct_term=CompactCTTerm(
                uid=activity_item_ar.activity_item_vo.ct_term_uid,
                name=activity_item_ar.activity_item_vo.ct_term_name,
            ),
            unit_definition=CompactUnitDefinition(
                uid=activity_item_ar.activity_item_vo.unit_definition_uid,
                name=activity_item_ar.activity_item_vo.unit_definition_name,
            ),
            library_name=Library.from_library_vo(activity_item_ar.library).name,
            start_date=activity_item_ar.item_metadata.start_date,
            end_date=activity_item_ar.item_metadata.end_date,
            status=activity_item_ar.item_metadata.status.value,
            version=activity_item_ar.item_metadata.version,
            change_description=activity_item_ar.item_metadata.change_description,
            user_initials=activity_item_ar.item_metadata.user_initials,
            possible_actions=sorted(
                [_.value for _ in activity_item_ar.get_possible_actions()]
            ),
        )


class ActivityItemCreateInput(BaseModel):
    name: str
    activity_item_class_uid: str
    library_name: str
    ct_term_uid: str | None
    unit_definition_uid: str | None


class ActivityItemEditInput(ActivityItemCreateInput):
    name: str | None = None
    activity_item_class_uid: str | None = None
    ct_term_uid: str | None = None
    unit_definition_uid: str | None = None
    library_name: str | None = None
    change_description: str | None = None


class ActivityItemVersion(ActivityItem):
    """
    Class for storing ActivityItem and calculation of differences
    """

    changes: dict[str, bool] | None = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective (e.g. name, start_date, ..)."
        ),
        nullable=True,
    )
