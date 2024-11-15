from fastapi import APIRouter, Body, Path, Query, Request
from pydantic.types import Json

from clinical_mdr_api import config, models
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.oauth import rbac
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.routers import _generic_descriptions, decorators
from clinical_mdr_api.services.clinical_programmes.clinical_programme import (
    ClinicalProgrammeService,
)

# Prefixed with "/clinical-programmes"
router = APIRouter()
ClinicalProgrammeUID = Path(description="The unique id of the clinical programme.")


@router.get(
    "",
    dependencies=[rbac.LIBRARY_READ],
    summary="Returns all clinical programmes.",
    response_model=GenericFilteringReturn[models.ClinicalProgramme],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.allow_exports(
    {
        "defaults": ["uid", "name"],
        "formats": [
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/xml",
            "application/json",
        ],
    }
)
# pylint: disable=unused-argument
def get_programmes(
    request: Request,  # request is actually required by the allow_exports decorator
    sort_by: Json = Query(None, description=_generic_descriptions.SORT_BY),
    page_number: int
    | None = Query(1, ge=1, description=_generic_descriptions.PAGE_NUMBER),
    page_size: int
    | None = Query(
        config.DEFAULT_PAGE_SIZE,
        ge=0,
        le=config.MAX_PAGE_SIZE,
        description=_generic_descriptions.PAGE_SIZE,
    ),
    filters: Json
    | None = Query(
        None,
        description=_generic_descriptions.FILTERS,
        example=_generic_descriptions.FILTERS_EXAMPLE,
    ),
    operator: str | None = Query("and", description=_generic_descriptions.OPERATOR),
    total_count: bool
    | None = Query(False, description=_generic_descriptions.TOTAL_COUNT),
) -> GenericFilteringReturn[models.ClinicalProgramme]:
    service = ClinicalProgrammeService()
    return service.get_all_clinical_programmes(
        sort_by=sort_by,
        page_number=page_number,
        page_size=page_size,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        total_count=total_count,
    )


@router.get(
    "/{clinical_programme_uid}",
    dependencies=[rbac.LIBRARY_READ],
    summary="Get a clinical programme.",
    response_model=models.ClinicalProgramme,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get(clinical_programme_uid: str = ClinicalProgrammeUID) -> models.ClinicalProgramme:
    service = ClinicalProgrammeService()
    return service.get_clinical_programme_by_uid(clinical_programme_uid)


@router.post(
    "",
    dependencies=[rbac.LIBRARY_WRITE],
    summary="Creates a new clinical programme.",
    response_model=models.ClinicalProgramme,
    status_code=201,
    responses={
        201: {
            "description": "Created - The clinical programme was successfully created."
        },
        500: _generic_descriptions.ERROR_500,
    },
)
# pylint: disable=unused-argument
def create(
    clinical_programme_create_input: models.ClinicalProgrammeInput = Body(
        description="Related parameters of the clinical programme that shall be created.",
    ),
) -> models.ClinicalProgramme:
    service = ClinicalProgrammeService()
    return service.create(clinical_programme_create_input)


@router.patch(
    "/{clinical_programme_uid}",
    dependencies=[rbac.LIBRARY_WRITE],
    summary="Edit a clinical programme.",
    response_model=models.ClinicalProgramme,
    status_code=200,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Some application/business rules forbid to process the request. Expect more detailed"
            " information in response body.",
        },
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def edit(
    clinical_programme_uid: str = ClinicalProgrammeUID,
    clinical_programme_edit_input: models.ClinicalProgrammeInput = Body(description=""),
) -> models.ClinicalProgramme:
    service = ClinicalProgrammeService()
    return service.edit(clinical_programme_uid, clinical_programme_edit_input)


@router.delete(
    "/{clinical_programme_uid}",
    dependencies=[rbac.LIBRARY_WRITE],
    summary="Delete a clinical programme.",
    status_code=204,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Some application/business rules forbid to process the request. Expect more detailed"
            " information in response body.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def delete(clinical_programme_uid: str = ClinicalProgrammeUID):
    service = ClinicalProgrammeService()
    return service.delete(clinical_programme_uid)
