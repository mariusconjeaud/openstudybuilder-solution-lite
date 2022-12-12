from json import loads

from neomodel import db
from starlette.testclient import TestClient

from clinical_mdr_api.tests.data.odm_xml import (
    clinspark_input,
    clinspark_output,
    import_input1,
    import_input2,
    import_input3,
    import_output1,
    import_output2,
)
from clinical_mdr_api.tests.integration.utils import api
from clinical_mdr_api.tests.integration.utils.api import inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_CT_TERM_ATTRIBUTES_CYPHER,
    STARTUP_UNIT_DEFINITIONS,
)


class OdmXmlImporterTest(api.APITest):
    TEST_DB_NAME = "odmxmlimporter"
    CONTENT_TYPE = "application/xml"

    def setUp(self):
        inject_and_clear_db(self.TEST_DB_NAME)
        db.cypher_query("MERGE (library:Library {name:'Sponsor', is_editable:true})")
        db.cypher_query(STARTUP_UNIT_DEFINITIONS)
        db.cypher_query(STARTUP_CT_TERM_ATTRIBUTES_CYPHER)

        from clinical_mdr_api import main

        self.test_client = TestClient(main.app)

    def ignored_fields(self):
        return [
            "start_date",
            "end_date",
            "user_initials",
        ]

    def test_import_odm_xml(self):
        response = self.test_client.post(
            "concepts/odms/metadata/xmls/import",
            files={"xml": ("odm.xml", import_input1, self.CONTENT_TYPE)},
        )

        self.check(import_output1, loads(response.content))

    def test_import_odm_xml_with_csv_mapper(self):
        response = self.test_client.post(
            "concepts/odms/metadata/xmls/import",
            files={
                "xml": ("odm.xml", import_input2, self.CONTENT_TYPE),
                "mapper": (
                    "mapper.csv",
                    "type,parent,from_name,to_name,to_alias,from_alias,alias_context\n"
                    "attribute,,Repeated,Repeating,,,\n"
                    "tag,,NameOne,cs:nameOne,,,\n"
                    "tag,,Alias,,,true,CompletionInstructions\n"
                    "tag,*,Alias,,,true,ImplementationNotes\n"
                    "attribute,,CompletionInstructions,osb:instruction,,,\n"
                    "attribute,*,ImplementationNotes,osb:sponsorInstruction,,,\n",
                    "text/csv",
                ),
            },
        )

        self.check(import_output2, loads(response.content))

    # Test for temporary endpoint of Clinspark Import
    def test_import_clinspark_odm_xml(self):
        db.cypher_query("MERGE (:CTCatalogue {name:'CDASH CT'})")
        response = self.test_client.post(
            "concepts/odms/metadata/clinspark/import",
            files={"xml": ("clinspark.xml", clinspark_input, self.CONTENT_TYPE)},
        )

        self.check(clinspark_output, loads(response.content))

    def test_throw_exception_if_file_is_not_xml(self):
        response = self.test_client.post(
            "concepts/odms/metadata/xmls/import",
            files={
                "xml": (
                    "mapper.json",
                    "",
                    "application/json",
                )
            },
        )

        self.assertEqual(response.status_code, 400)
        rs = loads(response.content)
        self.assertEqual(rs["type"], "BusinessLogicException")
        self.assertEqual(rs["message"], "Only XML format is supported.")

    def test_throw_exception_if_measurementunits_dont_exist(self):
        response = self.test_client.post(
            "concepts/odms/metadata/xmls/import",
            files={"xml": ("odm.xml", import_input3, self.CONTENT_TYPE)},
        )

        self.assertEqual(response.status_code, 400)
        rs = loads(response.content)
        self.assertEqual(rs["type"], "BusinessLogicException")
        self.assertEqual(
            rs["message"],
            "MeasurementUnits identified by following OIDs {'wrong name'} don't match any Unit Definition.",
        )
