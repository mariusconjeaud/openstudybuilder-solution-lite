from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field

from clinical_mdr_api.domain.syntax_templates.objective_template import (
    ObjectiveTemplateAR,
)
from clinical_mdr_api.models.ct_term import CTTermNameAndAttributes
from clinical_mdr_api.models.dictionary_term import DictionaryTerm
from clinical_mdr_api.models.library import ItemCounts, Library
from clinical_mdr_api.models.template_parameter import TemplateParameter
from clinical_mdr_api.models.template_parameter_term import (
    IndexedTemplateParameterTerm,
    MultiTemplateParameterTerm,
)
from clinical_mdr_api.models.utils import BaseModel


class ObjectiveTemplateName(BaseModel):
    name: Optional[str] = Field(
        None,
        description="The actual value/content. It may include parameters referenced by simple strings in square brackets [].",
    )
    name_plain: Optional[str] = Field(
        None,
        description="The plain text version of the name property, stripped of HTML tags",
    )
    guidance_text: Optional[str] = Field(
        None, description="Optional guidance text for using the template."
    )


class ObjectiveTemplateNameUid(ObjectiveTemplateName):
    uid: str = Field(..., description="The unique id of the objective template.")


class ObjectiveTemplate(ObjectiveTemplateNameUid):
    start_date: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Part of the metadata: The point in time when the (version of the) objective template was created. "
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )
    end_date: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Part of the metadata: The point in time when the version of the objective template was closed (and a new one was created). "
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )
    status: Optional[str] = Field(
        None,
        description="The status in which the (version of the) objective template is in. "
        "Possible values are: 'Final', 'Draft' or 'Retired'.",
    )
    version: Optional[str] = Field(
        None,
        description="The version number of the (version of the) objective template. "
        "The format is: <major>.<minor> where <major> and <minor> are digits. E.g. '0.1', '0.2', '1.0', ...",
    )
    change_description: Optional[str] = Field(
        None,
        description="A short description about what has changed compared to the previous version.",
    )
    user_initials: Optional[str] = Field(
        None,
        description="The initials of the user that triggered the change of the objective template.",
    )

    # TODO use the standard _link/name approach
    possible_actions: Optional[List[str]] = Field(
        None,
        description=(
            "Holds those actions that can be performed on the objective template. "
            "Actions are: 'approve', 'edit', 'new_version', 'inactivate', 'reactivate' and 'delete'."
        ),
    )
    parameters: Optional[List[TemplateParameter]] = Field(
        None, description="Those parameters that are used by the objective template."
    )
    default_parameter_terms: Optional[
        Dict[int, List[MultiTemplateParameterTerm]]
    ] = Field(
        None,
        description="""Holds the default terms for the parameters that are used
        within the template. The terms are ordered as they occur in the template's name.""",
    )
    library: Optional[Library] = Field(
        None, description=("The library to which the objective template belongs.")
    )

    # Template indexings
    indications: Optional[List[DictionaryTerm]] = Field(
        None,
        description="The study indications, conditions, diseases or disorders in scope for the template.",
    )
    is_confirmatory_testing: Optional[bool] = Field(
        None, description="Indicates if template is related to confirmatory testing."
    )
    categories: Optional[List[CTTermNameAndAttributes]] = Field(
        None, description="A list of categories the template belongs to."
    )

    study_count: Optional[int] = Field(
        None, description="Count of studies referencing template"
    )

    @classmethod
    def from_objective_template_ar(
        cls, objective_template_ar: ObjectiveTemplateAR
    ) -> "ObjectiveTemplate":
        default_parameter_terms: Dict[int, List[MultiTemplateParameterTerm]] = {}
        if objective_template_ar.template_value.default_parameter_terms is not None:
            for (
                set_number,
                term_set,
            ) in objective_template_ar.template_value.default_parameter_terms.items():
                term_list = []
                for position, parameter in enumerate(term_set):
                    terms: List[IndexedTemplateParameterTerm] = [
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
            uid=objective_template_ar.uid,
            name=objective_template_ar.name,
            name_plain=objective_template_ar.name_plain,
            guidance_text=objective_template_ar.guidance_text,
            start_date=objective_template_ar.item_metadata.start_date,
            end_date=objective_template_ar.item_metadata.end_date,
            status=objective_template_ar.item_metadata.status.value,
            version=objective_template_ar.item_metadata.version,
            change_description=objective_template_ar.item_metadata.change_description,
            user_initials=objective_template_ar.item_metadata.user_initials,
            possible_actions=sorted(
                [_.value for _ in objective_template_ar.get_possible_actions()]
            ),
            library=Library.from_library_vo(objective_template_ar.library),
            is_confirmatory_testing=objective_template_ar.is_confirmatory_testing,
            indications=[
                DictionaryTerm.from_dictionary_term_ar(indication)
                for indication in objective_template_ar.indications
            ]
            if objective_template_ar.indications
            else None,
            categories=[
                CTTermNameAndAttributes.from_ct_term_ars(*category)
                for category in objective_template_ar.categories
            ]
            if objective_template_ar.categories
            else None,
            study_count=objective_template_ar.study_count,
            parameters=[
                TemplateParameter(name=_)
                for _ in objective_template_ar.template_value.parameter_names
            ],
            default_parameter_terms=default_parameter_terms,
        )


