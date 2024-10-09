""" PRD Data Corrections, for release 1.8"""

import os

from migrations.utils.utils import get_logger
from data_corrections.utils.utils import (
    get_db_driver,
    run_cypher_query,
    print_counters_table,
    capture_changes,
    save_md_title,
)


LOGGER = get_logger(os.path.basename(__file__))
DB_DRIVER = get_db_driver()
CORRECTION_DESC = "data-correction-release-1.8"


def main(run_label="correction"):
    desc = f"Running data corrections on DB '{os.environ['DATABASE_NAME']}'"
    LOGGER.info(desc)
    save_md_title(run_label, __doc__, desc)

    delete_valid_for_epoch_type_relationship(DB_DRIVER, LOGGER, run_label)


@capture_changes(task_level=1)
def delete_valid_for_epoch_type_relationship(db_driver, log, run_label):
    """
    Delete VALID_FOR_EPOCH_TYPE relationship
    """
    desc = "Deleting VALID_FOR_EPOCH_TYPE relationship from the database"
    log.info(f"Run: {run_label}, {desc}")

    _, summary = run_cypher_query(
        db_driver,
        """
        MATCH ()-[r:VALID_FOR_EPOCH_TYPE]-()
        DETACH DELETE r
        """,
    )
    counters = summary.counters
    print_counters_table(counters)
    return counters.contains_updates


if __name__ == "__main__":
    main()
