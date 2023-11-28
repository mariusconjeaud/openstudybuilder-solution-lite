import re
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
class CriteriaTemplateAR(TemplateAggregateRootBase):
    """
    A specific Criteria Template AR. It can be used to customize Criteria Template
    behavior. Inherits generic template versioning behaviors
    """

    _type: tuple[CTTermNameAR, CTTermAttributesAR] = ()

    _indications: list[DictionaryTermAR] | None = None

    _categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None

    _subcategories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None

    @property
    def type(self) -> tuple[CTTermNameAR, CTTermAttributesAR]:
        return self._type

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
        criteria_type: tuple[CTTermNameAR, CTTermAttributesAR] | None = None,
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
            _type=criteria_type,
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
            [str, str | None, str | None, LibraryVO | None], str | None
        ] = (lambda uid, prefix, type_uid, library: None),
        criteria_type: tuple[CTTermNameAR, CTTermAttributesAR] | None = None,
        indications: list[DictionaryTermAR] | None = None,
        categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None,
        sub_categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None,
    ) -> Self:
        criteria_type_name = re.sub(
            "criteria", "", criteria_type[0].name, flags=re.IGNORECASE
        ).title()

        ar: Self = super().from_input_values(
            author=author,
            template=template,
            library=library,
            generate_uid_callback=generate_uid_callback,
        )
        ar._sequence_id = next_available_sequence_id_callback(
            uid=ar._uid,
            prefix="C"
            + "".join([char for char in criteria_type_name if char.isupper()]),
            type_uid=criteria_type[0].uid,
            library=library,
        )
        ar._type = criteria_type
        ar._indications = indications
        ar._categories = categories
        ar._subcategories = sub_categories

        return ar
