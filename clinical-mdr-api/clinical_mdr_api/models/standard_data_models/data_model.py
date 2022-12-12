from typing import Sequence

from pydantic import Field

from clinical_mdr_api.models.concept import VersionProperties


class DataModel(VersionProperties):
    class Config:
        orm_mode = True

    uid: str
    name: str = Field(
        ...,
        title="name",
        description="The name or the data model. E.g. 'SDTM', 'ADAM', ...",
        source="has_latest_value.name",
    )
    description: str = Field(
        ...,
        title="name_sentence_case",
        description="",
        source="has_latest_value.description",
    )
    implementation_guides: Sequence[str] = Field(
        [],
        title="implementation_guides",
        description="",
        source="has_latest_value.implements.name",
    )
    library_name: str = Field(
        None,
        title="library_name",
        description="",
        source="has_library.name",
    )
