# pylint:disable=broad-except
import csv
import io
import logging
from datetime import datetime, timedelta, timezone
from random import randint
from typing import List, Optional, Sequence
from xml.etree import ElementTree

import openpyxl
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api import config, models
from clinical_mdr_api.config import DEFAULT_STUDY_FIELD_CONFIG_FILE
from clinical_mdr_api.domain_repositories.models.standard_data_model import (
    ClassVariableRoot,
    DataModelIGRoot,
    DataModelRoot,
    DatasetClassRoot,
    DatasetRoot,
    DatasetVariableRoot,
)
from clinical_mdr_api.models import Activity, ActivityCreateInput, CTCodelist
from clinical_mdr_api.models.activities.activity_group import (
    ActivityGroup,
    ActivityGroupCreateInput,
)
from clinical_mdr_api.models.activities.activity_instance import (
    ActivityInstance,
    ActivityInstanceCreateInput,
)
from clinical_mdr_api.models.activities.activity_sub_group import (
    ActivitySubGroup,
    ActivitySubGroupCreateInput,
)
from clinical_mdr_api.models.biomedical_concepts.activity_instance_class import (
    ActivityInstanceClass,
    ActivityInstanceClassInput,
)
from clinical_mdr_api.models.biomedical_concepts.activity_item import (
    ActivityItem,
    ActivityItemCreateInput,
)
from clinical_mdr_api.models.biomedical_concepts.activity_item_class import (
    ActivityItemClass,
    ActivityItemClassCreateInput,
)
from clinical_mdr_api.models.compound import Compound, CompoundCreateInput
from clinical_mdr_api.models.compound_alias import (
    CompoundAlias,
    CompoundAliasCreateInput,
)
from clinical_mdr_api.models.concept import TextValue, TextValueInput
from clinical_mdr_api.models.configuration import CTConfigPostInput
from clinical_mdr_api.models.standard_data_models.class_variable import ClassVariable
from clinical_mdr_api.models.standard_data_models.data_model import DataModel
from clinical_mdr_api.models.standard_data_models.data_model_ig import DataModelIG
from clinical_mdr_api.models.standard_data_models.dataset import Dataset
from clinical_mdr_api.models.standard_data_models.dataset_class import DatasetClass
from clinical_mdr_api.models.standard_data_models.dataset_variable import (
    DatasetVariable,
)
from clinical_mdr_api.models.study import Study, StudyCreateInput
from clinical_mdr_api.models.study_disease_milestone import (
    StudyDiseaseMilestone,
    StudyDiseaseMilestoneCreateInput,
)
from clinical_mdr_api.models.study_epoch import StudyEpoch, StudyEpochCreateInput
from clinical_mdr_api.models.study_selection import (
    EndpointUnitsInput,
    StudyActivitySchedule,
    StudyActivityScheduleCreateInput,
    StudyCompoundDosing,
    StudyCompoundDosingInput,
    StudyDesignCell,
    StudyDesignCellCreateInput,
    StudySelectionArm,
    StudySelectionArmCreateInput,
    StudySelectionCompound,
    StudySelectionCompoundInput,
    StudySelectionCriteria,
    StudySelectionCriteriaCreateInput,
    StudySelectionElement,
    StudySelectionElementCreateInput,
    StudySelectionEndpoint,
    StudySelectionEndpointCreateInput,
    StudySelectionObjective,
    StudySelectionObjectiveCreateInput,
)
from clinical_mdr_api.models.syntax_instances.criteria import CriteriaCreateInput
from clinical_mdr_api.models.syntax_instances.endpoint import EndpointCreateInput
from clinical_mdr_api.models.syntax_instances.objective import ObjectiveCreateInput
from clinical_mdr_api.models.syntax_instances.timeframe import (
    Timeframe,
    TimeframeCreateInput,
)
from clinical_mdr_api.models.syntax_pre_instances.activity_instruction_pre_instance import (
    ActivityInstructionPreInstance,
    ActivityInstructionPreInstanceCreateInput,
)
from clinical_mdr_api.models.syntax_pre_instances.criteria_pre_instance import (
    CriteriaPreInstance,
    CriteriaPreInstanceCreateInput,
)
from clinical_mdr_api.models.syntax_pre_instances.endpoint_pre_instance import (
    EndpointPreInstance,
    EndpointPreInstanceCreateInput,
)
from clinical_mdr_api.models.syntax_pre_instances.objective_pre_instance import (
    ObjectivePreInstance,
    ObjectivePreInstanceCreateInput,
)
from clinical_mdr_api.models.syntax_templates.activity_instruction_template import (
    ActivityInstructionTemplate,
    ActivityInstructionTemplateCreateInput,
)
from clinical_mdr_api.models.syntax_templates.criteria_template import (
    CriteriaTemplate,
    CriteriaTemplateCreateInput,
)
from clinical_mdr_api.models.syntax_templates.endpoint_template import (
    EndpointTemplate,
    EndpointTemplateCreateInput,
)
from clinical_mdr_api.models.syntax_templates.objective_template import (
    ObjectiveTemplate,
    ObjectiveTemplateCreateInput,
)
from clinical_mdr_api.models.syntax_templates.timeframe_template import (
    TimeframeTemplate,
    TimeframeTemplateCreateInput,
)
from clinical_mdr_api.models.template_parameter_multi_select_input import (
    TemplateParameterMultiSelectInput,
)
from clinical_mdr_api.models.template_parameter_term import MultiTemplateParameterTerm
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.services import libraries as library_service
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services.biomedical_concepts.activity_instance_class import (
    ActivityInstanceClassService,
)
from clinical_mdr_api.services.biomedical_concepts.activity_item import (
    ActivityItemService,
)
from clinical_mdr_api.services.biomedical_concepts.activity_item_class import (
    ActivityItemClassService,
)
from clinical_mdr_api.services.brand import BrandService
from clinical_mdr_api.services.clinical_programme import (
    create as create_clinical_programme,
)
from clinical_mdr_api.services.concepts.activities.activity_group_service import (
    ActivityGroupService,
)
from clinical_mdr_api.services.concepts.activities.activity_instance_service import (
    ActivityInstanceService,
)
from clinical_mdr_api.services.concepts.activities.activity_service import (
    ActivityService,
)
from clinical_mdr_api.services.concepts.activities.activity_sub_group_service import (
    ActivitySubGroupService,
)
from clinical_mdr_api.services.concepts.compound_alias_service import (
    CompoundAliasService,
)
from clinical_mdr_api.services.concepts.compound_service import CompoundService
from clinical_mdr_api.services.concepts.simple_concepts.lag_time import LagTimeService
from clinical_mdr_api.services.concepts.simple_concepts.numeric_value_with_unit import (
    NumericValueWithUnitService,
)
from clinical_mdr_api.services.concepts.simple_concepts.text_value import (
    TextValueService,
)
from clinical_mdr_api.services.configuration import CTConfigService
from clinical_mdr_api.services.ct_codelist import CTCodelistService
from clinical_mdr_api.services.ct_codelist_attributes import CTCodelistAttributesService
from clinical_mdr_api.services.ct_codelist_name import CTCodelistNameService
from clinical_mdr_api.services.ct_term import CTTermService
from clinical_mdr_api.services.ct_term_attributes import CTTermAttributesService
from clinical_mdr_api.services.ct_term_name import CTTermNameService
from clinical_mdr_api.services.dictionary_codelist_generic_service import (
    DictionaryCodelistGenericService as DictionaryCodelistService,
)
from clinical_mdr_api.services.dictionary_term_generic_service import (
    DictionaryTermGenericService as DictionaryTermService,
)
from clinical_mdr_api.services.project import ProjectService
from clinical_mdr_api.services.standard_data_models.class_variable import (
    ClassVariableService,
)
from clinical_mdr_api.services.standard_data_models.data_model import DataModelService
from clinical_mdr_api.services.standard_data_models.data_model_ig import (
    DataModelIGService,
)
from clinical_mdr_api.services.standard_data_models.dataset import DatasetService
from clinical_mdr_api.services.standard_data_models.dataset_class import (
    DatasetClassService,
)
from clinical_mdr_api.services.standard_data_models.dataset_variable import (
    DatasetVariableService,
)
from clinical_mdr_api.services.study import StudyService
from clinical_mdr_api.services.study_activity_schedule import (
    StudyActivityScheduleService,
)
from clinical_mdr_api.services.study_arm_selection import StudyArmSelectionService
from clinical_mdr_api.services.study_compound_dosing_selection import (
    StudyCompoundDosingSelectionService,
)
from clinical_mdr_api.services.study_compound_selection import (
    StudyCompoundSelectionService,
)
from clinical_mdr_api.services.study_criteria_selection import (
    StudyCriteriaSelectionService,
)
from clinical_mdr_api.services.study_design_cell import StudyDesignCellService
from clinical_mdr_api.services.study_disease_milestone import (
    StudyDiseaseMilestoneService,
)
from clinical_mdr_api.services.study_element_selection import (
    StudyElementSelectionService,
)
from clinical_mdr_api.services.study_endpoint_selection import (
    StudyEndpointSelectionService,
)
from clinical_mdr_api.services.study_epoch import StudyEpochService
from clinical_mdr_api.services.study_objective_selection import (
    StudyObjectiveSelectionService,
)
from clinical_mdr_api.services.syntax_instances.timeframes import TimeframeService
from clinical_mdr_api.services.syntax_pre_instances.activity_instruction_pre_instances import (
    ActivityInstructionPreInstanceService,
)
from clinical_mdr_api.services.syntax_pre_instances.criteria_pre_instances import (
    CriteriaPreInstanceService,
)
from clinical_mdr_api.services.syntax_pre_instances.endpoint_pre_instances import (
    EndpointPreInstanceService,
)
from clinical_mdr_api.services.syntax_pre_instances.objective_pre_instances import (
    ObjectivePreInstanceService,
)
from clinical_mdr_api.services.syntax_templates.activity_instruction_templates import (
    ActivityInstructionTemplateService,
)
from clinical_mdr_api.services.syntax_templates.criteria_templates import (
    CriteriaTemplateService,
)
from clinical_mdr_api.services.syntax_templates.endpoint_templates import (
    EndpointTemplateService,
)
from clinical_mdr_api.services.syntax_templates.objective_templates import (
    ObjectiveTemplateService,
)
from clinical_mdr_api.services.syntax_templates.timeframe_templates import (
    TimeframeTemplateService,
)
from clinical_mdr_api.services.unit_definition import UnitDefinitionService
from clinical_mdr_api.tests.unit.domain.study_definition_aggregate.test_study_metadata import (
    initialize_ct_data_map,
)

