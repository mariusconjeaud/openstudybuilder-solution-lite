"""
Tests for /studies/{uid}/study-arms endpoints
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import logging

import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api.main import app
from clinical_mdr_api.models.study import Study
from clinical_mdr_api.tests.integration.utils.api import (
    drop_db,
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

log = logging.getLogger(__name__)

study: Study


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "studyarmapi"
    inject_and_clear_db(db_name)
    inject_base_data()
    global study
    study = TestUtils.create_study()

    yield
    drop_db(db_name)


def test_arm_modify_actions_on_locked_study(api_client):
    response = api_client.post(
        f"/studies/{study.uid}/study-arms",
        json={
            "name": "Arm_Name_1",
            "short_name": "Arm_Short_Name_1",
            "code": "Arm_code_1",
            "description": "desc...",
            "arm_colour": "arm_colour...",
            "randomization_group": "Randomization_Group_1",
            "number_of_subjects": 1,
        },
    )
    res = response.json()
    assert response.status_code == 201

    # get all arms
    response = api_client.get(
        f"/studies/{study.uid}/study-arms/audit-trail/",
        json={},
    )
    res = response.json()
    assert response.status_code == 200
    old_res = res
    arm_uid = res[0]["arm_uid"]

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
        f"/studies/{study.uid}/study-arms",
        json={
            "name": "Arm_Name_2",
            "short_name": "Arm_Short_Name_2",
            "code": "Arm_code_2",
            "description": "desc...",
            "arm_colour": "arm_colour...",
            "randomization_group": "Randomization_Group_2",
            "number_of_subjects": 2,
        },
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."
    # edit arm
    response = api_client.patch(
        f"/studies/{study.uid}/study-arms/{arm_uid}",
        json={
            "name": "New_Arm_Name_1",
        },
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    # get all history when was locked
    response = api_client.get(
        f"/studies/{study.uid}/study-arms/audit-trail/",
        json={},
    )
    res = response.json()
    assert response.status_code == 200
    assert old_res == res


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
def test_get_study_arms_csv_xml_excel(api_client, export_format):
    url = f"/studies/{study.uid}/study-arms"
    TestUtils.verify_exported_data_format(api_client, export_format, url)
