from dataclasses import dataclass
from typing import Callable, List, Self

from clinical_mdr_api.domains.concepts.concept_base import (
    ConceptARBase,
    ConceptVO,
    _ConceptVOType,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)
from clinical_mdr_api.exceptions import BusinessLogicException


@dataclass(frozen=True)
class ActivityGroupingVO:
    activity_subgroup_uid: str
    activity_group_uid: str


@dataclass(frozen=True)
class ActivityVO(ConceptVO):
    """
    The ActivityVO acts as the value object for a single Activity aggregate
    """

    activity_groupings: List[ActivityGroupingVO]
    request_rationale: str | None
    replaced_by_activity: str | None

    @classmethod
    def from_repository_values(
        cls,
        name: str,
        name_sentence_case: str | None,
        definition: str | None,
        abbreviation: str | None,
        activity_groupings: List[ActivityGroupingVO],
        request_rationale: str | None,
        replaced_by_activity: str | None = None,
    ) -> Self:
        activity_vo = cls(
            name=name,
            name_sentence_case=name_sentence_case,
            definition=definition,
            abbreviation=abbreviation,
            is_template_parameter=True,
            activity_groupings=activity_groupings,
            request_rationale=request_rationale,
            replaced_by_activity=replaced_by_activity,
        )

        return activity_vo

    def validate(
        self,
        activity_exists_by_name_callback: Callable[[str], bool],
        activity_subgroup_exists: Callable[[str], bool],
        activity_group_exists: Callable[[str], bool],
        previous_name: str | None = None,
    ) -> None:
        ex = activity_exists_by_name_callback(self.name)
        if ex and previous_name != self.name:
            raise BusinessLogicException(
                f"Activity with ['name: {self.name}'] already exists."
            )
        for activity_grouping in self.activity_groupings:
            if not activity_subgroup_exists(activity_grouping.activity_subgroup_uid):
                raise BusinessLogicException(
                    "Activity tried to connect to non existing concepts "
                    f"""[('Concept Name: Activity Subgroup', "uids: {{'{activity_grouping.activity_subgroup_uid}'}}")]."""
                )
            if not activity_group_exists(activity_grouping.activity_group_uid):
                raise BusinessLogicException(
                    "Activity tried to connect to non existing concepts "
                    f"""[('Concept Name: Activity Group', "uids: {{'{activity_grouping.activity_group_uid}'}}")]."""
                )


@dataclass
class ActivityAR(ConceptARBase):
    _concept_vo: ActivityVO

    @property
    def concept_vo(self) -> _ConceptVOType:
        return self._concept_vo

    @property
    def name(self) -> str:
        return self._concept_vo.name

    @classmethod
    def from_input_values(
        cls,
        author: str,
        concept_vo: ActivityVO,
        library: LibraryVO,
        generate_uid_callback: Callable[[], str | None] = (lambda: None),
        concept_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        concept_exists_by_name_callback: Callable[[str], bool] = lambda _: True,
        activity_subgroup_exists: Callable[[str], bool] = lambda _: False,
        activity_group_exists: Callable[[str], bool] = lambda _: False,
    ) -> Self:
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        if not library.is_editable:
            raise BusinessLogicException(
                f"The library with the name='{library.name}' does not allow to create objects."
            )
        concept_vo.validate(
            activity_exists_by_name_callback=concept_exists_by_name_callback,
            activity_subgroup_exists=activity_subgroup_exists,
            activity_group_exists=activity_group_exists,
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
        concept_vo: ActivityVO,
        concept_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        concept_exists_by_name_callback: Callable[[str], bool] = lambda x, y, z: True,
        activity_subgroup_exists: Callable[[str], bool] = None,
        activity_group_exists: Callable[[str], bool] = lambda _: False,
    ) -> None:
        """
        Creates a new draft version for the object.
        """
        concept_vo.validate(
            activity_exists_by_name_callback=concept_exists_by_name_callback,
            activity_subgroup_exists=activity_subgroup_exists,
            activity_group_exists=activity_group_exists,
            previous_name=self.name,
        )
        if self._concept_vo != concept_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self._concept_vo = concept_vo
