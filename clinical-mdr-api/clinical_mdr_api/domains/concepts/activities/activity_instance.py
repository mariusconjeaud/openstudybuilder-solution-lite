from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from clinical_mdr_api.domains.concepts.concept_base import (
    ConceptARBase,
    ConceptVO,
    _AggregateRootType,
    _ConceptVOType,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)


@dataclass(frozen=True)
class SimpleActivityItemVO:
    uid: str
    name: Optional[str]
    activity_item_class_uid: Optional[str]
    activity_item_class_name: Optional[str]

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        name: Optional[str],
        activity_item_class_uid: Optional[str],
        activity_item_class_name: Optional[str],
    ) -> "SimpleActivityItemVO":
        simple_activity_item_vo = cls(
            uid=uid,
            name=name,
            activity_item_class_uid=activity_item_class_uid,
            activity_item_class_name=activity_item_class_name,
        )
        return simple_activity_item_vo


@dataclass(frozen=True)
class ActivityInstanceVO(ConceptVO):
    """
    The ActivityInstanceVO acts as the value object for a single ActivityInstance aggregate
    """

    topic_code: str
    adam_param_code: str
    legacy_description: Optional[str]
    activity_uids: Sequence[str]
    activity_instance_class_uid: str
    activity_instance_class_name: Optional[str]
    activity_items: Sequence[SimpleActivityItemVO]

    @classmethod
    def from_repository_values(
        cls,
        name: str,
        name_sentence_case: str,
        definition: str,
        abbreviation: Optional[str],
        topic_code: str,
        adam_param_code: str,
        legacy_description: Optional[str],
        activity_uids: Sequence[str],
        activity_instance_class_uid: str,
        activity_instance_class_name: Optional[str],
        activity_items: Sequence[SimpleActivityItemVO],
    ) -> "ActivityInstanceVO":
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
            activity_uids=activity_uids if activity_uids is not None else [],
            activity_items=activity_items if activity_items is not None else [],
        )

        return activity_instance_vo

    def validate(
        self,
        activity_hierarchy_exists_by_uid_callback: Callable[[str], bool],
        activity_instance_class_exists_by_uid_callback: Callable[[str], bool],
        activity_item_exists_by_uid_callback: Callable[[str], bool],
        activity_exists_by_name_callback: Callable[[str], bool] = None,
        previous_name: Optional[str] = None,
    ) -> None:
        if activity_exists_by_name_callback(self.name) and self.name != previous_name:
            raise ValueError(
                f"{type(self).__name__} with name ({self.name}) already exists"
            )

        for activity in self.activity_uids:
            if not activity_hierarchy_exists_by_uid_callback(activity):
                raise ValueError(
                    f"{type(self).__name__} tried to connect to non existing Activity identified by uid ({activity})"
                )
        for activity_item in self.activity_items:
            if not activity_item_exists_by_uid_callback(activity_item.uid):
                raise ValueError(
                    f"{type(self).__name__} tried to connect to non existing Activity item identified by uid ({activity_item.uid})"
                )
        if not activity_instance_class_exists_by_uid_callback(
            self.activity_instance_class_uid
        ):
            raise ValueError(
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
        library: Optional[LibraryVO],
        item_metadata: LibraryItemMetadataVO,
    ) -> _AggregateRootType:
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
        concept_exists_by_name_callback: Callable[[str], bool],
        activity_hierarchy_exists_by_uid_callback: Callable[[str], bool],
        activity_instance_class_exists_by_uid_callback: Callable[[str], bool],
        activity_item_exists_by_uid_callback: Callable[[str], bool],
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
    ) -> _AggregateRootType:
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        if not library.is_editable:
            raise ValueError(
                f"The library with the name='{library.name}' does not allow to create objects."
            )

        concept_vo.validate(
            activity_exists_by_name_callback=concept_exists_by_name_callback,
            activity_hierarchy_exists_by_uid_callback=activity_hierarchy_exists_by_uid_callback,
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
        change_description: Optional[str],
        concept_vo: _ConceptVOType,
        concept_exists_by_name_callback: Callable[[str], bool],
        activity_item_exists_by_uid_callback: Callable[[str], bool] = None,
        activity_hierarchy_exists_by_uid_callback: Callable[[str], bool] = None,
        activity_instance_class_exists_by_uid_callback: Callable[[str], bool] = None,
    ) -> None:
        """
        Creates a new draft version for the object.
        """
        concept_vo.validate(
            activity_exists_by_name_callback=concept_exists_by_name_callback,
            activity_hierarchy_exists_by_uid_callback=activity_hierarchy_exists_by_uid_callback,
            activity_instance_class_exists_by_uid_callback=activity_instance_class_exists_by_uid_callback,
            activity_item_exists_by_uid_callback=activity_item_exists_by_uid_callback,
            previous_name=self.name,
        )
        if self._concept_vo != concept_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self._concept_vo = concept_vo
