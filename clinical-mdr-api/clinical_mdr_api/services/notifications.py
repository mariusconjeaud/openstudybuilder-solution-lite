# pylint: disable=invalid-name
import functools
from datetime import datetime, timezone

from neomodel import db

from clinical_mdr_api import config, exceptions
from clinical_mdr_api.domain_repositories.notification_repository import (
    NotificationRepository,
)
from clinical_mdr_api.models.notification import Notification, NotificationInput


class NotificationService:
    repo: NotificationRepository

    def __init__(self) -> None:
        self.repo = NotificationRepository()

    def get_all_notifications(self) -> list[Notification]:
        return self.repo.retrieve_all_notifications()

    def get_all_active_notifications(self) -> list[Notification]:
        return self.repo.retrieve_all_active_notifications()

    def get_notification(self, sn: int) -> Notification:
        return self.repo.retrieve_notification(sn)

    @db.transaction
    def create_notification(
        self,
        notification_input: NotificationInput,
    ) -> Notification:
        return self.repo.create_notification(
            title=notification_input.title,
            description=notification_input.description,
            notification_type=notification_input.notification_type.value,
            started_at=notification_input.started_at,
            ended_at=notification_input.ended_at,
            published_at=datetime.now(timezone.utc)
            if notification_input.published
            else None,
        )

    @db.transaction
    def update_notification(
        self,
        sn: int,
        notification_input: NotificationInput,
    ) -> Notification:
        return self.repo.update_notification(
            sn=sn,
            title=notification_input.title,
            description=notification_input.description,
            notification_type=notification_input.notification_type.value,
            started_at=notification_input.started_at,
            ended_at=notification_input.ended_at,
            published_at=datetime.now(timezone.utc)
            if notification_input.published
            else None,
        )

    @db.transaction
    def delete_notification(self, sn: int) -> None:
        return self.repo.delete_notification(sn)


def validate_serial_number_less_than_max_int_neo4j():
    """Decorator ensures the provided Serial Number is not bigger than MAX_INT_NEO4J, else raises ValidationException."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if kwargs["sn"] > config.MAX_INT_NEO4J:
                raise exceptions.ValidationException(
                    f"Serial Number must not be greater than {config.MAX_INT_NEO4J}"
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
