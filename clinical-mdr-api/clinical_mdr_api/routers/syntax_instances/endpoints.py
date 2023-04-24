from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, Path, Query, Request, Response
from fastapi import status as fast_api_status
from pydantic.types import Json

from clinical_mdr_api import config, models
from clinical_mdr_api.domain_repositories.models.syntax import EndpointValue
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.models.study import Study
from clinical_mdr_api.models.utils import CustomPage
from clinical_mdr_api.oauth import get_current_user_id
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.routers import _generic_descriptions, decorators
from clinical_mdr_api.services.syntax_instances.endpoints import EndpointService

router = APIRouter()

Service = EndpointService

# Argument definitions
EndpointUID = Path(None, description="The unique id of the endpoint.")


@router.get(
    "",
    summary="Returns all final versions of endpoints referenced by any study.",
    description=_generic_descriptions.DATA_EXPORTS_HEADER,
    response_model=CustomPage[models.Endpoint],
    status_code=200,
    responses={
        200: {
            "content": {
                "text/csv": {
                    "example": """
"library","uid","objective","endpoint_template","endpoint","start_date","end_date","status","version","change_description","user_initials"
"Sponsor","826d80a7-0b6a-419d-8ef1-80aa241d7ac7","Objective","First [ComparatorIntervention]","First Intervention","2020-10-22T10:19:29+00:00",,"Draft","0.1","Initial version","NdSJ"
"""
                },
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
                "text/xml": {
                    "example": """
<?xml version="1.0" encoding="UTF-8" ?>
<root>
    <data type="list">
        <item type="dict">
            <library type="str">Sponsor</library>
            <uid type="str">682d7003-8dcc-480d-b07b-878e659b8697</uid>
            <objective type="str">Test template new [glucose metabolism] [MACE+] totot</objective>
            <endpoint_template type="str">Endpoint using [Activity] and [Indication]</endpoint_template>
            <endpoint type="str">Endpoint using [body weight] and [type 2 diabetes]</endpoint>
            <start_date type="str">2020-11-26T13:43:23.000Z</start_date>
            <end_date type="str"></end_date>
            <status type="str">Draft</status>
            <version type="str">0.2</version>
            <change_description type="str">Changed indication</change_description>
            <user_initials type="str">TODO Initials</user_initials>
        </item>
    </data>
</root>
"""
                },
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
            "objective=objective.name",
            "endpoint_template=endpoint_template.name",
            "endpoint=name",
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
def get_all(
    request: Request,  # request is actually required by the allow_exports decorator
    sort_by: Json = Query(None, description=_generic_descriptions.SORT_BY),
    page_number: Optional[int] = Query(
        1, ge=1, description=_generic_descriptions.PAGE_NUMBER
    ),
    page_size: Optional[int] = Query(
        config.DEFAULT_PAGE_SIZE, ge=0, description=_generic_descriptions.PAGE_SIZE
    ),
    filters: Optional[Json] = Query(
        None,
        description=_generic_descriptions.FILTERS,
        example=_generic_descriptions.FILTERS_EXAMPLE,
    ),
    operator: Optional[str] = Query("and", description=_generic_descriptions.OPERATOR),
    total_count: Optional[bool] = Query(
        False, description=_generic_descriptions.TOTAL_COUNT
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    all_items = EndpointService(current_user_id).get_all(
        return_study_count=True,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
    )

    return CustomPage.create(
        items=all_items.items,
        total=all_items.total_count,
        page=page_number,
        size=page_size,
    )


@router.get(
    "/headers",
    summary="Returns possible values from the database for a given header",
    description="""Allowed parameters include : field name for which to get possible
    values, search string to provide filtering for the field name, additional filters to apply on other fields""",
    response_model=List[Any],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Invalid field name specified",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_distinct_values_for_header(
    current_user_id: str = Depends(get_current_user_id),
    status: Optional[str] = Query(
        None,
        description="If specified, only those objective templates will be returned that are currently in the specified status. "
        "This may be particularly useful if the objective template has "
        "a) a 'Draft' and a 'Final' status or "
        "b) a 'Draft' and a 'Retired' status at the same time "
        "and you are interested in the 'Final' or 'Retired' status.\n"
        "Valid values are: 'Final', 'Draft' or 'Retired'.",
    ),
    field_name: str = Query(..., description=_generic_descriptions.HEADER_FIELD_NAME),
    search_string: Optional[str] = Query(
        "", description=_generic_descriptions.HEADER_SEARCH_STRING
    ),
    filters: Optional[Json] = Query(
        None,
        description=_generic_descriptions.FILTERS,
        example=_generic_descriptions.FILTERS_EXAMPLE,
    ),
    operator: Optional[str] = Query("and", description=_generic_descriptions.OPERATOR),
    result_count: Optional[int] = Query(
        10, description=_generic_descriptions.HEADER_RESULT_COUNT
    ),
):
    return Service(current_user_id).get_distinct_values_for_header(
        status=status,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/{uid}",
    summary="Returns the latest/newest version of a specific endpoint identified by 'uid'.",
    description="""If multiple request query parameters are used, then they need to
    match all at the same time (they are combined with the AND operation).""",
    response_model=Optional[models.Endpoint],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The endpoint with the specified 'uid' (and the specified date/time and/or status) wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get(
    uid: str = EndpointUID,
    at_specified_date_time: Optional[datetime] = Query(
        None,
        description="If specified, the latest/newest representation of the endpoint at this point in time is returned.\n"
        "The point in time needs to be specified in ISO 8601 format including the timezone, e.g.: "
        "'2020-10-31T16:00:00+02:00' for October 31, 2020 at 4pm in UTC+2 timezone. "
        "If the timezone is ommitted, UTC±0 is assumed.",
    ),
    status: Optional[str] = Query(
        None,
        description="If specified, the representation of the endpoint in that status is returned (if existent). "
        "This may be particularly useful if the endpoint has "
        "a) a 'Draft' and a 'Final' status or "
        "b) a 'Draft' and a 'Retired' status at the same time "
        "and you are interested in the 'Final' or 'Retired' status.\n"
        "Valid values are: 'Final', 'Draft' or 'Retired'.",
    ),
    version: Optional[str] = Query(
        None,
        description=r"If specified, the latest/newest representation of the endpoint in that version is returned. "
        r"Only exact matches are considered. "
        r"The version is specified in the following format: \<major\>.\<minor\> where \<major\> and \<minor\> are digits. "
        r"E.g. '0.1', '0.2', '1.0', ...",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    if at_specified_date_time is not None or status is not None or version is not None:
        raise NotImplementedError(
            "TODO: support for at_specified_date, status and version parameters not implemented."
        )
    return EndpointService(current_user_id).get_by_uid(uid=uid)


@router.get(
    "/{uid}/versions",
    summary="Returns the version history of a specific endpoint identified by 'uid'.",
    description=f"""
The returned versions are ordered by `start_date` descending (newest entries first).

{_generic_descriptions.DATA_EXPORTS_HEADER}
""",
    response_model=List[models.EndpointVersion],
    status_code=200,
    responses={
        200: {
            "content": {
                "text/csv": {
                    "example": """
"library","endpoint_template","objective","uid","endpoint","start_date","end_date","status","version","change_description","user_initials"
"Sponsor","First [ComparatorIntervention]","Objective","826d80a7-0b6a-419d-8ef1-80aa241d7ac7","First Intervention","2020-10-22T10:19:29+00:00",,"Draft","0.1","Initial version","NdSJ"
"""
                },
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
                "text/xml": {
                    "example": """
<?xml version="1.0" encoding="UTF-8" ?>
<root>
    <data type="list">
        <item type="dict">
            <library type="str">Sponsor</library>
            <endpoint_template type="str">Endpoint using [Activity] and [Indication]</endpoint_template>
            <objective type="str">Test template new [glucose metabolism] [MACE+] totot</objective>
            <uid type="str">682d7003-8dcc-480d-b07b-878e659b8697</uid>
            <endpoint type="str">Endpoint using [body weight] and [type 2 diabetes]</endpoint>
            <start_date type="str">2020-11-26T13:43:23.000Z</start_date>
            <end_date type="str"></end_date>
            <status type="str">Draft</status>
            <version type="str">0.2</version>
            <change_description type="str">Changed indication</change_description>
            <user_initials type="str">TODO Initials</user_initials>
        </item>
    </data>
</root>
"""
                },
            }
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The endpoint with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.allow_exports(
    {
        "text/csv": [
            "library=library.name",
            "endpoint_template=endpoint_template.name",
            "objective=objective.name",
            "uid",
            "endpoint=name",
            "start_date",
            "end_date",
            "status",
            "version",
            "change_description",
            "user_initials",
        ],
        "text/xml": [
            "library=library.name",
            "endpoint_template=endpoint_template.name",
            "objective=objective.name",
            "uid",
            "endpoint=name",
            "start_date",
            "end_date",
            "status",
            "version",
            "change_description",
            "user_initials",
        ],
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
            "library=library.name",
            "endpoint_template=endpoint_template.name",
            "objective=objective.name",
            "uid",
            "endpoint=name",
            "start_date",
            "end_date",
            "status",
            "version",
            "change_description",
            "user_initials",
        ],
    }
)
# pylint: disable=unused-argument
def get_versions(
    request: Request,  # request is actually required by the allow_exports decorator
    uid: str = EndpointUID,
    current_user_id: str = Depends(get_current_user_id),
):
    return EndpointService(current_user_id).get_version_history(uid)


@router.get(
    "/{uid}/studies",
    summary="",
    description="",
    response_model=List[Study],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The endpoint with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_studies(
    uid: str = EndpointUID,
    current_user_id: str = Depends(get_current_user_id),
    fields: Optional[str] = Query(
        default=None,
        description="Parameter specifies which parts of the whole Study Definition representation to retrieve. In"
        " the form of comma separated name of the fields prefixed by (optional) `+` "
        " if the client wishes"
        " to retrieve the field or `-` if the client wants to skip the field."
        " If not specified identification metadata and version metadata are retrieved."
        " If value starts with `+` or `-` above default is extended or reduced by the specified fields"
        " otherwise (if not started with `+` or `-`) provided fields specification"
        " replaces the default. Currently supported fields are"
        " `current_metadata.identification_metadata`, `current_metadata.high_level_study_design`"
        " , `current_metadata.study_population` and `current_metadata.study_intervention`"
        " , `current_metadata.study_description`.",
    ),
):
    return Service(current_user_id).get_referencing_studies(
        uid=uid, node_type=EndpointValue, fields=fields
    )


@router.post(
    "",
    summary="Creates a new endpoint in 'Draft' status.",
    description="""This request is only valid if
* the specified endpoint template is in 'Final' status and
* the specified objective is in 'Final' status and
* the specified library allows creating endpoints (the 'is_editable' property of the library needs to be true) and
* the endpoint does not yet exist (no endpoint with the same content in 'Final' or 'Draft' status).

If the request succeeds:
* The status will be automatically set to 'Draft'.
* The 'change_description' property will be set automatically.
* The 'version' property will be set to '0.1'.
""",
    response_model=models.Endpoint,
    status_code=201,
    responses={
        201: {"description": "Created - The endpoint was successfully created."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The provided list of parameters is invalid.\n"
            "- The objective wasn't found or it is not in 'Final' status.\n"
            "- The library does not allow to create endpoints.\n"
            "- The endpoint does already exist.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Reasons include e.g.: \n"
            "- The library with the specified 'library_name' could not be found.\n"
            "- The endpoint template with the specified 'endpoint_template_uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def create(
    endpoint: models.EndpointCreateInput = Body(
        description="Related parameters of the endpoint that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    return EndpointService(current_user_id).create(endpoint)
    # return service.create(endpoint)


@router.post(
    "/preview",
    summary="Previews the creation of a new endpoint.",
    description="""This request is only valid if
* the specified endpoint template is in 'Final' status and
* the specified library allows creating endpoints (the 'is_editable' property of the library needs to be true) and
* the endpoint does not yet exist (no endpoint with the same content in 'Final' or 'Draft' status).

If the request succeeds:
* No endpoint will be created, but the result of the request will show what the endpoint will look like.
""",
    response_model=models.Endpoint,
    status_code=200,
    responses={
        200: {"description": "Success - The endpoint is able to be created."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The provided list of parameters is invalid.\n"
            "- The library does not allow to create endpoints.\n"
            "- The endpoint does already exist.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Reasons include e.g.: \n"
            "- The library with the specified 'library_name' could not be found.\n"
            "- The endpoint template with the specified 'endpoint_template_uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def preview(
    endpoint: models.EndpointCreateInput = Body(
        description="Related parameters of the endpoint that shall be previewed."
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    return EndpointService(current_user_id).create(endpoint, preview=True)


@router.patch(
    "/{uid}",
    summary="Updates the endpoint identified by 'uid'.",
    description="""This request is only valid if the endpoint
* is in 'Draft' status and
* belongs to a library that allows editing (the 'is_editable' property of the library needs to be true). 

If the request succeeds:
* The 'version' property will be increased automatically by +0.1.
* The status will remain in 'Draft'.
* The link to the objective will remain as is.
""",
    response_model=models.Endpoint,
    status_code=200,
    responses={
        200: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The endpoint is not in draft status.\n"
            "- The endpoint had been in 'Final' status before.\n"
            "- The provided list of parameters is invalid.\n"
            "- The library does not allow to edit draft versions.\n"
            "- The endpoint does already exist.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The endpoint with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def edit(
    uid: str = EndpointUID,
    endpoint: models.EndpointEditInput = Body(
        description="The new parameter terms for the endpoint including the change description.",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    return EndpointService(current_user_id).edit_draft(uid=uid, template=endpoint)


@router.post(
    "/{uid}/approvals",
    summary="Approves the endpoint identified by 'uid'.",
    description="""This request is only valid if the endpoint
* is in 'Draft' status and
* belongs to a library that allows editing (the 'is_editable' property of the library needs to be true).

If the request succeeds:
* The status will be automatically set to 'Final'.
* The 'change_description' property will be set automatically.
* The 'version' property will be increased automatically to the next major version.
    """,
    response_model=models.Endpoint,
    status_code=201,
    responses={
        201: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The endpoint is not in draft status.\n"
            "- The library does not allow to approve endpoints.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The endpoint with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def approve(
    uid: str = EndpointUID, current_user_id: str = Depends(get_current_user_id)
):
    return EndpointService(current_user_id).approve(uid)
    # return service.approve_draft(uid)


@router.delete(
    "/{uid}/activations",
    summary="Inactivates/deactivates the endpoint identified by 'uid'.",
    description="""This request is only valid if the endpoint
* is in 'Final' status only (so no latest 'Draft' status exists).

If the request succeeds:
* The status will be automatically set to 'Retired'.
* The 'change_description' property will be set automatically. 
* The 'version' property will remain the same as before.
    """,
    response_model=models.Endpoint,
    status_code=200,
    responses={
        200: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The endpoint is not in final status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The endpoint with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def inactivate(
    uid: str = EndpointUID, current_user_id: str = Depends(get_current_user_id)
):
    return EndpointService(current_user_id).inactivate_final(uid)


# TODO check if * there is no other endpoint with the same name (it may be that one had been created after inactivating this one here)
@router.post(
    "/{uid}/activations",
    summary="Reactivates the endpoint identified by 'uid'.",
    description="""This request is only valid if the endpoint
* is in 'Retired' status only (so no latest 'Draft' status exists).

If the request succeeds:
* The status will be automatically set to 'Final'.
* The 'change_description' property will be set automatically. 
* The 'version' property will remain the same as before.
    """,
    response_model=models.Endpoint,
    status_code=200,
    responses={
        200: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The endpoint is not in retired status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The endpoint with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def reactivate(
    uid: str = EndpointUID, current_user_id: str = Depends(get_current_user_id)
):
    return EndpointService(current_user_id).reactivate_retired(uid)
    # return service.reactivate_retired(uid)


@router.delete(
    "/{uid}",
    summary="Deletes the endpoint identified by 'uid'.",
    description="""This request is only valid if \n
* the endpoint is in 'Draft' status and
* the endpoint has never been in 'Final' status and
* the endpoint belongs to a library that allows deleting (the 'is_editable' property of the library needs to be true).""",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The endpoint was successfully deleted."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The endpoint is not in draft status.\n"
            "- The endpoint was already in final state or is in use.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - An endpoint with the specified uid could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def delete(uid: str = EndpointUID, current_user_id: str = Depends(get_current_user_id)):
    EndpointService(current_user_id).soft_delete(uid)
    return Response(status_code=fast_api_status.HTTP_204_NO_CONTENT)


# TODO this endpoint potentially returns duplicated entries (by intention, currently).
#       however: check if that is ok with regard to the data volume we expect in the future. is paging needed?
@router.get(
    "/{uid}/parameters",
    summary="Returns all template parameters available for the endpoint identified by 'uid'. Includes the available values per parameter.",
    description="""Returns all template parameters used in the endpoint template
that is the basis for the endpoint identified by 'uid'. 
Includes the available values per parameter.

The returned parameters are ordered
0. as they occur in the endpoint template

Per parameter, the parameter.values are ordered by
0. value.name ascending

Note that parameters may be used multiple times in templates.
In that case, the same parameter (with the same values) is included multiple times in the response.
    """,
    response_model=List[models.TemplateParameter],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_parameters(
    uid: str = Path(None, description="The unique id of the endpoint."),
    current_user_id: str = Depends(get_current_user_id),
):
    return EndpointService(current_user_id).get_parameters(uid)
