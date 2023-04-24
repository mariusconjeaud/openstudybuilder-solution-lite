from typing import Any, Callable, Optional, Sequence, Union

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
    StudyInterventionVO,
    StudyMetadataVO,
    StudyPopulationVO,
)
from clinical_mdr_api.domain.study_selection.study_design_cell import StudyDesignCellVO
from clinical_mdr_api.domain.study_selection.study_selection_arm import (
    StudySelectionArmAR,
    StudySelectionArmVO,
)
from clinical_mdr_api.domain.study_selection.study_selection_branch_arm import (
    StudySelectionBranchArmAR,
    StudySelectionBranchArmVO,
)
from clinical_mdr_api.domain.study_selection.study_selection_cohort import (
    StudySelectionCohortAR,
    StudySelectionCohortVO,
)
from clinical_mdr_api.domain.study_selection.study_selection_element import (
    StudySelectionElementAR,
    StudySelectionElementVO,
)
from clinical_mdr_api.domain.study_selection.study_visit import StudyVisitVO
from clinical_mdr_api.models.study import (
    HighLevelStudyDesignJsonModel,
    RegistryIdentifiersJsonModel,
    StudyDescriptionJsonModel,
    StudyInterventionJsonModel,
    StudyPopulationJsonModel,
)
from clinical_mdr_api.models.study_epoch import StudyEpoch
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
                        name=getattr(term.ct_term_vo, "code_submission_value"),
                    )
                elif hasattr(term, "dictionary_term_vo"):
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

    name: Optional[str] = Field(
        None,
        title="name: submission name for CDISC CT, name for dictionary codes",
        description="",
    )


def ct_term_uid_to_str(ct_uid: str, find_term_by_uid: Callable[[str], Optional[Any]]):
    if ct_uid is not None:
        term = find_term_by_uid(ct_uid)
        if term is not None:
            if hasattr(term, "ct_term_vo"):
                return getattr(term.ct_term_vo, "code_submission_value")
        else:
            return f"uid: {ct_uid} not found"
    return ""


def none_to_empty_str(obj):
    if obj is None:
        return ""
    return obj


class RegistryIdentifiersListingModel(RegistryIdentifiersJsonModel):
    class Config:
        title = "Registry identifiers model for listing"
        description = "Registry identifiers model for listing."

    ct_gov_id_null_value_code: Optional[str] = None
    eudract_id_null_value_code: Optional[str] = None
    universal_trial_number_utn_null_value_code: Optional[str] = None
    japanese_trial_registry_id_japic_null_value_code: Optional[str] = None
    investigational_new_drug_application_number_ind_null_value_code: Optional[
        str
    ] = None

    @classmethod
    def from_study_registry_identifiers_vo(
        cls,
        registry_identifiers_vo: RegistryIdentifiersVO,
        find_term_by_uid: Callable[[str], Optional[str]],
    ) -> "RegistryIdentifiersListingModel":
        if registry_identifiers_vo is None:
            return None
        return cls(
            ct_gov_id=none_to_empty_str(registry_identifiers_vo.ct_gov_id),
            ct_gov_id_null_value_code=ct_term_uid_to_str(
                registry_identifiers_vo.ct_gov_id_null_value_code, find_term_by_uid
            ),
            eudract_id=none_to_empty_str(registry_identifiers_vo.eudract_id),
            eudract_id_null_value_code=ct_term_uid_to_str(
                registry_identifiers_vo.eudract_id_null_value_code, find_term_by_uid
            ),
            universal_trial_number_utn=none_to_empty_str(
                registry_identifiers_vo.universal_trial_number_utn
            ),
            universal_trial_number_utn_null_value_code=ct_term_uid_to_str(
                registry_identifiers_vo.universal_trial_number_utn_null_value_code,
                find_term_by_uid,
            ),
            japanese_trial_registry_id_japic=none_to_empty_str(
                registry_identifiers_vo.japanese_trial_registry_id_japic
            ),
            japanese_trial_registry_id_japic_null_value_code=ct_term_uid_to_str(
                registry_identifiers_vo.japanese_trial_registry_id_japic_null_value_code,
                find_term_by_uid,
            ),
            investigational_new_drug_application_number_ind=none_to_empty_str(
                registry_identifiers_vo.investigational_new_drug_application_number_ind
            ),
            investigational_new_drug_application_number_ind_null_value_code=ct_term_uid_to_str(
                registry_identifiers_vo.investigational_new_drug_application_number_ind_null_value_code,
                find_term_by_uid,
            ),
        )


