import os
from typing import Any, List, Optional, Sequence, Union

from fastapi import APIRouter, Body, Depends, Path, Query, Request, Response, status
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic.types import Json

from clinical_mdr_api import config, models
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.models.utils import CustomPage, GenericFilteringReturn
from clinical_mdr_api.oauth import get_current_user_id
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.routers import _generic_descriptions, decorators
from clinical_mdr_api.services.study_activity_selection import (
    StudyActivitySelectionService,
)
from clinical_mdr_api.services.study_arm_selection import StudyArmSelectionService
from clinical_mdr_api.services.study_branch_arm_selection import (
    StudyBranchArmSelectionService,
)
from clinical_mdr_api.services.study_cohort_selection import StudyCohortSelectionService
from clinical_mdr_api.services.study_compound_selection import (
    StudyCompoundSelectionService,
)
from clinical_mdr_api.services.study_criteria_selection import (
    StudyCriteriaSelectionService,
)
from clinical_mdr_api.services.study_element_selection import (
    StudyElementSelectionService,
)
from clinical_mdr_api.services.study_endpoint_selection import (
    StudyEndpointSelectionService,
)
from clinical_mdr_api.services.study_objective_selection import (
    StudyObjectiveSelectionService,
)
from clinical_mdr_api.services.study_objectives import StudyObjectivesService

router = APIRouter()

studyUID = Path(None, description="The unique id of the study.")

study_selection_uid = Path(None, description="The unique id of the study selection.")

"""
    API endpoints to study objectives
"""


