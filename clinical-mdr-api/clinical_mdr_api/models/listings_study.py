from typing import Any, Callable, Optional, Sequence

from pydantic import Field

from clinical_mdr_api.domain.controlled_terminology.ct_term_attributes import (
    CTTermAttributesAR,
)
from clinical_mdr_api.domain.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domain.study_definition_aggregate.registry_identifiers import (
    RegistryIdentifiersVO,
)
from clinical_mdr_api.domain.study_definition_aggregate.study_metadata import (
    HighLevelStudyDesignVO,
    StudyPopulationVO,
)
from clinical_mdr_api.models.study import (
    HighLevelStudyDesignJsonModel,
    RegistryIdentifiersJsonModel,
    StudyPopulationJsonModel,
)
from clinical_mdr_api.models.utils import BaseModel


class SimpleListingCTModel(BaseModel):
    @classmethod
    def from_ct_code(
        cls, ct_uid: str, find_term_by_uid: Callable[[str], Optional[Any]]
    ) -> Optional["SimpleListingCTModel"]:
        simple_listing_ct_model = None
        if ct_uid is not None:
            term = find_term_by_uid(ct_uid)

            if term is not None:
                if hasattr(term, "ct_term_vo"):
                    simple_listing_ct_model = cls(
                        id=getattr(term.ct_term_vo, "concept_id"),
                        code=getattr(term.ct_term_vo, "code_submission_value"),
                        name=getattr(term.ct_term_vo, "name_submission_value"),
                    )
                elif hasattr(term, "dictionary_term_vo"):
                    # library = DictionaryTerm.from_dictionary_term_ar(term).library_name
                    # print("Library: ", library)
                    # if library == "SNOMED":
                    #     simple_listing_ct_model = cls(
                    #     id=getattr(term.dictionary_term_vo, "dictionary_id"),
                    #     name=getattr(term.dictionary_term_vo, "definition"))
                    # else:
                    simple_listing_ct_model = cls(
                        id=getattr(term.dictionary_term_vo, "dictionary_id"),
                        name=getattr(term.dictionary_term_vo, "name"),
                    )
            else:
                simple_listing_ct_model = cls(term_id=ct_uid, name=None)
        else:
            simple_listing_ct_model = None
        return simple_listing_ct_model

    id: Optional[str] = Field(
        None,
        title="concept id: c code for CDISC CT, dictionary id for dictionary codes",
        description="",
    )
    code: Optional[str] = Field(
        None,
        title="code: submission code for CDISC CT, this doesnot exists for dictionary codes",
        description="",
    )

    name: Optional[str] = Field(
        None,
        title="name: submission name for CDISC CT, name for dictionary codes",
        description="",
    )


class RegistryIdentifiersListingModel(RegistryIdentifiersJsonModel):
    class Config:
        title = "Registry identifiers model for listing"
        description = "Registry identifiers model for listing."

    ct_gov_id_null_value_code: Optional[SimpleListingCTModel] = None
    eudract_id_null_value_code: Optional[SimpleListingCTModel] = None
    universal_trial_number_utn_null_value_code: Optional[SimpleListingCTModel] = None
    japanese_trial_registry_id_japic_null_value_code: Optional[
        SimpleListingCTModel
    ] = None
    investigational_new_drug_application_number_ind_null_value_code: Optional[
        SimpleListingCTModel
    ] = None

    @classmethod
    def from_study_registry_identifiers_vo_to_listing(
        cls,
        registry_identifiers_vo: RegistryIdentifiersVO,
        find_term_by_uid: Callable[[str], Optional[CTTermAttributesAR]],
    ) -> "RegistryIdentifiersListingModel":
        return cls(
            ct_gov_id=registry_identifiers_vo.ct_gov_id,
            ct_gov_id_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=registry_identifiers_vo.ct_gov_id_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            eudract_id=registry_identifiers_vo.eudract_id,
            eudract_id_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=registry_identifiers_vo.eudract_id_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            universal_trial_number_utn=registry_identifiers_vo.universal_trial_number_utn,
            universal_trial_number_utn_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=registry_identifiers_vo.universal_trial_number_utn_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            japanese_trial_registry_id_japic=registry_identifiers_vo.japanese_trial_registry_id_japic,
            japanese_trial_registry_id_japic_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=registry_identifiers_vo.japanese_trial_registry_id_japic_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            investigational_new_drug_application_number_ind=registry_identifiers_vo.investigational_new_drug_application_number_ind,
            investigational_new_drug_application_number_ind_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=registry_identifiers_vo.investigational_new_drug_application_number_ind_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
        )


