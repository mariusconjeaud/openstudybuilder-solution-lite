from datetime import datetime
from typing import Callable, Self

from pydantic import Field, conlist

from clinical_mdr_api.domains.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domains.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domains.syntax_templates.activity_instruction_template import (
    ActivityInstructionTemplateAR,
)
from clinical_mdr_api.models.concepts.activities.activity import Activity
from clinical_mdr_api.models.concepts.activities.activity_group import ActivityGroup
from clinical_mdr_api.models.concepts.activities.activity_sub_group import (
    ActivitySubGroup,
)
from clinical_mdr_api.models.dictionaries.dictionary_term import DictionaryTerm
from clinical_mdr_api.models.libraries.library import ItemCounts, Library
from clinical_mdr_api.models.syntax_templates.template_parameter import (
    TemplateParameter,
)
from clinical_mdr_api.models.syntax_templates.template_parameter_term import (
    IndexedTemplateParameterTerm,
    MultiTemplateParameterTerm,
)
from clinical_mdr_api.models.utils import BaseModel


class ActivityInstructionTemplateName(BaseModel):
    name: str = Field(
        ...,
        description="The actual value/content. It may include parameters referenced by simple strings in square brackets [].",
    )
    name_plain: str = Field(
        ...,
        description="The plain text version of the name property, stripped of HTML tags",
    )
    guidance_text: str | None = Field(
        None,
        description="Optional guidance text for using the template.",
        nullable=True,
    )


class ActivityInstructionTemplateNameUid(ActivityInstructionTemplateName):
    uid: str = Field(
        ..., description="The unique id of the activity instruction template."
    )
    sequence_id: str | None = Field(None, nullable=True)


class ActivityInstructionTemplateNameUidLibrary(ActivityInstructionTemplateNameUid):
    library_name: str = Field(...)


class ActivityInstructionTemplate(ActivityInstructionTemplateNameUid):
    start_date: datetime | None = Field(
        default_factory=datetime.utcnow,
        description="Part of the metadata: The point in time when the (version of the) activity instruction template was created. "
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )
    end_date: datetime | None = Field(
        default_factory=datetime.utcnow,
        description="""Part of the metadata: The point in time when the version of
        the activity instruction template was closed (and a new one was created). """
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
        nullable=True,
    )
    status: str | None = Field(
        None,
        description="The status in which the (version of the) activity instruction template is in. "
        "Possible values are: 'Final', 'Draft' or 'Retired'.",
        nullable=True,
    )
    version: str | None = Field(
        None,
        description="The version number of the (version of the) activity instruction template. "
        "The format is: <major>.<minor> where <major> and <minor> are digits. E.g. '0.1', '0.2', '1.0', ...",
        nullable=True,
    )
    change_description: str | None = Field(
        None,
        description="A short description about what has changed compared to the previous version.",
        nullable=True,
    )
    user_initials: str | None = Field(
        None,
        description="The initials of the user that triggered the change of the activity instruction template.",
        nullable=True,
    )
    possible_actions: list[str] = Field(
        [],
        description=(
            "Holds those actions that can be performed on the activity instruction template. "
            "Actions are: 'approve', 'edit', 'new_version', 'inactivate', 'reactivate' and 'delete'."
        ),
    )
    parameters: list[TemplateParameter] = Field(
        [],
        description="Those parameters that are used by the activity instruction template.",
    )
    default_parameter_terms: dict[int, list[MultiTemplateParameterTerm]] | None = Field(
        None,
        description="""Holds the default terms for the parameters that are used
        within the template. The terms are ordered as they occur in the template's name.""",
        nullable=True,
    )
    library: Library | None = Field(
        None,
        description="The library to which the activity instruction template belongs.",
        nullable=True,
    )

    # Template indexings
    indications: list[DictionaryTerm] = Field(
        [],
        description="The study indications, conditions, diseases or disorders in scope for the template.",
    )
    activities: list[Activity] = Field(
        [], description="The activities in scope for the template"
    )
    activity_groups: list[ActivityGroup] = Field(
        [], description="The activity groups in scope for the template"
    )
    activity_subgroups: list[ActivitySubGroup] = Field(
        [], description="The activity sub groups in scope for the template"
    )

    study_count: int = Field(0, description="Count of studies referencing template")

    @classmethod
    def from_activity_instruction_template_ar(
        cls,
        activity_instruction_template_ar: ActivityInstructionTemplateAR,
        find_activity_subgroup_by_uid: Callable[[str], ActivitySubGroupAR | None],
        find_activity_group_by_uid: Callable[[str], ActivityGroupAR | None],
    ) -> Self:
        default_parameter_terms: dict[int, list[MultiTemplateParameterTerm]] = {}
        if (
            activity_instruction_template_ar.template_value.default_parameter_terms
            is not None
        ):
            for (
                set_number,
                term_set,
            ) in (
                activity_instruction_template_ar.template_value.default_parameter_terms.items()
            ):
                term_list = []
                for position, parameter in enumerate(term_set):
                    terms: list[IndexedTemplateParameterTerm] = [
                        IndexedTemplateParameterTerm(
                            index=index + 1,
                            uid=parameter_term.uid,
                            name=parameter_term.value,
                            type=parameter.parameter_name,
                        )
                        for index, parameter_term in enumerate(parameter.parameters)
                    ]

                    term_list.append(
                        MultiTemplateParameterTerm(
                            conjunction=parameter.conjunction,
                            position=position + 1,
                            terms=terms,
                        )
                    )
                default_parameter_terms[set_number] = term_list

        return cls(
            uid=activity_instruction_template_ar.uid,
            sequence_id=activity_instruction_template_ar.sequence_id,
            name=activity_instruction_template_ar.name,
            name_plain=activity_instruction_template_ar.name_plain,
            guidance_text=activity_instruction_template_ar.guidance_text,
            start_date=activity_instruction_template_ar.item_metadata.start_date,
            end_date=activity_instruction_template_ar.item_metadata.end_date,
            status=activity_instruction_template_ar.item_metadata.status.value,
            version=activity_instruction_template_ar.item_metadata.version,
            change_description=activity_instruction_template_ar.item_metadata.change_description,
            user_initials=activity_instruction_template_ar.item_metadata.user_initials,
            possible_actions=sorted(
                [
                    _.value
                    for _ in activity_instruction_template_ar.get_possible_actions()
                ]
            ),
            library=Library.from_library_vo(activity_instruction_template_ar.library),
            indications=[
                DictionaryTerm.from_dictionary_term_ar(indication)
                for indication in activity_instruction_template_ar.indications
            ]
            if activity_instruction_template_ar.indications
            else [],
            activities=[
                Activity.from_activity_ar(
                    activity,
                    find_activity_subgroup_by_uid,
                    find_activity_group_by_uid,
                )
                for activity in activity_instruction_template_ar.activities
            ]
            if activity_instruction_template_ar.activities
            else [],
            activity_groups=[
                ActivityGroup.from_activity_ar(group)
                for group in activity_instruction_template_ar.activity_groups
            ]
            if activity_instruction_template_ar.activity_groups
            else [],
            activity_subgroups=[
                ActivitySubGroup.from_activity_ar(group, find_activity_group_by_uid)
                for group in activity_instruction_template_ar.activity_subgroups
            ]
            if activity_instruction_template_ar.activity_subgroups
            else [],
            study_count=activity_instruction_template_ar.study_count,
            parameters=[
                TemplateParameter(name=_)
                for _ in activity_instruction_template_ar.template_value.parameter_names
            ],
            default_parameter_terms=default_parameter_terms,
        )


