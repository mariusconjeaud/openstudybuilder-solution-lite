from typing import Callable, Self

from pydantic import Field

from clinical_mdr_api.domains.clinical_programmes.clinical_programme import (
    ClinicalProgrammeAR,
)
from clinical_mdr_api.models.utils import BaseModel


class ClinicalProgramme(BaseModel):
    uid: str = Field(
        ...,
        title="uid",
        description="The unique id of the ClinicalProgramme value.",
    )

    name: str = Field(
        ...,
        title="name",
        description="",
    )

    @classmethod
    def from_uid(
        cls,
        uid: str,
        find_by_uid: Callable[[str], ClinicalProgrammeAR],
    ) -> Self:
        return ClinicalProgramme.from_clinical_programme_ar(find_by_uid(uid))

    @classmethod
    def from_clinical_programme_ar(
        cls, clinical_programme_ar: ClinicalProgrammeAR
    ) -> Self:
        return cls(uid=clinical_programme_ar.uid, name=clinical_programme_ar.name)


class ClinicalProgrammeInput(BaseModel):
    name: str = Field(
        ...,
        title="name",
        description="",
        min_length=1,
    )
