from typing import Callable, Dict, List, Optional, Sequence

from pydantic import Field

from clinical_mdr_api.domain.brand.brand import BrandAR
from clinical_mdr_api.domain.clinical_programme.clinical_programme import (
    ClinicalProgrammeAR,
)
from clinical_mdr_api.domain.concepts.compound import CompoundAR
from clinical_mdr_api.domain.concepts.simple_concepts.lag_time import LagTimeAR
from clinical_mdr_api.domain.concepts.simple_concepts.numeric_value import (
    NumericValueAR,
)
from clinical_mdr_api.domain.controlled_terminology.ct_term_name import CTTermNameAR
from clinical_mdr_api.domain.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domain.dictionaries.dictionary_term_substance import (
    DictionaryTermSubstanceAR,
)
from clinical_mdr_api.domain.project.project import ProjectAR
from clinical_mdr_api.domain.unit_definition.unit_definition import UnitDefinitionAR
from clinical_mdr_api.models import Library, Project
from clinical_mdr_api.models.brand import Brand
from clinical_mdr_api.models.concept import (
    Concept,
    ConceptInput,
    SimpleLagTime,
    SimpleNumericValueWithUnit,
)
from clinical_mdr_api.models.ct_term import SimpleTermModel
from clinical_mdr_api.models.dictionary_term import CompoundSubstance
from clinical_mdr_api.models.utils import BaseModel


class Compound(Concept):
    possible_actions: List[str] = Field(
        ...,
        description=(
            "Holds those actions that can be performed on Compounds. "
            "Actions are: 'approve', 'edit', 'new_version'."
        ),
    )

    analyte_number: Optional[str]
    nnc_short_number: Optional[str]
    nnc_long_number: Optional[str]
    is_sponsor_compound: Optional[bool] = True
    is_name_inn: Optional[bool] = True
    substances: Optional[Sequence[CompoundSubstance]]
    dose_values: Optional[Sequence[SimpleNumericValueWithUnit]]
    strength_values: Optional[Sequence[SimpleNumericValueWithUnit]]
    lag_times: Optional[Sequence[SimpleLagTime]]
    delivery_devices: Optional[Sequence[SimpleTermModel]]
    dispensers: Optional[Sequence[SimpleTermModel]]
    projects: Optional[Sequence[Project]]
    brands: Optional[Sequence[Brand]]
    half_life: Optional[SimpleNumericValueWithUnit]
    dose_frequencies: Optional[Sequence[SimpleTermModel]]
    dosage_forms: Optional[Sequence[SimpleTermModel]]
    routes_of_administration: Optional[Sequence[SimpleTermModel]]

    @classmethod
    def from_compound_ar(
        cls,
        compound_ar: CompoundAR,
        find_term_by_uid: Callable[[str], Optional[CTTermNameAR]],
        find_dictionary_term_by_uid: Callable[[str], Optional[DictionaryTermAR]],
        find_substance_term_by_uid: Callable[
            [str], Optional[DictionaryTermSubstanceAR]
        ],
        find_numeric_value_by_uid: Callable[[str], Optional[NumericValueAR]],
        find_lag_time_by_uid: Callable[[str], Optional[LagTimeAR]],
        find_unit_by_uid: Callable[[str], Optional[UnitDefinitionAR]],
        find_project_by_uid: Callable[[str], Optional[ProjectAR]],
        find_brand_by_uid: Callable[[str], Optional[BrandAR]],
        find_clinical_programme_by_uid: Callable[[str], Optional[ClinicalProgrammeAR]],
    ) -> "Compound":
        return cls(
            uid=compound_ar.uid,
            name=compound_ar.name,
            name_sentence_case=compound_ar.concept_vo.name_sentence_case,
            definition=compound_ar.concept_vo.definition,
            abbreviation=compound_ar.concept_vo.abbreviation,
            dose_values=sorted(
                [
                    SimpleNumericValueWithUnit.from_concept_uid(
                        uid=uid,
                        find_unit_by_uid=find_unit_by_uid,
                        find_numeric_value_by_uid=find_numeric_value_by_uid,
                    )
                    for uid in compound_ar.concept_vo.dose_values_uids
                ],
                key=lambda item: item.value,
            ),
            strength_values=sorted(
                [
                    SimpleNumericValueWithUnit.from_concept_uid(
                        uid=uid,
                        find_unit_by_uid=find_unit_by_uid,
                        find_numeric_value_by_uid=find_numeric_value_by_uid,
                    )
                    for uid in compound_ar.concept_vo.strength_values_uids
                ],
                key=lambda item: item.value,
            ),
            lag_times=sorted(
                [
                    SimpleLagTime.from_concept_uid(
                        uid=uid,
                        find_unit_by_uid=find_unit_by_uid,
                        find_lag_time_by_uid=find_lag_time_by_uid,
                        find_term_by_uid=find_term_by_uid,
                    )
                    for uid in compound_ar.concept_vo.lag_time_uids
                ],
                key=lambda item: item.value,
            ),
            delivery_devices=sorted(
                [
                    SimpleTermModel.from_ct_code(
                        c_code=uid,
                        find_term_by_uid=find_term_by_uid,
                    )
                    for uid in compound_ar.concept_vo.delivery_devices_uids
                ],
                key=lambda item: item.name,
            ),
            dispensers=sorted(
                [
                    SimpleTermModel.from_ct_code(
                        c_code=uid,
                        find_term_by_uid=find_term_by_uid,
                    )
                    for uid in compound_ar.concept_vo.dispensers_uids
                ],
                key=lambda item: item.name,
            ),
            projects=sorted(
                [
                    Project.from_uid(
                        uid=uid,
                        find_by_uid=find_project_by_uid,
                        find_clinical_programme_by_uid=find_clinical_programme_by_uid,
                    )
                    for uid in compound_ar.concept_vo.projects_uids
                ],
                key=lambda item: item.name,
            ),
            brands=sorted(
                [
                    Brand.from_uid(
                        uid=uid,
                        find_by_uid=find_brand_by_uid,
                    )
                    for uid in compound_ar.concept_vo.brands_uids
                ],
                key=lambda item: item.name,
            ),
            half_life=SimpleNumericValueWithUnit.from_concept_uid(
                uid=compound_ar.concept_vo.half_life_uid,
                find_unit_by_uid=find_unit_by_uid,
                find_numeric_value_by_uid=find_numeric_value_by_uid,
            ),
            dose_frequencies=sorted(
                [
                    SimpleTermModel.from_ct_code(
                        c_code=uid,
                        find_term_by_uid=find_term_by_uid,
                    )
                    for uid in compound_ar.concept_vo.dose_frequency_uids
                ],
                key=lambda item: item.name if item.name else "",
            ),
            dosage_forms=sorted(
                [
                    SimpleTermModel.from_ct_code(
                        c_code=uid,
                        find_term_by_uid=find_term_by_uid,
                    )
                    for uid in compound_ar.concept_vo.dosage_form_uids
                ],
                key=lambda item: item.name if item.name else "",
            ),
            routes_of_administration=sorted(
                [
                    SimpleTermModel.from_ct_code(
                        c_code=uid,
                        find_term_by_uid=find_term_by_uid,
                    )
                    for uid in compound_ar.concept_vo.route_of_administration_uids
                ],
                key=lambda item: item.name if item.name else "",
            ),
            analyte_number=compound_ar.concept_vo.analyte_number,
            nnc_short_number=compound_ar.concept_vo.nnc_short_number,
            nnc_long_number=compound_ar.concept_vo.nnc_long_number,
            is_sponsor_compound=compound_ar.concept_vo.is_sponsor_compound,
            is_name_inn=compound_ar.concept_vo.is_name_inn,
            substances=sorted(
                [
                    CompoundSubstance.from_term_uid(
                        uid=unii_uid,
                        find_term_by_uid=find_dictionary_term_by_uid,
                        find_substance_by_uid=find_substance_term_by_uid,
                    )
                    for unii_uid in compound_ar.concept_vo.substance_terms_uids
                ],
                key=lambda item: item.substance_name,
            ),
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
        cls, uid: str, find_by_uid: Callable[[str], Optional[CompoundAR]]
    ) -> Optional["SimpleCompound"]:
        simple_compound_model = None
        if uid is not None:
            compound_ar: CompoundAR = find_by_uid(uid)
            if compound_ar is not None:
                simple_compound_model = cls(uid=uid, name=compound_ar.concept_vo.name)

        return simple_compound_model

    uid: str = Field(..., title="uid", description="")
    name: str = Field(..., title="name", description="")

    @classmethod
    def from_compound_ar(cls, compound_ar: CompoundAR) -> "SimpleCompound":
        return cls(
            uid=compound_ar.uid,
            name=compound_ar.name,
        )


