import os

from fastapi.testclient import TestClient
from neomodel import db
from pydantic import BaseModel

from clinical_mdr_api.services.syntax_templates.criteria_templates import (
    CriteriaTemplateService,
)
from clinical_mdr_api.tests.integration.utils import api
from clinical_mdr_api.tests.integration.utils.api import inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    CREATE_BASE_TEMPLATE_PARAMETER_TREE,
    STARTUP_CRITERIA,
    STARTUP_PARAMETERS_CYPHER,
)
from clinical_mdr_api.tests.integration.utils.data_library import (
    criteria_template_data as template_data,
)
from clinical_mdr_api.tests.integration.utils.data_library import (
    inject_base_data,
    library_data,
)

BASE_SCENARIO_PATH = "clinical_mdr_api/tests/data/scenarios/"


class CriteriaTest(api.APITest):
    TEST_DB_NAME = "unittestscrit"

    def setUp(self):
        inject_and_clear_db(self.TEST_DB_NAME)
        db.cypher_query(STARTUP_PARAMETERS_CYPHER)
        db.cypher_query(CREATE_BASE_TEMPLATE_PARAMETER_TREE)
        inject_base_data()
        db.cypher_query(STARTUP_CRITERIA)

        import clinical_mdr_api.models.syntax_templates.criteria_template as ct_models
        import clinical_mdr_api.services.libraries as library_service
        from clinical_mdr_api import main

        self.test_client = TestClient(main.app)
        self.library = library_service.create(**library_data)
        templatedata = template_data.copy()
        criteria_template = ct_models.CriteriaTemplateCreateInput(**templatedata)
        self.ct = CriteriaTemplateService().create(criteria_template)
        if isinstance(self.ct, BaseModel):
            self.ct = self.ct.dict()
        CriteriaTemplateService().approve(self.ct["uid"])
        self.data["ctuid"] = self.ct["uid"]

    SCENARIO_PATHS = [os.path.join(BASE_SCENARIO_PATH, "criteria.json")]

    def ignored_fields(self):
        return ["start_date", "end_date", "uid", "time"]