class ObjectiveTemplateWithCount(ObjectiveTemplate):
    counts: Optional[ItemCounts] = Field(
        None, description="Optional counts of objective instatiations"
    )

    @classmethod
    def from_objective_template_ar(
        cls, objective_template_ar: ObjectiveTemplateAR
    ) -> "ObjectiveTemplate":
        ot = super().from_objective_template_ar(objective_template_ar)
        if objective_template_ar.counts is not None:
            ot.counts = ItemCounts(
                draft=objective_template_ar.counts.count_draft,
                final=objective_template_ar.counts.count_final,
                retired=objective_template_ar.counts.count_retired,
                total=objective_template_ar.counts.count_total,
            )
        return ot


class ObjectiveTemplateVersion(ObjectiveTemplate):
    """
    Class for storing Objective Templates and calculation of differences
    """

    changes: Dict[str, bool] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective template (e.g. name, start_date, ..)."
        ),
    )


class ObjectiveTemplateNameInput(BaseModel):
    name: str = Field(
        ...,
        description="The actual value/content. It may include parameters referenced by simple strings in square brackets [].",
    )
    guidance_text: Optional[str] = Field(
        None, description="Optional guidance text for using the template."
    )


class ObjectiveTemplateCreateInput(ObjectiveTemplateNameInput):
    study_uid: Optional[str] = Field(
        None,
        description="The UID of the Study in scope of which given template is being created.",
    )
    library_name: Optional[str] = Field(
        "Sponsor",
        description="If specified: The name of the library to which the objective template will be linked. The following rules apply: \n"
        "* The library needs to be present, it will not be created with this request. The *[GET] /libraries* endpoint can help. And \n"
        "* The library needs to allow the creation: The 'is_editable' property of the library needs to be true.",
    )
    default_parameter_terms: Optional[List[MultiTemplateParameterTerm]] = Field(
        None,
        description="""Holds the parameter terms to be used as default for this
        template. The terms are ordered as they occur in the template name. \n"""
        "These default parameter terms will be created as set#0.",
    )
    indication_uids: Optional[List[str]] = Field(
        None,
        description="A list of UID of the study indications, conditions, diseases or disorders to attach the template to.",
    )
    is_confirmatory_testing: Optional[bool] = Field(
        None, description="Indicates if template is related to confirmatory testing."
    )
    category_uids: Optional[List[str]] = Field(
        None, description="A list of UID of the categories to attach the template to."
    )


class ObjectiveTemplateEditInput(ObjectiveTemplateNameInput):
    change_description: str = Field(
        ...,
        description="A short description about what has changed compared to the previous version.",
    )


class ObjectiveTemplateEditIndexingsInput(BaseModel):
    indication_uids: Optional[List[str]] = Field(
        None,
        description="A list of UID of the study indications, conditions, diseases or disorders to attach the template to.",
    )
    category_uids: Optional[List[str]] = Field(
        None, description="A list of UID of the categories to attach the template to."
    )
    is_confirmatory_testing: Optional[bool] = Field(
        None, description="Indicates if template is related to confirmatory testing."
    )
