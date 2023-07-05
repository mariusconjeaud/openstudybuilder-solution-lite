import datetime
from dataclasses import dataclass
from typing import AbstractSet, Optional, Sequence, Tuple

from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemAggregateRootBase,
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
    ObjectAction,
)


@dataclass(frozen=True)
class MasterModelVariableVO:
    """
    The MasterModelVariableVO acts as the value object for a single MasterModelVariable value object
    """

    dataset_uid: str
    variable_uid: str
    master_model_version_number: str

    description: str
    is_basic_std: bool
    variable_type: str
    length: int
    display_format: str
    xml_datatype: str
    xml_codelist: str
    xml_codelist_multi: str
    core: str
    role: str
    term: str
    algorithm: str
    qualifiers: Sequence[str]
    comment: str
    ig_comment: str
    map_var_flag: bool
    fixed_mapping: str
    include_in_raw: bool
    nn_internal: bool
    value_lvl_where_cols: str
    value_lvl_label_col: str
    value_lvl_collect_ct_val: str
    value_lvl_ct_codelist_id_col: str
    enrich_build_order: int
    enrich_rule: str
    xml_codelist_values: Sequence[str]
    activity_item_class_uid: str

    @classmethod
    def from_repository_values(
        cls,
        dataset_uid: str,
        variable_uid: str,
        master_model_version_number: Optional[str],
        description: str,
        is_basic_std: bool,
        variable_type: str,
        length: int,
        display_format: str,
        xml_datatype: str,
        xml_codelist: str,
        xml_codelist_multi: str,
        core: str,
        role: str,
        term: str,
        algorithm: str,
        qualifiers: Sequence[str],
        comment: str,
        ig_comment: str,
        map_var_flag: bool,
        fixed_mapping: str,
        include_in_raw: bool,
        nn_internal: bool,
        value_lvl_where_cols: str,
        value_lvl_label_col: str,
        value_lvl_collect_ct_val: str,
        value_lvl_ct_codelist_id_col: str,
        enrich_build_order: int,
        enrich_rule: str,
        xml_codelist_values: Sequence[str],
        activity_item_class_uid: str,
    ) -> "MasterModelVariableVO":
        master_model_variable_vo = cls(
            dataset_uid=dataset_uid,
            variable_uid=variable_uid,
            master_model_version_number=master_model_version_number,
            description=description,
            is_basic_std=is_basic_std,
            variable_type=variable_type,
            length=length,
            display_format=display_format,
            xml_datatype=xml_datatype,
            xml_codelist=xml_codelist,
            xml_codelist_multi=xml_codelist_multi,
            core=core,
            role=role,
            term=term,
            algorithm=algorithm,
            qualifiers=qualifiers,
            comment=comment,
            ig_comment=ig_comment,
            map_var_flag=map_var_flag,
            fixed_mapping=fixed_mapping,
            include_in_raw=include_in_raw,
            nn_internal=nn_internal,
            value_lvl_where_cols=value_lvl_where_cols,
            value_lvl_label_col=value_lvl_label_col,
            value_lvl_collect_ct_val=value_lvl_collect_ct_val,
            value_lvl_ct_codelist_id_col=value_lvl_ct_codelist_id_col,
            enrich_build_order=enrich_build_order,
            enrich_rule=enrich_rule,
            xml_codelist_values=xml_codelist_values,
            activity_item_class_uid=activity_item_class_uid,
        )

        return master_model_variable_vo


class MasterModelVariableMetadataVO(LibraryItemMetadataVO):
    @property
    def version(self) -> str:
        return self._major_version

    @classmethod
    def get_initial_item_metadata(
        cls, author: str, version: str
    ) -> "MasterModelVariableMetadataVO":
        return cls(
            _change_description="Approved version",
            _status=LibraryItemStatus.FINAL,
            _author=author,
            _start_date=datetime.datetime.now(datetime.timezone.utc),
            _end_date=None,
            _major_version=version,
            _minor_version=0,
        )

    def _get_new_version(
        self, new_status: LibraryItemStatus = LibraryItemStatus.FINAL
    ) -> Tuple[int, int]:
        """
        Overriding the method to generate version number.
        MasterModelVariable only have a major version, updated when a new version is created.
        """
        v_major = self._major_version

        return v_major, 0


@dataclass
class MasterModelVariableAR(LibraryItemAggregateRootBase):
    """
    An abstract generic master model variable aggregate for versioned master models
    """

    _master_model_variable_vo: MasterModelVariableVO

    @property
    def master_model_variable_vo(self) -> MasterModelVariableVO:
        return self._master_model_variable_vo

    @property
    def name(self) -> str:
        return self._uid

    def _is_edit_allowed_in_non_editable_library(self) -> bool:
        return True

    @master_model_variable_vo.setter
    def master_model_variable_vo(self, master_model_variable_vo: MasterModelVariableVO):
        self._master_model_variable_vo = master_model_variable_vo

    @classmethod
    def from_repository_values(
        cls,
        variable_uid: str,
        master_model_variable_vo: MasterModelVariableVO,
        library: Optional[LibraryVO],
        item_metadata: MasterModelVariableMetadataVO,
    ) -> "MasterModelVariableAR":
        master_model_variable_ar = cls(
            _uid=variable_uid,
            _master_model_variable_vo=master_model_variable_vo,
            _item_metadata=item_metadata,
            _library=library,
        )
        return master_model_variable_ar

    @classmethod
    def from_input_values(
        cls,
        *,
        author: str,
        master_model_variable_vo: MasterModelVariableVO,
        library: LibraryVO,
    ) -> "MasterModelVariableAR":
        item_metadata = MasterModelVariableMetadataVO.get_initial_item_metadata(
            author=author, version=master_model_variable_vo.master_model_version_number
        )

        master_model_variable_ar = cls(
            _uid=master_model_variable_vo.variable_uid,
            _item_metadata=item_metadata,
            _library=library,
            _master_model_variable_vo=master_model_variable_vo,
        )
        return master_model_variable_ar

    def edit_draft(
        self,
        author: str,
        change_description: Optional[str],
        master_model_variable_vo: MasterModelVariableVO,
    ) -> None:
        """
        Creates a new draft version for the object.
        """

        if self._master_model_variable_vo != master_model_variable_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self.master_model_variable_vo = master_model_variable_vo

    def create_new_version(self, author: str) -> None:
        """
        Puts object into DRAFT status with relevant changes to version numbers.
        """
        super()._create_new_version(author=author)

    def get_possible_actions(self) -> AbstractSet[ObjectAction]:
        """
        Returns list of possible actions
        """
        if (
            self._item_metadata.status == LibraryItemStatus.DRAFT
            and self._item_metadata.major_version == 0
        ):
            return {ObjectAction.APPROVE, ObjectAction.EDIT, ObjectAction.DELETE}
        if self._item_metadata.status == LibraryItemStatus.DRAFT:
            return {ObjectAction.APPROVE, ObjectAction.EDIT}
        if self._item_metadata.status == LibraryItemStatus.FINAL:
            return {ObjectAction.NEWVERSION, ObjectAction.INACTIVATE}
        if self._item_metadata.status == LibraryItemStatus.RETIRED:
            return {ObjectAction.REACTIVATE}
        return frozenset()
