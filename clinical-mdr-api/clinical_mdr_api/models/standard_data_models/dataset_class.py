from typing import Optional

from pydantic import Field

from clinical_mdr_api.models.concept import VersionProperties


class DatasetClass(VersionProperties):
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
        title="catalogue_name",
        description="catalogue_name",
        source="has_dataset_class.name",
    )
    data_model_name: str = Field(
        ...,
        title="data_model_name",
        description="data_model_name",
        source="has_latest_value.has_dataset_class.name",
    )
    parent_class: Optional[str] = Field(
        None,
        title="parent_class_name",
        description="parent_class_name",
        source="has_latest_value.has_parent_class.label",
    )
