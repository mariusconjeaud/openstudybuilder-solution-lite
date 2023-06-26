from typing import Sequence

from fastapi import Body, Depends, Response, status

from clinical_mdr_api import models
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.oauth import get_current_user_id
from clinical_mdr_api.routers import _generic_descriptions
from clinical_mdr_api.routers import study_router as router
from clinical_mdr_api.routers.studies import utils
from clinical_mdr_api.services.studies.study_activity_schedule import (
    StudyActivityScheduleService,
)


@router.get(
    "/studies/{uid}/study-activity-schedules",
    summary="List all study activity schedules currently defined for the study",
    response_model=Sequence[models.StudyActivitySchedule],
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
def get_all_selected_activities(
    uid: str = utils.studyUID, current_user_id: str = Depends(get_current_user_id)
) -> Sequence[models.StudyActivitySchedule]:
    service = StudyActivityScheduleService(author=current_user_id)
    return service.get_all_schedules(study_uid=uid)


@router.post(
    "/studies/{uid}/study-activity-schedules",
    summary="Add a study activity schedule to a study",
    response_model=models.StudyActivitySchedule,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - A study activity schedule already exists for selected study activity and visit",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Study, study activity or study visit is not found with the passed 'uid'.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def post_new_activity_schedule_create(
    uid: str = utils.studyUID,
    selection: models.StudyActivityScheduleCreateInput = Body(
        description="Related parameters of the schedule that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.StudyActivitySchedule:
    service = StudyActivityScheduleService(author=current_user_id)
    return service.create(study_uid=uid, schedule_input=selection)


@router.delete(
    "/studies/{uid}/study-activity-schedules/{study_activity_schedule_uid}",
    summary="Delete a study activity schedule",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The selection was successfully deleted."},
        404: {
            "model": ErrorResponse,
            "description": "Not Found - there exist no selection of the activity schedule and the study provided.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def delete_activity_schedule(
    uid: str = utils.studyUID,
    study_activity_schedule_uid: str = utils.study_activity_schedule_uid,
    current_user_id: str = Depends(get_current_user_id),
):
    service = StudyActivityScheduleService(author=current_user_id)
    service.delete(study_uid=uid, schedule_uid=study_activity_schedule_uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/studies/{uid}/study-activity-schedules/audit-trail/",
    summary="List full audit trail related to definition of all study activity schedules.",
    description="""
The following values should be returned for all study activities:
- date_time
- user_initials
- action
- activity
- order
    """,
    response_model=Sequence[models.StudyActivityScheduleHistory],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_all_schedules_audit_trail(
    uid: str = utils.studyUID, current_user_id: str = Depends(get_current_user_id)
) -> Sequence[models.StudyActivityScheduleHistory]:
    service = StudyActivityScheduleService(author=current_user_id)
    return service.get_all_schedules_audit_trail(study_uid=uid)


@router.post(
    "/studies/{uid}/study-activity-schedules/batch",
    summary="Batch operations (create, delete) for study activity schedules",
    response_model=Sequence[models.StudyActivityScheduleBatchOutput],
    status_code=207,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def activity_schedule_batch_operations(
    uid: str = utils.studyUID,
    operations: Sequence[models.StudyActivityScheduleBatchInput] = Body(
        description="List of operation to perform"
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> Sequence[models.StudyActivityScheduleBatchOutput]:
    service = StudyActivityScheduleService(author=current_user_id)
    return service.handle_batch_operations(uid, operations)
