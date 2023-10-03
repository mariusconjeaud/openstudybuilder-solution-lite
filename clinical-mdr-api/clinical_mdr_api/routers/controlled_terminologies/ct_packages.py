"""CTPackage router."""
from datetime import date

from fastapi import APIRouter, Depends, Path, Query

from clinical_mdr_api import models
from clinical_mdr_api.oauth import get_current_user_id, rbac
from clinical_mdr_api.routers import _generic_descriptions
from clinical_mdr_api.services.controlled_terminologies.ct_package import (
    CTPackageService,
)

# Prefixed with "/ct"
router = APIRouter()

CTCodelistUid = Path(None, description="The unique id of the CTCodelist")


@router.get(
    "/packages",
    dependencies=[rbac.LIBRARY_READ],
    summary="Returns all controlled terminology packages.",
    response_model=list[models.CTPackage],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_packages(
    catalogue_name: str
    | None = Query(
        None,
        description="If specified, only packages from given catalogue are returned.",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    ct_package_service = CTPackageService(current_user_id)
    return ct_package_service.get_all_ct_packages(catalogue_name=catalogue_name)


@router.get(
    "/packages/changes",
    dependencies=[rbac.LIBRARY_READ],
    summary="Returns changes between codelists and terms inside two different packages.",
    response_model=models.CTPackageChanges,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_packages_changes_between_codelists_and_terms(
    catalogue_name: str,
    old_package_date: date = Query(
        ...,
        description="The date for the old package, for instance '2020-03-27'"
        "\n_the possible dates for given catalogue_name can be retrieved by the /ct/packages/dates endpoint",
    ),
    new_package_date: date = Query(
        ...,
        description="The datetime for the new package, for instance '2020-06-26'"
        "\n_the possible dates for given catalogue_name can be retrieved by the /ct/packages/dates endpoint",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    ct_package_service = CTPackageService(current_user_id)
    return ct_package_service.get_ct_packages_changes(
        catalogue_name=catalogue_name,
        old_package_date=old_package_date,
        new_package_date=new_package_date,
    )


@router.get(
    "/packages/{codelist_uid}/changes",
    dependencies=[rbac.LIBRARY_READ],
    summary="Returns changes from given codelist and all associated terms inside two different packages.",
    response_model=models.CTPackageChangesSpecificCodelist,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_packages_changes_between_codelist_and_all_associated_terms(
    catalogue_name: str,
    codelist_uid: str = CTCodelistUid,
    old_package_date: date = Query(
        ...,
        description="The date for the old package, for instance '2020-03-27'"
        "\n_the possible dates for given catalogue_name can be retrieved by the /ct/packages/dates endpoint",
    ),
    new_package_date: date = Query(
        ...,
        description="The date for the new package, for instance '2020-06-26'"
        "\n_the possible dates for given catalogue_name can be retrieved by the /ct/packages/dates endpoint",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    ct_package_service = CTPackageService(current_user_id)
    return ct_package_service.get_ct_packages_codelist_changes(
        catalogue_name=catalogue_name,
        old_package_date=old_package_date,
        new_package_date=new_package_date,
        codelist_uid=codelist_uid,
    )


@router.get(
    "/packages/dates",
    dependencies=[rbac.LIBRARY_READ],
    summary="Returns all effective dates for packages in a given catalogue.",
    response_model=models.CTPackageDates,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_package_dates(
    catalogue_name: str, current_user_id: str = Depends(get_current_user_id)
):
    ct_package_service = CTPackageService(current_user_id)
    return ct_package_service.get_all_effective_dates(catalogue_name=catalogue_name)
