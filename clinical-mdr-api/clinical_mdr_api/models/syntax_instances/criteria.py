from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Sequence

from pydantic.fields import Field
from pydantic.main import BaseModel

from clinical_mdr_api.domain_repositories.models.syntax import CriteriaTemplateRoot
from clinical_mdr_api.domains.syntax_instances.criteria import CriteriaAR
from clinical_mdr_api.models.libraries.library import Library
from clinical_mdr_api.models.syntax_templates.criteria_template import (
    CriteriaTemplateNameUid,
    CTTermNameAndAttributes,
)
from clinical_mdr_api.models.syntax_templates.template_parameter_multi_select_input import (
    TemplateParameterMultiSelectInput,
)
from clinical_mdr_api.models.syntax_templates.template_parameter_term import (
    IndexedTemplateParameterTerm,
    MultiTemplateParameterTerm,
)


class CriteriaTemplateWithType(CriteriaTemplateNameUid):
    type: CTTermNameAndAttributes


class Criteria(BaseModel):
    uid: str
    name: Optional[str] = Field(None, nullable=True)
    name_plain: Optional[str] = Field(None, nullable=True)

    start_date: Optional[datetime] = Field(None, nullable=True)
    end_date: Optional[datetime] = Field(None, nullable=True)
    status: Optional[str] = Field(None, nullable=True)
    version: Optional[str] = Field(None, nullable=True)
    change_description: Optional[str] = Field(None, nullable=True)
    user_initials: Optional[str] = Field(None, nullable=True)

    possible_actions: Optional[Sequence[str]] = Field(
        None,
        description=(
            "Holds those actions that can be performed on the criteria. "
            "Actions are: None"
        ),
    )

    criteria_template: Optional[CriteriaTemplateNameUid]
    parameter_terms: Optional[Sequence[MultiTemplateParameterTerm]] = Field(
        None,
        description="Holds the parameter terms that are used within the criteria. The terms are ordered as they occur in the criteria name.",
    )
    library: Optional[Library] = None

    study_count: int = Field(0, description="Count of studies referencing criteria")

    @classmethod
    def from_criteria_ar(
        cls,
        criteria_ar: CriteriaAR,
    ) -> "Criteria":
        parameter_terms: List[MultiTemplateParameterTerm] = []
        for position, parameter in enumerate(criteria_ar.get_parameters()):
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
            uid=criteria_ar.uid,
            name=criteria_ar.name,
            name_plain=criteria_ar.name_plain,
            start_date=criteria_ar.item_metadata.start_date,
            end_date=criteria_ar.item_metadata.end_date,
            status=criteria_ar.item_metadata.status.value,
            version=criteria_ar.item_metadata.version,
            change_description=criteria_ar.item_metadata.change_description,
            user_initials=criteria_ar.item_metadata.user_initials,
            possible_actions=sorted(
                {_.value for _ in criteria_ar.get_possible_actions()}
            ),
            criteria_template=CriteriaTemplateNameUid(
                name=criteria_ar.template_name,
                name_plain=criteria_ar.name_plain,
                uid=criteria_ar.template_uid,
                sequence_id=criteria_ar.template_sequence_id,
                guidance_text=criteria_ar.template_guidance_text,
            ),
            library=Library.from_library_vo(criteria_ar.library),
            study_count=criteria_ar.study_count,
            parameter_terms=parameter_terms,
        )


class CriteriaWithType(Criteria):
    criteria_template: Optional[CriteriaTemplateWithType]

    @classmethod
    def from_criteria_ar(
        cls,
        criteria_ar: CriteriaAR,
        get_criteria_type_name: Callable[[type, str], Any],
        get_criteria_type_attributes: Callable[[type, str], Any],
    ) -> "CriteriaWithType":
        parameter_terms: List[MultiTemplateParameterTerm] = []
        for position, parameter in enumerate(criteria_ar.get_parameters()):
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
            uid=criteria_ar.uid,
            name=criteria_ar.name,
            name_plain=criteria_ar.name_plain,
            start_date=criteria_ar.item_metadata.start_date,
            end_date=criteria_ar.item_metadata.end_date,
            status=criteria_ar.item_metadata.status.value,
            version=criteria_ar.item_metadata.version,
            change_description=criteria_ar.item_metadata.change_description,
            user_initials=criteria_ar.item_metadata.user_initials,
            possible_actions=sorted(
                {_.value for _ in criteria_ar.get_possible_actions()}
            ),
            criteria_template=CriteriaTemplateWithType(
                name=criteria_ar.template_name,
                name_plain=criteria_ar.name_plain,
                uid=criteria_ar.template_uid,
                sequence_id=criteria_ar.template_sequence_id,
                guidance_text=criteria_ar.template_guidance_text,
                type=CTTermNameAndAttributes.from_ct_term_ars(
                    ct_term_name_ar=get_criteria_type_name(
                        CriteriaTemplateRoot, criteria_ar.template_uid
                    ),
                    ct_term_attributes_ar=get_criteria_type_attributes(
                        CriteriaTemplateRoot, criteria_ar.template_uid
                    ),
                ),
            ),
            library=Library.from_library_vo(criteria_ar.library),
            study_count=criteria_ar.study_count,
            parameter_terms=parameter_terms,
        )


class CriteriaVersion(CriteriaWithType):
    """
    Class for storing Criteria and calculation of differences
    """

    changes: Optional[Dict[str, bool]] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the criteria (e.g. name, start_date, ..)."
        ),
        nullable=True,
    )


class CriteriaParameterInput(BaseModel):
    parameter_terms: List[TemplateParameterMultiSelectInput] = Field(
        ...,
        title="parameter_terms",
        description="An ordered list of selected parameter terms that are used to replace the parameters of the criteria template.",
    )


class CriteriaEditInput(CriteriaParameterInput):
    change_description: str = Field(
        ...,
        description="A short description about what has changed compared to the previous version.",
    )


class CriteriaCreateInput(CriteriaParameterInput):
    criteria_template_uid: str = Field(
        ...,
        title="criteria_template_uid",
        description="The unique id of the criteria template that is used as the basis for the new criteria.",
    )
    library_name: str = Field(
        None,
        title="library_name",
        description="If specified: The name of the library to which the criteria will be linked. The following rules apply: \n"
        "* The library needs to be present, it will not be created with this request. The *[GET] /libraries* criteria can help. And \n"
        "* The library needs to allow the creation: The 'is_editable' property of the library needs to be true. \n\n"
        "If not specified: The library of the criteria template will be used.",
    )
