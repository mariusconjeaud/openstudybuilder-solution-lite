from datetime import datetime
from typing import Callable, Dict, List, Optional, Sequence, TypeVar

from pydantic import Field

from clinical_mdr_api.domain.concepts.activities.activity import ActivityAR
from clinical_mdr_api.domain.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domain.concepts.activities.activity_instance import (
    ActivityInstanceAR,
)
from clinical_mdr_api.domain.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domain.concepts.concept_base import ConceptVO
from clinical_mdr_api.models import Library
from clinical_mdr_api.models.activities.activity import (
    ActivityBase,
    ActivityHierarchySimpleModel,
)
from clinical_mdr_api.models.concept import ConceptInput
from clinical_mdr_api.models.ct_term import SimpleTermModel

_AggregateRootType = TypeVar("_AggregateRootType", bound=ActivityInstanceAR)


class ActivityInstance(ActivityBase):
    @classmethod
    def _get_term_model(
        cls, item: ConceptVO, uid_attribute: str, name_attribute: str
    ) -> Optional[SimpleTermModel]:
        uid_value = getattr(item, uid_attribute)
        if uid_value is None:
            return None
        return SimpleTermModel(term_uid=uid_value, name=getattr(item, name_attribute))

    @classmethod
    def from_activity_ar(
        cls,
        activity_ar: _AggregateRootType,
        find_activity_hierarchy_by_uid: Callable[[str], Optional[ActivityAR]],
        find_activity_subgroup_by_uid: Callable[[str], Optional[ActivitySubGroupAR]],
        find_activity_group_by_uid: Callable[[str], Optional[ActivityGroupAR]],
    ) -> "ActivityInstance":

        activity_subgroup_uids = [
            find_activity_hierarchy_by_uid(activity_uid).concept_vo.activity_subgroup
            for activity_uid in activity_ar.concept_vo.activity_uids
        ]
        activity_group_uids = [
            find_activity_subgroup_by_uid(subgroup_uid).concept_vo.activity_group
            for subgroup_uid in activity_subgroup_uids
        ]
        sdtm_variable = cls._get_term_model(
            activity_ar.concept_vo, "sdtm_variable_uid", "sdtm_variable_name"
        )
        sdtm_subcat = cls._get_term_model(
            activity_ar.concept_vo, "sdtm_subcat_uid", "sdtm_subcat_name"
        )
        sdtm_cat = cls._get_term_model(
            activity_ar.concept_vo, "sdtm_cat_uid", "sdtm_cat_name"
        )
        sdtm_domain = cls._get_term_model(
            activity_ar.concept_vo, "sdtm_domain_uid", "sdtm_domain_name"
        )
        specimen = cls._get_term_model(
            activity_ar.concept_vo, "specimen_uid", "specimen_name"
        )

        return cls(
            uid=activity_ar.uid,
            type=activity_ar.concept_vo.activity_type,
            name=activity_ar.name,
            name_sentence_case=activity_ar.concept_vo.name_sentence_case,
            definition=activity_ar.concept_vo.definition,
            abbreviation=activity_ar.concept_vo.abbreviation,
            topic_code=activity_ar.concept_vo.topic_code,
            adam_param_code=activity_ar.concept_vo.adam_param_code,
            legacy_description=activity_ar.concept_vo.legacy_description,
            sdtm_variable=sdtm_variable,
            sdtm_subcat=sdtm_subcat,
            sdtm_cat=sdtm_cat,
            sdtm_domain=sdtm_domain,
            activities=sorted(
                [
                    ActivityHierarchySimpleModel.from_activity_uid(
                        uid=activity,
                        find_activity_by_uid=find_activity_hierarchy_by_uid,
                    )
                    for activity in activity_ar.concept_vo.activity_uids
                ],
                key=lambda item: item.name,
            ),
            activity_subgroups=sorted(
                [
                    ActivityHierarchySimpleModel.from_activity_uid(
                        uid=activity_subgroup,
                        find_activity_by_uid=find_activity_subgroup_by_uid,
                    )
                    for activity_subgroup in activity_subgroup_uids
                ],
                key=lambda item: item.name,
            ),
            activity_groups=sorted(
                [
                    ActivityHierarchySimpleModel.from_activity_uid(
                        uid=activity_group,
                        find_activity_by_uid=find_activity_group_by_uid,
                    )
                    for activity_group in activity_group_uids
                ],
                key=lambda item: item.name,
            ),
            specimen=specimen,
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

    type: Optional[str] = Field(
        None, title="type", description="The subtype of ActivityInstance"
    )
    topic_code: str = Field(
        ...,
        title="topic_code",
        description="",
    )
    adam_param_code: str = Field(
        ...,
        title="adam_param_code",
        description="",
    )
    legacy_description: Optional[str] = Field(
        None,
        title="legacy_description",
        description="",
    )
    sdtm_variable: Optional[SimpleTermModel] = Field(
        ...,
        title="sdtm_variable",
        description="",
    )
    sdtm_subcat: Optional[SimpleTermModel] = Field(
        ...,
        title="sdtm_subcat",
        description="",
    )
    sdtm_cat: Optional[SimpleTermModel] = Field(
        ...,
        title="sdtm_cat",
        description="",
    )
    sdtm_domain: Optional[SimpleTermModel] = Field(
        ...,
        title="sdtm_domain",
        description="",
    )
    activities: Sequence[ActivityHierarchySimpleModel] = Field(
        ...,
        title="activities",
        description="List of activity unique identifiers",
    )
    activity_subgroups: Sequence[ActivityHierarchySimpleModel] = Field(
        ...,
        title="activity_subgroups",
        description="List of activity sub group unique identifiers",
    )
    activity_groups: Sequence[ActivityHierarchySimpleModel] = Field(
        ...,
        title="activity_groups",
        description="List of activity group unique identifiers",
    )
    specimen: Optional[SimpleTermModel] = Field(
        ...,
        title="specimen",
        description="",
    )
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str
    version: str
    change_description: str
    user_initials: str
    possible_actions: List[str] = Field(
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
    name_sentence_case: Optional[str] = Field(
        None,
        title="name_sentence_case",
        description="",
    )
    topic_code: Optional[str] = Field(
        None,
        title="topic_code",
        description="",
    )
    adam_param_code: Optional[str] = Field(
        None,
        title="adam_param_code",
        description="",
    )
    legacy_description: Optional[str] = Field(
        None,
        title="legacy_description",
        description="",
    )
    sdtm_variable: Optional[str] = Field(
        None,
        title="sdtm_variable",
        description="",
    )
    sdtm_subcat: Optional[str] = Field(
        None,
        title="sdtm_subcat",
        description="",
    )
    sdtm_cat: Optional[str] = Field(
        None,
        title="sdtm_cat",
        description="",
    )
    sdtm_domain: Optional[str] = Field(
        None,
        title="sdtm_domain",
        description="",
    )
    activities: Optional[Sequence[str]] = Field(
        None,
        title="activity",
        description="",
    )
    library_name: str


class ActivityInstanceEditInput(ConceptInput):
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
    topic_code: Optional[str] = Field(
        None,
        title="topic_code",
        description="",
    )
    adam_param_code: Optional[str] = Field(
        None,
        title="adam_param_code",
        description="",
    )
    legacy_description: Optional[str] = Field(
        None,
        title="legacy_description",
        description="",
    )
    sdtm_variable: Optional[str] = Field(
        None,
        title="sdtm_variable",
        description="",
    )
    sdtm_subcat: Optional[str] = Field(
        None,
        title="sdtm_subcat",
        description="",
    )
    sdtm_cat: Optional[str] = Field(
        None,
        title="sdtm_cat",
        description="",
    )
    sdtm_domain: Optional[str] = Field(
        None,
        title="sdtm_domain",
        description="",
    )
    specimen: Optional[str] = Field(
        None,
        title="specimen",
        description="",
    )
    activities: Optional[Sequence[str]] = Field(
        None,
        title="activity",
        description="",
    )
    change_description: str = Field(..., title="change_description", description="")


class ActivityInstanceVersion(ActivityInstance):
    """
    Class for storing ActivityInstance and calculation of differences
    """

    changes: Dict[str, bool] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective (e.g. name, start_date, ..)."
        ),
    )
