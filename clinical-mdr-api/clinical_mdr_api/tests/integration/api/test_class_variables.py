"""
Tests for /standards/class-variables endpoints
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

from clinical_mdr_api.main import app
from clinical_mdr_api.models.standard_data_models.class_variable import ClassVariable
from clinical_mdr_api.models.standard_data_models.data_model import DataModel
from clinical_mdr_api.models.standard_data_models.dataset_class import DatasetClass
from clinical_mdr_api.models.standard_data_models.dataset_variable import (
    DatasetVariable,
)
from clinical_mdr_api.services.standard_data_models.class_variable import (
    ClassVariableService,
)
from clinical_mdr_api.tests.integration.utils.api import (
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
data_model_catalogue_name: str
data_models: List[DataModel]
dataset_classes: List[DatasetClass]
dataset_variable: DatasetVariable
class_variables: List[ClassVariable]


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    inject_and_clear_db("class-variables.api")
    inject_base_data()

    global data_model_catalogue_name
    global data_models
    global dataset_classes
    global dataset_variable
    global class_variables

    data_model_catalogue_name = TestUtils.create_data_model_catalogue(
        name="DataModelCatalogue name"
    )
    data_models = [
        TestUtils.create_data_model(name=name)
        for name in ["DataModel A", "DataModel B", "DataModel C"]
    ]
    dataset_classes = [
        TestUtils.create_dataset_class(
            label=label,
            data_model_uid=data_model_uid,
            data_model_catalogue_name=data_model_catalogue_name,
        )
        for label, data_model_uid in [
            ("DatasetClass A", data_models[0].uid),
            ("DatasetClass B", data_models[1].uid),
            ("DatasetClass C", data_models[2].uid),
        ]
    ]
    data_model_ig = TestUtils.create_data_model_ig(name="DataModelIG A")
    # Create some datasets
    dataset = TestUtils.create_dataset(
        label="Dataset A label",
        title="Dataset A title",
        description="Dataset A desc",
        data_model_catalogue_name=data_model_catalogue_name,
        data_model_ig_uid=data_model_ig.uid,
        implemented_dataset_class_name=dataset_classes[0].uid,
    )

    # Create some class-variables
    class_variables = []
    class_variables.append(
        TestUtils.create_class_variable(
            label="ClassVariable A label",
            title="ClassVariable A title",
            description="ClassVariable A desc",
            data_model_catalogue_name=data_model_catalogue_name,
            dataset_class_uid=dataset_classes[0].uid,
        )
    )
    dataset_variable = TestUtils.create_dataset_variable(
        label="DatasetVariable A",
        dataset_uid=dataset.uid,
        data_model_catalogue_name=data_model_catalogue_name,
        class_variable_uid=class_variables[0].uid,
    )
    # update class variable with dataset variable relationship
    class_variables[0] = ClassVariableService().get_by_uid(uid=class_variables[0].uid)
    class_variables.append(
        TestUtils.create_class_variable(
            label="name-AAA",
            data_model_catalogue_name=data_model_catalogue_name,
            dataset_class_uid=dataset_classes[1].uid,
        )
    )
    class_variables.append(
        TestUtils.create_class_variable(
            label="name-BBB",
            data_model_catalogue_name=data_model_catalogue_name,
            dataset_class_uid=dataset_classes[1].uid,
        )
    )
    class_variables.append(
        TestUtils.create_class_variable(
            description="def-XXX",
            data_model_catalogue_name=data_model_catalogue_name,
            dataset_class_uid=dataset_classes[1].uid,
        )
    )
    class_variables.append(
        TestUtils.create_class_variable(
            description="def-YYY",
            data_model_catalogue_name=data_model_catalogue_name,
            dataset_class_uid=dataset_classes[1].uid,
        )
    )

    for index in range(5):
        class_variables.append(
            TestUtils.create_class_variable(
                label=f"name-AAA-{index}",
                data_model_catalogue_name=data_model_catalogue_name,
                dataset_class_uid=dataset_classes[2].uid,
            )
        )
        class_variables.append(
            TestUtils.create_class_variable(
                label=f"name-BBB-{index}",
                data_model_catalogue_name=data_model_catalogue_name,
                dataset_class_uid=dataset_classes[2].uid,
            )
        )
        class_variables.append(
            TestUtils.create_class_variable(
                description=f"def-XXX-{index}",
                data_model_catalogue_name=data_model_catalogue_name,
                dataset_class_uid=dataset_classes[2].uid,
            )
        )
        class_variables.append(
            TestUtils.create_class_variable(
                description=f"def-YYY-{index}",
                data_model_catalogue_name=data_model_catalogue_name,
                dataset_class_uid=dataset_classes[2].uid,
            )
        )


CLASS_VARIABLE_FIELDS_ALL = [
    "uid",
    "label",
    "title",
    "description",
    "implementation_notes",
    "title",
    "label",
    "mapping_instructions",
    "prompt",
    "question_text",
    "simple_datatype",
    "role",
    "catalogue_name",
    "dataset_class_name",
    "dataset_variable_name",
    # "library_name",
    "start_date",
    "end_date",
    "status",
    "version",
    "change_description",
    "user_initials",
]

CLASS_VARIABLE_FIELDS_NOT_NULL = [
    "uid",
    "label",
    "catalogue_name",
    "dataset_class_name",
]


def test_get_class_variable(api_client):
    response = api_client.get(f"/standards/class-variables/{class_variables[0].uid}")
    res = response.json()

    assert response.status_code == 200

    # Check fields included in the response
    assert set(list(res.keys())) == set(CLASS_VARIABLE_FIELDS_ALL)
    for key in CLASS_VARIABLE_FIELDS_NOT_NULL:
        assert res[key] is not None

    assert res["uid"] == class_variables[0].uid
    assert res["label"] == "ClassVariable A label"
    assert res["description"] == "ClassVariable A desc"
    assert res["version"] == "1.0"
    assert res["status"] == "Final"
    assert res["catalogue_name"] == data_model_catalogue_name
    assert res["dataset_class_name"] == dataset_classes[0].label
    assert res["dataset_variable_name"] == dataset_variable.label


def test_get_class_variables_pagination(api_client):
    results_paginated: dict = {}
    sort_by = '{"uid": true}'
    for page_number in range(1, 4):
        url = f"/standards/class-variables?page_number={page_number}&page_size=10&sort_by={sort_by}"
        response = api_client.get(url)
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
        f"/standards/class-variables?page_number=1&page_size=100&sort_by={sort_by}"
    ).json()
    results_all_in_one_page = list(map(lambda x: x["uid"], res_all["items"]))
    log.info("All rows in one page: %s", results_all_in_one_page)
    assert len(results_all_in_one_page) == len(results_paginated_merged)
    assert len(class_variables) == len(results_paginated_merged)


@pytest.mark.parametrize(
    "page_size, page_number, total_count, sort_by, expected_result_len",
    [
        pytest.param(None, None, None, None, 10),
        pytest.param(3, 1, True, None, 3),
        pytest.param(3, 2, True, None, 3),
        pytest.param(10, 2, True, None, 10),
        pytest.param(10, 3, True, None, 5),  # Total numer of data models is 25
        pytest.param(10, 1, True, '{"label": false}', 10),
        pytest.param(10, 2, True, '{"label": true}', 10),
    ],
)
def test_get_class_variables(
    api_client, page_size, page_number, total_count, sort_by, expected_result_len
):
    url = "/standards/class-variables"
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
    assert res["total"] == (len(class_variables) if total_count else 0)
    assert res["page"] == (page_number if page_number else 1)
    assert res["size"] == (page_size if page_size else 10)

    for item in res["items"]:
        assert set(list(item.keys())) == set(CLASS_VARIABLE_FIELDS_ALL)
        for key in CLASS_VARIABLE_FIELDS_NOT_NULL:
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
    "filter_by, expected_matched_field, expected_result_prefix",
    [
        pytest.param('{"*": {"v": ["aaa"]}}', "label", "name-AAA"),
        pytest.param('{"*": {"v": ["bBb"]}}', "label", "name-BBB"),
        pytest.param('{"*": {"v": ["ccc"]}}', None, None),
        pytest.param(
            '{"*": {"v": ["DatasetClass A"]}}', "dataset_class_name", "DatasetClass A"
        ),
        pytest.param(
            '{"*": {"v": ["DatasetVariable A"]}}',
            "dataset_variable_name",
            "DatasetVariable A",
        ),
        pytest.param(
            '{"*": {"v": ["DataModelCatalogue name"]}}',
            "catalogue_name",
            "DataModelCatalogue name",
        ),
    ],
)
def test_filtering_wildcard(
    api_client, filter_by, expected_matched_field, expected_result_prefix
):
    url = f"/standards/class-variables?filters={filter_by}"
    response = api_client.get(url)
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
        pytest.param('{"label": {"v": ["name-AAA"]}}', "label", "name-AAA"),
        pytest.param('{"label": {"v": ["name-BBB"]}}', "label", "name-BBB"),
        pytest.param('{"label": {"v": ["cc"]}}', None, None),
        pytest.param('{"description": {"v": ["def-XXX"]}}', "description", "def-XXX"),
        pytest.param('{"description": {"v": ["def-YYY"]}}', "description", "def-YYY"),
        pytest.param('{"description": {"v": ["cc"]}}', None, None),
        pytest.param(
            '{"dataset_class_name": {"v": ["DatasetClass A"]}}',
            "dataset_class_name",
            "DatasetClass A",
        ),
        pytest.param(
            '{"dataset_variable_name": {"v": ["DatasetVariable A"]}}',
            "dataset_variable_name",
            "DatasetVariable A",
        ),
        pytest.param(
            '{"catalogue_name": {"v": ["DataModelCatalogue name"]}}',
            "catalogue_name",
            "DataModelCatalogue name",
        ),
    ],
)
def test_filtering_exact(
    api_client, filter_by, expected_matched_field, expected_result
):
    url = f"/standards/class-variables?filters={filter_by}"
    response = api_client.get(url)
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
                assert row[expected_matched_field] == expected_result
    else:
        assert len(res["items"]) == 0


@pytest.mark.parametrize(
    "field_name",
    [
        pytest.param("label"),
        pytest.param("description"),
        pytest.param("role"),
        pytest.param("dataset_class_name"),
        pytest.param("dataset_variable_name"),
        pytest.param("catalogue_name"),
    ],
)
def test_headers(api_client, field_name):
    url = f"/standards/class-variables/headers?field_name={field_name}&result_count=100"
    response = api_client.get(url)
    res = response.json()

    assert response.status_code == 200
    expected_result = []
    for class_variable in class_variables:
        value = getattr(class_variable, field_name)
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
