from typing import Optional, Sequence

from pydantic import Field

from clinical_mdr_api.domains.standard_data_models.master_model_variable import (
    MasterModelVariableAR,
)
from clinical_mdr_api.models import Library
from clinical_mdr_api.models.standard_data_models.master_model import MasterModelBase
from clinical_mdr_api.models.utils import BaseModel


class MasterModelVariable(MasterModelBase):
    class Config:
        orm_mode = True

    uid: str = Field(
        None,
        title="uid",
        description="",
        source="uid",
    )
    library_name: Optional[str] = Field(
        None,
        title="library_name",
        description="",
        source="has_library.name",
        nullable=True,
    )
    description: Optional[str] = Field(
        None,
        title="description",
        source="has_latest_master_model_value.description",
        nullable=True,
    )
    is_basic_std: Optional[bool] = Field(
        None,
        title="is_basic_std",
        source="has_latest_master_model_value.is_basic_std",
        nullable=True,
    )
    activity_item_class: Optional[str] = Field(
        None,
        title="activity_item_class",
        description="Optionally, the uid of the activity item class to connect this Variable to.",
        nullable=True,
    )
    variable_type: Optional[str] = Field(
        None,
        title="type",
        source="has_latest_master_model_value.variable_type",
        nullable=True,
    )
    length: Optional[int] = Field(
        None,
        title="length",
        source="has_latest_master_model_value.length",
        nullable=True,
    )
    display_format: Optional[str] = Field(
        None,
        title="display_format",
        source="has_latest_master_model_value.display_format",
        nullable=True,
    )
    xml_datatype: Optional[str] = Field(
        None,
        title="xml_datatype",
        source="has_latest_master_model_value.xml_datatype",
        nullable=True,
    )
    xml_codelist: Optional[str] = Field(
        None,
        title="xml_codelist",
        source="has_latest_master_model_value.xml_codelist",
        nullable=True,
    )
    xml_codelist_multi: Optional[str] = Field(
        None,
        title="xml_codelist_multi",
        source="has_latest_master_model_value.xml_codelist_multi",
        nullable=True,
    )
    core: Optional[str] = Field(
        None, title="core", source="has_latest_master_model_value.core", nullable=True
    )
    role: Optional[str] = Field(
        None, title="role", source="has_latest_master_model_value.role", nullable=True
    )
    term: Optional[str] = Field(
        None, title="term", source="has_latest_master_model_value.term", nullable=True
    )
    algorithm: Optional[str] = Field(
        None,
        title="algorithm",
        source="has_latest_master_model_value.algorithm",
        nullable=True,
    )
    qualifiers: Optional[Sequence[str]] = Field(
        None,
        title="qualifiers",
        source="has_latest_master_model_value.qualifiers",
        nullable=True,
    )
    comment: Optional[str] = Field(
        None,
        title="comment",
        source="has_latest_master_model_value.comment",
        nullable=True,
    )
    ig_comment: Optional[str] = Field(
        None,
        title="ig_comment",
        source="has_latest_master_model_value.ig_comment",
        nullable=True,
    )
    map_var_flag: Optional[bool] = Field(
        None,
        title="map_var_flag",
        source="has_latest_master_model_value.map_var_flag",
        nullable=True,
    )
    fixed_mapping: Optional[str] = Field(
        None,
        title="fixed_mapping",
        source="has_latest_master_model_value.fixed_mapping",
        nullable=True,
    )
    include_in_raw: Optional[bool] = Field(
        None,
        title="include_in_raw",
        source="has_latest_master_model_value.include_in_raw",
        nullable=True,
    )
    nn_internal: Optional[bool] = Field(
        None,
        title="nn_internal",
        source="has_latest_master_model_value.nn_internal",
        nullable=True,
    )
    value_lvl_where_cols: Optional[str] = Field(
        None,
        title="value_lvl_where_cols",
        source="has_latest_master_model_value.value_lvl_where_cols",
        nullable=True,
    )
    value_lvl_label_col: Optional[str] = Field(
        None,
        title="value_lvl_label_col",
        source="has_latest_master_model_value.value_lvl_label_col",
        nullable=True,
    )
    value_lvl_collect_ct_val: Optional[str] = Field(
        None,
        title="value_lvl_collect_ct_val",
        source="has_latest_master_model_value.value_lvl_collect_ct_val",
        nullable=True,
    )
    value_lvl_ct_codelist_id_col: Optional[str] = Field(
        None,
        title="value_lvl_ct_codelist_id_col",
        source="has_latest_master_model_value.value_lvl_ct_codelist_id_col",
        nullable=True,
    )
    enrich_build_order: Optional[str] = Field(
        None,
        title="enrich_build_order",
        source="has_latest_master_model_value.enrich_build_order",
        nullable=True,
    )
    enrich_build_order: Optional[int] = Field(
        None,
        title="enrich_build_order",
        source="has_latest_master_model_value.enrich_build_order",
        nullable=True,
    )
    xml_codelist_values: Optional[Sequence[str]] = Field(
        None,
        title="fixed_mapping",
        source="has_latest_master_model_value.xml_codelist_values",
        nullable=True,
    )
    activity_item_class_uid: Optional[str] = Field(
        None,
        title="activity_item_class_uid",
        source="has_latest_master_model_value.has_activity_item_class.uid",
        nullable=True,
    )

    @classmethod
    def from_master_model_variable_ar(
        cls,
        master_model_variable_ar: MasterModelVariableAR,
    ) -> "MasterModelVariable":
        return cls(
            uid=master_model_variable_ar.uid,
            description=master_model_variable_ar.master_model_variable_vo.description,
            is_basic_std=master_model_variable_ar.master_model_variable_vo.is_basic_std,
            variable_type=master_model_variable_ar.master_model_variable_vo.variable_type,
            length=master_model_variable_ar.master_model_variable_vo.length,
            display_format=master_model_variable_ar.master_model_variable_vo.display_format,
            xml_datatype=master_model_variable_ar.master_model_variable_vo.xml_datatype,
            xml_codelist=master_model_variable_ar.master_model_variable_vo.xml_codelist,
            xml_codelist_multi=master_model_variable_ar.master_model_variable_vo.xml_codelist_multi,
            core=master_model_variable_ar.master_model_variable_vo.core,
            role=master_model_variable_ar.master_model_variable_vo.role,
            term=master_model_variable_ar.master_model_variable_vo.term,
            algorithm=master_model_variable_ar.master_model_variable_vo.algorithm,
            qualifiers=master_model_variable_ar.master_model_variable_vo.qualifiers,
            comment=master_model_variable_ar.master_model_variable_vo.comment,
            ig_comment=master_model_variable_ar.master_model_variable_vo.ig_comment,
            map_var_flag=master_model_variable_ar.master_model_variable_vo.map_var_flag,
            fixed_mapping=master_model_variable_ar.master_model_variable_vo.fixed_mapping,
            include_in_raw=master_model_variable_ar.master_model_variable_vo.include_in_raw,
            nn_internal=master_model_variable_ar.master_model_variable_vo.nn_internal,
            value_lvl_where_cols=master_model_variable_ar.master_model_variable_vo.value_lvl_where_cols,
            value_lvl_label_col=master_model_variable_ar.master_model_variable_vo.value_lvl_label_col,
            value_lvl_collect_ct_val=master_model_variable_ar.master_model_variable_vo.value_lvl_collect_ct_val,
            value_lvl_ct_codelist_id_col=master_model_variable_ar.master_model_variable_vo.value_lvl_ct_codelist_id_col,
            enrich_build_order=master_model_variable_ar.master_model_variable_vo.enrich_build_order,
            enrich_rule=master_model_variable_ar.master_model_variable_vo.enrich_rule,
            xml_codelist_values=master_model_variable_ar.master_model_variable_vo.xml_codelist_values,
            activity_item_class_uid=master_model_variable_ar.master_model_variable_vo.activity_item_class_uid,
            library_name=Library.from_library_vo(master_model_variable_ar.library).name,
            start_date=master_model_variable_ar.item_metadata.start_date,
            end_date=master_model_variable_ar.item_metadata.end_date,
            status=master_model_variable_ar.item_metadata.status.value,
            version=master_model_variable_ar.item_metadata.version,
            change_description=master_model_variable_ar.item_metadata.change_description,
            user_initials=master_model_variable_ar.item_metadata.user_initials,
            possible_actions=sorted(
                [_.value for _ in master_model_variable_ar.get_possible_actions()]
            ),
        )


