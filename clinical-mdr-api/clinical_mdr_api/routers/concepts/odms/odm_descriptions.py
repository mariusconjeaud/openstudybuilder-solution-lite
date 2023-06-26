from typing import Any, List, Optional

from fastapi import APIRouter, Body, Path, Query
from pydantic.types import Json

from clinical_mdr_api import config
from clinical_mdr_api.models import (
    OdmDescription,
    OdmDescriptionBatchInput,
    OdmDescriptionBatchOutput,
    OdmDescriptionPatchInput,
    OdmDescriptionPostInput,
)
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.models.utils import CustomPage
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.routers import _generic_descriptions
from clinical_mdr_api.services.concepts.odms.odm_descriptions import (
    OdmDescriptionService,
)

router = APIRouter()

# Argument definitions
OdmDescriptionUID = Path(None, description="The unique id of the ODM Description.")


@router.get(
    "",
    summary="Return a listing of ODM Descriptions",
    description="",
    response_model=CustomPage[OdmDescription],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_all_odm_descriptions(
    library: Optional[str] = Query(None),
    sort_by: Json = Query(None, description=_generic_descriptions.SORT_BY),
    page_number: Optional[int] = Query(
        1, ge=1, description=_generic_descriptions.PAGE_NUMBER
    ),
    page_size: Optional[int] = Query(
        config.DEFAULT_PAGE_SIZE,
        ge=0,
        le=config.MAX_PAGE_SIZE,
        description=_generic_descriptions.PAGE_SIZE,
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
):
    odm_description_service = OdmDescriptionService()
    results = odm_description_service.get_all_concepts(
        library=library,
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
    library_name: Optional[str] = Query(None),
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
    odm_description_service = OdmDescriptionService()
    return odm_description_service.get_distinct_values_for_header(
        library=library_name,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/{uid}/relationships",
    summary="Get UIDs of a specific ODM Description's relationships",
    description="",
    response_model=dict,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_active_relationships(uid: str = OdmDescriptionUID):
    odm_description_service = OdmDescriptionService()
    return odm_description_service.get_active_relationships(uid=uid)


@router.get(
    "/{uid}/versions",
    summary="Return a listing of versions of a specific ODM Description",
    description="""
State before:
 - uid must exist.

Business logic:
 - List version history for ODM Descriptions.
 - The returned versions are ordered by start_date descending (newest entries first).

State after:
 - No change

Possible errors:
 - Invalid uid.
    """,
    response_model=List[OdmDescription],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Description with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_odm_description_versions(uid: str = OdmDescriptionUID):
    odm_description_service = OdmDescriptionService()
    return odm_description_service.get_version_history(uid=uid)


@router.post(
    "",
    summary="Create a new ODM Description",
    description="",
    response_model=OdmDescription,
    status_code=201,
    responses={
        201: {"description": "Created - The ODM Description was successfully created."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The library does not exist.\n"
            "- The library does not allow to add new items.\n",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def create_odm_description(
    odm_description_create_input: OdmDescriptionPostInput = Body(description=""),
):
    odm_description_service = OdmDescriptionService()
    return odm_description_service.create(concept_input=odm_description_create_input)


@router.post(
    "/batch",
    summary="Batch operations (create, edit) for ODM Descriptions",
    description="",
    response_model=List[OdmDescriptionBatchOutput],
    status_code=207,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def odm_description_batch_operations(
    operations: List[OdmDescriptionBatchInput] = Body(
        description="List of operation to perform"
    ),
):
    odm_description_service = OdmDescriptionService()
    return odm_description_service.handle_batch_operations(operations)


@router.patch(
    "/{uid}",
    summary="Update an ODM Description",
    description="",
    response_model=OdmDescription,
    status_code=200,
    responses={
        200: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Description is not in draft status.\n"
            "- The ODM Description had been in 'Final' status before.\n"
            "- The library does not allow to edit draft versions.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Description with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def edit_odm_description(
    uid: str = OdmDescriptionUID,
    odm_description_edit_input: OdmDescriptionPatchInput = Body(description=""),
):
    odm_description_service = OdmDescriptionService()
    return odm_description_service.edit_draft(
        uid=uid, concept_edit_input=odm_description_edit_input
    )


@router.post(
    "/{uid}/versions",
    summary="Create a new version of an ODM Description",
    description="""
State before:
 - uid must exist and the ODM Description must be in status Final.

Business logic:
- The ODM Description is changed to a draft state.

State after:
 - ODM Description changed status to Draft and assigned a new minor version number.
 - Audit trail entry must be made with action of creating a new draft version.

Possible errors:
 - Invalid uid or status not Final.
""",
    response_model=OdmDescription,
    status_code=201,
    responses={
        201: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The library does not allow to create ODM Descriptions.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Reasons include e.g.: \n"
            "- The ODM Description is not in final status.\n"
            "- The ODM Description with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def create_odm_description_version(uid: str = OdmDescriptionUID):
    odm_description_service = OdmDescriptionService()
    return odm_description_service.create_new_version(uid=uid)


@router.post(
    "/{uid}/approvals",
    summary="Approve an ODM Description",
    description="",
    response_model=OdmDescription,
    status_code=201,
    responses={
        201: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Description is not in draft status.\n"
            "- The library does not allow to approve ODM Description.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Description with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def approve_odm_description(uid: str = OdmDescriptionUID):
    odm_description_service = OdmDescriptionService()
    return odm_description_service.approve(uid=uid)


@router.delete(
    "/{uid}/activations",
    summary=" Inactivate an ODM Description",
    description="",
    response_model=OdmDescription,
    status_code=200,
    responses={
        200: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Description is not in final status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Description with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def inactivate_odm_description(uid: str = OdmDescriptionUID):
    odm_description_service = OdmDescriptionService()
    return odm_description_service.inactivate_final(uid=uid)


@router.post(
    "/{uid}/activations",
    summary="Reactivate an ODM Description",
    description="",
    response_model=OdmDescription,
    status_code=200,
    responses={
        200: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Description is not in retired status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Description with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def reactivate_odm_description(uid: str = OdmDescriptionUID):
    odm_description_service = OdmDescriptionService()
    return odm_description_service.reactivate_retired(uid=uid)


@router.delete(
    "/{uid}",
    summary="Delete draft version of ODM Description",
    description="",
    response_model=None,
    status_code=204,
    responses={
        204: {
            "description": "No Content - The ODM Description was successfully deleted."
        },
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Description is not in draft status.\n"
            "- The ODM Description was already in final state or is in use.\n"
            "- The library does not allow to delete ODM Description.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - An ODM Description with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def delete_odm_description(uid: str = OdmDescriptionUID):
    odm_description_service = OdmDescriptionService()
    odm_description_service.soft_delete(uid=uid)