log = logging.getLogger(__name__)

AUTHOR = "test"
STUDY_UID = "study_root"
PROJECT_NUMBER = "123"
LIBRARY_NAME = "Sponsor"
REQUESTED_LIBRARY_NAME = "Requested"
CDISC_LIBRARY_NAME = "CDISC"
CT_CATALOGUE_NAME = "SDTM CT"
CT_CODELIST_NAME = "CT Codelist"
CT_CODELIST_UID = "C66737"
CT_CODELIST_LIBRARY = "CDISC"
DICTIONARY_CODELIST_NAME = "UCUM"
DICTIONARY_CODELIST_LIBRARY = "UCUM"


class TestUtils:
    """Class containg methods that create all kinds of entities, e.g. library compounds"""

    @classmethod
    def assert_timestamp_is_in_utc_zone(cls, val: str):
        ts: datetime = datetime.strptime(val, config.DATE_TIME_FORMAT)
        assert ts.tzinfo == timezone.utc

    @classmethod
    def assert_timestamp_is_newer_than(cls, val: str, seconds: int):
        ts: datetime = datetime.strptime(val, config.DATE_TIME_FORMAT)
        assert abs(datetime.now(timezone.utc) - ts) < timedelta(seconds=seconds)

    @classmethod
    def assert_valid_csv(cls, val: str):
        csv_file = io.StringIO(val)
        try:
            csv_reader = csv.reader(csv_file)
            for _row in csv_reader:
                pass  # Do nothing, just iterate through the rows
        except csv.Error:
            assert False, "Returned content is not a valid CSV file"

    @classmethod
    def assert_valid_xml(cls, val: str):
        # Attempt to parse the XML content using ElementTree
        try:
            _root = ElementTree.fromstring(val)
        except ElementTree.ParseError:
            assert False, "Content is not valid XML"

    @classmethod
    def assert_valid_excel(cls, content):
        excel_file = io.BytesIO(content)
        # Attempt to open the Excel file using openpyxl
        try:
            _workbook = openpyxl.load_workbook(excel_file)
        except openpyxl.utils.exceptions.InvalidFileException:
            assert False, "File does not contain valid Excel data"

    @classmethod
    def verify_exported_data_format(
        cls, api_client: TestClient, export_format: str, url: str
    ):
        """Verifies that the specified endpoint returns valid csv/xml/Excel content"""
        headers = {"Accept": export_format}
        log.info("GET %s | %s", url, headers)
        response = api_client.get(url, headers=headers)

        assert response.status_code == 200
        assert export_format in response.headers["content-type"]

        if export_format == "text/csv":
            TestUtils.assert_valid_csv(response.content.decode("utf-8"))
        if export_format == "text/xml":
            TestUtils.assert_valid_xml(response.content.decode("utf-8"))
        if (
            export_format
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            TestUtils.assert_valid_excel(response.content)

    @classmethod
    def random_str(cls, max_length: int, prefix: str = ""):
        return prefix + str(randint(1, 10**max_length - 1))

    @classmethod
    def random_if_none(cls, val, max_length: int = 10, prefix: str = ""):
        """Return supplied `val` if its value is not None.
        Otherwise return random string with optional prefix."""
        return val if val else cls.random_str(max_length, prefix)

    # region Syntax templates
    @classmethod
    def create_template_parameter(cls, name: str) -> None:
        db.cypher_query(f"CREATE (:TemplateParameter {{name:'{name}'}})")

    @classmethod
    def set_final_props(cls, final_variable):
        return f""" SET {final_variable} = {{
        change_description: "Approved version",
        start_date: datetime("2020-06-26T00:00:00"),
        status: "Final",
        user_initials: "TODO initials",
        version: "1.0"
    }} """

    @classmethod
    def create_text_value(
        cls,
        library_name: Optional[str] = LIBRARY_NAME,
        name: Optional[str] = None,
        name_sentence_case: Optional[str] = None,
        definition: Optional[str] = None,
        abbreviation: Optional[str] = None,
        template_parameter: Optional[bool] = True,
    ) -> TextValue:
        service = TextValueService()
        payload: TextValueInput = TextValueInput(
            name=cls.random_if_none(name, prefix="name-"),
            name_sentence_case=cls.random_if_none(
                name_sentence_case, prefix="name_sentence_case-"
            ),
            definition=cls.random_if_none(definition, prefix="def-"),
            abbreviation=cls.random_if_none(abbreviation, prefix="abbr-"),
            library_name=library_name,
            template_parameter=template_parameter,
        )

        result: TextValue = service.create(payload)
        return result

    @classmethod
    def create_objective_template(
        cls,
        name: Optional[str] = None,
        guidance_text: Optional[str] = None,
        study_uid: Optional[str] = None,
        library_name: Optional[str] = LIBRARY_NAME,
        default_parameter_terms: Optional[List[MultiTemplateParameterTerm]] = None,
        indication_uids: Optional[List[str]] = None,
        is_confirmatory_testing: Optional[bool] = False,
        category_uids: Optional[List[str]] = None,
        approve: bool = True,
    ) -> ObjectiveTemplate:
        service = ObjectiveTemplateService()
        payload: ObjectiveTemplateCreateInput = ObjectiveTemplateCreateInput(
            name=cls.random_if_none(name, prefix="ot-"),
            guidance_text=guidance_text,
            study_uid=study_uid,
            library_name=library_name,
            default_parameter_terms=default_parameter_terms,
            indication_uids=indication_uids,
            is_confirmatory_testing=is_confirmatory_testing,
            category_uids=category_uids,
        )

        result: ObjectiveTemplate = service.create(payload)
        if approve:
            service.approve(result.uid)
        return result

    @classmethod
    def create_endpoint_template(
        cls,
        name: Optional[str] = None,
        guidance_text: Optional[str] = None,
        study_uid: Optional[str] = None,
        library_name: Optional[str] = LIBRARY_NAME,
        default_parameter_terms: Optional[List[MultiTemplateParameterTerm]] = None,
        indication_uids: Optional[List[str]] = None,
        is_confirmatory_testing: Optional[bool] = False,
        category_uids: Optional[List[str]] = None,
        sub_category_uids: Optional[List[str]] = None,
        approve: bool = True,
    ) -> EndpointTemplate:
        service = EndpointTemplateService()
        payload: EndpointTemplateCreateInput = EndpointTemplateCreateInput(
            name=cls.random_if_none(name, prefix="et-"),
            guidance_text=guidance_text,
            study_uid=study_uid,
            library_name=library_name,
            default_parameter_terms=default_parameter_terms,
            indication_uids=indication_uids,
            is_confirmatory_testing=is_confirmatory_testing,
            category_uids=category_uids,
            sub_category_uids=sub_category_uids,
        )

        result: ObjectiveTemplate = service.create(payload)
        if approve:
            service.approve(result.uid)
        return result

    @classmethod
    def create_activity_instruction_template(
        cls,
        name: Optional[str] = None,
        guidance_text: Optional[str] = None,
        library_name: Optional[str] = LIBRARY_NAME,
        default_parameter_terms: Optional[List[MultiTemplateParameterTerm]] = None,
        indication_uids: Optional[List[str]] = None,
        activity_uids: Optional[List[str]] = None,
        activity_group_uids: Optional[List[str]] = None,
        activity_subgroup_uids: Optional[List[str]] = None,
        approve: bool = True,
    ) -> ActivityInstructionTemplate:
        service = ActivityInstructionTemplateService()
        payload: ActivityInstructionTemplateCreateInput = (
            ActivityInstructionTemplateCreateInput(
                name=cls.random_if_none(name, prefix="ct-"),
                guidance_text=cls.random_if_none(guidance_text),
                library_name=library_name,
                default_parameter_terms=default_parameter_terms,
                indication_uids=indication_uids,
                activity_uids=activity_uids,
                activity_group_uids=activity_group_uids,
                activity_subgroup_uids=activity_subgroup_uids,
            )
        )

        result: ActivityInstructionTemplate = service.create(payload)
        if approve:
            service.approve(result.uid)
        return result

    @classmethod
    def create_criteria_template(
        cls,
        name: Optional[str] = None,
        guidance_text: Optional[str] = None,
        study_uid: Optional[str] = None,
        library_name: Optional[str] = LIBRARY_NAME,
        default_parameter_terms: Optional[List[MultiTemplateParameterTerm]] = None,
        type_uid: Optional[str] = None,
        indication_uids: Optional[List[str]] = None,
        category_uids: Optional[List[str]] = None,
        sub_category_uids: Optional[List[str]] = None,
        approve: bool = True,
    ) -> CriteriaTemplate:
        service = CriteriaTemplateService()
        payload: CriteriaTemplateCreateInput = CriteriaTemplateCreateInput(
            name=cls.random_if_none(name, prefix="ct-"),
            guidance_text=cls.random_if_none(guidance_text),
            study_uid=study_uid,
            library_name=library_name,
            default_parameter_terms=default_parameter_terms,
            type_uid=type_uid,
            indication_uids=indication_uids,
            category_uids=category_uids,
            sub_category_uids=sub_category_uids,
        )

        result: CriteriaTemplate = service.create(payload)
        if approve:
            service.approve(result.uid)
        return result

    @classmethod
    def create_timeframe_template(
        cls,
        name: Optional[str] = None,
        guidance_text: Optional[str] = None,
        library_name: Optional[str] = LIBRARY_NAME,
        approve: bool = True,
    ) -> TimeframeTemplate:
        service = TimeframeTemplateService()
        payload: TimeframeTemplateCreateInput = TimeframeTemplateCreateInput(
            name=cls.random_if_none(name, prefix="tt-"),
            guidance_text=guidance_text,
            library_name=library_name,
        )

        result: TimeframeTemplate = service.create(payload)
        if approve:
            service.approve(result.uid)
        return result

    # endregion

    @classmethod
    def create_activity_instruction_pre_instance(
        cls,
        template_uid: Optional[str] = None,
        parameter_terms: Optional[List[MultiTemplateParameterTerm]] = None,
        indication_uids: Optional[List[str]] = None,
        activity_uids: Optional[List[str]] = None,
        activity_group_uids: Optional[List[str]] = None,
        activity_subgroup_uids: Optional[List[str]] = None,
        library_name: Optional[str] = LIBRARY_NAME,
    ) -> ActivityInstructionPreInstance:
        if not template_uid:
            activity_group_uid = cls.create_activity_group(name="test").uid
            template_uid = cls.create_activity_instruction_template(
                name="name",
                guidance_text="guidance text",
                library_name="Sponsor",
                default_parameter_terms=[],
                indication_uids=[],
                activity_uids=[],
                activity_group_uids=[activity_group_uid],
                activity_subgroup_uids=[
                    cls.create_activity_subgroup(
                        name="test", activity_group=activity_group_uid
                    ).uid
                ],
                approve=False,
            ).uid

        service = ActivityInstructionPreInstanceService()
        payload: ActivityInstructionPreInstanceCreateInput = (
            ActivityInstructionPreInstanceCreateInput(
                library_name=library_name,
                parameter_terms=parameter_terms,
                indication_uids=indication_uids,
                activity_uids=activity_uids,
                activity_group_uids=activity_group_uids,
                activity_subgroup_uids=activity_subgroup_uids,
            )
        )

        result: ActivityInstructionPreInstance = service.create(
            payload, template_uid=template_uid
        )
        return result

    @classmethod
    def create_endpoint_pre_instance(
        cls,
        template_uid: Optional[str] = None,
        parameter_terms: Optional[List[MultiTemplateParameterTerm]] = None,
        indication_uids: Optional[List[str]] = None,
        category_uids: Optional[List[str]] = None,
        sub_category_uids: Optional[List[str]] = None,
        library_name: Optional[str] = LIBRARY_NAME,
    ) -> EndpointPreInstance:
        if not template_uid:
            template_uid = cls.create_endpoint_template(
                name="name",
                guidance_text="guidance text",
                study_uid=None,
                library_name="Sponsor",
                default_parameter_terms=[],
                indication_uids=[],
                category_uids=[],
                sub_category_uids=[],
            ).uid

        service = EndpointPreInstanceService()
        payload: EndpointPreInstanceCreateInput = EndpointPreInstanceCreateInput(
            library_name=library_name,
            parameter_terms=parameter_terms,
            indication_uids=indication_uids,
            category_uids=category_uids,
            sub_category_uids=sub_category_uids,
        )

        result: EndpointPreInstance = service.create(payload, template_uid=template_uid)
        return result

    @classmethod
    def create_objective_pre_instance(
        cls,
        template_uid: Optional[str] = None,
        is_confirmatory_testing: Optional[bool] = None,
        parameter_terms: Optional[List[MultiTemplateParameterTerm]] = None,
        indication_uids: Optional[List[str]] = None,
        category_uids: Optional[List[str]] = None,
        library_name: Optional[str] = LIBRARY_NAME,
    ) -> ObjectivePreInstance:
        if not template_uid:
            template_uid = cls.create_objective_template(
                name="name",
                guidance_text="guidance text",
                study_uid=None,
                library_name="Sponsor",
                default_parameter_terms=[],
                indication_uids=[],
                category_uids=[],
            ).uid

        service = ObjectivePreInstanceService()
        payload: ObjectivePreInstanceCreateInput = ObjectivePreInstanceCreateInput(
            library_name=library_name,
            is_confirmatory_testing=is_confirmatory_testing,
            parameter_terms=parameter_terms,
            indication_uids=indication_uids,
            category_uids=category_uids,
        )

        result: ObjectivePreInstance = service.create(
            payload, template_uid=template_uid
        )
        return result

    @classmethod
    def create_criteria_pre_instance(
        cls,
        template_uid: Optional[str] = None,
        parameter_terms: Optional[List[MultiTemplateParameterTerm]] = None,
        indication_uids: Optional[List[str]] = None,
        category_uids: Optional[List[str]] = None,
        sub_category_uids: Optional[List[str]] = None,
        library_name: Optional[str] = LIBRARY_NAME,
    ) -> CriteriaPreInstance:
        if not template_uid:
            template_uid = cls.create_criteria_template(
                name="name",
                guidance_text="guidance text",
                study_uid=None,
                library_name="Sponsor",
                default_parameter_terms=[],
                indication_uids=[],
                category_uids=[],
            ).uid

        service = CriteriaPreInstanceService()
        payload: CriteriaPreInstanceCreateInput = CriteriaPreInstanceCreateInput(
            library_name=library_name,
            parameter_terms=parameter_terms,
            indication_uids=indication_uids,
            category_uids=category_uids,
            sub_category_uids=sub_category_uids,
        )

        result: CriteriaPreInstance = service.create(payload, template_uid=template_uid)
        return result

    @classmethod
    def create_compound(
        cls,
        name=None,
        name_sentence_case=None,
        definition=None,
        abbreviation=None,
        library_name=LIBRARY_NAME,
        analyte_number=None,
        nnc_long_number=None,
        nnc_short_number=None,
        is_sponsor_compound=True,
        is_name_inn=False,
        substance_terms_uids=None,
        dose_values_uids=None,
        lag_times_uids=None,
        strength_values_uids=None,
        delivery_devices_uids=None,
        dispensers_uids=None,
        projects_uids=None,
        brands_uids=None,
        dose_frequency_uids=None,
        dosage_form_uids=None,
        route_of_administration_uids=None,
        half_life_uid=None,
    ) -> Compound:
        service = CompoundService()
        payload: CompoundCreateInput = CompoundCreateInput(
            name=cls.random_if_none(name, prefix="name-"),
            name_sentence_case=cls.random_if_none(
                name_sentence_case, prefix="name_sentence_case-"
            ),
            definition=cls.random_if_none(definition, prefix="definition-"),
            abbreviation=cls.random_if_none(abbreviation, prefix="abbreviation-"),
            library_name=library_name,
            analyte_number=cls.random_if_none(analyte_number, prefix="analyte_number-"),
            nnc_long_number=cls.random_if_none(
                nnc_long_number, prefix="nnc_long_number-"
            ),
            nnc_short_number=cls.random_if_none(
                nnc_short_number, prefix="nnc_short_number-"
            ),
            is_sponsor_compound=is_sponsor_compound if is_sponsor_compound else True,
            is_name_inn=is_name_inn if is_name_inn else False,
            substance_terms_uids=substance_terms_uids if substance_terms_uids else [],
            dose_values_uids=dose_values_uids if dose_values_uids else [],
            lag_times_uids=lag_times_uids if lag_times_uids else [],
            strength_values_uids=strength_values_uids if strength_values_uids else [],
            delivery_devices_uids=delivery_devices_uids
            if delivery_devices_uids
            else [],
            dispensers_uids=dispensers_uids if dispensers_uids else [],
            projects_uids=projects_uids if projects_uids else [],
            brands_uids=brands_uids if brands_uids else [],
            dose_frequency_uids=dose_frequency_uids if dose_frequency_uids else [],
            dosage_form_uids=dosage_form_uids if dosage_form_uids else [],
            route_of_administration_uids=route_of_administration_uids
            if route_of_administration_uids
            else [],
            half_life_uid=half_life_uid if half_life_uid else None,
        )

        result: Compound = service.create(payload)
        return result

    @classmethod
    def create_compound_alias(
        cls,
        name=None,
        name_sentence_case=None,
        definition=None,
        abbreviation=None,
        library_name=LIBRARY_NAME,
        is_preferred_synonym=None,
        compound_uid=None,
    ) -> CompoundAlias:
        service = CompoundAliasService()
        payload: CompoundAliasCreateInput = CompoundAliasCreateInput(
            name=cls.random_if_none(name, prefix="name-"),
            name_sentence_case=cls.random_if_none(
                name_sentence_case, prefix="name_sentence_case-"
            ),
            definition=cls.random_if_none(definition, prefix="definition-"),
            abbreviation=cls.random_if_none(abbreviation, prefix="abbreviation-"),
            library_name=library_name,
            is_preferred_synonym=is_preferred_synonym
            if is_preferred_synonym
            else False,
            compound_uid=compound_uid if compound_uid else None,
        )

        result: CompoundAlias = service.create(payload)
        return result

    @classmethod
    def create_activity_instance(
        cls,
        name: str,
        activity_instance_class_uid: str,
        name_sentence_case: Optional[str] = None,
        topic_code: Optional[str] = None,
        adam_param_code: Optional[str] = None,
        legacy_description: Optional[bool] = None,
        activities: Optional[Sequence] = None,
        activity_item_uids: Optional[Sequence] = None,
        library_name: Optional[str] = LIBRARY_NAME,
        approve: bool = True,
    ) -> ActivityInstanceClass:
        service = ActivityInstanceService()
        activity_instance_input: ActivityInstanceCreateInput = (
            ActivityInstanceCreateInput(
                name=name,
                name_sentence_case=name_sentence_case,
                topic_code=topic_code,
                adam_param_code=adam_param_code,
                legacy_description=legacy_description,
                activities=activities if activities else [],
                activity_instance_class_uid=activity_instance_class_uid,
                activity_item_uids=activity_item_uids if activity_item_uids else [],
                library_name=library_name,
            )
        )
        result: ActivityInstance = service.create(concept_input=activity_instance_input)
        if approve:
            service.approve(result.uid)
        return result

    @classmethod
    def create_activity_instance_class(
        cls,
        name: str,
        order: Optional[int] = None,
        definition: Optional[str] = None,
        is_domain_specific: Optional[bool] = None,
        parent_uid: Optional[str] = None,
        library_name: Optional[str] = LIBRARY_NAME,
        approve: bool = True,
    ) -> ActivityInstanceClass:
        service = ActivityInstanceClassService()
        activity_instance_class_input: ActivityInstanceClassInput = (
            ActivityInstanceClassInput(
                name=name,
                order=order,
                definition=definition,
                is_domain_specific=is_domain_specific,
                parent_uid=parent_uid,
                library_name=library_name,
            )
        )
        result: ActivityInstanceClass = service.create(
            item_input=activity_instance_class_input
        )
        if approve:
            service.approve(result.uid)
        return result

    @classmethod
    def create_activity_item_class(
        cls,
        name: str,
        order: int,
        mandatory: bool,
        activity_instance_class_uids: List[str],
        library_name: Optional[str] = LIBRARY_NAME,
        approve: bool = True,
    ) -> ActivityItemClass:
        service = ActivityItemClassService()
        activity_item_class_input: ActivityItemClassCreateInput = (
            ActivityItemClassCreateInput(
                name=name,
                order=order,
                mandatory=mandatory,
                activity_instance_class_uids=activity_instance_class_uids,
                library_name=library_name,
            )
        )
        result: ActivityItemClass = service.create(item_input=activity_item_class_input)
        if approve:
            service.approve(result.uid)
        return result

    @classmethod
    def create_activity_item(
        cls,
        name: str,
        activity_item_class_uid: str,
        ct_term_uid: Optional[str] = None,
        unit_definition_uid: Optional[str] = None,
        library_name: Optional[str] = LIBRARY_NAME,
        approve: bool = True,
    ) -> ActivityItem:
        service = ActivityItemService()
        activity_item_input: ActivityItemCreateInput = ActivityItemCreateInput(
            name=name,
            activity_item_class_uid=activity_item_class_uid,
            ct_term_uid=ct_term_uid,
            unit_definition_uid=unit_definition_uid,
            library_name=library_name,
        )
        result: ActivityItem = service.create(item_input=activity_item_input)
        if approve:
            service.approve(result.uid)
        return result

    @classmethod
    def create_activity(
        cls,
        name: str,
        name_sentence_case: Optional[str] = None,
        definition: Optional[str] = None,
        abbreviation: Optional[str] = None,
        activity_subgroup: Optional[str] = None,
        request_rationale: Optional[str] = None,
        library_name: Optional[str] = LIBRARY_NAME,
        approve: bool = True,
    ) -> Activity:
        service = ActivityService()
        activity_create_input: ActivityCreateInput = ActivityCreateInput(
            name=name,
            name_sentence_case=name_sentence_case,
            definition=definition,
            abbreviation=abbreviation,
            activity_subgroup=activity_subgroup,
            request_rationale=request_rationale,
            library_name=library_name,
        )
        result: Activity = service.create(concept_input=activity_create_input)
        if approve:
            service.approve(result.uid)
        return result

    @classmethod
    def create_activity_subgroup(
        cls,
        name: str,
        activity_group: str,
        name_sentence_case: Optional[str] = None,
        definition: Optional[str] = None,
        abbreviation: Optional[str] = None,
        library_name: Optional[str] = LIBRARY_NAME,
        approve: bool = True,
    ) -> ActivitySubGroup:
        service = ActivitySubGroupService()
        activity_subgroup_create_input: ActivitySubGroupCreateInput = (
            ActivitySubGroupCreateInput(
                name=name,
                name_sentence_case=name_sentence_case,
                definition=definition,
                abbreviation=abbreviation,
                activity_group=activity_group,
                library_name=library_name,
            )
        )
        result: ActivitySubGroup = service.create(
            concept_input=activity_subgroup_create_input
        )
        if approve:
            service.approve(result.uid)
        return result

    @classmethod
    def create_activity_group(
        cls,
        name: str,
        name_sentence_case: Optional[str] = None,
        definition: Optional[str] = None,
        abbreviation: Optional[str] = None,
        library_name: Optional[str] = LIBRARY_NAME,
        approve: bool = True,
    ) -> ActivityGroup:
        service = ActivityGroupService()
        activity_group_create_input: ActivityGroupCreateInput = (
            ActivityGroupCreateInput(
                name=name,
                name_sentence_case=name_sentence_case,
                definition=definition,
                abbreviation=abbreviation,
                library_name=library_name,
            )
        )
        result: ActivityGroup = service.create(
            concept_input=activity_group_create_input
        )
        if approve:
            service.approve(result.uid)
        return result

    @classmethod
    def create_study_activity_schedule(
        cls,
        study_uid: str,
        study_activity_uid: str,
        study_visit_uid: str,
        note: Optional[str] = None,
    ) -> StudyActivitySchedule:
        service = StudyActivityScheduleService(author="test")
        study_activity_schedule: StudyActivityScheduleCreateInput = (
            StudyActivityScheduleCreateInput(
                study_activity_uid=study_activity_uid,
                study_visit_uid=study_visit_uid,
                note=note,
            )
        )
        schedule = service.create(
            study_uid=study_uid,
            schedule_input=study_activity_schedule,
        )
        return schedule

    # region Study selection
    @classmethod
    def _complete_parameter_terms(
        cls, parameter_terms: List[TemplateParameterMultiSelectInput]
    ):
        for value in parameter_terms:
            if value.conjunction is None:
                value.conjunction = ""
        return parameter_terms

    @classmethod
    def create_study_objective(
        cls,
        study_uid: str,
        objective_template_uid: str,
        library_name: Optional[str] = LIBRARY_NAME,
        objective_level_uid: Optional[str] = None,
        parameter_terms: Optional[List[TemplateParameterMultiSelectInput]] = None,
    ) -> StudySelectionObjective:
        service = StudyObjectiveSelectionService(AUTHOR)
        objective_create_input: StudySelectionObjectiveCreateInput = (
            StudySelectionObjectiveCreateInput(
                objective_level_uid=objective_level_uid,
                objective_data=ObjectiveCreateInput(
                    objective_template_uid=objective_template_uid,
                    library_name=library_name,
                    parameter_terms=cls._complete_parameter_terms(parameter_terms),
                ),
            )
        )

        result: StudySelectionObjective = service.make_selection_create_objective(
            study_uid=study_uid, selection_create_input=objective_create_input
        )
        return result

    @classmethod
    def create_study_endpoint(
        cls,
        study_uid: str,
        endpoint_template_uid: str,
        library_name: Optional[str] = LIBRARY_NAME,
        study_objective_uid: Optional[str] = None,
        endpoint_level_uid: Optional[str] = None,
        endpoint_sublevel_uid: Optional[str] = None,
        parameter_terms: Optional[List[TemplateParameterMultiSelectInput]] = None,
        endpoint_units: Optional[EndpointUnitsInput] = None,
        timeframe_uid: Optional[str] = None,
    ) -> StudySelectionEndpoint:
        service = StudyEndpointSelectionService(AUTHOR)
        if parameter_terms is None:
            parameter_terms = []
        endpoint_create_input: StudySelectionEndpointCreateInput = (
            StudySelectionEndpointCreateInput(
                study_objective_uid=study_objective_uid,
                endpoint_level_uid=endpoint_level_uid,
                endpoint_sublevel_uid=endpoint_sublevel_uid,
                endpoint_data=EndpointCreateInput(
                    endpoint_template_uid=endpoint_template_uid,
                    library_name=library_name,
                    parameter_terms=cls._complete_parameter_terms(parameter_terms),
                ),
                endpoint_units=endpoint_units,
                timeframe_uid=timeframe_uid,
            )
        )

        result: StudySelectionEndpoint = service.make_selection_create_endpoint(
            study_uid=study_uid, selection_create_input=endpoint_create_input
        )
        return result

    @classmethod
    def create_study_criteria(
        cls,
        study_uid: str,
        criteria_template_uid: str,
        library_name: Optional[str] = LIBRARY_NAME,
        parameter_terms: Optional[List[TemplateParameterMultiSelectInput]] = None,
    ) -> StudySelectionCriteria:
        service = StudyCriteriaSelectionService(AUTHOR)
        if parameter_terms is None:
            parameter_terms = []
        criteria_create_input: StudySelectionCriteriaCreateInput = (
            StudySelectionCriteriaCreateInput(
                criteria_data=CriteriaCreateInput(
                    criteria_template_uid=criteria_template_uid,
                    library_name=library_name,
                    parameter_terms=cls._complete_parameter_terms(parameter_terms),
                )
            )
        )

        result: StudySelectionCriteria = service.make_selection_create_criteria(
            study_uid=study_uid, selection_create_input=criteria_create_input
        )
        return result

    @classmethod
    def create_timeframe(
        cls,
        timeframe_template_uid: str,
        library_name: Optional[str] = LIBRARY_NAME,
        parameter_terms: Optional[List[TemplateParameterMultiSelectInput]] = None,
    ) -> Timeframe:
        service = TimeframeService(AUTHOR)
        if parameter_terms is None:
            parameter_terms = []
        timeframe_create_input: TimeframeCreateInput = TimeframeCreateInput(
            timeframe_template_uid=timeframe_template_uid,
            library_name=library_name,
            parameter_terms=cls._complete_parameter_terms(parameter_terms),
        )

        result: Timeframe = service.create(timeframe_create_input)
        return result

    @classmethod
    def create_study_compound(
        cls,
        study_uid: str,
        compound_alias_uid=None,
        type_of_treatment_uid=None,
        other_info=None,
        reason_for_missing_null_value_uid=None,
        device_uid=None,
        dispensed_in_uid=None,
        dosage_form_uid=None,
        route_of_administration_uid=None,
        strength_value_uid=None,
    ) -> StudySelectionCompound:
        service = StudyCompoundSelectionService(AUTHOR)
        payload: StudySelectionCompoundInput = StudySelectionCompoundInput(
            compound_alias_uid=compound_alias_uid,
            type_of_treatment_uid=type_of_treatment_uid,
            other_info=cls.random_if_none(other_info, prefix="other_info-"),
            reason_for_missing_null_value_uid=reason_for_missing_null_value_uid,
            device_uid=device_uid if device_uid else None,
            dispensed_in_uid=dispensed_in_uid if dispensed_in_uid else None,
            dosage_form_uid=dosage_form_uid if dosage_form_uid else None,
            route_of_administration_uid=route_of_administration_uid
            if route_of_administration_uid
            else None,
            strength_value_uid=strength_value_uid if strength_value_uid else None,
        )

        result: StudySelectionCompound = service.make_selection(
            study_uid=study_uid, selection_create_input=payload
        )
        return result

    @classmethod
    def create_study_compound_dosing(
        cls,
        study_uid: str,
        study_compound_uid=None,
        study_element_uid=None,
        dose_value_uid=None,
        dose_frequency_uid=None,
    ) -> StudyCompoundDosing:
        service = StudyCompoundDosingSelectionService(AUTHOR)
        payload: StudyCompoundDosingInput = StudyCompoundDosingInput(
            study_compound_uid=study_compound_uid,
            study_element_uid=study_element_uid,
            dose_value_uid=dose_value_uid,
            dose_frequency_uid=dose_frequency_uid,
        )

        result: StudyCompoundDosing = service.make_selection(
            study_uid=study_uid, selection_create_input=payload
        )
        return result

    @classmethod
    def create_study_element(
        cls,
        study_uid: str,
        name=None,
        short_name=None,
        code=None,
        description=None,
        planned_duration=None,
        start_rule=None,
        end_rule=None,
        element_colour=None,
        element_subtype_uid=None,
    ) -> StudySelectionElement:
        service = StudyElementSelectionService(AUTHOR)
        payload: StudySelectionElementCreateInput = StudySelectionElementCreateInput(
            name=name,
            short_name=short_name,
            code=code,
            description=description,
            planned_duration=planned_duration,
            start_rule=start_rule,
            end_rule=end_rule,
            element_colour=element_colour,
            element_subtype_uid=element_subtype_uid,
        )

        result: StudySelectionElement = service.make_selection(
            study_uid=study_uid, selection_create_input=payload
        )
        return result

    # endregion

    @classmethod
    def create_unit_definition(
        cls,
        name=None,
        library_name=LIBRARY_NAME,
        convertible_unit=False,
        display_unit=True,
        master_unit=False,
        si_unit=False,
        us_conventional_unit=False,
        ct_units=None,
        unit_subsets=None,
        ucum=None,
        unit_dimension=None,
        legacy_code=None,
        molecular_weight_conv_expon=0,
        conversion_factor_to_master=0.001,
        comment=None,
        order=None,
        definition=None,
        template_parameter=False,
        approve: bool = True,
    ) -> models.UnitDefinitionModel:
        user_id = AUTHOR
        service = UnitDefinitionService(
            user_id=user_id, meta_repository=MetaRepository(user_id)
        )

        payload: models.UnitDefinitionPostInput = models.UnitDefinitionPostInput(
            name=name,
            library_name=library_name,
            convertible_unit=convertible_unit,
            display_unit=display_unit,
            master_unit=master_unit,
            si_unit=si_unit,
            us_conventional_unit=us_conventional_unit,
            ct_units=ct_units if ct_units else [],
            unit_subsets=unit_subsets if unit_subsets else [],
            ucum=ucum,
            unit_dimension=unit_dimension,
            legacy_code=legacy_code,
            molecular_weight_conv_expon=molecular_weight_conv_expon,
            conversion_factor_to_master=conversion_factor_to_master,
            comment=comment,
            order=order,
            definition=definition,
            template_parameter=template_parameter,
        )

        result: models.UnitDefinitionModel = service.post(post_input=payload)
        if approve:
            service.approve(result.uid)
        return result

    @classmethod
    def create_library(cls, name: str = LIBRARY_NAME, is_editable: bool = True) -> dict:
        return library_service.create(name, is_editable)

    @classmethod
    def create_project(
        cls,
        name="Project ABC",
        project_number=PROJECT_NUMBER,
        description="Base project",
        clinical_programme_uid=None,
    ) -> models.Project:
        service = ProjectService()
        payload = models.ProjectCreateInput(
            name=name,
            project_number=project_number,
            description=description,
            clinical_programme_uid=clinical_programme_uid,
        )
        return service.create(payload)

    @classmethod
    def create_clinical_programme(cls, name: str = "CP") -> models.ClinicalProgramme:
        return create_clinical_programme(models.ClinicalProgrammeInput(name=name))

    @classmethod
    def create_study(
        cls,
        number: Optional[str] = None,
        acronym: Optional[str] = None,
        project_number: Optional[str] = PROJECT_NUMBER,
    ) -> Study:
        service = StudyService()
        payload = StudyCreateInput(
            study_number=cls.random_if_none(number, max_length=4),
            study_acronym=cls.random_if_none(acronym, prefix="st-"),
            project_number=project_number,
        )
        return service.create(payload)

    @classmethod
    def create_ct_term(
        cls,
        catalogue_name: str = CT_CATALOGUE_NAME,
        codelist_uid: str = CT_CODELIST_UID,
        code_submission_value: str = None,
        name_submission_value: str = None,
        nci_preferred_name: str = None,
        definition: str = None,
        sponsor_preferred_name: str = None,
        sponsor_preferred_name_sentence_case: str = None,
        order: int = None,
        library_name: str = CT_CODELIST_LIBRARY,
        approve: bool = True,
    ) -> models.CTTerm:
        service = CTTermService()
        payload = models.CTTermCreateInput(
            catalogue_name=catalogue_name,
            codelist_uid=codelist_uid,
            code_submission_value=cls.random_if_none(
                code_submission_value, prefix="code_submission_value-"
            ),
            name_submission_value=cls.random_if_none(
                name_submission_value, prefix="name_submission_value-"
            ),
            nci_preferred_name=cls.random_if_none(
                nci_preferred_name, prefix="nci_name-"
            ),
            definition=cls.random_if_none(definition, prefix="definition-"),
            sponsor_preferred_name=cls.random_if_none(
                sponsor_preferred_name, prefix="name-"
            ),
            sponsor_preferred_name_sentence_case=cls.random_if_none(
                sponsor_preferred_name_sentence_case,
                prefix="name_sent_case-",
            ),
            order=order,
            library_name=library_name,
        )
        ct_term: models.CTTerm = service.create(payload)
        if approve:
            CTTermAttributesService().approve(term_uid=ct_term.term_uid)
            CTTermNameService().approve(term_uid=ct_term.term_uid)
        return ct_term

    @classmethod
    def add_ct_term_parent(
        cls, term, parent, relationship_type: str = "type"
    ) -> models.CTTerm:
        service = CTTermService()
        service.add_parent(
            term_uid=term.term_uid,
            parent_uid=parent.term_uid,
            relationship_type=relationship_type,
        )

    @classmethod
    def create_ct_codelist(
        cls,
        catalogue_name: str = CT_CATALOGUE_NAME,
        name: str = CT_CODELIST_NAME,
        submission_value: str = None,
        nci_preferred_name: str = None,
        sponsor_preferred_name: str = None,
        definition: str = None,
        extensible: bool = False,
        template_parameter: bool = False,
        parent_codelist_uid: str = None,
        terms: Sequence[models.CTCodelistTermInput] = None,
        library_name: str = LIBRARY_NAME,
        approve: bool = False,
    ) -> models.CTCodelist:
        if terms is None:
            terms = []

        service = CTCodelistService()
        payload = models.CTCodelistCreateInput(
            catalogue_name=catalogue_name,
            name=cls.random_if_none(name, prefix="name-"),
            submission_value=cls.random_if_none(
                submission_value, prefix="submission_value-"
            ),
            nci_preferred_name=cls.random_if_none(
                nci_preferred_name, prefix="nci_name-"
            ),
            definition=cls.random_if_none(definition, prefix="definition-"),
            extensible=extensible,
            sponsor_preferred_name=cls.random_if_none(
                sponsor_preferred_name, prefix="name-"
            ),
            template_parameter=template_parameter,
            parent_codelist_uid=parent_codelist_uid,
            terms=terms,
            library_name=library_name,
        )
        result: CTCodelist = service.create(payload)
        if approve:
            CTCodelistNameService().approve(codelist_uid=result.codelist_uid)
            CTCodelistAttributesService().approve(codelist_uid=result.codelist_uid)
        return result

    @classmethod
    def create_dictionary_codelist(
        cls,
        name: Optional[str] = DICTIONARY_CODELIST_NAME,
        template_parameter: Optional[bool] = False,
        library_name: Optional[str] = DICTIONARY_CODELIST_LIBRARY,
        approve: Optional[bool] = True,
    ) -> models.DictionaryCodelist:
        service = DictionaryCodelistService()
        payload = models.DictionaryCodelistCreateInput(
            name=name, template_parameter=template_parameter, library_name=library_name
        )
        dictionary_codelist: models.DictionaryCodelist = service.create(payload)
        if approve:
            service.approve(dictionary_codelist.codelist_uid)
        return dictionary_codelist

    @classmethod
    def create_dictionary_term(
        cls,
        codelist_uid: str,
        dictionary_id: Optional[str] = None,
        name: Optional[str] = None,
        name_sentence_case: Optional[str] = None,
        abbreviation: Optional[str] = None,
        definition: Optional[str] = None,
        library_name: Optional[str] = DICTIONARY_CODELIST_LIBRARY,
        approve: Optional[bool] = True,
    ) -> models.DictionaryTerm:
        service = DictionaryTermService()
        target_name = cls.random_if_none(name, prefix="name-")
        payload = models.DictionaryTermCreateInput(
            codelist_uid=codelist_uid,
            dictionary_id=cls.random_if_none(dictionary_id, prefix="dict-"),
            name=target_name,
            name_sentence_case=name_sentence_case
            if name_sentence_case
            else target_name,
            abbreviation=cls.random_if_none(abbreviation, prefix="abbr-"),
            definition=cls.random_if_none(definition, prefix="definition-"),
            library_name=library_name,
        )
        dictionary_term: models.DictionaryTerm = service.create(payload)
        if approve:
            service.approve(dictionary_term.term_uid)
        return dictionary_term

    @classmethod
    def create_numeric_value_with_unit(
        cls,
        unit: str = None,
        name: str = None,
        name_sentence_case: str = None,
        definition: str = None,
        abbreviation: str = None,
        library_name: str = LIBRARY_NAME,
        template_parameter: bool = False,
        value: float = None,
        unit_definition_uid: str = None,
    ) -> models.NumericValueWithUnit:
        # First make sure that the specified unit exists
        if unit_definition_uid is None:
            try:
                unit_definition = cls.create_unit_definition(
                    name=unit,
                    library_name=library_name,
                    convertible_unit=False,
                    display_unit=True,
                    master_unit=False,
                    si_unit=True,
                    us_conventional_unit=True,
                    ct_units=[],
                    unit_subsets=[],
                    ucum=None,
                    unit_dimension=None,
                    legacy_code=None,
                    molecular_weight_conv_expon=0,
                    conversion_factor_to_master=0.001,
                    comment=unit,
                    order=0,
                    definition=unit,
                    template_parameter=True,
                    approve=True,
                )
                unit_definition_uid = unit_definition.uid
            except Exception as _:
                log.info("Unit '%s' already exists", unit)
                unit_definition_uid = cls.get_unit_uid_by_name(unit_name=unit)

        service = NumericValueWithUnitService()
        payload = models.NumericValueWithUnitInput(
            name=cls.random_if_none(name, prefix="name-"),
            name_sentence_case=cls.random_if_none(
                name_sentence_case, prefix="name_sentence_case-"
            ),
            definition=cls.random_if_none(definition, prefix="definition-"),
            abbreviation=cls.random_if_none(abbreviation, prefix="abbreviation-"),
            library_name=library_name,
            template_parameter=template_parameter,
            value=value,
            unit_definition_uid=unit_definition_uid,
        )

        result: models.NumericValueWithUnit = service.create(payload)
        return result

    @classmethod
    def create_lag_time(
        cls,
        unit: str = None,
        sdtm_domain_label: str = "Adverse Event Domain",
        name: str = None,
        name_sentence_case: str = None,
        definition: str = None,
        abbreviation: str = None,
        library_name: str = LIBRARY_NAME,
        template_parameter: bool = False,
        value: float = None,
        unit_definition_uid: str = None,
        sdtm_domain_uid: str = None,
    ) -> models.LagTime:
        # First make sure that the specified unit exists
        if unit_definition_uid is None:
            try:
                unit_definition = cls.create_unit_definition(
                    name=unit,
                    library_name=library_name,
                    convertible_unit=False,
                    display_unit=True,
                    master_unit=False,
                    si_unit=True,
                    us_conventional_unit=True,
                    ct_units=[],
                    unit_subsets=[],
                    ucum=None,
                    unit_dimension=None,
                    legacy_code=None,
                    molecular_weight_conv_expon=0,
                    conversion_factor_to_master=0.001,
                    comment=unit,
                    order=0,
                    definition=unit,
                    template_parameter=True,
                    approve=True,
                )
                unit_definition_uid = unit_definition.uid
            except Exception as _:
                log.info("Unit '%s' already exists", unit)
                unit_definition_uid = cls.get_unit_uid_by_name(unit_name=unit)

        # Make sure that the specified SDTM domain exists
        if sdtm_domain_uid is None:
            try:
                sdtm_domain: models.CTTerm = cls.create_ct_term(
                    sponsor_preferred_name=sdtm_domain_label, approve=True
                )
                sdtm_domain_uid = sdtm_domain.term_uid
            except Exception as _:
                log.info("SDTM domain '%s' already exists", sdtm_domain_label)
                sdtm_domains: GenericFilteringReturn[
                    models.CTTermNameAndAttributes
                ] = cls.get_ct_terms_by_name(name=sdtm_domain_label)
                sdtm_domain_uid = sdtm_domains.items[0].term_uid

        service = LagTimeService()
        payload = models.LagTimeInput(
            name=cls.random_if_none(name, prefix="name-"),
            name_sentence_case=cls.random_if_none(
                name_sentence_case, prefix="name_sentence_case-"
            ),
            definition=cls.random_if_none(definition, prefix="definition-"),
            abbreviation=cls.random_if_none(abbreviation, prefix="abbreviation-"),
            library_name=library_name,
            template_parameter=template_parameter,
            value=value,
            unit_definition_uid=unit_definition_uid,
            sdtm_domain_uid=sdtm_domain_uid,
        )

        result: models.NumericValueWithUnit = service.create(payload)
        return result

    @classmethod
    def get_unit_uid_by_name(cls, unit_name) -> str:
        unit_uid = MetaRepository().unit_definition_repository.find_uid_by_name(
            unit_name
        )
        return unit_uid

    @classmethod
    def get_unit_by_uid(
        cls,
        unit_uid: str,
        at_specified_datetime: Optional[datetime] = None,
        status: Optional[str] = None,
        version: Optional[str] = None,
    ) -> models.UnitDefinitionModel:
        return UnitDefinitionService(
            user_id=AUTHOR, meta_repository=MetaRepository(AUTHOR)
        ).get_by_uid(
            uid=unit_uid,
            at_specified_datetime=at_specified_datetime,
            status=status,
            version=version,
        )

    @classmethod
    def get_ct_terms_by_name(
        cls, name
    ) -> GenericFilteringReturn[models.CTTermNameAndAttributes]:
        return CTTermService().get_all_terms(
            codelist_name=None,
            codelist_uid=None,
            library=None,
            package=None,
            filter_by={"name.sponsor_preferred_name": {"v": [name]}},
        )

    @classmethod
    def create_brand(
        cls,
        name: str = None,
    ) -> models.Brand:
        service = BrandService()
        return service.create(models.BrandCreateInput(name=name))

    @classmethod
    def create_ct_catalogue(
        cls, library: str = LIBRARY_NAME, catalogue_name: str = CT_CATALOGUE_NAME
    ):
        create_catalogue_query = """
        MATCH (library:Library {name:$library_name})
        MERGE (catalogue:CTCatalogue {name:$catalogue_name})
        MERGE (library)-[:CONTAINS_CATALOGUE]->(catalogue)
        """
        db.cypher_query(
            create_catalogue_query,
            {
                "library_name": library,
                "catalogue_name": catalogue_name,
            },
        )
        return catalogue_name

    @classmethod
    def create_study_ct_data_map(
        cls,
        codelist_uid: str,
        # pylint: disable=dangerous-default-value
        ct_data_map: dict = initialize_ct_data_map,
        library_name: str = LIBRARY_NAME,
    ):
        dictionary_codelist = cls.create_dictionary_codelist()
        # used cypher below to manually assign uids related to CDISC concept_ids
        create_ct_term_with_custom_uid_query = """
            MATCH (codelist_root:CTCodelistRoot {uid:$codelist_uid})
            WITH codelist_root
            MERGE (term_root:CTTermRoot {uid: $uid})-[:HAS_NAME_ROOT]->(term_ver_root:CTTermNameRoot)-
                [:LATEST]->(term_ver_value:CTTermNameValue {name: $name, name_sentence_case: toLower($name)})
            MERGE (term_ver_root)-[final:LATEST_FINAL]->(term_ver_value)
            MERGE (term_ver_root)-[hasver:HAS_VERSION]->(term_ver_value)
            MERGE (codelist_root)-[:HAS_TERM]->(term_root)
            WITH term_root, final, hasver
            MATCH (library:Library {name:$library_name})
            WITH library, term_root, final, hasver
            MERGE (library)-[:CONTAINS_TERM]->(term_root)""" + cls.set_final_props(
            "hasver"
        )
        create_dictionary_term_with_custom_uid_query = """
            MATCH (dictionary_codelist_root:DictionaryCodelistRoot {uid:$dictionary_codelist_uid})
            WITH dictionary_codelist_root
            MERGE (dictionary_term_root:DictionaryTermRoot {uid: $uid})-[:LATEST]->(dictionary_term_value:DictionaryTermValue
            {name: $name, name_sentence_case: toLower($name)})
            MERGE (dictionary_term_root)-[final:LATEST_FINAL]->(dictionary_term_value)
            MERGE (dictionary_term_root)-[hasver:HAS_VERSION]->(dictionary_term_value)
            MERGE (dictionary_codelist_root)-[:HAS_TERM]->(dictionary_term_root)
            
            WITH dictionary_term_root, final, hasver
            MATCH (library:Library {name:$library_name})
            WITH library, dictionary_term_root, final, hasver
            MERGE (library)-[:CONTAINS_DICTIONARY_TERM]->(dictionary_term_root)""" + cls.set_final_props(
            "hasver"
        )
        for field_name, value in ct_data_map.items():
            if field_name in [
                "TherapeuticAreas",
                "DiseaseConditionOrIndications",
                "DiagnosisGroups",
            ]:
                query = create_dictionary_term_with_custom_uid_query
            else:
                query = create_ct_term_with_custom_uid_query

            if isinstance(value, list):
                for uid, name in value:
                    db.cypher_query(
                        query,
                        {
                            "codelist_uid": codelist_uid,
                            "dictionary_codelist_uid": dictionary_codelist.codelist_uid,
                            "uid": uid,
                            "name": name,
                            "library_name": library_name,
                        },
                    )
            else:
                db.cypher_query(
                    query,
                    {
                        "codelist_uid": codelist_uid,
                        "dictionary_codelist_uid": dictionary_codelist.codelist_uid,
                        "uid": value[0],
                        "name": value[1],
                        "library_name": library_name,
                    },
                )

    @classmethod
    def create_study_fields_configuration(cls):
        config_service = CTConfigService()
        with open(DEFAULT_STUDY_FIELD_CONFIG_FILE, encoding="UTF-8") as f:
            r = csv.DictReader(f)
            for line in r:
                if line.get("configured_codelist_uid") != "":
                    db.cypher_query(
                        """
                    MATCH (library:Library {name:$library})
                    MATCH (catalogue:CTCatalogue {name:$catalogue})
                    MERGE (library)-[:CONTAINS_CODELIST]->(codelist_root:CTCodelistRoot {uid: $uid})-[:HAS_NAME_ROOT]->
                    (codelist_ver_root:CTCodelistNameRoot)-[:LATEST]->(codelist_ver_value:CTCodelistNameValue {
                    name: $uid + 'name',
                    name_sentence_case: $uid + 'name'})
                    MERGE (codelist_root)-[:HAS_ATTRIBUTES_ROOT]->(codelist_a_root:CTCodelistAttributesRoot)
                    -[:LATEST]->(codelist_a_value:CTCodelistAttributesValue {definition:$uid + ' DEF',
                    name:$uid + ' NAME', preferred_term:$uid + ' PREF', submission_value:$uid + ' SUMBVAL', extensible:true})
                    MERGE (catalogue)-[:HAS_CODELIST]->(codelist_root)
                    MERGE (codelist_ver_root)-[name_final:LATEST_FINAL]->(codelist_ver_value)
                    MERGE (codelist_ver_root)-[name_hasver:HAS_VERSION]->(codelist_ver_value)
                    MERGE (codelist_a_root)-[attributes_final:LATEST_FINAL]->(codelist_a_value)
                    MERGE (codelist_a_root)-[attributes_hasver:HAS_VERSION]->(codelist_a_value)
                    """
                        + cls.set_final_props("name_hasver")
                        + cls.set_final_props("attributes_hasver"),
                        {
                            "uid": line.get("configured_codelist_uid"),
                            "library": LIBRARY_NAME,
                            "catalogue": CT_CATALOGUE_NAME,
                        },
                    )
                elif line.get("configured_term_uid") != "":
                    db.cypher_query(
                        """
                    MATCH (library:Library {name:$library})
                    MATCH (catalogue:CTCatalogue {name:$catalogue})
                    // common codelist for all terms that we create for tests
                    MERGE (codelist_root:CTCodelistRoot{uid:$codelist})
                    MERGE (library)-[:CONTAINS_TERM]->(term_root:CTTermRoot {uid: $uid})-[:HAS_NAME_ROOT]->
                    (term_ver_root:CTTermNameRoot)-[:LATEST]->(term_ver_value:CTTermNameValue)
                    SET term_ver_value.name=$uid + 'name'
                    SET term_ver_value.name_sentence_case=$uid + 'name'
                    MERGE (term_root)-[:HAS_ATTRIBUTES_ROOT]->(term_a_root:CTTermAttributesRoot)
                    -[:LATEST]->(term_a_value:CTTermAttributesValue {
                    preferred_term: $uid + 'nci', definition: $uid + 'def', name:$uid + ' NAME', submission_value:$uid + 'submval'})
                    MERGE (codelist_root)-[:HAS_TERM]->(term_root)
                    MERGE (catalogue)-[:HAS_CODELIST]->(codelist_root)
                    MERGE (term_ver_root)-[name_final:LATEST_FINAL]->(term_ver_value)
                    MERGE (term_ver_root)-[name_hasver:HAS_VERSION]->(term_ver_value)
                    MERGE (term_a_root)-[attributes_final:LATEST_FINAL]->(term_a_value)
                    MERGE (term_a_root)-[attributes_hasver:HAS_VERSION]->(term_a_value)
                    """
                        + cls.set_final_props("name_hasver")
                        + cls.set_final_props("attributes_hasver"),
                        {
                            "uid": line.get("configured_term_uid"),
                            "codelist": CT_CODELIST_UID,
                            "library": LIBRARY_NAME,
                            "catalogue": CT_CATALOGUE_NAME,
                        },
                    )
                input_data = CTConfigPostInput(**line)
                config_service.post(input_data)

    @classmethod
    def create_data_model_catalogue(
        cls,
        name: str = "name",
        data_model_type: str = "data_model_type",
        library_name: str = LIBRARY_NAME,
    ) -> str:
        """
        Method uses cypher query to create DataModelCatalogue nodes because we don't have POST endpoints to instantiate these entities.

        :param name
        :param data_model_type
        :param library_name
        """

        create_data_model_catalogue = """
            MERGE (data_model_catalogue:DataModelCatalogue {name: $name, data_model_type:$data_model_type})
            WITH data_model_catalogue
            MATCH (library:Library {name:$library_name})
            MERGE (library)-[:CONTAINS_CATALOGUE]->(data_model_catalogue)"""
        db.cypher_query(
            create_data_model_catalogue,
            {
                "name": name,
                "data_model_type": data_model_type,
                "library_name": library_name,
            },
        )
        return name

    @classmethod
    def create_data_model(
        cls,
        name: str = "name",
        description: str = "description",
        implementation_guides=None,
        library_name: str = LIBRARY_NAME,
    ) -> DataModel:
        """
        Method uses cypher query to create DataModel nodes because we don't have POST endpoints to instantiate these entities.

        :param name
        :param description
        :param implementation_guides
        :param library_name
        """

        if implementation_guides is None:
            implementation_guides = []
        create_data_model = (
            """
            MERGE (data_model_root:DataModelRoot {uid: $data_model_uid})-[:LATEST]->(data_model_value:DataModelValue
            {name: $name, description: $description})
            MERGE (data_model_root)-[final:LATEST_FINAL]->(data_model_value)
            MERGE (data_model_root)-[hv:HAS_VERSION]->(data_model_value)
            WITH data_model_root, data_model_value, final, hv
            MATCH (library:Library {name:$library_name})
            WITH library, data_model_root, data_model_value, final, hv
            MERGE (library)-[:CONTAINS_DATA_MODEL]->(data_model_root)
            """
            + cls.set_final_props("hv")
            + """ WITH data_model_root, data_model_value, final
            UNWIND CASE WHEN $implementation_guides = [] THEN [NULL] 
            ELSE $implementation_guides END as implementation_guide
            MATCH (data_model_ig_root:DataModelIGRoot {uid:implementation_guide})-[:LATEST]->(data_model_ig_value)
            MERGE (data_model_value)<-[:IMPLEMENTS]-(data_model_ig_value)"""
        )
        data_model_uid = DataModelRoot.get_next_free_uid_and_increment_counter()
        db.cypher_query(
            create_data_model,
            {
                "data_model_uid": data_model_uid,
                "name": name,
                "description": description,
                "implementation_guides": implementation_guides,
                "library_name": library_name,
            },
        )
        return DataModelService().get_by_uid(uid=data_model_uid)

    @classmethod
    def create_data_model_ig(
        cls,
        name: str = "name",
        description: str = "description",
        implemented_data_model: Optional[str] = None,
        library_name: str = LIBRARY_NAME,
    ) -> DataModelIG:
        """
        Method uses cypher query to create DataModelIG nodes because we don't have POST endpoints to instantiate these entities.

        :param name
        :param description
        :param implemented_data_model
        :param library_name
        """
        create_data_model_ig = (
            """
            MERGE (data_model_ig_root:DataModelIGRoot {uid: $data_model_ig_uid})-[:LATEST]->(data_model_ig_value:DataModelIGValue
            {name: $name, description: $description})
            MERGE (data_model_ig_root)-[final:LATEST_FINAL]->(data_model_ig_value)
            MERGE (data_model_ig_root)-[hv:HAS_VERSION]->(data_model_ig_value)
            WITH data_model_ig_root, data_model_ig_value, final, hv
            MATCH (library:Library {name:$library_name})
            WITH library, data_model_ig_root, data_model_ig_value, final, hv
            MERGE (library)-[:CONTAINS_DATA_MODEL_IG]->(data_model_ig_root)
            """
            + cls.set_final_props("hv")
            + """WITH data_model_ig_root, data_model_ig_value, final
            MATCH (data_model_root:DataModelRoot {uid:$implemented_data_model})-[:LATEST]->(data_model_value)
            MERGE (data_model_ig_value)-[:IMPLEMENTS]->(data_model_value)"""
        )
        data_model_ig_uid = DataModelIGRoot.get_next_free_uid_and_increment_counter()
        db.cypher_query(
            create_data_model_ig,
            {
                "data_model_ig_uid": data_model_ig_uid,
                "name": name,
                "description": description,
                "implemented_data_model": implemented_data_model,
                "library_name": library_name,
            },
        )
        return DataModelIGService().get_by_uid(uid=data_model_ig_uid)

    @classmethod
    def create_dataset_class(
        cls,
        data_model_uid: str,
        data_model_catalogue_name: str,
        label: str = "label",
        description: str = "description",
        title: str = "title",
        library_name: str = LIBRARY_NAME,
    ) -> DatasetClass:
        """
        Method uses cypher query to create DatasetClass nodes because we don't have POST endpoints to instantiate these entities.

        :param data_model_uid
        :param data_model_catalogue_name
        :param label
        :param description
        :param title
        :param library_name
        """

        create_dataset_class = (
            """
            MERGE (dataset_class_root:DatasetClassRoot {uid: $implemented_dataset_class_name})-[:LATEST]->(dataset_class_value:DatasetClassValue
            {label: $label, description: $description, title: $title})
            MERGE (dataset_class_root)-[final:LATEST_FINAL]->(dataset_class_value)
            MERGE (dataset_class_root)-[hv:HAS_VERSION]->(dataset_class_value)
            WITH dataset_class_root, dataset_class_value, final, hv
            MATCH (data_model_catalogue:DataModelCatalogue {name: $data_model_catalogue_name})
            MERGE (data_model_catalogue)-[:HAS_DATASET_CLASS]->(dataset_class_root)
            //MATCH (library:Library {name:$library_name})
            //WITH library, dataset_class_root, dataset_class_value, final, hv
            //MERGE (library)-[:CONTAINS_DATASET_CLASS]->(dataset_class_root)
            """
            + cls.set_final_props("hv")
            + """ WITH dataset_class_root, dataset_class_value, final
            MATCH (data_model_root:DataModelRoot {uid:$data_model_uid})-[:LATEST]->(data_model_value)
            MERGE (dataset_class_value)<-[:HAS_DATASET_CLASS]-(data_model_value)"""
        )
        dataset_class_uid = DatasetClassRoot.get_next_free_uid_and_increment_counter()
        db.cypher_query(
            create_dataset_class,
            {
                "implemented_dataset_class_name": dataset_class_uid,
                "data_model_catalogue_name": data_model_catalogue_name,
                "label": label,
                "title": title,
                "description": description,
                "data_model_uid": data_model_uid,
                "library_name": library_name,
            },
        )
        return DatasetClassService().get_by_uid(uid=dataset_class_uid)

    @classmethod
    def create_dataset(
        cls,
        data_model_ig_uid: str,
        implemented_dataset_class_name: str,
        data_model_catalogue_name: str,
        label: str = "label",
        description: str = "description",
        title: str = "title",
        library_name: str = LIBRARY_NAME,
    ) -> Dataset:
        """
        Method uses cypher query to create Dataset nodes because we don't have POST endpoints to instantiate these entities.

        :param data_model_ig_uid
        :param implemented_dataset_class_name
        :param data_model_catalogue_name
        :param label
        :param description
        :param title
        :param library_name
        """

        create_dataset = (
            """
            MERGE (dataset_root:DatasetRoot {uid: $dataset_uid})-[:LATEST]->(dataset_value:DatasetValue
            {label: $label, description: $description, title: $title})
            MERGE (dataset_root)-[final:LATEST_FINAL]->(dataset_value)
            MERGE (dataset_root)-[hv:HAS_VERSION]->(dataset_value)
            WITH dataset_root, dataset_value, final, hv
            MATCH (data_model_catalogue:DataModelCatalogue {name: $data_model_catalogue_name})
            MERGE (data_model_catalogue)-[:HAS_DATASET]->(dataset_root)
            //MATCH (library:Library {name:$library_name})
            //WITH library, dataset_root, dataset_value, final, hv
            //MERGE (library)-[:CONTAINS_DATASET]->(dataset_root)
            """
            + cls.set_final_props("hv")
            + """ WITH dataset_root, dataset_value, final
            MATCH (data_model_ig_root:DataModelIGRoot {uid:$data_model_ig_uid})-[:LATEST]->(data_model_ig_value)
            MERGE (dataset_value)<-[:HAS_DATASET]-(data_model_ig_value)
            WITH dataset_root, dataset_value
            MATCH (dataset_class_root:DatasetClassRoot {uid: $implemented_dataset_class_name})-[:LATEST]->(dataset_class_value)
            MERGE (dataset_value)-[:IMPLEMENTS_DATASET_CLASS]->(dataset_class_value)"""
        )
        dataset_uid = DatasetRoot.get_next_free_uid_and_increment_counter()
        db.cypher_query(
            create_dataset,
            {
                "dataset_uid": dataset_uid,
                "data_model_ig_uid": data_model_ig_uid,
                "implemented_dataset_class_name": implemented_dataset_class_name,
                "data_model_catalogue_name": data_model_catalogue_name,
                "label": label,
                "title": title,
                "description": description,
                "library_name": library_name,
            },
        )
        return DatasetService().get_by_uid(uid=dataset_uid)

    @classmethod
    def create_disease_milestone(
        cls,
        study_uid,
        disease_milestone_type=None,
        repetition_indicator=None,
    ) -> StudyDiseaseMilestone:
        service = StudyDiseaseMilestoneService()
        payload = StudyDiseaseMilestoneCreateInput(
            study_uid=study_uid,
            disease_milestone_type=disease_milestone_type,
            repetition_indicator=repetition_indicator,
        )

        result: StudyDiseaseMilestone = service.create(
            study_uid, study_disease_milestone_input=payload
        )
        return result

    @classmethod
    def create_class_variable(
        cls,
        dataset_class_uid: str,
        data_model_catalogue_name: str,
        label: str = "label",
        description: str = "description",
        title: str = "title",
        implementation_notes: str = "implementation_notes",
        mapping_instructions: str = "mapping_instructions",
        prompt: str = "prompt",
        question_text: str = "question_text",
        simple_datatype: str = "simple_datatype",
        role: str = "role",
        library_name: str = LIBRARY_NAME,
    ) -> ClassVariable:
        """
        Method uses cypher query to create ClassVariable nodes because we don't have POST endpoints to instantiate these entities.

        :param dataset_class_uid
        :param data_model_catalogue_name
        :param label
        :param description
        :param title
        :param implementation_notes
        :param mapping_instructions
        :param prompt
        :param question_text
        :param simple_datatype
        :param role
        :param library_name
        """

        create_class_variable = (
            """
            MERGE (class_variable_root:ClassVariableRoot {uid: $class_variable_uid})-[:LATEST]->(class_variable_value:ClassVariableValue
            {label: $label, description: $description, title: $title,
            implementation_notes: $implementation_notes, mapping_instructions: $mapping_instructions, prompt: $prompt,
            question_text: $question_text, simple_datatype: $simple_datatype, role: $role})
            MERGE (class_variable_root)-[final:LATEST_FINAL]->(class_variable_value)
            MERGE (class_variable_root)-[hv:HAS_VERSION]->(class_variable_value)
            WITH class_variable_root, class_variable_value, final, hv
            MATCH (data_model_catalogue:DataModelCatalogue {name: $data_model_catalogue_name})
            MERGE (data_model_catalogue)-[:HAS_CLASS_VARIABLE]->(class_variable_root)
            //MATCH (library:Library {name:$library_name})
            //WITH library, class_variable_root, class_variable_value, final
            //MERGE (library)-[:CONTAINS_CLASS_VARIABLE]->(class_variable_root)
            """
            + cls.set_final_props("hv")
            + """ WITH class_variable_root, class_variable_value, final
            MATCH (dataset_class_root:DatasetClassRoot {uid:$dataset_class_uid})-[:LATEST]->(dataset_class_value)
            MERGE (class_variable_value)<-[:HAS_CLASS_VARIABLE]-(dataset_class_value)"""
        )
        class_variable_uid = ClassVariableRoot.get_next_free_uid_and_increment_counter()
        db.cypher_query(
            create_class_variable,
            {
                "class_variable_uid": class_variable_uid,
                "dataset_class_uid": dataset_class_uid,
                "data_model_catalogue_name": data_model_catalogue_name,
                "label": label,
                "description": description,
                "title": title,
                "implementation_notes": implementation_notes,
                "mapping_instructions": mapping_instructions,
                "prompt": prompt,
                "question_text": question_text,
                "simple_datatype": simple_datatype,
                "role": role,
                "library_name": library_name,
            },
        )
        return ClassVariableService().get_by_uid(uid=class_variable_uid)

    @classmethod
    def create_dataset_variable(
        cls,
        dataset_uid: str,
        data_model_catalogue_name: str,
        class_variable_uid: Optional[str] = None,
        label: str = "label",
        description: str = "description",
        title: str = "title",
        simple_datatype: str = "simple_datatype",
        role: str = "role",
        core: str = "core",
        library_name: str = LIBRARY_NAME,
    ) -> DatasetVariable:
        """
        Method uses cypher query to create DatasetVariable nodes because we don't have POST endpoints to instantiate these entities.

        :param dataset_uid
        :param data_model_catalogue_name
        :param class_variable_uid
        :param label
        :param description
        :param title
        :param simple_datatype
        :param role
        :param core
        :param library_name
        """

        create_dataset_variable = (
            """
            MERGE (dataset_variable_root:DatasetVariableRoot {uid: $dataset_variable_uid})-[:LATEST]->(dataset_variable_value:DatasetVariableValue
            {label: $label, description: $description, title: $title,
            simple_datatype: $simple_datatype, role: $role, core: $core})
            MERGE (dataset_variable_root)-[final:LATEST_FINAL]->(dataset_variable_value)
            MERGE (dataset_variable_root)-[hv:HAS_VERSION]->(dataset_variable_value)
            WITH dataset_variable_root, dataset_variable_value, final, hv
            MATCH (data_model_catalogue:DataModelCatalogue {name: $data_model_catalogue_name})
            MERGE (data_model_catalogue)-[:HAS_DATASET_VARIABLE]->(dataset_variable_root)
            //MATCH (library:Library {name:$library_name})
            //WITH library, dataset_variable_root, dataset_variable_value, final
            //MERGE (library)-[:CONTAINS_DATASET_VARIABLE]->(dataset_variable_root)
            """
            + cls.set_final_props("hv")
            + """ WITH dataset_variable_root, dataset_variable_value, final
            MATCH (dataset_root:DatasetRoot {uid:$dataset_uid})-[:LATEST]->(dataset_value)
            MERGE (dataset_variable_value)<-[:HAS_DATASET_VARIABLE]-(dataset_value)
            WITH dataset_variable_root, dataset_variable_value
            MATCH (class_variable_root:ClassVariableRoot {uid: $class_variable_uid})-[:LATEST]->(class_variable_value)
            MERGE (dataset_variable_value)-[:IMPLEMENTS_VARIABLE]->(class_variable_value)"""
        )
        dataset_variable_uid = (
            DatasetVariableRoot.get_next_free_uid_and_increment_counter()
        )
        db.cypher_query(
            create_dataset_variable,
            {
                "dataset_variable_uid": dataset_variable_uid,
                "dataset_uid": dataset_uid,
                "data_model_catalogue_name": data_model_catalogue_name,
                "class_variable_uid": class_variable_uid,
                "label": label,
                "description": description,
                "title": title,
                "simple_datatype": simple_datatype,
                "role": role,
                "core": core,
                "library_name": library_name,
            },
        )
        return DatasetVariableService().get_by_uid(uid=dataset_variable_uid)

    @classmethod
    def create_study_epoch(
        cls,
        study_uid: str,
        start_rule: Optional[str] = None,
        end_rule: Optional[str] = None,
        epoch: Optional[str] = None,
        epoch_subtype: Optional[str] = None,
        duration_unit: Optional[str] = None,
        order: Optional[int] = None,
        description: Optional[str] = None,
        duration: Optional[int] = 0,
        color_hash: Optional[str] = None,
    ) -> StudyEpoch:
        epoch_create_input = StudyEpochCreateInput(
            study_uid=study_uid,
            start_rule=start_rule,
            end_rule=end_rule,
            epoch=epoch,
            epoch_subtype=epoch_subtype,
            duration_unit=duration_unit,
            order=order,
            description=description,
            duration=duration,
            color_hash=color_hash,
        )

        result: StudyEpoch = StudyEpochService(AUTHOR).create(
            study_uid=study_uid, study_epoch_input=epoch_create_input
        )
        return result

    @classmethod
    def create_study_design_cell(
        cls,
        study_uid: str,
        study_epoch_uid: str,
        study_element_uid: str,
        study_arm_uid: Optional[str] = None,
        study_branch_arm_uid: Optional[str] = None,
        transition_rule: Optional[str] = None,
        order: Optional[int] = None,
    ) -> StudyDesignCell:
        design_cell_input = StudyDesignCellCreateInput(
            study_epoch_uid=study_epoch_uid,
            study_element_uid=study_element_uid,
            study_arm_uid=study_arm_uid,
            study_branch_arm_uid=study_branch_arm_uid,
            transition_rule=transition_rule,
            order=order,
        )

        result: StudyDesignCell = StudyDesignCellService(AUTHOR).create(
            study_uid=study_uid, design_cell_input=design_cell_input
        )
        return result

    @classmethod
    def create_study_arm(
        cls,
        study_uid: str,
        name: str,
        short_name: str,
        code: Optional[str] = None,
        description: Optional[str] = None,
        arm_colour: Optional[str] = None,
        randomization_group: Optional[str] = None,
        number_of_subjects: Optional[int] = None,
        arm_type_uid: Optional[str] = None,
    ) -> StudySelectionArm:
        arm_input = StudySelectionArmCreateInput(
            name=name,
            short_name=short_name,
            code=code,
            description=description,
            arm_colour=arm_colour,
            randomization_group=randomization_group,
            number_of_subjects=number_of_subjects,
            arm_type_uid=arm_type_uid,
        )

        result: StudySelectionArm = StudyArmSelectionService(AUTHOR).make_selection(
            study_uid=study_uid, selection_create_input=arm_input
        )
        return result