class CompoundCreateInput(ConceptInput):
    analyte_number: Optional[str] = None
    nnc_short_number: Optional[str] = None
    nnc_long_number: Optional[str] = None
    is_sponsor_compound: bool = True
    is_name_inn: bool = True
    substance_terms_uids: Optional[Sequence[str]] = []
    dose_values_uids: Sequence[str] = []
    strength_values_uids: Sequence[str] = []
    lag_times_uids: Sequence[str] = []
    delivery_devices_uids: Sequence[str] = []
    dispensers_uids: Sequence[str] = []
    projects_uids: Sequence[str] = []
    brands_uids: Sequence[str] = []
    dose_frequency_uids: Sequence[str] = []
    dosage_form_uids: Sequence[str] = []
    route_of_administration_uids: Sequence[str] = []
    half_life_uid: Optional[str] = None


class CompoundEditInput(ConceptInput):
    analyte_number: Optional[str]
    nnc_short_number: Optional[str]
    nnc_long_number: Optional[str]
    is_sponsor_compound: Optional[bool]
    is_name_inn: Optional[bool]
    substance_terms_uids: Optional[Sequence[str]] = []
    dose_values_uids: Optional[Sequence[str]] = []
    strength_values_uids: Optional[Sequence[str]] = []
    lag_times_uids: Optional[Sequence[str]] = []
    delivery_devices_uids: Optional[Sequence[str]] = []
    dispensers_uids: Optional[Sequence[str]] = []
    projects_uids: Optional[Sequence[str]] = []
    brands_uids: Optional[Sequence[str]] = []
    half_life_uid: Optional[str]
    dose_frequency_uids: Optional[Sequence[str]] = []
    dosage_form_uids: Optional[Sequence[str]] = []
    route_of_administration_uids: Optional[Sequence[str]] = []
    change_description: str


class CompoundVersion(Compound):
    changes: Dict[str, bool] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective (e.g. name, start_date, ..)."
        ),
    )
