from clinical_mdr_api.domain.study_definition_aggregate.study_metadata import (
    StudyStatus,
    StudyVersionMetadataVO,
)
from clinical_mdr_api.models.study import (
    HighLevelStudyDesignJsonModel,
    RegistryIdentifiersJsonModel,
    StudyIdentificationMetadataJsonModel,
    StudyMetadataJsonModel,
    StudyPatchRequestJsonModel,
    StudyPopulationJsonModel,
    StudyVersionMetadataJsonModel,
)
from clinical_mdr_api.services.study import StudyService


def input_metadata_in_study(study_uid):
    study_service = StudyService(user="some_user")
    study_service.patch(
        uid=study_uid,
        dry=False,
        study_patch_request=generate_study_patch_request(),
    )


def generate_id_metadata() -> StudyIdentificationMetadataJsonModel:
    ri_data = RegistryIdentifiersJsonModel(
        ct_gov_id="some ct gov id",
        ct_gov_id_null_value_code=None,
        eudract_id="some eudtact id",
        eudract_id_null_value_code=None,
        universal_trial_number_utn="some utn id",
        universal_trial_number_utn_null_value_code=None,
        japanese_trial_registry_id_japic="some japic id",
        japanese_trial_registry_id_japic_null_value_code=None,
        investigational_new_drug_application_number_ind="some ind id",
        investigational_new_drug_application_number_ind_null_value_code=None,
    )

    return StudyIdentificationMetadataJsonModel(registry_identifiers=ri_data)


def generate_ver_metadata() -> StudyVersionMetadataJsonModel:
    result = StudyVersionMetadataVO(study_status=StudyStatus.DRAFT)
    return StudyVersionMetadataJsonModel.from_study_version_metadata_vo(result)


def generate_high_level_study_design() -> HighLevelStudyDesignJsonModel:
    return HighLevelStudyDesignJsonModel(
        study_type_code=None,
        study_type_null_value_code=None,
        trial_types_codes=None,
        trial_types_null_value_code=None,
        trial_phase_code=None,
        trial_phase_null_value_code=None,
        is_extension_trial=None,
        is_extension_trial_null_value_code=None,
        is_adaptive_design=None,
        is_adaptive_design_null_value_code=None,
        study_stop_rules="some stop rule",
        study_stop_rules_null_value_code=None,
        confirmed_response_minimum_duration=None,
        confirmed_response_minimum_duration_null_value_code=None,
        post_auth_indicator="True",
        post_auth_indicator_null_value_code=None,
    )


def generate_study_population() -> StudyPopulationJsonModel:
    return StudyPopulationJsonModel(
        therapeutic_areas_codes=None,
        therapeutic_areas_null_value_code=None,
        disease_conditions_or_indications_codes=None,
        disease_conditions_or_indications_null_value_code=None,
        diagnosis_groups_codes=None,
        diagnosis_groups_null_value_code=None,
        sex_of_participants_code=None,
        sex_of_participants_null_value_code=None,
        rare_disease_indicator=None,
        rare_disease_indicator_null_value_code=None,
        healthy_subject_indicator=None,
        healthy_subject_indicator_null_value_code=None,
        planned_minimum_age_of_subjects=None,
        planned_minimum_age_of_subjects_null_value_code=None,
        planned_maximum_age_of_subjects=None,
        planned_maximum_age_of_subjects_null_value_code=None,
        stable_disease_minimum_duration=None,
        stable_disease_minimum_duration_null_value_code=None,
        pediatric_study_indicator=None,
        pediatric_study_indicator_null_value_code=None,
        pediatric_postmarket_study_indicator=False,
        pediatric_postmarket_study_indicator_null_value_code=None,
        pediatric_investigation_plan_indicator=True,
        pediatric_investigation_plan_indicator_null_value_code=None,
        relapse_criteria="some criteria",
        relapse_criteria_null_value_code=None,
    )


def generate_study_metadata() -> StudyMetadataJsonModel:
    return StudyMetadataJsonModel(
        identification_metadata=generate_id_metadata(),
        version_metadata=generate_ver_metadata(),
        high_level_study_design=generate_high_level_study_design(),
        study_population=generate_study_population(),
    )


def generate_study_patch_request() -> StudyPatchRequestJsonModel:
    return StudyPatchRequestJsonModel(current_metadata=generate_study_metadata())
