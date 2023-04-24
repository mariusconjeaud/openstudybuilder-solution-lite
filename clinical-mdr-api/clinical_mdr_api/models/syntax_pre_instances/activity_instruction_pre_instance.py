from datetime import datetime
from typing import Callable, Dict, List, Optional

from pydantic import Field

from clinical_mdr_api.domain.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domain.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domain.syntax_pre_instances.activity_instruction_pre_instance import (
    ActivityInstructionPreInstanceAR,
)
from clinical_mdr_api.models.activities.activity import Activity
from clinical_mdr_api.models.activities.activity_group import ActivityGroup
from clinical_mdr_api.models.activities.activity_sub_group import ActivitySubGroup
from clinical_mdr_api.models.dictionary_term import DictionaryTerm
from clinical_mdr_api.models.library import Library
from clinical_mdr_api.models.syntax_pre_instances.generic_pre_instance import (
    PreInstanceCreateInput,
)
from clinical_mdr_api.models.template_parameter_term import (
    IndexedTemplateParameterTerm,
    MultiTemplateParameterTerm,
)
from clinical_mdr_api.models.utils import BaseModel


class ActivityInstructionPreInstance(BaseModel):
    uid: Optional[str] = None
    template_uid: str
    name: Optional[str] = None
    name_plain: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    version: Optional[str] = None
    change_description: Optional[str] = None
    user_initials: Optional[str] = None
    parameter_terms: Optional[List[MultiTemplateParameterTerm]] = Field(
        None,
        description=(
            """Holds the parameter terms that are used within the activity instruction.
            The terms are ordered as they occur in the activity instruction name."""
        ),
    )
    indications: Optional[List[DictionaryTerm]] = Field(
        None,
        description="The study indications, conditions, diseases or disorders in scope for the pre instance.",
    )
    activities: Optional[List[Activity]] = Field(
        None, description="The activities in scope for the pre instance"
    )
    activity_groups: Optional[List[ActivityGroup]] = Field(
        None, description="The activity groups in scope for the pre instance"
    )
    activity_subgroups: Optional[List[ActivitySubGroup]] = Field(
        None, description="The activity sub groups in scope for the pre instance"
    )
    library: Optional[Library] = None
    possible_actions: Optional[List[str]] = None

    @classmethod
    def from_activity_instruction_pre_instance_ar(
        cls,
        activity_instruction_pre_instance_ar: ActivityInstructionPreInstanceAR,
        find_activity_subgroup_by_uid: Callable[[str], Optional[ActivitySubGroupAR]],
        find_activity_group_by_uid: Callable[[str], Optional[ActivityGroupAR]],
    ) -> "ActivityInstructionPreInstance":
        parameter_terms: List[MultiTemplateParameterTerm] = []
        for position, parameter in enumerate(
            activity_instruction_pre_instance_ar.get_parameters()
        ):
            terms: List[IndexedTemplateParameterTerm] = []
            for index, parameter_term in enumerate(parameter.parameters):
                pv = IndexedTemplateParameterTerm(
                    index=index + 1,
                    uid=parameter_term.uid,
                    name=parameter_term.value,
                    type=parameter.parameter_name,
                )
                terms.append(pv)
            conjunction = parameter.conjunction

            parameter_terms.append(
                MultiTemplateParameterTerm(
                    conjunction=conjunction, position=position + 1, terms=terms
                )
            )
        return cls(
            uid=activity_instruction_pre_instance_ar.uid,
            template_uid=activity_instruction_pre_instance_ar.template_uid,
            name=activity_instruction_pre_instance_ar.name,
            name_plain=activity_instruction_pre_instance_ar.name_plain,
            start_date=activity_instruction_pre_instance_ar.item_metadata.start_date,
            end_date=activity_instruction_pre_instance_ar.item_metadata.end_date,
            status=activity_instruction_pre_instance_ar.item_metadata.status.value,
            version=activity_instruction_pre_instance_ar.item_metadata.version,
            change_description=activity_instruction_pre_instance_ar.item_metadata.change_description,
            user_initials=activity_instruction_pre_instance_ar.item_metadata.user_initials,
            library=Library.from_library_vo(
                activity_instruction_pre_instance_ar.library
            ),
            parameter_terms=parameter_terms,
            indications=[
                DictionaryTerm.from_dictionary_term_ar(indication)
                for indication in activity_instruction_pre_instance_ar.indications
            ]
            if activity_instruction_pre_instance_ar.indications
            else None,
            activities=[
                Activity.from_activity_ar(
                    activity,
                    find_activity_subgroup_by_uid,
                    find_activity_group_by_uid,
                )
                for activity in activity_instruction_pre_instance_ar.activities
            ]
            if activity_instruction_pre_instance_ar.activities
            else None,
            activity_groups=[
                ActivityGroup.from_activity_ar(group)
                for group in activity_instruction_pre_instance_ar.activity_groups
            ]
            if activity_instruction_pre_instance_ar.activity_groups
            else None,
            activity_subgroups=[
                ActivitySubGroup.from_activity_ar(group, find_activity_group_by_uid)
                for group in activity_instruction_pre_instance_ar.activity_subgroups
            ]
            if activity_instruction_pre_instance_ar.activity_subgroups
            else None,
            possible_actions=sorted(
                {
                    _.value
                    for _ in activity_instruction_pre_instance_ar.get_possible_actions()
                }
            ),
        )


class ActivityInstructionPreInstanceVersion(ActivityInstructionPreInstance):
    """
    Class for storing ActivityInstruction Pre Instances and calculation of differences
    """

    changes: Dict[str, bool] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the activity instruction (e.g. name, start_date, ..)."
        ),
    )


class ActivityInstructionPreInstanceCreateInput(PreInstanceCreateInput):
    indication_uids: List[str]
    activity_uids: List[str]
    activity_group_uids: List[str]
    activity_subgroup_uids: List[str]
