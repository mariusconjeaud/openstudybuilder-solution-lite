from dataclasses import dataclass
from typing import Callable, Self, Sequence

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
class ObjectivePreInstanceAR(PreInstanceAR):
    """
    Implementation of ObjectivePreInstanceAR. Solely based on Parametrized Template.
    """

    _is_confirmatory_testing: bool | None = None

    _indications: Sequence[DictionaryTermAR] | None = None

    _categories: Sequence[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None

    @property
    def is_confirmatory_testing(self) -> bool:
        return self._is_confirmatory_testing

    @property
    def indications(self) -> Sequence[DictionaryTermAR]:
        return self._indications

    @property
    def categories(self) -> Sequence[tuple[CTTermNameAR, CTTermAttributesAR]]:
        return self._categories

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        template: ParametrizedTemplateVO,
        library: LibraryVO,
        item_metadata: LibraryItemMetadataVO,
        sequence_id: str,
        study_count: int = 0,
        is_confirmatory_testing: bool | None = None,
        indications: Sequence[DictionaryTermAR] | None = None,
        categories: Sequence[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None,
    ) -> Self:
        ar = cls(
            _uid=uid,
            _sequence_id=sequence_id,
            _item_metadata=item_metadata,
            _library=library,
            _template=template,
            _is_confirmatory_testing=is_confirmatory_testing,
            _indications=indications,
            _categories=categories,
            _study_count=study_count,
        )

        return ar

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
        is_confirmatory_testing: bool | None = None,
        indications: Sequence[DictionaryTermAR] | None = None,
        categories: Sequence[tuple[CTTermNameAR, CTTermAttributesAR]] | None = None,
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
        ar._is_confirmatory_testing = is_confirmatory_testing
        ar._indications = indications
        ar._categories = categories

        return ar
