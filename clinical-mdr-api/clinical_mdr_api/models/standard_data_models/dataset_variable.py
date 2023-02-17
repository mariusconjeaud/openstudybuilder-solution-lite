from typing import Optional

from pydantic import Field

from clinical_mdr_api.models.concept import VersionProperties


class DatasetVariable(VersionProperties):
    class Config:
        orm_mode = True

    uid: str = Field(
        ...,
        title="uid",
        description="The uid of the dataset",
        source="uid",
    )
    label: str = Field(
        ...,
        title="label",
        description="The label of the dataset",
        source="has_latest_value.label",
    )
    title: str = Field(
        ...,
        title="title",
        description="The title of the dataset",
        source="has_latest_value.title",
    )
    description: Optional[str] = Field(
        None,
        title="description",
        description="description",
        source="has_latest_value.description",
    )
    simple_datatype: Optional[str] = Field(
        None,
        title="simple_datatype",
        description="simple_datatype",
        source="has_latest_value.simple_datatype",
    )
    role: Optional[str] = Field(
        None,
        title="role",
        description="role",
        source="has_latest_value.role",
    )
    core: Optional[str] = Field(
        None,
        title="core",
        description="core",
        source="has_latest_value.core",
    )
    dataset_name: str = Field(
        ...,
        title="dataset_name",
        description="dataset_name",
        source="has_latest_value.has_dataset_variable.label",
    )
    implemented_class_variable: str = Field(
        ...,
        title="implemented_class_variable",
        description="implemented_class_variable",
        source="has_latest_value.implements_class_variable.label",
    )
    catalogue_name: str = Field(
        ...,
        title="catalogue",
        description="catalogue",
        source="has_dataset_variable.name",
    )
    # library_name: str = Field(
    #     None,
    #     title="library_name",
    #     description="",
    #     source="has_library.name",
    # )
