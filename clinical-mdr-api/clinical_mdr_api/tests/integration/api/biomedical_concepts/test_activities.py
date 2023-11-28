"""
Tests for /concepts/activities/activities endpoints
"""
import logging
from operator import itemgetter

import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api.main import app
from clinical_mdr_api.models import Activity
from clinical_mdr_api.models.concepts.activities.activity_group import ActivityGroup
from clinical_mdr_api.models.concepts.activities.activity_sub_group import (
    ActivitySubGroup,
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
activity_group: ActivityGroup
activity_subgroup: ActivitySubGroup
activities_all: list[Activity]


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "activities.api"
    inject_and_clear_db(db_name)
    inject_base_data()

    global activity_group
    activity_group = TestUtils.create_activity_group(name="activity_group")

    global activity_subgroup
    activity_subgroup = TestUtils.create_activity_subgroup(
        name="activity_subgroup", activity_groups=[activity_group.uid]
    )
    global activities_all
    activities_all = [
        TestUtils.create_activity(
            name="name-AAA",
            activity_subgroups=[activity_subgroup.uid],
            activity_groups=[activity_group.uid],
        ),
        TestUtils.create_activity(
            name="name-BBB",
            activity_subgroups=[activity_subgroup.uid],
            activity_groups=[activity_group.uid],
        ),
    ]

    for index in range(5):
        activities_all.append(
            TestUtils.create_activity(
                name=f"Activity-{index}",
                activity_subgroups=[activity_subgroup.uid],
                activity_groups=[activity_group.uid],
            )
        )

    yield


ACTIVITY_FIELDS_ALL = [
    "uid",
    "nci_concept_id",
    "name",
    "name_sentence_case",
    "definition",
    "abbreviation",
    "activity_groupings",
    "request_rationale",
    "replaced_by_activity",
    "is_data_collected",
    "library_name",
    "start_date",
    "end_date",
    "status",
    "version",
    "change_description",
    "user_initials",
    "possible_actions",
]

ACTIVITY_FIELDS_NOT_NULL = ["uid", "name", "activity_groupings", "start_date"]


def test_get_activity(api_client):
    response = api_client.get(
        f"/concepts/activities/activities/{activities_all[0].uid}"
    )
    res = response.json()

    assert response.status_code == 200

    # Check fields included in the response
    assert set(list(res.keys())) == set(ACTIVITY_FIELDS_ALL)
    for key in ACTIVITY_FIELDS_NOT_NULL:
        assert res[key] is not None

    assert res["uid"] == activities_all[0].uid
    assert res["name"] == "name-AAA"
    assert res["name_sentence_case"] == "name-AAA"
    assert len(res["activity_groupings"]) == 1
    assert res["activity_groupings"][0]["activity_group_uid"] == activity_group.uid
    assert res["activity_groupings"][0]["activity_group_name"] == activity_group.name
    assert (
        res["activity_groupings"][0]["activity_subgroup_uid"] == activity_subgroup.uid
    )
    assert (
        res["activity_groupings"][0]["activity_subgroup_name"] == activity_subgroup.name
    )

    assert res["library_name"] == "Sponsor"
    assert res["definition"] is None
    assert res["version"] == "1.0"
    assert res["status"] == "Final"
    assert res["possible_actions"] == ["inactivate", "new_version"]


def test_get_activity_versions(api_client):
    # Create a new version of an activity
    response = api_client.post(
        f"/concepts/activities/activities/{activities_all[0].uid}/versions"
    )
    assert response.status_code == 201

    # Get all versions of all activities
    response = api_client.get("/concepts/activities/activities/versions?page_size=100")
    res = response.json()

    assert response.status_code == 200

    # Check fields included in the response
    assert set(list(res.keys())) == set(["items", "total", "page", "size"])

    assert len(res["items"]) == len(activities_all) * 2 + 1
    for item in res["items"]:
        assert set(list(item.keys())) == set(ACTIVITY_FIELDS_ALL)
        for key in ACTIVITY_FIELDS_NOT_NULL:
            assert item[key] is not None

    # Check that the items are sorted by start_date descending
    sorted_items = sorted(res["items"], key=itemgetter("start_date"), reverse=True)
    assert sorted_items == res["items"]


@pytest.mark.parametrize(
    "filter_by, expected_matched_field, expected_result_prefix",
    [
        pytest.param('{"*": {"v": ["aaa"]}}', "name", "name-AAA"),
        pytest.param('{"*": {"v": ["bBb"]}}', "name", "name-BBB"),
        pytest.param('{"*": {"v": ["ccc"]}}', None, None),
        pytest.param('{"*": {"v": ["Final"]}}', "status", "Final"),
        pytest.param('{"*": {"v": ["1.0"]}}', "version", "1.0"),
    ],
)
def test_filtering_versions_wildcard(
    api_client, filter_by, expected_matched_field, expected_result_prefix
):
    url = f"/concepts/activities/activities/versions?filters={filter_by}"
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
            '{"name_sentence_case": {"v": ["name-AAA"]}}',
            "name_sentence_case",
            "name-AAA",
        ),
        pytest.param(
            '{"name_sentence_case": {"v": ["name-BBB"]}}',
            "name_sentence_case",
            "name-BBB",
        ),
        pytest.param('{"name_sentence_case": {"v": ["cc"]}}', None, None),
    ],
)
def test_filtering_versions_exact(
    api_client, filter_by, expected_matched_field, expected_result
):
    url = f"/concepts/activities/activities/versions?filters={filter_by}"
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


def test_create_activity_unique_name_validation(api_client):
    activity_name = TestUtils.random_str(20, "ActivityName-")
    activity_name2 = TestUtils.random_str(20, "ActivityName-")
    TestUtils.create_activity(
        name=activity_name,
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        approve=False,
    )
    TestUtils.create_activity(
        name=activity_name2,
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        approve=True,
    )

    # Create activity with the same name as the first one
    response = api_client.post(
        "/concepts/activities/activities",
        json={
            "name": activity_name,
            "name_sentence_case": activity_name,
            "activity_groupings": [
                {
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                }
            ],
            "library_name": "Sponsor",
        },
    )
    assert response.status_code == 400
    assert (
        response.json()["message"]
        == f"Activity with ['name: {activity_name}'] already exists."
    )

    # Create activity with the same name as the second one
    response = api_client.post(
        "/concepts/activities/activities",
        json={
            "name": activity_name2,
            "name_sentence_case": activity_name2,
            "activity_groupings": [
                {
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                }
            ],
            "library_name": "Sponsor",
        },
    )
    assert response.status_code == 400
    assert (
        response.json()["message"]
        == f"Activity with ['name: {activity_name2}'] already exists."
    )