class ActivityInstructionTemplateWithCount(ActivityInstructionTemplate):
    counts: ItemCounts | None = Field(
        None, description="Optional counts of activity instruction instantiations"
    )

    @classmethod
    def from_activity_instruction_template_ar(
        cls, activity_instruction_template_ar: ActivityInstructionTemplateAR, **kwargs
    ) -> Self:
        activity_instruction_template = super().from_activity_instruction_template_ar(
            activity_instruction_template_ar, **kwargs
        )
        if activity_instruction_template_ar.counts is not None:
            activity_instruction_template.counts = ItemCounts(
                draft=activity_instruction_template_ar.counts.count_draft,
                final=activity_instruction_template_ar.counts.count_final,
                retired=activity_instruction_template_ar.counts.count_retired,
                total=activity_instruction_template_ar.counts.count_total,
            )
        return activity_instruction_template


class ActivityInstructionTemplateVersion(ActivityInstructionTemplate):
    """
    Class for storing Activity Instruction Templates and calculation of differences
    """

    changes: dict[str, bool] | None = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the activity instruction template (e.g. name, start_date, ..)."
        ),
        nullable=True,
    )


class ActivityInstructionTemplateNameInput(BaseModel):
    name: str = Field(
        ...,
        description="The actual value/content. It may include parameters referenced by simple strings in square brackets [].",
        min_length=1,
    )
    guidance_text: str | None = Field(
        None, description="Optional guidance text for using the template."
    )


class ActivityInstructionTemplateCreateInput(ActivityInstructionTemplateNameInput):
    library_name: str | None = Field(
        "Sponsor",
        description="If specified: The name of the library to which the activity instruction template will be linked. The following rules apply: \n"
        "* The library needs to be present, it will not be created with this request. The *[GET] /libraries* endpoint can help. And \n"
        "* The library needs to allow the creation: The 'is_editable' property of the library needs to be true.",
    )
    default_parameter_terms: list[MultiTemplateParameterTerm] | None = Field(
        None,
        description="Holds the parameter terms to be used as default for this template. The terms are ordered as they occur in the template name.",
    )
    indication_uids: list[str] | None = Field(
        None,
        description="A list of UID of the study indications, conditions, diseases or disorders to attach the template to.",
    )
    activity_uids: list[str] | None = Field(
        None, description="A list of UID of the activities to attach the template to."
    )
    activity_group_uids: conlist(
        str,
        min_items=1,
    )
    activity_subgroup_uids: conlist(
        str,
        min_items=1,
    )


class ActivityInstructionTemplateEditInput(ActivityInstructionTemplateNameInput):
    change_description: str = Field(
        ...,
        description="A short description about what has changed compared to the previous version.",
    )


class ActivityInstructionTemplateEditIndexingsInput(BaseModel):
    indication_uids: list[str] | None = Field(
        None,
        description="A list of UID of the study indications, conditions, diseases or disorders to attach the template to.",
    )
    activity_uids: list[str] | None = Field(
        None, description="A list of UID of the activities to attach the template to."
    )
    activity_group_uids: list[str] | None = Field(
        None,
        description="A list of UID of the activity groups to attach the template to.",
    )
    activity_subgroup_uids: list[str] | None = Field(
        None,
        description="A list of UID of the activity sub groups to attach the template to.",
    )
