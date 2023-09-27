from datetime import datetime
from typing import Callable, Self, Sequence

from pydantic import Field

from clinical_mdr_api.domains.concepts.activities.activity import ActivityAR
from clinical_mdr_api.domains.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domains.concepts.activities.activity_instance import (
    ActivityInstanceAR,
)
from clinical_mdr_api.domains.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.models import Library
from clinical_mdr_api.models.biomedical_concepts.activity_instance_class import (
    CompactActivityInstanceClass,
)
from clinical_mdr_api.models.concepts.activities.activity import (
    ActivityBase,
    ActivityGrouping,
    ActivityHierarchySimpleModel,
    SimpleActivityGroup,
    SimpleActivityGrouping,
    SimpleActivityInstance,
    SimpleActivityInstanceClass,
    SimpleActivitySubGroup,
)
from clinical_mdr_api.models.concepts.concept import ConceptInput
from clinical_mdr_api.models.utils import BaseModel


class SimpleActivityItem(BaseModel):
    uid: str
    name: str | None = None
    activity_item_class_uid: str | None = None
    activity_item_class_name: str | None = None


class ActivityInstanceHierarchySimpleModel(BaseModel):
    activity: ActivityHierarchySimpleModel
    activity_subgroup: ActivityHierarchySimpleModel
    activity_group: ActivityHierarchySimpleModel


class ActivityInstanceGrouping(ActivityGrouping):
    activity_uid: str


class ActivityInstance(ActivityBase):
    @classmethod
    def from_activity_ar(
        cls,
        activity_ar: ActivityInstanceAR,
        find_activity_hierarchy_by_uid: Callable[[str], ActivityAR | None],
        find_activity_subgroup_by_uid: Callable[[str], ActivitySubGroupAR | None],
        find_activity_group_by_uid: Callable[[str], ActivityGroupAR | None],
    ) -> Self:
        return cls(
            uid=activity_ar.uid,
            name=activity_ar.name,
            name_sentence_case=activity_ar.concept_vo.name_sentence_case,
            definition=activity_ar.concept_vo.definition,
            abbreviation=activity_ar.concept_vo.abbreviation,
            topic_code=activity_ar.concept_vo.topic_code,
            adam_param_code=activity_ar.concept_vo.adam_param_code,
            legacy_description=activity_ar.concept_vo.legacy_description,
            activity_groupings=[
                ActivityInstanceHierarchySimpleModel(
                    activity_group=ActivityHierarchySimpleModel.from_activity_uid(
                        uid=activity_grouping.activity_group_uid,
                        find_activity_by_uid=find_activity_group_by_uid,
                    ),
                    activity_subgroup=ActivityHierarchySimpleModel.from_activity_uid(
                        uid=activity_grouping.activity_subgroup_uid,
                        find_activity_by_uid=find_activity_subgroup_by_uid,
                    ),
                    activity=ActivityHierarchySimpleModel.from_activity_uid(
                        uid=activity_grouping.activity_uid,
                        find_activity_by_uid=find_activity_hierarchy_by_uid,
                    ),
                )
                for activity_grouping in activity_ar.concept_vo.activity_groupings
            ],
            activity_instance_class=CompactActivityInstanceClass(
                uid=activity_ar.concept_vo.activity_instance_class_uid,
                name=activity_ar.concept_vo.activity_instance_class_name,
            ),
            activity_items=[
                SimpleActivityItem(
                    uid=activity_item_vo.uid,
                    name=activity_item_vo.name,
                    activity_item_class_uid=activity_item_vo.activity_item_class_uid,
                    activity_item_class_name=activity_item_vo.activity_item_class_name,
                )
                for activity_item_vo in activity_ar.concept_vo.activity_items
            ],
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

    topic_code: str | None = Field(
        None,
        title="topic_code",
        description="",
    )
    adam_param_code: str | None = Field(
        None,
        title="adam_param_code",
        description="",
    )
    legacy_description: str | None = Field(
        None,
        title="legacy_description",
        description="",
    )
    activity_groupings: Sequence[ActivityInstanceHierarchySimpleModel] = Field(
        ...,
        title="activity_groupings",
    )
    activity_instance_class: CompactActivityInstanceClass = Field(
        ...,
        title="The class of an activity instance",
        description="The uid and the name of the linked activity instance class",
    )
    activity_items: Sequence[SimpleActivityItem] = Field(
        ...,
        title="activity_items",
        description="List of activity items",
    )
    start_date: datetime
    end_date: datetime | None = Field(None, nullable=True)
    status: str
    version: str
    change_description: str
    user_initials: str
    possible_actions: list[str] = Field(
        ...,
        description=(
            "Holds those actions that can be performed on the ActivityInstances. "
            "Actions are: 'approve', 'edit', 'new_version'."
        ),
    )


class ActivityInstanceCreateInput(ConceptInput):
    name: str = Field(
        ...,
        title="name",
        description="The name or the actual value. E.g. 'Systolic Blood Pressure', 'Body Temperature', 'Metformin', ...",
    )
    name_sentence_case: str | None = Field(
        None,
        title="name_sentence_case",
        description="",
    )
    topic_code: str | None = Field(
        None,
        title="topic_code",
        description="",
    )
    adam_param_code: str | None = Field(
        None,
        title="adam_param_code",
        description="",
    )
    legacy_description: str | None = Field(
        None,
        title="legacy_description",
        description="",
    )
    activity_groupings: list[ActivityInstanceGrouping] | None = Field(
        None,
        title="activity_groupings",
        description="",
    )
    activity_instance_class_uid: str = Field(
        ...,
        title="activity_instance_class_uid",
        description="",
    )
    activity_item_uids: Sequence[str] | None = Field(
        None,
        title="activity_item_uids",
        description="",
    )
    library_name: str


class ActivityInstanceEditInput(ConceptInput):
    name: str | None = Field(
        None,
        title="name",
        description="The name or the actual value. E.g. 'Systolic Blood Pressure', 'Body Temperature', 'Metformin', ...",
    )
    name_sentence_case: str | None = Field(
        None,
        title="name_sentence_case",
        description="",
    )
    topic_code: str | None = Field(
        None,
        title="topic_code",
        description="",
    )
    adam_param_code: str | None = Field(
        None,
        title="adam_param_code",
        description="",
    )
    legacy_description: str | None = Field(
        None,
        title="legacy_description",
        description="",
    )
    activity_instance_class_uid: str | None = Field(
        None,
        title="activity_instance_class_uid",
        description="",
    )
    activity_groupings: list[ActivityInstanceGrouping] | None = Field(
        None,
        title="activity_groupings",
        description="",
    )
    activity_item_uids: list[str] | None = Field(
        None,
        title="activity_item_uids",
        description="",
    )
    change_description: str = Field(..., title="change_description", description="")


class ActivityInstanceVersion(ActivityInstance):
    """
    Class for storing ActivityInstance and calculation of differences
    """

    changes: dict[str, bool] | None = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective (e.g. name, start_date, ..)."
        ),
        nullable=True,
    )


