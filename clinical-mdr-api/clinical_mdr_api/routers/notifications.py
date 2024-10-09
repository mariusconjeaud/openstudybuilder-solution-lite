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
    "/{sn}",
    dependencies=[rbac.ADMIN_READ],
    summary="Returns the notification identified by the provided Serial Number.",
    response_model=Notification,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.validate_serial_number_less_than_max_int_neo4j()
def get_notification(sn: int = SN) -> Notification:
    return service.get_notification(sn)


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
    "/{sn}",
    dependencies=[rbac.ADMIN_WRITE],
    summary="Updates the notification identified by the provided Serial Number.",
    response_model=Notification,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.validate_serial_number_less_than_max_int_neo4j()
def update_notification(
    sn: int = SN,
    notification_input: NotificationInput = Body(),
) -> Notification:
    return service.update_notification(sn, notification_input)


@router.delete(
    "/{sn}",
    dependencies=[rbac.ADMIN_WRITE],
    summary="Deletes the notification identified by the provided Serial Number.",
    status_code=204,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.validate_serial_number_less_than_max_int_neo4j()
def delete_notification(sn: int = SN) -> None:
    return service.delete_notification(sn)
