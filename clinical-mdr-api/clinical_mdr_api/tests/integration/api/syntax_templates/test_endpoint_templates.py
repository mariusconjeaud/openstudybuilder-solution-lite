"""
Tests for endpoint-templates endpoints
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import json
import logging
from functools import reduce
from typing import List

import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api import models
from clinical_mdr_api.main import app
from clinical_mdr_api.models.syntax_templates.endpoint_template import EndpointTemplate
from clinical_mdr_api.models.template_parameter_term import (
    IndexedTemplateParameterTerm,
    MultiTemplateParameterTerm,
)
from clinical_mdr_api.tests.integration.utils.api import (
    drop_db,
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
endpoint_templates: List[EndpointTemplate]
ct_term_inclusion: models.CTTerm
dictionary_term_indication: models.DictionaryTerm
ct_term_category: models.CTTerm
ct_term_subcategory: models.CTTerm
indications_codelist: models.DictionaryCodelist
indications_library_name: str
text_value_1: models.TextValue
text_value_2: models.TextValue

URL = "endpoint-templates"


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    inject_and_clear_db(URL + ".api")
    inject_base_data()

    global endpoint_templates
    global ct_term_inclusion
    global dictionary_term_indication
    global ct_term_category
    global ct_term_subcategory
    global indications_codelist
    global indications_library_name
    global text_value_1
    global text_value_2

    # Create Template Parameter
    TestUtils.create_template_parameter("TextValue")

    text_value_1 = TestUtils.create_text_value()
    text_value_2 = TestUtils.create_text_value()

    # Create Dictionary/CT Terms
    ct_term_inclusion = TestUtils.create_ct_term(
        sponsor_preferred_name="INCLUSION ENDPOINT"
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

    # Create some endpoint_templates
    endpoint_templates = []
    endpoint_templates.append(
        TestUtils.create_endpoint_template(
            name="Default name with [TextValue]",
            guidance_text="Default guidance text",
            study_uid=None,
            library_name="Sponsor",
            default_parameter_terms=[
                MultiTemplateParameterTerm(
                    position=1,
                    conjunction="",
                    terms=[
                        IndexedTemplateParameterTerm(
                            index=1,
                            name=text_value_1.name,
                            uid=text_value_1.uid,
                            type="TextValue",
                        )
                    ],
                )
            ],
            indication_uids=[dictionary_term_indication.term_uid],
            category_uids=[ct_term_category.term_uid],
            sub_category_uids=[ct_term_subcategory.term_uid],
        )
    )
    endpoint_templates.append(
        TestUtils.create_endpoint_template(
            name="Default-AAA name with [TextValue]",
            guidance_text="Default-AAA guidance text",
            study_uid=None,
            library_name="Sponsor",
            default_parameter_terms=None,
            indication_uids=[dictionary_term_indication.term_uid],
            category_uids=[ct_term_category.term_uid],
            sub_category_uids=[ct_term_subcategory.term_uid],
        )
    )
    endpoint_templates.append(
        TestUtils.create_endpoint_template(
            name="Default-BBB name with [TextValue]",
            guidance_text="Default-BBB guidance text",
            study_uid=None,
            library_name="Sponsor",
            default_parameter_terms=None,
            indication_uids=[dictionary_term_indication.term_uid],
            category_uids=[ct_term_category.term_uid],
            sub_category_uids=[ct_term_subcategory.term_uid],
            approve=False,
        )
    )
    endpoint_templates.append(
        TestUtils.create_endpoint_template(
            name="Default-XXX name with [TextValue]",
            guidance_text="Default-XXX guidance text",
            study_uid=None,
            library_name="Sponsor",
            default_parameter_terms=None,
            indication_uids=[dictionary_term_indication.term_uid],
            category_uids=[ct_term_category.term_uid],
            sub_category_uids=[ct_term_subcategory.term_uid],
            approve=False,
        )
    )
    endpoint_templates.append(
        TestUtils.create_endpoint_template(
            name="Default-YYY name with [TextValue]",
            guidance_text="Default-YYY guidance text",
            study_uid=None,
            library_name="Sponsor",
            default_parameter_terms=None,
            indication_uids=[dictionary_term_indication.term_uid],
            category_uids=[ct_term_category.term_uid],
            sub_category_uids=[ct_term_subcategory.term_uid],
        )
    )

    for index in range(5):
        endpoint_templates.append(
            TestUtils.create_endpoint_template(
                name=f"Default-AAA-{index} name with [TextValue]",
                guidance_text=f"Default-AAA-{index} guidance text",
                study_uid=None,
                library_name="Sponsor",
                default_parameter_terms=None,
                indication_uids=[dictionary_term_indication.term_uid],
                category_uids=[ct_term_category.term_uid],
                sub_category_uids=[ct_term_subcategory.term_uid],
            )
        )
        endpoint_templates.append(
            TestUtils.create_endpoint_template(
                name=f"Default-BBB-{index} name with [TextValue]",
                guidance_text=f"Default-BBB-{index} guidance text",
                study_uid=None,
                library_name="Sponsor",
                default_parameter_terms=None,
                indication_uids=[dictionary_term_indication.term_uid],
                category_uids=[ct_term_category.term_uid],
                sub_category_uids=[ct_term_subcategory.term_uid],
            )
        )
        endpoint_templates.append(
            TestUtils.create_endpoint_template(
                name=f"Default-XXX-{index} name with [TextValue]",
                guidance_text=f"Default-XXX-{index} guidance text",
                study_uid=None,
                library_name="Sponsor",
                default_parameter_terms=None,
                indication_uids=[dictionary_term_indication.term_uid],
                category_uids=[ct_term_category.term_uid],
                sub_category_uids=[ct_term_subcategory.term_uid],
            )
        )
        endpoint_templates.append(
            TestUtils.create_endpoint_template(
                name=f"Default-YYY-{index} name with [TextValue]",
                guidance_text=f"Default-YYY-{index} guidance text",
                study_uid=None,
                library_name="Sponsor",
                default_parameter_terms=None,
                indication_uids=[dictionary_term_indication.term_uid],
                category_uids=[ct_term_category.term_uid],
                sub_category_uids=[ct_term_subcategory.term_uid],
            )
        )

    yield

    drop_db(URL + ".api")


ENDPOINT_TEMPLATE_FIELDS_ALL = [
    "name",
    "name_plain",
    "guidance_text",
    "uid",
    "status",
    "version",
    "change_description",
    "start_date",
    "end_date",
    "user_initials",
    "possible_actions",
    "parameters",
    "default_parameter_terms",
    "library",
    "indications",
    "categories",
    "sub_categories",
    "study_count",
]

ENDPOINT_TEMPLATE_FIELDS_NOT_NULL = [
    "uid",
    "name",
]


def test_get_endpoint_template(api_client):
    response = api_client.get(f"{URL}/{endpoint_templates[1].uid}")
    res = response.json()

    assert response.status_code == 200

    # Check fields included in the response
    fields_all_set = set(ENDPOINT_TEMPLATE_FIELDS_ALL)
    fields_all_set.add("counts")
    assert set(list(res.keys())) == fields_all_set
    for key in ENDPOINT_TEMPLATE_FIELDS_NOT_NULL:
        assert res[key] is not None

    assert res["uid"] == endpoint_templates[1].uid
    assert res["name"] == "Default-AAA name with [TextValue]"
    assert res["guidance_text"] == "Default-AAA guidance text"
    assert res["parameters"][0]["name"] == "TextValue"
    assert res["parameters"][0]["terms"] is None
    assert res["indications"][0]["term_uid"] == dictionary_term_indication.term_uid
    assert (
        res["indications"][0]["dictionary_id"]
        == dictionary_term_indication.dictionary_id
    )
    assert res["indications"][0]["name"] == dictionary_term_indication.name
    assert res["categories"][0]["term_uid"] == ct_term_category.term_uid
    assert res["categories"][0]["catalogue_name"] == ct_term_category.catalogue_name
    assert res["categories"][0]["codelist_uid"] == ct_term_category.codelist_uid
    assert res["sub_categories"][0]["term_uid"] == ct_term_subcategory.term_uid
    assert (
        res["sub_categories"][0]["catalogue_name"] == ct_term_subcategory.catalogue_name
    )
    assert res["sub_categories"][0]["codelist_uid"] == ct_term_subcategory.codelist_uid
    assert res["version"] == "1.0"
    assert res["status"] == "Final"


def test_get_endpoint_templates_pagination(api_client):
    results_paginated: dict = {}
    sort_by = '{"uid": true}'
    for page_number in range(1, 4):
        response = api_client.get(
            f"{URL}?page_number={page_number}&page_size=10&sort_by={sort_by}"
        )
        res = response.json()
        res_uids = list(map(lambda x: x["uid"], res["items"]))
        results_paginated[page_number] = res_uids
        log.info("Page %s: %s", page_number, res_uids)

    log.info("All pages: %s", results_paginated)

    results_paginated_merged = list(
        list(reduce(lambda a, b: a + b, list(results_paginated.values())))
    )
    log.info("All rows returned by pagination: %s", results_paginated_merged)

    res_all = api_client.get(
        f"{URL}?page_number=1&page_size=100&sort_by={sort_by}"
    ).json()
    results_all_in_one_page = list(map(lambda x: x["uid"], res_all["items"]))
    log.info("All rows in one page: %s", results_all_in_one_page)
    assert len(results_all_in_one_page) == len(results_paginated_merged)
    assert len(endpoint_templates) == len(results_paginated_merged)


@pytest.mark.parametrize(
    "page_size, page_number, total_count, sort_by, expected_result_len",
    [
        pytest.param(None, None, True, None, 10),
        pytest.param(3, 1, True, None, 3),
        pytest.param(3, 2, True, None, 3),
        pytest.param(10, 2, True, None, 10),
        pytest.param(10, 3, True, None, 5),  # Total number of data models is 25
        pytest.param(10, 1, True, '{"name": false}', 10),
        pytest.param(10, 2, True, '{"name": true}', 10),
    ],
)
def test_get_endpoint_templates(
    api_client, page_size, page_number, total_count, sort_by, expected_result_len
):
    url = URL
    query_params = []
    if page_size:
        query_params.append(f"page_size={page_size}")
    if page_number:
        query_params.append(f"page_number={page_number}")
    if total_count:
        query_params.append(f"total_count={total_count}")
    if sort_by:
        query_params.append(f"sort_by={sort_by}")

    if query_params:
        url = f"{url}?{'&'.join(query_params)}"

    log.info("GET %s", url)
    response = api_client.get(url)
    res = response.json()

    assert response.status_code == 200

    # Check fields included in the response
    assert list(res.keys()) == ["items", "total", "page", "size"]
    assert len(res["items"]) == expected_result_len
    assert res["total"] == (len(endpoint_templates) if total_count else 0)
    assert res["page"] == (page_number if page_number else 1)
    assert res["size"] == (page_size if page_size else 10)

    for item in res["items"]:
        assert set(list(item.keys())) == set(ENDPOINT_TEMPLATE_FIELDS_ALL)
        for key in ENDPOINT_TEMPLATE_FIELDS_NOT_NULL:
            assert item[key] is not None

    if sort_by:
        # sort_by is JSON string in the form: {"sort_field_name": is_ascending_order}
        sort_by_dict = json.loads(sort_by)
        sort_field: str = list(sort_by_dict.keys())[0]
        sort_order_ascending: bool = list(sort_by_dict.values())[0]

        # extract list of values of 'sort_field_name' field from the returned result
        result_vals = list(map(lambda x: x[sort_field], res["items"]))
        result_vals_sorted_locally = result_vals.copy()
        result_vals_sorted_locally.sort(reverse=not sort_order_ascending)
        # This assert fails due to API issue with sorting coupled with pagination
        # assert result_vals == result_vals_sorted_locally


def test_get_all_parameters_of_endpoint_template(api_client):
    response = api_client.get(f"{URL}/{endpoint_templates[0].uid}/parameters")
    res = response.json()

    assert response.status_code == 200
    assert len(res) == 1
    assert res[0]["name"] == "TextValue"
    assert len(res[0]["terms"]) == 2


def test_get_versions_of_endpoint_template(api_client):
    response = api_client.get(f"{URL}/{endpoint_templates[1].uid}/versions")
    res = response.json()

    assert response.status_code == 200

    assert len(res) == 2
    assert res[0]["uid"] == endpoint_templates[1].uid
    assert res[0]["version"] == "1.0"
    assert res[0]["status"] == "Final"
    assert res[1]["uid"] == endpoint_templates[1].uid
    assert res[1]["version"] == "0.1"
    assert res[1]["status"] == "Draft"


def test_get_all_final_versions_of_endpoint_template(api_client):
    response = api_client.get(f"{URL}/{endpoint_templates[1].uid}/releases")
    res = response.json()

    assert response.status_code == 200

    assert len(res) == 1
    assert res[0]["uid"] == endpoint_templates[1].uid
    assert res[0]["version"] == "1.0"
    assert res[0]["status"] == "Final"


@pytest.mark.parametrize(
    "filter_by, expected_matched_field, expected_result_prefix",
    [
        pytest.param(
            '{"*": {"v": ["Default-AAA"], "op": "co"}}', "name", "Default-AAA"
        ),
        pytest.param(
            '{"*": {"v": ["Default-BBB"], "op": "co"}}', "name", "Default-BBB"
        ),
        pytest.param('{"*": {"v": ["cc"], "op": "co"}}', None, None),
        pytest.param(
            '{"*": {"v": ["Default-XXX"], "op": "co"}}', "guidance_text", "Default-XXX"
        ),
        pytest.param(
            '{"*": {"v": ["Default-YYY"], "op": "co"}}', "guidance_text", "Default-YYY"
        ),
        pytest.param('{"*": {"v": ["cc"], "op": "co"}}', None, None),
    ],
)
def test_filtering_wildcard(
    api_client, filter_by, expected_matched_field, expected_result_prefix
):
    response = api_client.get(f"{URL}?filters={filter_by}")
    res = response.json()

    assert response.status_code == 200
    if expected_result_prefix:
        assert len(res["items"]) > 0
        # Each returned row has a field that starts with the specified filter value
        for row in res["items"]:
            assert row[expected_matched_field].startswith(expected_result_prefix)
    else:
        assert len(res["items"]) == 0


@pytest.mark.parametrize(
    "filter_by, expected_matched_field, expected_result",
    [
        pytest.param(
            '{"name": {"v": ["Default-AAA"], "op": "co"}}', "name", "Default-AAA"
        ),
        pytest.param(
            '{"name": {"v": ["Default-BBB"], "op": "co"}}', "name", "Default-BBB"
        ),
        pytest.param('{"name": {"v": ["cc"], "op": "co"}}', None, None),
        pytest.param(
            '{"guidance_text": {"v": ["Default-XXX"], "op": "co"}}',
            "guidance_text",
            "Default-XXX",
        ),
        pytest.param(
            '{"guidance_text": {"v": ["Default-YYY"], "op": "co"}}',
            "guidance_text",
            "Default-YYY",
        ),
        pytest.param('{"guidance_text": {"v": ["cc"], "op": "co"}}', None, None),
    ],
)
def test_filtering_exact(
    api_client, filter_by, expected_matched_field, expected_result
):
    response = api_client.get(f"{URL}?filters={filter_by}")
    res = response.json()

    assert response.status_code == 200
    if expected_result:
        assert len(res["items"]) > 0
        # Each returned row has a field whose value is equal to the specified filter value
        for row in res["items"]:
            if isinstance(expected_result, list):
                assert all(
                    item in row[expected_matched_field] for item in expected_result
                )
            else:
                assert expected_result in row[expected_matched_field]
    else:
        assert len(res["items"]) == 0


@pytest.mark.parametrize(
    "field_name",
    [
        pytest.param("name"),
    ],
)
def test_headers(api_client, field_name):
    response = api_client.get(f"{URL}/headers?field_name={field_name}&result_count=100")
    res = response.json()

    assert response.status_code == 200
    expected_result = []
    for endpoint_template in endpoint_templates:
        value = getattr(endpoint_template, field_name)
        if value:
            expected_result.append(value)
    log.info("Expected result is %s", expected_result)
    log.info("Returned %s", res)
    if expected_result:
        assert len(res) > 0
        assert len(set(expected_result)) == len(res)
        assert all(item in res for item in expected_result)
    else:
        assert len(res) == 0


def test_pre_validate_endpoint_template_name(api_client):
    data = {"name": "test [TextValue]"}
    response = api_client.post(f"{URL}/pre-validate", json=data)
    res = response.json()
    log.info("Pre Validated Endpoint Template name: %s", res)

    assert response.status_code == 202


def test_create_endpoint_template(api_client):
    data = {
        "name": "default_name [TextValue]",
        "guidance_text": "default_guidance_text",
        "library_name": "Sponsor",
        "default_parameter_terms": [],
        "indication_uids": [dictionary_term_indication.term_uid],
        "category_uids": [ct_term_category.term_uid],
        "sub_category_uids": [ct_term_subcategory.term_uid],
    }
    response = api_client.post(URL, json=data)
    res = response.json()
    log.info("Created Endpoint Template: %s", res)

    assert response.status_code == 201
    assert res["uid"]
    assert res["name"] == "default_name [TextValue]"
    assert res["guidance_text"] == "default_guidance_text"
    assert res["parameters"][0]["name"] == "TextValue"
    assert res["parameters"][0]["terms"] is None
    assert res["indications"][0]["term_uid"] == dictionary_term_indication.term_uid
    assert (
        res["indications"][0]["dictionary_id"]
        == dictionary_term_indication.dictionary_id
    )
    assert res["indications"][0]["name"] == dictionary_term_indication.name
    assert res["categories"][0]["term_uid"] == ct_term_category.term_uid
    assert res["categories"][0]["catalogue_name"] == ct_term_category.catalogue_name
    assert res["categories"][0]["codelist_uid"] == ct_term_category.codelist_uid
    assert res["sub_categories"][0]["term_uid"] == ct_term_subcategory.term_uid
    assert (
        res["sub_categories"][0]["catalogue_name"] == ct_term_subcategory.catalogue_name
    )
    assert res["sub_categories"][0]["codelist_uid"] == ct_term_subcategory.codelist_uid
    assert res["version"] == "0.1"
    assert res["status"] == "Draft"
    assert set(list(res.keys())) == set(ENDPOINT_TEMPLATE_FIELDS_ALL)
    for key in ENDPOINT_TEMPLATE_FIELDS_NOT_NULL:
        assert res[key] is not None


def test_create_new_version_of_endpoint_template(api_client):
    data = {
        "name": "new test name",
        "guidance_text": "new test guidance text",
        "change_description": "new version",
    }
    response = api_client.post(f"{URL}/{endpoint_templates[4].uid}/versions", json=data)
    res = response.json()
    log.info("Created new version of Endpoint Template: %s", res)

    assert response.status_code == 201
    assert res["uid"]
    assert res["name"] == "new test name"
    assert res["guidance_text"] == "new test guidance text"
    assert res["indications"][0]["term_uid"] == dictionary_term_indication.term_uid
    assert (
        res["indications"][0]["dictionary_id"]
        == dictionary_term_indication.dictionary_id
    )
    assert res["indications"][0]["name"] == dictionary_term_indication.name
    assert res["categories"][0]["term_uid"] == ct_term_category.term_uid
    assert res["categories"][0]["catalogue_name"] == ct_term_category.catalogue_name
    assert res["categories"][0]["codelist_uid"] == ct_term_category.codelist_uid
    assert res["sub_categories"][0]["term_uid"] == ct_term_subcategory.term_uid
    assert (
        res["sub_categories"][0]["catalogue_name"] == ct_term_subcategory.catalogue_name
    )
    assert res["sub_categories"][0]["codelist_uid"] == ct_term_subcategory.codelist_uid
    assert res["version"] == "1.1"
    assert res["status"] == "Draft"
    assert set(list(res.keys())) == set(ENDPOINT_TEMPLATE_FIELDS_ALL)
    for key in ENDPOINT_TEMPLATE_FIELDS_NOT_NULL:
        assert res[key] is not None


def test_get_specific_version_of_endpoint_template(api_client):
    response = api_client.get(f"{URL}/{endpoint_templates[4].uid}/versions/1.1")
    res = response.json()

    assert response.status_code == 200

    assert res["uid"] == endpoint_templates[4].uid
    assert res["version"] == "1.1"
    assert res["status"] == "Draft"


def test_create_endpoint_template_with_default_parameters(api_client):
    data = {
        "name": "test_name [TextValue]",
        "guidance_text": "test_guidance_text",
        "library_name": "Sponsor",
        "default_parameter_terms": [
            {
                "position": 1,
                "conjunction": "",
                "terms": [
                    {
                        "index": 1,
                        "name": text_value_1.name,
                        "uid": text_value_1.uid,
                        "type": "TextValue",
                    }
                ],
            }
        ],
        "indication_uids": [dictionary_term_indication.term_uid],
        "category_uids": [ct_term_category.term_uid],
        "sub_category_uids": [ct_term_subcategory.term_uid],
    }
    response = api_client.post(URL, json=data)
    res = response.json()
    log.info("Created Endpoint Template with default parameter terms: %s", res)

    assert response.status_code == 201
    assert res["uid"]
    assert res["name"] == "test_name [TextValue]"
    assert res["guidance_text"] == "test_guidance_text"
    assert res["parameters"][0]["name"] == "TextValue"
    assert res["parameters"][0]["terms"] is None
    assert (
        res["default_parameter_terms"]["0"][0]["terms"][0]["name"] == text_value_1.name
    )
    assert res["default_parameter_terms"]["0"][0]["terms"][0]["uid"] == text_value_1.uid
    assert res["indications"][0]["term_uid"] == dictionary_term_indication.term_uid
    assert (
        res["indications"][0]["dictionary_id"]
        == dictionary_term_indication.dictionary_id
    )
    assert res["indications"][0]["name"] == dictionary_term_indication.name
    assert res["categories"][0]["term_uid"] == ct_term_category.term_uid
    assert res["categories"][0]["catalogue_name"] == ct_term_category.catalogue_name
    assert res["categories"][0]["codelist_uid"] == ct_term_category.codelist_uid
    assert res["sub_categories"][0]["term_uid"] == ct_term_subcategory.term_uid
    assert (
        res["sub_categories"][0]["catalogue_name"] == ct_term_subcategory.catalogue_name
    )
    assert res["sub_categories"][0]["codelist_uid"] == ct_term_subcategory.codelist_uid
    assert res["version"] == "0.1"
    assert res["status"] == "Draft"
    assert set(list(res.keys())) == set(ENDPOINT_TEMPLATE_FIELDS_ALL)
    for key in ENDPOINT_TEMPLATE_FIELDS_NOT_NULL:
        assert res[key] is not None


def test_change_endpoint_template_parameters(api_client):
    data = {
        "set_number": 0,
        "default_parameter_terms": [
            {
                "position": 1,
                "conjunction": "and",
                "terms": [
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
        ],
    }
    response = api_client.patch(
        f"{URL}/{endpoint_templates[0].uid}/default-parameter-terms",
        json=data,
    )
    res = response.json()
    log.info("Changed Endpoint Template parameters: %s", res)

    assert response.status_code == 200
    assert res["uid"]
    assert res["name"] == "Default name with [TextValue]"
    assert res["guidance_text"] == "Default guidance text"
    assert res["parameters"][0]["name"] == "TextValue"
    assert res["parameters"][0]["terms"] is None
    assert (
        res["default_parameter_terms"]["0"][0]["terms"][0]["name"] == text_value_1.name
    )
    assert res["default_parameter_terms"]["0"][0]["terms"][0]["uid"] == text_value_1.uid
    assert (
        res["default_parameter_terms"]["0"][0]["terms"][1]["name"] == text_value_2.name
    )
    assert res["default_parameter_terms"]["0"][0]["terms"][1]["uid"] == text_value_2.uid
    assert res["indications"][0]["term_uid"] == dictionary_term_indication.term_uid
    assert (
        res["indications"][0]["dictionary_id"]
        == dictionary_term_indication.dictionary_id
    )
    assert res["indications"][0]["name"] == dictionary_term_indication.name
    assert res["categories"][0]["term_uid"] == ct_term_category.term_uid
    assert res["categories"][0]["catalogue_name"] == ct_term_category.catalogue_name
    assert res["categories"][0]["codelist_uid"] == ct_term_category.codelist_uid
    assert res["sub_categories"][0]["term_uid"] == ct_term_subcategory.term_uid
    assert (
        res["sub_categories"][0]["catalogue_name"] == ct_term_subcategory.catalogue_name
    )
    assert res["sub_categories"][0]["codelist_uid"] == ct_term_subcategory.codelist_uid
    assert res["version"] == "1.0"
    assert res["status"] == "Final"
    assert set(list(res.keys())) == set(ENDPOINT_TEMPLATE_FIELDS_ALL)
    for key in ENDPOINT_TEMPLATE_FIELDS_NOT_NULL:
        assert res[key] is not None


def test_change_endpoint_template_indexings(api_client):
    indication = TestUtils.create_dictionary_term(
        codelist_uid=indications_codelist.codelist_uid,
        library_name=indications_library_name,
    )
    subcategory = TestUtils.create_ct_term()
    category = TestUtils.create_ct_term()

    data = {
        "indication_uids": [indication.term_uid],
        "sub_category_uids": [
            ct_term_subcategory.term_uid,
            subcategory.term_uid,
        ],
        "category_uids": [
            ct_term_category.term_uid,
            category.term_uid,
        ],
    }
    response = api_client.patch(
        f"{URL}/{endpoint_templates[1].uid}/indexings",
        json=data,
    )
    res = response.json()
    log.info("Changed Endpoint Template indexings: %s", res)

    assert response.status_code == 200
    assert res["uid"]
    assert res["name"] == "Default-AAA name with [TextValue]"
    assert res["guidance_text"] == "Default-AAA guidance text"
    assert res["indications"][0]["term_uid"] == indication.term_uid
    assert res["indications"][0]["dictionary_id"] == indication.dictionary_id
    assert res["indications"][0]["name"] == indication.name
    assert res["sub_categories"][0]["term_uid"] == ct_term_subcategory.term_uid
    assert (
        res["sub_categories"][0]["catalogue_name"] == ct_term_subcategory.catalogue_name
    )
    assert res["sub_categories"][0]["codelist_uid"] == ct_term_subcategory.codelist_uid
    assert res["sub_categories"][1]["term_uid"] == subcategory.term_uid
    assert res["sub_categories"][1]["catalogue_name"] == subcategory.catalogue_name
    assert res["sub_categories"][1]["codelist_uid"] == subcategory.codelist_uid
    assert res["categories"][0]["term_uid"] == ct_term_category.term_uid
    assert res["categories"][0]["catalogue_name"] == ct_term_category.catalogue_name
    assert res["categories"][0]["codelist_uid"] == ct_term_category.codelist_uid
    assert res["categories"][1]["term_uid"] == category.term_uid
    assert res["categories"][1]["catalogue_name"] == category.catalogue_name
    assert res["categories"][1]["codelist_uid"] == category.codelist_uid
    assert res["version"] == "1.0"
    assert res["status"] == "Final"
    assert set(list(res.keys())) == set(ENDPOINT_TEMPLATE_FIELDS_ALL)
    for key in ENDPOINT_TEMPLATE_FIELDS_NOT_NULL:
        assert res[key] is not None


def test_delete_endpoint_template(api_client):
    response = api_client.delete(f"{URL}/{endpoint_templates[2].uid}")
    log.info("Deleted Endpoint Template: %s", endpoint_templates[2].uid)

    assert response.status_code == 204


def test_approve_endpoint_template(api_client):
    response = api_client.post(f"{URL}/{endpoint_templates[3].uid}/approvals")
    res = response.json()

    assert response.status_code == 201
    assert res["uid"] == endpoint_templates[3].uid
    assert res["version"] == "1.0"
    assert res["status"] == "Final"


def test_inactivate_endpoint_template(api_client):
    response = api_client.delete(f"{URL}/{endpoint_templates[3].uid}/activations")
    res = response.json()

    assert response.status_code == 200
    assert res["uid"] == endpoint_templates[3].uid
    assert res["version"] == "1.0"
    assert res["status"] == "Retired"


def test_reactivate_endpoint_template(api_client):
    response = api_client.post(f"{URL}/{endpoint_templates[3].uid}/activations")
    res = response.json()

    assert response.status_code == 200
    assert res["uid"] == endpoint_templates[3].uid
    assert res["version"] == "1.0"
    assert res["status"] == "Final"


def test_create_pre_instance_endpoint_template(api_client):
    data = {
        "library_name": "Sponsor",
        "parameter_terms": [
            {
                "position": 1,
                "conjunction": "",
                "terms": [
                    {
                        "index": 1,
                        "name": text_value_1.name_sentence_case,
                        "uid": text_value_1.uid,
                        "type": "TextValue",
                    }
                ],
            }
        ],
        "indication_uids": [dictionary_term_indication.term_uid],
        "category_uids": [ct_term_category.term_uid],
        "sub_category_uids": [ct_term_subcategory.term_uid],
    }
    response = api_client.post(
        f"{URL}/{endpoint_templates[0].uid}/pre-instances", json=data
    )
    res = response.json()
    log.info("Created Endpoint Pre Instance: %s", res)

    assert response.status_code == 201
    assert "PreInstance" in res["uid"]
    assert res["template_uid"] == endpoint_templates[0].uid
    assert res["name"] == f"Default name with [{text_value_1.name_sentence_case}]"
    assert (
        res["parameter_terms"][0]["position"] == data["parameter_terms"][0]["position"]
    )
    assert (
        res["parameter_terms"][0]["conjunction"]
        == data["parameter_terms"][0]["conjunction"]
    )
    assert res["parameter_terms"][0]["terms"] == data["parameter_terms"][0]["terms"]
    assert res["indications"][0]["term_uid"] == dictionary_term_indication.term_uid
    assert (
        res["indications"][0]["dictionary_id"]
        == dictionary_term_indication.dictionary_id
    )
    assert res["indications"][0]["name"] == dictionary_term_indication.name
    assert res["categories"][0]["term_uid"] == ct_term_category.term_uid
    assert res["categories"][0]["catalogue_name"] == ct_term_category.catalogue_name
    assert res["categories"][0]["codelist_uid"] == ct_term_category.codelist_uid
    assert res["sub_categories"][0]["term_uid"] == ct_term_subcategory.term_uid
    assert (
        res["sub_categories"][0]["catalogue_name"] == ct_term_subcategory.catalogue_name
    )
    assert res["sub_categories"][0]["codelist_uid"] == ct_term_subcategory.codelist_uid
    assert res["version"] == "0.1"
    assert res["status"] == "Draft"


def test_cannot_create_endpoint_template_with_existing_name(api_client):
    data = {
        "name": "Default name with [TextValue]",
        "guidance_text": "default_guidance_text",
        "library_name": "Sponsor",
        "default_parameter_terms": [],
        "indication_uids": [dictionary_term_indication.term_uid],
        "category_uids": [ct_term_category.term_uid],
        "sub_category_uids": [ct_term_subcategory.term_uid],
    }
    response = api_client.post(URL, json=data)
    res = response.json()
    log.info("Didn't Create Endpoint Template: %s", res)

    assert response.status_code == 400
    assert (
        res["message"]
        == f"Duplicate templates not allowed - template exists: {data['name']}"
    )


def test_cannot_update_endpoint_template_to_an_existing_name(api_client):
    data = {
        "name": "Default name with [TextValue]",
        "change_description": "Change for duplicate",
    }
    response = api_client.patch(f"{URL}/{endpoint_templates[1].uid}", json=data)
    res = response.json()
    log.info("Didn't Update Endpoint Template: %s", res)

    assert response.status_code == 500
    assert (
        res["message"]
        == f"Duplicate templates not allowed - template exists: {data['name']}"
    )


def test_cannot_update_endpoint_template_without_change_description(api_client):
    data = {"name": "Default name with [TextValue]"}
    response = api_client.patch(f"{URL}/{endpoint_templates[1].uid}", json=data)
    res = response.json()
    log.info("Didn't Update Endpoint Template: %s", res)

    assert response.status_code == 422
    assert res["detail"] == [
        {
            "loc": ["body", "change_description"],
            "msg": "field required",
            "type": "value_error.missing",
        }
    ]


def test_cannot_update_endpoint_template_in_final_status(api_client):
    data = {
        "name": "test name [TextValue]",
        "change_description": "Change for final status",
    }
    response = api_client.patch(f"{URL}/{endpoint_templates[1].uid}", json=data)
    res = response.json()
    log.info("Didn't Update Endpoint Template: %s", res)

    assert response.status_code == 400
    assert res["message"] == "The object is not in draft status."


def test_cannot_change_parameter_numbers_of_endpoint_template_after_approval(
    api_client,
):
    data = {
        "name": "Default name with",
        "change_description": "Change for parameter numbers",
    }
    response = api_client.patch(f"{URL}/{endpoint_templates[1].uid}", json=data)
    res = response.json()
    log.info("Didn't Change Endpoint Template parameter numbers: %s", res)

    assert response.status_code == 400
    assert (
        res["message"]
        == "You cannot change number or order of template parameters for a previously approved template."
    )


def test_pre_validate_invalid_endpoint_template_name(api_client):
    data = {"name": "Missing opening bracket ]"}
    response = api_client.post(f"{URL}/pre-validate", json=data)
    res = response.json()
    log.info("Pre Validated Endpoint Temaplate name: %s", res)

    assert response.status_code == 400
    assert res["message"] == f"Template string syntax incorrect: {data['name']}"

    data = {"name": "Lacking closing bracket ["}
    response = api_client.post(f"{URL}/pre-validate", json=data)
    res = response.json()
    log.info("Pre Validated Endpoint Template name: %s", res)

    assert response.status_code == 400
    assert res["message"] == f"Template string syntax incorrect: {data['name']}"

    data = {"name": " "}
    response = api_client.post(f"{URL}/pre-validate", json=data)
    res = response.json()
    log.info("Pre Validated Endpoint Template name: %s", res)

    assert response.status_code == 400
    assert res["message"] == f"Template string syntax incorrect: {data['name']}"


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
def test_get_endpoint_templates_csv_xml_excel(api_client, export_format):
    TestUtils.verify_exported_data_format(api_client, export_format, URL)