class SimpleActivity(BaseModel):
    name: str | None = Field(
        None,
        title="name",
        description="",
    )
    definition: str | None = Field(
        None,
        title="name",
        description="",
    )
    library_name: str | None = Field(
        None,
        title="name",
        description="",
    )


class SimpleActivityItemClass(BaseModel):
    name: str = Field(..., title="name", description="")
    order: int = Field(..., title="order", description="")
    mandatory: bool = Field(..., title="mandatory", description="")
    role_name: str = Field(..., title="role_name", description="")
    data_type_name: str = Field(..., title="data_type_name", description="")


class SimplifiedActivityItem(BaseModel):
    name: str = Field(..., title="name", description="")
    ct_term_name: str | None = Field(None, title="name", description="")
    unit_definition_name: str | None = Field(None, title="name", description="")
    activity_item_class: SimpleActivityItemClass = Field(...)


class SimpleActivityInstanceGrouping(SimpleActivityGrouping):
    activity: SimpleActivity = Field(...)


class ActivityInstanceOverview(BaseModel):
    activity_groupings: list[SimpleActivityInstanceGrouping] = Field(...)
    activity_instance: SimpleActivityInstance = Field(...)
    activity_items: list[SimplifiedActivityItem] = Field(...)

    @classmethod
    def from_repository_input(cls, overview: dict):
        return cls(
            activity_groupings=[
                SimpleActivityInstanceGrouping(
                    activity=SimpleActivity(
                        name=activity_grouping.get("activity_value").get("name"),
                        definition=activity_grouping.get("activity_value").get(
                            "definition"
                        ),
                        library_name=activity_grouping.get("activity_library_name"),
                    ),
                    activity_group=SimpleActivityGroup(
                        name=activity_grouping.get("activity_group_value").get("name"),
                        definition=activity_grouping.get("activity_group_value").get(
                            "definition"
                        ),
                    ),
                    activity_subgroup=SimpleActivitySubGroup(
                        name=activity_grouping.get("activity_subgroup_value").get(
                            "name"
                        ),
                        definition=activity_grouping.get("activity_subgroup_value").get(
                            "definition"
                        ),
                    ),
                )
                for activity_grouping in overview.get("hierarchy")
            ],
            activity_instance=SimpleActivityInstance(
                name=overview.get("activity_instance_value").get("name"),
                name_sentence_case=overview.get("activity_instance_value").get(
                    "name_sentence_case"
                ),
                abbreviation=overview.get("activity_instance_value").get(
                    "abbreviation"
                ),
                definition=overview.get("activity_instance_value").get("definition"),
                adam_param_code=overview.get("activity_instance_value").get(
                    "adam_param_code"
                ),
                topic_code=overview.get("activity_instance_value").get("topic_code"),
                library_name=overview.get("instance_library_name"),
                activity_instance_class=SimpleActivityInstanceClass(
                    name=overview.get("activity_instance_class").get("name")
                ),
            ),
            activity_items=[
                SimplifiedActivityItem(
                    name=activity_item.get("activity_item").get("name"),
                    ct_term_name=(activity_item.get("ct_term") or {}).get("name"),
                    unit_definition_name=(
                        activity_item.get("unit_definition") or {}
                    ).get("name"),
                    activity_item_class=SimpleActivityItemClass(
                        name=activity_item.get("activity_item_class").get("name"),
                        order=activity_item.get("activity_item_class").get("order"),
                        mandatory=activity_item.get("activity_item_class").get(
                            "mandatory"
                        ),
                        role_name=activity_item.get("activity_item_class_role"),
                        data_type_name=activity_item.get(
                            "activity_item_class_data_type"
                        ),
                    ),
                )
                for activity_item in overview.get("activity_items")
            ],
        )
