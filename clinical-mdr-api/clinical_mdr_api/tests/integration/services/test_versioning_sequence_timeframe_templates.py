from unittest import TestCase

from pydantic import BaseModel

import clinical_mdr_api.models.syntax_templates.timeframe_template as models
import clinical_mdr_api.services.libraries.libraries as library_service
import clinical_mdr_api.services.syntax_templates.timeframe_templates as tt_service
from clinical_mdr_api.exceptions import BusinessLogicException, NotFoundException
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.tests.integration.utils.api import inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    library_data,
    template_data,
)

service = tt_service.TimeframeTemplateService()


class TestCreate(TestCase):
    TEST_DB_NAME = "ttfversioning"
    timeframe_template: BaseModel

    @classmethod
    def setUp(cls):
        inject_and_clear_db(cls.TEST_DB_NAME)
        cls.library = library_service.create(**library_data)

    def test_create(self):
        data = {"name": template_data["name"], "library_name": self.library["name"]}
        timeframe_template = models.TimeframeTemplateCreateInput(**data)
        result = service.create(timeframe_template)
        self.assertIsInstance(result, models.TimeframeTemplate)
        self.assertEqual(result.name, template_data["name"])
        self.assertEqual(result.status, "Draft")
        self.assertEqual(result.version, "0.1")
        self.timeframe_template = result


# @pytest.mark.skip
class TestDraftEdit(TestCase):
    TEST_DB_NAME = "ttfversioning"

    @classmethod
    def setUp(cls):
        inject_and_clear_db(cls.TEST_DB_NAME)
        cls.library = library_service.create(**library_data)
        timeframe_template = models.TimeframeTemplateCreateInput(**template_data)
        cls.timeframe_template = service.create(timeframe_template)

    def test_edit(self):
        data = {
            "name": template_data["name"] + " edited",
            "change_description": "tested",
        }
        timeframe_template = models.TimeframeTemplateEditInput(**data)
        assert isinstance(self.timeframe_template, models.TimeframeTemplate)
        result = service.edit_draft(self.timeframe_template.uid, timeframe_template)
        assert isinstance(result, models.TimeframeTemplate)
        self.assertEqual(result.version, "0.2")
        self.assertEqual(result.status, "Draft")
        self.assertEqual(result.name, data["name"])

        data = {
            "name": template_data["name"] + " edited again",
            "change_description": "tested",
        }
        timeframe_template = models.TimeframeTemplateEditInput(**data)
        result = service.edit_draft(self.timeframe_template.uid, timeframe_template)
        assert isinstance(result, models.TimeframeTemplate)
        self.assertEqual(result.version, "0.3")
        self.assertEqual(result.status, "Draft")
        self.assertEqual(result.name, data["name"])


# @pytest.mark.skip
class TestApprove(TestCase):
    TEST_DB_NAME = "ttfversioning"

    @classmethod
    def setUp(cls):
        inject_and_clear_db(cls.TEST_DB_NAME)
        cls.library = library_service.create(**library_data)
        timeframe_template = models.TimeframeTemplateCreateInput(**template_data)
        timeframe_template = service.create(timeframe_template)
        assert isinstance(timeframe_template, models.TimeframeTemplate)
        cls.timeframe_template = timeframe_template

    def test_approve(self):
        result = service.approve(self.timeframe_template.uid)
        assert isinstance(result, models.TimeframeTemplate)
        self.assertEqual(result.version, "1.0")
        self.assertEqual(result.status, "Final")


class TestActivation(TestCase):
    TEST_DB_NAME = "ttfversioning"

    @classmethod
    def setUp(cls):
        inject_and_clear_db(cls.TEST_DB_NAME)
        cls.library = library_service.create(**library_data)
        timeframe_template = models.TimeframeTemplateCreateInput(**template_data)
        timeframe_template = service.create(timeframe_template)
        assert isinstance(timeframe_template, models.TimeframeTemplate)
        timeframe_template = service.approve(timeframe_template.uid)
        assert isinstance(timeframe_template, models.TimeframeTemplate)
        cls.timeframe_template = timeframe_template

    def test_activation(self):
        result = service.inactivate_final(self.timeframe_template.uid)
        assert isinstance(result, models.TimeframeTemplate)
        self.assertEqual(result.version, "1.0")
        self.assertEqual(result.status, "Retired")
        with self.assertRaises(BusinessLogicException):
            service.inactivate_final(self.timeframe_template.uid)

        result = service.reactivate_retired(self.timeframe_template.uid)
        assert isinstance(result, models.TimeframeTemplate)
        self.assertEqual(result.version, "1.0")
        self.assertEqual(result.status, "Final")
        with self.assertRaises(BusinessLogicException):
            service.reactivate_retired(self.timeframe_template.uid)


# @pytest.mark.skip
class TestSoftDelete(TestCase):
    TEST_DB_NAME = "ttfversioning"

    @classmethod
    def setUp(cls):
        inject_and_clear_db(cls.TEST_DB_NAME)
        cls.library = library_service.create(**library_data)
        timeframe_template = models.TimeframeTemplateCreateInput(**template_data)
        timeframe_template = service.create(timeframe_template)
        assert isinstance(timeframe_template, models.TimeframeTemplate)
        cls.timeframe_template = timeframe_template

    def test_softdelete(self):
        service.soft_delete(self.timeframe_template.uid)
        repos = MetaRepository()

        with self.assertRaises(NotFoundException) as message:
            repos.timeframe_template_repository.find_by_uid(self.timeframe_template.uid)
        self.assertEqual(
            "No Syntax Template with UID (TimeframeTemplate_000001) found in given status and version.",
            str(message.exception),
        )
