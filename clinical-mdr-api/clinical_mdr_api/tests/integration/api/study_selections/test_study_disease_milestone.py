"""
Tests for /studies/{uid}/study-disease-milestones endpoints
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
from clinical_mdr_api.models import CTTerm
from clinical_mdr_api.models.study import Study
from clinical_mdr_api.tests.integration.utils.api import (
    drop_db,
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
study: Study
disease_milestone_type_term: CTTerm


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "studydiseasemilestoneapi"
    inject_and_clear_db(db_name)
    inject_base_data()
    global disease_milestone_type_term
    global study
    study = TestUtils.create_study()

    type_codelist = TestUtils.create_ct_codelist(
        name="Disease Milestone Type",
        sponsor_preferred_name="Disease Milestone Type",
        extensible=True,
        approve=True,
    )
    disease_milestone_type_term = TestUtils.create_ct_term(
        codelist_uid=type_codelist.codelist_uid,
        sponsor_preferred_name="Disease Milestone Type",
    )
    yield

    drop_db(db_name)


def test_disease_milestone_modify_actions_on_locked_study(api_client):
    response = api_client.post(
        f"/studies/{study.uid}/study-disease-milestones",
        json={
            "study_uid": study.uid,
            "repetition_indicator": True,
            "description": "test_description",
            "disease_milestone_type": disease_milestone_type_term.term_uid,
        },
    )
    res = response.json()
    disease_milestone_uid = res["uid"]
    assert response.status_code == 201

    # get all disease milestones
    response = api_client.get(
        f"/studies/{study.uid}/study-disease-milestones/audit-trail/",
        json={},
    )
    res = response.json()
    assert response.status_code == 200
    old_res = res

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
        f"/studies/{study.uid}/study-disease-milestones",
        json={
            "study_uid": study.uid,
            "repetition_indicator": True,
            "description": "test_description",
            "disease_milestone_type": disease_milestone_type_term.term_uid,
        },
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    response = api_client.patch(
        f"/studies/{study.uid}/study-disease-milestones/{disease_milestone_uid}",
        json={"repetition_indicator": False},
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    # get all history when was locked
    response = api_client.get(
        f"/studies/{study.uid}/study-disease-milestones/audit-trail/",
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
def test_get_disease_milestones_csv_xml_excel(api_client, export_format):
    url = f"/studies/{study.uid}/study-disease-milestones"
    TestUtils.verify_exported_data_format(api_client, export_format, url)