@router.get(
    "/study-objectives",
    summary="Returns all study objectives currently selected",
    response_model=CustomPage[models.StudySelectionObjective],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_selected_objectives_for_all_studies(
    no_brackets: bool = Query(
        False,
        description="Indicates whether brackets around Template Parameters in the Objective"
        "should be returned",
    ),
    project_name: Optional[str] = Query(
        None,
        description="Optionally, the name of the project for which to return study selections.",
    ),
    project_number: Optional[str] = Query(
        None,
        description="Optionally, the number of the project for which to return study selections.",
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
) -> Sequence[models.StudySelectionObjective]:
    service = StudyObjectiveSelectionService(author=current_user_id)
    all_selections = service.get_all_selections_for_all_studies(
        no_brackets=no_brackets,
        project_name=project_name,
        project_number=project_number,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
    )
    return CustomPage.create(
        items=all_selections.items,
        total=all_selections.total_count,
        page=page_number,
        size=page_size,
    )


@router.get(
    "/study-objectives/headers",
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
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_distinct_objective_values_for_header(
    project_name: Optional[str] = Query(
        None,
        description="Optionally, the name of the project for which to return study selections.",
    ),
    project_number: Optional[str] = Query(
        None,
        description="Optionally, the number of the project for which to return study selections.",
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
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyObjectiveSelectionService(author=current_user_id)
    return service.get_distinct_values_for_header(
        project_name=project_name,
        project_number=project_number,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/studies/{uid}/study-objectives",
    summary="Returns all study objectives currently selected for study with provided uid",
    response_model=GenericFilteringReturn[models.StudySelectionObjective],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "uid",
            "order",
            "objective_level=objective_level.sponsor_preferred_name",
            "name=objective.name_plain",
            "endpoint_count",
            "start_date",
            "user_initials",
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
def get_all_selected_objectives(
    request: Request,  # request is actually required by the allow_exports decorator
    uid: str = studyUID,
    no_brackets: bool = Query(
        False,
        description="Indicates whether brackets around Template Parameters in the Objective"
        "should be returned",
    ),
    current_user_id: str = Depends(get_current_user_id),
    filters: Optional[Json] = Query(
        None,
        description=_generic_descriptions.FILTERS,
        example=_generic_descriptions.FILTERS_EXAMPLE,
    ),
    page_number: Optional[int] = Query(
        1, ge=1, description=_generic_descriptions.PAGE_NUMBER
    ),
    page_size: Optional[int] = Query(
        config.DEFAULT_PAGE_SIZE, ge=0, description=_generic_descriptions.PAGE_SIZE
    ),
    operator: Optional[str] = Query("and", description=_generic_descriptions.OPERATOR),
    total_count: Optional[bool] = Query(
        False, description=_generic_descriptions.TOTAL_COUNT
    ),
):
    service = StudyObjectiveSelectionService(author=current_user_id)
    return service.get_all_selection(
        study_uid=uid,
        no_brackets=no_brackets,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
    )


@router.get(
    "/studies/{uid}/study-objectives/headers",
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
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_distinct_values_for_header(
    uid: str = studyUID,
    project_name: Optional[str] = Query(
        None,
        description="Optionally, the name of the project for which to return study selections.",
    ),
    project_number: Optional[str] = Query(
        None,
        description="Optionally, the number of the project for which to return study selections.",
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
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyObjectiveSelectionService(author=current_user_id)
    return service.get_distinct_values_for_header(
        study_uid=uid,
        project_name=project_name,
        project_number=project_number,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/studies/{uid}/study-objectives/audit-trail",
    summary="List full audit trail related to definition of all study objectives.",
    description="""
The following values should be return for all study objectives.
- date_time
- user_initials
- action
- objective_template
- objective
- objective_level
- order
    """,
    response_model=Sequence[models.StudySelectionObjectiveCore],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_objectives_audit_trail(
    uid: str = studyUID, current_user_id: str = Depends(get_current_user_id)
) -> Sequence[models.StudySelectionObjectiveCore]:
    service = StudyObjectiveSelectionService(author=current_user_id)
    return service.get_all_selection_audit_trail(study_uid=uid)


@router.get(
    "/studies/{uid}/study-objectives/{study_objective_uid}",
    summary="Returns specific study objective",
    response_model=models.StudySelectionObjective,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the objective for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_objective(
    uid: str = studyUID,
    study_objective_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionObjective:
    service = StudyObjectiveSelectionService(author=current_user_id)
    return service.get_specific_selection(
        study_uid=uid, study_selection_uid=study_objective_uid
    )


@router.get(
    "/studies/{uid}/study-objectives/{study_objective_uid}/audit-trail",
    summary="List audit trail related to definition of a specific study objective.",
    description="""
The following values should be return for selected study objective:
- date_time
- user_initials
- action
- objective_template
- objective
- objective_level
- order
    """,
    response_model=Sequence[models.StudySelectionObjectiveCore],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the objective for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_objective_audit_trail(
    uid: str = studyUID,
    study_objective_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionObjectiveCore:
    service = StudyObjectiveSelectionService(author=current_user_id)
    return service.get_specific_selection_audit_trail(
        study_uid=uid, study_selection_uid=study_objective_uid
    )


@router.post(
    "/studies/{uid}/study-objectives",
    summary="Creating a study objective selection based on the input data, including optionally creating a library objective",
    response_model=models.StudySelectionObjective,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - There already exists a selection of the objective",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or objective is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def post_new_objective_selection_create(
    uid: str = studyUID,
    selection: Union[
        models.study_selection.StudySelectionObjectiveCreateInput,
        models.study_selection.StudySelectionObjectiveInput,
    ] = Body(None, description="Parameters of the selection that shall be created."),
    create_objective: bool = Query(
        False,
        description="Indicates whether the specified objective should be created in the library.\n"
        "- If this parameter is set to `true`, a `StudySelectionObjectiveCreateInput` payload needs to be sent.\n"
        "- Otherwise, `StudySelectionObjectiveInput` payload should be sent, referencing an existing library objective by uid.",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionObjective:
    service = StudyObjectiveSelectionService(author=current_user_id)

    if create_objective:
        return service.make_selection_create_objective(
            study_uid=uid, selection_create_input=selection
        )
    return service.make_selection(study_uid=uid, selection_create_input=selection)


@router.post(
    "/studies/{uid}/study-objectives/preview",
    summary="Preview creating a study objective selection based on the input data",
    response_model=models.StudySelectionObjective,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - There already exists a selection of the objective",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or objective is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def preview_new_objective_selection_create(
    uid: str = studyUID,
    selection: models.study_selection.StudySelectionObjectiveCreateInput = Body(
        None, description="Related parameters of the selection that shall be previewed."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionObjective:
    service = StudyObjectiveSelectionService(author=current_user_id)
    return service.make_selection_preview_objective(
        study_uid=uid, selection_create_input=selection
    )


@router.delete(
    "/studies/{uid}/study-objectives/{study_objective_uid}",
    summary="Deletes a study objective",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The selection was successfully deleted."},
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the objective and the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def delete_selected_objective(
    uid: str = studyUID,
    study_objective_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyObjectiveSelectionService(author=current_user_id)
    service.delete_selection(study_uid=uid, study_selection_uid=study_objective_uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/studies/{uid}/study-objectives/{study_objective_uid}/order",
    summary="Change a order of a study objective",
    response_model=models.StudySelectionObjective,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and objective to reorder.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_new_objective_selection_order(
    uid: str = studyUID,
    study_objective_uid: str = study_selection_uid,
    new_order_input: models.StudySelectionObjectiveNewOrder = Body(
        None, description="Related parameters of the selection that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionObjective:
    service = StudyObjectiveSelectionService(author=current_user_id)
    return service.set_new_order(
        study_uid=uid,
        study_selection_uid=study_objective_uid,
        new_order=new_order_input.new_order,
    )


@router.patch(
    "/studies/{uid}/study-objectives/{study_objective_uid}",
    summary="update the objective level of a study objective",
    response_model=models.StudySelectionObjective,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and objective.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_update_objective_selection(
    uid: str = studyUID,
    study_objective_uid: str = study_selection_uid,
    selection: models.StudySelectionObjectiveInput = Body(
        None, description="Related parameters of the selection that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionObjective:
    service = StudyObjectiveSelectionService(author=current_user_id)
    return service.patch_selection(
        study_uid=uid,
        study_selection_uid=study_objective_uid,
        selection_update_input=selection,
    )


@router.post(
    "/studies/{uid}/study-objectives/{study_objective_uid}/sync-latest-version",
    summary="update to latest objective version study selection",
    response_model=models.StudySelectionObjective,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and objective.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def sync_latest_version(
    uid: str = studyUID,
    study_objective_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionObjective:
    service = StudyObjectiveSelectionService(author=current_user_id)
    return service.update_selection_to_latest_version(
        study_uid=uid, study_selection_uid=study_objective_uid
    )


"""
    API endpoints to study endpoints
"""


@router.get(
    "/study-endpoints",
    summary="Returns all study endpoints currently selected",
    response_model=CustomPage[models.StudySelectionEndpoint],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_selected_endpoints_for_all_studies(
    no_brackets: bool = Query(
        False,
        description="Indicates whether brackets around Template Parameters in the Endpoint"
        "should be returned",
    ),
    project_name: Optional[str] = Query(
        None,
        description="Optionally, the name of the project for which to return study selections.",
    ),
    project_number: Optional[str] = Query(
        None,
        description="Optionally, the number of the project for which to return study selections.",
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
) -> Sequence[models.StudySelectionEndpoint]:
    service = StudyEndpointSelectionService(author=current_user_id)
    all_selections = service.get_all_selections_for_all_studies(
        no_brackets=no_brackets,
        project_name=project_name,
        project_number=project_number,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
    )
    return CustomPage.create(
        items=all_selections.items,
        total=all_selections.total_count,
        page=page_number,
        size=page_size,
    )


@router.get(
    "/study-endpoints/headers",
    summary="Returns possible values from the database for a given header",
    description="""Allowed parameters include : field name for which to get possible
    values, search string to provide filtering for the field name, additional filters to apply on other fields""",
    response_model=Sequence[Any],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Invalid field name specified",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_distinct_endpoint_values_for_header(
    project_name: Optional[str] = Query(
        None,
        description="Optionally, the name of the project for which to return study selections.",
    ),
    project_number: Optional[str] = Query(
        None,
        description="Optionally, the number of the project for which to return study selections.",
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
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyEndpointSelectionService(author=current_user_id)
    return service.get_distinct_values_for_header(
        project_name=project_name,
        project_number=project_number,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/studies/{uid}/study-endpoints",
    summary="""List all study endpoints currently selected for study with provided uid""",
    description="""
State before:
- Study must exist.

Business logic:
 - By default (no study status is provided) list all study endpoints for the study uid in status draft. If the study not exist in status draft then return the study endpoints for the study in status released. If the study uid only exist as deleted then this is returned.
- If a specific study status parameter is provided then return study endpoints for this study status.
- If the locked study status parameter is requested then a study version should also be provided, and then the study endpoints for the specific locked study version is returned.
- Indicate by an boolean variable if the study endpoint can be updated (if the selected study is in status draft).
- Indicate by an boolean variable if all expected selections have been made for each study endpoint, or some are missing.
   - e.g. endpoint level, minimum one timeframe and one unit is expected.
 - Indicate by an boolean variable if the selected endpoint is available in a newer version.
 - Indicate by an boolean variable if a study endpoint can be re-ordered.

State after:
- no change.
""",
    response_model=GenericFilteringReturn[models.StudySelectionEndpoint],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "uid",
            "order",
            "name=endpoint.name_plain",
            "units=endpoint_units.units",
            "timeframe=timeframe.name",
            "objective=study_objective",
            "start_date",
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
def get_all_selected_endpoints(
    request: Request,  # request is actually required by the allow_exports decorator
    uid: str = studyUID,
    no_brackets: bool = Query(
        False,
        description="Indicates whether brackets around Template Parameters in the Objective"
        "and Endpoint should be returned",
    ),
    current_user_id: str = Depends(get_current_user_id),
    filters: Optional[Json] = Query(
        None,
        description=_generic_descriptions.FILTERS,
        example=_generic_descriptions.FILTERS_EXAMPLE,
    ),
    page_number: Optional[int] = Query(
        1, ge=1, description=_generic_descriptions.PAGE_NUMBER
    ),
    page_size: Optional[int] = Query(
        config.DEFAULT_PAGE_SIZE, ge=0, description=_generic_descriptions.PAGE_SIZE
    ),
    operator: Optional[str] = Query("and", description=_generic_descriptions.OPERATOR),
    total_count: Optional[bool] = Query(
        False, description=_generic_descriptions.TOTAL_COUNT
    ),
):
    service = StudyEndpointSelectionService(author=current_user_id)
    return service.get_all_selection(
        study_uid=uid,
        no_brackets=no_brackets,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
    )


@router.get(
    "/studies/{uid}/study-endpoints/headers",
    summary="Returns possible values from the database for a given header",
    description="""Allowed parameters include : field name for which to get possible
    values, search string to provide filtering for the field name, additional filters to apply on other fields""",
    response_model=Sequence[Any],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Invalid field name specified",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_distinct_study_endpoint_values_for_header(
    uid: str = studyUID,
    project_name: Optional[str] = Query(
        None,
        description="Optionally, the name of the project for which to return study selections.",
    ),
    project_number: Optional[str] = Query(
        None,
        description="Optionally, the number of the project for which to return study selections.",
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
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyEndpointSelectionService(author=current_user_id)
    return service.get_distinct_values_for_header(
        study_uid=uid,
        project_name=project_name,
        project_number=project_number,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/studies/{uid}/study-endpoints/audit-trail",
    summary="List full audit trail related to definition of all study endpoints.",
    description="""
Parameters:
 - uid as study-uid (required)
 - [NOT YET IMPLEMENTED] study status (optional)
 - [NOT YET IMPLEMENTED] study version (required when study status is locked)

State before:
 - Study must exist.

Business logic:
 - List all entries in the audit trail related to study endpoints for specified study-uid.
 - If the released or a locked version of the study is selected then only entries up to the time of the study release or lock is included.

State after:
 - no change.
 
Possible errors:
 - Invalid study-uid.

Returned data:
 - List of actions and changes related to study endpoints.
    """,
    response_model=Sequence[models.StudySelectionEndpoint],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_endpoints_audit_trail(
    uid: str = studyUID, current_user_id: str = Depends(get_current_user_id)
) -> Sequence[models.StudySelectionEndpoint]:
    service = StudyEndpointSelectionService(author=current_user_id)
    return service.get_all_selection_audit_trail(study_uid=uid)


@router.get(
    "/studies/{uid}/study-endpoints/{study_endpoint_uid}",
    summary="Returns specific study endpoint",
    description="""
State before:
 - Study and study endpoint must exist

Business logic:
 - By default (no study status is provided) list all details for specified study endpoint for the study uid in status draft. If the study not exist in status draft then return the study endpoints for the study in status released. If the study uid only exist as deleted then this is returned.
 - If a specific study status parameter is provided then return study endpoints for this study status.
 - If the locked study status parameter is requested then a study version should also be provided, and then the specified study endpoint for the specific locked study version is returned.
 - Indicate by an boolean variable if the study endpoint can be updated (if the selected study is in status draft).
 - Indicate by an boolean variable if all expected selections have been made for each study endpoint, or some are missing.
 - e.g. endpoint level, minimum one timeframe and one unit is expected.
 - Indicate by an boolean variable if the selected endpoint is available in a newer version.
 - Indicate by an boolean variable if a study endpoint can be re-ordered.

State after:
 - no change
""",
    response_model=models.StudySelectionEndpoint,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - When there exist no study endpoint with the study endpoint uid.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_endpoint(
    uid: str = studyUID,
    study_endpoint_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionEndpoint:
    service = StudyEndpointSelectionService(author=current_user_id)
    return service.get_specific_selection(
        study_uid=uid, study_selection_uid=study_endpoint_uid
    )


@router.get(
    "/studies/{uid}/study-endpoints/{study_endpoint_uid}/audit-trail",
    summary="List audit trail related to definition of a specific study coendpointsmpound.",
    description="""
Parameters:
 - uid as study-uid (required)
 - study-compound-uid (required)
 - [NOT YET IMPLEMENTED] study status (optional)
 - [NOT YET IMPLEMENTED] study version (required when study status is locked)

State before:
 - Study and study compounds must exist.

Business logic:
 - List a specific entry in the audit trail related to the specified study endpoints for the specified study-uid.
 - If the released or a locked version of the study is selected then only entries up to the time of the study release or lock is included.

State after:
 - no change.
 
Possible errors:
 - Invalid study-uid.

Returned data:
 - List of actions and changes related to the specified study endpoints.
    """,
    response_model=Sequence[models.StudySelectionEndpoint],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the objective for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_endpoint_audit_trail(
    uid: str = studyUID,
    study_endpoint_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionEndpoint:
    service = StudyEndpointSelectionService(author=current_user_id)
    return service.get_specific_selection_audit_trail(
        study_uid=uid, study_selection_uid=study_endpoint_uid
    )


@router.post(
    "/studies/{uid}/study-endpoints",
    summary="Creates a study endpoint selection based on the input data, including optionally creating library endpoint",
    response_model=models.StudySelectionEndpoint,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - There already exists a selection of the endpoint",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or endpoint is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def post_new_endpoint_selection_create(
    uid: str = studyUID,
    selection: Union[
        models.study_selection.StudySelectionEndpointCreateInput,
        models.study_selection.StudySelectionEndpointInput,
    ] = Body(None, description="Parameters of the selection that shall be created."),
    create_endpoint: bool = Query(
        False,
        description="Indicates whether the specified endpoint should be created in the library.\n"
        "- If this parameter is set to `true`, a `StudySelectionEndpointCreateInput` payload needs to be sent.\n"
        "- Otherwise, `StudySelectionEndpointInput` payload should be sent, referencing an existing library endpoint by uid.",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionEndpoint:
    service = StudyEndpointSelectionService(author=current_user_id)
    if create_endpoint:
        return service.make_selection_create_endpoint(
            study_uid=uid, selection_create_input=selection
        )
    return service.make_selection(study_uid=uid, selection_create_input=selection)


@router.post(
    "/studies/{uid}/study-endpoints/preview",
    summary="Preview creating a study endpoint selection based on the input data",
    response_model=models.StudySelectionEndpoint,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - There already exists a selection of the endpoint",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or endpoint is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def post_new_endpoint_selection_preview(
    uid: str = studyUID,
    selection: models.study_selection.StudySelectionEndpointCreateInput = Body(
        None, description="Related parameters of the selection that shall be previewed."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionEndpoint:
    service = StudyEndpointSelectionService(author=current_user_id)
    return service.make_selection_preview_endpoint(
        study_uid=uid, selection_create_input=selection
    )


@router.delete(
    "/studies/{uid}/study-endpoints/{study_endpoint_uid}",
    summary="Deletes a objective selection",
    description="""
State before:
 - Study must exist and study status must be in draft.
 - study-endpoint-uid must exist.

Business logic:
 - Remove specified study-endpoint from the study.
 - Reference to the study-endpoint should still exist in the the audit trail.
 - If a subsequent study endpoint exist in the list of study endpoints then the order number for following study endpoint must be decreased with 1.

State after:
- Study endpoint is deleted from the study, but still exist as a node in the database with a reference from the audit trail.
- Added new entry in the audit trail for the deletion of the study-endpoint.
""",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The selection was successfully deleted."},
        404: {
            "model": ErrorResponse,
            "description": "Not Found - When there exist no study endpoint with the study endpoint uid.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def delete_selected_endpoint(
    uid: str = studyUID,
    study_endpoint_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyEndpointSelectionService(author=current_user_id)
    service.delete_selection(study_uid=uid, study_selection_uid=study_endpoint_uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/studies/{uid}/study-endpoints/{study_endpoint_uid}/order",
    summary="Change a order of a selection",
    description="""
State before:
 - Study must exist and study status must be in draft.
 - study_endpoint_uid must exist.

Business logic:
 - moves the study selection to the order which is send in the new_order property

State after:
 - Order number for specified study-endpoint is updated to new order number.
 - Note this will change order on either the preceding or following study-endpoints as well.
 - Added new entry in the audit trail for the re-ordering of the study-endpoints.
""",
    response_model=models.StudySelectionEndpoint,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Order is larger than the number of selections",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - When there exist no study endpoint with the study endpoint uid.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_new_endpoint_selection_order(
    uid: str = studyUID,
    study_endpoint_uid: str = study_selection_uid,
    new_order_input: models.StudySelectionEndpointNewOrder = Body(
        None, description="Related parameters of the selection that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionEndpoint:
    service = StudyEndpointSelectionService(author=current_user_id)
    return service.set_new_order(
        study_uid=uid,
        study_selection_uid=study_endpoint_uid,
        new_order=new_order_input.new_order,
    )


@router.patch(
    "/studies/{uid}/study-endpoints/{study_endpoint_uid}",
    summary="update the study endpoint",
    description="""
State before:
 - Study must exist and study status must be in draft.
 - Selected endpoint-uid, endpoint-template-uid, endpoint-level, timeframe-uid and unit-definition-uid must exist.

Business logic:
 - Same logic applies as for selecting or creating an study endpoint (see two POST statements for /study-endpoints)

State after:
- Endpoint is added as study endpoint to the study.
 - This PATCH method can cover cover two parts:
    - Change the endpoint level for the currently selected study endpoint
    - Replace the currently selected study endpoint based on the same functionality as POST `/studies/{uid}/study-endpoints`
 - Added new entry in the audit trail for the update of the study-endpoint.
""",
    response_model=models.StudySelectionEndpoint,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - When there exist no study endpoint with the study endpoint uid.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_update_endpoint_selection(
    uid: str = studyUID,
    study_endpoint_uid: str = study_selection_uid,
    selection: models.StudySelectionEndpointInput = Body(
        None, description="Related parameters of the selection that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionEndpoint:
    service = StudyEndpointSelectionService(author=current_user_id)
    return service.patch_selection(
        study_uid=uid,
        study_selection_uid=study_endpoint_uid,
        selection_update_input=selection,
    )


@router.get(
    "/studies/{uid}/study-objectives.docx",
    summary="""Returns Study Objectives and Endpoints table in standard layout DOCX document""",
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_selected_objectives_and_endpoints_standard_docx(
    uid: str = studyUID, current_user_id: str = Depends(get_current_user_id)
) -> StreamingResponse:
    docx = StudyObjectivesService(user_id=current_user_id).get_standard_docx(
        study_uid=uid
    )
    stream = docx.get_document_stream()
    size = stream.seek(0, os.SEEK_END)
    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{uid} study-objectives.docx"',
            "Content-Length": f"{size:d}",
        },
    )


@router.get(
    "/studies/{uid}/study-objectives.html",
    summary="""Returns Study Objectives and Endpoints table in standard layout HTML document""",
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    response_class=HTMLResponse,
)
def get_all_selected_objectives_and_endpoints_standard_html(
    uid: str = studyUID, current_user_id: str = Depends(get_current_user_id)
) -> str:
    return StudyObjectivesService(user_id=current_user_id).get_standard_html(
        study_uid=uid
    )


"""
    API endpoints to study compounds
"""


@router.get(
    "/study-compounds",
    summary="Returns all study compounds currently selected",
    response_model=CustomPage[models.StudySelectionCompound],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_selected_compounds_for_all_studies(
    project_name: Optional[str] = Query(
        None,
        description="Optionally, the name of the project for which to return study selections.",
    ),
    project_number: Optional[str] = Query(
        None,
        description="Optionally, the number of the project for which to return study selections.",
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
) -> Sequence[models.StudySelectionCompound]:
    service = StudyCompoundSelectionService(author=current_user_id)
    all_selections = service.get_all_selections_for_all_studies(
        project_name=project_name,
        project_number=project_number,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
    )
    return CustomPage.create(
        items=all_selections.items,
        total=all_selections.total_count,
        page=page_number,
        size=page_size,
    )


@router.get(
    "/study-compounds/headers",
    summary="Returns possible values from the database for a given header",
    description="""Allowed parameters include : field name for which to get possible
    values, search string to provide filtering for the field name, additional filters to apply on other fields""",
    response_model=Sequence[Any],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Invalid field name specified",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_distinct_compound_values_for_header(
    project_name: Optional[str] = Query(
        None,
        description="Optionally, the name of the project for which to return study selections.",
    ),
    project_number: Optional[str] = Query(
        None,
        description="Optionally, the number of the project for which to return study selections.",
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
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyCompoundSelectionService(author=current_user_id)
    return service.get_distinct_values_for_header(
        project_name=project_name,
        project_number=project_number,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/studies/{uid}/study-compounds",
    summary="List all study compounds currently selected for study with provided uid",
    description="""
State before:
 - Study-uid must exist.

Business logic:
 - By default (no study status is provided) list all study compounds for the study uid in status draft. If the study not exist in status draft then return the study compounds for the study in status released. If the study uid only exist as deleted then this is returned.
 - If a specific study status parameter is provided then return study compounds for this study status.
 - If the locked study status parameter is requested then a study version should also be provided, and then the study compounds for the specific locked study version is returned.
 - Indicate by an boolean variable if the study compound can be updated (if the selected study is in status draft).
 - Indicate by an boolean variable if all expected selections have been made for each study compound, or some are missing.
   - e.g. Compound and TypeOfTreatment are expected.
 - Indicate by an boolean variable if the selected compound is available in a newer version.
 - Indicate by an boolean variable if a study compound can be re-ordered.
 
State after:
- no change.
""",
    response_model=GenericFilteringReturn[models.StudySelectionCompound],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "uid",
            "compound=compound.name",
            "pharma_class=compound.p_class_concept",
            "substance_names=compound.unii_substance_name",
            "unii_codes=compound.unii_substance_cd",
            "type_of_treatment=type_of_treatment.name",
            "route_of_admin=route_of_administration.name",
            "dosage_form=dosage_form.name",
            "dispensed_in=dispensed_in",
            "device=device",
            "formulation=formulation",
            "other=other_info",
            "reason_for_missing=reason_for_missing_null_value_code",
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
def get_all_selected_compounds(
    request: Request,  # request is actually required by the allow_exports decorator
    uid: str = studyUID,
    current_user_id: str = Depends(get_current_user_id),
    filters: Optional[Json] = Query(
        None,
        description=_generic_descriptions.FILTERS,
        example=_generic_descriptions.FILTERS_EXAMPLE,
    ),
    page_number: Optional[int] = Query(
        1, ge=1, description=_generic_descriptions.PAGE_NUMBER
    ),
    page_size: Optional[int] = Query(
        config.DEFAULT_PAGE_SIZE, ge=0, description=_generic_descriptions.PAGE_SIZE
    ),
    operator: Optional[str] = Query("and", description=_generic_descriptions.OPERATOR),
    total_count: Optional[bool] = Query(
        False, description=_generic_descriptions.TOTAL_COUNT
    ),
):
    service = StudyCompoundSelectionService(author=current_user_id)
    return service.get_all_selection(
        study_uid=uid,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
    )


@router.get(
    "/studies/{uid}/study-compounds/headers",
    summary="Returns possible values from the database for a given header",
    description="""Allowed parameters include : field name for which to get possible
    values, search string to provide filtering for the field name, additional filters to apply on other fields""",
    response_model=Sequence[Any],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Invalid field name specified",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_distinct_compounds_values_for_header(
    uid: str = studyUID,
    project_name: Optional[str] = Query(
        None,
        description="Optionally, the name of the project for which to return study selections.",
    ),
    project_number: Optional[str] = Query(
        None,
        description="Optionally, the number of the project for which to return study selections.",
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
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyCompoundSelectionService(author=current_user_id)
    return service.get_distinct_values_for_header(
        study_uid=uid,
        project_name=project_name,
        project_number=project_number,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/studies/{uid}/study-compounds/audit-trail",
    summary="List full audit trail related to definition of all study compounds.",
    description="""
Parameters:
 - uid as study-uid (required)
 - [NOT YET IMPLEMENTED] study status (optional)
 - [NOT YET IMPLEMENTED] study version (required when study status is locked)

State before:
 - Study must exist.

Business logic:
 - List all entries in the audit trail related to study compounds for specified study-uid.
 - If the released or a locked version of the study is selected then only entries up to the time of the study release or lock is included.

State after:
 - no change.
 
Possible errors:
 - Invalid study-uid.

Returned data:
 - List of actions and changes related to study compounds.
    """,
    response_model=Sequence[models.StudySelectionCompound],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_compounds_audit_trail(
    uid: str = studyUID, current_user_id: str = Depends(get_current_user_id)
) -> Sequence[models.StudySelectionCompound]:
    service = StudyCompoundSelectionService(author=current_user_id)
    return service.get_all_selection_audit_trail(study_uid=uid)


@router.get(
    "/studies/{uid}/study-compounds/{study_compound_uid}/audit-trail",
    summary="List audit trail related to definition of a specific study compound.",
    description="""
Parameters:
 - uid as study-uid (required)
 - study-compound-uid (required)
 - [NOT YET IMPLEMENTED] study status (optional)
 - [NOT YET IMPLEMENTED] study version (required when study status is locked)

State before:
 - Study and study compounds must exist.

Business logic:
 - List a specific entry in the audit trail related to the specified study compound for the specified study-uid.
 - If the released or a locked version of the study is selected then only entries up to the time of the study release or lock is included.

State after:
 - no change.
 
Possible errors:
 - Invalid study-uid.

Returned data:
 - List of actions and changes related to the specified study compound.
    """,
    response_model=Sequence[models.StudySelectionCompound],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the objective for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_compound_audit_trail(
    uid: str = studyUID,
    study_compound_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCompound:
    service = StudyCompoundSelectionService(author=current_user_id)
    return service.get_specific_selection_audit_trail(
        study_uid=uid, study_selection_uid=study_compound_uid
    )


@router.get(
    "/studies/{uid}/study-compounds/{study_compound_uid}",
    summary="Returns specific study compound",
    description="""
State before:
 - Study-uid and study-compound-uid must exist

Business logic:
 - By default (no study status is provided) list all details for specified study compound for the study uid in status draft. If the study not exist in status draft then return the study compounds for the study in status released. If the study uid only exist as deleted then this is returned.
 - If a specific study status parameter is provided then return study compounds for this study status.
 - If the locked study status parameter is requested then a study version should also be provided, and then the specified study compound for the specific locked study version is returned.  - Indicate by an boolean variable if the study compound can be updated (if the selected study is in status draft).
 - Indicate by an boolean variable if all expected selections have been made for each study compound, or some are missing.
   - e.g. Compound and TypeOfTreatment are expected.
 - Indicate by an boolean variable if the selected compound is available in a newer version.
 - Indicate by an boolean variable if a study compound can be re-ordered.

State after:
 - no change
""",
    response_model=models.StudySelectionCompound,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the objective for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_compound(
    uid: str = studyUID,
    study_compound_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCompound:
    service = StudyCompoundSelectionService(author=current_user_id)
    return service.get_specific_selection(
        study_uid=uid, study_selection_uid=study_compound_uid
    )


@router.post(
    "/studies/{uid}/study-compounds",
    summary="Add a study compound to a study based on selection of a compound concept in library, or a 'Reason for missing'.",
    description="""
State before:
 - Study must exist and be in status draft
 - Compound-uid must exist and be in status Final.
 
Business logic:
 - Add a study-compound to the study based on selection of an existing compound concept in the library.
 - If the selected compound-uid is retired then an error message must be provided.
 - A single relationships can be defined for a study compound to each of the following code list terms:
   - Type of treatment
   - Route of administration
   - Dosages form
   - Dispensed in
   - Device
   - Formulation
 - It is also possible to save a free test string describing other information for the study-compound.
 - Order for the study compound must be assigged as the next incremental order number or as 1 if this is the initial study objective for the study.
 - It should be possible to define a 'Reason for missing' value for a specific value of 'Type of treatment'. In this case the following rule apply:
   - Only the parameter for 'Type of treatment' can be defined - the parameter value for compound or any other related parameters must be null.
   - No other study compound must exist for the study with the same value for 'Type of Treatment'.
   - No other 'Reason for missing' value must exist for the study with the same value for 'Type of Treatment' (ReasonForMissing can only be defined once for a TypeOfTreatment).
   - Thereby either the parameter compound-uid or type-of-treatment-uid must be provided, but not both of them 8they are mytually exclusive).

State after:
 - compound is added as study compound to the study.
 - Added new entry in the audit trail for the creation of the study-compound.
 """,
    response_model=models.StudySelectionCompound,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - There already exists a selection of the objective",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or objective is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def post_new_compound_selection(
    uid: str = studyUID,
    selection: models.StudySelectionCompoundInput = Body(
        None, description="Related parameters of the selection that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCompound:
    service = StudyCompoundSelectionService(author=current_user_id)
    return service.make_selection(study_uid=uid, selection_create_input=selection)


@router.delete(
    "/studies/{uid}/study-compounds/{study_compound_uid}",
    summary="Delete a study compound.",
    description="""
State before:
- Study and study-compound-uid must exist and study must be in status draft.

Business logic:
 - Remove specified study-compound from the study.
 - Reference to the study-compound should still exist in the the audit trail.
 - If a subsequent study compound exist in the list of study compounds then the order number for following study compound must be decreased with 1.

State after:
- Study compound is deleted from the study, but still exist as a node in the database with a reference from the audit trail.
- Added new entry in the audit trail for the deletion of the study-compound.
""",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The selection was successfully deleted."},
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the objective and the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def delete_selected_compound(
    uid: str = studyUID,
    study_compound_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyCompoundSelectionService(author=current_user_id)
    service.delete_selection(study_uid=uid, study_selection_uid=study_compound_uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/studies/{uid}/study-compounds/{study_compound_uid}/order",
    summary="Change display order of study compound",
    description="""
State before:
- Study and study-compound-uid must exist and study must be in status draft.
- Old order number must match current order number in database for study compound.

Business logic:
 - moves the study selection to the order which is send in the new_order property
 
State after:
 - Order number for specified study-compound is updated to new order number.
 - Note this will change order on either the preceding or following study-compounds as well.
 - Added new entry in the audit trail for the re-ordering of the study-compounds.
""",
    response_model=models.StudySelectionCompound,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and objective to reorder.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_new_compound_selection_order(
    uid: str = studyUID,
    study_compound_uid: str = study_selection_uid,
    new_order_input: models.StudySelectionCompoundNewOrder = Body(
        None, description="Related parameters of the selection that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCompound:
    service = StudyCompoundSelectionService(author=current_user_id)
    return service.set_new_order(
        study_uid=uid,
        study_selection_uid=study_compound_uid,
        new_order=new_order_input.new_order,
    )


@router.patch(
    "/studies/{uid}/study-compounds/{study_compound_uid}",
    summary="Edit or replace a study compound",
    description="""
State before:
 - Study must exist and be in status draft
 - Compound-uid must exist and be in status Final.

Business logic:
 - Update specified study-compound with selection of an existing compound concept in the library.
 - If the selected compound-uid is retired then an error message must be provided.
 - A single relationships can be defined for a study compound to each of the following code list terms:
   - Type of treatment
   - Route of administration
   - Dosages form
   - Dispensed in
   - Device
   - Formulation
 - It is also possible to save a free text string describing other information for the study-compound.
 - Order number for the study compound cannot be changed by this API endpoint.
 - It should be possible to define a 'Reason for missing' value for a specific value of 'Type of treatment'. In this case the following rule apply:
   - Only the parameter for 'Type of treatment' can be defined - the parameter value for compound or any other related parameters must be null.
   - No other study compound must exist for the study with the same value for 'Type of Treatment'.
   - No other 'Reason for missing' value must exist for the study with the same value for 'Type of Treatment' (ReasonForMissing can only be defined once for a TypeOfTreatment).
   - Thereby either the parameter compound-uid or type-of-treatment-uid must be provided, but not both of them 8they are mutually exclusive).

State after:
 - compound or related parameters is updated for the study compound.
 - Added new entry in the audit trail for the update of the study-compound.""",
    response_model=models.StudySelectionCompound,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and objective.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_update_compound_selection(
    uid: str = studyUID,
    study_compound_uid: str = study_selection_uid,
    selection: models.StudySelectionCompoundInput = Body(
        None, description="Related parameters of the selection that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCompound:
    service = StudyCompoundSelectionService(author=current_user_id)
    return service.patch_selection(
        study_uid=uid,
        study_selection_uid=study_compound_uid,
        selection_update_input=selection,
    )


@router.post(
    "/studies/{uid}/study-endpoints/{study_endpoint_uid}/sync-latest-endpoint-version",
    summary="update to latest endpoint version study selection",
    description="""
State before:
 - Study must exist
 - Study endpoint selection must exist
 - Endpoint version selected for study endpoint selection is not the latest available final version of endpoint.

Business logic:
 - Update specified endpoint study-selection with the latest final version of previously selected endpoint.

State after:
 - Study exists
 - Study endpoint selection exists
 - Endpoint version selected for study endpoint selection is the latest available final version.
 - Added new entry in the audit trail for the update of the study-endpoint.""",
    response_model=models.StudySelectionEndpoint,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and endpoint",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def sync_latest_endpoint_version(
    uid: str = studyUID,
    study_endpoint_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionObjective:
    service = StudyEndpointSelectionService(author=current_user_id)
    return service.update_selection_to_latest_version_of_endpoint(
        study_uid=uid, study_selection_uid=study_endpoint_uid
    )


@router.post(
    "/studies/{uid}/study-endpoints/{study_endpoint_uid}/sync-latest-timeframe-version",
    summary="update to latest timeframe version study selection",
    description="""
    State before:
     - Study must exist
     - Study endpoint selection must exist
     - Timeframe version selected for study endpoint selection is not the latest available final version of the timeframe.

    Business logic:
     - Update specified endpoint study-selection with the latest final version of previously selected timeframe.

    State after:
     - Study exists
     - Study endpoint selection exists
     - Timeframe version selected for study endpoint selection is the latest available final version.
     - Added new entry in the audit trail for the update of the study-endpoint.""",
    response_model=models.StudySelectionEndpoint,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and timeframe",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def sync_latest_timeframe_version(
    uid: str = studyUID,
    study_endpoint_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionObjective:
    service = StudyEndpointSelectionService(author=current_user_id)
    return service.update_selection_to_latest_version_of_timeframe(
        study_uid=uid, study_selection_uid=study_endpoint_uid
    )


@router.post(
    "/studies/{uid}/study-endpoints/{study_endpoint_uid}/accept-version",
    summary="update to latest timeframe version study selection",
    description="""
    State before:
     - Study must exist
     - Study endpoint selection must exist
     - Timeframe and/or endpoint version selected for study endpoint selection is not the latest available final version of the timeframe.

    Business logic:
     - Update specified endpoint study-selection, setting accepted version to show that update was refused by user.

    State after:
     - Study exists
     - Study endpoint selection exists
     - Timeframe and endpoint version selected for study endpoint selection is not changed.
     - Added new entry in the audit trail for the update of the study-endpoint.""",
    response_model=models.StudySelectionEndpoint,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and timeframe",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_endpoint_accept_version(
    uid: str = studyUID,
    study_endpoint_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionObjective:
    service = StudyEndpointSelectionService(author=current_user_id)
    return service.update_selection_accept_versions(
        study_uid=uid, study_selection_uid=study_endpoint_uid
    )


@router.post(
    "/studies/{uid}/study-objectives/{study_objective_uid}/accept-version",
    summary="update to latest timeframe version study selection",
    description="""
    State before:
     - Study must exist
     - Study endpoint selection must exist
     - Objective version selected for study endpoint selection is not the latest available final version of the timeframe.

    Business logic:
     - Update specified endpoint study-selection, setting accepted version to show that update was refused by user.

    State after:
     - Study exists
     - Study endpoint selection exists
     - Objective version selected for study endpoint selection is not changed.
     - Added new entry in the audit trail for the update of the study-endpoint.""",
    response_model=models.StudySelectionObjective,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and timeframe",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_objective_accept_version(
    uid: str = studyUID,
    study_objective_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionObjective:
    service = StudyObjectiveSelectionService(author=current_user_id)
    return service.update_selection_accept_version(
        study_uid=uid, study_selection_uid=study_objective_uid
    )


"""
    API endpoints to study criteria
"""


@router.get(
    "/study-criteria",
    summary="Returns all study criteria currently selected",
    response_model=CustomPage[models.StudySelectionCriteria],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_selected_criteria_for_all_studies(
    no_brackets: bool = Query(
        False,
        description="Indicates whether brackets around Template Parameters in the Criteria"
        "should be returned",
    ),
    project_name: Optional[str] = Query(
        None,
        description="Optionally, the name of the project for which to return study selections.",
    ),
    project_number: Optional[str] = Query(
        None,
        description="Optionally, the number of the project for which to return study selections.",
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
) -> Sequence[models.StudySelectionCriteria]:
    service = StudyCriteriaSelectionService(author=current_user_id)
    all_selections = service.get_all_selections_for_all_studies(
        no_brackets=no_brackets,
        project_name=project_name,
        project_number=project_number,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
    )
    return CustomPage.create(
        items=all_selections.items,
        total=all_selections.total_count,
        page=page_number,
        size=page_size,
    )


@router.get(
    "/study-criteria/headers",
    summary="Returns possible values from the database for a given header",
    description="""Allowed parameters include : field name for which to get possible
    values, search string to provide filtering for the field name, additional filters to apply on other fields""",
    response_model=Sequence[Any],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Invalid field name specified",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_distinct_criteria_values_for_header(
    project_name: Optional[str] = Query(
        None,
        description="Optionally, the name of the project for which to return study selections.",
    ),
    project_number: Optional[str] = Query(
        None,
        description="Optionally, the number of the project for which to return study selections.",
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
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyCriteriaSelectionService(author=current_user_id)
    return service.get_distinct_values_for_header(
        project_name=project_name,
        project_number=project_number,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/studies/{uid}/study-criteria",
    summary="Returns all study criteria currently selected for study with provided uid",
    description="""
    State before:
    - Study must exist.
    
    Business logic:
    - By default (no study status is provided) list all study criteria for the study uid in status draft. If the study not exist in status draft then return the study criteria for the study in status released. If the study uid only exist as deleted then this is returned.
    - If a specific study status parameter is provided then return study criteria for this study status.
    - If the locked study status parameter is requested then a study version should also be provided, and then the study criteria for the specific locked study version is returned.
    - Indicate by a boolean variable if the study criteria can be updated (if the selected study is in status draft).  
    - Indicate by a boolean variable if all expected selections have been made for each study criteria, or some are missing.
    - e.g. a criteria instance is expected.
    - Indicate by an boolean variable if a study criteria can be re-ordered.

    State after:
    - no change.
    
    Possible errors:
    - Invalid study-uid.
    
    Returned data:
    List selected study with the following information:
    - study_uid
    - study_criteria_uid
    - order (Derived Integer, valid in the scope of a criteria_type)
    - criteria_uid (Selected CriteriaRoot  uid)
    - criteria_name (String, CriteriaValue name)
    - criteria_type (String, derived from the selected criteria instance's template, which has a connection to a type node)
    - note (String)
    - Modified (as a date of last modification).
    - Possible Actions (based on study state, version of selected nodes, metadata consistency checks, etc. - see business rules).
        - Boolean indication if edit is possible.
        - Boolean indication if all expected selections have been made.
        - Boolean indication if the study criteria can be re-ordered.
    """,
    response_model=CustomPage[models.StudySelectionCriteria],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "uid",
            "name",
            "guidance_text",
            "key_criteria",
            "start_date",
            "user_initials",
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
def get_all_selected_criteria(
    request: Request,  # request is actually required by the allow_exports decorator
    uid: str = studyUID,
    no_brackets: bool = Query(
        False,
        description="Indicates whether brackets around Template Parameters in the Criteria"
        "should be returned",
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
) -> Sequence[models.StudySelectionCriteria]:
    service = StudyCriteriaSelectionService(author=current_user_id)
    all_items = service.get_all_selection(
        study_uid=uid,
        no_brackets=no_brackets,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
    )

    return CustomPage.create(
        items=all_items.items,
        total=all_items.total_count,
        page=page_number,
        size=page_size,
    )


@router.get(
    "/studies/{uid}/study-criteria/headers",
    summary="Returns possible values from the database for a given header",
    description="""Allowed parameters include : field name for which to get possible
    values, search string to provide filtering for the field name, additional filters to apply on other fields""",
    response_model=Sequence[Any],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Invalid field name specified",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_distinct_study_criteria_values_for_header(
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
    uid: str = studyUID,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyCriteriaSelectionService(author=current_user_id)
    return service.get_distinct_values_for_header(
        study_uid=uid,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/studies/{uid}/study-criteria/audit-trail",
    summary="List full audit trail related to definition of all study criteria.",
    description="""
    State before:
    - Study must exist.

    Business logic:
    - List all entries in the audit trail related to study criteria for specified study-uid.
    - If the released or a locked version of the study is selected then only entries up to the time of the study release or lock is included.

    State after:
    - no change.
    
    Possible errors:
    - Invalid study-uid.

    Returned data:
    List selected study with the following information:
    - study_uid
    - study_criteria_uid
    - order (Derived Integer)
    - criteria_uid (Selected CriteriaRoot  uid)
    - criteria_name (String, CriteriaValue name)
    - criteria_type (String, derived from the selected criteria instance's template, which has a connection to a type node)
    - note (String)
    - Modified (as a date of last modification).
    - Possible Actions (based on study state, version of selected nodes, metadata consistency checks, etc. - see business rules).
        - Boolean indication if edit is possible.
        - Boolean indication if all expected selections have been made.
        - Boolean indication if the study criteria can be re-ordered.
    """,
    response_model=Sequence[models.StudySelectionCriteriaCore],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_criteria_audit_trail(
    uid: str = studyUID,
    criteria_type_uid: Optional[str] = Query(
        None,
        description="Optionally, the uid of the criteria_type for which to return study criteria audit trial.",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> Sequence[models.StudySelectionCriteriaCore]:
    service = StudyCriteriaSelectionService(author=current_user_id)
    return service.get_all_selection_audit_trail(
        study_uid=uid, criteria_type_uid=criteria_type_uid
    )


@router.get(
    "/studies/{uid}/study-criteria/{study_criteria_uid}",
    summary="Returns specific study criteria",
    description="""
    State before:
    - Study and study criteria must exist
    
    Business logic:
    - By default (no study status is provided) list all details for specified study criteria for the study uid in status draft. If the study not exist in status draft then return the study criteria for the study in status released. If the study uid only exist as deleted then this is returned.
    - If a specific study status parameter is provided then return study criteria for this study status.
    - If the locked study status parameter is requested then a study version should also be provided, and then the specified study criteria for the specific locked study version is returned.
    - Indicate by an boolean variable if the study criteria can be updated (if the selected study is in status draft).
    - Indicate by an boolean variable if all expected selections have been made for each study criteria, or some are missing.
    - Indicate by an boolean variable if the selected criteria is available in a newer version.
    - Indicate by an boolean variable if a study criteria can be re-ordered.
    
    State after:
    - no change
    
    Possible errors:
    - Invalid study-uid or study_criteria_uid.
    
    Returned data:
    List selected study with the following information:
    - study_uid
    - study_criteria_uid
    - order (Derived Integer)
    - criteria_uid (Selected CriteriaRoot  uid)
    - criteria_name (String, CriteriaValue name)
    - criteria_type (String, derived from the selected criteria instance's template, which has a connection to a type node)
    - note (String)
    - Modified (as a date of last modification).
    - Possible Actions (based on study state, version of selected nodes, metadata consistency checks, etc. - see business rules).
        - Boolean indication if edit is possible.
        - Boolean indication if all expected selections have been made.
        - Boolean indication if the study criteria can be re-ordered.
    """,
    response_model=models.StudySelectionCriteria,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exists no selection of the criteria for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_criteria(
    uid: str = studyUID,
    study_criteria_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCriteria:
    service = StudyCriteriaSelectionService(author=current_user_id)
    return service.get_specific_selection(
        study_uid=uid, study_selection_uid=study_criteria_uid
    )


@router.get(
    "/studies/{uid}/study-criteria/{study_criteria_uid}/audit-trail",
    summary="List audit trail related to definition of a specific study criteria.",
    description="""
    State before:
    - Study and study criteria must exist.

    Business logic:
    - List a specific entry in the audit trail related to the specified study criteria for the specified study-uid.
    - If the released or a locked version of the study is selected then only entries up to the time of the study release or lock is included.

    State after:
    - no change.
    
    Possible errors:
    - Invalid study-uid.

    Returned data:
    List selected study with the following information:
    - study_uid
    - study_criteria_uid
    - order (Derived Integer)
    - criteria_uid (Selected CriteriaRoot  uid)
    - criteria_name (String, CriteriaValue name)
    - criteria_type (String, derived from the selected criteria instance's template, which has a connection to a type node)
    - note (String)
    - Modified (as a date of last modification).
    - Possible Actions (based on study state, version of selected nodes, metadata consistency checks, etc. - see business rules).
        - Boolean indication if edit is possible.
        - Boolean indication if all expected selections have been made.
        - Boolean indication if the study criteria can be re-ordered.
    """,
    response_model=Sequence[models.StudySelectionCriteriaCore],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the criteria for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_criteria_audit_trail(
    uid: str = studyUID,
    study_criteria_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCriteriaCore:
    service = StudyCriteriaSelectionService(author=current_user_id)
    return service.get_specific_selection_audit_trail(
        study_uid=uid, study_selection_uid=study_criteria_uid
    )


@router.post(
    "/studies/{uid}/study-criteria",
    summary="Creating a study criteria selection based on the input data including creating new criteria",
    description="""
    State before:
    - Study must exist and study status must be in draft.

    Business logic:
    - Create a study criteria and to a study based on valid selections and values.
    
    State after:
    - criteria instance is created
    - criteria is added as study criteria to the study.
    - Added new entry in the audit trail for the creation of the study-criteria.
    
    Possible errors:
    - Invalid study-uid.

    Returned data:
    List selected study with the following information:
    - study_uid
    - study_criteria_uid
    - order (Derived Integer)
    - criteria_uid (Selected CriteriaRoot  uid)
    - criteria_name (String, CriteriaValue name)
    - criteria_type (String, derived from the selected criteria instance's template, which has a connection to a type node)
    - note (String)
    - Modified (as a date of last modification).
    - Possible Actions (based on study state, version of selected nodes, metadata consistency checks, etc. - see business rules).
        - Boolean indication if edit is possible. (study is in Draft status)
        - Boolean indication if all expected selections have been made. (expected !== required)
    """,
    response_model=models.StudySelectionCriteria,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - There already exists a selection of the criteria",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or criteria is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def post_new_criteria_selection_create(
    uid: str = studyUID,
    selection: models.study_selection.StudySelectionCriteriaCreateInput = Body(
        None, description="Related parameters of the selection that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCriteria:
    service = StudyCriteriaSelectionService(author=current_user_id)
    return service.make_selection_create_criteria(
        study_uid=uid, selection_create_input=selection
    )


@router.post(
    "/studies/{uid}/study-criteria/preview",
    summary="Previews creating a study criteria selection based on the input data including creating new criteria",
    response_model=models.StudySelectionCriteria,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - There already exists a selection of the criteria",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or criteria is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def preview_new_criteria_selection_create(
    uid: str = studyUID,
    selection: models.study_selection.StudySelectionCriteriaCreateInput = Body(
        None, description="Related parameters of the selection that shall be previewed."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCriteria:
    service = StudyCriteriaSelectionService(author=current_user_id)
    return service.make_selection_preview_criteria(
        study_uid=uid, selection_create_input=selection
    )


@router.post(
    "/studies/{uid}/study-criteria/batch-select",
    summary="Select multiple criteria templates as a batch. If the template has no parameters, will also create the instance.",
    description="""
    State before:
    - Study must exist and study status must be in draft.

    Business logic:
    - Select criteria template without instantiating them.
    - This must be done as a batch
    
    State after:
    - Study criteria is created.
    - Criteria templates are all selected by the study criteria.
    - If a given template has no parameters, the instance will be created and selected.
    - Added new entry in the audit trail for the creation of the study-criteria.
    
    Possible errors:
    - Invalid study-uid.
    - Invalid study-criteria-template-uid.

    Returned data:
    List selected criteria templates/instances with the following information:
    - study_uid
    - study_criteria_template_uid / study_criteria_uid
    - order (Derived Integer)
    - latest version of the selected criteria template/instance
    """,
    response_model=Sequence[models.StudySelectionCriteria],
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - There already exists a selection of the criteria",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or criteria is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def post_batch_select_criteria_template(
    uid: str = studyUID,
    selection: Sequence[
        models.study_selection.StudySelectionCriteriaTemplateSelectInput
    ] = Body(
        None,
        description="List of objects with properties needed to identify the templates to select",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCriteria:
    service = StudyCriteriaSelectionService(author=current_user_id)
    return service.batch_select_criteria_template(
        study_uid=uid, selection_create_input=selection
    )


@router.patch(
    "/studies/{uid}/study-criteria/{study_criteria_uid}/finalize",
    summary="Finalize the study criteria template selection by creating an instance of this template",
    description="""
    State before:
    - Study and study selection must exist and the selected object must be a template and not an instance.

    Business logic:
    - Create an instance of the selected template
    - Re-attach the study criteria object to the instance instead of the template
    
    State after:
    - Instance of the template is created
    - Study criteria is detached from the template
    - Study criteria is attached to the instance
    
    Possible errors:
    - Invalid study-uid.
    - Invalid study-criteria-uid.

    Returned data:
    Selected criteria instance with the following information:
    - study_uid
    - study_criteria_uid
    - order
    - latest version of the selected criteria
    """,
    response_model=models.StudySelectionCriteria,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or study criteria is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_finalize_criteria_selection(
    uid: str = studyUID,
    study_criteria_uid: str = study_selection_uid,
    criteria_data: models.CriteriaCreateInput = Body(
        None,
        description="Data necessary to create the criteria instance from the template",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCriteria:
    service = StudyCriteriaSelectionService(author=current_user_id)
    return service.finalize_criteria_selection(
        study_uid=uid,
        study_criteria_uid=study_criteria_uid,
        criteria_data=criteria_data,
    )


@router.delete(
    "/studies/{uid}/study-criteria/{study_criteria_uid}",
    summary="Deletes a study criteria",
    description="""
    State before:
    - Study must exist and study status must be in draft.
    - study_criteria_uid must exist. 

    Business logic:
    - Remove specified study-criteria from the study.
    - Reference to the study-criteria should still exist in the the audit trail.

    State after:
    - Study criteria deleted from the study, but still exist as a node in the database with a reference from the audit trail.
    - Added new entry in the audit trail for the deletion of the study-criteria .
    
    Possible errors:
    - Invalid study-uid or study_criteria_uid.

    Returned data:
    - none
    """,
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The selection was successfully deleted."},
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the criteria and the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def delete_selected_criteria(
    uid: str = studyUID,
    study_criteria_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyCriteriaSelectionService(author=current_user_id)
    service.delete_selection(study_uid=uid, study_selection_uid=study_criteria_uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/studies/{uid}/study-criteria/{study_criteria_uid}/order",
    summary="Change the order of a study criteria",
    response_model=models.StudySelectionCriteria,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exists no selection between the study and criteria to reorder.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_new_criteria_selection_order(
    uid: str = studyUID,
    study_criteria_uid: str = study_selection_uid,
    new_order_input: models.StudySelectionCriteriaNewOrder = Body(
        None, description="New value to set for the order property of the selection"
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCriteria:
    service = StudyCriteriaSelectionService(author=current_user_id)
    return service.set_new_order(
        study_uid=uid,
        study_selection_uid=study_criteria_uid,
        new_order=new_order_input.new_order,
    )


@router.patch(
    "/studies/{uid}/study-criteria/{study_criteria_uid}/key-criteria",
    summary="Change the key-criteria property of a study criteria",
    response_model=models.StudySelectionCriteria,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exists no selection between the study and criteria to change.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_criteria_selection_key_criteria_property(
    uid: str = studyUID,
    study_criteria_uid: str = study_selection_uid,
    key_criteria_input: models.StudySelectionCriteriaKeyCriteria = Body(
        None,
        description="New value to set for the key-criteria property of the selection",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCriteria:
    service = StudyCriteriaSelectionService(author=current_user_id)
    return service.set_key_criteria(
        study_uid=uid,
        study_selection_uid=study_criteria_uid,
        key_criteria=key_criteria_input.key_criteria,
    )


#
# API endpoints to study activity
#


@router.get(
    "/study-activities",
    summary="Returns all study activities currently selected",
    response_model=CustomPage[models.StudySelectionActivity],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_selected_activities_for_all_studies(
    project_name: Optional[str] = Query(
        None,
        description="Optionally, the name of the project for which to return study selections.",
    ),
    project_number: Optional[str] = Query(
        None,
        description="Optionally, the number of the project for which to return study selections.",
    ),
    activity_names: Optional[List[str]] = Query(
        None, description="A list of activity names to use as a specific filter"
    ),
    activity_subgroup_names: Optional[List[str]] = Query(
        None,
        description="A list of activity sub group names to use as a specific filter",
    ),
    activity_group_names: Optional[List[str]] = Query(
        None, description="A list of activity group names to use as a specific filter"
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
) -> Sequence[models.StudySelectionEndpoint]:
    service = StudyActivitySelectionService(author=current_user_id)
    all_selections = service.get_all_selections_for_all_studies(
        project_name=project_name,
        project_number=project_number,
        activity_names=activity_names,
        activity_subgroup_names=activity_subgroup_names,
        activity_group_names=activity_group_names,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
    )
    return CustomPage.create(
        items=all_selections.items,
        total=all_selections.total_count,
        page=page_number,
        size=page_size,
    )


@router.get(
    "/studies/{uid}/study-activities",
    summary="Returns all study activities currently selected",
    response_model=CustomPage[models.StudySelectionActivity],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there is no study with the given uid.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "uid",
            "flowchart_group=flowchart_group.sponsor_preferred_name",
            "activity_group",
            "activity_subgroup",
            "name=activity.name",
            "note",
            "start_date",
            "user_initials",
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
def get_all_selected_activities(
    request: Request,  # request is actually required by the allow_exports decorator
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
    uid: str = studyUID,
    current_user_id: str = Depends(get_current_user_id),
) -> CustomPage[models.StudySelectionActivity]:
    service = StudyActivitySelectionService(author=current_user_id)
    all_items = service.get_all_selection(
        study_uid=uid,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
    )

    return CustomPage.create(
        items=all_items.items,
        total=all_items.total_count,
        page=page_number,
        size=page_size,
    )


@router.get(
    "/studies/{uid}/study-activities/headers",
    summary="Returns possible values from the database for a given header",
    description="""Allowed parameters include : field name for which to get possible
    values, search string to provide filtering for the field name, additional filters to apply on other fields""",
    response_model=Sequence[Any],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Invalid field name specified",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_distinct_activity_values_for_header(
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
    uid: str = studyUID,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyActivitySelectionService(author=current_user_id)
    return service.get_distinct_values_for_header(
        study_uid=uid,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/studies/{uid}/study-activities/audit-trail",
    summary="List full audit trail related to definition of all study activities.",
    description="""
The following values should be returned for all study activities:
- date_time
- user_initials
- action
- activity
- order
    """,
    response_model=Sequence[models.StudySelectionActivityCore],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_activity_audit_trail(
    uid: str = studyUID, current_user_id: str = Depends(get_current_user_id)
) -> Sequence[models.StudySelectionActivityCore]:
    service = StudyActivitySelectionService(author=current_user_id)
    return service.get_all_selection_audit_trail(study_uid=uid)


@router.get(
    "/studies/{uid}/study-activities/{study_activity_uid}",
    summary="Returns specific study activity",
    response_model=models.StudySelectionActivity,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exists no selection of the activity for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_activity(
    uid: str = studyUID,
    study_activity_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionActivity:
    service = StudyActivitySelectionService(author=current_user_id)
    return service.get_specific_selection(
        study_uid=uid, study_selection_uid=study_activity_uid
    )


@router.get(
    "/studies/{uid}/study-activities/{study_activity_uid}/audit-trail",
    summary="List audit trail related to definition of a specific study activity.",
    response_model=Sequence[models.StudySelectionActivityCore],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the activity for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_activity_audit_trail(
    uid: str = studyUID,
    study_activity_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionActivityCore:
    service = StudyActivitySelectionService(author=current_user_id)
    return service.get_specific_selection_audit_trail(
        study_uid=uid, study_selection_uid=study_activity_uid
    )


@router.post(
    "/studies/{uid}/study-activities",
    summary="Creating a study activity selection based on the input data",
    response_model=models.StudySelectionActivity,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - There already exists a selection of the activity",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or activity is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def post_new_activity_selection_create(
    uid: str = studyUID,
    selection: models.study_selection.StudySelectionActivityCreateInput = Body(
        None, description="Related parameters of the selection that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionActivity:
    service = StudyActivitySelectionService(author=current_user_id)
    return service.make_selection(study_uid=uid, selection_create_input=selection)


@router.patch(
    "/studies/{uid}/study-activities/{study_activity_uid}",
    summary="Edit a study activity",
    description="""
State before:
 - Study must exist and be in status draft

Business logic:
 

State after:
 - Added new entry in the audit trail for the update of the study-activity.""",
    response_model=models.StudySelectionActivity,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and activity.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_update_activity_selection(
    uid: str = studyUID,
    study_activity_uid: str = study_selection_uid,
    selection: models.StudySelectionActivityInput = Body(
        None, description="Related parameters of the selection that shall be updated."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionActivity:
    service = StudyActivitySelectionService(author=current_user_id)
    return service.patch_selection(
        study_uid=uid,
        study_selection_uid=study_activity_uid,
        selection_update_input=selection,
    )


@router.patch(
    "/studies/{uid}/study-activities/{study_activity_uid}/activity-requests-approvals",
    summary="Update Study Activity with the Sponsor Activity that replaced Activity Request",
    description="""
State before:
 - Study must exist and be in status draft

Business logic:


State after:
 - Added new entry in the audit trail for the update of the study-activity.""",
    response_model=models.StudySelectionActivity,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and activity.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def update_activity_request_with_sponsor_activity(
    uid: str = studyUID,
    study_activity_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionActivity:
    service = StudyActivitySelectionService(author=current_user_id)
    return service.update_activity_request_with_sponsor_activity(
        study_uid=uid,
        study_selection_uid=study_activity_uid,
    )


@router.delete(
    "/studies/{uid}/study-activities/{study_activity_uid}",
    summary="Delete a study activity",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The selection was successfully deleted."},
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the activity and the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def delete_selected_activity(
    uid: str = studyUID,
    study_activity_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyActivitySelectionService(author=current_user_id)
    service.delete_selection(study_uid=uid, study_selection_uid=study_activity_uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/studies/{uid}/study-activities/batch",
    summary="Batch create and/or edit of study activities",
    response_model=Sequence[models.StudySelectionActivityBatchOutput],
    status_code=207,
    responses={500: {"model": ErrorResponse, "description": "Internal Server Error"}},
)
def activity_selection_batch_operations(
    uid: str = studyUID,
    operations: Sequence[models.StudySelectionActivityBatchInput] = Body(
        None, description=""
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> Sequence[models.StudySelectionActivityBatchOutput]:
    service = StudyActivitySelectionService(author=current_user_id)
    return service.handle_batch_operations(uid, operations)


@router.patch(
    "/studies/{uid}/study-activities/{study_activity_uid}/order",
    summary="Change the order of a study activity",
    response_model=models.StudySelectionActivity,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exists no selection between the study and activity to reorder.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_new_activity_selection_order(
    uid: str = studyUID,
    study_activity_uid: str = study_selection_uid,
    new_order_input: models.StudySelectionActivityNewOrder = Body(
        None, description="New value to set for the order property of the selection"
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionActivity:
    service = StudyActivitySelectionService(author=current_user_id)
    return service.set_new_order(
        study_uid=uid,
        study_selection_uid=study_activity_uid,
        new_order=new_order_input.new_order,
    )


"""
Study Selection Arm endpoints 
 """


@router.get(
    "/studies/{uid}/study-arms",
    summary="""List all study arms currently selected for study with provided uid""",
    description="""
    State before:
    - Study must exist.
     
    Business logic:
     - By default (no study status is provided) list all study arms for the study uid in status draft. If the study not exist in status draft then return the study arms for the study in status released. If the study uid only exist as deleted then this is returned.
     - If a specific study status parameter is provided then return study arm for this study status.
    - If the locked study status parameter is requested then a study version should also be provided, and then the study arms for the specific locked study version is returned.
    - Indicate by a boolean variable if the study arm can be updated (if the selected study is in status draft).  
    - Indicate by a boolean variable if all expected selections have been made for each study arms, or some are missing.


    State after:
    - no change.
     
    Possible errors:
    - Invalid study-uid.
""",
    response_model=CustomPage[models.StudySelectionArmWithConnectedBranchArms],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "uid",
            "type=arm_type.sponsor_preferred_name",
            "name",
            "code",
            "randomization_group",
            "number_of_subjects",
            "description",
            "start_date",
            "user_initials",
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
def get_all_selected_arms(
    request: Request,  # request is actually required by the allow_exports decorator
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
    uid: str = studyUID,
    current_user_id: str = Depends(get_current_user_id),
) -> CustomPage[models.StudySelectionArmWithConnectedBranchArms]:
    service = StudyArmSelectionService(author=current_user_id)
    all_items = service.get_all_selection(
        study_uid=uid,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
    )

    return CustomPage.create(
        items=all_items.items,
        total=all_items.total_count,
        page=page_number,
        size=page_size,
    )


@router.get(
    "/studies/{uid}/study-arms/headers",
    summary="Returns possible values from the database for a given header",
    description="""Allowed parameters include : field name for which to get possible
    values, search string to provide filtering for the field name, additional filters to apply on other fields""",
    response_model=Sequence[Any],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Invalid field name specified",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_distinct_arm_values_for_header(
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
    uid: str = studyUID,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyArmSelectionService(author=current_user_id)
    return service.get_distinct_values_for_header(
        study_uid=uid,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/study-arms",
    summary="Returns all study arms currently selected",
    response_model=CustomPage[models.StudySelectionArmWithConnectedBranchArms],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_selected_arms_for_all_studies(
    project_name: Optional[str] = Query(
        None,
        description="Optionally, the name of the project for which to return study selections.",
    ),
    project_number: Optional[str] = Query(
        None,
        description="Optionally, the number of the project for which to return study selections.",
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
) -> Sequence[models.StudySelectionArmWithConnectedBranchArms]:
    service = StudyArmSelectionService(author=current_user_id)
    all_selections = service.get_all_selections_for_all_studies(
        project_name=project_name,
        project_number=project_number,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
    )
    return CustomPage.create(
        items=all_selections.items,
        total=all_selections.total_count,
        page=page_number,
        size=page_size,
    )


@router.post(
    "/studies/{uid}/study-arms",
    summary="Creating a study arm selection based on the input data",
    response_model=models.StudySelectionArm,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - There already exists a selection of the arm",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or arm is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def post_new_arm_selection_create(
    uid: str = studyUID,
    selection: models.study_selection.StudySelectionArmCreateInput = Body(
        None, description="Related parameters of the selection that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionArm:
    service = StudyArmSelectionService(author=current_user_id)
    return service.make_selection(study_uid=uid, selection_create_input=selection)


@router.patch(
    "/studies/{uid}/study-arms/{study_arm_uid}",
    summary="Edit a study arm",
    description="""
State before:
 - Study must exist and be in status draft

Business logic:


State after:
 - Added new entry in the audit trail for the update of the study-arm.""",
    response_model=models.StudySelectionArmWithConnectedBranchArms,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and arm.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_update_arm_selection(
    uid: str = studyUID,
    study_arm_uid: str = study_selection_uid,
    selection: models.StudySelectionArmInput = Body(
        None, description="Related parameters of the selection that shall be updated."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionArmWithConnectedBranchArms:
    service = StudyArmSelectionService(author=current_user_id)
    return service.patch_selection(
        study_uid=uid,
        study_selection_uid=study_arm_uid,
        selection_update_input=selection,
    )


@router.get(
    "/studies/{uid}/study-arms/{study_arm_uid}/audit-trail",
    summary="List audit trail related to definition of a specific study arm.",
    response_model=Sequence[models.StudySelectionArmVersion],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the activity for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_arm_audit_trail(
    uid: str = studyUID,
    study_arm_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> Sequence[models.StudySelectionArmVersion]:
    service = StudyArmSelectionService(author=current_user_id)
    return service.get_specific_selection_audit_trail(
        study_uid=uid, study_selection_uid=study_arm_uid
    )


@router.get(
    "/studies/{uid}/study-arms/audit-trail",
    summary="List audit trail related to definition of all study arms.",
    response_model=Sequence[models.StudySelectionArmVersion],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_arm_audit_trail(
    uid: str = studyUID,
    current_user_id: str = Depends(get_current_user_id),
) -> Sequence[models.StudySelectionArmVersion]:
    service = StudyArmSelectionService(author=current_user_id)
    return service.get_all_selection_audit_trail(study_uid=uid)


@router.get(
    "/studies/{uid}/study-arms/{study_arm_uid}",
    summary="Returns specific study arm",
    response_model=models.StudySelectionArmWithConnectedBranchArms,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exists no selection of the arm for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_arm(
    uid: str = studyUID,
    study_arm_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionArmWithConnectedBranchArms:
    service = StudyArmSelectionService(author=current_user_id)
    return service.get_specific_selection(
        study_uid=uid, study_selection_uid=study_arm_uid
    )


@router.patch(
    "/studies/{uid}/study-arms/{study_arm_uid}/order",
    summary="Change the order of a study arm",
    response_model=models.StudySelectionArmWithConnectedBranchArms,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exists no selection between the study and arm to reorder.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_new_arm_selection_order(
    uid: str = studyUID,
    study_arm_uid: str = study_selection_uid,
    new_order_input: models.StudySelectionArmNewOrder = Body(
        None, description="New value to set for the order property of the selection"
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionArmWithConnectedBranchArms:
    service = StudyArmSelectionService(author=current_user_id)
    return service.set_new_order(
        study_uid=uid,
        study_selection_uid=study_arm_uid,
        new_order=new_order_input.new_order,
    )


@router.delete(
    "/studies/{uid}/study-arms/{study_arm_uid}",
    summary="Delete a study arm",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The selection was successfully deleted."},
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the arm and the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def delete_selected_arm(
    uid: str = studyUID,
    study_arm_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyArmSelectionService(author=current_user_id)
    service.delete_selection(study_uid=uid, study_selection_uid=study_arm_uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


#
# API endpoints to study elements
#


@router.post(
    "/studies/{uid}/study-elements",
    summary="Creating a study element selection based on the input data",
    response_model=models.StudySelectionElement,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - There already exists a selection of the element",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or element is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def post_new_element_selection_create(
    uid: str = studyUID,
    selection: models.study_selection.StudySelectionElementCreateInput = Body(
        None, description="Related parameters of the selection that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionElement:
    service = StudyElementSelectionService(author=current_user_id)
    return service.make_selection(study_uid=uid, selection_create_input=selection)


@router.get(
    "/studies/{uid}/study-elements",
    summary="""List all study elements currently selected for study with provided uid""",
    description="""
    State before:
    - Study must exist.

    State after:
    - no change.
     
    Possible errors:
    - Invalid study-uid.
""",
    response_model=CustomPage[models.StudySelectionElement],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_selected_elements(
    uid: str = studyUID,
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
) -> CustomPage[models.StudySelectionElement]:
    service = StudyElementSelectionService(author=current_user_id)
    all_items = service.get_all_selection(
        study_uid=uid,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
    )

    return CustomPage.create(
        items=all_items.items,
        total=all_items.total_count,
        page=page_number,
        size=page_size,
    )


@router.get(
    "/studies/{uid}/study-elements/headers",
    summary="Returns possible values from the database for a given header",
    description="""Allowed parameters include : field name for which to get possible
    values, search string to provide filtering for the field name, additional filters to apply on other fields""",
    response_model=Sequence[Any],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Invalid field name specified",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_distinct_element_values_for_header(
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
    uid: str = studyUID,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyElementSelectionService(author=current_user_id)
    return service.get_distinct_values_for_header(
        study_uid=uid,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/studies/{uid}/study-elements/{study_element_uid}",
    summary="Returns specific study element",
    response_model=models.StudySelectionElement,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exists no selection of the element for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_element(
    uid: str = studyUID,
    study_element_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionElement:
    service = StudyElementSelectionService(author=current_user_id)
    return service.get_specific_selection(
        study_uid=uid, study_selection_uid=study_element_uid
    )


@router.patch(
    "/studies/{uid}/study-elements/{study_element_uid}",
    summary="Edit a study element",
    description="""
        State before:
        - Study must exist and be in status draft

        Business logic:

        State after:
        - Added new entry in the audit trail for the update of the study-element.""",
    response_model=models.StudySelectionElement,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and element.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_update_element_selection(
    uid: str = studyUID,
    study_element_uid: str = study_selection_uid,
    selection: models.StudySelectionElementInput = Body(
        None, description="Related parameters of the selection that shall be updated."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionElement:
    service = StudyElementSelectionService(author=current_user_id)
    return service.patch_selection(
        study_uid=uid,
        study_selection_uid=study_element_uid,
        selection_update_input=selection,
    )


@router.get(
    "/studies/{uid}/study-elements/{study_element_uid}/audit-trail",
    summary="List audit trail related to definition of a specific study element.",
    response_model=Sequence[models.StudySelectionElementVersion],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the activity for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_element_audit_trail(
    uid: str = studyUID,
    study_element_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> Sequence[models.StudySelectionElementVersion]:
    service = StudyElementSelectionService(author=current_user_id)
    return service.get_specific_selection_audit_trail(
        study_uid=uid, study_selection_uid=study_element_uid
    )


@router.get(
    "/studies/{uid}/study-element/audit-trail",
    summary="List audit trail related to definition of all study element.",
    response_model=Sequence[models.StudySelectionElementVersion],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_element_audit_trail(
    uid: str = studyUID,
    current_user_id: str = Depends(get_current_user_id),
) -> Sequence[models.StudySelectionElementVersion]:
    service = StudyElementSelectionService(author=current_user_id)
    return service.get_all_selection_audit_trail(study_uid=uid)


@router.delete(
    "/studies/{uid}/study-elements/{study_element_uid}",
    summary="Delete a study element",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The selection was successfully deleted."},
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the element and the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def delete_selected_element(
    uid: str = studyUID,
    study_element_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyElementSelectionService(author=current_user_id)
    service.delete_selection(study_uid=uid, study_selection_uid=study_element_uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/study-elements/allowed-element-configs",
    summary="Returns all allowed config sets for element type and subtype",
    response_model=Sequence[models.StudyElementTypes],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_configs(
    current_user_id: str = Depends(get_current_user_id),
) -> Sequence[models.StudyElementTypes]:
    service = StudyElementSelectionService(current_user_id)
    return service.get_allowed_configs()


@router.patch(
    "/studies/{uid}/study-elements/{study_element_uid}/order",
    summary="Change the order of a study element",
    response_model=models.StudySelectionElement,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exists no selection between the study and element to reorder.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_new_element_selection_order(
    uid: str = studyUID,
    study_element_uid: str = study_selection_uid,
    new_order_input: models.StudySelectionElementNewOrder = Body(
        None, description="New value to set for the order property of the selection"
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionElement:
    service = StudyElementSelectionService(author=current_user_id)
    return service.set_new_order(
        study_uid=uid,
        study_selection_uid=study_element_uid,
        new_order=new_order_input.new_order,
    )


"""
API Study-Branch-Arms endpoints 
"""


@router.post(
    "/studies/{uid}/study-branch-arms",
    summary="Creating a study branch arm selection based on the input data",
    response_model=models.StudySelectionBranchArm,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - There already exists a selection of the branch arm",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or branch arm is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def post_new_branch_arm_selection_create(
    uid: str = studyUID,
    selection: models.study_selection.StudySelectionBranchArmCreateInput = Body(
        None, description="Related parameters of the selection that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionBranchArm:
    service = StudyBranchArmSelectionService(author=current_user_id)
    return service.make_selection(study_uid=uid, selection_create_input=selection)


@router.get(
    "/studies/{uid}/study-branch-arms",
    summary="""List all study branch arms currently selected for study with provided uid""",
    description="""
    State before:
    - Study must exist.
     
    Business logic:
     - By default (no study status is provided) list all study branch arms for the study uid in status draft. If the study not exist in status draft then return the study branch arms for the study in status released. If the study uid only exist as deleted then this is returned.
     - If a specific study status parameter is provided then return study branch arm for this study status.
    - If the locked study status parameter is requested then a study version should also be provided, and then the study branch arms for the specific locked study version is returned.
    - Indicate by a boolean variable if the study branch arm can be updated (if the selected study is in status draft).  
    - Indicate by a boolean variable if all expected selections have been made for each study branch arms, or some are missing.


    State after:
    - no change.
     
    Possible errors:
    - Invalid study-uid.
""",
    response_model=Sequence[models.StudySelectionBranchArm],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_selected_branch_arms(
    uid: str = studyUID, current_user_id: str = Depends(get_current_user_id)
) -> Sequence[models.StudySelectionBranchArm]:
    service = StudyBranchArmSelectionService(author=current_user_id)
    return service.get_all_selection(study_uid=uid)


@router.get(
    "/studies/{uid}/study-branch-arms/{study_branch_arm_uid}",
    summary="Returns specific study branch arm",
    response_model=models.StudySelectionBranchArm,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exists no selection of the branch arm for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_branch_arm(
    uid: str = studyUID,
    study_branch_arm_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionBranchArm:
    service = StudyBranchArmSelectionService(author=current_user_id)
    return service.get_specific_selection(
        study_uid=uid, study_selection_uid=study_branch_arm_uid
    )


@router.patch(
    "/studies/{uid}/study-branch-arms/{study_branch_arm_uid}",
    summary="Edit a study branch arm",
    description="""
            State before:
            - Study must exist and be in status draft
            Business logic:

            State after:
            - Added new entry in the audit trail for the update of the study-branch-arm.""",
    response_model=models.StudySelectionBranchArm,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and branch arm.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_update_branch_arm_selection(
    uid: str = studyUID,
    study_branch_arm_uid: str = study_selection_uid,
    selection: models.StudySelectionBranchArmEditInput = Body(
        None, description="Related parameters of the selection that shall be updated."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionBranchArm:
    service = StudyBranchArmSelectionService(author=current_user_id)
    selection.branch_arm_uid = study_branch_arm_uid
    return service.patch_selection(
        study_uid=uid,
        # study_selection_uid=study_branch_arm_uid,
        selection_update_input=selection,
    )


@router.get(
    "/studies/{uid}/study-branch-arms/{study_branch_arm_uid}/audit-trail",
    summary="List audit trail related to definition of a specific study branch-arm.",
    response_model=Sequence[models.StudySelectionBranchArmVersion],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the activity for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_branch_arm_audit_trail(
    uid: str = studyUID,
    study_branch_arm_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> Sequence[models.StudySelectionBranchArmVersion]:
    service = StudyBranchArmSelectionService(author=current_user_id)
    return service.get_specific_selection_audit_trail(
        study_uid=uid, study_selection_uid=study_branch_arm_uid
    )


@router.get(
    "/studies/{uid}/study-branch-arm/audit-trail",
    summary="List audit trail related to definition of all study branch-arm.",
    response_model=Sequence[models.StudySelectionBranchArmVersion],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_branch_arm_audit_trail(
    uid: str = studyUID,
    current_user_id: str = Depends(get_current_user_id),
) -> Sequence[models.StudySelectionBranchArmVersion]:
    service = StudyBranchArmSelectionService(author=current_user_id)
    return service.get_all_selection_audit_trail(study_uid=uid)


@router.delete(
    "/studies/{uid}/study-branch-arms/{study_branch_arm_uid}",
    summary="Delete a study branch arm",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The selection was successfully deleted."},
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the branch arm and the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def delete_selected_branch_arm(
    uid: str = studyUID,
    study_branch_arm_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyBranchArmSelectionService(author=current_user_id)
    service.delete_selection(study_uid=uid, study_selection_uid=study_branch_arm_uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/studies/{uid}/study-branch-arms/{study_branch_arm_uid}/order",
    summary="Change the order of a study branch arm",
    response_model=models.StudySelectionBranchArm,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exists no selection between the study and branch arm to reorder.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_new_branch_arm_selection_order(
    uid: str = studyUID,
    study_branch_arm_uid: str = study_selection_uid,
    new_order_input: models.StudySelectionBranchArmNewOrder = Body(
        None, description="New value to set for the order property of the selection"
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionBranchArm:
    service = StudyBranchArmSelectionService(author=current_user_id)
    return service.set_new_order(
        study_uid=uid,
        study_selection_uid=study_branch_arm_uid,
        new_order=new_order_input.new_order,
    )


@router.get(
    "/studies/{uid}/study-branch-arms/arm/{arm_uid}",
    summary="""List all study branch arms currently selected for study with provided uid""",
    description="""
    State before:
    - Study must exist.
     
    Business logic:
     - By default (no study status is provided) list all study branch arms for the study uid in status draft. If the study not exist in status draft then return the study branch arms for the study in status released. If the study uid only exist as deleted then this is returned.
     - If a specific study status parameter is provided then return study branch arm for this study status.
    - If the locked study status parameter is requested then a study version should also be provided, and then the study branch arms for the specific locked study version is returned.
    - Indicate by a boolean variable if the study branch arm can be updated (if the selected study is in status draft).  
    - Indicate by a boolean variable if all expected selections have been made for each study branch arms, or some are missing.


    State after:
    - no change.
     
    Possible errors:
    - Invalid study-uid.
""",
    response_model=Sequence[models.StudySelectionBranchArm],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_selected_branch_arms_within_arm(
    uid: str, arm_uid: str, current_user_id: str = Depends(get_current_user_id)
) -> Sequence[models.StudySelectionBranchArm]:
    service = StudyBranchArmSelectionService(author=current_user_id)
    return service.get_all_selection_within_arm(study_uid=uid, study_arm_uid=arm_uid)


"""
API Study-Cohorts endpoints 
"""


@router.post(
    "/studies/{uid}/study-cohorts",
    summary="Creating a study cohort selection based on the input data",
    response_model=models.StudySelectionCohort,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - There already exists a selection of the cohort",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study or cohort is not found with the passed 'uid'.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def post_new_cohort_selection_create(
    uid: str = studyUID,
    selection: models.StudySelectionCohortCreateInput = Body(
        None, description="Related parameters of the selection that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCohort:
    service = StudyCohortSelectionService(author=current_user_id)
    return service.make_selection(study_uid=uid, selection_create_input=selection)


@router.get(
    "/studies/{uid}/study-cohorts",
    summary="""List all study cohorts currently selected for study with provided uid""",
    description="""
    State before:
    - Study must exist.
     
    Business logic:
     - By default (no study status is provided) list all study cohorts for the study uid in status draft. If the study not exist in status draft then return the study cohorts for the study in status released. If the study uid only exist as deleted then this is returned.
     - If a specific study status parameter is provided then return study cohort for this study status.
    - If the locked study status parameter is requested then a study version should also be provided, and then the study cohorts for the specific locked study version is returned.
    - Indicate by a boolean variable if the study cohort can be updated (if the selected study is in status draft).  
    - Indicate by a boolean variable if all expected selections have been made for each study cohorts, or some are missing.


    State after:
    - no change.
     
    Possible errors:
    - Invalid study-uid.
""",
    response_model=CustomPage[models.StudySelectionCohort],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_selected_cohorts(
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
    arm_uid: Optional[str] = Query(
        None,
        description="The unique id of the study arm for which specified study cohorts should be returned",
    ),
    uid: str = studyUID,
) -> CustomPage[models.StudySelectionCohort]:
    service = StudyCohortSelectionService(author=current_user_id)

    all_selections = service.get_all_selection(
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
        study_uid=uid,
        arm_uid=arm_uid,
    )
    return CustomPage.create(
        items=all_selections.items,
        total=all_selections.total_count,
        page=page_number,
        size=page_size,
    )


@router.get(
    "/studies/{uid}/study-cohorts/{study_cohort_uid}",
    summary="Returns specific study cohort",
    response_model=models.StudySelectionCohort,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exists no selection of the cohort for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_cohort(
    uid: str = studyUID,
    study_cohort_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCohort:
    service = StudyCohortSelectionService(author=current_user_id)
    return service.get_specific_selection(
        study_uid=uid, study_selection_uid=study_cohort_uid
    )


@router.patch(
    "/studies/{uid}/study-cohorts/{study_cohort_uid}",
    summary="Edit a study cohort",
    description="""
            State before:
            - Study must exist and be in status draft
            Business logic:

            State after:
            - Added new entry in the audit trail for the update of the study-cohort.""",
    response_model=models.StudySelectionCohort,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exist no selection between the study and cohort.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_update_cohort_selection(
    uid: str = studyUID,
    study_cohort_uid: str = study_selection_uid,
    selection: models.StudySelectionCohortEditInput = Body(
        None, description="Related parameters of the selection that shall be updated."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCohort:
    service = StudyCohortSelectionService(author=current_user_id)
    return service.patch_selection(
        study_uid=uid,
        study_selection_uid=study_cohort_uid,
        selection_update_input=selection,
    )


@router.get(
    "/studies/{uid}/study-cohorts/{study_cohort_uid}/audit-trail",
    summary="List audit trail related to definition of a specific study study-cohorts.",
    response_model=Sequence[models.StudySelectionCohortVersion],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the activity for the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_selected_cohort_audit_trail(
    uid: str = studyUID,
    study_cohort_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
) -> Sequence[models.StudySelectionCohortVersion]:
    service = StudyCohortSelectionService(author=current_user_id)
    return service.get_specific_selection_audit_trail(
        study_uid=uid, study_selection_uid=study_cohort_uid
    )


@router.get(
    "/studies/{uid}/study-cohort/audit-trail",
    summary="List audit trail related to definition of all study study-cohort.",
    response_model=Sequence[models.StudySelectionCohortVersion],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_all_cohort_audit_trail(
    uid: str = studyUID,
    current_user_id: str = Depends(get_current_user_id),
) -> Sequence[models.StudySelectionCohortVersion]:
    service = StudyCohortSelectionService(author=current_user_id)
    return service.get_all_selection_audit_trail(study_uid=uid)


@router.delete(
    "/studies/{uid}/study-cohorts/{study_cohort_uid}",
    summary="Delete a study cohort",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The selection was successfully deleted."},
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the cohort and the study provided.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def delete_selected_cohort(
    uid: str = studyUID,
    study_cohort_uid: str = study_selection_uid,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyCohortSelectionService(author=current_user_id)
    service.delete_selection(study_uid=uid, study_selection_uid=study_cohort_uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/studies/{uid}/study-cohorts/{study_cohort_uid}/order",
    summary="Change the order of a study cohort",
    response_model=models.StudySelectionCohort,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - There exists no selection between the study and cohort to reorder.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def patch_new_cohort_selection_order(
    uid: str = studyUID,
    study_cohort_uid: str = study_selection_uid,
    new_order_input: models.StudySelectionCohortNewOrder = Body(
        None, description="New value to set for the order property of the selection"
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudySelectionCohort:
    service = StudyCohortSelectionService(author=current_user_id)
    return service.set_new_order(
        study_uid=uid,
        study_selection_uid=study_cohort_uid,
        new_order=new_order_input.new_order,
    )
