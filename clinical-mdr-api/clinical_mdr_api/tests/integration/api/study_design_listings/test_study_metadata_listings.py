# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api.config import STUDY_ENDPOINT_TP_NAME
from clinical_mdr_api.main import app
from clinical_mdr_api.models import study_selections
from clinical_mdr_api.services.studies.study import StudyService
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
    get_catalogue_name_library_name,
    input_metadata_in_study,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

study_number: str


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
    # Create CT Terms
    ct_term_inclusion_criteria = TestUtils.create_ct_term(
        sponsor_preferred_name="INCLUSION CRITERIA"
    )
    ct_term_exclusion_criteria = TestUtils.create_ct_term(
        sponsor_preferred_name="EXCLUSION CRITERIA"
    )

    # Create templates
    incl_criteria_template_1 = TestUtils.create_criteria_template(
        type_uid=ct_term_inclusion_criteria.term_uid
    )
    excl_criteria_template_1 = TestUtils.create_criteria_template(
        type_uid=ct_term_exclusion_criteria.term_uid
    )

    # Create study criterias
    TestUtils.create_study_criteria(
        study_uid=study_uid,
        criteria_template_uid=incl_criteria_template_1.uid,
        library_name=incl_criteria_template_1.library.name,
        parameter_terms=[],
    )

    TestUtils.create_study_criteria(
        study_uid=study_uid,
        criteria_template_uid=excl_criteria_template_1.uid,
        library_name=excl_criteria_template_1.library.name,
        parameter_terms=[],
    )

    # Create objective template
    objective_template = TestUtils.create_objective_template()
    TestUtils.create_study_objective(
        study_uid=study_uid,
        objective_template_uid=objective_template.uid,
        parameter_terms=[],
    )

    # Create study objectives
    study_objective = TestUtils.create_study_objective(
        study_uid=study_uid,
        objective_template_uid=objective_template.uid,
        library_name=objective_template.library.name,
        parameter_terms=[],
    )

    # Create endpoint templates
    TestUtils.create_template_parameter(STUDY_ENDPOINT_TP_NAME)
    endpoint_template = TestUtils.create_endpoint_template()

    unit_definitions = [
        TestUtils.create_unit_definition(name="unit1"),
        TestUtils.create_unit_definition(name="unit2"),
    ]
    unit_separator = "and"
    timeframe_template = TestUtils.create_timeframe_template()
    timeframe = TestUtils.create_timeframe(
        timeframe_template_uid=timeframe_template.uid
    )

    # Create study endpoints
    TestUtils.create_study_endpoint(
        study_uid=study_uid,
        endpoint_template_uid=endpoint_template.uid,
        endpoint_units=study_selections.study_selection.EndpointUnitsInput(
            units=[u.uid for u in unit_definitions], separator=unit_separator
        ),
        timeframe_uid=timeframe.uid,
        library_name=endpoint_template.library.name,
    )

    TestUtils.create_study_endpoint(
        study_uid=study_uid,
        endpoint_template_uid=endpoint_template.uid,
        library_name=endpoint_template.library.name,
        timeframe_uid=timeframe.uid,
        study_objective_uid=study_objective.study_objective_uid,
    )


def test_study_metadata_listing_api(api_client):
    response = api_client.get(
        f"/listings/studies/{study_number}/study-metadata",
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
            "post_auth_indicator": "True",
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
                "uid": "StudyArm_000001",
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
                "uid": "StudyArm_000003",
                "name": "Arm_Name_2",
                "short_name": "Arm_Short_Name_2",
                "code": "Arm_code_2",
                "number_of_subjects": 100,
                "description": "desc...",
                "randomization_group": "Arm_randomizationGroup2",
                "arm_type": "test",
                "connected_branches": [
                    {
                        "uid": "StudyBranchArm_000001",
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
                "uid": "StudyArm_000005",
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
                "uid": "StudyArm_000007",
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
                "uid": "StudyCohort_000001",
                "name": "Cohort_Name_1",
                "short_name": "Cohort_Short_Name_1",
                "code": "Cohort_code_1",
                "number_of_subjects": 100,
                "description": "desc...",
                "arm_uid": ["StudyArm_000001"],
                "branch_arm_uid": [],
            }
        ],
        "study_epochs": [
            {
                "uid": "StudyEpoch_000001",
                "name": "Epoch Subtype",
                "type": "test",
                "subtype": "test",
                "start_rule": "",
                "end_rule": "",
                "description": "",
            },
            {
                "uid": "StudyEpoch_000002",
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
                "uid": "StudyElement_000001",
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
                "uid": "StudyElement_000003",
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
                "arm_uid": "",
                "branch_arm_uid": "StudyBranchArm_000001",
                "epoch_uid": "StudyEpoch_000001",
                "element_uid": "StudyElement_000001",
            },
            {
                "arm_uid": "",
                "branch_arm_uid": "StudyBranchArm_000001",
                "epoch_uid": "StudyEpoch_000002",
                "element_uid": "StudyElement_000001",
            },
            {
                "arm_uid": "StudyArm_000001",
                "branch_arm_uid": "",
                "epoch_uid": "StudyEpoch_000002",
                "element_uid": "StudyElement_000003",
            },
            {
                "arm_uid": "StudyArm_000005",
                "branch_arm_uid": "",
                "epoch_uid": "StudyEpoch_000002",
                "element_uid": "StudyElement_000001",
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
        "study_criterias": [
            {"type": "code_submission_value-4207139844", "text": "ct-7574858067"},
            {"type": "code_submission_value-2326449895", "text": "ct-8900556670"},
        ],
        "study_objectives": [
            {"uid": "StudyObjective_000001", "type": "", "text": "ot-1973472967"},
            {"uid": "StudyObjective_000002", "type": "", "text": "ot-1973472967"},
        ],
        "study_endpoints": [
            {
                "uid": "StudyEndpoint_000003",
                "type": "",
                "sub_type": None,
                "text": "et-9780196775",
                "connected_objective": "StudyObjective_000002",
                "timeframe": "tt-5719443953",
                "endpoint_units": {"units": [], "separator": None},
            },
            {
                "uid": "StudyEndpoint_000001",
                "type": "",
                "sub_type": None,
                "text": "et-9780196775",
                "connected_objective": "",
                "timeframe": "tt-5719443953",
                "endpoint_units": {
                    "units": [
                        {"uid": "UnitDefinition_000003", "name": "unit1"},
                        {"uid": "UnitDefinition_000004", "name": "unit2"},
                    ],
                    "separator": "and",
                },
            },
        ],
    }
    assert res["study_title"] == expected_output["study_title"]
    assert res["registry_identifiers"] == expected_output["registry_identifiers"]
    assert res["study_type"] == expected_output["study_type"]
    assert res["study_attributes"] == expected_output["study_attributes"]
    assert res["study_population"] == expected_output["study_population"]
    assert res["study_arms"] == expected_output["study_arms"]
    assert res["study_cohorts"] == expected_output["study_cohorts"]
    assert res["study_epochs"] == expected_output["study_epochs"]
    assert res["study_elements"] == expected_output["study_elements"]
    assert res["study_design_matrix"] == expected_output["study_design_matrix"]
    assert res["study_visits"] == expected_output["study_visits"]
    assert len(res["study_criterias"]) == len(expected_output["study_criterias"])
    assert len(res["study_objectives"]) == len(expected_output["study_objectives"])
    assert len(res["study_endpoints"]) == len(expected_output["study_endpoints"])
