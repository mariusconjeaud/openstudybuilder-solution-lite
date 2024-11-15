# RESTful API endpoints used by consumers that want to extract data from StudyBuilder
# pylint: disable=invalid-name
# pylint: disable=redefined-builtin
from fastapi import APIRouter, Path, Query, Request

from consumer_api.auth import rbac
from consumer_api.shared import config
from consumer_api.shared.responses import ErrorResponse, PaginatedResponse
from consumer_api.v1 import db as DB
from consumer_api.v1 import models

router = APIRouter()


# GET endpoint to retrieve a list of studies
@router.get(
    "/studies",
    dependencies=[rbac.STUDY_READ],
    response_model=PaginatedResponse[models.Study],
    status_code=200,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid request",
        },
    },
)
async def get_studies(
    request: Request,
    sort_by: models.SortByStudies = models.SortByStudies.UID,
    sort_order: models.SortOrder = models.SortOrder.ASC,
    page_size: int = Query(
        config.DEFAULT_PAGE_SIZE,
        ge=1,
        le=config.MAX_PAGE_SIZE,
    ),
    page_number: int = Query(1, ge=1),
    id: str = Query(
        None, description="Filter by study ID (case-insensitive partial match)"
    ),
):
    """Get a paginated list of studies"""
    studies = DB.get_studies(
        sort_by=sort_by,
        sort_order=sort_order,
        page_size=page_size,
        page_number=page_number,
        id=id,
    )

    return PaginatedResponse.from_input(
        request=request,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        page_size=page_size,
        page_number=page_number,
        items=[models.Study.from_input(study) for study in studies],
        query_param_names=["id"],
    )


# GET endpoint to retrieve a study's visits
@router.get(
    "/studies/{uid}/study-visits",
    dependencies=[rbac.STUDY_READ],
    response_model=PaginatedResponse[models.StudyVisit],
    status_code=200,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid request",
        },
    },
)
async def get_study_visits(
    request: Request,
    uid: str = Path(description="Study UID"),
    sort_by: models.SortByStudyVisits = models.SortByStudyVisits.UID,
    sort_order: models.SortOrder = models.SortOrder.ASC,
    page_size: int = Query(
        config.PAGE_SIZE_100,
        ge=1,
        le=config.MAX_PAGE_SIZE,
    ),
    page_number: int = Query(1, ge=1),
    study_version_number: str | None = Query(None, description="Study Version Number"),
):
    """Get a paginated list of study visits"""
    study_visits = DB.get_study_visits(
        study_uid=uid,
        sort_by=sort_by,
        sort_order=sort_order,
        page_size=page_size,
        page_number=page_number,
        study_version_number=study_version_number,
    )

    return PaginatedResponse.from_input(
        request=request,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        page_size=page_size,
        page_number=page_number,
        items=[
            models.StudyVisit.from_input(study_visit) for study_visit in study_visits
        ],
        query_param_names=["study_version_number"],
    )


# GET endpoint to retrieve a study's operational soa
@router.get(
    "/studies/{uid}/operational-soa",
    dependencies=[rbac.STUDY_READ],
    response_model=PaginatedResponse[models.StudyOperationalSoA],
    status_code=200,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid request",
        },
    },
)
async def get_study_operational_soa(
    request: Request,
    uid: str = Path(description="Study UID"),
    sort_by: models.SortByStudyOperationalSoA = models.SortByStudyOperationalSoA.ACTIVITY,
    sort_order: models.SortOrder = models.SortOrder.ASC,
    page_size: int = Query(
        config.PAGE_SIZE_100,
        ge=1,
        le=config.MAX_PAGE_SIZE,
    ),
    page_number: int = Query(1, ge=1),
    study_version_number: str | None = Query(None, description="Study Version Number"),
):
    """Get a paginated list of operational SoA items representing a point in the activities/visits matrix"""
    study_operational_soa = DB.get_study_operational_soa(
        study_uid=uid,
        sort_by=sort_by,
        sort_order=sort_order,
        page_size=page_size,
        page_number=page_number,
        study_version_number=study_version_number,
    )

    return PaginatedResponse.from_input(
        request=request,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        page_size=page_size,
        page_number=page_number,
        items=[
            models.StudyOperationalSoA.from_input(study_visit)
            for study_visit in study_operational_soa
        ],
        query_param_names=["study_version_number"],
    )
