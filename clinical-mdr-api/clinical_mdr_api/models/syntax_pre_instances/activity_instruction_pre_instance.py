from datetime import datetime
from typing import Callable, Self

from pydantic import Field

from clinical_mdr_api.domains.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domains.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domains.syntax_pre_instances.activity_instruction_pre_instance import (
    ActivityInstructionPreInstanceAR,
)
from clinical_mdr_api.models.concepts.activities.activity import Activity
from clinical_mdr_api.models.concepts.activities.activity_group import ActivityGroup
from clinical_mdr_api.models.concepts.activities.activity_sub_group import (
    ActivitySubGroup,
)
from clinical_mdr_api.models.dictionaries.dictionary_term import DictionaryTerm
from clinical_mdr_api.models.libraries.library import Library
from clinical_mdr_api.models.syntax_pre_instances.generic_pre_instance import (
    PreInstanceInput,
)
from clinical_mdr_api.models.syntax_templates.template_parameter_term import (
    IndexedTemplateParameterTerm,
    MultiTemplateParameterTerm,
)
from clinical_mdr_api.models.utils import BaseModel


class ActivityInstructionPreInstance(BaseModel):
    uid: str
    sequence_id: str | None = Field(None, nullable=True)
    template_uid: str
    template_name: str
    name: str | None = Field(None, nullable=True)
    name_plain: str | None = Field(None, nullable=True)
    start_date: datetime | None = Field(None, nullable=True)
    end_date: datetime | None = Field(None, nullable=True)
    status: str | None = Field(None, nullable=True)
    version: str | None = Field(None, nullable=True)
    change_description: str | None = Field(None, nullable=True)
    user_initials: str | None = Field(None, nullable=True)
    parameter_terms: list[MultiTemplateParameterTerm] = Field(
        [],
        description=(
            """Holds the parameter terms that are used within the activity instruction.
            The terms are ordered as they occur in the activity instruction name."""
        ),
    )
    indications: list[DictionaryTerm] = Field(
        [],
        description="The study indications, conditions, diseases or disorders in scope for the pre-instance.",
    )
    activities: list[Activity] = Field(
        [], description="The activities in scope for the pre-instance"
    )
    activity_groups: list[ActivityGroup] = Field(
        [], description="The activity groups in scope for the pre-instance"
    )
    activity_subgroups: list[ActivitySubGroup] = Field(
        [], description="The activity sub groups in scope for the pre-instance"
    )
    library: Library | None = None
    possible_actions: list[str] = Field([])

    @classmethod
    def from_activity_instruction_pre_instance_ar(
        cls,
        activity_instruction_pre_instance_ar: ActivityInstructionPreInstanceAR,
        find_activity_subgroup_by_uid: Callable[[str], ActivitySubGroupAR | None],
        find_activity_group_by_uid: Callable[[str], ActivityGroupAR | None],
    ) -> Self:
        parameter_terms: list[MultiTemplateParameterTerm] = []
        for position, parameter in enumerate(
            activity_instruction_pre_instance_ar.get_parameters()
        ):
            terms: list[IndexedTemplateParameterTerm] = []
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
            sequence_id=activity_instruction_pre_instance_ar.sequence_id,
            template_uid=activity_instruction_pre_instance_ar.template_uid,
            template_name=activity_instruction_pre_instance_ar.template_name,
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
            indications=sorted(
                [
                    DictionaryTerm.from_dictionary_term_ar(indication)
                    for indication in activity_instruction_pre_instance_ar.indications
                ],
                key=lambda item: item.term_uid,
            )
            if activity_instruction_pre_instance_ar.indications
            else [],
            activities=sorted(
                [
                    Activity.from_activity_ar(
                        activity,
                        find_activity_subgroup_by_uid,
                        find_activity_group_by_uid,
                    )
                    for activity in activity_instruction_pre_instance_ar.activities
                ],
                key=lambda item: item.uid,
            )
            if activity_instruction_pre_instance_ar.activities
            else [],
            activity_groups=sorted(
                [
                    ActivityGroup.from_activity_ar(group)
                    for group in activity_instruction_pre_instance_ar.activity_groups
                ],
                key=lambda item: item.uid,
            )
            if activity_instruction_pre_instance_ar.activity_groups
            else [],
            activity_subgroups=sorted(
                [
                    ActivitySubGroup.from_activity_ar(group, find_activity_group_by_uid)
                    for group in activity_instruction_pre_instance_ar.activity_subgroups
                ],
                key=lambda item: item.uid,
            )
            if activity_instruction_pre_instance_ar.activity_subgroups
            else [],
            possible_actions=sorted(
                {
                    _.value
                    for _ in activity_instruction_pre_instance_ar.get_possible_actions()
                }
            ),
        )


class ActivityInstructionPreInstanceCreateInput(PreInstanceInput):
    indication_uids: list[str]
    activity_uids: list[str]
    activity_group_uids: list[str]
    activity_subgroup_uids: list[str]


class ActivityInstructionPreInstanceEditInput(PreInstanceInput):
    change_description: str = Field(
        ...,
        description="A short description about what has changed compared to the previous version.",
    )


class ActivityInstructionPreInstanceIndexingsInput(BaseModel):
    indication_uids: list[str] | None = Field(
        None,
        description="A list of UID of the study indications, conditions, diseases or disorders to attach the pre-instance to.",
    )
    activity_uids: list[str] | None = Field(
        None,
        description="A list of UID of the activities to attach the pre-instance to.",
    )
    activity_group_uids: list[str] | None = Field(
        None,
        description="A list of UID of the activity groups to attach the pre-instance to.",
    )
    activity_subgroup_uids: list[str] | None = Field(
        None,
        description="A list of UID of the activity subgroups to attach the pre-instance to.",
    )


class ActivityInstructionPreInstanceVersion(ActivityInstructionPreInstance):
    """
    Class for storing ActivityInstruction Pre-Instances and calculation of differences
    """

    changes: dict[str, bool] | None = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the activity instruction (e.g. name, start_date, ..)."
        ),
        nullable=True,
    )
