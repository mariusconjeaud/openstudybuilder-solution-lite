import logging
from enum import Enum

from pydantic import BaseModel, Field

log = logging.getLogger(__name__)


class SortOrder(Enum):
    ASC = "asc"
    DESC = "desc"


class SortByStudies(Enum):
    UID = "uid"
    ID_PREFIX = "id_prefix"
    NUMBER = "number"


class Study(BaseModel):
    uid: str = Field(..., description="Study UID")
    id: str = Field(..., description="Study ID")
    id_prefix: str = Field(..., description="Study ID prefix")
    number: str | None = Field(None, description="Study number", nullable=True)
    acronym: str | None = Field(None, description="Study acronym", nullable=True)

    @classmethod
    def from_input(cls, val: dict):
        log.debug("Create Study from input: %s", val)
        return cls(
            uid=val["uid"],
            id=val["id"],
            id_prefix=val["id_prefix"],
            number=val["number"],
            acronym=val.get("acronym", None),
        )
