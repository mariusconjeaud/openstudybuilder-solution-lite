"""Objective templates router."""

from fastapi import APIRouter, Body, Depends, Path, Query, Request

from clinical_mdr_api.domains.versioned_object_aggregate import LibraryItemStatus
from clinical_mdr_api.models.complex_parameter_template import (
    ComplexParameterTemplate,
    ComplexParameterTemplateCreateInput,
    ComplexParameterTemplateEditInput,
    ComplexParameterTemplateNameInput,
    ComplexParameterTemplateVersion,
    ComplexParameterTemplateWithCount,
)
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.models.syntax_templates.template_parameter import (
    ComplexTemplateParameter,
)
from clinical_mdr_api.oauth import get_current_user_id, rbac
from clinical_mdr_api.routers import _generic_descriptions, decorators
from clinical_mdr_api.services.syntax_templates.parameter_templates import (
    ComplexParameterTemplateService,
)

# Prefixed with "/parameter-templates"
router = APIRouter()

Service = ComplexParameterTemplateService

# Argument definitions
ComplexParameterTemplateUID = Path(
    None, description="The unique id of the parameter template."
)

PARAMETERS_NOTE = """**Parameters in the 'name' property**:

The 'name' of an parameter template may contain parameters, that can - and usually will - be replaced with concrete values once an parameter is created out of the complex-parameter template.

Parameters are referenced by simple strings in square brackets [] that match existing parameters defined in the MDR repository.

See the *[GET] /parameter-templates/* endpoint for available terms.

The parameter template will be linked to those parameters defined in the 'name' property.

You may use an arbitrary number of parameters and you may use the same parameter multiple times within the same parameter template 'name'.

*Example*:

name='MORE TESTING of the superiority in the efficacy of [Intervention] with [Activity] and [Activity] in [ComplexParameter].'

'Intervention', 'Activity' and 'ComplexParameter' are parameters."""


