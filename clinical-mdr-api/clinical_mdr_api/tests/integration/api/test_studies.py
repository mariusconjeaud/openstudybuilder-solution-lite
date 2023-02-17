"""
Tests for /standards/data-models endpoints
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
from clinical_mdr_api.models.study import Study
from clinical_mdr_api.tests.integration.utils.api import (
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
studies_all: List[Study]
study_without_time_unit: Study
study_with_time_unit: Study
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
    inject_and_clear_db("studies.api")
    global study_without_time_unit
    study_without_time_unit = inject_base_data()

    global study_with_time_unit
    study_with_time_unit = TestUtils.create_study()

    global day_unit_definition
    day_unit_definition = TestUtils.create_unit_definition(name="day")
    global week_unit_definition
    week_unit_definition = TestUtils.create_unit_definition(name="week")

    TestUtils.create_study_preferred_time_unit(
        study_uid=study_with_time_unit.uid, unit_definition_uid=day_unit_definition.uid
    )


def test_get_time_units(api_client):

    response = api_client.get(f"/studies/{study_without_time_unit.uid}/time-units")
    res = response.json()
    assert response.status_code == 400
    assert (
        res["message"]
        == f"The preferred study time StudyTimeField node for the following study_uid='{study_without_time_unit.uid}' could not be found."
    )

    response = api_client.get(f"/studies/{study_with_time_unit.uid}/time-units")
    assert response.status_code == 200
    res = response.json()
    assert res["study_uid"] == study_with_time_unit.uid
    assert res["time_unit_uid"] == day_unit_definition.uid
    assert res["time_unit_name"] == day_unit_definition.name


def test_edit_time_units(api_client):

    response = api_client.patch(
        f"/studies/{study_without_time_unit.uid}/time-units",
        json={"unit_definition_uid": day_unit_definition.uid},
    )
    assert response.status_code == 400
    res = response.json()
    assert res["message"] == "The previous preferred StudyTimeField node was not found"

    response = api_client.patch(
        f"/studies/{study_with_time_unit.uid}/time-units",
        json={"unit_definition_uid": day_unit_definition.uid},
    )
    res = response.json()
    assert response.status_code == 400
    assert (
        res["message"]
        == f"The preferred_time_unit for the following study ({study_with_time_unit.uid}) is already ({day_unit_definition.uid})"
    )

    response = api_client.patch(
        f"/studies/{study_with_time_unit.uid}/time-units",
        json={"unit_definition_uid": week_unit_definition.uid},
    )
    res = response.json()
    assert response.status_code == 200
    assert res["study_uid"] == study_with_time_unit.uid
    assert res["time_unit_uid"] == week_unit_definition.uid
    assert res["time_unit_name"] == week_unit_definition.name


def test_post_time_units(api_client):
    response = api_client.post(
        f"/studies/{study_with_time_unit.uid}/time-units",
        json={"unit_definition_uid": day_unit_definition.uid},
    )
    res = response.json()
    assert response.status_code == 400
    assert (
        res["message"]
        == f"There already exists a preferred time unit for the following study ({study_with_time_unit.uid})"
    )

    response = api_client.post(
        f"/studies/{study_without_time_unit.uid}/time-units",
        json={"unit_definition_uid": day_unit_definition.uid},
    )
    assert response.status_code == 201
    res = response.json()
    assert res["study_uid"] == study_without_time_unit.uid
    assert res["time_unit_uid"] == day_unit_definition.uid
    assert res["time_unit_name"] == day_unit_definition.name
