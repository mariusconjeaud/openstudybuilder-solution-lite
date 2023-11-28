from typing import Self

from pydantic import Field

from clinical_mdr_api.domains.concepts.activities.activity_item import ActivityItemAR
from clinical_mdr_api.models import Library
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
        source="has_ct_term.uid",
    )
    name: str | None = Field(
        None,
        title="ct term name",
        description="",
        source="has_ct_term.has_name_root.has_latest_value.name",
    )


class CompactUnitDefinition(BaseModel):
    class Config:
        orm_mode = True

    uid: str | None = Field(
        None,
        title="unit definition uid",
        description="",
        source="has_unit_definition.uid",
    )
    name: str | None = Field(
        None,
        title="unit definition name",
        description="",
        source="has_unit_definition.has_latest_value.name",
    )


class ActivityItem(BaseModel):
    class Config:
        orm_mode = True

    activity_item_class: CompactActivityItemClass = Field(...)
    ct_terms: list[CompactCTTerm] = Field([])
    unit_definitions: list[CompactUnitDefinition] = Field([])

    @classmethod
    def from_activity_item_ar(
        cls,
        activity_item_ar: ActivityItemAR,
    ) -> Self:
        return cls(
            activity_item_class=CompactActivityItemClass(
                uid=activity_item_ar.activity_item_vo.activity_item_class_uid,
                name=activity_item_ar.activity_item_vo.activity_item_class_name,
            ),
            ct_terms=[
                CompactCTTerm(
                    uid=term.uid,
                    name=term.name,
                )
                for term in activity_item_ar.activity_item_vo.ct_terms
            ],
            unit_definitions=[
                CompactUnitDefinition(
                    uid=unit.uid,
                    name=unit.name,
                )
                for unit in activity_item_ar.activity_item_vo.unit_definitions
            ],
        )


class ActivityItemCreateInput(BaseModel):
    activity_item_class_uid: str
    ct_term_uids: list[str]
    unit_definition_uids: list[str]


class ActivityItemEditInput(ActivityItemCreateInput):
    activity_item_class_uid: str | None = None
    ct_term_uids: list[str] | None = None
    unit_definition_uids: list[str] | None = None
    change_description: str | None = None
