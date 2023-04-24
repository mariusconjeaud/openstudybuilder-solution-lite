from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field

from clinical_mdr_api.domain.syntax_templates.endpoint_template import (
    EndpointTemplateAR,
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


class EndpointTemplateName(BaseModel):
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


class EndpointTemplateNameUid(EndpointTemplateName):
    uid: str = Field(..., description="The unique id of the endpoint template.")


class EndpointTemplate(EndpointTemplateNameUid):
    start_date: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Part of the metadata: The point in time when the (version of the) endpoint template was created. "
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )
    end_date: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Part of the metadata: The point in time when the version of the endpoint template was closed (and a new one was created). "
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )
    status: Optional[str] = Field(
        None,
        description="The status in which the (version of the) endpoint template is in. "
        "Possible values are: 'Final', 'Draft' or 'Retired'.",
    )
    version: Optional[str] = Field(
        None,
        description="The version number of the (version of the) endpoint template. "
        "The format is: <major>.<minor> where <major> and <minor> are digits. E.g. '0.1', '0.2', '1.0', ...",
    )
    change_description: Optional[str] = Field(
        None,
        description="A short description about what has changed compared to the previous version.",
    )
    user_initials: Optional[str] = Field(
        None,
        description="The initials of the user that triggered the change of the endpoint template.",
    )

    # TODO use the standard _link/name approach
    possible_actions: Optional[List[str]] = Field(
        None,
        description=(
            "Holds those actions that can be performed on the endpoint template. "
            "Actions are: 'approve', 'edit', 'new_version', 'inactivate', 'reactivate' and 'delete'."
        ),
    )
    parameters: Optional[List[TemplateParameter]] = Field(
        None, description="Those parameters that are used by the endpoint template."
    )
    default_parameter_terms: Optional[
        Dict[int, List[MultiTemplateParameterTerm]]
    ] = Field(
        None,
        description="""Holds the default terms for the parameters that are used
        within the template. The terms are ordered as they occur in the template's name.""",
    )
    library: Optional[Library] = Field(
        None, description=("The library to which the endpoint template belongs.")
    )

    # Template indexings
    indications: Optional[List[DictionaryTerm]] = Field(
        None,
        description="The study indications, conditions, diseases or disorders in scope for the template.",
    )
    categories: Optional[List[CTTermNameAndAttributes]] = Field(
        None, description="A list of categories the template belongs to."
    )
    sub_categories: Optional[List[CTTermNameAndAttributes]] = Field(
        None, description="A list of sub-categories the template belongs to."
    )

    study_count: Optional[int] = Field(
        None, description="Count of studies referencing template"
    )

    @classmethod
    def from_endpoint_template_ar(
        cls, endpoint_template_ar: EndpointTemplateAR
    ) -> "EndpointTemplate":
        default_parameter_terms: Dict[int, List[MultiTemplateParameterTerm]] = {}
        if endpoint_template_ar.template_value.default_parameter_terms is not None:
            for (
                set_number,
                term_set,
            ) in endpoint_template_ar.template_value.default_parameter_terms.items():
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
            uid=endpoint_template_ar.uid,
            name=endpoint_template_ar.name,
            name_plain=endpoint_template_ar.name_plain,
            guidance_text=endpoint_template_ar.guidance_text,
            start_date=endpoint_template_ar.item_metadata.start_date,
            end_date=endpoint_template_ar.item_metadata.end_date,
            status=endpoint_template_ar.item_metadata.status.value,
            version=endpoint_template_ar.item_metadata.version,
            change_description=endpoint_template_ar.item_metadata.change_description,
            user_initials=endpoint_template_ar.item_metadata.user_initials,
            possible_actions=sorted(
                [_.value for _ in endpoint_template_ar.get_possible_actions()]
            ),
            library=Library.from_library_vo(endpoint_template_ar.library),
            indications=[
                DictionaryTerm.from_dictionary_term_ar(indication)
                for indication in endpoint_template_ar.indications
            ]
            if endpoint_template_ar.indications
            else None,
            categories=[
                CTTermNameAndAttributes.from_ct_term_ars(*category)
                for category in endpoint_template_ar.categories
            ]
            if endpoint_template_ar.categories
            else None,
            sub_categories=[
                CTTermNameAndAttributes.from_ct_term_ars(*category)
                for category in endpoint_template_ar.sub_categories
            ]
            if endpoint_template_ar.sub_categories
            else None,
            study_count=endpoint_template_ar.study_count,
            parameters=[
                TemplateParameter(name=_)
                for _ in endpoint_template_ar.template_value.parameter_names
            ],
            default_parameter_terms=default_parameter_terms,
        )


class EndpointTemplateWithCount(EndpointTemplate):
    counts: Optional[ItemCounts] = Field(
        None, description="Optional counts of objective instatiations"
    )

    @classmethod
    def from_endpoint_template_ar(
        cls, endpoint_template_ar: EndpointTemplateAR
    ) -> "EndpointTemplate":
        ot = super().from_endpoint_template_ar(endpoint_template_ar)
        if endpoint_template_ar.counts is not None:
            ot.counts = ItemCounts(
                draft=endpoint_template_ar.counts.count_draft,
                final=endpoint_template_ar.counts.count_final,
                retired=endpoint_template_ar.counts.count_retired,
                total=endpoint_template_ar.counts.count_total,
            )
        return ot


class EndpointTemplateVersion(EndpointTemplate):
    changes: Dict[str, bool] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the endpoint template (e.g. name, start_date, ..)."
        ),
    )


class EndpointTemplateNameInput(BaseModel):
    name: str = Field(
        ...,
        description="The actual value/content. It may include parameters referenced by simple strings in square brackets [].",
    )
    guidance_text: Optional[str] = Field(
        None, description="Optional guidance text for using the template."
    )


class EndpointTemplateCreateInput(EndpointTemplateNameInput):
    study_uid: Optional[str] = Field(
        None,
        description="The UID of the Study in scope of which given template is being created.",
    )
    library_name: Optional[str] = Field(
        "Sponsor",
        description="If specified: The name of the library to which the endpoint template will be linked. The following rules apply: \n"
        "* The library needs to be present, it will not be created with this request. The *[GET] /libraries* endpoint can help. And \n"
        "* The library needs to allow the creation: The 'is_editable' property of the library needs to be true.",
    )
    default_parameter_terms: Optional[List[MultiTemplateParameterTerm]] = Field(
        None,
        description="Holds the parameter terms to be used as default for this template. The terms are ordered as they occur in the template name.",
    )
    indication_uids: Optional[List[str]] = Field(
        None,
        description="A list of UID of the study indications, conditions, diseases or disorders to attach the template to.",
    )
    category_uids: Optional[List[str]] = Field(
        None, description="A list of UID of the categories to attach the template to."
    )
    sub_category_uids: Optional[List[str]] = Field(
        None,
        description="A list of UID of the sub_categories to attach the template to.",
    )


class EndpointTemplateEditInput(EndpointTemplateNameInput):
    change_description: str = Field(
        ...,
        description="A short description about what has changed compared to the previous version.",
    )


class EndpointTemplateEditIndexingsInput(BaseModel):
    indication_uids: Optional[List[str]] = Field(
        None,
        description="A list of UID of the study indications, conditions, diseases or disorders to attach the template to.",
    )
    category_uids: Optional[List[str]] = Field(
        None, description="A list of UID of the categories to attach the template to."
    )
    sub_category_uids: Optional[List[str]] = Field(
        None,
        description="A list of UID of the sub_categories to attach the template to.",
    )
