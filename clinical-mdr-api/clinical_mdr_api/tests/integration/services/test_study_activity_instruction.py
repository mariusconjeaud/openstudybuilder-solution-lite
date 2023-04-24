import unittest

import pydantic
from neomodel import db

import clinical_mdr_api.services.libraries as library_service
from clinical_mdr_api import models
from clinical_mdr_api.services.study_activity_instruction import (
    StudyActivityInstructionService,
)
from clinical_mdr_api.services.study_activity_selection import (
    StudyActivitySelectionService,
)
from clinical_mdr_api.services.syntax_templates.activity_instruction_templates import (
    ActivityInstructionTemplateService,
)
from clinical_mdr_api.tests.integration.utils import data_library
from clinical_mdr_api.tests.integration.utils.api import inject_and_clear_db


class StudyActivityInstructionTestCase(unittest.TestCase):
    def setUp(self):
        inject_and_clear_db("studyactivityinstructiontest")
        db.cypher_query(data_library.STARTUP_PARAMETERS_CYPHER)
        db.cypher_query(data_library.CREATE_BASE_TEMPLATE_PARAMETER_TREE)
        db.cypher_query(data_library.STARTUP_ACTIVITY_GROUPS)
        db.cypher_query(data_library.STARTUP_ACTIVITY_SUB_GROUPS)
        db.cypher_query(data_library.STARTUP_ACTIVITIES)
        db.cypher_query(
            data_library.get_codelist_with_term_cypher("EFFICACY", "Flowchart Group")
        )
        db.cypher_query(data_library.STARTUP_SINGLE_STUDY_CYPHER)

        self.library = library_service.create(**data_library.library_data)
        data = data_library.template_data.copy()
        data["name"] = "Test [Indication]"
        data["activity_subgroup_uids"] = ["activity_subgroup_root1"]
        data["activity_group_uids"] = ["activity_group_root1"]
        template_input = models.ActivityInstructionTemplateCreateInput(**data)
        service = ActivityInstructionTemplateService()
        self.template = service.create(template_input)
        service.approve(self.template.dict()["uid"])
        self._create_study_activities()
        self.service = StudyActivityInstructionService("AZNG")

    def _create_study_activities(self):
        service = StudyActivitySelectionService("AZNG")
        service.handle_batch_operations(
            "study_root",
            [
                models.StudySelectionActivityBatchInput(
                    method="POST",
                    content=models.StudySelectionActivityCreateInput(
                        flowchart_group_uid="term_root_final",
                        activity_uid="activity_root1",
                    ),
                ),
                models.StudySelectionActivityBatchInput(
                    method="POST",
                    content=models.StudySelectionActivityCreateInput(
                        flowchart_group_uid="term_root_final",
                        activity_uid="activity_root2",
                    ),
                ),
            ],
        )

    def _create_study_activity_instruction(self):
        self.service.create(
            "study_root",
            models.StudyActivityInstructionCreateInput(
                activity_instruction_data=models.ActivityInstructionCreateInput(
                    activity_instruction_template_uid=self.template.uid,
                    parameter_terms=[
                        {
                            "conjunction": "",
                            "position": 1,
                            "terms": [
                                {
                                    "index": 1,
                                    "name": "type 2 diabetes",
                                    "type": "Indication",
                                    "uid": "Indication-99991",
                                }
                            ],
                        }
                    ],
                    library_name=self.library["name"],
                ),
                study_activity_uid="StudyActivity_000001",
            ),
        )

    def test_create_validation_error(self):
        with self.assertRaises(pydantic.ValidationError):
            self.service.create(
                "study_root",
                models.StudyActivityInstructionCreateInput(
                    study_activity_uid="StudyActivity_000001"
                ),
            )

    def test_get_all_instructions(self):
        self._create_study_activity_instruction()
        study_activity_instruction = self.service.get_all_instructions_for_all_studies()
        self.assertEqual(len(study_activity_instruction.items), 1)

    def test_create(self):
        # Test with activity instruction creation
        self._create_study_activity_instruction()
        study_activity_instructions = self.service.get_all_instructions("study_root")
        self.assertEqual(len(study_activity_instructions), 1)

        # Test activity instruction selection
        self.service.create(
            "study_root",
            models.StudyActivityInstructionCreateInput(
                activity_instruction_uid="ActivityInstruction_000001",
                study_activity_uid="StudyActivity_000001",
            ),
        )
        study_activity_instructions = self.service.get_all_instructions("study_root")
        self.assertEqual(len(study_activity_instructions), 2)

    def test_delete(self):
        self._create_study_activity_instruction()
        self.service.delete("study_root", "StudyActivityInstruction_000001")
        study_activity_instructions = self.service.get_all_instructions("study_root")
        self.assertEqual(len(study_activity_instructions), 0)

    def test_batch_operations(self):
        self.service.handle_batch_operations(
            "study_root",
            [
                models.StudyActivityInstructionBatchInput(
                    method="POST",
                    content=models.StudyActivityInstructionCreateInput(
                        activity_instruction_data=models.ActivityInstructionCreateInput(
                            activity_instruction_template_uid=self.template.uid,
                            parameter_terms=[
                                {
                                    "conjunction": "",
                                    "position": 1,
                                    "terms": [
                                        {
                                            "index": 1,
                                            "name": "type 2 diabetes",
                                            "type": "Indication",
                                            "uid": "Indication-99991",
                                        }
                                    ],
                                }
                            ],
                            library_name=self.library["name"],
                        ),
                        study_activity_uid="StudyActivity_000001",
                    ),
                ),
                models.StudyActivityInstructionBatchInput(
                    method="POST",
                    content=models.StudyActivityInstructionCreateInput(
                        activity_instruction_data=models.ActivityInstructionCreateInput(
                            activity_instruction_template_uid=self.template.uid,
                            parameter_terms=[
                                {
                                    "conjunction": "",
                                    "position": 1,
                                    "terms": [
                                        {
                                            "index": 1,
                                            "name": "type 2 diabetes",
                                            "type": "Indication",
                                            "uid": "Indication-99991",
                                        }
                                    ],
                                }
                            ],
                            library_name=self.library["name"],
                        ),
                        study_activity_uid="StudyActivity_000002",
                    ),
                ),
            ],
        )
        study_activity_instructions = self.service.get_all_instructions("study_root")
        assert len(study_activity_instructions) == 2

        self.service.handle_batch_operations(
            "study_root",
            [
                models.StudyActivityInstructionBatchInput(
                    method="DELETE",
                    content=models.StudyActivityInstructionDeleteInput(
                        study_activity_instruction_uid="StudyActivityInstruction_000001"
                    ),
                )
            ],
        )
        study_activity_instructions = self.service.get_all_instructions("study_root")
        assert len(study_activity_instructions) == 1
