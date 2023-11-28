"""
Tests for /studies endpoints
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
from clinical_mdr_api.models import UnitDefinitionModel
from clinical_mdr_api.models.study_selections.study import Study
from clinical_mdr_api.tests.integration.utils.api import (
    drop_db,
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.method_library import (
    create_codelist,
    create_ct_term,
    get_catalogue_name_library_name,
    input_metadata_in_study,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
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


def test_get_study_by_uid(api_client):
    response = api_client.get(
        f"/studies/{study.uid}",
    )
    assert response.status_code == 200
    res = response.json()
    assert res["uid"] == study.uid
    assert res["current_metadata"]["identification_metadata"] is not None
    assert res["current_metadata"]["version_metadata"] is not None
    assert res["current_metadata"].get("high_level_study_design") is None
    assert res["current_metadata"].get("study_population") is None
    assert res["current_metadata"].get("study_intervention") is None
    assert res["current_metadata"].get("study_description") is None

    response = api_client.get(
        f"/studies/{study.uid}",
        params={
            "include_sections": ["high_level_study_design", "study_intervention"],
            "exclude_sections": ["identification_metadata"],
        },
    )
    assert response.status_code == 200
    res = response.json()
    assert res["uid"] == study.uid
    assert res["current_metadata"].get("identification_metadata") is None
    assert res["current_metadata"]["version_metadata"] is not None
    assert res["current_metadata"].get("high_level_study_design") is not None
    assert res["current_metadata"].get("study_population") is None
    assert res["current_metadata"].get("study_intervention") is not None
    assert res["current_metadata"].get("study_description") is None

    response = api_client.get(
        f"/studies/{study.uid}",
        params={
            "include_sections": ["not existing section"],
            "exclude_sections": ["not existing section"],
        },
    )
    assert response.status_code == 422


def test_get_study_fields_audit_trail(api_client):
    created_study = TestUtils.create_study()

    response = api_client.patch(
        f"/studies/{created_study.uid}",
        json={"current_metadata": {"study_description": {"study_title": "new title"}}},
    )
    assert response.status_code == 200

    # Study-fields audit trail for all sections
    response = api_client.get(
        f"/studies/{created_study.uid}/fields-audit-trail",
    )
    assert response.status_code == 200
    res = response.json()
    for audit_trail_item in res:
        actions = audit_trail_item["actions"]
        for action in actions:
            assert action["section"] in [
                "study_description",
                "Unknown",
                "identification_metadata",
            ]

    # Study-fields audit trail for all sections without identification_metadata
    response = api_client.get(
        f"/studies/{created_study.uid}/fields-audit-trail",
        params={"exclude_sections": ["identification_metadata"]},
    )
    assert response.status_code == 200
    res = response.json()
    for audit_trail_item in res:
        actions = audit_trail_item["actions"]
        for action in actions:
            # we have filtered out the identification_metadata entries, so we should only have
            # study_description entry for study_title patch and Unknown section for preferred_time_unit that is not
            # included in any Study sections
            assert action["section"] in ["study_description", "Unknown"]

    # Study-fields audit trail with not existing section sent
    response = api_client.get(
        f"/studies/{created_study.uid}/fields-audit-trail",
        params={"exclude_sections": ["not existing section"]},
    )
    assert response.status_code == 422


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


def test_study_listing(api_client):
    # Create three new studies
    studies = [
        TestUtils.create_study(),
        TestUtils.create_study(),
        TestUtils.create_study(),
    ]

    response = api_client.get("/studies")
    assert response.status_code == 200
    res = response.json()
    assert len(res["items"]) >= 3
    uids = [s["uid"] for s in res["items"]]
    for study in res["items"]:
        assert "current_metadata" in study
        metadata = study["current_metadata"]
        # Check that the expected fields exist
        assert "identification_metadata" in metadata
        assert "version_metadata" in metadata
        # Check that no unwanted field is present
        assert "study_description" not in metadata
        assert "high_level_study_design" not in metadata
        assert "study_population" not in metadata
        assert "study_intervention" not in metadata

    for study in studies:
        # Check that each study occurs only once in the list
        assert uids.count(study.uid) == 1

    # Clean up
    for study in studies:
        response = api_client.delete(f"/studies/{study.uid}")
        assert response.status_code == 204


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
        f"/studies/{study_with_history.uid}/locks",
        json={"change_description": "Lock 1"},
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
    response = api_client.delete(f"/studies/{study_with_history.uid}/locks")
    assert response.status_code == 200

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
        f"/studies/{study_with_history.uid}/locks",
        json={"change_description": "Lock 2"},
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


def test_get_specific_version(api_client):
    study = TestUtils.create_study()

    title_1 = "new title"
    title_11 = "title after 1st lock."
    title_12 = "title after 1st release."
    title_2 = "title after 2nd release."
    title_draft = "title after 2nd lock."

    # update study title to be able to lock it
    response = api_client.patch(
        f"/studies/{study.uid}",
        json={"current_metadata": {"study_description": {"study_title": title_1}}},
    )
    assert response.status_code == 200

    # Lock
    response = api_client.post(
        f"/studies/{study.uid}/locks", json={"change_description": "Lock 1"}
    )
    assert response.status_code == 201

    # Unlock
    response = api_client.delete(f"/studies/{study.uid}/locks")
    assert response.status_code == 200

    # update study title
    response = api_client.patch(
        f"/studies/{study.uid}",
        json={"current_metadata": {"study_description": {"study_title": title_11}}},
    )
    assert response.status_code == 200

    # Release
    response = api_client.post(
        f"/studies/{study.uid}/release",
        json={"change_description": "Explicit release"},
    )
    assert response.status_code == 201

    # update study title
    response = api_client.patch(
        f"/studies/{study.uid}",
        json={"current_metadata": {"study_description": {"study_title": title_12}}},
    )
    assert response.status_code == 200

    # 2nd Release
    response = api_client.post(
        f"/studies/{study.uid}/release",
        json={"change_description": "Explicit second release"},
    )
    assert response.status_code == 201

    # update study title
    response = api_client.patch(
        f"/studies/{study.uid}",
        json={"current_metadata": {"study_description": {"study_title": title_2}}},
    )
    assert response.status_code == 200

    # Lock
    response = api_client.post(
        f"/studies/{study.uid}/locks", json={"change_description": "Lock 2"}
    )
    assert response.status_code == 201

    # Unlock
    response = api_client.delete(f"/studies/{study.uid}/locks")
    assert response.status_code == 200

    # update study title
    response = api_client.patch(
        f"/studies/{study.uid}",
        json={"current_metadata": {"study_description": {"study_title": title_draft}}},
    )
    assert response.status_code == 200

    # check study title in different versions
    response = api_client.get(
        f"/studies/{study.uid}",
        params={"include_sections": ["study_description"], "study_value_version": "1"},
    )
    res_title = response.json()["current_metadata"]["study_description"]["study_title"]
    assert res_title == title_1
    response = api_client.get(
        f"/studies/{study.uid}",
        params={
            "include_sections": ["study_description"],
            "study_value_version": "1.1",
        },
    )
    res_title = response.json()["current_metadata"]["study_description"]["study_title"]
    assert res_title == title_11
    response = api_client.get(
        f"/studies/{study.uid}",
        params={
            "include_sections": ["study_description"],
            "study_value_version": "1.2",
        },
    )
    res_title = response.json()["current_metadata"]["study_description"]["study_title"]
    assert res_title == title_12
    response = api_client.get(
        f"/studies/{study.uid}",
        params={"include_sections": ["study_description"], "study_value_version": "2"},
    )
    res_title = response.json()["current_metadata"]["study_description"]["study_title"]
    assert res_title == title_2
    response = api_client.get(
        f"/studies/{study.uid}",
        params={"include_sections": ["study_description"]},
    )
    res_title = response.json()["current_metadata"]["study_description"]["study_title"]
    assert res_title == title_draft


def test_get_protocol_title_for_specific_version(api_client):
    study = TestUtils.create_study()
    TestUtils.create_library(name="UCUM", is_editable=True)
    codelist = TestUtils.create_ct_codelist()
    TestUtils.create_study_ct_data_map(codelist_uid=codelist.codelist_uid)
    compound = TestUtils.create_compound(name="name-AAA", approve=True)
    compound_alias = TestUtils.create_compound_alias(
        name="compAlias-AAA", compound_uid=compound.uid, approve=True
    )
    compound2 = TestUtils.create_compound(name="name-BBB", approve=True)
    compound_alias2 = TestUtils.create_compound_alias(
        name="compAlias-BBB", compound_uid=compound2.uid, approve=True
    )
    catalogue_name, library_name = get_catalogue_name_library_name(use_test_utils=True)
    type_of_trt_codelist = create_codelist(
        name="Type of Treatment",
        uid="CTCodelist_00009",
        catalogue=catalogue_name,
        library=library_name,
    )
    type_of_treatment = create_ct_term(
        codelist=type_of_trt_codelist.codelist_uid,
        name="Investigational Product",
        uid="type_of_treatment_00001",
        order=1,
        catalogue_name=catalogue_name,
        library_name=library_name,
    )

    # add some metadata to study
    input_metadata_in_study(study.uid)

    # add a study compound
    response = api_client.post(
        f"/studies/{study.uid}/study-compounds",
        json={
            "compound_alias_uid": compound_alias.uid,
            "type_of_treatment_uid": type_of_treatment.uid,
        },
    )
    res = response.json()
    study_compound_uid = res["study_compound_uid"]
    assert response.status_code == 201

    # response before locking
    response = api_client.get(
        f"/studies/{study.uid}/protocol-title",
    )
    assert response.status_code == 200
    res_old = response.json()

    # Lock
    response = api_client.post(
        f"/studies/{study.uid}/locks", json={"change_description": "Lock 1"}
    )
    assert response.status_code == 201

    # Unlock
    response = api_client.delete(f"/studies/{study.uid}/locks")
    assert response.status_code == 200

    # Update
    response = api_client.patch(
        f"/studies/{study.uid}",
        json={
            "current_metadata": {
                "study_description": {
                    "study_title": "some title, updated",
                }
            }
        },
    )
    assert response.status_code == 200
    response = api_client.patch(
        f"/studies/{study.uid}",
        json={
            "current_metadata": {
                "identification_metadata": {
                    "registry_identifiers": {"eudract_id": "eudract_id, updated"}
                },
            }
        },
    )
    assert response.status_code == 200
    response = api_client.patch(
        f"/studies/{study.uid}/study-compounds/{study_compound_uid}",
        json={"compound_alias_uid": compound_alias2.uid},
    )
    assert response.status_code == 200
    # check the study compound dosings for version 1 is same as first locked
    res_new = api_client.get(
        f"/studies/{study.uid}/protocol-title",
    ).json()
    res_v1 = api_client.get(
        f"/studies/{study.uid}/protocol-title?study_value_version=1",
    ).json()
    assert res_v1 == res_old
    assert res_v1 != res_new
