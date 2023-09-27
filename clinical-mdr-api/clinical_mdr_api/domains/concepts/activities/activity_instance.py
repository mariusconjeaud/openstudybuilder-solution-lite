from dataclasses import dataclass
from typing import Callable, Self, Sequence

from clinical_mdr_api import exceptions
from clinical_mdr_api.domains.concepts.activities.activity import ActivityGroupingVO
from clinical_mdr_api.domains.concepts.concept_base import (
    ConceptARBase,
    ConceptVO,
    _ConceptVOType,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)


@dataclass(frozen=True)
class SimpleActivityItemVO:
    uid: str
    name: str | None
    activity_item_class_uid: str | None
    activity_item_class_name: str | None

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        name: str | None,
        activity_item_class_uid: str | None,
        activity_item_class_name: str | None,
    ) -> Self:
        simple_activity_item_vo = cls(
            uid=uid,
            name=name,
            activity_item_class_uid=activity_item_class_uid,
            activity_item_class_name=activity_item_class_name,
        )
        return simple_activity_item_vo


@dataclass(frozen=True)
class ActivityInstanceGroupingVO(ActivityGroupingVO):
    activity_uid: str | None = None


@dataclass(frozen=True)
class ActivityInstanceVO(ConceptVO):
    """
    The ActivityInstanceVO acts as the value object for a single ActivityInstance aggregate
    """

    topic_code: str
    adam_param_code: str
    legacy_description: str | None
    activity_groupings: Sequence[ActivityInstanceGroupingVO]
    activity_instance_class_uid: str
    activity_instance_class_name: str | None
    activity_items: Sequence[SimpleActivityItemVO]

    @classmethod
    def from_repository_values(
        cls,
        name: str,
        name_sentence_case: str,
        definition: str,
        abbreviation: str | None,
        topic_code: str,
        adam_param_code: str,
        legacy_description: str | None,
        activity_groupings: Sequence[ActivityInstanceGroupingVO],
        activity_instance_class_uid: str,
        activity_instance_class_name: str | None,
        activity_items: Sequence[SimpleActivityItemVO],
    ) -> Self:
        activity_instance_vo = cls(
            name=name,
            name_sentence_case=name_sentence_case,
            definition=definition,
            abbreviation=abbreviation,
            is_template_parameter=True,
            activity_instance_class_uid=activity_instance_class_uid,
            activity_instance_class_name=activity_instance_class_name,
            topic_code=topic_code,
            adam_param_code=adam_param_code,
            legacy_description=legacy_description,
            activity_groupings=activity_groupings
            if activity_groupings is not None
            else [],
            activity_items=activity_items if activity_items is not None else [],
        )

        return activity_instance_vo

    def validate(
        self,
        activity_hierarchy_exists_by_uid_callback: Callable[[str], bool],
        activity_subgroup_exists: Callable[[str], bool],
        activity_group_exists: Callable[[str], bool],
        activity_instance_class_exists_by_uid_callback: Callable[[str], bool],
        activity_item_exists_by_uid_callback: Callable[[str], bool],
        concept_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        previous_name: str | None = None,
    ) -> None:
        self.duplication_check(
            [("name", self.name, previous_name)],
            concept_exists_by_callback,
            "Activity Instance",
        )
        for activity_grouping in self.activity_groupings:
            if not activity_hierarchy_exists_by_uid_callback(
                activity_grouping.activity_uid
            ):
                raise exceptions.ValidationException(
                    f"{type(self).__name__} tried to connect to non existing Activity identified by uid "
                    f"({activity_grouping.activity_uid})"
                )
            if not activity_subgroup_exists(activity_grouping.activity_subgroup_uid):
                raise exceptions.ValidationException(
                    f"{type(self).__name__} tried to connect to non existing Activity Sub Group identified by uid "
                    f"({activity_grouping.activity_subgroup_uid})"
                )
            if not activity_group_exists(activity_grouping.activity_group_uid):
                raise exceptions.ValidationException(
                    f"{type(self).__name__} tried to connect to non existing Activity Group identified by uid "
                    f"({activity_grouping.activity_group_uid})"
                )
        for activity_item in self.activity_items:
            if not activity_item_exists_by_uid_callback(activity_item.uid):
                raise exceptions.ValidationException(
                    f"{type(self).__name__} tried to connect to non existing Activity item identified by uid ({activity_item.uid})"
                )
        if not activity_instance_class_exists_by_uid_callback(
            self.activity_instance_class_uid
        ):
            raise exceptions.ValidationException(
                f"ActivityInstanceClass with specified uid ({self.activity_instance_class_uid}) doesn't exist"
            )


