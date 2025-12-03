"""
Tests for sponsor ct package
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
from clinical_mdr_api.models.controlled_terminologies.ct_codelist import CTCodelist
from clinical_mdr_api.models.controlled_terminologies.ct_term import CTTerm
from clinical_mdr_api.tests.integration.utils.api import (
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils
from clinical_mdr_api.tests.utils.checks import assert_response_status_code

log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
codelist_a: CTCodelist
codelist_b: CTCodelist
term_a: CTTerm
term_b: CTTerm
term_c: CTTerm

URL = "/ct/codelists"


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "ct-codelists-sharing-terms.api"
    inject_and_clear_db(db_name)
    inject_base_data(inject_unit_subset=False)

    catalogue = "SDTM CT"
    global codelist_a
    codelist_a = TestUtils.create_ct_codelist(
        catalogue_name=catalogue,
        name="Codelist A",
        library_name="Sponsor",
        approve=True,
        extensible=True,
    )
    global codelist_b
    codelist_b = TestUtils.create_ct_codelist(
        catalogue_name=catalogue,
        name="Codelist B",
        library_name="Sponsor",
        approve=True,
        extensible=True,
    )
    global term_a
    term_a = TestUtils.create_ct_term(
        codelist_uid=codelist_a.codelist_uid,
        sponsor_preferred_name="Term A",
        submission_value="A",
        library_name="Sponsor",
        approve=True,
    )
    global term_b
    term_b = TestUtils.create_ct_term(
        codelist_uid=codelist_b.codelist_uid,
        sponsor_preferred_name="Term B",
        submission_value="B",
        library_name="Sponsor",
        approve=True,
    )
    global term_c
    term_c = TestUtils.create_ct_term(
        codelist_uid=codelist_a.codelist_uid,
        sponsor_preferred_name="Term C",
        submission_value="C",
        library_name="Sponsor",
        approve=True,
    )
    yield


def test_duplicated_submission_value(api_client):
    # Test that adding two terms with the same submission value
    # to the same codelist returns a 409 conflict error
    response = api_client.post(
        f"{URL}/{codelist_a.codelist_uid}/terms",
        json={"term_uid": term_b.term_uid, "order": 2, "submission_value": "A"},
    )
    assert_response_status_code(response, 409)
    response_json = response.json()
    assert "already has a Term with submission value 'A'" in response_json["message"]


def test_unique_submission_value(api_client):
    # Test that adding an existing term to a second codelist
    # with a new unique submission value works
    response = api_client.post(
        f"{URL}/{codelist_a.codelist_uid}/terms",
        json={"term_uid": term_b.term_uid, "order": 2, "submission_value": "D"},
    )
    assert_response_status_code(response, 201)


def test_existing_submission_value(api_client):
    # Test that it is possible to add an existing term to a second codelist
    # with a submission value that already exists in another codelist.
    response = api_client.post(
        f"{URL}/{codelist_b.codelist_uid}/terms",
        json={"term_uid": term_c.term_uid, "order": 2, "submission_value": "A"},
    )
    assert_response_status_code(response, 201)


def test_reuse_previous_submission_value(api_client):
    # Test that it is possible to remove a term from a codelist
    # and then reuse the same submission value for a new term in the same codelist
    term1 = TestUtils.create_ct_term(
        codelist_uid=codelist_a.codelist_uid,
        sponsor_preferred_name="Term to remove",
        submission_value="REMOVED",
        library_name="Sponsor",
        approve=True,
    )
    response = api_client.delete(
        f"{URL}/{codelist_a.codelist_uid}/terms/{term1.term_uid}"
    )
    assert_response_status_code(response, 200)

    term2 = TestUtils.create_ct_term(
        codelist_uid=codelist_a.codelist_uid,
        sponsor_preferred_name="New term to add",
        submission_value="REMOVED",
        library_name="Sponsor",
        approve=True,
    )

    assert term2 is not None
