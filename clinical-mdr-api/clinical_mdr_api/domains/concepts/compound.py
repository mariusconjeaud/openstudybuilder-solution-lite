from dataclasses import dataclass
from typing import Callable, Self

from clinical_mdr_api import exceptions
from clinical_mdr_api.domains.concepts.concept_base import ConceptARBase, ConceptVO
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)


@dataclass(frozen=True)
class CompoundVO(ConceptVO):
    """
    The CompoundVO acts as the single value object for CompoundAR aggregate.
    """

    is_sponsor_compound: bool = True
    external_id: str | None = None

    @classmethod
    def from_repository_values(
        cls,
        name: str,
        name_sentence_case: str | None,
        definition: str | None,
        abbreviation: str | None,
        is_sponsor_compound: bool,
        external_id: str | None,
    ) -> Self:
        compound_vo = cls(
            name=name,
            name_sentence_case=name_sentence_case,
            definition=definition,
            abbreviation=abbreviation,
            is_template_parameter=True,
            is_sponsor_compound=is_sponsor_compound,
            external_id=external_id,
        )

        return compound_vo

    def validate(
        self,
        uid: str | None,
        compound_uid_by_property_value_callback: Callable[[str, str], str],
    ):
        self.validate_uniqueness(
            lookup_callback=compound_uid_by_property_value_callback,
            uid=uid,
            property_name="name",
            value=self.name,
            error_message=f"Compound with name ({self.name}) already exists",
        )

        self.validate_uniqueness(
            lookup_callback=compound_uid_by_property_value_callback,
            uid=uid,
            property_name="name_sentence_case",
            value=self.name_sentence_case,
            error_message=f"Compound with name sentence case ({self.name_sentence_case}) already exists",
        )

        self.validate_uniqueness(
            lookup_callback=compound_uid_by_property_value_callback,
            uid=uid,
            property_name="external_id",
            value=self.external_id,
            error_message=f"Compound with external_id ({self.external_id}) already exists",
        )


class CompoundAR(ConceptARBase):
    _concept_vo: CompoundVO

    @property
    def concept_vo(self) -> CompoundVO:
        return self._concept_vo

    @property
    def name(self) -> str:
        return self.concept_vo.name

    @classmethod
    def from_input_values(
        cls,
        author: str,
        concept_vo: CompoundVO,
        library: LibraryVO,
        compound_uid_by_property_value_callback: Callable[[str, str], str],
        generate_uid_callback: Callable[[], str | None] = (lambda: None),
    ) -> Self:
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)
        uid = generate_uid_callback()

        if not library.is_editable:
            raise exceptions.BusinessLogicException(
                f"The library with the name='{library.name}' does not allow to create objects."
            )

        concept_vo.validate(
            uid=uid,
            compound_uid_by_property_value_callback=compound_uid_by_property_value_callback,
        )

        compound_ar = cls(
            _uid=uid,
            _item_metadata=item_metadata,
            _library=library,
            _concept_vo=concept_vo,
        )
        return compound_ar

    def edit_draft(
        self,
        author: str,
        change_description: str | None,
        concept_vo: CompoundVO,
        concept_exists_by_callback: Callable[[str, str, bool], bool] | None = None,
        compound_uid_by_property_value_callback: Callable[[str, str], str]
        | None = None,
    ) -> None:
        """
        Creates a new draft version for the object.
        """
        concept_vo.validate(
            self.uid,
            compound_uid_by_property_value_callback=compound_uid_by_property_value_callback,
        )

        if self._concept_vo != concept_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self._concept_vo = concept_vo
