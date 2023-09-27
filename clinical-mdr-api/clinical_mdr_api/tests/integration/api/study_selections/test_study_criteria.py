"""
Tests for /studies/{uid}/study-criteria endpoints
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments
# pylint: disable=too-many-statements

import copy
import json
import logging

import pytest
from deepdiff import DeepDiff
from fastapi.testclient import TestClient

from clinical_mdr_api import models
from clinical_mdr_api.main import app
from clinical_mdr_api.models.study_selections.study import Study
from clinical_mdr_api.tests.integration.utils.api import (
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
study: Study
study_uid: str
url_prefix: str
ct_term_inclusion_criteria: models.CTTerm
ct_term_exclusion_criteria: models.CTTerm
incl_criteria_template_1: models.CriteriaTemplate
incl_criteria_template_2: models.CriteriaTemplate
excl_criteria_template_1: models.CriteriaTemplate
excl_criteria_template_2: models.CriteriaTemplate
excl_criteria_template_with_param: models.CriteriaTemplate
inclusion_type_output: dict
exclusion_type_output: dict
incl_criteria_template_1_output: dict
incl_criteria_template_2_output: dict
excl_criteria_template_1_output: dict
excl_criteria_template_2_output: dict
excl_criteria_template_with_param_output: dict
default_study_criteria_input: dict
default_study_criteria_output: dict
change_description_approve: str


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    global study
    global study_uid
    global url_prefix
    global ct_term_inclusion_criteria
    global ct_term_exclusion_criteria
    global incl_criteria_template_1
    global incl_criteria_template_2
    global excl_criteria_template_1
    global excl_criteria_template_2
    global excl_criteria_template_with_param
    global inclusion_type_output
    global exclusion_type_output
    global incl_criteria_template_1_output
    global incl_criteria_template_2_output
    global excl_criteria_template_1_output
    global excl_criteria_template_2_output
    global excl_criteria_template_with_param_output
    global default_study_criteria_input
    global default_study_criteria_output
    global change_description_approve

    """Initialize test data"""
    inject_and_clear_db("studycriteria.api")
    study = inject_base_data()
    study_uid = study.uid
    url_prefix = f"/studies/{study_uid}/study-criteria"
    change_description_approve = "Approved version"

    # Create Template Parameter
    parameter_name = "TextValue"
    TestUtils.create_template_parameter(parameter_name)

    # Create CT Terms
    ct_term_inclusion_criteria = TestUtils.create_ct_term(
        sponsor_preferred_name="INCLUSION CRITERIA"
    )
    ct_term_exclusion_criteria = TestUtils.create_ct_term(
        sponsor_preferred_name="EXCLUSION CRITERIA"
    )

    # Create templates
    incl_criteria_template_1 = TestUtils.create_criteria_template(
        type_uid=ct_term_inclusion_criteria.term_uid
    )
    incl_criteria_template_2 = TestUtils.create_criteria_template(
        type_uid=ct_term_inclusion_criteria.term_uid
    )
    excl_criteria_template_1 = TestUtils.create_criteria_template(
        type_uid=ct_term_exclusion_criteria.term_uid
    )
    excl_criteria_template_2 = TestUtils.create_criteria_template(
        type_uid=ct_term_exclusion_criteria.term_uid
    )
    excl_criteria_template_with_param = TestUtils.create_criteria_template(
        name=f"<p>With parameter [{parameter_name}]</p>",
        type_uid=ct_term_exclusion_criteria.term_uid,
    )

    # Define default expected outputs
    inclusion_type_output = {
        "term_uid": ct_term_inclusion_criteria.term_uid,
        "catalogue_name": ct_term_inclusion_criteria.catalogue_name,
        "codelist_uid": ct_term_inclusion_criteria.codelist_uid,
        "sponsor_preferred_name": ct_term_inclusion_criteria.sponsor_preferred_name,
        "sponsor_preferred_name_sentence_case": ct_term_inclusion_criteria.sponsor_preferred_name_sentence_case,
        "order": None,
        "library_name": ct_term_inclusion_criteria.library_name,
        "status": "Final",
        "version": "1.0",
        "change_description": change_description_approve,
        "possible_actions": ["inactivate", "new_version"],
    }
    exclusion_type_output = {
        "term_uid": ct_term_exclusion_criteria.term_uid,
        "catalogue_name": ct_term_exclusion_criteria.catalogue_name,
        "codelist_uid": ct_term_exclusion_criteria.codelist_uid,
        "sponsor_preferred_name": ct_term_exclusion_criteria.sponsor_preferred_name,
        "sponsor_preferred_name_sentence_case": ct_term_exclusion_criteria.sponsor_preferred_name_sentence_case,
        "order": None,
        "library_name": ct_term_exclusion_criteria.library_name,
        "status": "Final",
        "version": "1.0",
        "change_description": change_description_approve,
        "possible_actions": ["inactivate", "new_version"],
    }
    incl_criteria_template_1_output = {
        "name": incl_criteria_template_1.name,
        "name_plain": incl_criteria_template_1.name_plain,
        "uid": incl_criteria_template_1.uid,
        "sequence_id": incl_criteria_template_1.sequence_id,
        "guidance_text": incl_criteria_template_1.guidance_text,
        "library_name": incl_criteria_template_1.library.name,
    }
    incl_criteria_template_2_output = {
        "name": incl_criteria_template_2.name,
        "name_plain": incl_criteria_template_2.name_plain,
        "uid": incl_criteria_template_2.uid,
        "sequence_id": incl_criteria_template_2.sequence_id,
        "guidance_text": incl_criteria_template_2.guidance_text,
        "library_name": incl_criteria_template_2.library.name,
    }
    excl_criteria_template_1_output = {
        "name": excl_criteria_template_1.name,
        "name_plain": excl_criteria_template_1.name_plain,
        "uid": excl_criteria_template_1.uid,
        "sequence_id": excl_criteria_template_1.sequence_id,
        "guidance_text": excl_criteria_template_1.guidance_text,
        "library_name": excl_criteria_template_1.library.name,
    }
    excl_criteria_template_2_output = {
        "name": excl_criteria_template_2.name,
        "name_plain": excl_criteria_template_2.name_plain,
        "uid": excl_criteria_template_2.uid,
        "sequence_id": excl_criteria_template_2.sequence_id,
        "guidance_text": excl_criteria_template_2.guidance_text,
        "library_name": excl_criteria_template_2.library.name,
    }
    excl_criteria_template_with_param_output = {
        "name": excl_criteria_template_with_param.name,
        "name_plain": excl_criteria_template_with_param.name_plain,
        "uid": excl_criteria_template_with_param.uid,
        "guidance_text": excl_criteria_template_with_param.guidance_text,
        "library_name": excl_criteria_template_with_param.library.name,
    }
    default_study_criteria_input = {
        "criteria_data": {
            "criteria_template_uid": incl_criteria_template_1.uid,
            "library_name": incl_criteria_template_1.library.name,
            "parameter_terms": [],
        }
    }
    default_study_criteria_output = {
        "study_uid": study_uid,
        "key_criteria": False,
        "order": 1,
        "study_criteria_uid": "preview",
        "criteria_type": {},
        "criteria": {},
        "latest_criteria": None,
        "accepted_version": False,
    }


ROOT_IGNORED_FIELDS = {
    "root['start_date']",
    "root['end_date']",
    "root['user_initials']",
    "root['project_number']",
    "root['project_name']",
}
CRITERIA_IGNORED_FIELDS = {
    "root['criteria']['start_date']",
    "root['criteria']['end_date']",
    "root['criteria']['user_initials']",
}
CRITERIA_TYPE_IGNORED_FIELDS = {
    "root['criteria_type']['start_date']",
    "root['criteria_type']['end_date']",
    "root['criteria_type']['user_initials']",
}
CRITERIA_TEMPLATE_IGNORED_FIELDS = {
    "root['criteria_template']['start_date']",
    "root['criteria_template']['end_date']",
    "root['criteria_template']['user_initials']",
    "root['criteria_template']['type']",
    "root['criteria_template']['library']",
    "root['criteria_template']['default_parameter_terms']",
    "root['criteria_template']['possible_actions']",
    "root['criteria_template']['status']",
    "root['criteria_template']['version']",
    "root['criteria_template']['change_description']",
}


def test_crud_study_criteria(api_client):
    """Test all endpoints for study-criteria routers.
    This covers all the CRUD operations, including /batch-select and /finalize

    * Preview
    * Create
    * Batch select
    * Reorder
    * Patch key-criteria
    * Get all for all studies
    * Delete
    * Get all with filters
    * Get audit trail for all selections
    * Get audit trail for specific selection
    * Batch select template with parameter
    * Finalize with parameter term
    * Get using specific project name and number filters
    * Get headers for all studies
    * Get headers for a specific study

    """
    # Selection preview
    response = api_client.post(
        url=f"{url_prefix}/preview",
        json=default_study_criteria_input,
    )
    res = response.json()

    assert response.status_code == 200
    expected_criteria = default_study_criteria_output
    expected_criteria["criteria_type"] = inclusion_type_output
    expected_criteria["criteria"] = {
        "uid": "preview",
        "name": incl_criteria_template_1.name,
        "name_plain": incl_criteria_template_1.name_plain,
        "status": "Final",
        "version": "1.0",
        "change_description": change_description_approve,
        "possible_actions": ["inactivate"],
        "criteria_template": incl_criteria_template_1_output,
        "parameter_terms": [],
        "library": {
            "name": incl_criteria_template_1.library.name,
            "is_editable": incl_criteria_template_1.library.is_editable,
        },
        "study_count": 0,
    }
    full_exclude_paths = {
        *ROOT_IGNORED_FIELDS,
        *CRITERIA_IGNORED_FIELDS,
        *CRITERIA_TYPE_IGNORED_FIELDS,
    }
    assert not DeepDiff(res, expected_criteria, exclude_paths=full_exclude_paths)

    # Create selection
    response = api_client.post(
        url=f"{url_prefix}?create_criteria=true",
        json=default_study_criteria_input,
    )
    res = response.json()

    assert response.status_code == 201
    expected_criteria["study_criteria_uid"] = "StudyCriteria_000001"
    expected_criteria["criteria"]["uid"] = "Criteria_000001"
    assert not DeepDiff(res, expected_criteria, exclude_paths=full_exclude_paths)

    # Test create batch
    response = api_client.post(
        url=f"{url_prefix}/batch-select",
        json=[
            {
                "criteria_template_uid": incl_criteria_template_2.uid,
                "library_name": incl_criteria_template_2.library.name,
            },
            {
                "criteria_template_uid": excl_criteria_template_1.uid,
                "library_name": excl_criteria_template_1.library.name,
            },
            {
                "criteria_template_uid": excl_criteria_template_2.uid,
                "library_name": excl_criteria_template_2.library.name,
            },
        ],
    )
    res = response.json()

    assert response.status_code == 201
    assert len(res) == 3

    expected_incl_criteria_1 = copy.deepcopy(expected_criteria)
    expected_incl_criteria_2 = copy.deepcopy(expected_criteria)
    expected_excl_criteria_1 = copy.deepcopy(expected_criteria)
    expected_excl_criteria_2 = copy.deepcopy(expected_criteria)

    expected_incl_criteria_2["study_criteria_uid"] = "StudyCriteria_000002"
    expected_incl_criteria_2["order"] = 2
    expected_incl_criteria_2["criteria"]["uid"] = "Criteria_000002"
    expected_incl_criteria_2["criteria"]["name"] = incl_criteria_template_2.name
    expected_incl_criteria_2["criteria"][
        "name_plain"
    ] = incl_criteria_template_2.name_plain
    expected_incl_criteria_2["criteria"][
        "criteria_template"
    ] = incl_criteria_template_2_output

    expected_excl_criteria_1["study_criteria_uid"] = "StudyCriteria_000003"
    expected_excl_criteria_1["order"] = 1
    expected_excl_criteria_1["criteria_type"] = exclusion_type_output
    expected_excl_criteria_1["criteria"]["uid"] = "Criteria_000003"
    expected_excl_criteria_1["criteria"]["name"] = excl_criteria_template_1.name
    expected_excl_criteria_1["criteria"][
        "name_plain"
    ] = excl_criteria_template_1.name_plain
    expected_excl_criteria_1["criteria"][
        "criteria_template"
    ] = excl_criteria_template_1_output

    expected_excl_criteria_2["study_criteria_uid"] = "StudyCriteria_000004"
    expected_excl_criteria_2["order"] = 2
    expected_excl_criteria_2["criteria_type"] = exclusion_type_output
    expected_excl_criteria_2["criteria"]["uid"] = "Criteria_000004"
    expected_excl_criteria_2["criteria"]["name"] = excl_criteria_template_2.name
    expected_excl_criteria_2["criteria"][
        "name_plain"
    ] = excl_criteria_template_2.name_plain
    expected_excl_criteria_2["criteria"][
        "criteria_template"
    ] = excl_criteria_template_2_output

    assert not DeepDiff(
        res[0], expected_incl_criteria_2, exclude_paths=full_exclude_paths
    )
    assert not DeepDiff(
        res[1], expected_excl_criteria_1, exclude_paths=full_exclude_paths
    )
    assert not DeepDiff(
        res[2], expected_excl_criteria_2, exclude_paths=full_exclude_paths
    )

    # Test reorder
    response = api_client.patch(
        url=f"{url_prefix}/StudyCriteria_000001/order",
        json={"new_order": 2},
    )
    res = response.json()

    assert response.status_code == 200
    expected_incl_criteria_1["order"] = 2
    expected_incl_criteria_2["order"] = 1
    assert not DeepDiff(res, expected_incl_criteria_1, exclude_paths=full_exclude_paths)

    # Test patch study selection key_criteria
    response = api_client.patch(
        url=f"{url_prefix}/StudyCriteria_000001/key-criteria",
        json={"key_criteria": True},
    )
    res = response.json()

    assert response.status_code == 200
    expected_incl_criteria_1["key_criteria"] = True
    assert not DeepDiff(res, expected_incl_criteria_1, exclude_paths=full_exclude_paths)

    # Test get specific - with right order
    response = api_client.get(url=f"{url_prefix}/StudyCriteria_000001")
    res = response.json()

    assert response.status_code == 200
    assert not DeepDiff(res, expected_incl_criteria_1, exclude_paths=full_exclude_paths)

    # Test get all - with right orders
    response = api_client.get(url=url_prefix)
    res = response.json()

    assert response.status_code == 200
    assert len(res) == 4
    assert not DeepDiff(
        res["items"][0], expected_incl_criteria_2, exclude_paths=full_exclude_paths
    )
    assert not DeepDiff(
        res["items"][1], expected_incl_criteria_1, exclude_paths=full_exclude_paths
    )
    assert not DeepDiff(
        res["items"][2], expected_excl_criteria_1, exclude_paths=full_exclude_paths
    )
    assert not DeepDiff(
        res["items"][3], expected_excl_criteria_2, exclude_paths=full_exclude_paths
    )

    # Test get all for all studies
    response = api_client.get(url="/study-criteria")
    res = response.json()

    assert response.status_code == 200
    assert len(res) == 4
    assert not DeepDiff(
        res["items"][0], expected_incl_criteria_2, exclude_paths=full_exclude_paths
    )
    assert not DeepDiff(
        res["items"][1], expected_incl_criteria_1, exclude_paths=full_exclude_paths
    )
    assert not DeepDiff(
        res["items"][2], expected_excl_criteria_1, exclude_paths=full_exclude_paths
    )
    assert not DeepDiff(
        res["items"][3], expected_excl_criteria_2, exclude_paths=full_exclude_paths
    )

    # Test delete
    response = api_client.delete(url=f"{url_prefix}/StudyCriteria_000002")
    assert response.status_code == 204

    # Re-test get all - Make sure that the order has been updated after deletion
    # This test also adds a filter on criteria type
    filter_by = {"criteria_type.term_uid": {"v": [ct_term_inclusion_criteria.term_uid]}}
    response = api_client.get(url=f"{url_prefix}?filters={json.dumps(filter_by)}")
    res = response.json()

    assert response.status_code == 200
    assert len(res["items"]) == 1
    expected_incl_criteria_1["order"] = 1
    assert not DeepDiff(
        res["items"][0], expected_incl_criteria_1, exclude_paths=full_exclude_paths
    )

    # Test history for all selections
    response = api_client.get(url=f"{url_prefix}/audit-trail")
    res = response.json()

    assert response.status_code == 200
    assert len(res) == 9
    incl_criteria_1_entries = [
        i for i in res if i["study_criteria_uid"] == "StudyCriteria_000001"
    ]
    incl_criteria_1_orders = [i["order"] for i in incl_criteria_1_entries]
    incl_criteria_1_change_types = [i["change_type"] for i in incl_criteria_1_entries]
    incl_criteria_2_entries = [
        i for i in res if i["study_criteria_uid"] == "StudyCriteria_000002"
    ]
    incl_criteria_2_orders = [i["order"] for i in incl_criteria_2_entries]
    incl_criteria_2_change_types = [i["change_type"] for i in incl_criteria_2_entries]
    assert incl_criteria_1_orders == [1, 2, 2, 1]
    assert incl_criteria_1_change_types == ["Edit", "Edit", "Edit", "Create"]
    assert incl_criteria_2_orders == [1, 1, 2]
    assert incl_criteria_2_change_types == ["Delete", "Edit", "Create"]

    # Test history for specific selection
    response = api_client.get(url=f"{url_prefix}/StudyCriteria_000002/audit-trail")
    res = response.json()

    assert response.status_code == 200
    assert len(res) == 3
    change_types = [i["change_type"] for i in res]
    assert change_types == ["Delete", "Edit", "Create"]

    # Test batch select for template with parameter
    # This study criteria will stay as a template instead of an instance
    # It then needs to be finalized
    response = api_client.post(
        url=f"{url_prefix}/batch-select",
        json=[
            {
                "criteria_template_uid": excl_criteria_template_with_param.uid,
                "library_name": excl_criteria_template_with_param.library.name,
            },
        ],
    )
    res = response.json()

    assert response.status_code == 201
    expected_excl_criteria_with_param = copy.deepcopy(expected_excl_criteria_2)
    expected_excl_criteria_with_param["study_criteria_uid"] = "StudyCriteria_000005"
    expected_excl_criteria_with_param["order"] = 3
    del expected_excl_criteria_with_param["criteria"]
    del expected_excl_criteria_with_param["latest_criteria"]
    # Load the object with values directly from the Template object
    # It needs to be flattened into a dict beforehand though
    expected_excl_criteria_with_param["criteria_template"] = vars(
        excl_criteria_template_with_param
    )
    expected_excl_criteria_with_param["criteria_template"]["parameters"] = [
        {"name": "TextValue"}
    ]
    assert not DeepDiff(
        res[0],
        expected_excl_criteria_with_param,
        exclude_paths={*full_exclude_paths, *CRITERIA_TEMPLATE_IGNORED_FIELDS},
    )

    # Test finalise selection with parameter
    text_value = TestUtils.create_text_value()
    target_parameter_term = {
        "index": 1,
        "name": text_value.name,
        "type": "TextValue",
        "uid": text_value.uid,
    }
    response = api_client.patch(
        url=f"{url_prefix}/StudyCriteria_000005",
        json={
            "criteria_template_uid": excl_criteria_template_with_param.uid,
            "library_name": excl_criteria_template_with_param.library.name,
            "parameter_terms": [
                {
                    "conjunction": "",
                    "position": 1,
                    "value": None,
                    "terms": [target_parameter_term],
                }
            ],
            "key_criteria": True,
        },
    )
    res = response.json()

    assert response.status_code == 200
    expected_criteria_with_param_name = excl_criteria_template_with_param.name.replace(
        "TextValue", text_value.name_sentence_case
    )
    expected_criteria_with_param_name_plain = (
        expected_criteria_with_param_name.replace("[", "")
        .replace("]", "")
        .replace("<p>", "")
        .replace("</p>", "")
    )
    assert res["study_criteria_uid"] == "StudyCriteria_000005"
    assert res["order"] == 3
    assert res["criteria"]["uid"] == "Criteria_000005"
    assert res["criteria"]["name"] == expected_criteria_with_param_name
    assert res["criteria"]["name_plain"] == expected_criteria_with_param_name_plain
    assert res["key_criteria"] is True

    # Test get with project name and number filter
    project_name = res["project_name"]
    project_number = res["project_number"]
    response = api_client.get(
        url=f"{url_prefix}?project_name={project_name}&project_number={project_number}"
    )
    res = response.json()
    assert len(res["items"]) == 4

    # Test /headers endpoint - for all studies
    field_name = "criteria.name"
    search_string = "parameter"
    filter_by = {"criteria_type.term_uid": {"v": [ct_term_exclusion_criteria.term_uid]}}
    response = api_client.get(
        url=f"/study-criteria/headers?filters={json.dumps(filter_by)}&field_name={field_name}&search_string={search_string}"
    )
    res = response.json()

    assert response.status_code == 200
    assert len(res) == 1

    # Test /headers endpoint - for a specific study
    response = api_client.get(
        url=f"{url_prefix}/headers?filters={json.dumps(filter_by)}&field_name={field_name}&search_string={search_string}"
    )
    res = response.json()

    assert response.status_code == 200
    assert res == [expected_criteria_with_param_name]

    # Test batch select for template with parameter and provide parameter values
    # This study criteria will be created directly
    response = api_client.post(
        url=f"{url_prefix}/batch-select",
        json=[
            {
                "criteria_template_uid": excl_criteria_template_with_param.uid,
                "library_name": excl_criteria_template_with_param.library.name,
                "parameter_terms": [
                    {
                        "conjunction": "",
                        "position": 1,
                        "value": None,
                        "terms": [target_parameter_term],
                    }
                ],
            },
        ],
    )
    res = response.json()

    assert response.status_code == 201
    assert len(res) == 1
    assert res[0]["study_criteria_uid"] == "StudyCriteria_000006"
    assert res[0]["order"] == 4
    assert res[0]["criteria"]["uid"] == "Criteria_000005"
    assert res[0]["criteria"]["name"] == expected_criteria_with_param_name
    assert res[0]["criteria"]["name_plain"] == expected_criteria_with_param_name_plain


def test_errors(api_client):
    """Test that we get the expected errors when doing something wrong

    * Test that we get a 404 when we reference a non existent template in these endpoints :
    ** Preview
    ** Create
    ** Batch select

    """
    # Test selecting with a non-existent template uid
    dummy_template_uid = "dummy_template_uid"
    expected_response_code = 404
    expected_response_text = (
        f"Syntax Template with uid {dummy_template_uid} does not exist"
    )

    # Preview
    dummy_study_criteria_input = copy.deepcopy(default_study_criteria_input)
    dummy_study_criteria_input["criteria_data"][
        "criteria_template_uid"
    ] = dummy_template_uid
    response = api_client.post(
        url=f"{url_prefix}/preview",
        json=dummy_study_criteria_input,
    )
    res = response.json()

    assert response.status_code == expected_response_code
    assert res["message"] == expected_response_text

    # Creation
    response = api_client.post(
        url=f"{url_prefix}?create_criteria=true",
        json=dummy_study_criteria_input,
    )
    res = response.json()

    assert response.status_code == expected_response_code
    assert res["message"] == expected_response_text

    # Batch selection
    response = api_client.post(
        url=f"{url_prefix}/batch-select",
        json=[
            {
                "criteria_template_uid": dummy_template_uid,
                "library_name": incl_criteria_template_1.library.name,
            },
        ],
    )
    res = response.json()

    assert response.status_code == expected_response_code
    assert res["message"] == expected_response_text


def test_study_locking_study_criteria(api_client):
    study = TestUtils.create_study()
    url_prefix = f"/studies/{study.uid}/study-criteria"
    # Create selection
    api_client.post(
        url=f"{url_prefix}?create_criteria=true",
        json=default_study_criteria_input,
    )

    # get all criteria
    response = api_client.get(
        f"{url_prefix}/audit-trail/",
    )
    res = response.json()
    assert response.status_code == 200
    old_res = res
    criteria_uid = res[0]["study_criteria_uid"]

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
        url=f"{url_prefix}/preview",
        json=default_study_criteria_input,
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    response = api_client.patch(
        url=f"{url_prefix}/{criteria_uid}/order",
        json={"new_order": 2},
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    # get all history when was locked
    response = api_client.get(
        f"{url_prefix}/audit-trail/",
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
def test_get_study_criteria_csv_xml_excel(api_client, export_format):
    url = f"/studies/{study.uid}/study-criteria"
    TestUtils.verify_exported_data_format(api_client, export_format, url)
