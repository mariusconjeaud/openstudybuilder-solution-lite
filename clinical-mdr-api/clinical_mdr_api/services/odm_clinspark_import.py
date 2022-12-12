"""
This is similar to the generic ODM XML Importer (odm_xml_importer.py)
However, this one is a temporary import functionality specific for ClinSpark.
The reason for not making it part of the generic importer is that the way ClinSpark manages ODM XML deviates from the standard.
"""
from distutils.util import strtobool
from time import time
from typing import Dict, Optional, Sequence, Union
from xml.dom import minicompat, minidom

from fastapi import UploadFile
from neomodel import db

from clinical_mdr_api import exceptions
from clinical_mdr_api.domain._utils import get_iso_lang_data
from clinical_mdr_api.domain.concepts.utils import ENG_LANGUAGE, RelationType
from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryVO,
    VersioningException,
)
from clinical_mdr_api.models import (
    OdmConditionPostInput,
    OdmDescriptionPostInput,
    OdmFormalExpressionPostInput,
    OdmFormItemGroupPostInput,
    OdmFormPostInput,
    OdmItemGroupItemPostInput,
    OdmItemGroupPostInput,
    OdmItemPostInput,
    OdmItemTermRelationshipInput,
    OdmItemUnitDefinitionRelationshipInput,
    OdmTemplateFormPostInput,
    OdmTemplatePostInput,
)
from clinical_mdr_api.models.ct_codelist import CTCodelistCreateInput
from clinical_mdr_api.models.ct_codelist_attributes import CTCodelistAttributes
from clinical_mdr_api.models.ct_term import CTTermCreateInput
from clinical_mdr_api.models.ct_term_attributes import CTTermAttributes
from clinical_mdr_api.models.odm_condition import OdmCondition
from clinical_mdr_api.models.odm_form import OdmForm
from clinical_mdr_api.models.odm_item import OdmItem
from clinical_mdr_api.models.odm_item_group import OdmItemGroup
from clinical_mdr_api.models.odm_method import OdmMethod, OdmMethodPostInput
from clinical_mdr_api.models.odm_template import OdmTemplate
from clinical_mdr_api.models.unit_definition import UnitDefinitionModel
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services._utils import normalize_string
from clinical_mdr_api.services.ct_codelist import CTCodelistService
from clinical_mdr_api.services.ct_codelist_attributes import CTCodelistAttributesService
from clinical_mdr_api.services.ct_codelist_name import CTCodelistNameService
from clinical_mdr_api.services.ct_term import CTTermService
from clinical_mdr_api.services.ct_term_attributes import CTTermAttributesService
from clinical_mdr_api.services.ct_term_name import CTTermNameService
from clinical_mdr_api.services.odm_conditions import OdmConditionService
from clinical_mdr_api.services.odm_descriptions import OdmDescriptionService
from clinical_mdr_api.services.odm_formal_expressions import OdmFormalExpressionService
from clinical_mdr_api.services.odm_forms import OdmFormService
from clinical_mdr_api.services.odm_item_groups import OdmItemGroupService
from clinical_mdr_api.services.odm_items import OdmItemService
from clinical_mdr_api.services.odm_methods import OdmMethodService
from clinical_mdr_api.services.odm_templates import OdmTemplateService
from clinical_mdr_api.services.unit_definition import UnitDefinitionService


