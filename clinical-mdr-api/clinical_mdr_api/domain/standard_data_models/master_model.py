import datetime
from dataclasses import dataclass
from typing import AbstractSet, Optional, Tuple

from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryItemAggregateRootBase,
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
    ObjectAction,
)


@dataclass(frozen=True)
class MasterModelVO:
    """
    The MasterModelVO acts as the value object for a single MasterModel value object
    """

    ig_uid: str
    ig_version_number: str
    version_number: str

    name: str

    @classmethod
    def from_repository_values(
        cls,
        ig_uid: str,
        ig_version_number: str,
        name: str,
        version_number: Optional[str],
    ) -> "MasterModelVO":
        master_model_vo = cls(
            ig_uid=ig_uid,
            ig_version_number=ig_version_number,
            version_number=version_number,
            name=name,
        )

        return master_model_vo


class MasterModelMetadataVO(LibraryItemMetadataVO):
    @property
    def version(self) -> str:
        return self._major_version

    @classmethod
    def get_initial_item_metadata(
        cls, author: str, version: str
    ) -> "MasterModelMetadataVO":
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
        MasterModel only have a major version, updated when a new version is created.
        """
        v_major = self._major_version

        return v_major, 0


@dataclass
class MasterModelAR(LibraryItemAggregateRootBase):
    """
    An abstract generic master model aggregate for versioned master models
    """

    _master_model_vo: MasterModelVO

    @property
    def master_model_vo(self) -> MasterModelVO:
        return self._master_model_vo

    @property
    def name(self) -> str:
        return self._master_model_vo.name

    def _is_edit_allowed_in_non_editable_library(self) -> bool:
        return True

    @master_model_vo.setter
    def master_model_vo(self, master_model_vo: MasterModelVO):
        self._master_model_vo = master_model_vo

    @classmethod
    def from_repository_values(
        cls,
        ig_uid: str,
        master_model_vo: MasterModelVO,
        library: Optional[LibraryVO],
        item_metadata: MasterModelMetadataVO,
    ) -> "MasterModelAR":
        master_model_ar = cls(
            _uid=ig_uid,
            _master_model_vo=master_model_vo,
            _item_metadata=item_metadata,
            _library=library,
        )
        return master_model_ar

    @classmethod
    def from_input_values(
        cls,
        *,
        author: str,
        master_model_vo: MasterModelVO,
        library: LibraryVO,
    ) -> "MasterModelAR":
        item_metadata = MasterModelMetadataVO.get_initial_item_metadata(
            author=author, version=master_model_vo.version_number
        )

        master_model_ar = cls(
            _uid=master_model_vo.ig_uid,
            _item_metadata=item_metadata,
            _library=library,
            _master_model_vo=master_model_vo,
        )
        return master_model_ar

    def edit_draft(
        self,
        author: str,
        change_description: Optional[str],
        master_model_vo: MasterModelVO,
    ) -> None:
        """
        Creates a new draft version for the object.
        """

        if self._master_model_vo != master_model_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self.master_model_vo = master_model_vo

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
