import logging
import xml.etree.ElementTree as ET

import pytest

from clinical_mdr_api.tests.integration.utils.api import inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import inject_base_data
from clinical_mdr_api.tests.integration.utils.method_library import generate_study_root
from clinical_mdr_api.tests.utils.checks import (
    assert_response_content_type,
    assert_response_status_code,
)

ODM_TAG = "{http://www.cdisc.org/ns/odm/v1.3}ODM"
TEST_DB_NAME = __name__.replace("_", "-")

log = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def test_database():
    log.info(
        "test_database fixture: doing ugly magic to use database: %s", TEST_DB_NAME
    )
    inject_and_clear_db(TEST_DB_NAME)
    log.info(
        "test_database fixture: injecting base data into database: %s", TEST_DB_NAME
    )
    study = inject_base_data()
    return study


# pylint: disable=unused-argument,redefined-outer-name
def test_xml_response(app_client, test_database):
    study = generate_study_root()
    response = app_client.get(f"/studies/{study.uid}/ctr/odm.xml", stream=True)
    assert_response_status_code(response, 200)
    assert_response_content_type(response, "text/xml")
    tree = ET.parse(response.raw)
    root = tree.getroot()
    assert root.tag == ODM_TAG, f"Document root tag is not '{ODM_TAG}'"
