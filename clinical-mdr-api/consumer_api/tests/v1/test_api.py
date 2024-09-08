# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments
import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api.tests.integration.utils.api import inject_base_data
from clinical_mdr_api.tests.integration.utils.utils import TestUtils
from consumer_api.consumer_api import app
from consumer_api.shared import config
from consumer_api.tests.utils import set_db
from consumer_api.v1 import models

BASE_URL = "/v1"


STUDY_FIELDS_ALL = [
    "uid",
    "id",
    "id_prefix",
    "number",
    "acronym",
]

STUDY_FIELDS_NOT_NULL = [
    "uid",
    "id",
    "id_prefix",
]

# Global variables shared between fixtures and tests
rand: str
studies: list[models.Study]
total_studies: int = 25


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "consumer-api-v1"
    set_db(db_name)
    study = inject_base_data()

    global rand
    global studies

    studies = [study]
    for _idx in range(1, total_studies):
        rand = TestUtils.random_str(4)
        studies.append(TestUtils.create_study(acronym=f"ACR-{rand}"))


def test_get_studies(api_client):
    response = api_client.get(f"{BASE_URL}/studies")
    assert response.status_code == 200
    res = response.json()

    assert res.keys() == {"self", "prev", "next", "items"}

    for item in res["items"]:
        TestUtils.assert_response_shape_ok(
            item, STUDY_FIELDS_ALL, STUDY_FIELDS_NOT_NULL
        )

    # Default page size is 10
    for idx, study in enumerate(studies):
        if idx < 10:
            assert any(
                item["uid"] == study.uid for item in res["items"]
            ), f"Study {study.uid} not found in response"


def test_get_studies_pagination_sorting(api_client):
    page_size_default = 10

    # Default page size
    response = api_client.get(f"{BASE_URL}/studies")
    assert response.status_code == 200
    res = response.json()
    assert res.keys() == {"self", "next", "prev", "items"}
    assert len(res["items"]) == page_size_default
    TestUtils.assert_sort_order(res["items"], "uid", False)

    # Non-default page size
    response = api_client.get(f"{BASE_URL}/studies?page_size=2")
    assert response.status_code == 200
    res = response.json()
    assert res.keys() == {"self", "next", "prev", "items"}
    assert len(res["items"]) == 2
    TestUtils.assert_sort_order(res["items"], "uid", False)

    # Non-default page size
    response = api_client.get(f"{BASE_URL}/studies?page_size=100")
    assert response.status_code == 200
    res = response.json()
    assert res.keys() == {"self", "next", "prev", "items"}
    assert len(res["items"]) == total_studies
    TestUtils.assert_sort_order(res["items"], "uid", False)

    # Non-default page number and page size
    response = api_client.get(f"{BASE_URL}/studies?page_size=3&page_number=2")
    assert response.status_code == 200
    res = response.json()
    assert res.keys() == {"self", "next", "prev", "items"}
    assert len(res["items"]) == 3
    TestUtils.assert_sort_order(res["items"], "uid", False)

    # Non-default sort_by
    response = api_client.get(f"{BASE_URL}/studies?page_size=10&sort_by=id_prefix")
    assert response.status_code == 200
    res = response.json()
    assert res.keys() == {"self", "prev", "next", "items"}
    assert len(res["items"]) == 10
    TestUtils.assert_sort_order(res["items"], "id_prefix", False)

    # Non-default sort_by and sort_order
    response = api_client.get(f"{BASE_URL}/studies?sort_order=desc&&sort_by=id_prefix")
    assert response.status_code == 200
    res = response.json()
    assert res.keys() == {"self", "next", "prev", "items"}
    assert len(res["items"]) == page_size_default
    TestUtils.assert_sort_order(res["items"], "id_prefix", True)


@pytest.mark.parametrize("page_size", [8, 20, 100])
def test_get_all_studies(api_client, page_size):
    all_fetched_studies = []

    response = api_client.get(f"{BASE_URL}/studies?page_size={page_size}")
    all_fetched_studies.extend(response.json()["items"])

    while response.json()["items"]:
        # Fetch the next page until no items are returned
        response = api_client.get(response.json()["next"])
        all_fetched_studies.extend(response.json()["items"])

    assert len(all_fetched_studies) == total_studies
    assert {study["uid"] for study in all_fetched_studies} == {
        study.uid for study in studies
    }

    TestUtils.assert_sort_order(all_fetched_studies, "uid", False)


def test_get_studies_filtering(api_client):
    # Find a study
    response = api_client.get(f"{BASE_URL}/studies")
    study_x = response.json()["items"][3]

    # Filter by existing id (full match)
    filter_by_id = study_x["id"]
    response = api_client.get(f"{BASE_URL}/studies?id={filter_by_id}")
    assert response.status_code == 200
    res = response.json()
    assert res.keys() == {"self", "prev", "next", "items"}
    assert len(res["items"]) == 1
    assert res["items"][0]["uid"] == study_x["uid"]
    for key in ["self", "prev", "next"]:
        assert f"id={filter_by_id}&" in res[key]

    # Filter by existing id (partial match)
    filter_by_id = study_x["id"][:3]
    response = api_client.get(f"{BASE_URL}/studies?id={filter_by_id}")
    assert response.status_code == 200
    res = response.json()
    assert res.keys() == {"self", "prev", "next", "items"}
    assert len(res["items"]) >= 1
    for item in res["items"]:
        assert filter_by_id in item["id"]
    for key in ["self", "prev", "next"]:
        assert f"id={filter_by_id}&" in res[key]

    # Filter by non-existing id
    filter_by_id = "non-existing-id"
    response = api_client.get(f"{BASE_URL}/studies?id={filter_by_id}")
    assert response.status_code == 200
    res = response.json()
    assert res.keys() == {"self", "prev", "next", "items"}
    assert len(res["items"]) == 0
    for key in ["self", "prev", "next"]:
        assert f"id={filter_by_id}&" in res[key]


def test_get_studies_invalid_pagination_params(api_client):
    response = api_client.get(f"{BASE_URL}/studies?page_size=0")
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"]
        == "ensure this value is greater than or equal to 1"
    )

    response = api_client.get(
        f"{BASE_URL}/studies?page_size={config.MAX_PAGE_SIZE + 1}"
    )
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"]
        == "ensure this value is less than or equal to 1000"
    )

    response = api_client.get(
        f"{BASE_URL}/studies?page_number={config.MAX_INT_NEO4J + 1}&page_size=1"
    )
    assert response.status_code == 400
    assert (
        response.json()["message"]
        == "(page_number * page_size) value cannot be bigger than 9223372036854775807"
    )
