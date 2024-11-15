from pydantic import BaseModel, Field


class FeatureFlag(BaseModel):
    sn: int
    name: str
    enabled: bool
    description: str | None = Field(None, nullable=True)


class FeatureFlagInput(BaseModel):
    name: str
    enabled: bool
    description: str | None = None
