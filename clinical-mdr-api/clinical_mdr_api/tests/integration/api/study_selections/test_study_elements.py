"""
Tests for /studies/{uid}/study-elements endpoints
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import logging

import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api import config as settings
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
element_subtype: CTTerm


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "studyelementapi"
    inject_and_clear_db(db_name)
    inject_base_data()
    global element_subtype

    global study
    study = TestUtils.create_study()
    element_subtype_codelist = TestUtils.create_ct_codelist(
        name=settings.STUDY_ELEMENT_SUBTYPE_NAME,
        sponsor_preferred_name=settings.STUDY_ELEMENT_SUBTYPE_NAME,
        extensible=True,
        approve=True,
    )
    element_subtype = TestUtils.create_ct_term(
        codelist_uid=element_subtype_codelist.codelist_uid,
        name_submission_value=settings.STUDY_ELEMENT_SUBTYPE_NAME,
        sponsor_preferred_name=settings.STUDY_ELEMENT_SUBTYPE_NAME,
    )
    element_type = TestUtils.create_ct_term()
    TestUtils.add_ct_term_parent(element_subtype, element_type)
    yield

    drop_db(db_name)


def test_element_modify_actions_on_locked_study(api_client):
    response = api_client.post(
        f"/studies/{study.uid}/study-elements",
        json={
            "name": "Element_Name_1",
            "short_name": "Element_Short_Name_1",
            "element_subtype_uid": element_subtype.term_uid,
        },
    )
    res = response.json()
    assert response.status_code == 201
    assert res["element_type"]["term_uid"] == "CTTerm_000002"

    # get all elements
    response = api_client.get(
        f"/studies/{study.uid}/study-element/audit-trail/",
        json={},
    )
    res = response.json()
    assert response.status_code == 200
    old_res = res
    element_uid = res[0]["element_uid"]

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
        f"/studies/{study.uid}/study-elements",
        json={
            "name": "Element_Name_2",
            "short_name": "Element_Short_Name_2",
            "element_subtype_uid": element_subtype.term_uid,
        },
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    # edit element
    response = api_client.patch(
        f"/studies/{study.uid}/study-elements/{element_uid}",
        json={
            "name": "New_Element_Name_1",
        },
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."
    # get all history when was locked
    response = api_client.get(
        f"/studies/{study.uid}/study-element/audit-trail/",
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
def test_get_study_elements_csv_xml_excel(api_client, export_format):
    url = f"/studies/{study.uid}/study-elements"
    TestUtils.verify_exported_data_format(api_client, export_format, url)
