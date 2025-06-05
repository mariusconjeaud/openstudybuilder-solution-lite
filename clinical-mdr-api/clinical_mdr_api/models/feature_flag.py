from typing import Annotated

from pydantic import Field

from clinical_mdr_api.models.utils import BaseModel, PatchInputModel, PostInputModel


class FeatureFlag(BaseModel):
    sn: Annotated[int, Field()]
    name: Annotated[str, Field()]
    enabled: Annotated[bool, Field()]
    description: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = (
        None
    )


class FeatureFlagInput(PostInputModel):
    name: Annotated[str, Field(min_length=1)]
    enabled: Annotated[bool, Field()]
    description: Annotated[str | None, Field(min_length=1)] = None


class FeatureFlagPatchInput(PatchInputModel):
    enabled: Annotated[bool, Field()] = False
