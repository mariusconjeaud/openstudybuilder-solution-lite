from typing import Callable, Self

from pydantic import Field

from clinical_mdr_api.domains.concepts.compound import CompoundAR
from clinical_mdr_api.models import Library
from clinical_mdr_api.models.concepts.concept import Concept, ConceptInput
from clinical_mdr_api.models.utils import BaseModel


class Compound(Concept):
    possible_actions: list[str] = Field(
        ...,
        description=(
            "Holds those actions that can be performed on Compounds. "
            "Actions are: 'approve', 'edit', 'new_version'."
        ),
    )

    is_sponsor_compound: bool | None = True
    external_id: str | None = None

    @classmethod
    def from_compound_ar(
        cls,
        compound_ar: CompoundAR,
    ) -> Self:
        return cls(
            uid=compound_ar.uid,
            name=compound_ar.name,
            name_sentence_case=compound_ar.concept_vo.name_sentence_case,
            definition=compound_ar.concept_vo.definition,
            abbreviation=compound_ar.concept_vo.abbreviation,
            is_sponsor_compound=compound_ar.concept_vo.is_sponsor_compound,
            external_id=compound_ar.concept_vo.external_id,
            library_name=Library.from_library_vo(compound_ar.library).name,
            start_date=compound_ar.item_metadata.start_date,
            end_date=compound_ar.item_metadata.end_date,
            status=compound_ar.item_metadata.status.value,
            version=compound_ar.item_metadata.version,
            change_description=compound_ar.item_metadata.change_description,
            user_initials=compound_ar.item_metadata.user_initials,
            possible_actions=sorted(
                [_.value for _ in compound_ar.get_possible_actions()]
            ),
        )


class SimpleCompound(BaseModel):
    @classmethod
    def from_uid(
        cls, uid: str, find_by_uid: Callable[[str], CompoundAR | None]
    ) -> Self | None:
        simple_compound_model = None
        if uid is not None:
            compound_ar: CompoundAR = find_by_uid(uid)
            if compound_ar is not None:
                simple_compound_model = cls(uid=uid, name=compound_ar.concept_vo.name)

        return simple_compound_model

    uid: str = Field(..., title="uid", description="")
    name: str = Field(..., title="name", description="")

    @classmethod
    def from_compound_ar(cls, compound_ar: CompoundAR) -> Self:
        return cls(
            uid=compound_ar.uid,
            name=compound_ar.name,
        )


class CompoundCreateInput(ConceptInput):
    is_sponsor_compound: bool = True
    external_id: str | None = None


class CompoundEditInput(ConceptInput):
    is_sponsor_compound: bool | None
    external_id: str | None = None
    change_description: str


class CompoundVersion(Compound):
    changes: dict[str, bool] | None = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective (e.g. name, start_date, ..)."
        ),
        nullable=True,
    )
