"""
This modules verifies that database nodes/relations and API endpoints look and behave as expected.

It utilizes tests written for verifying a specific migration,
without inserting any test data and without running any migration script on the target database.
"""

import os

from data_corrections.utils.utils import get_db_driver, run_cypher_query
from migrations.utils.utils import get_logger

LOGGER = get_logger(os.path.basename(__file__))
DB_DRIVER = get_db_driver()


def test_delete_unwanted_valid_for_epoch_type_relationship():
    LOGGER.info("Check for unwanted VALID_FOR_EPOCH_TYPE relationship")

    records, _summary = run_cypher_query(
        DB_DRIVER,
        """
        MATCH ()-[r:VALID_FOR_EPOCH_TYPE]-()
        RETURN r
        """,
    )
    assert (
        len(records) == 0
    ), f"Found {len(records)} unwanted VALID_FOR_EPOCH_TYPE relationship."
