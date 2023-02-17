# pylint: disable=unused-argument,redefined-outer-name

import logging

import pytest

from clinical_mdr_api.tests.integration.utils.api import inject_and_clear_db

__all__ = ["tst_database"]

log = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def tst_database(request) -> str:
    """fixture changing to a clear database, name derived from module name"""
    db_name = request.module.__name__.rsplit(".", 1)[-1].replace("_", "-")
    log.info(
        "%s fixture: doing ugly magic to use database: %s", request.fixturename, db_name
    )
    inject_and_clear_db(db_name)
    return db_name
