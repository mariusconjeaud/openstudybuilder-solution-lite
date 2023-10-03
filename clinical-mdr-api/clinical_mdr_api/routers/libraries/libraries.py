"""Objective templates router."""


from fastapi import APIRouter, Body, Depends, Query

from clinical_mdr_api import models
from clinical_mdr_api.oauth import get_current_user_id, rbac
from clinical_mdr_api.services.libraries import libraries as service

# Prefixed with "/libraries"
router = APIRouter()


@router.get(
    "",
    dependencies=[rbac.LIBRARY_READ],
    summary="Returns all libraries",
    response_model=list[models.Library],
)
# pylint: disable=unused-argument
def get_libraries(
    is_editable: bool
    | None = Query(
        None,
        description="If specified, only those libraries are returned that are editable. \n"
        "Valid values are: 'true' or 'false'.",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    return service.get_libraries(is_editable)


@router.post(
    "",
    dependencies=[rbac.LIBRARY_WRITE],
    summary="Creates a new library.",
    response_model=models.Library,
    status_code=201,
    responses={
        201: {"description": "Created - The library was successfully created."},
    },
)
# pylint: disable=unused-argument
def create_library(
    library: models.Library = Body(description=""),
    current_user_id: str = Depends(get_current_user_id),
):
    return service.create(library.name, library.is_editable)