class OdmClinicalXmlImporterService:
    _repos: MetaRepository
    odm_template_service: OdmTemplateService
    odm_form_service: OdmFormService
    odm_item_group_service: OdmItemGroupService
    odm_item_service: OdmItemService
    odm_condition_service: OdmConditionService
    odm_method_service: OdmMethodService
    odm_formal_expression_service: OdmFormalExpressionService
    odm_description_service: OdmDescriptionService
    unit_definition_service: UnitDefinitionService
    ct_term_attributes_service: CTTermAttributesService
    ct_term_name_service: CTTermNameService
    ct_codelist_attributes_service: CTCodelistAttributesService
    ct_codelist_name_service: CTCodelistNameService
    ct_codelist_service: CTCodelistService
    ct_term_service: CTTermService

    user_initials: Optional[str]

    xml_document: minidom.Document
    form_defs: minicompat.NodeList
    item_group_defs: minicompat.NodeList
    item_defs: minicompat.NodeList
    condition_defs: minicompat.NodeList
    method_defs: minicompat.NodeList
    codelists: minicompat.NodeList
    measurement_units: minicompat.NodeList

    db_templates: Sequence[OdmTemplate]
    db_forms: Sequence[OdmForm]
    db_item_groups: Sequence[OdmItemGroup]
    db_items: Sequence[OdmItem]
    db_conditions: Sequence[OdmCondition]
    db_methods: Sequence[OdmMethod]
    db_ct_term_attributes: Sequence[CTTermAttributes]
    db_ct_codelist_attributes: Sequence[CTCodelistAttributes]
    db_unit_definitions: Sequence[UnitDefinitionModel]
    unit_definition_uids_by_name: Dict[str, str]
    measurement_unit_names_by_oid: Dict[str, str]

    def __init__(self, xml: UploadFile):
        if xml.content_type not in ["application/xml", "text/xml"]:
            raise exceptions.BusinessLogicException("Only XML format is supported.")

        self._repos = MetaRepository()
        self.odm_template_service = OdmTemplateService()
        self.odm_form_service = OdmFormService()
        self.odm_item_group_service = OdmItemGroupService()
        self.odm_item_service = OdmItemService()
        self.odm_condition_service = OdmConditionService()
        self.odm_method_service = OdmMethodService()
        self.odm_formal_expression_service = OdmFormalExpressionService()
        self.odm_description_service = OdmDescriptionService()
        self.ct_term_attributes_service = CTTermAttributesService()
        self.ct_term_name_service = CTTermNameService()
        self.ct_codelist_attributes_service = CTCodelistAttributesService()
        self.ct_codelist_name_service = CTCodelistNameService()
        self.ct_codelist_service = CTCodelistService()
        self.ct_term_service = CTTermService()

        self.user_initials = "TODO user initials"

        self.db_templates = []
        self.db_forms = []
        self.db_item_groups = []
        self.db_items = []
        self.db_conditions = []
        self.db_methods = []
        self.db_ct_term_attributes = []
        self.db_ct_codelist_attributes = []
        self.db_unit_definitions = []
        self.unit_definition_uids_by_name = {}
        self.measurement_unit_names_by_oid = {}

        self.xml_document = minidom.parseString(xml.file.read())
        self._set_def_elements()

    @db.transaction
    def store_odm_xml(self):
        self._set_unit_definitions()
        self._set_unit_definition_uids_by_name()
        self._set_measurement_unit_names_by_oid()
        self._set_codelists()
        self._set_ct_term_attributes()
        self._create_conditions_with_relations()
        self._create_methods_with_relations()
        self._create_items_with_relations()
        self._create_item_groups_with_relations()
        self._create_forms_with_relations()
        self._create_template_with_relations()

        return {
            "templates": self._get_newly_created_templates(),
            "forms": self._get_newly_created_forms(),
            "item_groups": self._get_newly_created_item_groups(),
            "items": self._get_newly_created_items(),
            "conditions": self._get_newly_created_conditions(),
            "methods": self._get_newly_created_methods(),
        }

    def _set_def_elements(self):
        self.measurement_units = self.xml_document.getElementsByTagName(
            "MeasurementUnit"
        )
        self.form_defs = self.xml_document.getElementsByTagName("FormDef")
        self.item_group_defs = self.xml_document.getElementsByTagName("ItemGroupDef")
        self.item_defs = self.xml_document.getElementsByTagName("ItemDef")
        self.condition_defs = self.xml_document.getElementsByTagName("ConditionDef")
        self.method_defs = self.xml_document.getElementsByTagName("MethodDef")
        self.codelists = self.xml_document.getElementsByTagName("CodeList")

    def _set_unit_definitions(self):
        measurement_unit_names = {
            measurement_unit.getAttribute("Name")
            for measurement_unit in self.measurement_units
        }

        rs, _ = self._repos.unit_definition_repository.find_all(
            filter_by={"name": {"v": measurement_unit_names, "op": "eq"}},
        )

        rs_names = {item.name for item in rs}

        non_existing_measurement_unit_names = measurement_unit_names - rs_names

        if non_existing_measurement_unit_names:
            raise exceptions.BusinessLogicException(
                f"MeasurementUnits identified by following names {non_existing_measurement_unit_names} don't match any Unit Definition."
            )

        self.db_unit_definitions = [
            UnitDefinitionModel.from_unit_definition_ar(
                unit_definition_ar,
                find_term_by_uid=self._repos.ct_term_name_repository.find_by_uid,
                find_dictionary_term_by_uid=self._repos.dictionary_term_generic_repository.find_by_uid,
            )
            for unit_definition_ar in rs
        ]

    def _set_unit_definition_uids_by_name(self):
        self.unit_definition_uids_by_name = {
            db_unit_definition.name: db_unit_definition.uid
            for db_unit_definition in self.db_unit_definitions
        }

    def _set_measurement_unit_names_by_oid(self):
        self.measurement_unit_names_by_oid = {
            measurement_unit.getAttribute("OID"): measurement_unit.getAttribute("Name")
            for measurement_unit in self.measurement_units
        }

    def _set_codelists(self):
        rs = self._get_and_create_codelists()

        self.db_ct_codelist_attributes = [
            self.ct_codelist_attributes_service._transform_aggregate_root_to_pydantic_model(
                item_ar
            )
            for item_ar in rs
        ]

    def _set_ct_term_attributes(self):
        term_attributes = self._get_and_create_term_attributes()

        self.db_ct_term_attributes = [
            self.ct_term_attributes_service._transform_aggregate_root_to_pydantic_model(
                item_ar
            )
            for item_ar in term_attributes
        ]

    def _get_and_create_codelists(self):
        rs = self._repos.ct_codelist_attribute_repository.find_all(
            filter_by={
                "submission_value": {
                    "v": [
                        self._get_codelist_submission_value(codelist)
                        for codelist in self.codelists
                    ],
                    "op": "eq",
                }
            }
        ).items
        existing_codelist_submission_values = {
            elm.ct_codelist_vo.submission_value for elm in rs
        }

        new_codelist_uids = set()
        for codelist in self.codelists:
            submission_value = self._get_codelist_submission_value(codelist)

            if submission_value not in existing_codelist_submission_values:
                ct_codelist = self.ct_codelist_service.non_transactional_create(
                    CTCodelistCreateInput(
                        catalogue_name="CDASH CT",
                        name=codelist.getAttribute("Name"),
                        submission_value=submission_value,
                        nci_preferred_name=codelist.getAttribute("Name"),
                        definition=codelist.getAttribute("Name"),
                        sponsor_preferred_name=codelist.getAttribute("Name"),
                        extensible=True,
                        template_parameter=True,
                        parent_codelist_uid=None,
                        library_name="Sponsor",
                        terms=[],
                    )
                )
                self.ct_codelist_name_service.non_transactional_approve(
                    ct_codelist.codelist_uid
                )
                self.ct_codelist_attributes_service.non_transactional_approve(
                    ct_codelist.codelist_uid
                )
                new_codelist_uids.add(ct_codelist.codelist_uid)
                existing_codelist_submission_values.add(submission_value)

        if new_codelist_uids:
            rs.extend(
                self._repos.ct_codelist_attribute_repository.find_all(
                    filter_by={"codelist_uid": {"v": new_codelist_uids, "op": "eq"}}
                ).items
            )

        return rs

    def _get_and_create_term_attributes(self):
        def manage_codelist_item():
            if (
                codelist_item.getAttribute("CodedValue")
                not in term_code_submission_values
            ):
                ct_term = self.ct_term_service.non_transactional_create(
                    CTTermCreateInput(
                        catalogue_name="CDASH CT",
                        codelist_uid=active_codelist.codelist_uid,
                        code_submission_value=codelist_item.getAttribute("CodedValue"),
                        name_submission_value=codelist_item.getAttribute("CodedValue"),
                        nci_preferred_name=translated_txt,
                        definition=translated_txt,
                        sponsor_preferred_name=translated_txt,
                        sponsor_preferred_name_sentence_case=translated_txt.lower(),
                        library_name="Sponsor",
                        order=999999,
                    )
                )
                self.ct_term_name_service.non_transactional_approve(ct_term.term_uid)
                self.ct_term_attributes_service.non_transactional_approve(
                    ct_term.term_uid
                )
                term_attribute_uids.add(ct_term.term_uid)
                term_code_submission_values.add(ct_term.code_submission_value)
                return True

            for item in rs.items:
                if (
                    codelist_item.getAttribute("CodedValue")
                    != item.ct_term_vo.code_submission_value
                ):
                    continue

                if active_codelist.codelist_uid in term_codelist_uids:
                    term_attribute_uids.add(item.uid)
                    return True

                self.ct_codelist_service.non_transactional_add_term(
                    active_codelist.codelist_uid,
                    item.uid,
                    idx,
                )
                term_attribute_uids.add(item.uid)
                return True

            return False

        rs = self._repos.ct_term_attributes_repository.find_all(
            filter_by={
                "code_submission_value": {
                    "v": [
                        codelist_item.getAttribute("CodedValue")
                        for codelist in self.codelists
                        for codelist_item in codelist.getElementsByTagName(
                            "CodeListItem"
                        )
                    ],
                    "op": "eq",
                }
            }
        )
        term_codelist_uids = {item.ct_term_vo.codelist_uid for item in rs.items}
        term_code_submission_values = {
            item.ct_term_vo.code_submission_value for item in rs.items
        }

        term_attribute_uids = set()
        for codelist in self.codelists:
            try:
                active_codelist = next(
                    db_ct_codelist_attribute
                    for db_ct_codelist_attribute in self.db_ct_codelist_attributes
                    if self._get_codelist_submission_value(codelist)
                    == db_ct_codelist_attribute.submission_value
                )
            except StopIteration as exc:
                raise exceptions.BusinessLogicException(
                    f"Codelist identified by ({codelist.getAttribute('OID')}) not found."
                ) from exc

            for idx, codelist_item in enumerate(
                codelist.getElementsByTagName("CodeListItem")
            ):
                translated_txt: str = (
                    codelist_item.getElementsByTagName("Decode")[0]
                    .getElementsByTagName("TranslatedText")[0]
                    .firstChild.nodeValue
                )

                if manage_codelist_item():
                    continue

        return self._repos.ct_term_attributes_repository.find_all(
            filter_by={"term_uid": {"v": term_attribute_uids, "op": "eq"}}
        ).items

    def _create_formal_expressions(self, target):
        new_formal_expressions = []
        for formal_expression in target.getElementsByTagName("FormalExpression"):
            rs = self._create(
                self._repos.odm_formal_expression_repository,
                self.odm_formal_expression_service,
                new_formal_expressions,
                OdmFormalExpressionPostInput(
                    context=formal_expression.getAttribute("Context"),
                    expression=formal_expression.firstChild.nodeValue,
                ),
            )

            self._approve(
                self._repos.odm_formal_expression_repository,
                self.odm_formal_expression_service,
                rs,
            )

        return new_formal_expressions

    def _create_conditions_with_relations(self):
        for condition_def in self.condition_defs:
            descriptions = self._extract_descriptions(condition_def)

            rs = self._create(
                self._repos.odm_condition_repository,
                self.odm_condition_service,
                self.db_conditions,
                OdmConditionPostInput(
                    oid=condition_def.getAttribute("OID"),
                    name=condition_def.getAttribute("Name"),
                    formal_expressions=[
                        formal_expression.uid
                        for formal_expression in self._create_formal_expressions(
                            condition_def
                        )
                    ],
                    descriptions=[
                        self._create_description(
                            name=description["name"],
                            description=description["description"],
                            lang=description["lang"],
                        ).uid
                        for description in descriptions
                    ],
                    alias_uids=[],
                ),
            )
            self._approve(
                self._repos.odm_condition_repository, self.odm_condition_service, rs
            )

    def _create_methods_with_relations(self):
        for method_def in self.method_defs:
            descriptions = self._extract_descriptions(method_def)

            rs = self._create(
                self._repos.odm_method_repository,
                self.odm_method_service,
                self.db_methods,
                OdmMethodPostInput(
                    oid=method_def.getAttribute("OID"),
                    name=method_def.getAttribute("Name"),
                    method_type=method_def.getAttribute("Name"),
                    formal_expressions=[
                        formal_expression.uid
                        for formal_expression in self._create_formal_expressions(
                            method_def
                        )
                    ],
                    descriptions=[
                        self._create_description(
                            name=description["name"],
                            lang=description["lang"],
                            description=description["description"],
                        ).uid
                        for description in descriptions
                    ],
                    alias_uids=[],
                ),
            )
            self._approve(
                self._repos.odm_method_repository, self.odm_method_service, rs
            )

    def _create_items_with_relations(self):
        for item_def in self.item_defs:
            descriptions = self._extract_descriptions(item_def)

            unit_definitions = [
                OdmItemUnitDefinitionRelationshipInput(
                    uid=self.unit_definition_uids_by_name[
                        self.measurement_unit_names_by_oid[
                            measurement_unit_ref.getAttribute("MeasurementUnitOID")
                        ]
                    ]
                )
                for measurement_unit_ref in item_def.getElementsByTagName(
                    "MeasurementUnitRef"
                )
            ]

            codelist = next(
                (
                    codelist
                    for codelist in self.codelists
                    if item_def.getElementsByTagName("CodeListRef")
                    and codelist.getAttribute("OID")
                    == item_def.getElementsByTagName("CodeListRef")[0].getAttribute(
                        "CodeListOID"
                    )
                ),
                None,
            )

            codelist_uid = next(
                (
                    db_ct_codelist_attribute.codelist_uid
                    for db_ct_codelist_attribute in self.db_ct_codelist_attributes
                    if codelist
                    and self._get_codelist_submission_value(codelist)
                    == db_ct_codelist_attribute.submission_value
                ),
                None,
            )

            terms = []
            input_terms = []
            if codelist:
                terms = [
                    db_ct_term_attribute
                    for codelist_item in codelist.getElementsByTagName("CodeListItem")
                    for db_ct_term_attribute in self.db_ct_term_attributes
                    if codelist_item.getAttribute("CodedValue")
                    == db_ct_term_attribute.code_submission_value
                    and db_ct_term_attribute.codelist_uid == codelist_uid
                ]

                input_terms = [
                    OdmItemTermRelationshipInput(uid=term.term_uid, order=idx)
                    for idx, term in enumerate(terms)
                ]

            rs = self._create(
                self._repos.odm_item_repository,
                self.odm_item_service,
                self.db_items,
                OdmItemPostInput(
                    oid=item_def.getAttribute("OID"),
                    name=item_def.getAttribute("Name")
                    + "@"
                    + item_def.getAttribute("OID"),
                    prompt=item_def.getAttribute("Prompt"),
                    datatype=item_def.getAttribute("DataType"),
                    length=int(item_def.getAttribute("Length"))
                    if item_def.getAttribute("Length")
                    else None,
                    significant_digits=None,
                    sas_field_name=item_def.getAttribute("SASFieldName"),
                    sds_var_name=item_def.getAttribute("SDSVarName"),
                    origin=item_def.getAttribute("Origin"),
                    comment=None,
                    descriptions=[
                        self._create_description(
                            name=description["name"],
                            description=description["description"],
                            lang=description["lang"],
                        ).uid
                        for description in descriptions
                    ],
                    alias_uids=[],
                    unit_definitions=unit_definitions,
                    codelist_uid=codelist_uid,
                    terms=input_terms,
                ),
            )

            if terms:
                self.odm_item_service._manage_terms(rs.uid, input_terms)
            self.odm_item_service._manage_unit_definitions(rs.uid, unit_definitions)

            self._approve(self._repos.odm_item_repository, self.odm_item_service, rs)

    def _create_item_groups_with_relations(self):
        for item_group_def in self.item_group_defs:
            descriptions = self._extract_descriptions(item_group_def)

            rs = self._create(
                self._repos.odm_item_group_repository,
                self.odm_item_group_service,
                self.db_item_groups,
                OdmItemGroupPostInput(
                    oid=item_group_def.getAttribute("OID"),
                    name=item_group_def.getAttribute("Name")
                    + "@"
                    + item_group_def.getAttribute("OID"),
                    origin=item_group_def.getAttribute("Origin"),
                    repeating=item_group_def.getAttribute("Repeating"),
                    is_reference_data="no",  # missing in odm
                    purpose=item_group_def.getAttribute("Purpose"),
                    sas_dataset_name=item_group_def.getAttribute("SASDatasetName"),
                    comment=None,
                    descriptions=[
                        self._create_description(
                            name=description["name"],
                            description=description["description"],
                            lang=description["lang"],
                        ).uid
                        for description in descriptions
                    ],
                    alias_uids=[],
                    sdtm_domain_uids=[],
                ),
            )

            odm_item_group_items = []
            for item_ref in item_group_def.getElementsByTagName("ItemRef"):
                odm_item_group_items.append(
                    OdmItemGroupItemPostInput(
                        uid=next(
                            (
                                db_item.uid
                                for db_item in self.db_items
                                if db_item.oid == item_ref.getAttribute("ItemOID")
                            ),
                            None,
                        ),
                        order_number=item_ref.getAttribute("OrderNumber"),
                        mandatory=item_ref.getAttribute("Mandatory"),
                        data_entry_required=item_ref.getAttribute(
                            "osb:dataEntryRequired"
                        )
                        or "No",
                        sdv=item_ref.getAttribute("osb:sdv") or "No",
                        locked=item_ref.getAttribute("osb:locked") or "No",
                        key_sequence="None",
                        method_oid=item_ref.getAttribute("MethodOID") or None,
                        imputation_method_oid="None",
                        role="None",
                        role_codelist_oid="None",
                        collection_exception_condition_oid=item_ref.getAttribute(
                            "CollectionExceptionConditionOID"
                        ),
                    )
                )

            try:
                for item in odm_item_group_items:
                    self._repos.odm_item_group_repository.add_relation(
                        uid=rs.uid,
                        relation_uid=item.uid,
                        relationship_type=RelationType.ITEM,
                        parameters={
                            "order_number": item.order_number,
                            "mandatory": strtobool(item.mandatory),
                            "data_entry_required": strtobool(item.data_entry_required),
                            "sdv": strtobool(item.sdv),
                            "locked": strtobool(item.locked),
                            "key_sequence": item.key_sequence,
                            "method_oid": item.method_oid,
                            "imputation_method_oid": item.imputation_method_oid,
                            "role": item.role,
                            "role_codelist_oid": item.role_codelist_oid,
                            "collection_exception_condition_oid": item.collection_exception_condition_oid,
                        },
                    )
            except ValueError as exception:
                raise exceptions.ValidationException(exception.args[0])

            self._approve(
                self._repos.odm_item_group_repository, self.odm_item_group_service, rs
            )

    def _create_forms_with_relations(self):
        for form_def in self.form_defs:
            descriptions = self._extract_descriptions(form_def)

            rs = self._create(
                self._repos.odm_form_repository,
                self.odm_form_service,
                self.db_forms,
                OdmFormPostInput(
                    oid=form_def.getAttribute("OID"),
                    name=form_def.getAttribute("Name")
                    + "@"
                    + form_def.getAttribute("OID"),
                    sdtm_version="",
                    repeating=form_def.getAttribute("Repeating"),
                    scope_uid=None,
                    descriptions=[
                        self._create_description(
                            name=description["name"],
                            description=description["description"],
                            lang=description["lang"],
                        ).uid
                        for description in descriptions
                    ],
                    alias_uids=[],
                ),
            )

            odm_form_item_groups = []
            for item_group_ref in form_def.getElementsByTagName("ItemGroupRef"):
                odm_form_item_groups.append(
                    OdmFormItemGroupPostInput(
                        uid=next(
                            (
                                db_item_group.uid
                                for db_item_group in self.db_item_groups
                                if db_item_group.oid
                                == item_group_ref.getAttribute("ItemGroupOID")
                            ),
                            None,
                        ),
                        order_number=item_group_ref.getAttribute("OrderNumber"),
                        mandatory=item_group_ref.getAttribute("Mandatory"),
                        locked=item_group_ref.getAttribute("osb:locked") or "No",
                        collection_exception_condition_oid=item_group_ref.getAttribute(
                            "CollectionExceptionConditionOID"
                        ),
                    )
                )

            try:
                for item_group in odm_form_item_groups:
                    self._repos.odm_form_repository.add_relation(
                        uid=rs.uid,
                        relation_uid=item_group.uid,
                        relationship_type=RelationType.ITEM_GROUP,
                        parameters={
                            "order_number": item_group.order_number,
                            "mandatory": strtobool(item_group.mandatory),
                            "locked": strtobool(item_group.locked),
                            "collection_exception_condition_oid": item_group.collection_exception_condition_oid,
                        },
                    )
            except ValueError as exception:
                raise exceptions.ValidationException(exception.args[0])

            self._approve(self._repos.odm_form_repository, self.odm_form_service, rs)

    def _create_template_with_relations(self):
        if self.xml_document.getElementsByTagName("StudyName"):
            study_name = self.xml_document.getElementsByTagName("StudyName")[
                0
            ].firstChild.nodeValue
        else:
            study_name = f"@{int(time() * 1_000)}"

        rs = self._create(
            self._repos.odm_template_repository,
            self.odm_template_service,
            self.db_templates,
            OdmTemplatePostInput(
                oid=study_name,
                name=study_name,
                description=None,
                effective_date=None,
                retired_date=None,
            ),
        )

        odm_template_forms = []
        for db_form in self.db_forms:
            odm_template_forms.append(
                OdmTemplateFormPostInput(
                    uid=db_form.uid,
                    order_number=999999,
                    mandatory="yes",
                    locked="No",
                    collection_exception_condition_oid=None,
                )
            )

        try:
            for odm_template_form in odm_template_forms:
                self._repos.odm_template_repository.add_relation(
                    uid=rs.uid,
                    relation_uid=odm_template_form.uid,
                    relationship_type=RelationType.FORM,
                    parameters={
                        "order_number": odm_template_form.order_number,
                        "mandatory": strtobool(odm_template_form.mandatory),
                        "locked": strtobool(odm_template_form.locked),
                        "collection_exception_condition_oid": odm_template_form.collection_exception_condition_oid,
                    },
                )
        except ValueError as exception:
            raise exceptions.ValidationException(exception.args[0])

        self._approve(
            self._repos.odm_template_repository, self.odm_template_service, rs
        )

    def _create_description(
        self,
        name: Union[str, minidom.Text],
        description: Optional[str] = None,
        instruction: Optional[str] = None,
        lang: str = ENG_LANGUAGE,
    ):
        if isinstance(name, minidom.Text):
            name = name.nodeValue

        if description is None:
            description = "Please update this description"

        if instruction is None:
            instruction = "Please update this instruction"

        concept_input = OdmDescriptionPostInput(
            name=name,
            language=lang,
            description=description,
            instruction=instruction,
            sponsor_instruction=None,
        )

        library_vo = self.get_library(concept_input)

        try:
            concept_ar = self.odm_description_service._create_aggregate_root(
                concept_input=concept_input, library=library_vo
            )
            self._repos.odm_description_repository.save(concept_ar)
            self._approve(
                self._repos.odm_description_repository,
                self.odm_description_service,
                concept_ar,
            )
            return self.odm_description_service._transform_aggregate_root_to_pydantic_model(
                concept_ar
            )
        except ValueError as value_error:
            raise exceptions.ValidationException(value_error.args[0])

    def _extract_descriptions(self, elm):
        description_tag = elm.getElementsByTagName("Description")
        question_tag = elm.getElementsByTagName("Question")
        descriptions = []
        description_langs = []

        if description_tag:
            for translated_text in description_tag[0].getElementsByTagName(
                "TranslatedText"
            ):
                lang = translated_text.getAttribute("xml:lang")
                desc = translated_text.firstChild.nodeValue

                descriptions.append(
                    {
                        "lang": lang,
                        "name": desc,
                        "description": desc,
                    }
                )
                description_langs.append(lang)

        if question_tag:
            for translated_text in question_tag[0].getElementsByTagName(
                "TranslatedText"
            ):
                lang = translated_text.getAttribute("xml:lang")
                name = translated_text.firstChild

                if lang not in description_langs:
                    descriptions.append(
                        {
                            "lang": lang,
                            "name": name,
                            "description": None,
                        }
                    )
                else:
                    for description in descriptions:
                        if lang == description["lang"]:
                            description["name"] = name
                            break

        for description in descriptions:
            description["lang"] = get_iso_lang_data(
                description["lang"], "639-1", "639-2/B"
            ).upper()

        if elm.tagName in {"ConditionDef", "MethodDef"} and not any(
            description["lang"] == ENG_LANGUAGE for description in descriptions
        ):
            raise ValueError(
                f"An English OdmDescription must be provided for {elm.tagName} identified by OID ({elm.getAttribute('OID')})."
            )

        return descriptions

    def _get_newly_created_templates(self):
        try:
            rs, _ = self._repos.odm_template_repository.find_all(
                filter_by={
                    "uid": {
                        "v": [template.uid for template in self.db_templates],
                        "op": "eq",
                    }
                },
            )

            rs = sorted(rs, key=lambda elm: elm.name)
        except ValueError as e:
            raise exceptions.ValidationException(e)

        return [
            self.odm_template_service._transform_aggregate_root_to_pydantic_model(
                concept_ar
            )
            for concept_ar in rs
        ]

    def _get_newly_created_forms(self):
        try:
            rs, _ = self._repos.odm_form_repository.find_all(
                filter_by={
                    "uid": {
                        "v": [form.uid for form in self.db_forms],
                        "op": "eq",
                    }
                },
            )

            rs = sorted(rs, key=lambda elm: elm.name)
        except ValueError as e:
            raise exceptions.ValidationException(e)

        return [
            self.odm_form_service._transform_aggregate_root_to_pydantic_model(
                concept_ar
            )
            for concept_ar in rs
        ]

    def _get_newly_created_item_groups(self):
        try:
            rs, _ = self._repos.odm_item_group_repository.find_all(
                filter_by={
                    "uid": {
                        "v": [item_group.uid for item_group in self.db_item_groups],
                        "op": "eq",
                    }
                }
            )

            rs = sorted(rs, key=lambda elm: elm.name)
        except ValueError as e:
            raise exceptions.ValidationException(e)

        return [
            self.odm_item_group_service._transform_aggregate_root_to_pydantic_model(
                concept_ar
            )
            for concept_ar in rs
        ]

    def _get_newly_created_conditions(self):
        try:
            rs, _ = self._repos.odm_condition_repository.find_all(
                filter_by={
                    "uid": {
                        "v": [condition.uid for condition in self.db_conditions],
                        "op": "eq",
                    }
                }
            )

            rs = sorted(rs, key=lambda elm: elm.name)
        except ValueError as e:
            raise exceptions.ValidationException(e)

        return [
            self.odm_condition_service._transform_aggregate_root_to_pydantic_model(
                concept_ar
            )
            for concept_ar in rs
        ]

    def _get_newly_created_methods(self):
        try:
            rs, _ = self._repos.odm_method_repository.find_all(
                filter_by={
                    "uid": {
                        "v": [method.uid for method in self.db_methods],
                        "op": "eq",
                    }
                }
            )

            rs = sorted(rs, key=lambda elm: elm.name)
        except ValueError as e:
            raise exceptions.ValidationException(e)

        return [
            self.odm_method_service._transform_aggregate_root_to_pydantic_model(
                concept_ar
            )
            for concept_ar in rs
        ]

    def _get_newly_created_items(self):
        try:
            rs, _ = self._repos.odm_item_repository.find_all(
                filter_by={
                    "uid": {
                        "v": [item.uid for item in self.db_items],
                        "op": "eq",
                    }
                }
            )

            rs = sorted(rs, key=lambda elm: elm.name)
        except ValueError as e:
            raise exceptions.ValidationException(e)

        return [
            self.odm_item_service._transform_aggregate_root_to_pydantic_model(
                concept_ar
            )
            for concept_ar in rs
        ]

    def get_library(self, concept_input):
        if not self._repos.library_repository.library_exists(
            normalize_string(concept_input.library_name)
        ):
            raise exceptions.BusinessLogicException(
                f"There is no library identified by provided library name ({concept_input.library_name})"
            )

        return LibraryVO.from_input_values_2(
            library_name=concept_input.library_name,
            is_library_editable_callback=(
                lambda name: self._repos.library_repository.find_by_name(
                    name
                ).is_editable
                if self._repos.library_repository.find_by_name(name) is not None
                else None
            ),
        )

    def _create(self, repository, service, save_to, concept_input):
        library_vo = self.get_library(concept_input)

        try:
            concept_ar = service._create_aggregate_root(
                concept_input=concept_input, library=library_vo
            )
            repository.save(concept_ar)
            item = service._transform_aggregate_root_to_pydantic_model(concept_ar)
            save_to.append(item)
            return item
        except ValueError as e:
            raise exceptions.ValidationException(e.args[0])

    def _approve(self, repository, service, item):
        try:
            appr = service._find_by_uid_or_raise_not_found(item.uid, for_update=True)
            appr.approve(author=self.user_initials)
            repository.save(appr)
        except VersioningException as e:
            raise exceptions.BusinessLogicException(e.msg)

    @staticmethod
    def _get_codelist_submission_value(codelist):
        try:
            return (
                codelist.getElementsByTagName("Description")[0]
                .getElementsByTagName("TranslatedText")[0]
                .firstChild.nodeValue
            )
        except Exception as exc:
            raise exceptions.BusinessLogicException(
                f"Code Submission Value not provided for codelist identified by OID ({codelist.getAttribute('OID')})"
            ) from exc
