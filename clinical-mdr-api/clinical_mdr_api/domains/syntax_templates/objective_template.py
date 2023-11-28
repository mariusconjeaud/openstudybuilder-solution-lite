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
class ObjectiveTemplateAR(TemplateAggregateRootBase):
    """
    A specific Objective Template AR. It can be used to customize Objective Template
    behavior. Inherits generic template versioning behaviors
    """

    _is_confirmatory_testing: bool | None = None

    _indications: list[DictionaryTermAR] | None = None

    _categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None

    @property
    def is_confirmatory_testing(self) -> bool:
        return self._is_confirmatory_testing

    @property
    def indications(self) -> list[DictionaryTermAR]:
        return self._indications

    @property
    def categories(self) -> list[tuple[CTTermNameAR, CTTermAttributesAR]]:
        return self._categories

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
        is_confirmatory_testing: bool | None = None,
        indications: list[DictionaryTermAR] | None = None,
        categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None,
    ) -> Self:
        return cls(
            _uid=uid,
            _sequence_id=sequence_id,
            _item_metadata=item_metadata,
            _library=library,
            _template=template,
            _is_confirmatory_testing=is_confirmatory_testing,
            _indications=indications,
            _categories=categories,
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
        is_confirmatory_testing: bool | None = None,
        indications: list[DictionaryTermAR] | None = None,
        categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None,
    ) -> Self:
        ar: Self = super().from_input_values(
            author=author,
            template=template,
            library=library,
            generate_uid_callback=generate_uid_callback,
            next_available_sequence_id_callback=next_available_sequence_id_callback,
        )
        ar._is_confirmatory_testing = is_confirmatory_testing
        ar._indications = indications
        ar._categories = categories

        return ar