@dataclass
class ActivityInstanceAR(ConceptARBase):
    _concept_vo: ActivityInstanceVO

    @property
    def concept_vo(self) -> _ConceptVOType:
        return self._concept_vo

    @property
    def name(self) -> str:
        return self._concept_vo.name

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        concept_vo: _ConceptVOType,
        library: LibraryVO | None,
        item_metadata: LibraryItemMetadataVO,
    ) -> Self:
        activity_ar = cls(
            _uid=uid,
            _concept_vo=concept_vo,
            _item_metadata=item_metadata,
            _library=library,
        )
        return activity_ar

    @classmethod
    def from_input_values(
        cls,
        *,
        author: str,
        concept_vo: _ConceptVOType,
        library: LibraryVO,
        concept_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        activity_hierarchy_exists_by_uid_callback: Callable[[str], bool],
        activity_subgroup_exists: Callable[[str], bool],
        activity_group_exists: Callable[[str], bool],
        activity_instance_class_exists_by_uid_callback: Callable[[str], bool],
        activity_item_exists_by_uid_callback: Callable[[str], bool],
        generate_uid_callback: Callable[[], str | None] = (lambda: None),
    ) -> Self:
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        if not library.is_editable:
            raise exceptions.BusinessLogicException(
                f"The library with the name='{library.name}' does not allow to create objects."
            )

        concept_vo.validate(
            concept_exists_by_callback=concept_exists_by_callback,
            activity_hierarchy_exists_by_uid_callback=activity_hierarchy_exists_by_uid_callback,
            activity_subgroup_exists=activity_subgroup_exists,
            activity_group_exists=activity_group_exists,
            activity_instance_class_exists_by_uid_callback=activity_instance_class_exists_by_uid_callback,
            activity_item_exists_by_uid_callback=activity_item_exists_by_uid_callback,
        )

        activity_ar = cls(
            _uid=generate_uid_callback(),
            _item_metadata=item_metadata,
            _library=library,
            _concept_vo=concept_vo,
        )
        return activity_ar

    def edit_draft(
        self,
        author: str,
        change_description: str | None,
        concept_vo: _ConceptVOType,
        concept_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        activity_item_exists_by_uid_callback: Callable[[str], bool] = None,
        activity_hierarchy_exists_by_uid_callback: Callable[[str], bool] = None,
        activity_subgroup_exists: Callable[[str], bool] = None,
        activity_group_exists: Callable[[str], bool] = None,
        activity_instance_class_exists_by_uid_callback: Callable[[str], bool] = None,
    ) -> None:
        """
        Creates a new draft version for the object.
        """
        concept_vo.validate(
            concept_exists_by_callback=concept_exists_by_callback,
            activity_hierarchy_exists_by_uid_callback=activity_hierarchy_exists_by_uid_callback,
            activity_subgroup_exists=activity_subgroup_exists,
            activity_group_exists=activity_group_exists,
            activity_instance_class_exists_by_uid_callback=activity_instance_class_exists_by_uid_callback,
            activity_item_exists_by_uid_callback=activity_item_exists_by_uid_callback,
            previous_name=self.name,
        )
        if self._concept_vo != concept_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self._concept_vo = concept_vo
