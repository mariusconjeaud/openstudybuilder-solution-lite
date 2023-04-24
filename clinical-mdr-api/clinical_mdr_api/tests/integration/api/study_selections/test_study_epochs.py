"""
Tests for /studies/{uid}/study-epochs endpoints
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api import main
from clinical_mdr_api.models.study import Study
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
    create_study_epoch_codelists_ret_cat_and_lib,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

# Global variables shared between fixtures and tests
study: Study
epoch_subtype_uid: str
epoch_subtype2_uid: str


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(main.app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "studyepochapi"
    inject_and_clear_db(db_name)
    inject_base_data()
    global epoch_subtype_uid
    global epoch_subtype2_uid
    global study
    study = TestUtils.create_study()
    db.cypher_query(STARTUP_STUDY_LIST_CYPHER)
    db.cypher_query(STARTUP_CT_CATALOGUE_CYPHER)
    create_study_epoch_codelists_ret_cat_and_lib()

    epoch_subtype_uid = "EpochSubType_0001"
    epoch_subtype2_uid = "EpochSubType_0002"
    yield

    drop_db(db_name)


def test_epoch_modify_actions_on_locked_study(api_client):
    response = api_client.post(
        f"/studies/{study.uid}/study-epochs",
        json={
            "study_uid": study.uid,
            "epoch_subtype": epoch_subtype_uid,
        },
    )
    res = response.json()
    assert response.status_code == 201

    # get all epochs
    response = api_client.get(
        f"/studies/{study.uid}/study-epoch/audit-trail/",
        json={},
    )
    res = response.json()
    assert response.status_code == 200
    old_res = res
    epoch_uid = res[0]["uid"]

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
        f"/studies/{study.uid}/study-epochs",
        json={
            "study_uid": study.uid,
            "epoch_subtype": epoch_subtype2_uid,
        },
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    # edit epoch
    response = api_client.patch(
        f"/studies/{study.uid}/study-epochs/{epoch_uid}",
        json={
            "study_uid": study.uid,
            "name": "New_epoch_Name_1",
            "change_description": "this is a changing test",
        },
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    # get all history when was locked
    response = api_client.get(
        f"/studies/{study.uid}/study-epoch/audit-trail/",
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
def test_get_study_epochs_csv_xml_excel(api_client, export_format):
    url = f"/studies/{study.uid}/study-epochs"
    TestUtils.verify_exported_data_format(api_client, export_format, url)
