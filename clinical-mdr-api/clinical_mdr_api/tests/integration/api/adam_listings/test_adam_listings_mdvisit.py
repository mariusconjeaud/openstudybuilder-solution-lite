"""
Tests for /listings/studies/all/adam/ endpoints
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
from clinical_mdr_api.models.listings_adam import StudyVisitAdamListing
from clinical_mdr_api.tests.integration.utils.api import inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_CT_CATALOGUE_CYPHER,
    STARTUP_STUDY_LIST_CYPHER,
)
from clinical_mdr_api.tests.integration.utils.method_library import (
    create_library_data,
    create_some_visits,
    generate_study_root,
)

log = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    inject_and_clear_db("ADAMMDVISITListingTest")
    db.cypher_query(STARTUP_STUDY_LIST_CYPHER)
    db.cypher_query(STARTUP_CT_CATALOGUE_CYPHER)
    create_library_data()
    generate_study_root()
    create_some_visits()


def test_adam_listing_mdvisit(api_client):
    response = api_client.get(
        "/listings/studies/study_root/adam/mdvisit/",
        json={},
    )
    assert response.status_code == 200
    res = response.json()["items"]
    assert res is not None
    res_visits = response.json()["items"]

    expected_output = StudyVisitAdamListing(
        STUDYID="SOME_ID-0",
        VISIT_TYPE_NAME="BASELINE",
        VISIT_NUM=100,
        VISIT_NAME="VISIT 1",
        DAY_VALUE=1,
        VISIT_SHORT_LABEL="V1",
        DAY_NAME="Day 1",
        WEEK_NAME="Week 1",
        WEEK_VALUE="1",
    )
    assert res[0] == expected_output

    # headers endpoint testing
    field_name = "VISIT_NAME"
    expected_result = []  # building expected result
    for res_visit in res_visits:
        value = res_visit[field_name]
        if value:
            expected_result.append(value)
    URL = "/listings/studies/study_root/adam/mdvisit"
    response = api_client.get(f"{URL}/headers?field_name={field_name}&result_count=100")
    res_headers = response.json()

    assert response.status_code == 200
    log.info("Expected result is %s", expected_result)
    log.info("Returned %s", res_headers)
    if expected_result:
        assert len(res_headers) > 0
        assert len(set(expected_result)) == len(res_headers)
        assert all(item in res_headers for item in expected_result)
    else:
        assert len(res_headers) == 0
