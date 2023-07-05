from typing import Optional, Sequence

from pydantic import Field

from clinical_mdr_api.domains.standard_data_models.master_model_dataset import (
    MasterModelDatasetAR,
)
from clinical_mdr_api.models import Library
from clinical_mdr_api.models.standard_data_models.master_model import MasterModelBase
from clinical_mdr_api.models.utils import BaseModel


class MasterModelDataset(MasterModelBase):
    class Config:
        orm_mode = True

    uid: str = Field(
        None,
        title="uid",
        description="",
        source="uid",
    )
    library_name: str = Field(
        None,
        title="library_name",
        description="",
        source="has_library.name",
    )
    description: str = Field(
        None, title="description", source="has_latest_master_model_value.description"
    )
    is_basic_std: bool = Field(
        None, title="is_basic_std", source="has_latest_master_model_value.is_basic_std"
    )
    xml_path: str = Field(
        None, title="xml_path", source="has_latest_master_model_value.xml_path"
    )
    xml_title: str = Field(
        None, title="xml_title", source="has_latest_master_model_value.xml_title"
    )
    structure: str = Field(
        None, title="structure", source="has_latest_master_model_value.structure"
    )
    purpose: str = Field(
        None, title="purpose", source="has_latest_master_model_value.purpose"
    )
    keys: Optional[Sequence[str]] = Field(
        None,
        title="keys",
    )
    sort_keys: Optional[Sequence[str]] = Field(
        None,
        title="sort_keys",
    )
    comment: str = Field(
        None, title="comment", source="has_latest_master_model_value.comment"
    )
    ig_comment: str = Field(
        None, title="ig_comment", source="has_latest_master_model_value.ig_comment"
    )
    map_domain_flag: bool = Field(
        None,
        title="map_domain_flag",
        source="has_latest_master_model_value.map_domain_flag",
    )
    suppl_qual_flag: bool = Field(
        None,
        title="suppl_qual_flag",
        source="has_latest_master_model_value.suppl_qual_flag",
    )
    include_in_raw: bool = Field(
        None,
        title="include_in_raw",
        source="has_latest_master_model_value.include_in_raw",
    )
    gen_raw_seqno_flag: bool = Field(
        None,
        title="gen_raw_seqno_flag",
        source="has_latest_master_model_value.gen_raw_seqno_flag",
    )
    enrich_build_order: int = Field(
        None,
        title="enrich_build_order",
        source="has_latest_master_model_value.enrich_build_order",
    )
    activity_instance_class_uid: str = Field(
        None,
        title="activity_instance_class_uid",
        source="has_latest_master_model_value.has_activity_instance_class.uid",
    )

    @classmethod
    def from_master_model_dataset_ar(
        cls,
        master_model_dataset_ar: MasterModelDatasetAR,
    ) -> "MasterModelDataset":
        return cls(
            uid=master_model_dataset_ar.uid,
            description=master_model_dataset_ar.master_model_dataset_vo.description,
            is_basic_std=master_model_dataset_ar.master_model_dataset_vo.is_basic_std,
            xml_path=master_model_dataset_ar.master_model_dataset_vo.xml_path,
            xml_title=master_model_dataset_ar.master_model_dataset_vo.xml_title,
            structure=master_model_dataset_ar.master_model_dataset_vo.structure,
            purpose=master_model_dataset_ar.master_model_dataset_vo.purpose,
            keys=master_model_dataset_ar.master_model_dataset_vo.keys,
            sort_keys=master_model_dataset_ar.master_model_dataset_vo.sort_keys,
            comment=master_model_dataset_ar.master_model_dataset_vo.comment,
            ig_comment=master_model_dataset_ar.master_model_dataset_vo.ig_comment,
            map_domain_flag=master_model_dataset_ar.master_model_dataset_vo.map_domain_flag,
            suppl_qual_flag=master_model_dataset_ar.master_model_dataset_vo.suppl_qual_flag,
            include_in_raw=master_model_dataset_ar.master_model_dataset_vo.include_in_raw,
            gen_raw_seqno_flag=master_model_dataset_ar.master_model_dataset_vo.gen_raw_seqno_flag,
            enrich_build_order=master_model_dataset_ar.master_model_dataset_vo.enrich_build_order,
            activity_instance_class_uid=master_model_dataset_ar.master_model_dataset_vo.activity_instance_class_uid,
            library_name=Library.from_library_vo(master_model_dataset_ar.library).name,
            start_date=master_model_dataset_ar.item_metadata.start_date,
            end_date=master_model_dataset_ar.item_metadata.end_date,
            status=master_model_dataset_ar.item_metadata.status.value,
            version=master_model_dataset_ar.item_metadata.version,
            change_description=master_model_dataset_ar.item_metadata.change_description,
            user_initials=master_model_dataset_ar.item_metadata.user_initials,
            possible_actions=sorted(
                [_.value for _ in master_model_dataset_ar.get_possible_actions()]
            ),
        )


class MasterModelDatasetInput(BaseModel):
    dataset_uid: str = Field(
        ..., title="uid", description="Unique identifier of the dataset"
    )
    master_model_name: str = Field(
        ...,
        title="master_model_name",
        description="Name of the master model in which to create the dataset. E.g sdtmig_mastermodel...",
    )
    master_model_version_number: str = Field(
        ...,
        title="master_model_version_number",
        description="Version number of the master model in which to create the dataset",
    )
    description: str = Field(None, title="description", description="")
    is_basic_std: bool = Field(None, title="is_basic_std", description="")
    activity_instance_class_uid: str = Field(
        None,
        title="activity_instance_class_uid",
        description="Optionally, the uid of the activity instance class to connect this Dataset to.",
    )
    xml_path: str = Field(None, title="xml_path", description="")
    xml_title: str = Field(None, title="xml_title", description="")
    structure: str = Field(None, title="structure", description="")
    purpose: str = Field(None, title="purpose", description="")
    keys: Sequence[str] = Field(None, title="keys", description="")
    sort_keys: Sequence[str] = Field(None, title="sort_keys", description="")
    comment: str = Field(None, title="comment", description="")
    ig_comment: str = Field(None, title="ig_comment", description="")
    map_domain_flag: bool = Field(None, title="map_domain_flag", description="")
    suppl_qual_flag: bool = Field(None, title="suppl_qual_flag", description="")
    include_in_raw: bool = Field(None, title="include_in_raw", description="")
    gen_raw_seqno_flag: bool = Field(None, title="gen_raw_seqno_flag", description="")
    enrich_build_order: int = Field(None, title="enrich_build_order", description="")
    change_description: Optional[str] = Field(
        "Imported new version",
        title="change_description",
        description="Optionally, provide a change description.",
    )
    library_name: Optional[str] = Field(
        "CDISC", title="library_name", description="Defaults to CDISC"
    )
