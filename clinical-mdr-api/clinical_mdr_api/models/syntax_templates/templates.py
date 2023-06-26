from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field

from clinical_mdr_api.models.libraries.library import Library
from clinical_mdr_api.models.syntax_templates.template_parameter import (
    TemplateParameter,
)
from clinical_mdr_api.models.utils import BaseModel


class TemplateName(BaseModel):
    name: Optional[str] = Field(
        None,
        description="""
            The actual value/content. It may include parameters
            referenced by simple strings in square brackets [].
            """,
    )


class Template(TemplateName):
    uid: str = Field(..., description="The unique id of the objective template.")

    start_date: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="""
            Part of the metadata: The point in time when the
            (version of the) objective template was created.
            The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00'
            for October 31, 2020 at 6pm in UTC+2 timezone.
            """,
    )
    end_date: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Part of the metadata: The point in time when the version of the objective template was closed (and a new one was created). "
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
        nullable=True,
    )
    status: Optional[str] = Field(
        None,
        description="The status in which the (version of the) objective template is in. "
        "Possible values are: 'Final', 'Draft' or 'Retired'.",
        nullable=True,
    )
    version: Optional[str] = Field(
        None,
        description="The version number of the (version of the) objective template. "
        "The format is: <major>.<minor> where <major> and <minor> are digits. E.g. '0.1', '0.2', '1.0', ...",
        nullable=True,
    )
    change_description: Optional[str] = Field(
        None,
        description="A short description about what has changed compared to the previous version.",
        nullable=True,
    )
    user_initials: Optional[str] = Field(
        None,
        description="The initials of the user that triggered the change of the objective template.",
        nullable=True,
    )

    # TODO use the standard _link/name approach
    possible_actions: List[str] = Field(
        [],
        description=(
            "Holds those actions that can be performed on the objective template. "
            "Actions are: 'approve', 'edit', 'new_version', 'inactivate', 'reactivate' and 'delete'."
        ),
    )
    parameters: List[TemplateParameter] = Field(
        [], description="Those parameters that are used by the objective template."
    )
    library: Optional[Library] = Field(
        None, description="The library to which the objective template belongs."
    )


class TemplateVersion(Template):
    """
    Class for storing Objective Templates and calculation of differences
    """

    changes: Optional[Dict[str, bool]] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective template (e.g. name, start_date, ..)."
        ),
        nullable=True,
    )


class TemplateCreateInput(BaseModel):
    name: str = Field(
        ...,
        description="The actual value/content. It may include parameters referenced by simple strings in square brackets [].",
    )

    library_name: Optional[str] = Field(
        "Sponsor",
        description="If specified: The name of the library to which the objective template will be linked. The following rules apply: \n"
        "* The library needs to be present, it will not be created with this request. The *[GET] /libraries* endpoint can help. And \n"
        "* The library needs to allow the creation: The 'is_editable' property of the library needs to be true.",
        nullable=True,
    )


class TemplateNameInput(BaseModel):
    name: str = Field(
        ...,
        description="The actual value/content. It may include parameters referenced by simple strings in square brackets [].",
    )


class TemplateEditInput(TemplateNameInput):
    change_description: str = Field(
        ...,
        description="A short description about what has changed compared to the previous version.",
    )


class RelatedObjectsCount(BaseModel):
    count_draft: int = Field(
        ..., description="Count of related objects in draft status"
    )
    count_final: int = Field(
        ..., description="Count of related objects in final status"
    )
    count_retired: int = Field(
        ..., description="Count of related objects in retired status"
    )
