"""
Tests for /studies/{uid}/study-endpoints endpoints
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

from clinical_mdr_api.domain_repositories.models.syntax import (
    EndpointRoot,
    EndpointTemplateRoot,
    ObjectiveRoot,
    ObjectiveTemplateRoot,
    TimeframeRoot,
    TimeframeTemplateRoot,
)
from clinical_mdr_api.main import app
from clinical_mdr_api.models.listings_adam import StudyEndpntAdamListing
from clinical_mdr_api.models.study import Study
from clinical_mdr_api.tests.integration.utils.api import (
    drop_db,
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.data_library import (
    CREATE_BASE_TEMPLATE_PARAMETER_TREE,
    STARTUP_CT_TERM_NAME_CYPHER,
    STARTUP_STUDY_ENDPOINT_CYPHER,
    STARTUP_STUDY_OBJECTIVE_CYPHER,
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
    db_name = "ADAMMDENDPNTListingTest"
    inject_and_clear_db(db_name)
    inject_base_data()
    global study
    study = TestUtils.create_study()

    db.cypher_query(CREATE_BASE_TEMPLATE_PARAMETER_TREE)
    db.cypher_query(STARTUP_CT_TERM_NAME_CYPHER)
    db.cypher_query(STARTUP_STUDY_OBJECTIVE_CYPHER)
    db.cypher_query(STARTUP_STUDY_ENDPOINT_CYPHER)
    ObjectiveTemplateRoot.generate_node_uids_if_not_present()
    ObjectiveRoot.generate_node_uids_if_not_present()
    EndpointTemplateRoot.generate_node_uids_if_not_present()
    EndpointRoot.generate_node_uids_if_not_present()
    TimeframeTemplateRoot.generate_node_uids_if_not_present()
    TimeframeRoot.generate_node_uids_if_not_present()

    yield
    drop_db(db_name)


def test_adam_listing_mdendpnt(api_client):
    response = api_client.post(
        f"/studies/{study.uid}/study-objectives",
        json={
            "objective_uid": "Objective_000001",
            "objective_level_uid": "term_root_final",
        },
    )
    res = response.json()
    objective_uid = res["study_objective_uid"]
    assert response.status_code == 201

    # create en endpoint 1
    response = api_client.post(
        f"/studies/{study.uid}/study-endpoints",
        json={"endpoint_uid": "Endpoint_000001", "study_objective_uid": objective_uid},
    )
    res = response.json()
    assert response.status_code == 201

    # create endpoint 2
    response = api_client.post(
        f"/studies/{study.uid}/study-endpoints",
        json={
            "endpoint_level_uid": "term_root_final",
            "endpoint_sublevel_uid": "term_root_final_non_edit",
            "endpoint_uid": "Endpoint_000001",
            "endpoint_units": {"separator": "string", "units": ["unit 1", "unit 2"]},
            "timeframe_uid": "Timeframe_000001",
            "study_objective_uid": objective_uid,
        },
    )
    res = response.json()
    assert response.status_code == 201

    # get all endpoints
    response = api_client.get(
        f"/studies/{study.uid}/study-endpoints/audit-trail/",
        json={},
    )
    res = response.json()
    assert response.status_code == 200

    response = api_client.get(
        "/listings/studies/Study_000002/adam/mdendpnt/",
        json={},
    )
    assert response.status_code == 200
    res = response.json()["items"]
    res_objectives = response.json()["items"]
    assert res is not None

    expected_output = StudyEndpntAdamListing(
        STUDYID="Study_000002",
        OBJTVLVL="term_value_name1",
        OBJTV="objective_1",
        OBJTVPT="objective_1",
        ENDPNTLVL="term_value_name1",
        ENDPNTSL="term_value_name3",
        ENDPNT="endpoint_1",
        ENDPNTPT="endpoint_1",
        UNITDEF=None,
        UNIT=None,
        TMFRM="timeframe_1",
        TMFRMPT="timeframe_1",
        RACT=[],
        RACTSGRP=[],
        RACTGRP=[],
        RACTINST=[],
    )
    assert res[1] == expected_output

    # headers endpoint testing
    field_name = "OBJTVLVL"
    expected_result = []  # building expected result
    for res_objective in res_objectives:
        value = res_objective[field_name]
        if value:
            expected_result.append(value)
    URL = "/listings/studies/Study_000002/adam/mdendpnt"
    response = api_client.get(f"{URL}/headers?field_name={field_name}&result_count=100")
    res_headers = response.json()

    assert response.status_code == 200
    log.info("Returned %s", res_headers)
    log.info("Expected result is %s", expected_result)
    if expected_result:
        assert len(res_headers) > 0
        assert len(set(expected_result)) == len(res_headers)
        assert all(item in res_headers for item in expected_result)
    else:
        assert len(res_headers) == 0
