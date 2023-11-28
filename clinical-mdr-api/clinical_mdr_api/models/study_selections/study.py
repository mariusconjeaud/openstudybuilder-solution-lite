"""Study model."""
from datetime import datetime
from decimal import Decimal
from typing import Callable, Collection, Iterable, Self

from pydantic import Field

from clinical_mdr_api import exceptions
from clinical_mdr_api.domains.clinical_programmes.clinical_programme import (
    ClinicalProgrammeAR,
)
from clinical_mdr_api.domains.concepts.unit_definitions.unit_definition import (
    UnitDefinitionAR,
)
from clinical_mdr_api.domains.controlled_terminologies.ct_term_name import CTTermNameAR
from clinical_mdr_api.domains.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domains.projects.project import ProjectAR
from clinical_mdr_api.domains.study_definition_aggregates.registry_identifiers import (
    RegistryIdentifiersVO,
)
from clinical_mdr_api.domains.study_definition_aggregates.root import StudyDefinitionAR
from clinical_mdr_api.domains.study_definition_aggregates.study_metadata import (
    HighLevelStudyDesignVO,
    StudyDescriptionVO,
    StudyFieldAuditTrailEntryAR,
    StudyIdentificationMetadataVO,
    StudyInterventionVO,
    StudyMetadataVO,
    StudyPopulationVO,
    StudyStatus,
    StudyVersionMetadataVO,
)
from clinical_mdr_api.models.controlled_terminologies.ct_term import SimpleTermModel
from clinical_mdr_api.models.study_selections.duration import DurationJsonModel
from clinical_mdr_api.models.utils import BaseModel


class StudyPreferredTimeUnit(BaseModel):
    class Config:
        orm_mode = True

    study_uid: str = Field(
        ...,
        description="Uid of study",
        source="has_time_field.latest_value.uid",
    )
    time_unit_uid: str = Field(
        ...,
        description="Uid of time unit",
        source="has_unit_definition.uid",
    )
    time_unit_name: str = Field(
        ...,
        description="Name of time unit",
        source="has_unit_definition.has_latest_value.name",
    )


class StudyPreferredTimeUnitInput(BaseModel):
    unit_definition_uid: str = Field(
        ...,
        description="Uid of preferred time unit",
    )


class RegistryIdentifiersJsonModel(BaseModel):
    class Config:
        title = "RegistryIdentifiersMetadata"
        description = "RegistryIdentifiersMetadata metadata for study definition."

    ct_gov_id: str | None = Field(None, nullable=True)
    ct_gov_id_null_value_code: SimpleTermModel | None = Field(None, nullable=True)
    eudract_id: str | None = Field(None, nullable=True)
    eudract_id_null_value_code: SimpleTermModel | None = Field(None, nullable=True)
    universal_trial_number_utn: str | None = Field(None, nullable=True)
    universal_trial_number_utn_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )
    japanese_trial_registry_id_japic: str | None = Field(None, nullable=True)
    japanese_trial_registry_id_japic_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )
    investigational_new_drug_application_number_ind: str | None = Field(
        None, nullable=True
    )
    investigational_new_drug_application_number_ind_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    @classmethod
    def from_study_registry_identifiers_vo(
        cls,
        registry_identifiers_vo: RegistryIdentifiersVO,
        find_term_by_uid: Callable[[str], CTTermNameAR | None],
    ) -> Self:
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

    study_number: str | None = Field(None, nullable=True)
    study_acronym: str | None = Field(None, nullable=True)
    project_number: str | None = Field(None, nullable=True)
    project_name: str | None = Field(None, nullable=True)
    clinical_programme_name: str | None = Field(None, nullable=True)
    study_id: str | None = Field(None, nullable=True)
    registry_identifiers: RegistryIdentifiersJsonModel | None = Field(
        None, nullable=True
    )

    @classmethod
    def from_study_identification_vo(
        cls,
        study_identification_o: StudyIdentificationMetadataVO | None,
        find_project_by_project_number: Callable[[str], ProjectAR],
        find_clinical_programme_by_uid: Callable[[str], ClinicalProgrammeAR],
        find_term_by_uid: Callable[[str], CTTermNameAR | None],
    ) -> Self | None:
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


