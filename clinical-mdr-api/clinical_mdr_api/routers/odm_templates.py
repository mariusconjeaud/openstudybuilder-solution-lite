from typing import Any, List, Optional

from fastapi import APIRouter, Body, Path, Query
from pydantic.types import Json
from starlette.requests import Request

from clinical_mdr_api import config
from clinical_mdr_api.models import (
    OdmTemplate,
    OdmTemplateFormPostInput,
    OdmTemplatePatchInput,
    OdmTemplatePostInput,
)
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.models.utils import CustomPage
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.routers import _generic_descriptions, decorators
from clinical_mdr_api.services.odm_templates import OdmTemplateService

router = APIRouter()

# Argument definitions
OdmTemplateUID = Path(None, description="The unique id of the ODM Template.")


@router.get(
    "",
    summary="Return every variable related to the selected status and version of the ODM Templates",
    description=_generic_descriptions.DATA_EXPORTS_HEADER,
    response_model=CustomPage[OdmTemplate],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "uid",
            "oid",
            "library_name",
            "name",
            "description",
            "forms",
            "start_date",
            "end_date",
            "effective_date",
            "retired_date",
            "status",
            "version",
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
def get_all_odm_templates(
    request: Request,  # request is actually required by the allow_exports decorator
    library: Optional[str] = Query(None),
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
):
    odm_template_service = OdmTemplateService()
    results = odm_template_service.get_all_concepts(
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
    odm_template_service = OdmTemplateService()
    return odm_template_service.get_distinct_values_for_header(
        library=library_name,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/{uid}",
    summary="Get details on a specific ODM Template (in a specific version)",
    description="",
    response_model=OdmTemplate,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_odm_template(uid: str = OdmTemplateUID):
    odm_template_service = OdmTemplateService()
    return odm_template_service.get_by_uid(uid=uid)


@router.get(
    "/{uid}/relationships",
    summary="Get UIDs of a specific ODM Template's relationships",
    description="",
    response_model=dict,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_active_relationships(uid: str = OdmTemplateUID):
    odm_template_service = OdmTemplateService()
    return odm_template_service.get_active_relationships(uid=uid)


@router.get(
    "/{uid}/versions",
    summary="List version history for ODM Template",
    description="""
State before:
 - uid must exist.

Business logic:
 - List version history for ODM Templates.
 - The returned versions are ordered by start_date descending (newest entries first).

State after:
 - No change

Possible errors:
 - Invalid uid.
    """,
    response_model=List[OdmTemplate],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Template with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_odm_template_versions(uid: str = OdmTemplateUID):
    odm_template_service = OdmTemplateService()
    return odm_template_service.get_version_history(uid=uid)


@router.post(
    "",
    summary="Creates a new Template in 'Draft' status with version 0.1",
    description="",
    response_model=OdmTemplate,
    status_code=201,
    responses={
        201: {"description": "Created - The ODM Template was successfully created."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The library does not exist.\n"
            "- The library does not allow to add new items.\n",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def create_odm_template(
    odm_template_create_input: OdmTemplatePostInput = Body(description=""),
):
    odm_template_service = OdmTemplateService()
    return odm_template_service.create(concept_input=odm_template_create_input)


@router.patch(
    "/{uid}",
    summary="Update ODM Template",
    description="",
    response_model=OdmTemplate,
    status_code=200,
    responses={
        200: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Template is not in draft status.\n"
            "- The ODM Template had been in 'Final' status before.\n"
            "- The library does not allow to edit draft versions.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Template with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def edit_odm_template(
    uid: str = OdmTemplateUID,
    odm_template_edit_input: OdmTemplatePatchInput = Body(description=""),
):
    odm_template_service = OdmTemplateService()
    return odm_template_service.edit_draft(
        uid=uid, concept_edit_input=odm_template_edit_input
    )


@router.post(
    "/{uid}/versions",
    summary=" Create a new version of ODM Template",
    description="""
State before:
 - uid must exist and the ODM Template must be in status Final.

Business logic:
- The ODM Template is changed to a draft state.

State after:
 - ODM Template changed status to Draft and assigned a new minor version number.
 - Audit trail entry must be made with action of creating a new draft version.

Possible errors:
 - Invalid uid or status not Final.
""",
    response_model=OdmTemplate,
    status_code=201,
    responses={
        201: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The library does not allow to create ODM Templates.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Reasons include e.g.: \n"
            "- The ODM Template is not in final status.\n"
            "- The ODM Template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def create_odm_template_version(uid: str = OdmTemplateUID):
    odm_template_service = OdmTemplateService()
    return odm_template_service.create_new_version(uid=uid)


@router.post(
    "/{uid}/approvals",
    summary="Approve draft version of ODM Template",
    description="",
    response_model=OdmTemplate,
    status_code=201,
    responses={
        201: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Template is not in draft status.\n"
            "- The library does not allow to approve ODM Template.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Template with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def approve_odm_template(uid: str = OdmTemplateUID):
    odm_template_service = OdmTemplateService()
    return odm_template_service.approve(uid=uid)


@router.delete(
    "/{uid}/activations",
    summary=" Inactivate final version of ODM Template",
    description="",
    response_model=OdmTemplate,
    status_code=200,
    responses={
        200: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Template is not in final status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def inactivate_odm_template(uid: str = OdmTemplateUID):
    odm_template_service = OdmTemplateService()
    return odm_template_service.inactivate_final(uid=uid)


@router.post(
    "/{uid}/activations",
    summary="Reactivate retired version of a ODM Template",
    description="",
    response_model=OdmTemplate,
    status_code=200,
    responses={
        200: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Template is not in retired status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def reactivate_odm_template(uid: str = OdmTemplateUID):
    odm_template_service = OdmTemplateService()
    return odm_template_service.reactivate_retired(uid=uid)


@router.post(
    "/{uid}/forms",
    summary="Adds forms to the ODM Template.",
    description="",
    response_model=OdmTemplate,
    status_code=201,
    responses={
        201: {
            "description": "Created - The forms were successfully added to the ODM Template."
        },
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The forms with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def add_forms_to_odm_template(
    uid: str = OdmTemplateUID,
    override: bool = Query(
        False,
        description="If true, all existing form relationships will be replaced with the provided form relationships.",
    ),
    odm_template_form_post_input: List[OdmTemplateFormPostInput] = Body(description=""),
):
    odm_template_service = OdmTemplateService()
    return odm_template_service.add_forms(
        uid=uid,
        odm_template_form_post_input=odm_template_form_post_input,
        override=override,
    )


@router.delete(
    "/{uid}",
    summary="Delete draft version of ODM Template",
    description="",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The ODM Template was successfully deleted."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Template is not in draft status.\n"
            "- The ODM Template was already in final state or is in use.\n"
            "- The library does not allow to delete ODM Template.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - An ODM Template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def delete_odm_template(uid: str = OdmTemplateUID):
    odm_template_service = OdmTemplateService()
    odm_template_service.soft_delete(uid=uid)
