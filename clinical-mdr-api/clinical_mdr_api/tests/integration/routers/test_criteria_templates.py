"""
Tests for /criteria-templates endpoints
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
from clinical_mdr_api.models.dictionary_codelist import DictionaryCodelist
from clinical_mdr_api.tests.integration.utils.api import (
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

BASE_SCENARIO_PATH = "clinical_mdr_api/tests/data/scenarios/"

log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
url_prefix: str
ct_term_inclusion_criteria: models.CTTerm
ct_term_exclusion_criteria: models.CTTerm
indications_library_name: str
indications_codelist: DictionaryCodelist
dictionary_term_indication: models.DictionaryTerm
ct_term_category: models.CTTerm
ct_term_subcategory: models.CTTerm
default_template_input: models.CriteriaTemplateCreateInput
inclusion_type_output: dict
exclusion_type_output: dict
default_template_output: dict


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    global url_prefix
    global ct_term_inclusion_criteria
    global ct_term_exclusion_criteria
    global indications_library_name
    global indications_codelist
    global dictionary_term_indication
    global ct_term_category
    global ct_term_subcategory
    global default_template_input
    global inclusion_type_output
    global exclusion_type_output
    global default_template_output

    """Initialize test data"""
    inject_and_clear_db("criteriatemplates.api")
    _ = inject_base_data()
    url_prefix = "/criteria-templates"

    # Create Template Parameter
    parameter_name = "TextValue"
    TestUtils.create_template_parameter(parameter_name)

    # Create Dictionary/CT Terms
    ct_term_inclusion_criteria = TestUtils.create_ct_term(
        sponsor_preferred_name="INCLUSION CRITERIA"
    )
    ct_term_exclusion_criteria = TestUtils.create_ct_term(
        sponsor_preferred_name="EXCLUSION CRITERIA"
    )
    indications_library_name = "SNOMED"
    indications_codelist = TestUtils.create_dictionary_codelist(
        name="DiseaseDisorder", library_name=indications_library_name
    )
    dictionary_term_indication = TestUtils.create_dictionary_term(
        codelist_uid=indications_codelist.codelist_uid,
        library_name=indications_library_name,
    )
    ct_term_category = TestUtils.create_ct_term()
    ct_term_subcategory = TestUtils.create_ct_term()

    # Define default inputs
    default_name = "Default name with [TextValue]"
    default_guidance_text = "Default guidance text"
    default_template_input = {
        "name": default_name,
        "guidance_text": default_guidance_text,
        "library_name": "Sponsor",
        "default_parameter_values": [],
        "editable_instance": False,
        "type_uid": ct_term_inclusion_criteria.term_uid,
        "indication_uids": [dictionary_term_indication.term_uid],
        "category_uids": [ct_term_category.term_uid],
        "sub_category_uids": [ct_term_subcategory.term_uid],
    }

    # Define default expected outputs
    inclusion_type_output = {
        "term_uid": ct_term_inclusion_criteria.term_uid,
        "catalogue_name": ct_term_inclusion_criteria.catalogue_name,
        "codelist_uid": ct_term_inclusion_criteria.codelist_uid,
        "library_name": ct_term_inclusion_criteria.library_name,
        "name": {
            "sponsor_preferred_name": ct_term_inclusion_criteria.sponsor_preferred_name
        },
        "attributes": {
            "code_submission_value": ct_term_inclusion_criteria.code_submission_value,
            "name_submission_value": ct_term_inclusion_criteria.name_submission_value,
            "nci_preferred_name": ct_term_inclusion_criteria.nci_preferred_name,
        },
    }
    exclusion_type_output = {
        "term_uid": ct_term_exclusion_criteria.term_uid,
        "catalogue_name": ct_term_exclusion_criteria.catalogue_name,
        "codelist_uid": ct_term_exclusion_criteria.codelist_uid,
        "library_name": ct_term_exclusion_criteria.library_name,
        "name": {
            "sponsor_preferred_name": ct_term_exclusion_criteria.sponsor_preferred_name
        },
        "attributes": {
            "code_submission_value": ct_term_exclusion_criteria.code_submission_value,
            "name_submission_value": ct_term_exclusion_criteria.name_submission_value,
            "nci_preferred_name": ct_term_exclusion_criteria.nci_preferred_name,
        },
    }
    default_template_output = {
        "name": default_name,
        "name_plain": default_name,
        "guidance_text": default_guidance_text,
        "uid": "CriteriaTemplate_000001",
        "editable_instance": False,
        "status": "Draft",
        "version": "0.1",
        "change_description": "Initial version",
        "possible_actions": ["approve", "delete", "edit"],
        "parameters": [{"name": "TextValue", "values": None}],
        "default_parameter_values": {
            "0": [{"position": 1, "conjunction": "", "values": []}]
        },
        "library": {"name": "Sponsor", "is_editable": True},
        "type": inclusion_type_output,
        "indications": [
            {
                "term_uid": dictionary_term_indication.term_uid,
                "dictionary_id": dictionary_term_indication.dictionary_id,
                "name": dictionary_term_indication.name,
                "library_name": dictionary_term_indication.library_name,
            }
        ],
        "categories": [
            {
                "term_uid": ct_term_category.term_uid,
                "catalogue_name": ct_term_category.catalogue_name,
                "codelist_uid": ct_term_category.codelist_uid,
                "library_name": ct_term_category.library_name,
            }
        ],
        "sub_categories": [
            {
                "term_uid": ct_term_subcategory.term_uid,
                "catalogue_name": ct_term_subcategory.catalogue_name,
                "codelist_uid": ct_term_subcategory.codelist_uid,
                "library_name": ct_term_subcategory.library_name,
            }
        ],
        "study_count": None,
    }


ROOT_IGNORED_FIELDS = {
    "root['start_date']",
    "root['end_date']",
    "root['user_initials']",
}
CRITERIA_TYPE_NAME_IGNORED_FIELDS = {
    "root['type']['name']['term_uid']",
    "root['type']['name']['catalogue_name']",
    "root['type']['name']['codelist_uid']",
    "root['type']['name']['sponsor_preferred_name_sentence_case']",
    "root['type']['name']['order']",
    "root['type']['name']['library_name']",
    "root['type']['name']['start_date']",
    "root['type']['name']['end_date']",
    "root['type']['name']['status']",
    "root['type']['name']['version']",
    "root['type']['name']['change_description']",
    "root['type']['name']['user_initials']",
    "root['type']['name']['possible_actions']",
}
CRITERIA_TYPE_ATTRIBUTES_IGNORED_FIELDS = {
    "root['type']['attributes']['term_uid']",
    "root['type']['attributes']['catalogue_name']",
    "root['type']['attributes']['codelist_uid']",
    "root['type']['attributes']['concept_id']",
    "root['type']['attributes']['definition']",
    "root['type']['attributes']['library_name']",
    "root['type']['attributes']['start_date']",
    "root['type']['attributes']['end_date']",
    "root['type']['attributes']['status']",
    "root['type']['attributes']['version']",
    "root['type']['attributes']['change_description']",
    "root['type']['attributes']['user_initials']",
    "root['type']['attributes']['possible_actions']",
}
INDICATION_IGNORED_FIELDS = {
    "root['indications'][0]['name_sentence_case']",
    "root['indications'][0]['abbreviation']",
    "root['indications'][0]['definition']",
    "root['indications'][0]['possible_actions']",
    "root['indications'][0]['start_date']",
    "root['indications'][0]['end_date']",
    "root['indications'][0]['status']",
    "root['indications'][0]['version']",
    "root['indications'][0]['change_description']",
    "root['indications'][0]['user_initials']",
}
CATEGORIES_IGNORED_FIELDS = {
    "root['categories'][0]['name']",
    "root['categories'][0]['attributes']",
}
SUB_CATEGORIES_IGNORED_FIELDS = {
    "root['sub_categories'][0]['name']",
    "root['sub_categories'][0]['attributes']",
}


def test_crud_criteria_templates(api_client):
    """Test all endpoints for criteria-template routers.
    This covers all the CRUD operations

    * Pre-validate name
    * Create as draft with different types - with default parameter values
    * Patch default parameter values - existing set
    * Add a default parameter value set
    * Change groupings
    * Get all
    * Get headers
    * Get specific
    * Delete
    """

    full_exclude_paths = {
        *ROOT_IGNORED_FIELDS,
        *CRITERIA_TYPE_NAME_IGNORED_FIELDS,
        *CRITERIA_TYPE_ATTRIBUTES_IGNORED_FIELDS,
        *INDICATION_IGNORED_FIELDS,
        *CATEGORIES_IGNORED_FIELDS,
        *SUB_CATEGORIES_IGNORED_FIELDS,
    }

    inclusion_template_input = copy.deepcopy(default_template_input)
    exclusion_template_input = copy.deepcopy(default_template_input)

    # Pre-validate
    response = api_client.post(
        url=f"{url_prefix}/pre-validate",
        json={"name": inclusion_template_input["name"]},
    )
    assert response.status_code == 202

    # Create as draft - Inclusion
    inclusion_template_output = copy.deepcopy(default_template_output)
    response = api_client.post(url=url_prefix, json=inclusion_template_input)
    res = response.json()

    assert response.status_code == 201
    assert not DeepDiff(
        res, inclusion_template_output, exclude_paths=full_exclude_paths
    )

    # Create as draft - Exclusion - With default parameter values
    exclusion_template_output = copy.deepcopy(default_template_output)

    text_value_1 = TestUtils.create_text_value()
    default_parameter_value_1 = {
        "position": 1,
        "conjunction": "",
        "values": [
            {
                "index": 1,
                "name": text_value_1.name,
                "uid": text_value_1.uid,
                "type": "TextValue",
            }
        ],
    }
    exclusion_template_input["default_parameter_values"] = [default_parameter_value_1]
    exclusion_template_input["type_uid"] = ct_term_exclusion_criteria.term_uid

    exclusion_template_uid = inclusion_template_output["uid"][:-1] + "2"
    exclusion_template_output["uid"] = exclusion_template_uid
    exclusion_template_output["type"] = exclusion_type_output
    exclusion_template_output["default_parameter_values"] = {
        "0": [default_parameter_value_1]
    }

    response = api_client.post(url=url_prefix, json=exclusion_template_input)
    res = response.json()

    assert response.status_code == 201
    assert not DeepDiff(
        res, exclusion_template_output, exclude_paths=full_exclude_paths
    )

    # Change default parameter values
    text_value_2 = TestUtils.create_text_value()
    default_parameter_value_2 = {
        "position": 1,
        "conjunction": "and",
        "values": [
            {
                "index": 1,
                "name": text_value_1.name,
                "uid": text_value_1.uid,
                "type": "TextValue",
            },
            {
                "index": 2,
                "name": text_value_2.name,
                "uid": text_value_2.uid,
                "type": "TextValue",
            },
        ],
    }

    response = api_client.patch(
        url=f"{url_prefix}/{exclusion_template_uid}/default-parameter-values",
        json={"set_number": 0, "default_parameter_values": [default_parameter_value_2]},
    )
    res = response.json()

    assert response.status_code == 200

    exclusion_template_output["default_parameter_values"] = {
        "0": [default_parameter_value_2]
    }
    exclusion_template_output["study_count"] = 0
    assert not DeepDiff(
        res, exclusion_template_output, exclude_paths=full_exclude_paths
    )

    # Change groupings - First indications and sub categories, then categories
    # This will test that it can replace, append, without deleting the not passed elements
    # And it will in a second step test that all of the groupings patching work
    dictionary_term_indication_2 = TestUtils.create_dictionary_term(
        codelist_uid=indications_codelist.codelist_uid,
        library_name=indications_library_name,
    )
    ct_term_category_2 = TestUtils.create_ct_term()
    ct_term_subcategory_2 = TestUtils.create_ct_term()
    response = api_client.patch(
        url=f"{url_prefix}/{exclusion_template_uid}/groupings",
        json={
            "indication_uids": [dictionary_term_indication_2.term_uid],
            "sub_category_uids": [
                ct_term_subcategory.term_uid,
                ct_term_subcategory_2.term_uid,
            ],
        },
    )
    res = response.json()

    assert response.status_code == 200
    exclusion_template_output["indications"] = [
        {
            "term_uid": dictionary_term_indication_2.term_uid,
            "dictionary_id": dictionary_term_indication_2.dictionary_id,
            "name": dictionary_term_indication_2.name,
            "library_name": dictionary_term_indication_2.library_name,
        }
    ]
    exclusion_template_output["sub_categories"].append(
        {
            "term_uid": ct_term_subcategory_2.term_uid,
            "catalogue_name": ct_term_subcategory_2.catalogue_name,
            "codelist_uid": ct_term_subcategory_2.codelist_uid,
            "library_name": ct_term_subcategory_2.library_name,
        }
    )
    SUB_CATEGORIES_IGNORED_FIELDS_2 = {
        "root['sub_categories'][1]['name']",
        "root['sub_categories'][1]['attributes']",
    }
    assert not DeepDiff(
        res,
        exclusion_template_output,
        exclude_paths=[*full_exclude_paths, *SUB_CATEGORIES_IGNORED_FIELDS_2],
    )

    # Change groupings - Categories
    response = api_client.patch(
        url=f"{url_prefix}/{exclusion_template_uid}/groupings",
        json={"category_uids": [ct_term_category_2.term_uid]},
    )
    res = response.json()

    assert response.status_code == 200
    exclusion_template_output["categories"] = [
        {
            "term_uid": ct_term_category_2.term_uid,
            "catalogue_name": ct_term_category_2.catalogue_name,
            "codelist_uid": ct_term_category_2.codelist_uid,
            "library_name": ct_term_category_2.library_name,
        }
    ]
    assert not DeepDiff(
        res,
        exclusion_template_output,
        exclude_paths=[*full_exclude_paths, *SUB_CATEGORIES_IGNORED_FIELDS_2],
    )

    # Get all
    response = api_client.get(url=f"{url_prefix}?total_count=true")
    res = response.json()

    assert response.status_code == 200
    assert res["total"] == 2
    assert len(res["items"]) == 2

    # Get all - with filters
    filter_by = {"type.term_uid": {"v": [ct_term_inclusion_criteria.term_uid]}}
    response = api_client.get(url=f"{url_prefix}?filters={json.dumps(filter_by)}")
    res = response.json()

    assert response.status_code == 200
    assert len(res["items"]) == 1
    inclusion_template_output["study_count"] = 0
    assert not DeepDiff(
        res["items"][0], inclusion_template_output, exclude_paths=full_exclude_paths
    )

    # Get headers
    field_name = "type.name.sponsor_preferred_name"
    search_string = "inclusion"
    response = api_client.get(
        url=f"{url_prefix}/headers?field_name={field_name}&search_string={search_string}"
    )
    res = response.json()

    assert response.status_code == 200
    assert res == ["INCLUSION CRITERIA"]

    # Get specific
    response = api_client.get(url=f"{url_prefix}/{inclusion_template_output['uid']}")
    res = response.json()

    assert response.status_code == 200
    inclusion_template_output["counts"] = None
    assert not DeepDiff(
        res, inclusion_template_output, exclude_paths=full_exclude_paths
    )

    # Delete
    response = api_client.delete(url=f"{url_prefix}/{exclusion_template_uid}")
    assert response.status_code == 204

    # Get all to check deletion
    response = api_client.get(url=f"{url_prefix}?total_count=true")
    res = response.json()

    assert response.status_code == 200
    assert res["total"] == 1


def test_versioning_criteria_templates(api_client):
    """Test endpoints specific to versioning

    * Approve
    * Create new version
    * Patch (must be in Draft)
    * Inactivate
    * Reactivate
    * Get versions
    * Get specific version
    * Get releases
    """

    # Create a template
    inclusion_template_input = copy.deepcopy(default_template_input)
    inclusion_template_input["name"] += " 2"
    response = api_client.post(url=url_prefix, json=inclusion_template_input)
    res = response.json()
    template_uid = res["uid"]

    # Approve
    response = api_client.post(url=f"{url_prefix}/{template_uid}/approve")
    res = response.json()
    assert response.status_code == 201
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["change_description"] == "Approved version"

    # Create new version
    change_description_new_version = "Create new version"
    response = api_client.post(
        url=f"{url_prefix}/{template_uid}/versions",
        json={
            "name": default_template_input["name"],
            "change_description": change_description_new_version,
        },
    )
    res = response.json()
    assert response.status_code == 201
    assert res["status"] == "Draft"
    assert res["version"] == "1.1"
    assert res["change_description"] == change_description_new_version

    # Patch template
    new_name = "<p>New name for template with [TextValue]</p>"
    change_description_new_name = "Changed template name"
    response = api_client.patch(
        url=f"{url_prefix}/{template_uid}",
        json={"name": new_name, "change_description": change_description_new_name},
    )
    res = response.json()
    assert response.status_code == 200
    assert res["name"] == new_name
    assert res["name_plain"] == new_name.replace("<p>", "").replace("</p>", "")
    assert res["status"] == "Draft"
    assert res["version"] == "1.2"
    assert res["change_description"] == change_description_new_name

    # Inactivate
    _ = api_client.post(url=f"{url_prefix}/{template_uid}/approve")
    response = api_client.post(url=f"{url_prefix}/{template_uid}/inactivate")
    res = response.json()
    assert response.status_code == 201
    assert res["status"] == "Retired"
    assert res["version"] == "2.0"
    assert res["change_description"] == "Deactivated version"

    # Reactivate
    response = api_client.post(url=f"{url_prefix}/{template_uid}/reactivate")
    res = response.json()
    assert response.status_code == 201
    assert res["status"] == "Final"
    assert res["version"] == "2.0"
    assert res["change_description"] == "Reactivated version"

    # Get versions
    response = api_client.get(url=f"{url_prefix}/{template_uid}/versions")
    res = response.json()
    assert response.status_code == 200
    assert len(res) == 7
    extract_versions = [{"status": v["status"], "version": v["version"]} for v in res]
    assert extract_versions == [
        {"status": "Final", "version": "2.0"},
        {"status": "Retired", "version": "2.0"},
        {"status": "Final", "version": "2.0"},
        {"status": "Draft", "version": "1.2"},
        {"status": "Draft", "version": "1.1"},
        {"status": "Final", "version": "1.0"},
        {"status": "Draft", "version": "0.1"},
    ]

    # Get specific version
    response = api_client.get(url=f"{url_prefix}/{template_uid}/versions/2.0")
    res = response.json()
    assert response.status_code == 200
    assert res["status"] == "Final"
    assert res["version"] == "2.0"

    # Get releases
    response = api_client.get(url=f"{url_prefix}/{template_uid}/releases")
    res = response.json()
    assert response.status_code == 200
    # This is 1 and not 3 because this looks for the number of different Value nodes
    # We didn't change the name after approving, so it's only a single Value node
    assert len(res) == 2
    extract_versions = [{"status": v["status"], "version": v["version"]} for v in res]
    assert extract_versions == [
        {"status": "Final", "version": "2.0"},
        {"status": "Final", "version": "1.0"},
    ]


def test_errors_criteria_templates(api_client):
    """Test that we get the expected errors when doing something wrong

    * Create with same name in a given type
    * Patch name to a duplicate in a given type
    * Patch without change description
    * Patch template in Final status
    * Patch name and change parameter set after it has been approved
    * Pre-validate invalid name
    * Create in a library that doesn't exist
    * Create in a read-only library
    """

    # Create a template
    inclusion_template_input = copy.deepcopy(default_template_input)
    inclusion_template_input["name"] += " 3"
    response = api_client.post(url=url_prefix, json=inclusion_template_input)
    res = response.json()
    template_uid = res["uid"]

    # Create template with the same name and type
    response = api_client.post(url=url_prefix, json=inclusion_template_input)
    res = response.json()
    assert response.status_code == 400
    assert (
        res["message"]
        == f"Duplicate templates not allowed - template exists: {inclusion_template_input['name']}"
    )

    # Create a template with different name
    # Then patch its name to the same as the existing template
    inclusion_template_input_2 = copy.deepcopy(default_template_input)
    inclusion_template_input_2["name"] = "Different name with [TextValue]"
    response = api_client.post(url=url_prefix, json=inclusion_template_input_2)
    res = response.json()
    template_uid_2 = res["uid"]

    response = api_client.patch(
        url=f"{url_prefix}/{template_uid_2}",
        json={
            "name": inclusion_template_input["name"],
            "change_description": "Change for duplicate",
        },
    )
    res = response.json()
    assert response.status_code == 500
    assert (
        res["message"]
        == f"Duplicate templates not allowed - template exists: {inclusion_template_input['name']}"
    )

    # Patch without change description
    response = api_client.patch(
        url=f"{url_prefix}/{template_uid}",
        json={"name": "Random new name with [TextValue]"},
    )
    res = response.json()
    assert response.status_code == 422
    assert res["detail"] == [
        {
            "loc": ["body", "change_description"],
            "msg": "field required",
            "type": "value_error.missing",
        }
    ]

    # Patch template in Final status
    _ = api_client.post(url=f"{url_prefix}/{template_uid}/approve")
    response = api_client.patch(
        url=f"{url_prefix}/{template_uid}",
        json={
            "name": "Patch approved template [TextValue]",
            "change_description": "Patch approved template",
        },
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == "The object is not in draft status."

    # Patch name and change parameter set after it has been approved
    _ = api_client.post(url=f"{url_prefix}/{template_uid}/versions")
    response = api_client.patch(
        url=f"{url_prefix}/{template_uid}",
        json={
            "name": "Change parameter set",
            "change_description": "Change parameter set",
        },
    )
    res = response.json()
    assert response.status_code == 400
    assert (
        res["message"]
        == "You cannot change number or order of template parameters for a previously approved template."
    )

    # Pre-validate invalid name
    invalid_name = "Missing opening bracket ]"
    response = api_client.post(
        url=f"{url_prefix}/pre-validate",
        json={"name": invalid_name},
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Template string syntax incorrect: {invalid_name}"

    invalid_name = "Lacking closing bracket ["
    response = api_client.post(
        url=f"{url_prefix}/pre-validate",
        json={"name": invalid_name},
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Template string syntax incorrect: {invalid_name}"

    invalid_name = " "
    response = api_client.post(
        url=f"{url_prefix}/pre-validate",
        json={"name": invalid_name},
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Template string syntax incorrect: {invalid_name}"

    # Create in a library that doesn't exist
    inclusion_template_input_no_library = copy.deepcopy(default_template_input)
    inclusion_template_input_no_library["name"] = "Using invalid library"
    inclusion_template_input_no_library["library_name"] = "No library"
    response = api_client.post(url=url_prefix, json=inclusion_template_input_no_library)
    res = response.json()

    assert response.status_code == 404
    assert (
        res["message"]
        == f"The library with the name='{inclusion_template_input_no_library['library_name']}' could not be found."
    )

    # Create in a read-only library
    read_only_library = TestUtils.create_library(name="Read only", is_editable=False)
    inclusion_template_input_read_only_library = copy.deepcopy(
        inclusion_template_input_no_library
    )
    inclusion_template_input_read_only_library["library_name"] = read_only_library[
        "name"
    ]
    response = api_client.post(
        url=url_prefix, json=inclusion_template_input_read_only_library
    )
    res = response.json()

    assert response.status_code == 400
    assert (
        res["message"]
        == f"The library with the name='{inclusion_template_input_read_only_library['library_name']}' does not allow to create objects."
    )