class MasterModelVariableInput(BaseModel):
    dataset_uid: str = Field(
        ...,
        title="dataset_uid",
        description="Uid of the dataset in which to create the variable. E.g AE",
    )
    variable_uid: str = Field(
        ..., title="uid", description="Unique identifier of the variable"
    )
    master_model_version_number: str = Field(
        ...,
        title="master_model_version_number",
        description="Version number of the master model in which to create the variable",
    )
    description: str = Field(None, title="description", description="")
    is_basic_std: bool = Field(None, title="is_basic_std", description="")
    variable_type: str = Field(None, title="variable_type", description="")
    length: int = Field(None, title="length", description="")
    display_format: str = Field(None, title="display_format", description="")
    xml_datatype: str = Field(None, title="xml_datatype", description="")
    xml_codelist: str = Field(None, title="xml_codelist", description="")
    xml_codelist_multi: str = Field(None, title="xml_codelist_multi", description="")
    core: str = Field(None, title="core", description="")
    role: str = Field(None, title="role", description="")
    term: str = Field(None, title="term", description="")
    algorithm: str = Field(None, title="algorithm", description="")
    qualifiers: Sequence[str] = Field(None, title="qualifiers", description="")
    comment: str = Field(None, title="comment", description="")
    ig_comment: str = Field(None, title="ig_comment", description="")
    map_var_flag: bool = Field(None, title="map_var_flag", description="")
    fixed_mapping: str = Field(None, title="fixed_mapping", description="")
    include_in_raw: bool = Field(None, title="include_in_raw", description="")
    nn_internal: bool = Field(None, title="nn_internal", description="")
    value_lvl_where_cols: str = Field(
        None, title="value_lvl_where_cols", description=""
    )
    value_lvl_label_col: str = Field(None, title="value_lvl_label_col", description="")
    value_lvl_collect_ct_val: str = Field(
        None, title="value_lvl_collect_ct_val", description=""
    )
    value_lvl_ct_codelist_id_col: str = Field(
        None, title="value_lvl_ct_codelist_id_col", description=""
    )
    enrich_build_order: int = Field(None, title="enrich_build_order", description="")
    enrich_rule: str = Field(None, title="enrich_rule", description="")
    xml_codelist_values: Sequence[str] = Field(
        None, title="xml_codelist_values", description=""
    )
    activity_item_class_uid: str = Field(
        None,
        title="activity_item_class_uid",
        description="Optionally, the uid of the activity item class to connect this Variable to.",
    )
    change_description: Optional[str] = Field(
        "Imported new version",
        title="change_description",
        description="Optionally, provide a change description.",
    )
    library_name: Optional[str] = Field(
        "CDISC", title="library_name", description="Defaults to CDISC"
    )
