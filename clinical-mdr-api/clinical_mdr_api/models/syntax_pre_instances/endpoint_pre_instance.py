from datetime import datetime
from typing import Self

from pydantic import Field

from clinical_mdr_api.domains.syntax_pre_instances.endpoint_pre_instance import (
    EndpointPreInstanceAR,
)
from clinical_mdr_api.models.controlled_terminologies.ct_term import (
    CTTermNameAndAttributes,
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


class EndpointPreInstance(BaseModel):
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
        description="Holds the parameter terms that are used within the endpoint. The terms are ordered as they occur in the endpoint name.",
    )
    indications: list[DictionaryTerm] = Field(
        [],
        description="The study indications, conditions, diseases or disorders in scope for the pre-instance.",
    )
    categories: list[CTTermNameAndAttributes] = Field(
        [], description="A list of categories the pre-instance belongs to."
    )
    sub_categories: list[CTTermNameAndAttributes] = Field(
        [], description="A list of sub-categories the pre-instance belongs to."
    )
    library: Library | None = Field(None, nullable=True)
    possible_actions: list[str] = []

    @classmethod
    def from_endpoint_pre_instance_ar(
        cls, endpoint_pre_instance_ar: EndpointPreInstanceAR
    ) -> Self:
        parameter_terms: list[MultiTemplateParameterTerm] = []
        for position, parameter in enumerate(endpoint_pre_instance_ar.get_parameters()):
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
            uid=endpoint_pre_instance_ar.uid,
            sequence_id=endpoint_pre_instance_ar.sequence_id,
            template_uid=endpoint_pre_instance_ar.template_uid,
            template_name=endpoint_pre_instance_ar.template_name,
            name=endpoint_pre_instance_ar.name,
            name_plain=endpoint_pre_instance_ar.name_plain,
            start_date=endpoint_pre_instance_ar.item_metadata.start_date,
            end_date=endpoint_pre_instance_ar.item_metadata.end_date,
            status=endpoint_pre_instance_ar.item_metadata.status.value,
            version=endpoint_pre_instance_ar.item_metadata.version,
            change_description=endpoint_pre_instance_ar.item_metadata.change_description,
            user_initials=endpoint_pre_instance_ar.item_metadata.user_initials,
            library=Library.from_library_vo(endpoint_pre_instance_ar.library),
            parameter_terms=parameter_terms,
            indications=sorted(
                [
                    DictionaryTerm.from_dictionary_term_ar(indication)
                    for indication in endpoint_pre_instance_ar.indications
                ],
                key=lambda item: item.term_uid,
                reverse=True,
            )
            if endpoint_pre_instance_ar.indications
            else [],
            categories=sorted(
                [
                    CTTermNameAndAttributes.from_ct_term_ars(*category)
                    for category in endpoint_pre_instance_ar.categories
                ],
                key=lambda item: item.term_uid,
            )
            if endpoint_pre_instance_ar.categories
            else [],
            sub_categories=sorted(
                [
                    CTTermNameAndAttributes.from_ct_term_ars(*category)
                    for category in endpoint_pre_instance_ar.sub_categories
                ],
                key=lambda item: item.term_uid,
            )
            if endpoint_pre_instance_ar.sub_categories
            else [],
            possible_actions=sorted(
                {_.value for _ in endpoint_pre_instance_ar.get_possible_actions()}
            ),
        )


class EndpointPreInstanceCreateInput(PreInstanceInput):
    indication_uids: list[str]
    category_uids: list[str]
    sub_category_uids: list[str]


class EndpointPreInstanceEditInput(PreInstanceInput):
    change_description: str = Field(
        ...,
        description="A short description about what has changed compared to the previous version.",
    )


class EndpointPreInstanceIndexingsInput(BaseModel):
    indication_uids: list[str] | None = Field(
        None,
        description="A list of UID of the study indications, conditions, diseases or disorders to attach the pre-instance to.",
    )
    category_uids: list[str] | None = Field(
        None,
        description="A list of UID of the categories to attach the pre-instance to.",
    )
    sub_category_uids: list[str] | None = Field(
        None,
        description="A list of UID of the sub_categories to attach the pre-instance to.",
    )


class EndpointPreInstanceVersion(EndpointPreInstance):
    """
    Class for storing Endpoint Pre-Instances and calculation of differences
    """

    changes: dict[str, bool] | None = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the endpoint (e.g. name, start_date, ..)."
        ),
        nullable=True,
    )