class CompactStudyIdentificationMetadataJsonModel(BaseModel):
    class Config:
        title = "CompactStudyIdentificationMetadata"
        description = "Identification metadata for study definition."

    study_number: str | None = Field(None, nullable=True)
    study_acronym: str | None = Field(None, nullable=True)
    project_number: str | None = Field(None, nullable=True)
    project_name: str | None = Field(None, nullable=True)
    clinical_programme_name: str | None = Field(None, nullable=True)
    study_id: str | None = Field(None, nullable=True)

    @classmethod
    def from_study_identification_vo(
        cls,
        study_identification_o: StudyIdentificationMetadataVO | None,
        find_project_by_project_number: Callable[[str], ProjectAR],
        find_clinical_programme_by_uid: Callable[[str], ClinicalProgrammeAR],
    ) -> Self | None:
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
        )


class StudyVersionMetadataJsonModel(BaseModel):
    class Config:
        title = "StudyVersionMetadata"
        description = "Version metadata for study definition."

    study_status: str | None = Field(None, nullable=True)
    version_number: Decimal | None = Field(None, nullable=True)
    version_timestamp: datetime | None = Field(None, remove_from_wildcard=True)
    version_author: str | None = Field(None, nullable=True)
    version_description: str | None = Field(None, nullable=True)

    @classmethod
    def from_study_version_metadata_vo(
        cls, study_version_metadata_vo: StudyVersionMetadataVO | None
    ) -> Self | None:
        if study_version_metadata_vo is None:
            return None
        return cls(
            study_status=study_version_metadata_vo.study_status.value,
            version_number=study_version_metadata_vo.version_number,
            version_timestamp=study_version_metadata_vo.version_timestamp,
            version_author=study_version_metadata_vo.version_author,
            version_description=study_version_metadata_vo.version_description,
        )


