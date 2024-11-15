# pylint: disable=invalid-name
from fastapi import APIRouter, Body, Path

from clinical_mdr_api.models.feature_flag import FeatureFlag, FeatureFlagInput
from clinical_mdr_api.oauth import rbac
from clinical_mdr_api.routers import _generic_descriptions, decorators
from clinical_mdr_api.services.feature_flags import FeatureFlagService

# Prefixed with "/feature-flags"
router = APIRouter()

SN = Path(title="Serial Number of the feature flag")

service = FeatureFlagService()


@router.get(
    "/{serial_number}",
    dependencies=[rbac.ADMIN_READ],
    summary="Returns the feature flag identified by the provided Serial Number.",
    response_model=FeatureFlag,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.validate_serial_number_against_neo4j_max_and_min_int()
def get_feature_flag(serial_number: int = SN) -> FeatureFlag:
    return service.get_feature_flag(serial_number)


@router.post(
    "",
    dependencies=[rbac.ADMIN_WRITE],
    summary="Creates a feature flag.",
    response_model=FeatureFlag,
    status_code=201,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def create_feature_flag(
    feature_flag_input: FeatureFlagInput = Body(),
) -> FeatureFlag:
    return service.create_feature_flag(feature_flag_input)


@router.patch(
    "/{serial_number}",
    dependencies=[rbac.ADMIN_WRITE],
    summary="Updates the feature flag identified by the provided Serial Number.",
    response_model=FeatureFlag,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.validate_serial_number_against_neo4j_max_and_min_int()
def update_feature_flag(
    serial_number: int = SN,
    feature_flag_input: FeatureFlagInput = Body(),
) -> FeatureFlag:
    return service.update_feature_flag(serial_number, feature_flag_input)


@router.delete(
    "/{serial_number}",
    dependencies=[rbac.ADMIN_WRITE],
    summary="Deletes the feature flag identified by the provided Serial Number.",
    status_code=204,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.validate_serial_number_against_neo4j_max_and_min_int()
def delete_feature_flag(serial_number: int = SN) -> None:
    return service.delete_feature_flag(serial_number)
