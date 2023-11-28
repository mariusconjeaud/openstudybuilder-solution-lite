from fastapi import APIRouter, Body, Depends

from clinical_mdr_api import models
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.oauth import get_current_user_id, rbac
from clinical_mdr_api.routers import _generic_descriptions
from clinical_mdr_api.services.projects.project import ProjectService

# Prefixed with "/projects"
router = APIRouter()


# Argument definitions
# ProjectUID = Path(
#     None, description="The unique id of the project.")


@router.get(
    "",
    dependencies=[rbac.LIBRARY_READ],
    summary="Returns all projects.",
    response_model=list[models.Project],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_projects() -> list[models.Project]:
    service = ProjectService()
    return service.get_all_projects()


@router.post(
    "",
    dependencies=[rbac.LIBRARY_WRITE],
    summary="Creates a new project.",
    response_model=models.Project,
    status_code=201,
    responses={
        201: {"description": "Created - The project was successfully created."},
        400: {
            "model": ErrorResponse,
            "description": "Some application/business rules forbid to process the request. Expect more detailed"
            " information in response body.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def create(
    project_create_input: models.ProjectCreateInput = Body(
        description="Related parameters of the project that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.Project:
    service = ProjectService(user=current_user_id)
    return service.create(project_create_input)
