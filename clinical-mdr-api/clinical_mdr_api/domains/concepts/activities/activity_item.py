from dataclasses import dataclass
from typing import Callable, Self

from pydantic import BaseModel

from clinical_mdr_api import exceptions


class LibraryItem(BaseModel):
    uid: str
    name: str | None


@dataclass(frozen=True)
class ActivityItemVO:
    """
    The ActivityItemVO acts as the value object for a single ActivityItem value object
    """

    activity_item_class_uid: str
    activity_item_class_name: str | None
    ct_terms: list[LibraryItem]
    unit_definitions: list[LibraryItem]

    @classmethod
    def from_repository_values(
        cls,
        activity_item_class_uid: str,
        activity_item_class_name: str | None,
        ct_terms: list[dict[str, str]],
        unit_definitions=list[dict[str, str]],
    ) -> Self:
        activity_item_vo = cls(
            activity_item_class_uid=activity_item_class_uid,
            activity_item_class_name=activity_item_class_name,
            ct_terms=ct_terms,
            unit_definitions=unit_definitions,
        )

        return activity_item_vo

    def validate(
        self,
        activity_item_class_exists: Callable[[str], bool],
        ct_term_exists: Callable[[str], bool],
        unit_definition_exists: Callable[[str], bool],
    ) -> None:
        if not activity_item_class_exists(self.activity_item_class_uid):
            raise exceptions.ValidationException(
                f"ActivityItemVO tried to connect to non existing ActivityItemClass ({self.activity_item_class_uid})."
            )
        for term in self.ct_terms:
            if not ct_term_exists(term.uid):
                raise exceptions.ValidationException(
                    f"ActivityItemVO tried to connect to non existing CTTerm ({term.uid})."
                )
        for unit in self.unit_definitions:
            if not unit_definition_exists(unit.uid):
                raise exceptions.ValidationException(
                    f"ActivityItemVO tried to connect to non existing UnitDefinition ({unit.uid})."
                )


@dataclass
class ActivityItemAR:
    """
    An abstract generic activity item aggregate for versioned activity items
    """

    _activity_item_vo: ActivityItemVO

    @property
    def activity_item_vo(self) -> ActivityItemVO:
        return self._activity_item_vo

    @property
    def name(self) -> str:
        return ""

    @activity_item_vo.setter
    def activity_item_vo(self, activity_item_vo: ActivityItemVO):
        self._activity_item_vo = activity_item_vo

    @classmethod
    def from_repository_values(
        cls,
        activity_item_vo: ActivityItemVO,
    ) -> Self:
        activity_item_class_ar = cls(
            _activity_item_vo=activity_item_vo,
        )
        return activity_item_class_ar

    @classmethod
    def from_input_values(
        cls,
        *,
        activity_item_vo: ActivityItemVO,
        activity_item_class_exists: Callable[[str], bool],
        ct_term_exists: Callable[[str], bool],
        unit_definition_exists: Callable[[str], bool],
    ) -> Self:
        activity_item_vo.validate(
            activity_item_class_exists=activity_item_class_exists,
            ct_term_exists=ct_term_exists,
            unit_definition_exists=unit_definition_exists,
        )
        activity_item_class_ar = cls(
            _activity_item_vo=activity_item_vo,
        )
        return activity_item_class_ar
