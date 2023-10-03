from datetime import datetime
from typing import Callable, Self

from pydantic import Field

from clinical_mdr_api.domains.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domains.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domains.study_selections.study_soa_footnote import (
    SoAItemType,
    StudySoAFootnoteVO,
    StudySoAFootnoteVOHistory,
)
from clinical_mdr_api.domains.syntax_instances.footnote import FootnoteAR
from clinical_mdr_api.domains.syntax_templates.footnote_template import (
    FootnoteTemplateAR,
)
from clinical_mdr_api.models import Footnote, FootnoteCreateInput, FootnoteTemplate
from clinical_mdr_api.models.utils import BaseModel


class ReferencedItem(BaseModel):
    item_uid: str = Field(
        ...,
    )
    item_name: str | None = Field(
        None,
    )
    item_type: SoAItemType = Field(
        ...,
    )


class StudySoAFootnote(BaseModel):
    uid: str = Field(
        ...,
        title="The uid of the study footnote",
    )
    study_uid: str = Field(
        ...,
        title="The uid of the study",
    )
    order: int = Field(
        ...,
        title="The uid of the study",
    )
    modified: datetime | None = Field(
        None,
        title="start_date",
        description="The most recent point in time when the study soa footnote was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )
    referenced_items: list[ReferencedItem] = Field([])
    footnote: Footnote | None = Field(None, nullable=True)
    footnote_template: FootnoteTemplate | None = Field(None, nullable=True)

    @classmethod
    def from_study_soa_footnote_vo(
        cls,
        study_soa_footnote_vo: StudySoAFootnoteVO,
        find_footnote_by_uid: Callable[[str], FootnoteAR | None],
        find_footnote_template_by_uid: Callable[[str], FootnoteTemplateAR | None],
        find_activity_group_by_uid: Callable[[str], ActivityGroupAR | None],
        find_activity_subgroup_by_uid: Callable[[str], ActivitySubGroupAR | None],
    ) -> Self:
        footnote = None
        footnote_template = None
        if study_soa_footnote_vo.footnote_uid:
            footnote = Footnote.from_footnote_ar(
                find_footnote_by_uid(study_soa_footnote_vo.footnote_uid)
            )
        elif study_soa_footnote_vo.footnote_template_uid:
            footnote_template = FootnoteTemplate.from_footnote_template_ar(
                find_footnote_template_by_uid(
                    study_soa_footnote_vo.footnote_template_uid
                ),
                find_activity_group_by_uid=find_activity_group_by_uid,
                find_activity_subgroup_by_uid=find_activity_subgroup_by_uid,
            )
        return cls(
            uid=study_soa_footnote_vo.uid,
            study_uid=study_soa_footnote_vo.study_uid,
            order=study_soa_footnote_vo.footnote_number,
            referenced_items=[
                ReferencedItem(
                    item_uid=ref_item.item_uid,
                    item_name=ref_item.item_name,
                    item_type=ref_item.item_type,
                )
                for ref_item in study_soa_footnote_vo.referenced_items
            ],
            footnote=footnote,
            footnote_template=footnote_template,
            modified=study_soa_footnote_vo.modified,
        )


class StudySoAFootnoteCreateInput(BaseModel):
    footnote_uid: str | None = Field(
        None,
        title="The uid of the footnote",
    )
    footnote_template_uid: str | None = Field(
        None,
        title="The uid of the footnote template",
    )
    referenced_items: list[ReferencedItem] = Field(
        [],
        title="The list of items referenced by a single footnote",
    )


class StudySoAFootnoteCreateFootnoteInput(BaseModel):
    footnote_data: FootnoteCreateInput = Field(
        ...,
        title="footnote_data",
        description="Footnote data to create new footnote",
    )
    referenced_items: list[ReferencedItem] = Field(
        [],
        title="The list of items referenced by a single footnote",
    )


class StudySoAFootnoteEditInput(BaseModel):
    footnote_uid: str | None = Field(
        None,
        title="The uid of the footnote",
    )
    footnote_template_uid: str | None = Field(
        None,
        title="The uid of the footnote template",
    )
    referenced_items: list[ReferencedItem] | None = Field(
        None,
        title="The list of items referenced by a single footnote",
    )


class StudySoAFootnoteHistory(StudySoAFootnote):
    change_type: str = Field(
        ...,
        title="type of action",
        description="type of action",
    )
    start_date: datetime = Field(
        ...,
        title="start_date",
    )
    end_date: datetime | None = Field(
        None,
        title="end_date",
    )

    @classmethod
    def from_study_soa_footnote_vo_history(
        cls,
        study_soa_footnote_vo: StudySoAFootnoteVOHistory,
        find_footnote_by_uid: Callable[[str], FootnoteAR | None],
        find_footnote_template_by_uid: Callable[[str], FootnoteTemplateAR | None],
        find_activity_group_by_uid: Callable[[str], ActivityGroupAR | None],
        find_activity_subgroup_by_uid: Callable[[str], ActivitySubGroupAR | None],
    ) -> Self:
        footnote = None
        footnote_template = None
        if study_soa_footnote_vo.footnote_uid:
            footnote = Footnote.from_footnote_ar(
                find_footnote_by_uid(study_soa_footnote_vo.footnote_uid)
            )
        elif study_soa_footnote_vo.footnote_template_uid:
            footnote_template = FootnoteTemplate.from_footnote_template_ar(
                find_footnote_template_by_uid(
                    study_soa_footnote_vo.footnote_template_uid
                ),
                find_activity_group_by_uid=find_activity_group_by_uid,
                find_activity_subgroup_by_uid=find_activity_subgroup_by_uid,
            )
        return cls(
            uid=study_soa_footnote_vo.uid,
            study_uid=study_soa_footnote_vo.study_uid,
            order=study_soa_footnote_vo.footnote_number,
            referenced_items=[
                ReferencedItem(
                    item_uid=ref_item.item_uid,
                    item_name=ref_item.item_name,
                    item_type=ref_item.item_type,
                )
                for ref_item in study_soa_footnote_vo.referenced_items
            ],
            footnote=footnote,
            footnote_template=footnote_template,
            start_date=study_soa_footnote_vo.start_date,
            end_date=study_soa_footnote_vo.end_date,
            change_type=study_soa_footnote_vo.change_type,
        )


class StudySoAFootnoteVersion(StudySoAFootnoteHistory):
    changes: dict
