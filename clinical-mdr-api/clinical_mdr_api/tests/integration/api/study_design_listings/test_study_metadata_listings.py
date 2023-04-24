import unittest

import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api.main import app
from clinical_mdr_api.models.listings_study import (
    RegistryIdentifiersListingModel,
    StudyArmListingModel,
    StudyAttributesListingModel,
    StudyCohortListingModel,
    StudyDesignMatrixListingModel,
    StudyElementListingModel,
    StudyEpochListingModel,
    StudyMetadataListingModel,
    StudyPopulationListingModel,
    StudyTypeListingModel,
    StudyVisitListingModel,
)
from clinical_mdr_api.services.listings_study import StudyMetadataListingService
from clinical_mdr_api.services.study import StudyService
from clinical_mdr_api.services.study_epoch import StudyEpochService
from clinical_mdr_api.tests.integration.utils.api import inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import inject_base_data
from clinical_mdr_api.tests.integration.utils.method_library import (
    create_codelist,
    create_ct_term,
    create_some_visits,
    create_study_arm,
    create_study_branch_arm,
    create_study_cohort,
    create_study_design_cell,
    create_study_element,
    create_study_epoch_codelists_ret_cat_and_lib,
    generate_description_json_model,
    get_catalogue_name_library_name,
    high_level_study_design_json_model_to_vo,
    input_metadata_in_study,
    registry_identifiers_json_model_to_vo,
    study_intervention_json_model_to_vo,
    study_population_json_model_to_vo,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    inject_and_clear_db("StudyListingTestAPI")
    TestUtils.create_library(name="UCUM", is_editable=True)
    inject_base_data()
    codelist = TestUtils.create_ct_codelist()
    TestUtils.create_study_ct_data_map(codelist_uid=codelist.codelist_uid)
    study_service = StudyService(user="some_user")
    studies = study_service.get_all()
    study_uid = studies.items[0].uid
    global study_number
    study_number = studies.items[
        0
    ].current_metadata.identification_metadata.study_number
    # Inject study metadata
    input_metadata_in_study(study_uid)
    # Create study epochs
    create_study_epoch_codelists_ret_cat_and_lib(use_test_utils=True)
    catalogue_name, library_name = get_catalogue_name_library_name(use_test_utils=True)
    study_epoch = TestUtils.create_study_epoch(
        study_uid=study_uid, epoch_subtype="EpochSubType_0001"
    )
    study_epoch2 = TestUtils.create_study_epoch(
        study_uid=study_uid, epoch_subtype="EpochSubType_0002"
    )
    # Create study elements
    element_type_codelist = create_codelist(
        "Element Type", "CTCodelist_ElementType", catalogue_name, library_name
    )
    element_type_term = create_ct_term(
        element_type_codelist.codelist_uid,
        "Element Type",
        "ElementType_0001",
        1,
        catalogue_name,
        library_name,
    )
    element_type_term_2 = create_ct_term(
        element_type_codelist.codelist_uid,
        "Element Type",
        "ElementType_0002",
        2,
        catalogue_name,
        library_name,
    )
    study_elements = [
        create_study_element(element_type_term.uid, study_uid),
        create_study_element(element_type_term_2.uid, study_uid),
    ]

    # Create study arms
    codelist = create_codelist(
        name="Arm Type",
        uid="CTCodelist_00009",
        catalogue=catalogue_name,
        library=library_name,
    )
    arm_type = create_ct_term(
        codelist=codelist.codelist_uid,
        name="Arm Type",
        uid="ArmType_0001",
        order=1,
        catalogue_name=catalogue_name,
        library_name=library_name,
    )

    create_study_arm(
        study_uid=study_uid,
        name="Arm_Name_1",
        short_name="Arm_Short_Name_1",
        code="Arm_code_1",
        description="desc...",
        colour_code="colour...",
        randomization_group="Arm_randomizationGroup",
        number_of_subjects=100,
        arm_type_uid=arm_type.uid,
    )
    create_study_arm(
        study_uid=study_uid,
        name="Arm_Name_2",
        short_name="Arm_Short_Name_2",
        code="Arm_code_2",
        description="desc...",
        colour_code="colour...",
        randomization_group="Arm_randomizationGroup2",
        number_of_subjects=100,
        arm_type_uid=arm_type.uid,
    )
    create_study_arm(
        study_uid=study_uid,
        name="Arm_Name_3",
        short_name="Arm_Short_Name_3",
        code="Arm_code_3",
        description="desc...",
        colour_code="colour...",
        randomization_group="Arm_randomizationGroup3",
        number_of_subjects=100,
        arm_type_uid=arm_type.uid,
    )

    create_study_arm(
        study_uid=study_uid,
        name="Arm_Name_9",
        short_name="Arm_Short_Name_9",
        code="Arm_code_9",
        description="desc...",
        colour_code="colour...",
        randomization_group="Arm_randomizationGroup9",
        number_of_subjects=100,
        arm_type_uid=arm_type.uid,
    )

    # Create study design cells
    create_study_design_cell(
        study_element_uid=study_elements[0].element_uid,
        study_epoch_uid=study_epoch.uid,
        study_arm_uid="StudyArm_000003",
        study_uid=study_uid,
    )
    create_study_design_cell(
        study_element_uid=study_elements[0].element_uid,
        study_epoch_uid=study_epoch2.uid,
        study_arm_uid="StudyArm_000003",
        study_uid=study_uid,
    )

    create_study_design_cell(
        study_element_uid=study_elements[1].element_uid,
        study_epoch_uid=study_epoch2.uid,
        study_arm_uid="StudyArm_000001",
        study_uid=study_uid,
    )

    create_study_design_cell(
        study_element_uid=study_elements[0].element_uid,
        study_epoch_uid=study_epoch2.uid,
        study_arm_uid="StudyArm_000005",
        study_uid=study_uid,
    )

    # Create study branch arms
    create_study_branch_arm(
        study_uid=study_uid,
        name="Branch_Arm_Name_1",
        short_name="Branch_Arm_Short_Name_1",
        code="Branch_Arm_code_1",
        description="desc...",
        colour_code="colour...",
        randomization_group="Branch_Arm_randomizationGroup",
        number_of_subjects=100,
        arm_uid="StudyArm_000003",
    )

    # Create study cohort
    create_study_cohort(
        study_uid=study_uid,
        name="Cohort_Name_1",
        short_name="Cohort_Short_Name_1",
        code="Cohort_code_1",
        description="desc...",
        colour_code="desc...",
        number_of_subjects=100,
        arm_uids=["StudyArm_000001"],
    )

    # Create study visit
    create_some_visits(
        use_test_utils=True,
        create_epoch_codelist=False,
        study_uid=study_uid,
        epoch1=study_epoch,
        epoch2=study_epoch2,
    )


def test_study_metadata_listing_api(api_client):
    response = api_client.get(
        f"/listings/studies/{study_number}/study-metadata",
        json={},
    )
    assert response.status_code == 200
    res = response.json()
    assert res is not None

    expected_output = {
        "study_title": {
            "study_title": "Some Study Title for Testing",
            "study_short_title": "Some Study Short Title for Testing",
        },
        "registry_identifiers": {
            "ct_gov_id": "some ct gov id",
            "ct_gov_id_null_value_code": "",
            "eudract_id": "some eudtact id",
            "eudract_id_null_value_code": "",
            "universal_trial_number_utn": "some utn id",
            "universal_trial_number_utn_null_value_code": "",
            "japanese_trial_registry_id_japic": "some japic id",
            "japanese_trial_registry_id_japic_null_value_code": "",
            "investigational_new_drug_application_number_ind": "some ind id",
            "investigational_new_drug_application_number_ind_null_value_code": "",
        },
        "study_type": {
            "study_type_code": "",
            "study_type_null_value_code": "",
            "trial_type_codes": [],
            "trial_type_null_value_code": "",
            "trial_phase_code": "",
            "trial_phase_null_value_code": "",
            "is_extension_trial": "False",
            "is_extension_trial_null_value_code": "",
            "is_adaptive_design": "False",
            "is_adaptive_design_null_value_code": "",
            "study_stop_rules": "some stop rule",
            "study_stop_rules_null_value_code": "",
            "confirmed_response_minimum_duration": "",
            "confirmed_response_minimum_duration_null_value_code": "",
            "post_auth_indicator": True,
            "post_auth_indicator_null_value_code": "",
        },
        "study_attributes": {
            "intervention_type_code": "",
            "intervention_type_null_value_code": "",
            "add_on_to_existing_treatments": "False",
            "add_on_to_existing_treatments_null_value_code": "",
            "control_type_code": "",
            "control_type_null_value_code": "",
            "intervention_model_code": "",
            "intervention_model_null_value_code": "",
            "is_trial_randomised": "True",
            "is_trial_randomised_null_value_code": "",
            "stratification_factor": "Some stratification factors",
            "stratification_factor_null_value_code": "",
            "trial_blinding_schema_code": "",
            "trial_blinding_schema_null_value_code": "",
            "planned_study_length": "",
            "planned_study_length_null_value_code": "",
            "trial_intent_types_codes": [],
            "trial_intent_types_null_value_code": "",
        },
        "study_population": {
            "therapeutic_area_codes": [],
            "therapeutic_area_null_value_code": "",
            "disease_condition_or_indication_codes": [],
            "disease_condition_or_indication_null_value_code": "",
            "diagnosis_group_codes": [],
            "diagnosis_group_null_value_code": "",
            "sex_of_participants_code": "",
            "sex_of_participants_null_value_code": "",
            "rare_disease_indicator": "",
            "rare_disease_indicator_null_value_code": "",
            "healthy_subject_indicator": "",
            "healthy_subject_indicator_null_value_code": "",
            "planned_minimum_age_of_subjects": "",
            "planned_minimum_age_of_subjects_null_value_code": "",
            "planned_maximum_age_of_subjects": "",
            "planned_maximum_age_of_subjects_null_value_code": "",
            "stable_disease_minimum_duration": "",
            "stable_disease_minimum_duration_null_value_code": "",
            "pediatric_study_indicator": "",
            "pediatric_study_indicator_null_value_code": "",
            "pediatric_postmarket_study_indicator": "False",
            "pediatric_postmarket_study_indicator_null_value_code": "",
            "pediatric_investigation_plan_indicator": "True",
            "pediatric_investigation_plan_indicator_null_value_code": "",
            "relapse_criteria": "some criteria",
            "relapse_criteria_null_value_code": "",
            "number_of_expected_subjects": None,
            "number_of_expected_subjects_null_value_code": "",
        },
        "study_arms": [
            {
                "name": "Arm_Name_1",
                "short_name": "Arm_Short_Name_1",
                "code": "Arm_code_1",
                "number_of_subjects": 100,
                "description": "desc...",
                "randomization_group": "Arm_randomizationGroup",
                "arm_type": "test",
                "connected_branches": [],
            },
            {
                "name": "Arm_Name_2",
                "short_name": "Arm_Short_Name_2",
                "code": "Arm_code_2",
                "number_of_subjects": 100,
                "description": "desc...",
                "randomization_group": "Arm_randomizationGroup2",
                "arm_type": "test",
                "connected_branches": [
                    {
                        "name": "Branch_Arm_Name_1",
                        "short_name": "Branch_Arm_Short_Name_1",
                        "code": "Branch_Arm_code_1",
                        "number_of_subjects": 100,
                        "description": "desc...",
                        "randomization_group": "Branch_Arm_randomizationGroup",
                    }
                ],
            },
            {
                "name": "Arm_Name_3",
                "short_name": "Arm_Short_Name_3",
                "code": "Arm_code_3",
                "number_of_subjects": 100,
                "description": "desc...",
                "randomization_group": "Arm_randomizationGroup3",
                "arm_type": "test",
                "connected_branches": [],
            },
            {
                "name": "Arm_Name_9",
                "short_name": "Arm_Short_Name_9",
                "code": "Arm_code_9",
                "number_of_subjects": 100,
                "description": "desc...",
                "randomization_group": "Arm_randomizationGroup9",
                "arm_type": "test",
                "connected_branches": [],
            },
        ],
        "study_cohorts": [
            {
                "name": "Cohort_Name_1",
                "short_name": "Cohort_Short_Name_1",
                "code": "Cohort_code_1",
                "number_of_subjects": 100,
                "description": "desc...",
                "arm_root_codes": ["Arm_code_1"],
                "branch_arm_root_codes": [],
            }
        ],
        "study_epochs": [
            {
                "name": "Epoch Subtype",
                "type": "test",
                "subtype": "test",
                "start_rule": "",
                "end_rule": "",
                "description": "",
            },
            {
                "name": "Epoch Subtype1",
                "type": "test",
                "subtype": "test",
                "start_rule": "",
                "end_rule": "",
                "description": "",
            },
        ],
        "study_elements": [
            {
                "name": "Element_Name_1",
                "short_name": "Element_Short_Name_1",
                "type": "uid: Element_code_1 not found",
                "subtype": "test",
                "start_rule": "",
                "end_rule": "",
                "planned_duration": "",
                "description": "desc...",
            },
            {
                "name": "Element_Name_1",
                "short_name": "Element_Short_Name_1",
                "type": "uid: Element_code_1 not found",
                "subtype": "test",
                "start_rule": "",
                "end_rule": "",
                "planned_duration": "",
                "description": "desc...",
            },
        ],
        "study_design_matrix": [
            {
                "arm_code": "",
                "branch_arm_code": "Branch_Arm_code_1",
                "epoch_name": "Epoch Subtype",
                "element_name": "Element_Name_1",
            },
            {
                "arm_code": "",
                "branch_arm_code": "Branch_Arm_code_1",
                "epoch_name": "Epoch Subtype1",
                "element_name": "Element_Name_1",
            },
            {
                "arm_code": "Arm_code_1",
                "branch_arm_code": "",
                "epoch_name": "Epoch Subtype1",
                "element_name": "Element_Name_1",
            },
            {
                "arm_code": "Arm_code_3",
                "branch_arm_code": "",
                "epoch_name": "Epoch Subtype1",
                "element_name": "Element_Name_1",
            },
        ],
        "study_visits": [
            {
                "epoch_uid": "StudyEpoch_000001",
                "epoch_name": "Epoch Subtype",
                "visit_type": "BASELINE",
                "contact_model": "On Site Visit",
                "unique_visit_number": "100",
                "name": "Visit 1",
                "short_name": "V1",
                "study_day_number": 1,
                "visit_window_min": -1,
                "visit_window_max": 1,
                "window_unit": "day",
                "description": "description",
                "epoch_allocation": None,
                "start_rule": "start_rule",
                "end_rule": "end_rule",
            },
            {
                "epoch_uid": "StudyEpoch_000001",
                "epoch_name": "Epoch Subtype",
                "visit_type": "Visit Type2",
                "contact_model": "On Site Visit",
                "unique_visit_number": "200",
                "name": "Visit 2",
                "short_name": "V2",
                "study_day_number": 1,
                "visit_window_min": -1,
                "visit_window_max": 1,
                "window_unit": "day",
                "description": "description",
                "epoch_allocation": None,
                "start_rule": "start_rule",
                "end_rule": "end_rule",
            },
            {
                "epoch_uid": "StudyEpoch_000001",
                "epoch_name": "Epoch Subtype",
                "visit_type": "Visit Type2",
                "contact_model": "On Site Visit",
                "unique_visit_number": "300",
                "name": "Visit 3",
                "short_name": "V3",
                "study_day_number": 1,
                "visit_window_min": -1,
                "visit_window_max": 1,
                "window_unit": "day",
                "description": "description",
                "epoch_allocation": None,
                "start_rule": "start_rule",
                "end_rule": "end_rule",
            },
            {
                "epoch_uid": "StudyEpoch_000002",
                "epoch_name": "Epoch Subtype1",
                "visit_type": "BASELINE2",
                "contact_model": "On Site Visit",
                "unique_visit_number": "400",
                "name": "Visit 4",
                "short_name": "V4D1",
                "study_day_number": 1,
                "visit_window_min": -1,
                "visit_window_max": 1,
                "window_unit": "day",
                "description": "description",
                "epoch_allocation": None,
                "start_rule": "start_rule",
                "end_rule": "end_rule",
            },
            {
                "epoch_uid": "StudyEpoch_000001",
                "epoch_name": "Epoch Subtype",
                "visit_type": "Visit Type3",
                "contact_model": "On Site Visit",
                "unique_visit_number": "500",
                "name": "Visit 5",
                "short_name": "V5",
                "study_day_number": 1,
                "visit_window_min": -1,
                "visit_window_max": 1,
                "window_unit": "day",
                "description": "description",
                "epoch_allocation": None,
                "start_rule": "start_rule",
                "end_rule": "end_rule",
            },
            {
                "epoch_uid": "StudyEpoch_000002",
                "epoch_name": "Epoch Subtype1",
                "visit_type": "Visit Type2",
                "contact_model": "On Site Visit",
                "unique_visit_number": "410",
                "name": "Visit 4",
                "short_name": "V4D1",
                "study_day_number": 1,
                "visit_window_min": -1,
                "visit_window_max": 1,
                "window_unit": "day",
                "description": "description",
                "epoch_allocation": None,
                "start_rule": "start_rule",
                "end_rule": "end_rule",
            },
        ],
    }
    assert res == expected_output
