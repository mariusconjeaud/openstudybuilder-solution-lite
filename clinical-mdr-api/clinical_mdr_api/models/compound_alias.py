from typing import Callable, Dict, List, Optional

from pydantic import Field

from clinical_mdr_api.domain.concepts.compound import CompoundAR
from clinical_mdr_api.domain.concepts.compound_alias import CompoundAliasAR
from clinical_mdr_api.models import Library
from clinical_mdr_api.models.compound import SimpleCompound
from clinical_mdr_api.models.concept import Concept, ConceptInput


class CompoundAlias(Concept):
    possible_actions: List[str] = Field(
        ...,
        description=(
            "Holds those actions that can be performed on CompoundAliass. "
            "Actions are: 'approve', 'edit', 'new_version'."
        ),
    )

    compound: SimpleCompound
    is_preferred_synonym: bool = False

    @classmethod
    def from_ar(
        cls,
        ar: CompoundAliasAR,
        find_compound_by_uid: Callable[[str], Optional[CompoundAR]],
    ) -> "CompoundAlias":
        return cls(
            uid=ar.uid,
            name=ar.name,
            name_sentence_case=ar.concept_vo.name_sentence_case,
            definition=ar.concept_vo.definition,
            abbreviation=ar.concept_vo.abbreviation,
            compound=SimpleCompound.from_uid(
                ar.concept_vo.compound_uid, find_by_uid=find_compound_by_uid
            ),
            is_preferred_synonym=ar.concept_vo.is_preferred_synonym
            if ar.concept_vo.is_preferred_synonym
            else False,
            library_name=Library.from_library_vo(ar.library).name,
            start_date=ar.item_metadata.start_date,
            end_date=ar.item_metadata.end_date,
            status=ar.item_metadata.status.value,
            version=ar.item_metadata.version,
            change_description=ar.item_metadata.change_description,
            user_initials=ar.item_metadata.user_initials,
            possible_actions=sorted([_.value for _ in ar.get_possible_actions()]),
        )


class CompoundAliasCreateInput(ConceptInput):
    compound_uid: str
    is_preferred_synonym: bool = False


class CompoundAliasEditInput(ConceptInput):
    compound_uid: str
    is_preferred_synonym: bool = False
    change_description: str


class CompoundAliasVersion(CompoundAlias):
    changes: Dict[str, bool] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective (e.g. name, start_date, ..)."
        ),
    )
