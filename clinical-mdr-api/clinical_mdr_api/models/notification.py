from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, validator


class NotificationType(Enum):
    INFORMATION = "information"
    WARNING = "warning"
    ERROR = "error"


class Notification(BaseModel):
    sn: int
    title: str
    notification_type: str
    description: str | None = Field(None, nullable=True)
    started_at: datetime | None = Field(None, nullable=True)
    ended_at: datetime | None = Field(None, nullable=True)
    published_at: datetime | None = Field(None, nullable=True)


class NotificationInput(BaseModel):
    title: str = Field(min_length=1)
    notification_type: NotificationType = NotificationType.INFORMATION
    description: str | None = Field(None, min_length=1)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    published: bool = False

    # pylint: disable=no-self-argument
    @validator("started_at", "ended_at")
    def transform_to_utc(cls, value: datetime | None):
        if not value:
            return None

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)