@router.get(
    "",
    dependencies=[rbac.LIBRARY_READ],
    summary="Returns all parameter templates in their latest/newest version.",
    description=_generic_descriptions.DATA_EXPORTS_HEADER,
    response_model=list[ComplexParameterTemplate],
    status_code=200,
    responses={
        200: {
            "content": {
                "text/csv": {
                    "example": """
"library","uid","name","start_date","end_date","status","version","change_description","user_initials"
"Sponsor","826d80a7-0b6a-419d-8ef1-80aa241d7ac7","First  [ComparatorIntervention]","2020-10-22T10:19:29+00:00",,"Draft","0.1","Initial version","NdSJ"
"""
                },
                "text/xml": {
                    "example": """
                    <?xml version="1.0" encoding="UTF-8" ?><root><data type="list"><item type="dict"><uid type="str">e9117175-918f-489e-9a6e-65e0025233a6</uid><name type="str">Alamakota</name><start_date type="str">2020-11-19T11:51:43.000Z</start_date><status type="str">Draft</status><version type="str">0.2</version><change_description type="str">Test</change_description><user_initials type="str">TODO Initials</user_initials></item></data></root>
"""
                },
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
            }
        },
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "library=library.name",
            "uid",
            "name",
            "start_date",
            "end_date",
            "status",
            "version",
            "change_description",
            "user_initials",
        ],
        "formats": [
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/xml",
            "application/json",
        ],
    }
)
# pylint: disable=unused-argument
def get_parameter_templates(
    request: Request,  # request is actually required by the allow_exports decorator
    status: LibraryItemStatus
    | None = Query(
        None,
        description="If specified, only those parameter templates will be returned that are currently in the specified status. "
        "This may be particularly useful if the parameter template has "
        "a) a 'Draft' and a 'Final' status or "
        "b) a 'Draft' and a 'Retired' status at the same time "
        "and you are interested in the 'Final' or 'Retired' status.\n"
        "Valid values are: 'Final', 'Draft' or 'Retired'.",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> list[ComplexParameterTemplate]:
    data: list[ComplexParameterTemplate] = Service(current_user_id).get_all(status)
    return data


@router.get(
    "/{uid}",
    dependencies=[rbac.LIBRARY_READ],
    summary="Returns the latest/newest version of a specific parameter template identified by 'uid'.",
    description="""If multiple request query parameters are used, then they need to
    match all at the same time (they are combined with the AND operation).""",
    response_model=ComplexParameterTemplateWithCount,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The parameter template with the specified 'uid' (and the specified date/time and/or status) wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_parameter_template(
    uid: str = ComplexParameterTemplateUID,
    return_instantiation_counts: bool
    | None = Query(
        None, description="if specified counts data will be returned along object"
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> ComplexParameterTemplate:
    return Service(current_user_id).get_by_uid(
        uid, return_instantiation_counts=bool(return_instantiation_counts)
    )


@router.get(
    "/{uid}/versions",
    dependencies=[rbac.LIBRARY_READ],
    summary="Returns the version history of a specific parameter template identified by 'uid'.",
    description=f"""
The returned versions are ordered by `start_date` descending (newest entries first)

{_generic_descriptions.DATA_EXPORTS_HEADER}
""",
    response_model=list[ComplexParameterTemplateVersion],
    status_code=200,
    responses={
        200: {
            "content": {
                "text/csv": {
                    "example": """
"library";"uid";"name";"start_date";"end_date";"status";"version";"change_description";"user_initials"
"Sponsor";"826d80a7-0b6a-419d-8ef1-80aa241d7ac7";"First  [ComparatorIntervention]";"2020-10-22T10:19:29+00:00";;"Draft";"0.1";"Initial version";"NdSJ"
"""
                },
                "text/xml": {
                    "example": """
                    <?xml version="1.0" encoding="UTF-8" ?><root><data type="list"><item type="dict"><name type="str">Alamakota</name><start_date type="str">2020-11-19 11:51:43+00:00</start_date><end_date type="str">None</end_date><status type="str">Draft</status><version type="str">0.2</version><change_description type="str">Test</change_description><user_initials type="str">TODO Initials</user_initials></item><item type="dict"><name type="str">Alamakota</name><start_date type="str">2020-11-19 11:51:07+00:00</start_date><end_date type="str">2020-11-19 11:51:43+00:00</end_date><status type="str">Draft</status><version type="str">0.1</version><change_description type="str">Initial version</change_description><user_initials type="str">TODO user initials</user_initials></item></data></root>
"""
                },
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
            }
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The parameter template with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "library=library.name",
            "name",
            "change_description",
            "status",
            "version",
            "start_date",
            "end_date",
            "user_initials",
        ],
        "formats": [
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/xml",
            "application/json",
        ],
    }
)
# pylint: disable=unused-argument
def get_parameter_template_versions(
    request: Request,  # request is actually required by the allow_exports decorator
    uid: str = ComplexParameterTemplateUID,
    current_user_id: str = Depends(get_current_user_id),
) -> list[ComplexParameterTemplateVersion]:
    return Service(current_user_id).get_version_history(uid)


@router.get(
    "/{uid}/versions/{version}",
    dependencies=[rbac.LIBRARY_READ],
    summary="Returns a specific version of a specific parameter template identified by 'uid' and 'version'.",
    description="**Multiple versions**:\n\n"
    "Technically, there can be multiple versions of the parameter template with the same version number. "
    "This is due to the fact, that the version number remains the same when inactivating or reactivating an parameter template "
    "(switching between 'Final' and 'Retired' status). \n\n"
    "In that case the latest/newest representation is returned.",
    response_model=ComplexParameterTemplate,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The parameter template with the specified 'uid' and 'version' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_parameter_template_version(
    uid: str = ComplexParameterTemplateUID,
    version: str = Path(
        None,
        description="A specific version number of the parameter template. "
        "The version number is specified in the following format: \\<major\\>.\\<minor\\> where \\<major\\> and \\<minor\\> are digits.\n"
        "E.g. '0.1', '0.2', '1.0', ...",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> ComplexParameterTemplate:
    return Service(current_user_id).get_specific_version(uid, version)


@router.post(
    "",
    dependencies=[rbac.LIBRARY_WRITE],
    summary="Creates a new parameter template in 'Draft' status.",
    description="""This request is only valid if the parameter template
* belongs to a library that allows creating (the 'is_editable' property of the library needs to be true).

If the request succeeds:
* The status will be automatically set to 'Draft'.
* The 'change_description' property will be set automatically.
* The 'version' property will be set to '0.1'.
* The parameter template will be linked to a library.

"""
    + PARAMETERS_NOTE,
    response_model=ComplexParameterTemplate,
    status_code=201,
    responses={
        201: {
            "description": "Created - The parameter template was successfully created."
        },
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The parameter template name is not valid.\n"
            "- The library does not allow to create parameter templates.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The library with the specified 'library_name' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def create_parameter_template(
    parameter_template: ComplexParameterTemplateCreateInput = (
        Body(description="The parameter template that shall be created.")
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> ComplexParameterTemplate:
    return Service(current_user_id).create(parameter_template)


@router.patch(
    "/{uid}",
    dependencies=[rbac.LIBRARY_WRITE],
    summary="Updates the parameter template identified by 'uid'.",
    description="""This request is only valid if the parameter template
* is in 'Draft' status and
* belongs to a library that allows editing (the 'is_editable' property of the library needs to be true).

If the request succeeds:
* The 'version' property will be increased automatically by +0.1.
* The status will remain in 'Draft'.

Parameters in the 'name' property can only be changed if the parameter template has never been approved.
Once the parameter template has been approved, only the surrounding text (excluding the parameters) can be changed.

"""
    + PARAMETERS_NOTE,
    response_model=ComplexParameterTemplate,
    status_code=200,
    responses={
        200: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The parameter template is not in draft status.\n"
            "- The parameter template name is not valid.\n"
            "- The library does not allow to edit draft versions.\n"
            "- The change of parameters of previously approved parameter templates.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The parameter template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def edit(
    uid: str = ComplexParameterTemplateUID,
    parameter_template: ComplexParameterTemplateEditInput = Body(
        description="The new content of the parameter template including the change description.",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> ComplexParameterTemplate:
    return Service(current_user_id).edit_draft(uid, parameter_template)


@router.post(
    "/{uid}/versions",
    dependencies=[rbac.LIBRARY_WRITE],
    summary="Creates a new version of the parameter template identified by 'uid'.",
    description="""This request is only valid if the parameter template
* is in 'Final' or 'Retired' status only (so no latest 'Draft' status exists) and
* belongs to a library that allows editing (the 'is_editable' property of the library needs to be true).

If the request succeeds:
* The latest 'Final' or 'Retired' version will remain the same as before.
* The status of the new version will be automatically set to 'Draft'.
* The 'version' property of the new version will be automatically set to the version of the latest 'Final' or 'Retired' version increased by +0.1.

Parameters in the 'name' property cannot be changed with this request.
Only the surrounding text (excluding the parameters) can be changed.
""",
    response_model=ComplexParameterTemplate,
    status_code=201,
    responses={
        201: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The parameter template is not in final or retired status or has a draft status.\n"
            "- The parameter template name is not valid.\n"
            "- The library does not allow to create a new version.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The parameter template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def create_new_version(
    uid: str = ComplexParameterTemplateUID,
    parameter_template: ComplexParameterTemplateEditInput = Body(
        description="The content of the parameter template for the new 'Draft' version including the change description.",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> ComplexParameterTemplate:
    return Service(current_user_id).create_new_version(uid, parameter_template)


@router.post(
    "/{uid}/approvals",
    dependencies=[rbac.LIBRARY_WRITE],
    summary="Approves the parameter template identified by 'uid'.",
    description="""This request is only valid if the parameter template
* is in 'Draft' status and
* belongs to a library that allows editing (the 'is_editable' property of the library needs to be true).
If parameter template has any related objects status will not be updated but item will be extended with 
related item counts.
If the request succeeds:
* The status will be automatically set to 'Final'.
* The 'change_description' property will be set automatically.
* The 'version' property will be increased automatically to the next major version.
    """,
    response_model=ComplexParameterTemplate,
    status_code=201,
    responses={
        201: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The parameter template is not in draft status.\n"
            "- The library does not allow to approve drafts.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The parameter template with the specified 'uid' could not be found.",
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflict - there are parameters created from template and cascade is false",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def approve(
    uid: str = ComplexParameterTemplateUID,
    current_user_id: str = Depends(get_current_user_id),
) -> ComplexParameterTemplate:
    """
    Approves parameter template. Fails with 409 if there is some complex-parameters created
    from this template and cascade is false
    """
    return Service(current_user_id).approve(uid=uid)


@router.delete(
    "/{uid}/activations",
    dependencies=[rbac.LIBRARY_WRITE],
    summary="Inactivates/deactivates the parameter template identified by 'uid'.",
    description="""This request is only valid if the parameter template
* is in 'Final' status only (so no latest 'Draft' status exists).

If the request succeeds:
* The status will be automatically set to 'Retired'.
* The 'change_description' property will be set automatically.
* The 'version' property will remain the same as before.
    """,
    response_model=ComplexParameterTemplate,
    status_code=200,
    responses={
        200: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The parameter template is not in final status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The parameter template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def inactivate(
    uid: str = ComplexParameterTemplateUID,
    current_user_id: str = Depends(get_current_user_id),
) -> ComplexParameterTemplate:
    return Service(current_user_id).inactivate_final(uid)


@router.post(
    "/{uid}/activations",
    dependencies=[rbac.LIBRARY_WRITE],
    summary="Reactivates the parameter template identified by 'uid'.",
    description="""This request is only valid if the parameter template
* is in 'Retired' status only (so no latest 'Draft' status exists).

If the request succeeds:
* The status will be automatically set to 'Final'.
* The 'change_description' property will be set automatically.
* The 'version' property will remain the same as before.
    """,
    response_model=ComplexParameterTemplate,
    status_code=200,
    responses={
        200: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The parameter template is not in retired status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The parameter template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def reactivate(
    uid: str = ComplexParameterTemplateUID,
    current_user_id: str = Depends(get_current_user_id),
) -> ComplexParameterTemplate:
    return Service(current_user_id).reactivate_retired(uid)


@router.delete(
    "/{uid}",
    dependencies=[rbac.LIBRARY_WRITE],
    summary="Deletes the parameter template identified by 'uid'.",
    description="""This request is only valid if \n
* the parameter template is in 'Draft' status and
* the parameter template has never been in 'Final' status and
* the parameter template has no references to any complex-parameters and
* the parameter template belongs to a library that allows deleting (the 'is_editable' property of the library needs to be true).""",
    response_model=None,
    status_code=204,
    responses={
        204: {
            "description": "No Content - The parameter template was successfully deleted."
        },
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The parameter template is not in draft status.\n"
            "- The parameter template was already in final state or is in use.\n"
            "- The library does not allow to delete parameter templates.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - An parameter template with the specified uid could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def delete_parameter_template(
    uid: str = ComplexParameterTemplateUID,
    current_user_id: str = Depends(get_current_user_id),
) -> None:
    Service(current_user_id).soft_delete(uid)


# TODO this endpoint potentially returns duplicated entries (by intention, currently).
#       however: check if that is ok with regard to the data volume we expect in the future. is paging needed?
@router.get(
    "/{uid}/parameters",
    dependencies=[rbac.LIBRARY_READ],
    summary="Returns all parameters used in the parameter template identified by 'uid'. Includes the available values per parameter.",
    description="""The returned parameters are ordered
0. as they occur in the parameter template

Per parameter, the parameter.values are ordered by
0. value.name ascending

Note that parameters may be used multiple times in templates.
In that case, the same parameter (with the same values) is included multiple times in the response.
    """,
    response_model=list[ComplexTemplateParameter],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_parameters(
    uid: str = Path(None, description="The unique id of the parameter template."),
    current_user_id: str = Depends(get_current_user_id),
):
    return Service(current_user_id).get_parameters(uid)


@router.post(
    "/pre-validate",
    dependencies=[rbac.LIBRARY_WRITE],
    summary="Validates the content of an parameter template without actually processing it.",
    description="""Be aware that - even if this request is accepted - there is no guarantee that
a following request to e.g. *[POST] /parameter-templates* or *[PATCH] /complex-parameter-templates/{uid}*
with the same content will succeed.

"""
    + PARAMETERS_NOTE,
    status_code=202,
    responses={
        202: {
            "description": "Accepted. The content is valid and may be submitted in another request."
        },
        400: {
            "model": ErrorResponse,
            "description": "Forbidden. The content is invalid - Reasons include e.g.: \n"
            "- The syntax of the 'name' is not valid.\n"
            "- One of the parameters wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def pre_validate(
    parameter_template: ComplexParameterTemplateNameInput = Body(
        description="The content of the parameter template that shall be validated.",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    Service(current_user_id).validate_template_syntax(parameter_template.name)
