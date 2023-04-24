from typing import Optional

from pydantic import Field

from clinical_mdr_api.domain.standard_data_models.master_model import MasterModelAR
from clinical_mdr_api.models import Library
from clinical_mdr_api.models.concept import VersionProperties
from clinical_mdr_api.models.utils import BaseModel


class MasterModel(VersionProperties):
    class Config:
        orm_mode = True

    uid: str = Field(
        None,
        title="uid",
        description="",
        source="uid",
    )
    name: str = Field(
        ...,
        title="name",
        description="The name or the master model. E.g. sdtm_mastermodel_3.2-NN15",
        source="has_latest_master_model_value.name",
    )
    extended_implementation_guide: Optional[str] = Field(
        None,
        title="extended_implementation_guide",
        description="",
        source="has_latest_master_model_value__extends_version.name",
    )
    library_name: str = Field(
        None,
        title="library_name",
        description="",
        source="has_library.name",
    )

    @classmethod
    def from_master_model_ar(
        cls,
        master_model_ar: MasterModelAR,
    ) -> "MasterModel":
        return cls(
            uid=master_model_ar.uid,
            name=master_model_ar.name,
            library_name=Library.from_library_vo(master_model_ar.library).name,
            start_date=master_model_ar.item_metadata.start_date,
            end_date=master_model_ar.item_metadata.end_date,
            status=master_model_ar.item_metadata.status.value,
            version=master_model_ar.item_metadata.version,
            change_description=master_model_ar.item_metadata.change_description,
            user_initials=master_model_ar.item_metadata.user_initials,
            possible_actions=sorted(
                [_.value for _ in master_model_ar.get_possible_actions()]
            ),
        )


class MasterModelInput(BaseModel):
    ig_uid: str = Field(
        "SDTMIG",
        title="ig_uid",
        description="Unique identifier of the implementation guide to create the master model from. E.g. SDTMIG",
    )
    ig_version_number: str = Field(
        ...,
        title="ig_version_number",
        description="the version number of the Implementation Guide which the master model is based on",
    )
    version_number: str = Field(
        ...,
        title="version_number",
        description="Version number of the master model to use - will be concatenated at the end of the full name",
    )
    change_description: Optional[str] = Field(
        "Imported new version",
        title="change_description",
        description="Optionally, provide a change description.",
    )
    library_name: Optional[str] = Field(
        "CDISC", title="library_name", description="Defaults to CDISC"
    )
