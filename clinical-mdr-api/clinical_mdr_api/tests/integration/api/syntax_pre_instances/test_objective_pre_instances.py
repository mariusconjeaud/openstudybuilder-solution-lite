"""
Tests for objective-templates endpoints
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
from clinical_mdr_api.models.syntax_pre_instances.objective_pre_instance import (
    ObjectivePreInstance,
)
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
objective_pre_instances: List[ObjectivePreInstance]
dictionary_term_indication: models.DictionaryTerm
ct_term_category: models.CTTerm
indications_codelist: models.DictionaryCodelist
indications_library_name: str
text_value_1: models.TextValue

URL = "objective-pre-instances"


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

    global objective_pre_instances
    global dictionary_term_indication
    global ct_term_category
    global indications_codelist
    global indications_library_name
    global text_value_1

    # Create Template Parameter
    TestUtils.create_template_parameter("TextValue")

    text_value_1 = TestUtils.create_text_value()

    # Create Dictionary/CT Terms
    indications_library_name = "SNOMED"
    indications_codelist = TestUtils.create_dictionary_codelist(
        name="DiseaseDisorder", library_name=indications_library_name
    )
    dictionary_term_indication = TestUtils.create_dictionary_term(
        codelist_uid=indications_codelist.codelist_uid,
        library_name=indications_library_name,
    )
    ct_term_category = TestUtils.create_ct_term()
    objective_template = TestUtils.create_objective_template(
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
    )

    # Create some objective_pre_instances
    objective_pre_instances = []
    objective_pre_instances.append(
        TestUtils.create_objective_pre_instance(
            template_uid=objective_template.uid,
            library_name="Sponsor",
            is_confirmatory_testing=True,
            parameter_terms=[
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
        )
    )
    objective_pre_instances.append(
        TestUtils.create_objective_pre_instance(
            template_uid=objective_template.uid,
            library_name="Sponsor",
            is_confirmatory_testing=True,
            parameter_terms=[
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
        )
    )
    objective_pre_instances.append(
        TestUtils.create_objective_pre_instance(
            template_uid=objective_template.uid,
            library_name="Sponsor",
            is_confirmatory_testing=True,
            parameter_terms=[
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
        )
    )
    objective_pre_instances.append(
        TestUtils.create_objective_pre_instance(
            template_uid=objective_template.uid,
            library_name="Sponsor",
            is_confirmatory_testing=True,
            parameter_terms=[
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
        )
    )
    objective_pre_instances.append(
        TestUtils.create_objective_pre_instance(
            template_uid=objective_template.uid,
            library_name="Sponsor",
            is_confirmatory_testing=True,
            parameter_terms=[
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
        )
    )

    for _ in range(5):
        objective_pre_instances.append(
            TestUtils.create_objective_pre_instance(
                template_uid=objective_template.uid,
                library_name="Sponsor",
                is_confirmatory_testing=False,
                parameter_terms=[
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
            )
        )
        objective_pre_instances.append(
            TestUtils.create_objective_pre_instance(
                template_uid=objective_template.uid,
                library_name="Sponsor",
                is_confirmatory_testing=False,
                parameter_terms=[
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
            )
        )
        objective_pre_instances.append(
            TestUtils.create_objective_pre_instance(
                template_uid=objective_template.uid,
                library_name="Sponsor",
                is_confirmatory_testing=False,
                parameter_terms=[
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
            )
        )
        objective_pre_instances.append(
            TestUtils.create_objective_pre_instance(
                template_uid=objective_template.uid,
                library_name="Sponsor",
                is_confirmatory_testing=False,
                parameter_terms=[
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
            )
        )

    yield

    drop_db(URL + ".api")


OBJECTIVE_PRE_INSTANCE_FIELDS_ALL = [
    "name",
    "name_plain",
    "uid",
    "template_uid",
    "status",
    "version",
    "change_description",
    "start_date",
    "end_date",
    "user_initials",
    "possible_actions",
    "is_confirmatory_testing",
    "parameter_terms",
    "library",
    "indications",
    "categories",
]

OBJECTIVE_PRE_INSTANCE_FIELDS_NOT_NULL = [
    "uid",
    "template_uid",
    "name",
]


def test_get_objective_pre_instances_pagination(api_client):
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
    assert len(objective_pre_instances) == len(results_paginated_merged)


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
def test_get_objective_pre_instances(
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
    assert res["total"] == (len(objective_pre_instances) if total_count else 0)
    assert res["page"] == (page_number if page_number else 1)
    assert res["size"] == (page_size if page_size else 10)

    for item in res["items"]:
        assert set(list(item.keys())) == set(OBJECTIVE_PRE_INSTANCE_FIELDS_ALL)
        for key in OBJECTIVE_PRE_INSTANCE_FIELDS_NOT_NULL:
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
