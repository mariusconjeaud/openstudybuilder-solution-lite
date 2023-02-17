from typing import Optional

from pydantic import Field

from clinical_mdr_api.models.concept import VersionProperties


class ClassVariable(VersionProperties):
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
    implementation_notes: Optional[str] = Field(
        None,
        title="implementation_notes",
        description="implementation_notes",
        source="has_latest_value.implementation_notes",
    )
    mapping_instructions: Optional[str] = Field(
        None,
        title="mapping_instructions",
        description="mapping_instructions",
        source="has_latest_value.mapping_instructions",
    )
    prompt: Optional[str] = Field(
        None,
        title="prompt",
        description="prompt",
        source="has_latest_value.prompt",
    )
    question_text: Optional[str] = Field(
        None,
        title="question_text",
        description="question_text",
        source="has_latest_value.question_text",
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

    dataset_class_name: str = Field(
        ...,
        title="dataset_class_name",
        description="dataset_class_name",
        source="has_latest_value.has_class_variable.label",
    )
    dataset_variable_name: Optional[str] = Field(
        None,
        title="dataset_variable_name",
        description="dataset_variable_name",
        source="has_latest_value.implements_class_variable.label",
    )
    catalogue_name: str = Field(
        ...,
        title="catalogue",
        description="catalogue",
        source="has_class_variable.name",
    )
    # library_name: str = Field(
    #     None,
    #     title="library_name",
    #     description="",
    #     source="has_library.name",
    # )
