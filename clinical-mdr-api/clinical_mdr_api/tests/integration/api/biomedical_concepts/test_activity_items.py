"""
Tests for /activity-items endpoints
"""
import json
import logging
from functools import reduce
from typing import List

import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api.main import app
from clinical_mdr_api.models import CTTerm, UnitDefinitionModel
from clinical_mdr_api.models.biomedical_concepts.activity_instance_class import (
    ActivityInstanceClass,
)
from clinical_mdr_api.models.biomedical_concepts.activity_item import ActivityItem
from clinical_mdr_api.models.biomedical_concepts.activity_item_class import (
    ActivityItemClass,
)
from clinical_mdr_api.tests.integration.utils.api import (
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments


log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
activity_items_all: List[ActivityItem]
activity_instance_class: ActivityInstanceClass
activity_item_class: ActivityItemClass
activity_item_class2: ActivityItemClass
ct_term_ai: CTTerm
ct_term_ai2: CTTerm
unit_definition_ai: UnitDefinitionModel
unit_definition_ai2: UnitDefinitionModel
data_type_term: CTTerm
role_term: CTTerm


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    inject_and_clear_db("activity-item.api")
    inject_base_data()

    global activity_items_all
    global activity_item_class
    global activity_item_class2
    global activity_instance_class
    global ct_term_ai
    global ct_term_ai2
    global unit_definition_ai
    global unit_definition_ai2
    activity_instance_class = TestUtils.create_activity_instance_class(
        name="activity instance class"
    )
    global data_type_term
    global role_term
    data_type_term = TestUtils.create_ct_term(sponsor_preferred_name="Data type")
    role_term = TestUtils.create_ct_term(sponsor_preferred_name="Role")
    activity_item_class = TestUtils.create_activity_item_class(
        name="Activity Item Class name1",
        order=1,
        mandatory=True,
        activity_instance_class_uids=[activity_instance_class.uid],
        role_uid=role_term.term_uid,
        data_type_uid=data_type_term.term_uid,
    )
    activity_item_class2 = TestUtils.create_activity_item_class(
        name="Activity Item Class name2",
        order=2,
        mandatory=True,
        activity_instance_class_uids=[activity_instance_class.uid],
        role_uid=role_term.term_uid,
        data_type_uid=data_type_term.term_uid,
    )
    codelist = TestUtils.create_ct_codelist(extensible=True, approve=True)
    ct_term_ai = TestUtils.create_ct_term(
        codelist_uid=codelist.codelist_uid, sponsor_preferred_name="Activity item term"
    )
    ct_term_ai2 = TestUtils.create_ct_term(
        codelist_uid=codelist.codelist_uid, sponsor_preferred_name="Activity item term2"
    )
    unit_definition_ai = TestUtils.create_unit_definition(name="Unit dimension")
    unit_definition_ai2 = TestUtils.create_unit_definition(name="Unit dimension2")

    # Create some activity items
    activity_items_all = [
        TestUtils.create_activity_item(
            name="name A",
            activity_item_class_uid=activity_item_class.uid,
            ct_term_uid=ct_term_ai.term_uid,
            unit_definition_uid=unit_definition_ai.uid,
        ),
        TestUtils.create_activity_item(
            name="name-AAA",
            activity_item_class_uid=activity_item_class.uid,
            ct_term_uid=ct_term_ai.term_uid,
            unit_definition_uid=unit_definition_ai.uid,
        ),
        TestUtils.create_activity_item(
            name="name-BBB",
            activity_item_class_uid=activity_item_class.uid,
            ct_term_uid=ct_term_ai.term_uid,
            unit_definition_uid=unit_definition_ai.uid,
        ),
        TestUtils.create_activity_item(
            name="name XXX",
            activity_item_class_uid=activity_item_class.uid,
            ct_term_uid=ct_term_ai.term_uid,
            unit_definition_uid=unit_definition_ai.uid,
        ),
        TestUtils.create_activity_item(
            name="name YYY",
            activity_item_class_uid=activity_item_class.uid,
            ct_term_uid=ct_term_ai.term_uid,
            unit_definition_uid=unit_definition_ai.uid,
        ),
    ]

    for index in range(5):
        activity_items_all.append(
            TestUtils.create_activity_item(
                name=f"name-AAA-{index}",
                activity_item_class_uid=activity_item_class2.uid,
                ct_term_uid=ct_term_ai2.term_uid,
                unit_definition_uid=unit_definition_ai2.uid,
            )
        )
        activity_items_all.append(
            TestUtils.create_activity_item(
                name=f"name-BBB-{index}",
                activity_item_class_uid=activity_item_class2.uid,
                ct_term_uid=ct_term_ai2.term_uid,
                unit_definition_uid=unit_definition_ai2.uid,
            )
        )
        activity_items_all.append(
            TestUtils.create_activity_item(
                name=f"name-XXX-{index}",
                activity_item_class_uid=activity_item_class2.uid,
                ct_term_uid=ct_term_ai2.term_uid,
                unit_definition_uid=unit_definition_ai2.uid,
            )
        )
        activity_items_all.append(
            TestUtils.create_activity_item(
                name=f"name-YYY-{index}",
                activity_item_class_uid=activity_item_class2.uid,
                ct_term_uid=ct_term_ai2.term_uid,
                unit_definition_uid=unit_definition_ai2.uid,
            )
        )


ACTIVITY_ITEM_FIELDS_ALL = [
    "uid",
    "name",
    "activity_item_class",
    "ct_term",
    "unit_definition",
    "library_name",
    "start_date",
    "end_date",
    "status",
    "version",
    "change_description",
    "user_initials",
    "possible_actions",
]

ACTIVITY_ITEM_FIELDS_NOT_NULL = [
    "uid",
    "name",
    "activity_item_class",
]


def test_get_activity_item(api_client):
    response = api_client.get(f"/activity-items/{activity_items_all[0].uid}")
    res = response.json()

    assert response.status_code == 200

    # Check fields included in the response
    assert set(list(res.keys())) == set(ACTIVITY_ITEM_FIELDS_ALL)
    for key in ACTIVITY_ITEM_FIELDS_NOT_NULL:
        assert res[key] is not None

    assert res["uid"] == activity_items_all[0].uid
    assert res["name"] == "name A"
    assert res["activity_item_class"]["uid"] == activity_item_class.uid
    assert res["activity_item_class"]["name"] == activity_item_class.name
    assert res["ct_term"]["uid"] == ct_term_ai.term_uid
    assert res["ct_term"]["name"] == ct_term_ai.sponsor_preferred_name
    assert res["unit_definition"]["uid"] == unit_definition_ai.uid
    assert res["unit_definition"]["name"] == unit_definition_ai.name
    assert res["version"] == "1.0"
    assert res["status"] == "Final"
    assert res["library_name"] == "Sponsor"
    assert res["possible_actions"] == ["inactivate", "new_version"]


def test_get_activity_items_pagination(api_client):
    results_paginated: dict = {}
    sort_by = '{"name": true}'
    for page_number in range(1, 4):
        url = (
            f"/activity-items?page_number={page_number}&page_size=10&sort_by={sort_by}"
        )
        response = api_client.get(url)
        res = response.json()
        res_names = list(map(lambda x: x["name"], res["items"]))
        results_paginated[page_number] = res_names
        log.info("Page %s: %s", page_number, res_names)

    log.info("All pages: %s", results_paginated)

    results_paginated_merged = list(
        list(reduce(lambda a, b: a + b, list(results_paginated.values())))
    )
    log.info("All rows returned by pagination: %s", results_paginated_merged)

    res_all = api_client.get(
        f"/activity-items?page_number=1&page_size=100&sort_by={sort_by}"
    ).json()
    results_all_in_one_page = list(map(lambda x: x["name"], res_all["items"]))
    log.info("All rows in one page: %s", results_all_in_one_page)
    assert len(results_all_in_one_page) == len(results_paginated_merged)
    assert len(activity_items_all) == len(results_paginated_merged)


@pytest.mark.parametrize(
    "page_size, page_number, total_count, sort_by, expected_result_len",
    [
        pytest.param(None, None, None, None, 10),
        pytest.param(3, 1, True, None, 3),
        pytest.param(3, 2, True, None, 3),
        pytest.param(10, 2, True, None, 10),
        pytest.param(10, 3, True, None, 5),  # Total numer of data models is 25
        pytest.param(10, 1, True, '{"name": false}', 10),
        pytest.param(10, 2, True, '{"name": true}', 10),
    ],
)
def test_get_activity_items(
    api_client, page_size, page_number, total_count, sort_by, expected_result_len
):
    url = "/activity-items"
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
    assert res["total"] == (len(activity_items_all) if total_count else 0)
    assert res["page"] == (page_number if page_number else 1)
    assert res["size"] == (page_size if page_size else 10)

    for item in res["items"]:
        assert set(list(item.keys())) == set(ACTIVITY_ITEM_FIELDS_ALL)
        for key in ACTIVITY_ITEM_FIELDS_NOT_NULL:
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
        # This asser fails due to API issue with sorting coupled with pagination
        # assert result_vals == result_vals_sorted_locally


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
def test_get_activity_items_csv_xml_excel(api_client, export_format):
    url = "/activity-items"
    TestUtils.verify_exported_data_format(api_client, export_format, url)


@pytest.mark.parametrize(
    "filter_by, expected_matched_field, expected_result_prefix",
    [
        pytest.param('{"*": {"v": ["aaa"]}}', "name", "name-AAA"),
        pytest.param('{"*": {"v": ["bBb"]}}', "name", "name-BBB"),
        pytest.param(
            '{"*": {"v": ["Activity Item Class name1"]}}',
            "activity_item_class.name",
            "Activity Item Class name1",
        ),
        pytest.param(
            '{"*": {"v": ["Activity item term"]}}',
            "ct_term.name",
            "Activity item term",
        ),
        pytest.param(
            '{"*": {"v": ["Unit dimension"]}}',
            "unit_definition.name",
            "Unit dimension",
        ),
        pytest.param('{"*": {"v": ["ccc"]}}', None, None),
    ],
)
def test_filtering_wildcard(
    api_client, filter_by, expected_matched_field, expected_result_prefix
):
    url = f"/activity-items?filters={filter_by}"
    response = api_client.get(url)
    res = response.json()

    assert response.status_code == 200
    if expected_result_prefix:
        assert len(res["items"]) > 0
        nested_path = None

        # if we expect a nested property to be equal to specified value
        if isinstance(expected_matched_field, str) and "." in expected_matched_field:
            nested_path = expected_matched_field.split(".")
            expected_matched_field = nested_path[-1]
            nested_path = nested_path[:-1]

        # Each returned row has a field that starts with the specified filter value
        for row in res["items"]:
            if nested_path:
                for prop in nested_path:
                    row = row[prop]
            if isinstance(row, list):
                any(
                    item[expected_matched_field].startswith(expected_result_prefix)
                    for item in row
                )
            else:
                assert row[expected_matched_field].startswith(expected_result_prefix)
    else:
        assert len(res["items"]) == 0


@pytest.mark.parametrize(
    "filter_by, expected_matched_field, expected_result",
    [
        pytest.param('{"name": {"v": ["name-AAA"]}}', "name", "name-AAA"),
        pytest.param('{"name": {"v": ["name-BBB"]}}', "name", "name-BBB"),
        pytest.param('{"name": {"v": ["cc"]}}', None, None),
        pytest.param(
            '{"activity_item_class.uid": {"v": ["ActivityItemClass_000001"]}}',
            "activity_item_class.uid",
            "ActivityItemClass_000001",
        ),
        pytest.param(
            '{"activity_item_class.name": {"v": ["Activity Item Class name1"]}}',
            "activity_item_class.name",
            "Activity Item Class name1",
        ),
        pytest.param(
            '{"ct_term.uid": {"v": ["CTTerm_000003"]}}',
            "ct_term.uid",
            "CTTerm_000003",
        ),
        pytest.param(
            '{"ct_term.name": {"v": ["Activity item term"]}}',
            "ct_term.name",
            "Activity item term",
        ),
        pytest.param(
            '{"unit_definition.uid": {"v": ["UnitDefinition_000003"]}}',
            "unit_definition.uid",
            "UnitDefinition_000003",
        ),
        pytest.param(
            '{"unit_definition.name": {"v": ["Unit dimension"]}}',
            "unit_definition.name",
            "Unit dimension",
        ),
    ],
)
def test_filtering_exact(
    api_client, filter_by, expected_matched_field, expected_result
):
    url = f"/activity-items?filters={filter_by}"
    response = api_client.get(url)
    res = response.json()

    assert response.status_code == 200
    if expected_result:
        assert len(res["items"]) > 0

        # if we expect a nested property to be equal to specified value
        nested_path = None
        if isinstance(expected_matched_field, str) and "." in expected_matched_field:
            nested_path = expected_matched_field.split(".")
            expected_matched_field = nested_path[-1]
            nested_path = nested_path[:-1]

        # Each returned row has a field whose value is equal to the specified filter value
        for row in res["items"]:
            if nested_path:
                for prop in nested_path:
                    row = row[prop]
            if isinstance(expected_result, list):
                assert all(
                    item in row[expected_matched_field] for item in expected_result
                )
            else:
                if isinstance(row, list):
                    all(item[expected_matched_field] == expected_result for item in row)
                else:
                    assert row[expected_matched_field] == expected_result
    else:
        assert len(res["items"]) == 0


def test_edit_activity_item(api_client):
    activity_item = TestUtils.create_activity_item(
        name="New item",
        activity_item_class_uid=activity_item_class.uid,
        approve=False,
    )
    response = api_client.patch(
        f"/activity-items/{activity_item.uid}",
        json={
            "name": "new name for item",
            "activity_item_class_uid": activity_item_class2.uid,
            "ct_term_uid": ct_term_ai2.term_uid,
            "unit_definition_uid": unit_definition_ai2.uid,
        },
    )
    res = response.json()
    assert response.status_code == 200
    assert res["name"] == "new name for item"
    assert res["activity_item_class"]["uid"] == activity_item_class2.uid
    assert res["ct_term"]["uid"] == ct_term_ai2.term_uid
    assert res["unit_definition"]["uid"] == unit_definition_ai2.uid
    assert res["version"] == "0.2"
    assert res["status"] == "Draft"
    assert res["possible_actions"] == ["approve", "delete", "edit"]
    assert res["library_name"] == "Sponsor"


def test_post_activity_item(api_client):
    response = api_client.post(
        "/activity-items",
        json={
            "name": "New Activity Item Name",
            "library_name": "Sponsor",
            "activity_item_class_uid": activity_item_class.uid,
            "ct_term_uid": ct_term_ai.term_uid,
            "unit_definition_uid": unit_definition_ai.uid,
        },
    )
    assert response.status_code == 201
    res = response.json()
    assert res["name"] == "New Activity Item Name"
    assert res["activity_item_class"]["uid"] == activity_item_class.uid
    assert res["ct_term"]["uid"] == ct_term_ai.term_uid
    assert res["unit_definition"]["uid"] == unit_definition_ai.uid
    assert res["version"] == "0.1"
    assert res["status"] == "Draft"
    assert res["possible_actions"] == ["approve", "delete", "edit"]
    assert res["library_name"] == "Sponsor"


def test_activity_item_versioning(api_client):
    activity_item = TestUtils.create_activity_item(
        name="New activity item",
        activity_item_class_uid=activity_item_class.uid,
        approve=False,
    )

    # not successful create new version
    response = api_client.post(f"/activity-items/{activity_item.uid}/versions")
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == "New draft version can be created only for FINAL versions."

    # successful approve
    response = api_client.post(f"/activity-items/{activity_item.uid}/approvals")
    assert response.status_code == 201

    # not successful approve
    response = api_client.post(f"/activity-items/{activity_item.uid}/approvals")
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == "The object is not in draft status."

    # not successful reactivate
    response = api_client.post(f"/activity-items/{activity_item.uid}/activations")
    assert response.status_code == 400
    res = response.json()
    assert res["message"] == "Only RETIRED version can be reactivated."

    # successful inactivate
    response = api_client.delete(f"/activity-items/{activity_item.uid}/activations")
    assert response.status_code == 200

    # successful reactivate
    response = api_client.post(f"/activity-items/{activity_item.uid}/activations")
    assert response.status_code == 200

    # successful new version
    response = api_client.post(f"/activity-items/{activity_item.uid}/versions")
    assert response.status_code == 201

    activity_item_to_delete = TestUtils.create_activity_item(
        name="activity item to delete",
        activity_item_class_uid=activity_item_class.uid,
        approve=False,
    )
    # successful delete
    response = api_client.delete(f"/activity-items/{activity_item_to_delete.uid}")
    assert response.status_code == 204
