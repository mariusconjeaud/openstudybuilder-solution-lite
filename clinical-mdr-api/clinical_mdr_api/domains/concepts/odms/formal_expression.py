from dataclasses import dataclass
from typing import Callable, Self

from clinical_mdr_api.domains.concepts.concept_base import ConceptVO
from clinical_mdr_api.domains.concepts.odms.odm_ar_base import OdmARBase
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)
from clinical_mdr_api.exceptions import BusinessLogicException


@dataclass(frozen=True)
class OdmFormalExpressionVO(ConceptVO):
    context: str
    expression: str

    @classmethod
    def from_repository_values(
        cls,
        context: str,
        expression: str,
    ) -> Self:
        return cls(
            context=context,
            expression=expression,
            name=None,
            name_sentence_case=None,
            definition=None,
            abbreviation=None,
            is_template_parameter=False,
        )

    def validate(self, odm_object_exists_callback: Callable) -> None:
        data = {"context": self.context, "expression": self.expression}
        if uids := odm_object_exists_callback(**data):
            raise BusinessLogicException(
                f"ODM Formal Expression already exists with UID ({uids[0]}) and data {data}"
            )


@dataclass
class OdmFormalExpressionAR(OdmARBase):
    _concept_vo: OdmFormalExpressionVO

    @property
    def name(self) -> str:
        return self._concept_vo.name

    @property
    def concept_vo(self) -> OdmFormalExpressionVO:
        return self._concept_vo

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        concept_vo: OdmFormalExpressionVO,
        library: LibraryVO | None,
        item_metadata: LibraryItemMetadataVO,
    ) -> Self:
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
        concept_vo: OdmFormalExpressionVO,
        library: LibraryVO,
        generate_uid_callback: Callable[[], str | None] = (lambda: None),
        odm_object_exists_callback: Callable = lambda _: True,
    ) -> Self:
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        concept_vo.validate(odm_object_exists_callback=odm_object_exists_callback)

        return cls(
            _uid=generate_uid_callback(),
            _item_metadata=item_metadata,
            _library=library,
            _concept_vo=concept_vo,
        )

    def edit_draft(
        self,
        author: str,
        change_description: str | None,
        concept_vo: OdmFormalExpressionVO,
        concept_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        odm_object_exists_callback: Callable = lambda _: True,
    ) -> None:
        """
        Creates a new draft version for the object.
        """
        concept_vo.validate(odm_object_exists_callback=odm_object_exists_callback)
        super()._edit_draft(change_description=change_description, author=author)
        self._concept_vo = concept_vo
