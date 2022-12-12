"""CTCodelistName router."""
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, Path, Query
from fastapi_etag import Etag
from pydantic.types import Json
from starlette.requests import Request

from clinical_mdr_api import config, models
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.models.utils import CustomPage
from clinical_mdr_api.oauth import get_current_user_id
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.routers import _generic_descriptions
from clinical_mdr_api.services.ct_codelist_name import CTCodelistNameService

router = APIRouter()

CTCodelistUID = Path(None, description="The unique id of the CTCodelistName")


def get_etag(request: Request) -> str:
    ct_codelist_name_service = CTCodelistNameService()
    return ct_codelist_name_service.get_codelist_etag(request)


@router.get(
    "/codelists/names",
    summary="Returns all codelists names.",
    response_model=CustomPage[models.CTCodelistName],
    status_code=200,
    responses={500: {"model": ErrorResponse, "description": "Internal Server Error"}},
)
def get_codelists(
    catalogue_name: str = Query(
        None,
        description="If specified, only codelists from given catalogue are returned.",
    ),
    library: Optional[str] = Query(
        None,
        description="If specified, only codelists from given library are returned.",
    ),
    package: Optional[str] = Query(
        None,
        description="If specified, only codelists from given package are returned.",
    ),
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
    ct_codelist_name_service = CTCodelistNameService(user=current_user_id)
    results = ct_codelist_name_service.get_all_ct_codelists(
        catalogue_name=catalogue_name,
        library=library,
        package=package,
        sort_by=sort_by,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
    )
    return CustomPage.create(
        items=results.items, total=results.total_count, page=page_number, size=page_size
    )


@router.get(
    "/codelists/names/headers",
    summary="Returns possibles values from the database for a given header",
    description="""Allowed parameters include : field name for which to get possible
    values, search string to provide filtering for the field name, additional filters to apply on other fields""",
    response_model=List[Any],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Invalid field name specified",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_distinct_values_for_header(
    current_user_id: str = Depends(get_current_user_id),
    catalogue_name: str = Query(
        None,
        description="If specified, only codelists from given catalogue are returned.",
    ),
    library: Optional[str] = Query(
        None, description="If specified, only terms from given library are returned."
    ),
    package: Optional[str] = Query(
        None, description="If specified, only terms from given package are returned."
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
    ct_codelist_name_service = CTCodelistNameService(user=current_user_id)
    return ct_codelist_name_service.get_distinct_values_for_header(
        catalogue_name=catalogue_name,
        library=library,
        package=package,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/codelists/{codelist_uid}/names",
    dependencies=[Depends(Etag(get_etag))],
    summary="Returns the latest/newest version of a specific codelist identified by 'uid'",
    response_model=models.CTCodelistName,
    status_code=200,
    responses={500: {"model": ErrorResponse, "description": "Internal Server Error"}},
)
def get_codelist_names(
    codelist_uid: str = CTCodelistUID,
    at_specified_date_time: Optional[datetime] = Query(
        None,
        description="If specified then the latest/newest representation of the sponsor defined name "
        "for CTCodelistNameValue at this point in time is returned.\n"
        "The point in time needs to be specified in ISO 8601 format including the timezone, "
        "e.g.: '2020-10-31T16:00:00+02:00' for October 31, 2020 at 4pm in UTC+2 timezone. "
        "If the timezone is omitted, UTC±0 is assumed.",
    ),
    status: Optional[str] = Query(
        None,
        description="If specified then the representation of the sponsor defined name for "
        "CTCodelistNameValue in that status is returned (if existent).\n_this is useful if the"
        " CTCodelistNameValue has a status 'Draft' and a status 'Final'.",
    ),
    version: Optional[str] = Query(
        None,
        description="If specified then the latest/newest representation of the sponsor defined name "
        "for CTCodelistNameValue in that version is returned.\n"
        "Only exact matches are considered. The version is specified in the following format:"
        "<major>.<minor> where <major> and <minor> are digits. E.g. '0.1', '0.2', '1.0',",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    ct_codelist_name_service = CTCodelistNameService(user=current_user_id)
    return ct_codelist_name_service.get_by_uid(
        codelist_uid=codelist_uid,
        at_specific_date=at_specified_date_time,
        status=status,
        version=version,
    )


@router.get(
    "/codelists/{codelist_uid}/names/versions",
    summary="Returns the version history of a specific CTCodelistName identified by 'codelist_uid'.",
    description="The returned versions are ordered by\n"
    "0. start_date descending (newest entries first)",
    response_model=List[models.CTCodelistNameVersion],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The codelist with the specified 'codelist_uid' wasn't found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_versions(
    codelist_uid: str = CTCodelistUID,
    current_user_id: str = Depends(get_current_user_id),
):
    ct_codelist_name_service = CTCodelistNameService(user=current_user_id)
    return ct_codelist_name_service.get_version_history(codelist_uid=codelist_uid)


@router.patch(
    "/codelists/{codelist_uid}/names",
    summary="Updates the codelist identified by 'codelist_uid'.",
    description="""This request is only valid if the codelist
* is in 'Draft' status and
* belongs to a library that allows editing (the 'is_editable' property of the library needs to be true). 

If the request succeeds:
* The 'version' property will be increased automatically by +0.1.
* The status will remain in 'Draft'.
""",
    response_model=models.CTCodelistName,
    status_code=200,
    responses={
        200: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The codelist is not in draft status.\n"
            "- The codelist had been in 'Final' status before.\n"
            "- The library does not allow to edit draft versions.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The codelist with the specified 'codelist_uid' wasn't found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def edit(
    codelist_uid: str = CTCodelistUID,
    codelist_input: models.CTCodelistNameEditInput = Body(
        None,
        description="The new parameter values for the codelist including the change description.",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    ct_codelist_name_service = CTCodelistNameService(user=current_user_id)
    return ct_codelist_name_service.edit_draft(
        codelist_uid=codelist_uid, codelist_input=codelist_input
    )


@router.post(
    "/codelists/{codelist_uid}/names/versions",
    summary="Creates a new codelist in 'Draft' status.",
    description="""This request is only valid if
* the specified codelist is in 'Final' status and
* the specified library allows creating codelists (the 'is_editable' property of the library needs to be true).

If the request succeeds:
* The status will be automatically set to 'Draft'.
* The 'change_description' property will be set automatically to 'new-version'.
* The 'version' property will be increased by '0.1'.
""",
    response_model=models.CTCodelistName,
    status_code=201,
    responses={
        201: {"description": "Created - The codelist was successfully created."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The library does not allow to create codelists.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Reasons include e.g.: \n"
            "- The codelist is not in final status.\n"
            "- The codelist with the specified 'codelist_uid' could not be found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def create(
    codelist_uid: str = CTCodelistUID,
    current_user_id: str = Depends(get_current_user_id),
):
    ct_codelist_name_service = CTCodelistNameService(user=current_user_id)
    return ct_codelist_name_service.create_new_version(codelist_uid=codelist_uid)


@router.post(
    "/codelists/{codelist_uid}/names/approve",
    summary="Approves the codelist identified by 'codelist_uid'.",
    description="""This request is only valid if the codelist
* is in 'Draft' status and
* belongs to a library that allows editing (the 'is_editable' property of the library needs to be true).

If the request succeeds:
* The status will be automatically set to 'Final'.
* The 'change_description' property will be set automatically to 'Approved version'.
* The 'version' property will be increased automatically to the next major version.
    """,
    response_model=models.CTCodelistName,
    status_code=201,
    responses={
        201: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The codelist is not in draft status.\n"
            "- The library does not allow to approve codelist.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The codelist with the specified 'codelist_uid' wasn't found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def approve(
    codelist_uid: str = CTCodelistUID,
    current_user_id: str = Depends(get_current_user_id),
):
    ct_codelist_name_service = CTCodelistNameService(user=current_user_id)
    return ct_codelist_name_service.approve(codelist_uid=codelist_uid)
