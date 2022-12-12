from datetime import datetime
from typing import Dict, List, Optional, Sequence

from pydantic.fields import Field
from pydantic.main import BaseModel

from clinical_mdr_api.domain.library.criteria import CriteriaAR
from clinical_mdr_api.models.criteria_template import CriteriaTemplateNameUid
from clinical_mdr_api.models.library import Library
from clinical_mdr_api.models.template_parameter_multi_select_input import (
    TemplateParameterMultiSelectInput,
)
from clinical_mdr_api.models.template_parameter_value import (
    IndexedTemplateParameterValue,
    MultiTemplateParameterValue,
)


class Criteria(BaseModel):
    uid: str
    name: Optional[str] = None
    name_plain: Optional[str] = None

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    version: Optional[str] = None
    change_description: Optional[str] = None
    user_initials: Optional[str] = None

    possible_actions: Optional[Sequence[str]] = Field(
        None,
        description=(
            "Holds those actions that can be performed on the criteria. "
            "Actions are: None"
        ),
    )

    criteria_template: Optional[CriteriaTemplateNameUid]
    parameter_values: Optional[Sequence[MultiTemplateParameterValue]] = Field(
        None,
        description="Holds the parameter values that are used within the criteria. The values are ordered as they occur in the criteria name.",
    )
    library: Optional[Library] = None

    study_count: Optional[int] = Field(
        None, description="Count of studies referencing criteria"
    )

    @classmethod
    def from_criteria_ar(cls, criteria_ar: CriteriaAR) -> "Criteria":

        parameter_values: List[MultiTemplateParameterValue] = []
        for position, parameter in enumerate(criteria_ar.get_parameters()):
            values: List[IndexedTemplateParameterValue] = []
            for index, parameter_value in enumerate(parameter.parameters):
                pv = IndexedTemplateParameterValue(
                    index=index + 1,
                    uid=parameter_value.uid,
                    name=parameter_value.value,
                    type=parameter.parameter_name,
                )
                values.append(pv)
            conjunction = parameter.conjunction

            parameter_values.append(
                MultiTemplateParameterValue(
                    conjunction=conjunction, position=position + 1, values=values
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
                guidance_text=criteria_ar.template_guidance_text,
            ),
            library=Library.from_library_vo(criteria_ar.library),
            study_count=criteria_ar.study_count,
            parameter_values=parameter_values,
        )


class CriteriaVersion(Criteria):
    """
    Class for storing Criteria and calculation of differences
    """

    changes: Dict[str, bool] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the criteria (e.g. name, start_date, ..)."
        ),
    )


class CriteriaParameterInput(BaseModel):
    parameter_values: List[TemplateParameterMultiSelectInput] = Field(
        ...,
        title="parameter_values",
        description="An ordered list of selected parameter values that are used to replace the parameters of the criteria template.",
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
    name_override: Optional[str] = Field(
        None,
        title="name",
        description="Optionally, a name to override the name inherited from the template.",
    )
    library_name: str = Field(
        None,
        title="library_name",
        description="If specified: The name of the library to which the criteria will be linked. The following rules apply: \n"
        "* The library needs to be present, it will not be created with this request. The *[GET] /libraries* criteria can help. And \n"
        "* The library needs to allow the creation: The 'is_editable' property of the library needs to be true. \n\n"
        "If not specified: The library of the criteria template will be used.",
    )
