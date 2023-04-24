from typing import List, Optional

from pydantic import Field

from clinical_mdr_api.models.template_parameter_term import TemplateParameterTerm
from clinical_mdr_api.models.utils import BaseModel


class TemplateParameter(BaseModel):
    name: Optional[str] = Field(
        ...,
        title="name",
        description="The name of the template parameter. E.g. 'Intervention', 'Indication', 'Activity', ...",
    )

    terms: Optional[List[TemplateParameterTerm]] = Field(
        None,
        title="terms",
        description="The possible terms of the template parameter.",
    )


class ComplexTemplateParameter(BaseModel):
    name: Optional[str]
    format: Optional[str]
    parameters: Optional[List[TemplateParameter]]
    terms: Optional[List[TemplateParameterTerm]] = Field(
        None,
        title="terms",
        description="The possible terms of the template parameter.",
    )
