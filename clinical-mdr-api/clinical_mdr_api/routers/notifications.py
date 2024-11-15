# pylint: disable=invalid-name
from fastapi import APIRouter, Body, Path

from clinical_mdr_api.models.notification import Notification, NotificationInput
from clinical_mdr_api.oauth import rbac
from clinical_mdr_api.routers import _generic_descriptions, decorators
from clinical_mdr_api.services.notifications import NotificationService

# Prefixed with "/notifications"
router = APIRouter()

SN = Path(title="Serial Number of the notification")

service = NotificationService()


@router.get(
    "",
    dependencies=[rbac.ADMIN_READ],
    summary="Returns all notifications.",
    response_model=list[Notification],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_all_notifications() -> list[Notification]:
    return service.get_all_notifications()


@router.get(
    "/{serial_number}",
    dependencies=[rbac.ADMIN_READ],
    summary="Returns the notification identified by the provided Serial Number.",
    response_model=Notification,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.validate_serial_number_against_neo4j_max_and_min_int()
def get_notification(serial_number: int = SN) -> Notification:
    return service.get_notification(serial_number)


@router.post(
    "",
    dependencies=[rbac.ADMIN_WRITE],
    summary="Creates a notification.",
    response_model=Notification,
    status_code=201,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def create_notification(
    notification_input: NotificationInput = Body(),
) -> Notification:
    return service.create_notification(notification_input)


@router.patch(
    "/{serial_number}",
    dependencies=[rbac.ADMIN_WRITE],
    summary="Updates the notification identified by the provided Serial Number.",
    response_model=Notification,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.validate_serial_number_against_neo4j_max_and_min_int()
def update_notification(
    serial_number: int = SN,
    notification_input: NotificationInput = Body(),
) -> Notification:
    return service.update_notification(serial_number, notification_input)


@router.delete(
    "/{serial_number}",
    dependencies=[rbac.ADMIN_WRITE],
    summary="Deletes the notification identified by the provided Serial Number.",
    status_code=204,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.validate_serial_number_against_neo4j_max_and_min_int()
def delete_notification(serial_number: int = SN) -> None:
    return service.delete_notification(serial_number)
