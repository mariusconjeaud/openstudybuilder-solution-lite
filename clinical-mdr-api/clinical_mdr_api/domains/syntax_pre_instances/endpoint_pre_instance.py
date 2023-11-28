from dataclasses import dataclass
from typing import Callable, Self

from clinical_mdr_api.domains.controlled_terminologies.ct_term_attributes import (
    CTTermAttributesAR,
)
from clinical_mdr_api.domains.controlled_terminologies.ct_term_name import CTTermNameAR
from clinical_mdr_api.domains.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domains.libraries.object import ParametrizedTemplateVO
from clinical_mdr_api.domains.syntax_pre_instances.pre_instance_ar import PreInstanceAR
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)


@dataclass
class EndpointPreInstanceAR(PreInstanceAR):
    """
    Implementation of EndpointPreInstanceAR. Solely based on Parametrized Template.
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
        template: ParametrizedTemplateVO,
        library: LibraryVO,
        item_metadata: LibraryItemMetadataVO,
        sequence_id: str,
        study_count: int = 0,
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
        )

    @classmethod
    def from_input_values(
        cls,
        author: str,
        library: LibraryVO,
        template: ParametrizedTemplateVO,
        generate_uid_callback: Callable[[], str | None] = (lambda: None),
        next_available_sequence_id_callback: Callable[[str], str | None] = (
            lambda _: None
        ),
        indications: list[DictionaryTermAR] | None = None,
        categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None,
        sub_categories: list[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None,
    ) -> Self:
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        generated_uid = generate_uid_callback()

        ar = cls(
            _uid=generated_uid,
            _sequence_id=next_available_sequence_id_callback(template.template_uid),
            _library=library,
            _template=template,
            _item_metadata=item_metadata,
        )
        ar._indications = indications
        ar._categories = categories
        ar._subcategories = sub_categories

        return ar