class StudyTypeListingModel(HighLevelStudyDesignJsonModel):
    class Config:
        title = "Study Type model for listing"
        description = "Study Type model for listing"

    study_type_code: Optional[SimpleListingCTModel] = None
    study_type_null_value_code: Optional[SimpleListingCTModel] = None

    trial_types_codes: Optional[Sequence[SimpleListingCTModel]] = None
    trial_types_null_value_code: Optional[SimpleListingCTModel] = None

    trial_phase_code: Optional[SimpleListingCTModel] = None
    trial_phase_null_value_code: Optional[SimpleListingCTModel] = None

    is_extension_trial_null_value_code: Optional[SimpleListingCTModel] = None

    is_adaptive_design_null_value_code: Optional[SimpleListingCTModel] = None

    study_stop_rules_null_value_code: Optional[SimpleListingCTModel] = None

    confirmed_response_minimum_duration: Optional[str] = None
    confirmed_response_minimum_duration_null_value_code: Optional[
        SimpleListingCTModel
    ] = None

    post_auth_indicator_null_value_code: Optional[SimpleListingCTModel] = None

    @classmethod
    def from_high_level_study_design_vo_to_listing(
        cls,
        high_level_study_design_vo: Optional[HighLevelStudyDesignVO],
        find_term_by_uid: Callable[[str], Optional[CTTermAttributesAR]],
    ) -> Optional["StudyTypeListingModel"]:
        if high_level_study_design_vo is None:
            return None
        return cls(
            study_type_code=SimpleListingCTModel.from_ct_code(
                ct_uid=high_level_study_design_vo.study_type_code,
                find_term_by_uid=find_term_by_uid,
            ),
            study_type_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=high_level_study_design_vo.study_type_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_types_codes=[
                SimpleListingCTModel.from_ct_code(
                    ct_uid=trial_type_code, find_term_by_uid=find_term_by_uid
                )
                for trial_type_code in high_level_study_design_vo.trial_type_codes
            ],
            trial_types_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=high_level_study_design_vo.trial_type_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_phase_code=SimpleListingCTModel.from_ct_code(
                ct_uid=high_level_study_design_vo.trial_phase_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_phase_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=high_level_study_design_vo.trial_phase_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            is_extension_trial=high_level_study_design_vo.is_extension_trial,
            is_extension_trial_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=high_level_study_design_vo.is_extension_trial_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            is_adaptive_design=high_level_study_design_vo.is_adaptive_design,
            is_adaptive_design_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=high_level_study_design_vo.is_adaptive_design_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            study_stop_rules=high_level_study_design_vo.study_stop_rules,
            study_stop_rules_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=high_level_study_design_vo.study_stop_rules_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            confirmed_response_minimum_duration=high_level_study_design_vo.confirmed_response_minimum_duration,
            confirmed_response_minimum_duration_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=high_level_study_design_vo.confirmed_response_minimum_duration_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            post_auth_indicator=high_level_study_design_vo.post_auth_indicator,
            post_auth_indicator_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=high_level_study_design_vo.post_auth_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
        )


class StudyPopulationListingModel(StudyPopulationJsonModel):
    class Config:
        title = "Study population model for listing"
        description = "Study population model for listing"

    therapeutic_areas_codes: Optional[Sequence[SimpleListingCTModel]] = None
    therapeutic_areas_null_value_code: Optional[SimpleListingCTModel] = None

    disease_conditions_or_indications_codes: Optional[
        Sequence[SimpleListingCTModel]
    ] = None
    disease_conditions_or_indications_null_value_code: Optional[
        SimpleListingCTModel
    ] = None

    diagnosis_groups_codes: Optional[Sequence[SimpleListingCTModel]] = None
    diagnosis_groups_null_value_code: Optional[SimpleListingCTModel] = None

    sex_of_participants_code: Optional[SimpleListingCTModel] = None
    sex_of_participants_null_value_code: Optional[SimpleListingCTModel] = None

    rare_disease_indicator_null_value_code: Optional[SimpleListingCTModel] = None

    healthy_subject_indicator_null_value_code: Optional[SimpleListingCTModel] = None

    planned_minimum_age_of_subjects: Optional[str] = None
    planned_minimum_age_of_subjects_null_value_code: Optional[
        SimpleListingCTModel
    ] = None

    planned_maximum_age_of_subjects: Optional[str] = None
    planned_maximum_age_of_subjects_null_value_code: Optional[
        SimpleListingCTModel
    ] = None

    stable_disease_minimum_duration: Optional[str] = None
    stable_disease_minimum_duration_null_value_code: Optional[
        SimpleListingCTModel
    ] = None

    pediatric_study_indicator_null_value_code: Optional[SimpleListingCTModel] = None

    pediatric_postmarket_study_indicator_null_value_code: Optional[
        SimpleListingCTModel
    ] = None

    pediatric_investigation_plan_indicator_null_value_code: Optional[
        SimpleListingCTModel
    ] = None

    relapse_criteria_null_value_code: Optional[SimpleListingCTModel] = None

    number_of_expected_subjects_null_value_code: Optional[SimpleListingCTModel] = None

    @classmethod
    def from_study_population_vo_to_listing(
        cls,
        study_population_vo: Optional[StudyPopulationVO],
        find_term_by_uid: Callable[[str], Optional[CTTermAttributesAR]],
        find_dictionary_term_by_uid: Callable[[str], Optional[DictionaryTermAR]],
    ) -> Optional["StudyPopulationListingModel"]:
        if study_population_vo is None:
            return None
        return cls(
            therapeutic_areas_codes=[
                SimpleListingCTModel.from_ct_code(
                    ct_uid=therapeutic_area_code,
                    find_term_by_uid=find_dictionary_term_by_uid,
                )
                for therapeutic_area_code in study_population_vo.therapeutic_area_codes
            ],
            therapeutic_areas_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.therapeutic_area_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            disease_conditions_or_indications_codes=[
                SimpleListingCTModel.from_ct_code(
                    ct_uid=disease_or_indication_code,
                    find_term_by_uid=find_dictionary_term_by_uid,
                )
                for disease_or_indication_code in study_population_vo.disease_condition_or_indication_codes
            ],
            disease_conditions_or_indications_null_value_code=(
                SimpleListingCTModel.from_ct_code(
                    ct_uid=study_population_vo.disease_condition_or_indication_null_value_code,
                    find_term_by_uid=find_term_by_uid,
                )
            ),
            diagnosis_groups_codes=[
                SimpleListingCTModel.from_ct_code(
                    ct_uid=diagnosis_group_code,
                    find_term_by_uid=find_dictionary_term_by_uid,
                )
                for diagnosis_group_code in study_population_vo.diagnosis_group_codes
            ],
            diagnosis_groups_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.diagnosis_group_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            sex_of_participants_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.sex_of_participants_code,
                find_term_by_uid=find_term_by_uid,
            ),
            sex_of_participants_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.sex_of_participants_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            rare_disease_indicator=study_population_vo.rare_disease_indicator,
            rare_disease_indicator_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.rare_disease_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            healthy_subject_indicator=study_population_vo.healthy_subject_indicator,
            healthy_subject_indicator_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.healthy_subject_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            planned_minimum_age_of_subjects=study_population_vo.planned_minimum_age_of_subjects,
            planned_minimum_age_of_subjects_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.planned_minimum_age_of_subjects_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            planned_maximum_age_of_subjects=study_population_vo.planned_maximum_age_of_subjects,
            planned_maximum_age_of_subjects_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.planned_maximum_age_of_subjects_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            stable_disease_minimum_duration=study_population_vo.stable_disease_minimum_duration,
            stable_disease_minimum_duration_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.stable_disease_minimum_duration_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            pediatric_study_indicator=study_population_vo.pediatric_study_indicator,
            pediatric_study_indicator_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.pediatric_study_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            pediatric_postmarket_study_indicator=study_population_vo.pediatric_postmarket_study_indicator,
            pediatric_postmarket_study_indicator_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.pediatric_postmarket_study_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            pediatric_investigation_plan_indicator=study_population_vo.pediatric_investigation_plan_indicator,
            pediatric_investigation_plan_indicator_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.pediatric_investigation_plan_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            relapse_criteria=study_population_vo.relapse_criteria,
            relapse_criteria_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.relapse_criteria_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            number_of_expected_subjects=study_population_vo.number_of_expected_subjects,
            number_of_expected_subjects_null_value_code=SimpleListingCTModel.from_ct_code(
                ct_uid=study_population_vo.number_of_expected_subjects_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
        )