class StudyTypeListingModel(HighLevelStudyDesignJsonModel):
    class Config:
        title = "Study type model for listing"
        description = "Study type model for listing"

    study_type_code: Optional[str] = None
    study_type_null_value_code: Optional[str] = None

    trial_type_codes: Optional[Sequence[SimpleListingCTModel]] = None
    trial_type_null_value_code: Optional[str] = None

    trial_phase_code: Optional[str] = None
    trial_phase_null_value_code: Optional[str] = None

    is_extension_trial: Optional[Union[str, bool]] = None
    is_extension_trial_null_value_code: Optional[str] = None

    is_adaptive_design: Optional[Union[str, bool]] = None
    is_adaptive_design_null_value_code: Optional[str] = None

    study_stop_rules_null_value_code: Optional[str] = None

    confirmed_response_minimum_duration: Optional[str] = None
    confirmed_response_minimum_duration_null_value_code: Optional[str] = None

    post_auth_indicator_null_value_code: Optional[str] = None

    @classmethod
    def from_high_level_study_design_vo(
        cls,
        high_level_study_design_vo: Optional[HighLevelStudyDesignVO],
        find_term_by_uid: Callable[[str], Optional[CTTermAttributesAR]],
    ) -> Optional["StudyTypeListingModel"]:
        if high_level_study_design_vo is None:
            return None
        return cls(
            study_type_code=ct_term_uid_to_str(
                ct_uid=high_level_study_design_vo.study_type_code,
                find_term_by_uid=find_term_by_uid,
            ),
            study_type_null_value_code=ct_term_uid_to_str(
                ct_uid=high_level_study_design_vo.study_type_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_type_codes=[
                SimpleListingCTModel.from_ct_code(
                    ct_uid=trial_type_code, find_term_by_uid=find_term_by_uid
                )
                for trial_type_code in high_level_study_design_vo.trial_type_codes
            ],
            trial_type_null_value_code=ct_term_uid_to_str(
                ct_uid=high_level_study_design_vo.trial_type_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_phase_code=ct_term_uid_to_str(
                ct_uid=high_level_study_design_vo.trial_phase_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_phase_null_value_code=ct_term_uid_to_str(
                ct_uid=high_level_study_design_vo.trial_phase_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            is_extension_trial=none_to_empty_str(
                high_level_study_design_vo.is_extension_trial
            ),
            is_extension_trial_null_value_code=ct_term_uid_to_str(
                ct_uid=high_level_study_design_vo.is_extension_trial_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            is_adaptive_design=none_to_empty_str(
                high_level_study_design_vo.is_adaptive_design
            ),
            is_adaptive_design_null_value_code=ct_term_uid_to_str(
                ct_uid=high_level_study_design_vo.is_adaptive_design_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            study_stop_rules=none_to_empty_str(
                high_level_study_design_vo.study_stop_rules
            ),
            study_stop_rules_null_value_code=ct_term_uid_to_str(
                ct_uid=high_level_study_design_vo.study_stop_rules_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            confirmed_response_minimum_duration=none_to_empty_str(
                high_level_study_design_vo.confirmed_response_minimum_duration
            ),
            confirmed_response_minimum_duration_null_value_code=ct_term_uid_to_str(
                ct_uid=high_level_study_design_vo.confirmed_response_minimum_duration_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            post_auth_indicator=none_to_empty_str(
                high_level_study_design_vo.post_auth_indicator
            ),
            post_auth_indicator_null_value_code=ct_term_uid_to_str(
                ct_uid=high_level_study_design_vo.post_auth_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
        )


class StudyPopulationListingModel(StudyPopulationJsonModel):
    class Config:
        title = "Study population model for listing"
        description = "Study population model for listing"

    therapeutic_area_codes: Optional[Sequence[SimpleListingCTModel]] = None
    therapeutic_area_null_value_code: Optional[str] = None

    disease_condition_or_indication_codes: Optional[
        Sequence[SimpleListingCTModel]
    ] = None
    disease_condition_or_indication_null_value_code: Optional[str] = None

    diagnosis_group_codes: Optional[Sequence[SimpleListingCTModel]] = None
    diagnosis_group_null_value_code: Optional[str] = None

    sex_of_participants_code: Optional[str] = None
    sex_of_participants_null_value_code: Optional[str] = None

    rare_disease_indicator: Optional[Union[str, bool]] = None
    rare_disease_indicator_null_value_code: Optional[str] = None

    healthy_subject_indicator: Optional[Union[str, bool]] = None
    healthy_subject_indicator_null_value_code: Optional[str] = None

    planned_minimum_age_of_subjects: Optional[str] = None
    planned_minimum_age_of_subjects_null_value_code: Optional[str] = None

    planned_maximum_age_of_subjects: Optional[str] = None
    planned_maximum_age_of_subjects_null_value_code: Optional[str] = None

    stable_disease_minimum_duration: Optional[str] = None
    stable_disease_minimum_duration_null_value_code: Optional[str] = None

    pediatric_study_indicator: Optional[Union[str, bool]] = None
    pediatric_study_indicator_null_value_code: Optional[str] = None

    pediatric_postmarket_study_indicator: Optional[Union[str, bool]] = None
    pediatric_postmarket_study_indicator_null_value_code: Optional[str] = None

    pediatric_investigation_plan_indicator: Optional[Union[str, bool]] = None
    pediatric_investigation_plan_indicator_null_value_code: Optional[str] = None

    relapse_criteria_null_value_code: Optional[str] = None

    number_of_expected_subjects_null_value_code: Optional[str] = None

    @classmethod
    def from_study_population_vo(
        cls,
        study_population_vo: Optional[StudyPopulationVO],
        find_term_by_uid: Callable[[str], Optional[CTTermAttributesAR]],
        find_dictionary_term_by_uid: Callable[[str], Optional[DictionaryTermAR]],
    ) -> Optional["StudyPopulationListingModel"]:
        if study_population_vo is None:
            return None
        return cls(
            therapeutic_area_codes=[
                SimpleListingCTModel(
                    ct_uid=therapeutic_area_code,
                    find_term_by_uid=find_dictionary_term_by_uid,
                )
                for therapeutic_area_code in study_population_vo.therapeutic_area_codes
            ],
            therapeutic_area_null_value_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.therapeutic_area_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            disease_condition_or_indication_codes=[
                SimpleListingCTModel.from_ct_code(
                    ct_uid=disease_or_indication_code,
                    find_term_by_uid=find_dictionary_term_by_uid,
                )
                for disease_or_indication_code in study_population_vo.disease_condition_or_indication_codes
            ],
            disease_condition_or_indication_null_value_code=(
                ct_term_uid_to_str(
                    ct_uid=study_population_vo.disease_condition_or_indication_null_value_code,
                    find_term_by_uid=find_term_by_uid,
                )
            ),
            diagnosis_group_codes=[
                SimpleListingCTModel.from_ct_code(
                    ct_uid=diagnosis_group_code,
                    find_term_by_uid=find_dictionary_term_by_uid,
                )
                for diagnosis_group_code in study_population_vo.diagnosis_group_codes
            ],
            diagnosis_group_null_value_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.diagnosis_group_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            sex_of_participants_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.sex_of_participants_code,
                find_term_by_uid=find_term_by_uid,
            ),
            sex_of_participants_null_value_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.sex_of_participants_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            rare_disease_indicator=none_to_empty_str(
                study_population_vo.rare_disease_indicator
            ),
            rare_disease_indicator_null_value_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.rare_disease_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            healthy_subject_indicator=none_to_empty_str(
                study_population_vo.healthy_subject_indicator
            ),
            healthy_subject_indicator_null_value_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.healthy_subject_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            planned_minimum_age_of_subjects=none_to_empty_str(
                study_population_vo.planned_minimum_age_of_subjects
            ),
            planned_minimum_age_of_subjects_null_value_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.planned_minimum_age_of_subjects_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            planned_maximum_age_of_subjects=none_to_empty_str(
                study_population_vo.planned_maximum_age_of_subjects
            ),
            planned_maximum_age_of_subjects_null_value_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.planned_maximum_age_of_subjects_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            stable_disease_minimum_duration=none_to_empty_str(
                study_population_vo.stable_disease_minimum_duration
            ),
            stable_disease_minimum_duration_null_value_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.stable_disease_minimum_duration_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            pediatric_study_indicator=none_to_empty_str(
                study_population_vo.pediatric_study_indicator
            ),
            pediatric_study_indicator_null_value_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.pediatric_study_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            pediatric_postmarket_study_indicator=none_to_empty_str(
                study_population_vo.pediatric_postmarket_study_indicator
            ),
            pediatric_postmarket_study_indicator_null_value_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.pediatric_postmarket_study_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            pediatric_investigation_plan_indicator=none_to_empty_str(
                study_population_vo.pediatric_investigation_plan_indicator
            ),
            pediatric_investigation_plan_indicator_null_value_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.pediatric_investigation_plan_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            relapse_criteria=none_to_empty_str(study_population_vo.relapse_criteria),
            relapse_criteria_null_value_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.relapse_criteria_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            number_of_expected_subjects=study_population_vo.number_of_expected_subjects,
            number_of_expected_subjects_null_value_code=ct_term_uid_to_str(
                ct_uid=study_population_vo.number_of_expected_subjects_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
        )


class StudyAttributesListingModel(StudyInterventionJsonModel):
    class Config:
        title = "study attributes model for listing"
        description = "Study attributes model for listing"

    intervention_type_code: Optional[str] = None
    intervention_type_null_value_code: Optional[str] = None

    add_on_to_existing_treatments: Optional[Union[str, bool]] = None
    add_on_to_existing_treatments_null_value_code: Optional[str] = None

    control_type_code: Optional[str] = None
    control_type_null_value_code: Optional[str] = None

    intervention_model_code: Optional[str] = None
    intervention_model_null_value_code: Optional[str] = None

    is_trial_randomised: Optional[Union[str, bool]] = None
    is_trial_randomised_null_value_code: Optional[str] = None

    stratification_factor_null_value_code: Optional[str] = None

    trial_blinding_schema_code: Optional[str] = None
    trial_blinding_schema_null_value_code: Optional[str] = None

    planned_study_length: Optional[str] = None
    planned_study_length_null_value_code: Optional[str] = None

    trial_intent_types_codes: Optional[Sequence[SimpleListingCTModel]] = None
    trial_intent_types_null_value_code: Optional[str] = None

    @classmethod
    def from_study_intervention_vo(
        cls,
        study_intervention_vo: Optional[StudyInterventionVO],
        find_term_by_uid: Callable[[str], Optional[CTTermAttributesAR]],
    ) -> Optional["StudyAttributesListingModel"]:
        if study_intervention_vo is None:
            return None
        return cls(
            intervention_type_code=ct_term_uid_to_str(
                ct_uid=study_intervention_vo.intervention_type_code,
                find_term_by_uid=find_term_by_uid,
            ),
            intervention_type_null_value_code=ct_term_uid_to_str(
                ct_uid=study_intervention_vo.intervention_type_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            add_on_to_existing_treatments=none_to_empty_str(
                study_intervention_vo.add_on_to_existing_treatments
            ),
            add_on_to_existing_treatments_null_value_code=ct_term_uid_to_str(
                ct_uid=study_intervention_vo.add_on_to_existing_treatments_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            control_type_code=ct_term_uid_to_str(
                ct_uid=study_intervention_vo.control_type_code,
                find_term_by_uid=find_term_by_uid,
            ),
            control_type_null_value_code=ct_term_uid_to_str(
                ct_uid=study_intervention_vo.control_type_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            intervention_model_code=ct_term_uid_to_str(
                ct_uid=study_intervention_vo.intervention_model_code,
                find_term_by_uid=find_term_by_uid,
            ),
            intervention_model_null_value_code=ct_term_uid_to_str(
                ct_uid=study_intervention_vo.intervention_model_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            is_trial_randomised=none_to_empty_str(
                study_intervention_vo.is_trial_randomised
            ),
            is_trial_randomised_null_value_code=ct_term_uid_to_str(
                ct_uid=study_intervention_vo.is_trial_randomised_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            stratification_factor=none_to_empty_str(
                study_intervention_vo.stratification_factor
            ),
            stratification_factor_null_value_code=ct_term_uid_to_str(
                ct_uid=study_intervention_vo.stratification_factor_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_blinding_schema_code=ct_term_uid_to_str(
                ct_uid=study_intervention_vo.trial_blinding_schema_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_blinding_schema_null_value_code=ct_term_uid_to_str(
                ct_uid=study_intervention_vo.trial_blinding_schema_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            planned_study_length=none_to_empty_str(
                study_intervention_vo.planned_study_length
            ),
            planned_study_length_null_value_code=ct_term_uid_to_str(
                ct_uid=study_intervention_vo.planned_study_length_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_intent_types_codes=[
                SimpleListingCTModel.from_ct_code(
                    ct_uid=trial_intent_type_code, find_term_by_uid=find_term_by_uid
                )
                for trial_intent_type_code in study_intervention_vo.trial_intent_types_codes
            ],
            trial_intent_types_null_value_code=ct_term_uid_to_str(
                ct_uid=study_intervention_vo.trial_intent_type_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
        )


class StudySelctionListingModel(BaseModel):
    name: str
    short_name: str
    code: Optional[str]
    number_of_subjects: Optional[int]
    description: Optional[str]


class StudyBranchArmListingModel(StudySelctionListingModel):
    class Config:
        title = "Study Branch Arm model for listing"
        description = "Study Branch Arm model for listing."

    randomization_group: Optional[str]

    @classmethod
    def from_study_selection_branch_arm_vo(
        cls,
        study_selection_branch_arm_vo: StudySelectionBranchArmVO,
    ) -> Optional["StudyBranchArmListingModel"]:
        return cls(
            name=none_to_empty_str(study_selection_branch_arm_vo.name),
            short_name=none_to_empty_str(study_selection_branch_arm_vo.short_name),
            randomization_group=none_to_empty_str(
                study_selection_branch_arm_vo.randomization_group
            ),
            code=none_to_empty_str(study_selection_branch_arm_vo.code),
            number_of_subjects=study_selection_branch_arm_vo.number_of_subjects,
            description=none_to_empty_str(study_selection_branch_arm_vo.description),
        )

    @staticmethod
    def from_study_selection_branch_arm_ar(
        study_selection_branch_arm_ar: StudySelectionBranchArmAR,
    ) -> Sequence["StudyBranchArmListingModel"]:
        branch_arms = []
        for selection in study_selection_branch_arm_ar.study_branch_arms_selection:
            branch_arms.append(
                StudyBranchArmListingModel.from_study_selection_branch_arm_vo(
                    study_selection_branch_arm_vo=selection,
                )
            )
        return branch_arms


class StudyArmListingModel(StudySelctionListingModel):
    class Config:
        title = "Study Arm model for listing"
        description = "Study Arm model for listing."

    randomization_group: Optional[str]
    arm_type: str
    connected_branches: Optional[Sequence[StudyBranchArmListingModel]] = None

    @classmethod
    def from_study_selection_arm_vo(
        cls,
        study_uid: str,
        study_selection_arm_vo: StudySelectionArmVO,
        find_simple_term_arm_type_by_term_uid: Callable,
        find_multiple_connected_branch_arm: Callable,
    ) -> Optional["StudyArmListingModel"]:
        return cls(
            arm_type=ct_term_uid_to_str(
                ct_uid=study_selection_arm_vo.arm_type_uid,
                find_term_by_uid=find_simple_term_arm_type_by_term_uid,
            ),
            name=none_to_empty_str(study_selection_arm_vo.name),
            short_name=none_to_empty_str(study_selection_arm_vo.short_name),
            randomization_group=none_to_empty_str(
                study_selection_arm_vo.randomization_group
            ),
            code=none_to_empty_str(study_selection_arm_vo.code),
            number_of_subjects=study_selection_arm_vo.number_of_subjects,
            description=none_to_empty_str(study_selection_arm_vo.description),
            connected_branches=StudyBranchArmListingModel.from_study_selection_branch_arm_ar(
                study_selection_branch_arm_ar=find_multiple_connected_branch_arm(
                    study_uid=study_uid,
                    study_arm_uid=study_selection_arm_vo.study_selection_uid,
                ),
            ),
        )

    @staticmethod
    def from_study_selection_arm_ar(
        study_uid: str,
        study_selection_arm_ar: StudySelectionArmAR,
        find_simple_term_arm_type_by_term_uid: Callable,
        find_multiple_connected_branch_arm: Callable,
    ) -> Sequence["StudyArmListingModel"]:
        arms = []
        for selection in study_selection_arm_ar.study_arms_selection:
            arms.append(
                StudyArmListingModel.from_study_selection_arm_vo(
                    study_uid=study_uid,
                    study_selection_arm_vo=selection,
                    find_simple_term_arm_type_by_term_uid=find_simple_term_arm_type_by_term_uid,
                    find_multiple_connected_branch_arm=find_multiple_connected_branch_arm,
                )
            )
        return arms


class StudyCohortListingModel(StudySelctionListingModel):
    class Config:
        title = "study attributes model for listing"
        description = "Study attributes model for listing"

    arm_root_codes: Optional[Sequence[str]] = None
    branch_arm_root_codes: Optional[Sequence[str]] = None

    @classmethod
    def from_study_selection_cohort_vo(
        cls,
        study_selection_cohort_vo: StudySelectionCohortVO,
        find_arm_by_uid: Optional[Callable] = None,
        find_branch_arm_by_uid: Optional[Callable] = None,
    ) -> Optional["StudyCohortListingModel"]:
        if study_selection_cohort_vo.arm_root_uids:
            arm_root_codes = [
                find_arm_by_uid(arm_root_uid)[0].code
                for arm_root_uid in study_selection_cohort_vo.arm_root_uids
            ]
        else:
            arm_root_codes = []
        if study_selection_cohort_vo.branch_arm_root_uids:
            branch_arm_root_codes = [
                find_branch_arm_by_uid(branch_arm_root_uid)[0].code
                for branch_arm_root_uid in study_selection_cohort_vo.branch_arm_root_uids
            ]
        else:
            branch_arm_root_codes = []
        return cls(
            name=none_to_empty_str(study_selection_cohort_vo.name),
            short_name=none_to_empty_str(study_selection_cohort_vo.short_name),
            code=none_to_empty_str(study_selection_cohort_vo.code),
            number_of_subjects=study_selection_cohort_vo.number_of_subjects,
            description=none_to_empty_str(study_selection_cohort_vo.description),
            arm_root_codes=arm_root_codes,
            branch_arm_root_codes=branch_arm_root_codes,
        )

    @staticmethod
    def from_study_selection_cohort_ar(
        study_selection_cohort_ar: StudySelectionCohortAR,
        find_arm_by_uid: Optional[Callable] = None,
        find_branch_arm_by_uid: Optional[Callable] = None,
    ) -> Optional[Sequence["StudyCohortListingModel"]]:
        cohorts = []
        for selection in study_selection_cohort_ar.study_cohorts_selection:
            cohorts.append(
                StudyCohortListingModel.from_study_selection_cohort_vo(
                    study_selection_cohort_vo=selection,
                    find_arm_by_uid=find_arm_by_uid,
                    find_branch_arm_by_uid=find_branch_arm_by_uid,
                )
            )
        return cohorts


class StudyEpochListingModel(BaseModel):
    name: str
    type: str
    subtype: str
    start_rule: Optional[str]
    end_rule: Optional[str]
    description: Optional[str]

    @classmethod
    def from_study_epoch(
        cls,
        study_epoch: StudyEpoch,
        find_term_by_uid: Callable,
    ) -> Optional["StudyEpochListingModel"]:
        return cls(
            name=none_to_empty_str(study_epoch.epoch_name),
            type=ct_term_uid_to_str(
                study_epoch.epoch_type, find_term_by_uid=find_term_by_uid
            ),
            subtype=ct_term_uid_to_str(
                study_epoch.epoch_subtype, find_term_by_uid=find_term_by_uid
            ),
            start_rule=none_to_empty_str(study_epoch.start_rule),
            end_rule=none_to_empty_str(study_epoch.end_rule),
            description=none_to_empty_str(study_epoch.description),
        )

    @staticmethod
    def from_all_study_epochs(
        all_study_epochs: Sequence[StudyEpoch],
        find_term_by_uid: Callable,
    ) -> Optional[Sequence["StudyEpochListingModel"]]:
        epochs = []
        for epoch in all_study_epochs:
            epochs.append(
                StudyEpochListingModel.from_study_epoch(
                    study_epoch=epoch,
                    find_term_by_uid=find_term_by_uid,
                )
            )
        return epochs


class StudyElementListingModel(BaseModel):
    name: str
    short_name: str
    type: str
    subtype: str
    start_rule: Optional[str]
    end_rule: Optional[str]
    planned_duration: Optional[str]
    description: Optional[str]

    @classmethod
    def from_study_element_vo(
        cls,
        study_element_vo: StudySelectionElementVO,
        find_term_by_uid: Callable,
    ) -> Optional["StudyElementListingModel"]:
        return cls(
            name=none_to_empty_str(study_element_vo.name),
            short_name=none_to_empty_str(study_element_vo.short_name),
            type=ct_term_uid_to_str(
                study_element_vo.code, find_term_by_uid=find_term_by_uid
            ),
            subtype=ct_term_uid_to_str(
                study_element_vo.element_subtype_uid, find_term_by_uid=find_term_by_uid
            ),
            start_rule=none_to_empty_str(study_element_vo.start_rule),
            end_rule=none_to_empty_str(study_element_vo.end_rule),
            planned_duration=none_to_empty_str(study_element_vo.planned_duration),
            description=none_to_empty_str(study_element_vo.description),
        )

    @staticmethod
    def from_study_element_ar(
        study_element_ar: StudySelectionElementAR,
        find_term_by_uid: Callable,
    ) -> Optional[Sequence["StudyEpochListingModel"]]:
        elements = []
        for element in study_element_ar.study_elements_selection:
            elements.append(
                StudyElementListingModel.from_study_element_vo(
                    study_element_vo=element,
                    find_term_by_uid=find_term_by_uid,
                )
            )
        return elements


class StudyDesignMatrixListingModel(BaseModel):
    arm_code: str
    branch_arm_code: Optional[str]
    epoch_name: str
    element_name: str

    @classmethod
    def from_study_design_cell_vo(
        cls,
        design_cell_vo: StudyDesignCellVO,
        find_arm_by_uid: Optional[Callable] = None,
        find_branch_arm_by_uid: Optional[Callable] = None,
    ) -> "StudyDesignMatrixListingModel":
        return cls(
            arm_code=find_arm_by_uid(design_cell_vo.study_arm_uid)[0].code
            if design_cell_vo.study_arm_uid
            else "",
            branch_arm_code=find_branch_arm_by_uid(design_cell_vo.study_branch_arm_uid)[
                0
            ].code
            if design_cell_vo.study_branch_arm_uid
            else "",
            epoch_name=none_to_empty_str(design_cell_vo.study_epoch_name),
            element_name=none_to_empty_str(design_cell_vo.study_element_name),
        )

    @staticmethod
    def from_all_study_design_cells(
        all_design_cells: Sequence[StudyDesignCellVO],
        find_arm_by_uid: Optional[Callable] = None,
        find_branch_arm_by_uid: Optional[Callable] = None,
    ) -> Optional[Sequence["StudyDesignMatrixListingModel"]]:
        design_cells = []
        for design_cell in all_design_cells:
            design_cells.append(
                StudyDesignMatrixListingModel.from_study_design_cell_vo(
                    design_cell_vo=design_cell,
                    find_arm_by_uid=find_arm_by_uid,
                    find_branch_arm_by_uid=find_branch_arm_by_uid,
                )
            )
        return design_cells


class StudyVisitListingModel(BaseModel):
    epoch_uid: str
    epoch_name: str
    visit_type: str
    contact_model: str
    unique_visit_number: str
    name: str
    short_name: str
    study_day_number: Optional[int]
    visit_window_min: Optional[int]
    visit_window_max: Optional[int]
    window_unit: Optional[str]
    description: Optional[str]
    epoch_allocation: Optional[str]
    start_rule: Optional[str]
    end_rule: Optional[str]

    @classmethod
    def from_study_visit_vo(
        cls,
        study_visit_vo: StudyVisitVO,
    ) -> "StudyVisitListingModel":
        return cls(
            epoch_uid=study_visit_vo.epoch_uid,
            epoch_name=study_visit_vo.epoch.epoch.value,
            visit_type=study_visit_vo.visit_type.value,
            contact_model=study_visit_vo.visit_contact_mode.value,
            unique_visit_number=study_visit_vo.unique_visit_number,
            name=study_visit_vo.derive_visit_name(),
            short_name=study_visit_vo.visit_short_name,
            study_day_number=study_visit_vo.study_day_number
            if study_visit_vo.study_day
            else None,
            visit_window_min=study_visit_vo.visit_window_min,
            visit_window_max=study_visit_vo.visit_window_max,
            window_unit=study_visit_vo.window_unit_object.name
            if study_visit_vo.window_unit_object
            else None,
            description=study_visit_vo.description,
            epoch_allocation=study_visit_vo.epoch_allocation.value
            if study_visit_vo.epoch_allocation
            else None,
            start_rule=study_visit_vo.start_rule,
            end_rule=study_visit_vo.end_rule,
        )

    @staticmethod
    def from_all_study_visits(
        all_study_visits: Sequence[StudyVisitVO],
    ) -> Optional[Sequence["StudyVisitListingModel"]]:
        study_visits = []
        for study_visit in all_study_visits:
            study_visits.append(
                StudyVisitListingModel.from_study_visit_vo(
                    study_visit_vo=study_visit,
                )
            )
        return study_visits


class StudyMetadataListingModel(BaseModel):
    class Config:
        title = "Study Metadata model for listing"
        description = "Study Metadata model for listing."

    study_title: Optional[StudyDescriptionJsonModel] = None
    registry_identifiers: Optional[RegistryIdentifiersListingModel] = None
    study_type: Optional[StudyTypeListingModel] = None
    study_attributes: Optional[StudyAttributesListingModel] = None
    study_population: Optional[StudyPopulationListingModel] = None
    study_arms: Optional[Sequence[StudyArmListingModel]] = None
    study_cohorts: Optional[Sequence[StudyCohortListingModel]] = None
    study_epochs: Optional[Sequence[StudyEpochListingModel]] = None
    study_elements: Optional[Sequence[StudyElementListingModel]] = None
    study_design_matrix: Optional[Sequence[StudyDesignMatrixListingModel]] = None
    study_visits: Optional[Sequence[StudyVisitListingModel]] = None

    @classmethod
    def from_study_metadata_vo(
        cls,
        study_uid: str,
        study_metadata_vo: StudyMetadataVO,
        study_selection_arm_ar: StudySelectionArmAR,
        study_selection_cohort_ar: StudySelectionCohortAR,
        study_epochs: Sequence[StudyEpoch],
        study_element_ar: StudySelectionElementAR,
        study_design_cells: Sequence[StudyDesignCellVO],
        study_visits: Sequence[StudyVisitVO],
        find_term_by_uid: Callable[[str], Optional[CTTermAttributesAR]],
        find_dictionary_term_by_uid: Callable[[str], Optional[DictionaryTermAR]],
        find_multiple_connected_branch_arm: Callable,
        find_arm_by_uid: Optional[Callable] = None,
        find_branch_arm_by_uid: Optional[Callable] = None,
    ) -> "StudyMetadataListingModel":
        if study_metadata_vo is None:
            return None
        return cls(
            study_title=StudyDescriptionJsonModel.from_study_description_vo(
                study_description_vo=study_metadata_vo.study_description
            ),
            registry_identifiers=RegistryIdentifiersListingModel.from_study_registry_identifiers_vo(
                registry_identifiers_vo=study_metadata_vo.id_metadata.registry_identifiers,
                find_term_by_uid=find_term_by_uid,
            ),
            study_type=StudyTypeListingModel.from_high_level_study_design_vo(
                high_level_study_design_vo=study_metadata_vo.high_level_study_design,
                find_term_by_uid=find_term_by_uid,
            ),
            study_attributes=StudyAttributesListingModel.from_study_intervention_vo(
                study_intervention_vo=study_metadata_vo.study_intervention,
                find_term_by_uid=find_term_by_uid,
            ),
            study_population=StudyPopulationListingModel.from_study_population_vo(
                study_population_vo=study_metadata_vo.study_population,
                find_term_by_uid=find_term_by_uid,
                find_dictionary_term_by_uid=find_dictionary_term_by_uid,
            ),
            study_arms=StudyArmListingModel.from_study_selection_arm_ar(
                study_uid=study_uid,
                study_selection_arm_ar=study_selection_arm_ar,
                find_simple_term_arm_type_by_term_uid=find_term_by_uid,
                find_multiple_connected_branch_arm=find_multiple_connected_branch_arm,
            ),
            study_cohorts=StudyCohortListingModel.from_study_selection_cohort_ar(
                study_selection_cohort_ar=study_selection_cohort_ar,
                find_arm_by_uid=find_arm_by_uid,
                find_branch_arm_by_uid=find_branch_arm_by_uid,
            ),
            study_epochs=StudyEpochListingModel.from_all_study_epochs(
                all_study_epochs=study_epochs,
                find_term_by_uid=find_term_by_uid,
            ),
            study_elements=StudyElementListingModel.from_study_element_ar(
                study_element_ar=study_element_ar,
                find_term_by_uid=find_term_by_uid,
            ),
            study_design_matrix=StudyDesignMatrixListingModel.from_all_study_design_cells(
                all_design_cells=study_design_cells,
                find_arm_by_uid=find_arm_by_uid,
                find_branch_arm_by_uid=find_branch_arm_by_uid,
            ),
            study_visits=StudyVisitListingModel.from_all_study_visits(
                all_study_visits=study_visits,
            ),
        )
