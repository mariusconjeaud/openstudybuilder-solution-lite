# pylint: disable=invalid-name
# pylint: disable=redefined-builtin
from consumer_api.shared.common import (
    db_pagination_clause,
    db_sort_clause,
    query,
    validate_page_number_and_page_size,
)
from consumer_api.v1 import models


def get_studies(
    sort_by: models.SortByStudies = models.SortByStudies.UID,
    sort_order: models.SortOrder = models.SortOrder.ASC,
    page_size: int = 10,
    page_number: int = 1,
    id: str = None,
) -> list[dict]:
    validate_page_number_and_page_size(page_number, page_size)

    params = {}
    filter_clause = ""

    if id is not None:
        params["id"] = id.strip()
        filter_clause = "WHERE id CONTAINS toUpper($id)"

    base_query = f"""
        MATCH (root:StudyRoot)-[:LATEST]->(val:StudyValue)
        WITH    root.uid as uid,
                val.study_acronym as acronym,
                val.study_id_prefix as id_prefix,
                val.study_number as number,
                toUpper(COALESCE(val.study_id_prefix, '') + "-" + COALESCE(val.study_number, '')) as id
        {filter_clause}
        RETURN *
        """

    full_query = " ".join(
        [
            base_query,
            db_sort_clause(sort_by.value, sort_order.value),
            db_pagination_clause(page_size, page_number),
        ]
    )
    return query(full_query, params)
