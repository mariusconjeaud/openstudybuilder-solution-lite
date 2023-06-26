"""
Tests for /studies/{uid}/study-activities endpoints
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

from clinical_mdr_api.main import app
from clinical_mdr_api.models.study_selections.study import Study
from clinical_mdr_api.tests.integration.utils.api import (
    drop_db,
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_ACTIVITIES,
    STARTUP_ACTIVITY_GROUPS,
    STARTUP_ACTIVITY_SUB_GROUPS,
    STARTUP_CT_CATALOGUE_CYPHER,
    STARTUP_STUDY_LIST_CYPHER,
    get_codelist_with_term_cypher,
)
from clinical_mdr_api.tests.integration.utils.factory_visit import (
    generate_default_input_data_for_visit,
)
from clinical_mdr_api.tests.integration.utils.method_library import (
    create_library_data,
    create_study_epoch,
    create_study_visit_codelists,
    get_unit_uid_by_name,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

log = logging.getLogger(__name__)

study: Study
epoch_uid: str
DAYUID: str
visits_basic_data: str


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "studyactivityapi"
    inject_and_clear_db(db_name)
    inject_base_data()
    global study
    study = TestUtils.create_study()

    db.cypher_query(STARTUP_ACTIVITY_GROUPS)
    db.cypher_query(STARTUP_ACTIVITY_SUB_GROUPS)
    db.cypher_query(STARTUP_ACTIVITIES)
    db.cypher_query(
        get_codelist_with_term_cypher(
            "EFFICACY", "Flowchart Group", term_uid="term_efficacy_uid"
        )
    )
    db.cypher_query(STARTUP_STUDY_LIST_CYPHER)
    db.cypher_query(STARTUP_CT_CATALOGUE_CYPHER)
    create_library_data()
    create_study_visit_codelists(create_unit_definitions=False)
    study_epoch = create_study_epoch("EpochSubType_0001", study_uid=study.uid)
    global epoch_uid
    epoch_uid = study_epoch.uid
    global DAYUID
    DAYUID = get_unit_uid_by_name("day")
    global visits_basic_data
    visits_basic_data = generate_default_input_data_for_visit().copy()
    yield
    drop_db(db_name)


def test_activity_modify_actions_on_locked_study(api_client):
    response = api_client.post(
        f"/studies/{study.uid}/study-activities",
        json={
            "activity_uid": "activity_root1",
            "flowchart_group_uid": "term_efficacy_uid",
        },
    )
    res = response.json()
    assert response.status_code == 201

    # get all activities
    response = api_client.get(
        f"/studies/{study.uid}/study-activities/audit-trail/",
    )
    res = response.json()
    assert response.status_code == 200
    old_res = res
    activity_uid = res[0]["study_activity_uid"]

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
        f"/studies/{study.uid}/study-activities",
        json={
            "activity_uid": "activity_root2",
            "flowchart_group_uid": "term_efficacy_uid",
        },
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."
    # edit activity
    response = api_client.patch(
        f"/studies/{study.uid}/study-activities/{activity_uid}",
        json={"note": "This is a note", "flowchart_group_uid": "term_efficacy_uid"},
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    # get all history when was locked
    response = api_client.get(
        f"/studies/{study.uid}/study-activities/audit-trail/",
    )
    res = response.json()
    assert response.status_code == 200
    assert old_res == res


def test_cascade_delete_on_activities_schedules(api_client):
    # Unlock
    response = api_client.post(f"/studies/{study.uid}/unlock")
    assert response.status_code == 201

    # get all activities
    response = api_client.get(
        f"/studies/{study.uid}/study-activities/audit-trail/",
    )
    res = response.json()
    assert response.status_code == 200
    activity_uid = res[0]["study_activity_uid"]

    # create visit
    inputs = {
        "study_epoch_uid": epoch_uid,
        "visit_type_uid": "VisitType_0001",
        "show_visit": True,
        "time_reference_uid": "VisitSubType_0001",
        "time_value": 0,
        "time_unit_uid": DAYUID,
        "visit_class": "SINGLE_VISIT",
        "visit_subclass": "SINGLE_VISIT",
        "is_global_anchor_visit": True,
    }
    datadict = visits_basic_data
    datadict.update(inputs)
    response = api_client.post(
        f"/studies/{study.uid}/study-visits",
        json=datadict,
    )
    res = response.json()
    assert response.status_code == 201

    # add activity schedule
    response = api_client.post(
        f"/studies/{study.uid}/study-activity-schedules",
        json={
            "study_activity_uid": activity_uid,
            "study_visit_uid": res["uid"],
        },
    )
    res = response.json()
    assert response.status_code == 201

    # delete activity
    response = api_client.delete(
        f"/studies/{study.uid}/study-activities/{activity_uid}",
    )
    assert response.status_code == 204

    # check if the activities schedules have been deleted
    response = api_client.get(
        f"/studies/{study.uid}/study-activity-schedules/",
    )
    res = response.json()
    assert response.status_code == 200
    assert res == []


@pytest.mark.parametrize(
    "export_format",
    [
        pytest.param("text/csv"),
        pytest.param("text/xml"),
        pytest.param(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    ],
)
def test_get_study_activities_csv_xml_excel(api_client, export_format):
    url = f"/studies/{study.uid}/study-activities"
    TestUtils.verify_exported_data_format(api_client, export_format, url)
