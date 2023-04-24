from dataclasses import dataclass
from typing import AbstractSet, Callable, Optional

from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryItemAggregateRootBase,
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
    ObjectAction,
)


@dataclass(frozen=True)
class ActivityItemVO:
    """
    The ActivityItemVO acts as the value object for a single ActivityItemClass value object
    """

    name: str
    activity_item_class_uid: str
    activity_item_class_name: Optional[str]
    ct_term_uid: Optional[str]
    ct_term_name: Optional[str]
    unit_definition_uid: Optional[str]
    unit_definition_name: Optional[str]

    @classmethod
    def from_repository_values(
        cls,
        name: str,
        activity_item_class_uid: str,
        activity_item_class_name: Optional[str],
        ct_term_uid: Optional[str],
        ct_term_name: Optional[str],
        unit_definition_uid: Optional[str],
        unit_definition_name: Optional[str],
    ) -> "ActivityItemVO":
        activity_item_vo = cls(
            name=name,
            activity_item_class_uid=activity_item_class_uid,
            activity_item_class_name=activity_item_class_name,
            ct_term_uid=ct_term_uid,
            ct_term_name=ct_term_name,
            unit_definition_uid=unit_definition_uid,
            unit_definition_name=unit_definition_name,
        )

        return activity_item_vo

    def validate(
        self,
        activity_item_exists_by_name_callback: Callable[[str], bool],
        activity_item_class_exists: Callable[[str], bool],
        ct_term_exists: Callable[[str], bool],
        unit_definition_exists: Callable[[str], bool],
        previous_name: Optional[str] = None,
    ) -> None:
        if (
            activity_item_exists_by_name_callback(self.name)
            and previous_name != self.name
        ):
            raise ValueError(f"ActivityItemVO with name ({self.name}) already exists.")
        if not activity_item_class_exists(self.activity_item_class_uid):
            raise ValueError(
                f"ActivityItemVO tried to connect to non existing ActivityItemClass ({self.activity_item_class_uid})."
            )
        if self.ct_term_uid and not ct_term_exists(self.ct_term_uid):
            raise ValueError(
                f"ActivityItemVO tried to connect to non existing CTTerm ({self.ct_term_uid})."
            )
        if self.unit_definition_uid and not unit_definition_exists(
            self.unit_definition_uid
        ):
            raise ValueError(
                f"ActivityItemVO tried to connect to non existing UnitDefinition ({self.unit_definition_uid})."
            )


@dataclass
class ActivityItemAR(LibraryItemAggregateRootBase):
    """
    An abstract generic activity item aggregate for versioned activity items
    """

    _activity_item_vo: ActivityItemVO

    @property
    def activity_item_vo(self) -> ActivityItemVO:
        return self._activity_item_vo

    @property
    def name(self) -> str:
        return self._activity_item_vo.name

    @activity_item_vo.setter
    def activity_item_vo(self, activity_item_vo: ActivityItemVO):
        self._activity_item_vo = activity_item_vo

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        activity_item_vo: ActivityItemVO,
        library: Optional[LibraryVO],
        item_metadata: LibraryItemMetadataVO,
    ) -> "ActivityItemAR":
        activity_item_class_ar = cls(
            _uid=uid,
            _activity_item_vo=activity_item_vo,
            _item_metadata=item_metadata,
            _library=library,
        )
        return activity_item_class_ar

    @classmethod
    def from_input_values(
        cls,
        *,
        author: str,
        activity_item_vo: ActivityItemVO,
        library: LibraryVO,
        activity_item_exists_by_name_callback: Callable[[str], bool],
        activity_item_class_exists: Callable[[str], bool],
        ct_term_exists: Callable[[str], bool],
        unit_definition_exists: Callable[[str], bool],
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
    ) -> "ActivityItemAR":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)
        if not library.is_editable:
            raise ValueError(
                f"The library with the name='{library.name}' does not allow to create objects."
            )
        activity_item_vo.validate(
            activity_item_class_exists=activity_item_class_exists,
            activity_item_exists_by_name_callback=activity_item_exists_by_name_callback,
            ct_term_exists=ct_term_exists,
            unit_definition_exists=unit_definition_exists,
        )
        activity_item_class_ar = cls(
            _uid=generate_uid_callback(),
            _item_metadata=item_metadata,
            _library=library,
            _activity_item_vo=activity_item_vo,
        )
        return activity_item_class_ar

    def edit_draft(
        self,
        author: str,
        change_description: Optional[str],
        activity_item_vo: ActivityItemVO,
        activity_item_class_exists: Callable[[str], bool],
        activity_item_exists_by_name_callback: Callable[[str], bool],
        ct_term_exists: Callable[[str], bool],
        unit_definition_exists: Callable[[str], bool],
    ) -> None:
        """
        Creates a new draft version for the object.
        """

        activity_item_vo.validate(
            activity_item_class_exists=activity_item_class_exists,
            activity_item_exists_by_name_callback=activity_item_exists_by_name_callback,
            ct_term_exists=ct_term_exists,
            unit_definition_exists=unit_definition_exists,
            previous_name=self.name,
        )
        if self._activity_item_vo != activity_item_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self.activity_item_vo = activity_item_vo

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
