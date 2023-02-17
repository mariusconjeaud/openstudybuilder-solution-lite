from typing import Optional

from pydantic import Field

from clinical_mdr_api.models.concept import VersionProperties


class Dataset(VersionProperties):
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
    catalogue_name: str = Field(
        ...,
        title="catalogue",
        description="catalogue",
        source="has_dataset.name",
    )
    implemented_dataset_class_label: str = Field(
        ...,
        title="implements_dataset_class",
        description="implements_dataset_class",
        source="has_latest_value.implements_dataset_class.label",
    )
    data_model_ig_name: str = Field(
        ...,
        title="data_model_ig_name",
        description="data_model_ig_name",
        source="has_latest_value.has_dataset.name",
    )
    # library_name: str = Field(
    #     None,
    #     title="library_name",
    #     description="",
    #     source="has_library.name",
    # )
