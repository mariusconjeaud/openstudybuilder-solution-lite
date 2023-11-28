from dataclasses import dataclass
from typing import Callable, Self

from clinical_mdr_api.domains.controlled_terminologies.ct_term_attributes import (
    CTTermAttributesAR,
)
from clinical_mdr_api.domains.controlled_terminologies.ct_term_name import CTTermNameAR
from clinical_mdr_api.domains.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domains.syntax_templates.template import (
    InstantiationCountsVO,
    TemplateAggregateRootBase,
    TemplateVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)


@dataclass
class EndpointTemplateAR(TemplateAggregateRootBase):
    """
    A specific Endpoint Template AR. It can be used to customize Endpoint Template
    behavior. Inherits generic template versioning behaviors
    """

    _indications: list[DictionaryTermAR] | None = None

    _categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None

    _subcategories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None

    @property
    def indications(self) -> list[DictionaryTermAR]:
        return self._indications

    @property
    def categories(self) -> list[tuple[CTTermNameAR, CTTermAttributesAR]]:
        return self._categories

    @property
    def sub_categories(self) -> list[tuple[CTTermNameAR, CTTermAttributesAR]]:
        return self._subcategories

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        sequence_id: str,
        template: TemplateVO,
        library: LibraryVO,
        item_metadata: LibraryItemMetadataVO,
        study_count: int = 0,
        counts: InstantiationCountsVO | None = None,
        indications: list[DictionaryTermAR] | None = None,
        categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None,
        sub_categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None,
    ) -> Self:
        return cls(
            _uid=uid,
            _sequence_id=sequence_id,
            _item_metadata=item_metadata,
            _library=library,
            _template=template,
            _indications=indications,
            _categories=categories,
            _subcategories=sub_categories,
            _study_count=study_count,
            _counts=counts,
        )

    @classmethod
    def from_input_values(
        cls,
        *,
        author: str,
        template: TemplateVO,
        library: LibraryVO,
        generate_uid_callback: Callable[[], str | None] = (lambda: None),
        next_available_sequence_id_callback: Callable[
            [str, LibraryVO | None], str | None
        ] = lambda uid, library: None,
        indications: list[DictionaryTermAR] | None = None,
        categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None,
        sub_categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None,
    ) -> Self:
        ar: Self = super().from_input_values(
            author=author,
            template=template,
            library=library,
            generate_uid_callback=generate_uid_callback,
            next_available_sequence_id_callback=next_available_sequence_id_callback,
        )
        ar._indications = indications
        ar._categories = categories
        ar._subcategories = sub_categories

        return ar
