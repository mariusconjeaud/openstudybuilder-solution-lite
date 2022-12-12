from typing import Optional

from pydantic import Field

from clinical_mdr_api.models.concept import VersionProperties


class DataModelIG(VersionProperties):
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
    implemented_data_model: Optional[str] = Field(
        None,
        title="implemented_data_model",
        description="",
        source="has_latest_value.implements.name",
    )
    library_name: str = Field(
        None,
        title="library_name",
        description="",
        source="has_library.name",
    )
