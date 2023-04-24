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
class ActivityInstanceClassVO:
    """
    The ActivityInstanceClassVO acts as the value object for a single ActivityInstanceClass value object
    """

    parent_uid: Optional[str]
    name: str
    order: Optional[int]
    definition: Optional[str]
    is_domain_specific: Optional[bool]

    @classmethod
    def from_repository_values(
        cls,
        name: str,
        order: Optional[int],
        definition: Optional[str],
        is_domain_specific: Optional[bool],
        parent_uid: Optional[str],
    ) -> "ActivityInstanceClassVO":
        activity_instance_class_vo = cls(
            name=name,
            order=order,
            definition=definition,
            is_domain_specific=is_domain_specific,
            parent_uid=parent_uid,
        )

        return activity_instance_class_vo

    def validate(
        self,
        activity_instance_class_exists_by_name_callback: Callable[[str], bool],
        activity_instance_class_parent_exists: Callable[[str], bool],
        previous_name: Optional[str] = None,
    ) -> None:
        if (
            activity_instance_class_exists_by_name_callback(self.name)
            and previous_name != self.name
        ):
            raise ValueError(
                f"ActivityInstanceClass with name ({self.name}) already exists."
            )
        if self.parent_uid and not activity_instance_class_parent_exists(
            self.parent_uid
        ):
            raise ValueError(
                f"ActivityInstanceClass tried to connect to non existing ActivityInstanceClass ({self.parent_uid})."
            )


@dataclass
class ActivityInstanceClassAR(LibraryItemAggregateRootBase):
    """
    An abstract generic activity item aggregate for versioned activity items
    """

    _activity_instance_class_vo: ActivityInstanceClassVO

    @property
    def activity_instance_class_vo(self) -> ActivityInstanceClassVO:
        return self._activity_instance_class_vo

    @property
    def name(self) -> str:
        return self._activity_instance_class_vo.name

    @activity_instance_class_vo.setter
    def activity_instance_class_vo(
        self, activity_instance_class_vo: ActivityInstanceClassVO
    ):
        self._activity_instance_class_vo = activity_instance_class_vo

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        activity_instance_class_vo: ActivityInstanceClassVO,
        library: Optional[LibraryVO],
        item_metadata: LibraryItemMetadataVO,
    ) -> "ActivityInstanceClassAR":
        activity_instance_class_ar = cls(
            _uid=uid,
            _activity_instance_class_vo=activity_instance_class_vo,
            _item_metadata=item_metadata,
            _library=library,
        )
        return activity_instance_class_ar

    @classmethod
    def from_input_values(
        cls,
        *,
        author: str,
        activity_instance_class_vo: ActivityInstanceClassVO,
        library: LibraryVO,
        activity_instance_class_parent_exists: Callable[[str], bool],
        activity_instance_class_exists_by_name_callback: Callable[[str], bool],
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
    ) -> "ActivityInstanceClassAR":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)
        if not library.is_editable:
            raise ValueError(
                f"The library with the name='{library.name}' does not allow to create objects."
            )
        activity_instance_class_vo.validate(
            activity_instance_class_parent_exists=activity_instance_class_parent_exists,
            activity_instance_class_exists_by_name_callback=activity_instance_class_exists_by_name_callback,
        )
        activity_instance_class_ar = cls(
            _uid=generate_uid_callback(),
            _item_metadata=item_metadata,
            _library=library,
            _activity_instance_class_vo=activity_instance_class_vo,
        )
        return activity_instance_class_ar

    def edit_draft(
        self,
        author: str,
        change_description: Optional[str],
        activity_instance_class_vo: ActivityInstanceClassVO,
        activity_instance_class_parent_exists: Callable[[str], bool],
        activity_instance_class_exists_by_name_callback: Callable[[str], bool],
    ) -> None:
        """
        Creates a new draft version for the object.
        """

        activity_instance_class_vo.validate(
            activity_instance_class_parent_exists=activity_instance_class_parent_exists,
            activity_instance_class_exists_by_name_callback=activity_instance_class_exists_by_name_callback,
            previous_name=self.name,
        )
        if self._activity_instance_class_vo != activity_instance_class_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self.activity_instance_class_vo = activity_instance_class_vo

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
