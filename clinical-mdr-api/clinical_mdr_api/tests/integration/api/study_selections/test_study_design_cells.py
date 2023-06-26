"""
Tests for /studies/{uid}/study-design-cells endpoints
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import logging

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api import main
from clinical_mdr_api.models import CTTerm
from clinical_mdr_api.models.study_selections.study import Study
from clinical_mdr_api.models.study_selections.study_selection import StudySelectionArm
from clinical_mdr_api.tests.integration.utils.api import (
    drop_db,
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_CT_CATALOGUE_CYPHER,
    STARTUP_STUDY_LIST_CYPHER,
)
from clinical_mdr_api.tests.integration.utils.method_library import (
    create_codelist,
    create_ct_term,
    create_study_arm,
    create_study_epoch,
    create_study_epoch_codelists_ret_cat_and_lib,
    get_catalogue_name_library_name,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
study: Study
study_arm: StudySelectionArm
study_arm2: StudySelectionArm
element_type_term: CTTerm
epoch_uid: str


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(main.app)


@pytest.fixture(scope="module")
def test_data():
    # reload(study_epoch_domain_module)
    # reload(study_epoch_service_module)
    """Initialize test data"""
    db_name = "studydesigncellapi"
    inject_and_clear_db(db_name)
    inject_base_data()
    global study_arm
    global study_arm2
    global study
    study = TestUtils.create_study()
    db.cypher_query(STARTUP_STUDY_LIST_CYPHER)
    db.cypher_query(STARTUP_CT_CATALOGUE_CYPHER)

    catalogue_name, library_name = get_catalogue_name_library_name()
    # Create a study arm
    arm_type_codelist = create_codelist(
        "Arm Type", "CTCodelist_ArmType", catalogue_name, library_name
    )
    arm_type_term = create_ct_term(
        arm_type_codelist.codelist_uid,
        "Arm Type",
        "ArmType_0001",
        1,
        catalogue_name,
        library_name,
    )
    study_arm = create_study_arm(
        study_uid=study.uid,
        name="Arm_Name_1",
        short_name="Arm_Short_Name_1",
        code="Arm_code_1",
        description="desc...",
        colour_code="colour...",
        randomization_group="Randomization_Group_1",
        number_of_subjects=1,
        arm_type_uid=arm_type_term.uid,
    )
    study_arm2 = create_study_arm(
        study_uid=study.uid,
        name="Arm_Name_2",
        short_name="Arm_Short_Name_2",
        code="Arm_code_2",
        description="desc...",
        colour_code="colour...",
        randomization_group="Randomization_Group_2",
        number_of_subjects=1,
        arm_type_uid=arm_type_term.uid,
    )
    create_study_epoch_codelists_ret_cat_and_lib()
    study_epoch = create_study_epoch("EpochSubType_0001", study_uid=study.uid)
    global epoch_uid
    epoch_uid = study_epoch.uid
    element_type_codelist = create_codelist(
        "Element Type", "CTCodelist_ElementType", catalogue_name, library_name
    )
    global element_type_term
    element_type_term = create_ct_term(
        element_type_codelist.codelist_uid,
        "Element Type",
        "ElementType_0001",
        1,
        catalogue_name,
        library_name,
    )
    yield

    drop_db(db_name)


def test_design_cell_modify_actions_on_locked_study(api_client):
    response = api_client.post(
        f"/studies/{study.uid}/study-elements",
        json={
            "name": "Element_Name_1",
            "short_name": "Element_Short_Name_1",
            "element_subtype_uid": element_type_term.uid,
        },
    )
    res = response.json()
    element_uid = res["element_uid"]
    assert response.status_code == 201

    response = api_client.post(
        f"/studies/{study.uid}/study-design-cells",
        json={
            "study_arm_uid": study_arm.arm_uid,
            "study_epoch_uid": epoch_uid,
            "study_element_uid": element_uid,
            "transition_rule": "Transition_Rule_1",
        },
    )
    res = response.json()
    # design_cell_uid = res['design_cell_uid']
    assert response.status_code == 201

    # get all design-cell
    response = api_client.get(
        f"/studies/{study.uid}/study-design-cells/audit-trail/",
    )
    res = response.json()
    assert response.status_code == 200
    old_res = res
    design_cell_uid = res[0]["study_design_cell_uid"]

    # update study title to be able to lock it
    response = api_client.patch(
        f"/studies/{study.uid}",
        json={"current_metadata": {"study_description": {"study_title": "new title"}}},
    )
    assert response.status_code == 200

    # Lock
    response = api_client.post(
        f"/studies/{study.uid}/lock",
        json={"change_description": "Lock 1"},
    )
    assert response.status_code == 201

    response = api_client.post(
        f"/studies/{study.uid}/study-design-cells",
        json={
            "study_arm_uid": study_arm2.arm_uid,
            "study_epoch_uid": epoch_uid,
            "study_element_uid": element_uid,
            "transition_rule": "Transition_Rule_1",
        },
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    # edit epoch
    response = api_client.post(
        f"/studies/{study.uid}/study-design-cells/batch",
        json=[
            {
                "method": "PATCH",
                "content": {
                    "study_design_cell_uid": design_cell_uid,
                    "study_arm_uid": study_arm2.arm_uid,
                    "study_epoch_uid": epoch_uid,
                    "study_element_uid": element_uid,
                    "transition_rule": "Transition_Rule_1",
                },
            }
        ],
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    # get all history when was locked
    response = api_client.get(
        f"/studies/{study.uid}/study-design-cells/audit-trail/",
    )
    res = response.json()
    assert response.status_code == 200
    assert old_res == res
