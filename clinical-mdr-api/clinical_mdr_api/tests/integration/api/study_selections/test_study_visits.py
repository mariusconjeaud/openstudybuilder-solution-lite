"""
Tests for /studies/{uid}/study-visits endpoints
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

from unittest import mock

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api import main
from clinical_mdr_api.models.study_selections.study import Study
from clinical_mdr_api.tests.integration.utils.api import (
    drop_db,
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_CT_CATALOGUE_CYPHER,
    STARTUP_STUDY_LIST_CYPHER,
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

# Global variables shared between fixtures and tests
study: Study
study_visit_uid: str
epoch_uid: str
DAYUID: str
visits_basic_data: dict


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(main.app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "studyvisitapi"
    inject_and_clear_db(db_name)
    inject_base_data()

    global study
    study = TestUtils.create_study()
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


def test_visit_modify_actions_on_locked_study(api_client):
    global study_visit_uid

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
    study_visit_uid = res["uid"]
    assert response.status_code == 201

    # get all visits
    response = api_client.get(
        f"/studies/{study.uid}/study-visit/audit-trail/",
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
        f"/studies/{study.uid}/locks",
        json={"change_description": "Lock 1"},
    )
    assert response.status_code == 201

    inputs = {
        "study_epoch_uid": epoch_uid,
        "visit_type_uid": "VisitType_0003",
        "show_visit": True,
        "time_reference_uid": "VisitSubType_0001",
        "time_value": 12,
        "time_unit_uid": DAYUID,
        "visit_class": "SINGLE_VISIT",
        "visit_subclass": "SINGLE_VISIT",
        "is_global_anchor_visit": False,
    }
    datadict = visits_basic_data
    datadict.update(inputs)
    response = api_client.post(
        f"/studies/{study.uid}/study-visits",
        json=datadict,
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    # edit visit
    inputs = {
        "uid": study_visit_uid,
        "study_uid": study.uid,
        "description": "new description",
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
    response = api_client.patch(
        f"/studies/{study.uid}/study-visits/{study_visit_uid}",
        json=datadict,
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    # get all history when was locked
    response = api_client.get(
        f"/studies/{study.uid}/study-visit/audit-trail/",
    )
    res = response.json()
    assert response.status_code == 200
    for i, _ in enumerate(old_res):
        old_res[i]["study_version"] = mock.ANY
    assert old_res == res

    # test cannot delete
    response = api_client.delete(f"/studies/{study.uid}/study-visits/{study_visit_uid}")
    assert response.status_code == 400
    assert (
        response.json()["message"]
        == f"Study with specified uid '{study.uid}' is locked."
    )


def test_study_visit_versioning(api_client):
    _study_epoch = create_study_epoch("EpochSubType_0003", study_uid=study.uid)

    # get specific study visit
    response = api_client.get(
        f"/studies/{study.uid}/study-visits/{study_visit_uid}",
    )
    res = response.json()
    assert response.status_code == 200
    assert res["study_epoch_uid"] == epoch_uid
    before_unlock = res

    # get study visit headers
    response = api_client.get(
        f"/studies/{study.uid}/study-visits/headers?field_name=study_epoch_uid",
    )
    res = response.json()
    assert response.status_code == 200
    assert res == [epoch_uid]

    # Unlock -- Study remain unlocked
    response = api_client.delete(f"/studies/{study.uid}/locks")
    assert response.status_code == 200

    # edit study visit
    response = api_client.patch(
        f"/studies/{study.uid}/study-visits/{study_visit_uid}",
        json={
            "show_visit": True,
            "time_unit_uid": "UnitDefinition_000001",
            "time_value": 0,
            "visit_contact_mode_uid": "VisitContactMode_0001",
            "visit_type_uid": "VisitType_0001",
            "time_reference_uid": "VisitSubType_0001",
            "is_global_anchor_visit": True,
            "visit_class": "SINGLE_VISIT",
            "study_epoch_uid": _study_epoch.uid,
            "uid": "StudyVisit_000001",
            "study_uid": "Study_000002",
        },
    )
    res = response.json()
    assert response.status_code == 200
    assert res["study_epoch_uid"] == _study_epoch.uid

    # delete epoch
    response = api_client.delete(f"/studies/{study.uid}/study-epochs/{epoch_uid}")
    assert response.status_code == 204

    # get all study visits of a specific study version
    response = api_client.get(
        f"/studies/{study.uid}/study-visits?study_value_version=1",
    )
    res = response.json()
    assert response.status_code == 200
    before_unlock["study_version"] = mock.ANY
    assert res["items"][0] == before_unlock

    # get specific study visit of a specific study version
    response = api_client.get(
        f"/studies/{study.uid}/study-visits/{study_visit_uid}?study_value_version=1",
    )
    res = response.json()
    assert response.status_code == 200
    assert res == before_unlock

    # get study visit headers of specific study version
    response = api_client.get(
        f"/studies/{study.uid}/study-visits/headers?field_name=study_epoch_uid&study_value_version=1",
    )
    res = response.json()
    assert response.status_code == 200
    assert res == [epoch_uid]

    # get all study visits
    response = api_client.get(
        f"/studies/{study.uid}/study-visits",
    )
    res = response.json()
    assert response.status_code == 200
    assert res["items"][0]["study_epoch_uid"] == _study_epoch.uid

    # get specific study visit
    response = api_client.get(
        f"/studies/{study.uid}/study-visits/{study_visit_uid}",
    )
    res = response.json()
    assert response.status_code == 200
    assert res["study_epoch_uid"] == _study_epoch.uid
    # get study visits headers
    response = api_client.get(
        f"/studies/{study.uid}/study-visits/headers?field_name=study_epoch_uid",
    )
    res = response.json()
    assert response.status_code == 200
    assert res == [_study_epoch.uid]


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
def test_get_study_visits_csv_xml_excel(api_client, export_format):
    url = f"/studies/{study.uid}/study-visits"
    exported_data = TestUtils.verify_exported_data_format(
        api_client, export_format, url
    )
    if export_format == "text/csv":
        assert "study_version" in str(exported_data.read())
        assert "LATEST" in str(exported_data.read())