class HighLevelStudyDesignJsonModel(BaseModel):
    class Config:
        title = "high_level_study_design"
        description = "High level study design parameters for study definition."

    study_type_code: SimpleTermModel | None = Field(None, nullable=True)
    study_type_null_value_code: SimpleTermModel | None = Field(None, nullable=True)

    trial_type_codes: list[SimpleTermModel] | None = Field(None, nullable=True)
    trial_type_null_value_code: SimpleTermModel | None = Field(None, nullable=True)

    trial_phase_code: SimpleTermModel | None = Field(None, nullable=True)
    trial_phase_null_value_code: SimpleTermModel | None = Field(None, nullable=True)

    is_extension_trial: bool | None = Field(None, nullable=True)
    is_extension_trial_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    is_adaptive_design: bool | None = Field(None, nullable=True)
    is_adaptive_design_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    study_stop_rules: str | None = Field(None, nullable=True)
    study_stop_rules_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    confirmed_response_minimum_duration: DurationJsonModel | None = Field(
        None, nullable=True
    )
    confirmed_response_minimum_duration_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    post_auth_indicator: bool | None = Field(None, nullable=True)
    post_auth_indicator_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    @classmethod
    def from_high_level_study_design_vo(
        cls,
        high_level_study_design_vo: HighLevelStudyDesignVO | None,
        find_term_by_uid: Callable[[str], CTTermNameAR | None],
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
    ) -> Self | None:
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
            trial_type_codes=[
                SimpleTermModel.from_ct_code(
                    c_code=trial_type_code, find_term_by_uid=find_term_by_uid
                )
                for trial_type_code in high_level_study_design_vo.trial_type_codes
            ],
            trial_type_null_value_code=SimpleTermModel.from_ct_code(
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
        title = "study_population"
        description = "Study population parameters for study definition."

    therapeutic_area_codes: list[SimpleTermModel] | None = Field(None, nullable=True)
    therapeutic_area_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    disease_condition_or_indication_codes: list[SimpleTermModel] | None = Field(
        None, nullable=True
    )
    disease_condition_or_indication_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    diagnosis_group_codes: list[SimpleTermModel] | None = Field(None, nullable=True)
    diagnosis_group_null_value_code: SimpleTermModel | None = Field(None, nullable=True)

    sex_of_participants_code: SimpleTermModel | None = Field(None, nullable=True)
    sex_of_participants_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    rare_disease_indicator: bool | None = Field(None, nullable=True)
    rare_disease_indicator_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    healthy_subject_indicator: bool | None = Field(None, nullable=True)
    healthy_subject_indicator_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    planned_minimum_age_of_subjects: DurationJsonModel | None = Field(
        None, nullable=True
    )
    planned_minimum_age_of_subjects_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    planned_maximum_age_of_subjects: DurationJsonModel | None = Field(
        None, nullable=True
    )
    planned_maximum_age_of_subjects_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    stable_disease_minimum_duration: DurationJsonModel | None = Field(
        None, nullable=True
    )
    stable_disease_minimum_duration_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    pediatric_study_indicator: bool | None = Field(None, nullable=True)
    pediatric_study_indicator_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    pediatric_postmarket_study_indicator: bool | None = Field(None, nullable=True)
    pediatric_postmarket_study_indicator_null_value_code: SimpleTermModel | None = (
        Field(None, nullable=True)
    )

    pediatric_investigation_plan_indicator: bool | None = Field(None, nullable=True)
    pediatric_investigation_plan_indicator_null_value_code: SimpleTermModel | None = (
        Field(None, nullable=True)
    )

    relapse_criteria: str | None = Field(None, nullable=True)
    relapse_criteria_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    number_of_expected_subjects: int | None = Field(None, nullable=True)
    number_of_expected_subjects_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    @classmethod
    def from_study_population_vo(
        cls,
        study_population_vo: StudyPopulationVO | None,
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
        find_term_by_uid: Callable[[str], CTTermNameAR | None],
        find_dictionary_term_by_uid: Callable[[str], DictionaryTermAR | None],
    ) -> Self | None:
        if study_population_vo is None:
            return None
        return cls(
            therapeutic_area_codes=[
                SimpleTermModel.from_ct_code(
                    c_code=therapeutic_area_code,
                    find_term_by_uid=find_dictionary_term_by_uid,
                )
                for therapeutic_area_code in study_population_vo.therapeutic_area_codes
            ],
            therapeutic_area_null_value_code=SimpleTermModel.from_ct_code(
                c_code=study_population_vo.therapeutic_area_null_value_code,
                find_term_by_uid=find_term_by_uid,
            ),
            disease_condition_or_indication_codes=[
                SimpleTermModel.from_ct_code(
                    c_code=disease_or_indication_code,
                    find_term_by_uid=find_dictionary_term_by_uid,
                )
                for disease_or_indication_code in study_population_vo.disease_condition_or_indication_codes
            ],
            disease_condition_or_indication_null_value_code=(
                SimpleTermModel.from_ct_code(
                    c_code=study_population_vo.disease_condition_or_indication_null_value_code,
                    find_term_by_uid=find_term_by_uid,
                )
            ),
            diagnosis_group_codes=[
                SimpleTermModel.from_ct_code(
                    c_code=diagnosis_group_code,
                    find_term_by_uid=find_dictionary_term_by_uid,
                )
                for diagnosis_group_code in study_population_vo.diagnosis_group_codes
            ],
            diagnosis_group_null_value_code=SimpleTermModel.from_ct_code(
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
        title = "study_intervention"
        description = "Study interventions parameters for study definition."

    intervention_type_code: SimpleTermModel | None = Field(None, nullable=True)
    intervention_type_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    add_on_to_existing_treatments: bool | None = Field(None, nullable=True)
    add_on_to_existing_treatments_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    control_type_code: SimpleTermModel | None = Field(None, nullable=True)
    control_type_null_value_code: SimpleTermModel | None = Field(None, nullable=True)

    intervention_model_code: SimpleTermModel | None = Field(None, nullable=True)
    intervention_model_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    is_trial_randomised: bool | None = Field(None, nullable=True)
    is_trial_randomised_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    stratification_factor: str | None = Field(None, nullable=True)
    stratification_factor_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    trial_blinding_schema_code: SimpleTermModel | None = Field(None, nullable=True)
    trial_blinding_schema_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    planned_study_length: DurationJsonModel | None = Field(None, nullable=True)
    planned_study_length_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    trial_intent_types_codes: list[SimpleTermModel] | None = Field(None, nullable=True)
    trial_intent_types_null_value_code: SimpleTermModel | None = Field(
        None, nullable=True
    )

    @classmethod
    def from_study_intervention_vo(
        cls,
        study_intervention_vo: StudyInterventionVO | None,
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
        find_term_by_uid: Callable[[str], CTTermNameAR | None],
    ) -> Self | None:
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
        title = "study_description"
        description = "Study description for the study definition."

    study_title: str | None = Field(None, nullable=True)
    study_short_title: str | None = Field(None, nullable=True)

    @classmethod
    def from_study_description_vo(
        cls, study_description_vo: StudyDescriptionVO | None
    ) -> Self | None:
        if study_description_vo is None:
            return None
        return cls(
            study_title=study_description_vo.study_title,
            study_short_title=study_description_vo.study_short_title,
        )


class CompactStudyMetadataJsonModel(BaseModel):
    class Config:
        title = "StudyMetadata"
        description = "Study metadata"

    identification_metadata: CompactStudyIdentificationMetadataJsonModel | None = Field(
        None, nullable=True
    )
    version_metadata: StudyVersionMetadataJsonModel | None = Field(None, nullable=True)

    @classmethod
    def from_study_metadata_vo(
        cls,
        study_metadata_vo: StudyMetadataVO,
        find_project_by_project_number: Callable[[str], ProjectAR],
        find_clinical_programme_by_uid: Callable[[str], ClinicalProgrammeAR],
    ) -> Self:
        return cls(
            identification_metadata=CompactStudyIdentificationMetadataJsonModel.from_study_identification_vo(
                study_identification_o=study_metadata_vo.id_metadata,
                find_project_by_project_number=find_project_by_project_number,
                find_clinical_programme_by_uid=find_clinical_programme_by_uid,
            ),
            version_metadata=StudyVersionMetadataJsonModel.from_study_version_metadata_vo(
                study_version_metadata_vo=study_metadata_vo.ver_metadata
            ),
        )


class StudyMetadataJsonModel(BaseModel):
    class Config:
        title = "StudyMetadata"
        description = "Study metadata"

    identification_metadata: StudyIdentificationMetadataJsonModel | None = Field(
        None, nullable=True
    )
    version_metadata: StudyVersionMetadataJsonModel | None = Field(None, nullable=True)
    high_level_study_design: HighLevelStudyDesignJsonModel | None = Field(
        None, nullable=True
    )
    study_population: StudyPopulationJsonModel | None = Field(None, nullable=True)
    study_intervention: StudyInterventionJsonModel | None = Field(None, nullable=True)
    study_description: StudyDescriptionJsonModel | None = Field(None, nullable=True)

    @classmethod
    def from_study_metadata_vo(
        cls,
        study_metadata_vo: StudyMetadataVO,
        find_project_by_project_number: Callable[[str], ProjectAR],
        find_clinical_programme_by_uid: Callable[[str], ClinicalProgrammeAR],
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
        find_term_by_uid: Callable[[str], CTTermNameAR | None],
        find_dictionary_term_by_uid: Callable[[str], DictionaryTermAR | None],
    ) -> Self:
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

    current_metadata: StudyMetadataJsonModel | None = Field(None, nullable=True)


class CompactStudy(BaseModel):
    uid: str = Field(
        title="uid",
        description="The unique id of the study.",
        remove_from_wildcard=True,
    )
    possible_actions: list[str] = Field(
        ...,
        description=(
            "Holds those actions that can be performed on the ActivityInstances. "
            "Actions are: 'lock', 'release', 'unlock', 'delete'."
        ),
    )
    current_metadata: CompactStudyMetadataJsonModel | None = Field(None, nullable=True)

    @classmethod
    def from_study_definition_ar(
        cls,
        study_definition_ar: StudyDefinitionAR,
        find_project_by_project_number: Callable[[str], ProjectAR],
        find_clinical_programme_by_uid: Callable[[str], ClinicalProgrammeAR],
    ) -> Self:
        return cls(
            uid=study_definition_ar.uid,
            possible_actions=sorted(
                [_.value for _ in study_definition_ar.get_possible_actions()]
            ),
            current_metadata=CompactStudyMetadataJsonModel.from_study_metadata_vo(
                study_metadata_vo=study_definition_ar.current_metadata,
                find_project_by_project_number=find_project_by_project_number,
                find_clinical_programme_by_uid=find_clinical_programme_by_uid,
            ),
        )


class Study(BaseModel):
    uid: str = Field(
        title="uid",
        description="The unique id of the study.",
    )
    possible_actions: list[str] = Field(
        ...,
        description=(
            "Holds those actions that can be performed on the ActivityInstances. "
            "Actions are: 'lock', 'release', 'unlock', 'delete'."
        ),
    )
    current_metadata: StudyMetadataJsonModel | None = Field(None, nullable=True)

    @classmethod
    def from_study_definition_ar(
        cls,
        study_definition_ar: StudyDefinitionAR,
        find_project_by_project_number: Callable[[str], ProjectAR],
        find_clinical_programme_by_uid: Callable[[str], ClinicalProgrammeAR],
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
        find_term_by_uid: Callable[[str], CTTermNameAR | None],
        find_dictionary_term_by_uid: Callable[[str], DictionaryTermAR | None],
        # pylint: disable=unused-argument
        at_specified_date_time: datetime | None = None,
        study_value_version: str | None = None,
        status: StudyStatus | None = None,
        history_endpoint: bool = False,
    ) -> Self | None:
        current_metadata = None
        if status is not None:
            if status == StudyStatus.DRAFT:
                current_metadata = study_definition_ar.draft_metadata
            elif status == StudyStatus.RELEASED:
                current_metadata = study_definition_ar.released_metadata
            elif status == StudyStatus.LOCKED:
                current_metadata = study_definition_ar.latest_locked_metadata
        elif study_value_version is not None:
            current_metadata = study_definition_ar.version_specific_metadata
        else:
            current_metadata = study_definition_ar.current_metadata
        if current_metadata is None:
            if not history_endpoint:
                raise exceptions.ValidationException(
                    f"Study {study_definition_ar.uid} doesn't have a version for status={status} version={study_value_version}"
                )
            return None
        is_metadata_the_last_one = bool(
            study_definition_ar.current_metadata == current_metadata
        )
        return cls(
            uid=study_definition_ar.uid,
            possible_actions=sorted(
                [_.value for _ in study_definition_ar.get_possible_actions()]
                if is_metadata_the_last_one
                else []
            ),
            current_metadata=StudyMetadataJsonModel.from_study_metadata_vo(
                study_metadata_vo=current_metadata,
                find_project_by_project_number=find_project_by_project_number,
                find_clinical_programme_by_uid=find_clinical_programme_by_uid,
                find_all_study_time_units=find_all_study_time_units,
                find_term_by_uid=find_term_by_uid,
                find_dictionary_term_by_uid=find_dictionary_term_by_uid,
            ),
        )


class StudyCreateInput(BaseModel):
    study_number: str | None = Field(
        # ...,
        title="study_number",
        description="",
    )

    study_acronym: str | None = Field(
        # ...,
        title="study_acronym",
        description="",
    )

    project_number: str | None = Field(
        # ...,
        title="project_number",
        description="",
    )


class StatusChangeDescription(BaseModel):
    change_description: str = Field(
        ...,
        title="Change description",
        description="The description of the Study status change.",
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

    actions: list[StudyFieldAuditTrailAction] = Field(
        None,
        title="actions",
        description="The actions that took place as part of this audit trial entry.",
    )

    @classmethod
    def from_study_field_audit_trail_vo(
        cls,
        study_field_audit_trail_vo: StudyFieldAuditTrailEntryAR,
        sections_selected: Collection[str],
        find_term_by_uid: Callable[[str], CTTermNameAR | None],
    ) -> Self:
        actions: list[StudyFieldAuditTrailAction] = [
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
    study_title: str | None = Field(None, nullable=True)
    study_short_title: str | None = Field(None, nullable=True)
    eudract_id: str | None = Field(None, nullable=True)
    universal_trial_number_utn: str | None = Field(None, nullable=True)
    trial_phase_code: SimpleTermModel | None = Field(None, nullable=True)
    ind_number: str | None = Field(None, nullable=True)
    substance_name: str | None = Field(None, nullable=True)

    @classmethod
    def from_study_definition_ar(
        cls,
        study_definition_ar: StudyDefinitionAR,
        find_term_by_uid: Callable[[str], CTTermNameAR | None],
        study_value_version: str | None = None,
    ) -> Self:
        if study_value_version is not None:
            current_metadata = study_definition_ar.version_specific_metadata
        else:
            current_metadata = study_definition_ar.current_metadata
        return cls(
            study_uid=study_definition_ar.uid,
            study_title=current_metadata.study_description.study_title,
            study_short_title=current_metadata.study_description.study_short_title,
            eudract_id=current_metadata.id_metadata.registry_identifiers.eudract_id,
            universal_trial_number_utn=current_metadata.id_metadata.registry_identifiers.universal_trial_number_utn,
            trial_phase_code=SimpleTermModel.from_ct_code(
                c_code=current_metadata.high_level_study_design.trial_phase_code,
                find_term_by_uid=find_term_by_uid,
            ),
            ind_number=current_metadata.id_metadata.registry_identifiers.investigational_new_drug_application_number_ind,
        )
