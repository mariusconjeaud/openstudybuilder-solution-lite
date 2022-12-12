"""Study model."""
from datetime import datetime
from typing import Callable, Collection, Iterable, List, Optional, Sequence

from pydantic import Field

from clinical_mdr_api.domain.clinical_programme.clinical_programme import (
    ClinicalProgrammeAR,
)
from clinical_mdr_api.domain.controlled_terminology.ct_term_name import CTTermNameAR
from clinical_mdr_api.domain.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domain.project.project import ProjectAR
from clinical_mdr_api.domain.study_definition_aggregate.registry_identifiers import (
    RegistryIdentifiersVO,
)
from clinical_mdr_api.domain.study_definition_aggregate.root import StudyDefinitionAR
from clinical_mdr_api.domain.study_definition_aggregate.study_metadata import (
    HighLevelStudyDesignVO,
    StudyDescriptionVO,
    StudyFieldAuditTrailEntryAR,
    StudyIdentificationMetadataVO,
    StudyInterventionVO,
    StudyMetadataVO,
    StudyPopulationVO,
    StudyVersionMetadataVO,
)
from clinical_mdr_api.domain.unit_definition.unit_definition import UnitDefinitionAR
from clinical_mdr_api.models.ct_term import SimpleTermModel
from clinical_mdr_api.models.duration import DurationJsonModel
from clinical_mdr_api.models.utils import BaseModel


