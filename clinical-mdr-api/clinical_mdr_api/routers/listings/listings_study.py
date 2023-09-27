from fastapi import APIRouter, Path

from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.models.listings.listings_study import StudyMetadataListingModel
from clinical_mdr_api.models.utils import PrettyJSONResponse
from clinical_mdr_api.oauth import rbac
from clinical_mdr_api.routers import _generic_descriptions
from clinical_mdr_api.services.listings.listings_study import (
    StudyMetadataListingService,
)

# Prefixed with "/listings"
router = APIRouter()


@router.get(
    "/studies/{study_number}/study-metadata",
    dependencies=[rbac.STUDY_READ],
    summary="Retrieve study metadata from a given study number",
    response_model=StudyMetadataListingModel,
    response_class=PrettyJSONResponse,
    status_code=200,
    responses={
        200: {
            "model": StudyMetadataListingModel,
        },
        500: _generic_descriptions.ERROR_500,
        404: {
            "model": ErrorResponse,
            "description": "Not Found - No study with the specified 'study_number'.",
        },
    },
)
def get_study_metadata(
    study_number: str = Path(
        None, description="Return study title for specific study number"
    )
):
    study_metadata_listing_service = StudyMetadataListingService()
    return study_metadata_listing_service.get_study_metadata(study_number)
