from dataclasses import dataclass
from typing import AbstractSet, Callable, List, Optional

from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryItemAggregateRootBase,
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
    ObjectAction,
)


@dataclass(frozen=True)
class ActivityItemClassVO:
    """
    The ActivityItemClassVO acts as the value object for a single ActivityItemClass value object
    """

    name: str
    mandatory: bool
    order: int
    activity_instance_class_uids: List[str]

    @classmethod
    def from_repository_values(
        cls,
        name: str,
        order: int,
        mandatory: bool,
        activity_instance_class_uids: List[str],
    ) -> "ActivityItemClassVO":
        activity_item_class_vo = cls(
            name=name,
            order=order,
            mandatory=mandatory,
            activity_instance_class_uids=activity_instance_class_uids,
        )

        return activity_item_class_vo

    def validate(
        self,
        activity_item_class_exists_by_name_callback: Callable[[str], bool],
        activity_instance_class_exists: Callable[[str], bool],
        previous_name: Optional[str] = None,
    ) -> None:
        if (
            activity_item_class_exists_by_name_callback(self.name)
            and previous_name != self.name
        ):
            raise ValueError(
                f"ActivityItemClass with name ({self.name}) already exists."
            )
        for activity_instance_class_uid in self.activity_instance_class_uids:
            if not activity_instance_class_exists(activity_instance_class_uid):
                raise ValueError(
                    f"ActivityItemClass tried to connect to non existing ActivityItemClass ({activity_instance_class_uid})."
                )


@dataclass
class ActivityItemClassAR(LibraryItemAggregateRootBase):
    """
    An abstract generic activity item aggregate for versioned activity items
    """

    _activity_item_class_vo: ActivityItemClassVO

    @property
    def activity_item_class_vo(self) -> ActivityItemClassVO:
        return self._activity_item_class_vo

    @property
    def name(self) -> str:
        return self._activity_item_class_vo.name

    @activity_item_class_vo.setter
    def activity_item_class_vo(self, activity_item_class_vo: ActivityItemClassVO):
        self._activity_item_class_vo = activity_item_class_vo

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        activity_item_class_vo: ActivityItemClassVO,
        library: Optional[LibraryVO],
        item_metadata: LibraryItemMetadataVO,
    ) -> "ActivityItemClassAR":
        activity_item_class_ar = cls(
            _uid=uid,
            _activity_item_class_vo=activity_item_class_vo,
            _item_metadata=item_metadata,
            _library=library,
        )
        return activity_item_class_ar

    @classmethod
    def from_input_values(
        cls,
        *,
        author: str,
        activity_item_class_vo: ActivityItemClassVO,
        library: LibraryVO,
        activity_instance_class_exists: Callable[[str], bool],
        activity_item_class_exists_by_name_callback: Callable[[str], bool],
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
    ) -> "ActivityItemClassAR":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)
        if not library.is_editable:
            raise ValueError(
                f"The library with the name='{library.name}' does not allow to create objects."
            )
        activity_item_class_vo.validate(
            activity_instance_class_exists=activity_instance_class_exists,
            activity_item_class_exists_by_name_callback=activity_item_class_exists_by_name_callback,
        )
        activity_item_class_ar = cls(
            _uid=generate_uid_callback(),
            _item_metadata=item_metadata,
            _library=library,
            _activity_item_class_vo=activity_item_class_vo,
        )
        return activity_item_class_ar

    def edit_draft(
        self,
        author: str,
        change_description: Optional[str],
        activity_item_class_vo: ActivityItemClassVO,
        activity_instance_class_exists: Callable[[str], bool],
        activity_item_class_exists_by_name_callback: Callable[[str], bool],
    ) -> None:
        """
        Creates a new draft version for the object.
        """

        activity_item_class_vo.validate(
            activity_instance_class_exists=activity_instance_class_exists,
            activity_item_class_exists_by_name_callback=activity_item_class_exists_by_name_callback,
            previous_name=self.name,
        )
        if self._activity_item_class_vo != activity_item_class_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self.activity_item_class_vo = activity_item_class_vo

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
