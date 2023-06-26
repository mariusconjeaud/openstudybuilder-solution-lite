from dataclasses import dataclass
from datetime import date
from typing import Callable, List, Optional

from clinical_mdr_api.domains.concepts.concept_base import ConceptVO
from clinical_mdr_api.domains.concepts.odms.odm_ar_base import OdmARBase
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)
from clinical_mdr_api.exceptions import BusinessLogicException


@dataclass(frozen=True)
class OdmStudyEventVO(ConceptVO):
    oid: Optional[str]
    effective_date: Optional[date]
    retired_date: Optional[date]
    description: Optional[str]
    display_in_tree: bool
    form_uids: List[str]

    @classmethod
    def from_repository_values(
        cls,
        name: str,
        oid: Optional[str],
        effective_date: Optional[date],
        retired_date: Optional[date],
        description: Optional[str],
        display_in_tree: bool,
        form_uids: List[str],
    ) -> "OdmStudyEventVO":
        return cls(
            name=name,
            oid=oid,
            effective_date=effective_date,
            retired_date=retired_date,
            description=description,
            display_in_tree=display_in_tree,
            form_uids=form_uids,
            name_sentence_case=None,
            definition=None,
            abbreviation=None,
            is_template_parameter=False,
        )

    def validate(
        self,
        concept_exists_by_callback: Callable[[str, str], bool],
        previous_name: Optional[str] = None,
        previous_oid: Optional[str] = None,
    ) -> None:
        if concept_exists_by_callback("name", self.name) and previous_name != self.name:
            raise BusinessLogicException(
                f"ODM Study Event with name ({self.name}) already exists."
            )

        if (
            self.oid
            and concept_exists_by_callback("oid", self.oid)
            and previous_oid != self.oid
        ):
            raise BusinessLogicException(
                f"ODM Study Event with OID ({self.oid}) already exists."
            )


@dataclass
class OdmStudyEventAR(OdmARBase):
    _concept_vo: OdmStudyEventVO

    @property
    def name(self) -> str:
        return self._concept_vo.name

    @property
    def concept_vo(self) -> OdmStudyEventVO:
        return self._concept_vo

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        concept_vo: OdmStudyEventVO,
        library: Optional[LibraryVO],
        item_metadata: LibraryItemMetadataVO,
    ) -> "OdmStudyEventAR":
        return cls(
            _uid=uid,
            _concept_vo=concept_vo,
            _library=library,
            _item_metadata=item_metadata,
        )

    @classmethod
    def from_input_values(
        cls,
        author: str,
        concept_vo: OdmStudyEventVO,
        library: LibraryVO,
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
        concept_exists_by_callback: Callable[[str, str], bool] = lambda x, y: True,
    ) -> "OdmStudyEventAR":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        concept_vo.validate(
            concept_exists_by_callback=concept_exists_by_callback,
        )

        return cls(
            _uid=generate_uid_callback(),
            _item_metadata=item_metadata,
            _library=library,
            _concept_vo=concept_vo,
        )

    def edit_draft(
        self,
        author: str,
        change_description: Optional[str],
        concept_vo: OdmStudyEventVO,
        concept_exists_by_name_callback: Callable[[str], bool] = lambda _: True,
        concept_exists_by_callback: Callable[[str, str], bool] = lambda x, y: True,
    ) -> None:
        """
        Creates a new draft version for the object.
        """
        concept_vo.validate(
            concept_exists_by_callback=concept_exists_by_callback,
            previous_name=self.name,
            previous_oid=self._concept_vo.oid,
        )

        if self._concept_vo != concept_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self._concept_vo = concept_vo
