import datetime
from dataclasses import dataclass
from typing import AbstractSet, Optional, Sequence, Tuple

from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryItemAggregateRootBase,
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
    ObjectAction,
)


@dataclass(frozen=True)
class MasterModelDatasetVO:
    """
    The MasterModelDatasetVO acts as the value object for a single MasterModelDataset value object
    """

    master_model_name: str
    master_model_version_number: str
    dataset_uid: str

    description: str
    is_basic_std: bool
    xml_path: str
    xml_title: str
    structure: str
    purpose: str
    comment: str
    ig_comment: str
    map_domain_flag: bool
    suppl_qual_flag: bool
    include_in_raw: bool
    gen_raw_seqno_flag: bool
    enrich_build_order: int
    keys: Sequence[str]
    sort_keys: Sequence[str]
    activity_instance_class_uid: str

    @classmethod
    def from_repository_values(
        cls,
        master_model_name: str,
        master_model_version_number: int,
        dataset_uid: str,
        description: str,
        is_basic_std: bool,
        xml_path: str,
        xml_title: str,
        structure: str,
        purpose: str,
        keys: Sequence[str],
        sort_keys: Sequence[str],
        comment: str,
        ig_comment: str,
        map_domain_flag: bool,
        suppl_qual_flag: bool,
        include_in_raw: bool,
        gen_raw_seqno_flag: bool,
        enrich_build_order: int,
        activity_instance_class_uid: str,
    ) -> "MasterModelDatasetVO":
        master_model_dataset_vo = cls(
            master_model_name=master_model_name,
            master_model_version_number=master_model_version_number,
            dataset_uid=dataset_uid,
            description=description,
            is_basic_std=is_basic_std,
            xml_path=xml_path,
            xml_title=xml_title,
            structure=structure,
            purpose=purpose,
            keys=keys,
            sort_keys=sort_keys,
            comment=comment,
            ig_comment=ig_comment,
            map_domain_flag=map_domain_flag,
            suppl_qual_flag=suppl_qual_flag,
            include_in_raw=include_in_raw,
            gen_raw_seqno_flag=gen_raw_seqno_flag,
            enrich_build_order=enrich_build_order,
            activity_instance_class_uid=activity_instance_class_uid,
        )

        return master_model_dataset_vo


class MasterModelDatasetMetadataVO(LibraryItemMetadataVO):
    @property
    def version(self) -> str:
        return self._major_version

    @classmethod
    def get_initial_item_metadata(
        cls, author: str, version: str
    ) -> "MasterModelDatasetMetadataVO":
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
        MasterModelDataset only have a major version, updated when a new version is created.
        """
        v_major = self._major_version

        return v_major, 0


@dataclass
class MasterModelDatasetAR(LibraryItemAggregateRootBase):
    """
    An abstract generic master model dataset aggregate for versioned master models
    """

    _master_model_dataset_vo: MasterModelDatasetVO

    @property
    def master_model_dataset_vo(self) -> MasterModelDatasetVO:
        return self._master_model_dataset_vo

    @property
    def name(self) -> str:
        return self._uid

    def _is_edit_allowed_in_non_editable_library(self) -> bool:
        return True

    @master_model_dataset_vo.setter
    def master_model_dataset_vo(self, master_model_dataset_vo: MasterModelDatasetVO):
        self._master_model_dataset_vo = master_model_dataset_vo

    @classmethod
    def from_repository_values(
        cls,
        dataset_uid: str,
        master_model_dataset_vo: MasterModelDatasetVO,
        library: Optional[LibraryVO],
        item_metadata: MasterModelDatasetMetadataVO,
    ) -> "MasterModelDatasetAR":
        master_model_dataset_ar = cls(
            _uid=dataset_uid,
            _master_model_dataset_vo=master_model_dataset_vo,
            _item_metadata=item_metadata,
            _library=library,
        )
        return master_model_dataset_ar

    @classmethod
    def from_input_values(
        cls,
        *,
        author: str,
        master_model_dataset_vo: MasterModelDatasetVO,
        library: LibraryVO,
    ) -> "MasterModelDatasetAR":
        item_metadata = MasterModelDatasetMetadataVO.get_initial_item_metadata(
            author=author, version=master_model_dataset_vo.master_model_version_number
        )

        master_model_dataset_ar = cls(
            _uid=master_model_dataset_vo.dataset_uid,
            _item_metadata=item_metadata,
            _library=library,
            _master_model_dataset_vo=master_model_dataset_vo,
        )
        return master_model_dataset_ar

    def edit_draft(
        self,
        author: str,
        change_description: Optional[str],
        master_model_dataset_vo: MasterModelDatasetVO,
    ) -> None:
        """
        Creates a new draft version for the object.
        """

        if self._master_model_dataset_vo != master_model_dataset_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self.master_model_dataset_vo = master_model_dataset_vo

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
