from typing import Optional, Sequence

from fastapi import Body, Depends, Query, Response, status
from pydantic.types import Json

from clinical_mdr_api import config, models
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.models.utils import CustomPage
from clinical_mdr_api.oauth import get_current_user_id
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.routers import _generic_descriptions
from clinical_mdr_api.routers import study_router as router
from clinical_mdr_api.routers import utils
from clinical_mdr_api.services.study_activity_instruction import (
    StudyActivityInstructionService,
)


@router.get(
    "/study-activity-instructions",
    summary="Returns all study activity instructions currently selected",
    response_model=CustomPage[models.StudyActivityInstruction],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_all_activity_instructions_for_all_studies(
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
) -> Sequence[models.StudyActivityInstruction]:
    service = StudyActivityInstructionService(author=current_user_id)
    all_selections = service.get_all_instructions_for_all_studies(
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
    "/studies/{uid}/study-activity-instructions",
    summary="List all study activity instructions currently defined for the study",
    response_model=Sequence[models.StudyActivityInstruction],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there is no study with the given uid.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_all_selected_instructions(
    uid: str = utils.studyUID, current_user_id: str = Depends(get_current_user_id)
) -> Sequence[models.StudyActivityInstruction]:
    service = StudyActivityInstructionService(author=current_user_id)
    return service.get_all_instructions(study_uid=uid)


@router.delete(
    "/studies/{uid}/study-activity-instructions/{study_activity_instruction_uid}",
    summary="Delete a study activity instruction",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The selection was successfully deleted."},
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the activity instruction and the study provided.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def delete_activity_instructon(
    uid: str = utils.studyUID,
    study_activity_instruction_uid: str = utils.study_activity_instruction_uid,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyActivityInstructionService(author=current_user_id)
    service.delete(study_uid=uid, instruction_uid=study_activity_instruction_uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/studies/{uid}/study-activity-instructions/batch",
    summary="Batch operations (create, delete) for study activity instructions",
    response_model=Sequence[models.StudyActivityInstructionBatchOutput],
    status_code=207,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def activity_instruction_batch_operations(
    uid: str = utils.studyUID,
    operations: Sequence[models.StudyActivityInstructionBatchInput] = Body(
        description="List of operation to perform"
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> Sequence[models.StudyActivityInstructionBatchOutput]:
    service = StudyActivityInstructionService(author=current_user_id)
    return service.handle_batch_operations(uid, operations)