class RegistryIdentifiersJsonModel(BaseModel):
    class Config:
        title = "RegistryIdentifiersMetadata"
        description = "RegistryIdentifiersMetadata metadata for study definition."

    ct_gov_id: Optional[str] = None
    ct_gov_id_null_value_code: Optional[SimpleTermModel] = None
    eudract_id: Optional[str] = None
    eudract_id_null_value_code: Optional[SimpleTermModel] = None
    universal_trial_number_utn: Optional[str] = None
    universal_trial_number_utn_null_value_code: Optional[SimpleTermModel] = None
    japanese_trial_registry_id_japic: Optional[str] = None
    japanese_trial_registry_id_japic_null_value_code: Optional[SimpleTermModel] = None
    investigational_new_drug_application_number_ind: Optional[str] = None
    investigational_new_drug_application_number_ind_null_value_code: Optional[
        SimpleTermModel
    ] = None

    @classmethod
    def from_study_registry_identifiers_vo(
        cls,
        registry_identifiers_vo: RegistryIdentifiersVO,
        find_term_by_uid: Callable[[str], Optional[CTTermNameAR]],
    ) -> "RegistryIdentifiersJsonModel":
        return cls(
            ct_gov_id=registry_identifiers_vo.ct_gov_id,
            ct_gov_id_null_value_code=SimpleTermModel.from_ct_code(
                c_code=registry_identifiers_vo.ct_gov_id_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            eudract_id=registry_identifiers_vo.eudract_id,
            eudract_id_null_value_code=SimpleTermModel.from_ct_code(
                c_code=registry_identifiers_vo.eudract_id_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            universal_trial_number_utn=registry_identifiers_vo.universal_trial_number_utn,
            universal_trial_number_utn_null_value_code=SimpleTermModel.from_ct_code(
                c_code=registry_identifiers_vo.universal_trial_number_utn_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            japanese_trial_registry_id_japic=registry_identifiers_vo.japanese_trial_registry_id_japic,
            japanese_trial_registry_id_japic_null_value_code=SimpleTermModel.from_ct_code(
                c_code=registry_identifiers_vo.japanese_trial_registry_id_japic_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            investigational_new_drug_application_number_ind=registry_identifiers_vo.investigational_new_drug_application_number_ind,
            investigational_new_drug_application_number_ind_null_value_code=SimpleTermModel.from_ct_code(
                c_code=registry_identifiers_vo.investigational_new_drug_application_number_ind_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
        )


class StudyIdentificationMetadataJsonModel(BaseModel):
    class Config:
        title = "StudyIdentificationMetadata"
        description = "Identification metadata for study definition."

    study_number: Optional[str] = None
    study_acronym: Optional[str] = None
    project_number: Optional[str] = None
    project_name: Optional[str] = None
    clinical_programme_name: Optional[str] = None
    study_id: Optional[str] = None
    registry_identifiers: Optional[RegistryIdentifiersJsonModel] = None

    @classmethod
    def from_study_identification_vo(
        cls,
        study_identification_o: Optional[StudyIdentificationMetadataVO],
        find_project_by_project_number: Callable[[str], ProjectAR],
        find_clinical_programme_by_uid: Callable[[str], ClinicalProgrammeAR],
        find_term_by_uid: Callable[[str], Optional[CTTermNameAR]],
    ) -> Optional["StudyIdentificationMetadataJsonModel"]:
        if study_identification_o is None:
            return None
        project_ar = find_project_by_project_number(
            study_identification_o.project_number
        )
        return cls(
            study_number=study_identification_o.study_number,
            study_acronym=study_identification_o.study_acronym,
            project_number=study_identification_o.project_number,
            project_name=project_ar.name,
            clinical_programme_name=find_clinical_programme_by_uid(
                project_ar.clinical_programme_uid
            ).name,
            study_id=study_identification_o.study_id,
            registry_identifiers=RegistryIdentifiersJsonModel.from_study_registry_identifiers_vo(
                study_identification_o.registry_identifiers, find_term_by_uid
            ),
        )


class StudyVersionMetadataJsonModel(BaseModel):
    class Config:
        title = "StudyVersionMetadata"
        description = "Version metadata for study definition."

    study_status: Optional[str] = None
    locked_version_number: Optional[int] = None
    version_timestamp: Optional[datetime] = None
    locked_version_author: Optional[str] = None
    locked_version_info: Optional[str] = None

    @classmethod
    def from_study_version_metadata_vo(
        cls, study_version_metadata_vo: Optional[StudyVersionMetadataVO]
    ) -> Optional["StudyVersionMetadataJsonModel"]:
        if study_version_metadata_vo is None:
            return None
        return cls(
            study_status=study_version_metadata_vo.study_status.value,
            locked_version_number=study_version_metadata_vo.locked_version_number,
            version_timestamp=study_version_metadata_vo.version_timestamp,
            locked_version_author=study_version_metadata_vo.locked_version_author,
            locked_version_info=study_version_metadata_vo.locked_version_info,
        )


class HighLevelStudyDesignJsonModel(BaseModel):
    class Config:
        title = "HighLevelStudyDesign"
        description = "High level study design parameters for study definition."

    study_type_code: Optional[SimpleTermModel] = None
    study_type_null_value_code: Optional[SimpleTermModel] = None

    trial_types_codes: Optional[Sequence[SimpleTermModel]] = None
    trial_types_null_value_code: Optional[SimpleTermModel] = None

    trial_phase_code: Optional[SimpleTermModel] = None
    trial_phase_null_value_code: Optional[SimpleTermModel] = None

    is_extension_trial: Optional[bool] = None
    is_extension_trial_null_value_code: Optional[SimpleTermModel] = None

    is_adaptive_design: Optional[bool] = None
    is_adaptive_design_null_value_code: Optional[SimpleTermModel] = None

    study_stop_rules: Optional[str] = None
    study_stop_rules_null_value_code: Optional[SimpleTermModel] = None

    confirmed_response_minimum_duration: Optional[DurationJsonModel] = None
    confirmed_response_minimum_duration_null_value_code: Optional[
        SimpleTermModel
    ] = None

    post_auth_indicator: Optional[bool] = None
    post_auth_indicator_null_value_code: Optional[SimpleTermModel] = None

    @classmethod
    def from_high_level_study_design_vo(
        cls,
        high_level_study_design_vo: Optional[HighLevelStudyDesignVO],
        find_term_by_uid: Callable[[str], Optional[CTTermNameAR]],
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
    ) -> Optional["HighLevelStudyDesignJsonModel"]:
        if high_level_study_design_vo is None:
            return None
        return cls(
            study_type_code=SimpleTermModel.from_ct_code(
                c_code=high_level_study_design_vo.study_type_code,
                find_term_by_uid=find_term_by_uid,
            ),
            study_type_null_value_code=SimpleTermModel.from_ct_code(
                c_code=high_level_study_design_vo.study_type_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_types_codes=[
                SimpleTermModel.from_ct_code(
                    c_code=trial_type_code, find_term_by_uid=find_term_by_uid
                )
                for trial_type_code in high_level_study_design_vo.trial_type_codes
            ],
            trial_types_null_value_code=SimpleTermModel.from_ct_code(
                c_code=high_level_study_design_vo.trial_type_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_phase_code=SimpleTermModel.from_ct_code(
                c_code=high_level_study_design_vo.trial_phase_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_phase_null_value_code=SimpleTermModel.from_ct_code(
                c_code=high_level_study_design_vo.trial_phase_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            is_extension_trial=high_level_study_design_vo.is_extension_trial,
            is_extension_trial_null_value_code=SimpleTermModel.from_ct_code(
                c_code=high_level_study_design_vo.is_extension_trial_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            is_adaptive_design=high_level_study_design_vo.is_adaptive_design,
            is_adaptive_design_null_value_code=SimpleTermModel.from_ct_code(
                high_level_study_design_vo.is_adaptive_design_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            study_stop_rules=high_level_study_design_vo.study_stop_rules,
            study_stop_rules_null_value_code=SimpleTermModel.from_ct_code(
                c_code=high_level_study_design_vo.study_stop_rules_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            confirmed_response_minimum_duration=(
                DurationJsonModel.from_duration_object(
                    duration=high_level_study_design_vo.confirmed_response_minimum_duration,
                    find_all_study_time_units=find_all_study_time_units,
                )
                if high_level_study_design_vo.confirmed_response_minimum_duration
                is not None
                else None
            ),
            confirmed_response_minimum_duration_null_value_code=SimpleTermModel.from_ct_code(
                c_code=high_level_study_design_vo.confirmed_response_minimum_duration_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            post_auth_indicator=high_level_study_design_vo.post_auth_indicator,
            post_auth_indicator_null_value_code=SimpleTermModel.from_ct_code(
                c_code=high_level_study_design_vo.post_auth_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
        )


class StudyPopulationJsonModel(BaseModel):
    class Config:
        title = "StudyPopulation"
        description = "Study population parameters for study definition."

    therapeutic_areas_codes: Optional[Sequence[SimpleTermModel]] = None
    therapeutic_areas_null_value_code: Optional[SimpleTermModel] = None

    disease_conditions_or_indications_codes: Optional[Sequence[SimpleTermModel]] = None
    disease_conditions_or_indications_null_value_code: Optional[SimpleTermModel] = None

    diagnosis_groups_codes: Optional[Sequence[SimpleTermModel]] = None
    diagnosis_groups_null_value_code: Optional[SimpleTermModel] = None

    sex_of_participants_code: Optional[SimpleTermModel] = None
    sex_of_participants_null_value_code: Optional[SimpleTermModel] = None

    rare_disease_indicator: Optional[bool] = None
    rare_disease_indicator_null_value_code: Optional[SimpleTermModel] = None

    healthy_subject_indicator: Optional[bool] = None
    healthy_subject_indicator_null_value_code: Optional[SimpleTermModel] = None

    planned_minimum_age_of_subjects: Optional[DurationJsonModel] = None
    planned_minimum_age_of_subjects_null_value_code: Optional[SimpleTermModel] = None

    planned_maximum_age_of_subjects: Optional[DurationJsonModel] = None
    planned_maximum_age_of_subjects_null_value_code: Optional[SimpleTermModel] = None

    stable_disease_minimum_duration: Optional[DurationJsonModel] = None
    stable_disease_minimum_duration_null_value_code: Optional[SimpleTermModel] = None

    pediatric_study_indicator: Optional[bool] = None
    pediatric_study_indicator_null_value_code: Optional[SimpleTermModel] = None

    pediatric_postmarket_study_indicator: Optional[bool] = None
    pediatric_postmarket_study_indicator_null_value_code: Optional[
        SimpleTermModel
    ] = None

    pediatric_investigation_plan_indicator: Optional[bool] = None
    pediatric_investigation_plan_indicator_null_value_code: Optional[
        SimpleTermModel
    ] = None

    relapse_criteria: Optional[str] = None
    relapse_criteria_null_value_code: Optional[SimpleTermModel] = None

    number_of_expected_subjects: Optional[int] = None
    number_of_expected_subjects_null_value_code: Optional[SimpleTermModel] = None

    @classmethod
    def from_study_population_vo(
        cls,
        study_population_vo: Optional[StudyPopulationVO],
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
        find_term_by_uid: Callable[[str], Optional[CTTermNameAR]],
        find_dictionary_term_by_uid: Callable[[str], Optional[DictionaryTermAR]],
    ) -> Optional["StudyPopulationJsonModel"]:
        if study_population_vo is None:
            return None
        return cls(
            therapeutic_areas_codes=[
                SimpleTermModel.from_ct_code(
                    c_code=therapeutic_area_code,
                    find_term_by_uid=find_dictionary_term_by_uid,
                )
                for therapeutic_area_code in study_population_vo.therapeutic_area_codes
            ],
            therapeutic_areas_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.therapeutic_area_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            disease_conditions_or_indications_codes=[
                SimpleTermModel.from_ct_code(
                    c_code=disease_or_indication_code,
                    find_term_by_uid=find_dictionary_term_by_uid,
                )
                for disease_or_indication_code in study_population_vo.disease_condition_or_indication_codes
            ],
            disease_conditions_or_indications_null_value_code=(
                SimpleTermModel.from_ct_code(
                    c_code=study_population_vo.disease_condition_or_indication_null_value_code,
                    find_term_by_uid=find_term_by_uid,
                )
            ),
            diagnosis_groups_codes=[
                SimpleTermModel.from_ct_code(
                    c_code=diagnosis_group_code,
                    find_term_by_uid=find_dictionary_term_by_uid,
                )
                for diagnosis_group_code in study_population_vo.diagnosis_group_codes
            ],
            diagnosis_groups_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.diagnosis_group_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            sex_of_participants_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.sex_of_participants_code,
                find_term_by_uid=find_term_by_uid,
            ),
            sex_of_participants_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.sex_of_participants_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            rare_disease_indicator=study_population_vo.rare_disease_indicator,
            rare_disease_indicator_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.rare_disease_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            healthy_subject_indicator=study_population_vo.healthy_subject_indicator,
            healthy_subject_indicator_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.healthy_subject_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            planned_minimum_age_of_subjects=(
                DurationJsonModel.from_duration_object(
                    duration=study_population_vo.planned_minimum_age_of_subjects,
                    find_all_study_time_units=find_all_study_time_units,
                )
                if study_population_vo.planned_minimum_age_of_subjects is not None
                else None
            ),
            planned_minimum_age_of_subjects_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.planned_minimum_age_of_subjects_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            planned_maximum_age_of_subjects=(
                DurationJsonModel.from_duration_object(
                    duration=study_population_vo.planned_maximum_age_of_subjects,
                    find_all_study_time_units=find_all_study_time_units,
                )
                if study_population_vo.planned_maximum_age_of_subjects is not None
                else None
            ),
            planned_maximum_age_of_subjects_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.planned_maximum_age_of_subjects_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            stable_disease_minimum_duration=(
                DurationJsonModel.from_duration_object(
                    duration=study_population_vo.stable_disease_minimum_duration,
                    find_all_study_time_units=find_all_study_time_units,
                )
                if study_population_vo.stable_disease_minimum_duration is not None
                else None
            ),
            stable_disease_minimum_duration_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.stable_disease_minimum_duration_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            pediatric_study_indicator=study_population_vo.pediatric_study_indicator,
            pediatric_study_indicator_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.pediatric_study_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            pediatric_postmarket_study_indicator=study_population_vo.pediatric_postmarket_study_indicator,
            pediatric_postmarket_study_indicator_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.pediatric_postmarket_study_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            pediatric_investigation_plan_indicator=study_population_vo.pediatric_investigation_plan_indicator,
            pediatric_investigation_plan_indicator_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.pediatric_investigation_plan_indicator_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            relapse_criteria=study_population_vo.relapse_criteria,
            relapse_criteria_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.relapse_criteria_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            number_of_expected_subjects=study_population_vo.number_of_expected_subjects,
            number_of_expected_subjects_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.number_of_expected_subjects_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
        )


class StudyInterventionJsonModel(BaseModel):
    class Config:
        title = "StudyIntervention"
        description = "Study interventions parameters for study definition."

    intervention_type_code: Optional[SimpleTermModel] = None
    intervention_type_null_value_code: Optional[SimpleTermModel] = None

    add_on_to_existing_treatments: Optional[bool] = None
    add_on_to_existing_treatments_null_value_code: Optional[SimpleTermModel] = None

    control_type_code: Optional[SimpleTermModel] = None
    control_type_null_value_code: Optional[SimpleTermModel] = None

    intervention_model_code: Optional[SimpleTermModel] = None
    intervention_model_null_value_code: Optional[SimpleTermModel] = None

    is_trial_randomised: Optional[bool] = None
    is_trial_randomised_null_value_code: Optional[SimpleTermModel] = None

    stratification_factor: Optional[str] = None
    stratification_factor_null_value_code: Optional[SimpleTermModel] = None

    trial_blinding_schema_code: Optional[SimpleTermModel] = None
    trial_blinding_schema_null_value_code: Optional[SimpleTermModel] = None

    planned_study_length: Optional[DurationJsonModel] = None
    planned_study_length_null_value_code: Optional[SimpleTermModel] = None

    drug_study_indication: Optional[bool] = None
    drug_study_indication_null_value_code: Optional[SimpleTermModel] = None

    device_study_indication: Optional[str] = None
    device_study_indication_null_value_code: Optional[SimpleTermModel] = None

    trial_intent_types_codes: Optional[Sequence[SimpleTermModel]] = None
    trial_intent_types_null_value_code: Optional[SimpleTermModel] = None

    @classmethod
    def from_study_intervention_vo(
        cls,
        study_intervention_vo: Optional[StudyInterventionVO],
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
        find_term_by_uid: Callable[[str], Optional[CTTermNameAR]],
    ) -> Optional["StudyInterventionJsonModel"]:
        if study_intervention_vo is None:
            return None
        return cls(
            intervention_type_code=SimpleTermModel.from_ct_code(
                c_code=study_intervention_vo.intervention_type_code,
                find_term_by_uid=find_term_by_uid,
            ),
            intervention_type_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_intervention_vo.intervention_type_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            add_on_to_existing_treatments=study_intervention_vo.add_on_to_existing_treatments,
            add_on_to_existing_treatments_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_intervention_vo.add_on_to_existing_treatments_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            control_type_code=SimpleTermModel.from_ct_code(
                c_code=study_intervention_vo.control_type_code,
                find_term_by_uid=find_term_by_uid,
            ),
            control_type_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_intervention_vo.control_type_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            intervention_model_code=SimpleTermModel.from_ct_code(
                c_code=study_intervention_vo.intervention_model_code,
                find_term_by_uid=find_term_by_uid,
            ),
            intervention_model_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_intervention_vo.intervention_model_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            is_trial_randomised=study_intervention_vo.is_trial_randomised,
            is_trial_randomised_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_intervention_vo.is_trial_randomised_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            stratification_factor=study_intervention_vo.stratification_factor,
            stratification_factor_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_intervention_vo.stratification_factor_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_blinding_schema_code=SimpleTermModel.from_ct_code(
                c_code=study_intervention_vo.trial_blinding_schema_code,
                find_term_by_uid=find_term_by_uid,
            ),
            trial_blinding_schema_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_intervention_vo.trial_blinding_schema_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            planned_study_length=(
                DurationJsonModel.from_duration_object(
                    duration=study_intervention_vo.planned_study_length,
                    find_all_study_time_units=find_all_study_time_units,
                )
                if study_intervention_vo.planned_study_length is not None
                else None
            ),
            planned_study_length_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_intervention_vo.planned_study_length_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            drug_study_indicator=study_intervention_vo.drug_study_indication,
            drug_study_indicator_null_value_code=(
                SimpleTermModel.from_ct_code(
                    c_code=study_intervention_vo.drug_study_indication_null_value_code,
                    find_term_by_uid=find_term_by_uid,
                )
            ),
            device_study_indicator=study_intervention_vo.device_study_indication,
            device_study_indicator_null_value_code=(
                SimpleTermModel.from_ct_code(
                    c_code=study_intervention_vo.device_study_indication_null_value_code,
                    find_term_by_uid=find_term_by_uid,
                )
            ),
            trial_intent_types_codes=[
                SimpleTermModel.from_ct_code(
                    c_code=trial_intent_type_code, find_term_by_uid=find_term_by_uid
                )
                for trial_intent_type_code in study_intervention_vo.trial_intent_types_codes
            ],
            trial_intent_types_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_intervention_vo.trial_intent_type_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
        )


class StudyDescriptionJsonModel(BaseModel):
    class Config:
        title = "StudyDescription"
        description = "Study description for the study definition."

    study_title: Optional[str] = None
    study_short_title: Optional[str] = None

    @classmethod
    def from_study_description_vo(
        cls, study_description_vo: Optional[StudyDescriptionVO]
    ) -> Optional["StudyDescriptionJsonModel"]:
        if study_description_vo is None:
            return None
        return cls(
            study_title=study_description_vo.study_title,
            study_short_title=study_description_vo.study_short_title,
        )


class StudyMetadataJsonModel(BaseModel):
    class Config:
        title = "StudyMetadata"
        description = "Study metadata"

    identification_metadata: Optional[StudyIdentificationMetadataJsonModel] = None
    version_metadata: Optional[StudyVersionMetadataJsonModel] = None
    high_level_study_design: Optional[HighLevelStudyDesignJsonModel] = None
    study_population: Optional[StudyPopulationJsonModel] = None
    study_intervention: Optional[StudyInterventionJsonModel] = None
    study_description: Optional[StudyDescriptionJsonModel] = None

    @classmethod
    def from_study_metadata_vo(
        cls,
        study_metadata_vo: StudyMetadataVO,
        find_project_by_project_number: Callable[[str], ProjectAR],
        find_clinical_programme_by_uid: Callable[[str], ClinicalProgrammeAR],
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
        find_term_by_uid: Callable[[str], Optional[CTTermNameAR]],
        find_dictionary_term_by_uid: Callable[[str], Optional[DictionaryTermAR]],
    ) -> "StudyMetadataJsonModel":
        return cls(
            identification_metadata=StudyIdentificationMetadataJsonModel.from_study_identification_vo(
                study_identification_o=study_metadata_vo.id_metadata,
                find_project_by_project_number=find_project_by_project_number,
                find_clinical_programme_by_uid=find_clinical_programme_by_uid,
                find_term_by_uid=find_term_by_uid,
            ),
            version_metadata=StudyVersionMetadataJsonModel.from_study_version_metadata_vo(
                study_version_metadata_vo=study_metadata_vo.ver_metadata
            ),
            high_level_study_design=HighLevelStudyDesignJsonModel.from_high_level_study_design_vo(
                high_level_study_design_vo=study_metadata_vo.high_level_study_design,
                find_term_by_uid=find_term_by_uid,
                find_all_study_time_units=find_all_study_time_units,
            ),
            study_population=StudyPopulationJsonModel.from_study_population_vo(
                study_population_vo=study_metadata_vo.study_population,
                find_all_study_time_units=find_all_study_time_units,
                find_term_by_uid=find_term_by_uid,
                find_dictionary_term_by_uid=find_dictionary_term_by_uid,
            ),
            study_intervention=StudyInterventionJsonModel.from_study_intervention_vo(
                study_intervention_vo=study_metadata_vo.study_intervention,
                find_all_study_time_units=find_all_study_time_units,
                find_term_by_uid=find_term_by_uid,
            ),
            study_description=StudyDescriptionJsonModel.from_study_description_vo(
                study_description_vo=study_metadata_vo.study_description
            ),
        )


class StudyPatchRequestJsonModel(BaseModel):
    class Config:
        title = "StudyPatchRequest"
        description = "Identification metadata for study definition."

    current_metadata: Optional[StudyMetadataJsonModel] = None


class Study(BaseModel):
    uid: str = Field(
        title="uid",
        description="The unique id of the study.",
    )

    study_number: Optional[str] = Field(
        None,
        title="study_number",
        description="DEPRECATED. Use field in current_metadata.identification_metadata.",
    )

    study_id: Optional[str] = Field(
        None,
        title="study_id",
        description="DEPRECATED. Use field in current_metadata.identification_metadata.",
    )

    study_acronym: Optional[str] = Field(
        None,
        title="study_acronym",
        description="DEPRECATED. Use field in current_metadata.identification_metadata.",
    )

    project_number: Optional[str] = Field(
        None,
        title="project_number",
        description="DEPRECATED. Use field in current_metadata.identification_metadata.",
    )
    study_status: str = Field(
        None,
        title="study_status",
        description="Current status of given StudyDefinition. "
        "Possible values are: 'DRAFT' or 'LOCKED'.",
    )

    current_metadata: Optional[StudyMetadataJsonModel] = None

    @classmethod
    def from_study_definition_ar(
        cls,
        study_definition_ar: StudyDefinitionAR,
        find_project_by_project_number: Callable[[str], ProjectAR],
        find_clinical_programme_by_uid: Callable[[str], ClinicalProgrammeAR],
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
        find_term_by_uid: Callable[[str], Optional[CTTermNameAR]],
        find_dictionary_term_by_uid: Callable[[str], Optional[DictionaryTermAR]],
    ) -> "Study":
        is_id_metadata_none = (
            True if study_definition_ar.current_metadata.id_metadata is None else None
        )
        return cls(
            uid=study_definition_ar.uid,
            study_number=study_definition_ar.current_metadata.id_metadata.study_number
            if not is_id_metadata_none
            else None,
            study_acronym=study_definition_ar.current_metadata.id_metadata.study_acronym
            if not is_id_metadata_none
            else None,
            project_number=study_definition_ar.current_metadata.id_metadata.project_number
            if not is_id_metadata_none
            else None,
            study_id=study_definition_ar.current_metadata.id_metadata.study_id
            if not is_id_metadata_none
            else None,
            study_status=study_definition_ar.current_metadata.ver_metadata.study_status.value
            if not is_id_metadata_none
            else None,
            current_metadata=StudyMetadataJsonModel.from_study_metadata_vo(
                study_metadata_vo=study_definition_ar.current_metadata,
                find_project_by_project_number=find_project_by_project_number,
                find_clinical_programme_by_uid=find_clinical_programme_by_uid,
                find_all_study_time_units=find_all_study_time_units,
                find_term_by_uid=find_term_by_uid,
                find_dictionary_term_by_uid=find_dictionary_term_by_uid,
            ),
        )


class StudyCreateInput(BaseModel):
    # project_uid: str = Field(
    #    ...,
    #    title="project_uid",
    #    description="The unique id of the project that holds the study.",
    # )
    study_number: Optional[str] = Field(
        # ...,
        title="study_number",
        description="",
    )

    # study_id_prefix: Optional[str] = Field(
    #     ...,
    #     title="study_id_prefix",
    #     description="",
    # )

    study_acronym: Optional[str] = Field(
        # ...,
        title="study_acronym",
        description="",
    )

    project_number: Optional[str] = Field(
        # ...,
        title="project_number",
        description="",
    )


class StudyFieldAuditTrailAction(BaseModel):
    section: str = Field(
        None,
        title="section",
        description="The section that the modified study field is in.",
    )

    field: str = Field(
        None,
        title="field",
        description="The name of the study field that was changed.",
    )

    before_value: SimpleTermModel = Field(
        None,
        title="before_value",
        description="The value of the field before the edit.",
    )

    after_value: SimpleTermModel = Field(
        None,
        title="after_value",
        description="The value of the field after the edit.",
    )

    action: str = Field(
        None,
        title="action",
        description="The action taken on the study field. One of (Create, edit, delete...)",
    )


class StudyFieldAuditTrailEntry(BaseModel):
    study_uid: str = Field(
        None,
        title="study_uid",
        description="The unique id of the study.",
    )

    user_initials: str = Field(
        None,
        title="user_initials",
        description="The initials of the user that made the edit.",
    )

    date: str = Field(
        None,
        title="date",
        description="The date that the edit was made.",
    )

    actions: List[StudyFieldAuditTrailAction] = Field(
        None,
        title="actions",
        description="The actions that took place as part of this audit trial entry.",
    )

    @classmethod
    def from_study_field_audit_trail_vo(
        cls,
        study_field_audit_trail_vo: StudyFieldAuditTrailEntryAR,
        sections_selected: Collection[str],
        find_term_by_uid: Callable[[str], Optional[CTTermNameAR]],
    ) -> "StudyFieldAuditTrailEntry":
        actions: List[StudyFieldAuditTrailAction] = [
            StudyFieldAuditTrailAction(
                section=action.section,
                field=action.field_name,
                action=action.action,
                before_value=SimpleTermModel.from_ct_code(
                    c_code=action.before_value, find_term_by_uid=find_term_by_uid
                ),
                after_value=SimpleTermModel.from_ct_code(
                    c_code=action.after_value, find_term_by_uid=find_term_by_uid
                ),
            )
            for action in study_field_audit_trail_vo.actions
            if action.section in sections_selected
        ]
        return cls(
            study_uid=study_field_audit_trail_vo.study_uid,
            actions=actions,
            user_initials=study_field_audit_trail_vo.user_initials,
            date=study_field_audit_trail_vo.date,
        )


class StudyProtocolTitle(BaseModel):
    study_uid: str = Field(
        None,
        title="study_uid",
        description="The unique id of the study.",
    )
    study_title: Optional[str] = None
    study_short_title: Optional[str] = None
    eudract_id: Optional[str] = None
    universal_trial_number_utn: Optional[str] = None
    trial_phase_code: Optional[SimpleTermModel] = None
    ind_number: Optional[str] = None
    substance_name: Optional[str] = None

    @classmethod
    def from_study_definition_ar(
        cls,
        study_definition_ar: StudyDefinitionAR,
        find_term_by_uid: Callable[[str], Optional[CTTermNameAR]],
    ) -> "StudyProtocolTitle":
        return cls(
            study_uid=study_definition_ar.uid,
            study_title=study_definition_ar.current_metadata.study_description.study_title,
            study_short_title=study_definition_ar.current_metadata.study_description.study_short_title,
            eudract_id=study_definition_ar.current_metadata.id_metadata.registry_identifiers.eudract_id,
            universal_trial_number_utn=study_definition_ar.current_metadata.id_metadata.registry_identifiers.universal_trial_number_utn,
            trial_phase_code=SimpleTermModel.from_ct_code(
                c_code=study_definition_ar.current_metadata.high_level_study_design.trial_phase_code,
                find_term_by_uid=find_term_by_uid,
            ),
            ind_number=study_definition_ar.current_metadata.id_metadata.registry_identifiers.investigational_new_drug_application_number_ind,
        )
