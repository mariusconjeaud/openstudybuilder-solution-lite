"""
Tests for /studies endpoints
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import logging
from typing import List

import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api.main import app
from clinical_mdr_api.models import UnitDefinitionModel
from clinical_mdr_api.models.study_selections.study import Study
from clinical_mdr_api.tests.integration.utils.api import (
    drop_db,
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
studies_all: List[Study]
study: Study

day_unit_definition: UnitDefinitionModel
week_unit_definition: UnitDefinitionModel


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "studies.api"
    inject_and_clear_db(db_name)
    inject_base_data()
    global day_unit_definition
    day_unit_definition = TestUtils.get_unit_by_uid(
        unit_uid=TestUtils.get_unit_uid_by_name(unit_name="day")
    )
    global week_unit_definition
    week_unit_definition = TestUtils.get_unit_by_uid(
        unit_uid=TestUtils.get_unit_uid_by_name(unit_name="week")
    )

    global study
    study = TestUtils.create_study()

    yield

    drop_db(db_name)


def test_study_delete_successful(api_client):
    study_to_delete = TestUtils.create_study()
    response = api_client.delete(f"/studies/{study_to_delete.uid}")
    assert response.status_code == 204

    response = api_client.get("/studies", params={"deleted": True})
    assert response.status_code == 200
    res = response.json()
    assert len(res["items"]) == 1
    assert res["items"][0]["uid"] == study_to_delete.uid

    # try to update the deleted study
    response = api_client.patch(
        f"/studies/{study_to_delete.uid}",
        json={"current_metadata": {"study_description": {"study_title": "new title"}}},
    )
    assert response.status_code == 400
    res = response.json()
    assert res["message"] == f"Study {study_to_delete.uid} is deleted."


def test_get_snapshot_history(api_client):
    study_with_history = TestUtils.create_study()
    # update study title to be able to lock it
    response = api_client.patch(
        f"/studies/{study_with_history.uid}",
        json={"current_metadata": {"study_description": {"study_title": "new title"}}},
    )
    assert response.status_code == 200

    # snapshot history before lock
    response = api_client.get(f"/studies/{study_with_history.uid}/snapshot-history")
    res = response.json()
    assert response.status_code == 200
    res = res["items"]
    assert len(res) == 1
    assert res[0]["possible_actions"] == ["delete", "lock", "release"]
    assert res[0]["current_metadata"]["version_metadata"]["study_status"] == "DRAFT"
    assert res[0]["current_metadata"]["version_metadata"]["version_number"] is None

    # Lock
    response = api_client.post(
        f"/studies/{study_with_history.uid}/lock", json={"change_description": "Lock 1"}
    )
    assert response.status_code == 201

    # snapshot history after lock
    response = api_client.get(f"/studies/{study_with_history.uid}/snapshot-history")
    res = response.json()
    assert response.status_code == 200
    res = res["items"]
    assert len(res) == 2
    assert res[0]["current_metadata"]["version_metadata"]["study_status"] == "LOCKED"
    assert res[0]["current_metadata"]["version_metadata"]["version_number"] == 1
    assert (
        res[0]["current_metadata"]["version_metadata"]["version_description"]
        == "Lock 1"
    )
    assert res[1]["current_metadata"]["version_metadata"]["study_status"] == "RELEASED"
    assert res[1]["current_metadata"]["version_metadata"]["version_number"] == 1
    assert (
        res[1]["current_metadata"]["version_metadata"]["version_description"]
        == "Lock 1"
    )

    # Unlock
    response = api_client.post(f"/studies/{study_with_history.uid}/unlock")
    assert response.status_code == 201

    # snapshot history after unlock
    response = api_client.get(f"/studies/{study_with_history.uid}/snapshot-history")
    assert response.status_code == 200
    res = response.json()
    res = res["items"]
    assert len(res) == 3
    assert res[0]["current_metadata"]["version_metadata"]["study_status"] == "DRAFT"
    assert res[1]["current_metadata"]["version_metadata"]["version_number"] == 1
    assert res[2]["current_metadata"]["version_metadata"]["version_number"] == 1

    # Release
    response = api_client.post(
        f"/studies/{study_with_history.uid}/release",
        json={"change_description": "Explicit release"},
    )
    assert response.status_code == 201
    # snapshot history after release
    response = api_client.get(f"/studies/{study_with_history.uid}/snapshot-history")
    assert response.status_code == 200
    res = response.json()
    res = res["items"]

    assert len(res) == 4
    assert res[0]["current_metadata"]["version_metadata"]["study_status"] == "DRAFT"
    assert res[1]["current_metadata"]["version_metadata"]["study_status"] == "RELEASED"
    assert (
        res[1]["current_metadata"]["version_metadata"]["version_description"]
        == "Explicit release"
    )
    assert res[1]["current_metadata"]["version_metadata"]["version_number"] == 1.1
    assert res[2]["current_metadata"]["version_metadata"]["version_number"] == 1
    assert (
        res[2]["current_metadata"]["version_metadata"]["version_description"]
        == "Lock 1"
    )

    # 2nd Release
    response = api_client.post(
        f"/studies/{study_with_history.uid}/release",
        json={"change_description": "Explicit second release"},
    )
    assert response.status_code == 201
    # snapshot history after second release
    response = api_client.get(f"/studies/{study_with_history.uid}/snapshot-history")
    assert response.status_code == 200
    res = response.json()
    res = res["items"]
    assert len(res) == 5
    assert res[0]["current_metadata"]["version_metadata"]["study_status"] == "DRAFT"
    assert res[1]["current_metadata"]["version_metadata"]["study_status"] == "RELEASED"
    assert (
        res[1]["current_metadata"]["version_metadata"]["version_description"]
        == "Explicit second release"
    )
    assert res[1]["current_metadata"]["version_metadata"]["version_number"] == 1.2
    assert res[2]["current_metadata"]["version_metadata"]["study_status"] == "RELEASED"
    assert res[2]["current_metadata"]["version_metadata"]["version_number"] == 1.1
    assert (
        res[2]["current_metadata"]["version_metadata"]["version_description"]
        == "Explicit release"
    )

    # Lock
    response = api_client.post(
        f"/studies/{study_with_history.uid}/lock", json={"change_description": "Lock 2"}
    )
    assert response.status_code == 201

    # snapshot history after lock
    response = api_client.get(f"/studies/{study_with_history.uid}/snapshot-history")
    assert response.status_code == 200
    res = response.json()
    res = res["items"]
    assert len(res) == 6
    assert res[0]["current_metadata"]["version_metadata"]["study_status"] == "LOCKED"
    assert res[0]["current_metadata"]["version_metadata"]["version_number"] == 2
    assert (
        res[0]["current_metadata"]["version_metadata"]["version_description"]
        == "Lock 2"
    )
    assert res[1]["current_metadata"]["version_metadata"]["study_status"] == "RELEASED"
    assert res[1]["current_metadata"]["version_metadata"]["version_number"] == 2
    assert (
        res[1]["current_metadata"]["version_metadata"]["version_description"]
        == "Lock 2"
    )


def test_get_default_time_unit(api_client):
    response = api_client.patch(
        f"/studies/{study.uid}",
        json={
            "current_metadata": {
                "identification_metadata": {"study_acronym": "new acronym"}
            }
        },
    )
    assert response.status_code == 200
    res = response.json()
    assert (
        res["current_metadata"]["identification_metadata"]["study_acronym"]
        == "new acronym"
    )

    response = api_client.get(f"/studies/{study.uid}/time-units")
    assert response.status_code == 200
    res = response.json()
    assert res["study_uid"] == study.uid
    assert res["time_unit_uid"] == day_unit_definition.uid
    assert res["time_unit_name"] == day_unit_definition.name


def test_edit_time_units(api_client):
    response = api_client.patch(
        f"/studies/{study.uid}/time-units",
        json={"unit_definition_uid": day_unit_definition.uid},
    )
    res = response.json()
    assert response.status_code == 400
    assert (
        res["message"]
        == f"The preferred_time_unit for the following study ({study.uid}) is already ({day_unit_definition.uid})"
    )

    response = api_client.patch(
        f"/studies/{study.uid}/time-units",
        json={"unit_definition_uid": week_unit_definition.uid},
    )
    res = response.json()
    assert response.status_code == 200
    assert res["study_uid"] == study.uid
    assert res["time_unit_uid"] == week_unit_definition.uid
    assert res["time_unit_name"] == week_unit_definition.name


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
def test_get_studies_csv_xml_excel(api_client, export_format):
    TestUtils.verify_exported_data_format(api_client, export_format, "/studies")
