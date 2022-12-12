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
from clinical_mdr_api.domain_repositories.concepts.odms.odm_generic_repository import (
    OdmGenericRepository,
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
    OdmXmlExtensionAttributePostInput,
)
from clinical_mdr_api.models.ct_term_attributes import CTTermAttributes
from clinical_mdr_api.models.odm_common_models import OdmXmlExtensionRelationPostInput
from clinical_mdr_api.models.odm_condition import OdmCondition
from clinical_mdr_api.models.odm_form import OdmForm
from clinical_mdr_api.models.odm_item import OdmItem
from clinical_mdr_api.models.odm_item_group import OdmItemGroup
from clinical_mdr_api.models.odm_method import OdmMethod, OdmMethodPostInput
from clinical_mdr_api.models.odm_template import OdmTemplate
from clinical_mdr_api.models.odm_xml_extension import (
    OdmXmlExtension,
    OdmXmlExtensionPostInput,
)
from clinical_mdr_api.models.odm_xml_extension_attribute import OdmXmlExtensionAttribute
from clinical_mdr_api.models.odm_xml_extension_tag import (
    OdmXmlExtensionTag,
    OdmXmlExtensionTagPostInput,
)
from clinical_mdr_api.models.unit_definition import UnitDefinitionModel
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services._utils import normalize_string
from clinical_mdr_api.services.ct_term_attributes import CTTermAttributesService
from clinical_mdr_api.services.odm_conditions import OdmConditionService
from clinical_mdr_api.services.odm_descriptions import OdmDescriptionService
from clinical_mdr_api.services.odm_formal_expressions import OdmFormalExpressionService
from clinical_mdr_api.services.odm_forms import OdmFormService
from clinical_mdr_api.services.odm_item_groups import OdmItemGroupService
from clinical_mdr_api.services.odm_items import OdmItemService
from clinical_mdr_api.services.odm_methods import OdmMethodService
from clinical_mdr_api.services.odm_templates import OdmTemplateService
from clinical_mdr_api.services.odm_xml_extension_attributes import (
    OdmXmlExtensionAttributeService,
)
from clinical_mdr_api.services.odm_xml_extension_tags import OdmXmlExtensionTagService
from clinical_mdr_api.services.odm_xml_extensions import OdmXmlExtensionService
from clinical_mdr_api.services.unit_definition import UnitDefinitionService
from clinical_mdr_api.services.utils.odm_xml_mapper import map_xml


class OdmXmlImporterService:
    _repos: MetaRepository
    odm_xml_extension_service: OdmXmlExtensionService
    odm_xml_extension_attribute_service: OdmXmlExtensionAttributeService
    odm_xml_extension_tag_service: OdmXmlExtensionTagService
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

    user_initials: Optional[str]

    xml_document: minidom.Document
    form_defs: minicompat.NodeList
    item_group_defs: minicompat.NodeList
    item_defs: minicompat.NodeList
    condition_defs: minicompat.NodeList
    method_defs: minicompat.NodeList
    codelists: minicompat.NodeList
    measurement_units: minicompat.NodeList

    extension_prefixes: Dict[str, str]

    db_xml_extensions: Sequence[OdmXmlExtension]
    db_xml_extension_attributes: Sequence[OdmXmlExtensionAttribute]
    db_xml_extension_tags: Sequence[OdmXmlExtensionTag]
    db_templates: Sequence[OdmTemplate]
    db_forms: Sequence[OdmForm]
    db_item_groups: Sequence[OdmItemGroup]
    db_items: Sequence[OdmItem]
    db_conditions: Sequence[OdmCondition]
    db_methods: Sequence[OdmMethod]
    db_ct_term_attributes: Sequence[CTTermAttributes]
    db_unit_definitions: Sequence[UnitDefinitionModel]
    unit_definition_uids_by_ucum_uid: Dict[str, str]
    measurement_unit_names_by_oid: Dict[str, str]

    mapper: Optional[UploadFile] = None

    OSB_PREFIX = "osb"
    EXCLUDED_OSB_XML_EXTENSION_ATTRIBUTES = [
        "version",
        "lang",
        "locked",
        "sdv",
        "dataEntryRequired",
        "instruction",
        "sponsorInstruction",
    ]
    EXCLUDED_OSB_XML_EXTENSION_TAGS = ["DomainColor"]
    OSB_INSTRUCTION = f"{OSB_PREFIX}:instruction"
    OSB_SPONSOR_INSTRUCTION = f"{OSB_PREFIX}:sponsorInstruction"

    def __init__(self, xml: UploadFile, mapper: Optional[UploadFile]):
        if xml.content_type not in ["application/xml", "text/xml"]:
            raise exceptions.BusinessLogicException("Only XML format is supported.")

        self._repos = MetaRepository()
        self.odm_xml_extension_service = OdmXmlExtensionService()
        self.odm_xml_extension_attribute_service = OdmXmlExtensionAttributeService()
        self.odm_xml_extension_tag_service = OdmXmlExtensionTagService()
        self.odm_template_service = OdmTemplateService()
        self.odm_form_service = OdmFormService()
        self.odm_item_group_service = OdmItemGroupService()
        self.odm_item_service = OdmItemService()
        self.odm_condition_service = OdmConditionService()
        self.odm_method_service = OdmMethodService()
        self.odm_formal_expression_service = OdmFormalExpressionService()
        self.odm_description_service = OdmDescriptionService()
        self.ct_term_attributes_service = CTTermAttributesService()

        self.user_initials = "TODO user initials"

        self.extension_prefixes = {}
        self.db_xml_extensions = []
        self.db_xml_extension_attributes = []
        self.db_xml_extension_tags = []
        self.db_templates = []
        self.db_forms = []
        self.db_item_groups = []
        self.db_items = []
        self.db_conditions = []
        self.db_methods = []
        self.db_ct_term_attributes = []
        self.db_unit_definitions = []
        self.unit_definition_uids_by_ucum_uid = {}
        self.measurement_unit_names_by_oid = {}

        self.mapper = mapper

        self.xml_document = minidom.parseString(xml.file.read())

        map_xml(self.xml_document, mapper)

        self._set_def_elements()

    @db.transaction
    def store_odm_xml(self):
        self._set_xml_extensions()
        self._create_missing_xml_extensions()
        self._set_xml_extension_attributes()
        self._set_xml_extension_tags()
        self._set_unit_definitions()
        self._set_unit_definition_uids_by_ucum_uid()
        self._set_measurement_unit_names_by_oid()
        self._set_ct_term_attributes()
        self._create_methods_with_relations()
        self._create_conditions_with_relations()
        self._create_items_with_relations()
        self._create_item_groups_with_relations()
        self._create_forms_with_relations()
        self._create_template_with_relations()

        return {
            "xml_extensions": self._get_newly_created_xml_extensions(),
            "xml_extension_attributes": self._get_newly_created_xml_extension_attributes(),
            "xml_extension_tags": self._get_newly_created_xml_extension_tags(),
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

    def _set_xml_extensions(self):
        odm_tag = self.xml_document.getElementsByTagName("ODM")[0]
        for attribute in odm_tag.attributes.values():
            if attribute.prefix and attribute.localName != "odm":
                self.extension_prefixes[attribute.localName] = attribute.nodeValue

        rs, _ = self._repos.odm_xml_extension_repository.find_all(
            filter_by={
                "prefix": {"v": list(self.extension_prefixes.keys()), "op": "eq"}
            },
        )

        rs = sorted(rs, key=lambda elm: elm.name)

        self.db_xml_extensions = [
            self.odm_xml_extension_service._transform_aggregate_root_to_pydantic_model(
                concept_ar
            )
            for concept_ar in rs
        ]

    def _set_xml_extension_attributes(self):
        xml_extension_attribute_uids = []
        for db_xml_extension in self.db_xml_extensions:
            xml_extension_attribute_uids.extend(
                [
                    xml_extension_attribute.uid
                    for xml_extension_attribute in db_xml_extension.xml_extension_attributes
                ]
            )

        rs, _ = self._repos.odm_xml_extension_attribute_repository.find_all(
            filter_by={"uid": {"v": xml_extension_attribute_uids, "op": "eq"}},
        )

        rs = sorted(rs, key=lambda elm: elm.name)

        self.db_xml_extension_attributes = [
            self.odm_xml_extension_attribute_service._transform_aggregate_root_to_pydantic_model(
                concept_ar
            )
            for concept_ar in rs
        ]

    def _set_xml_extension_tags(self):
        xml_extension_tag_uids = []
        for db_xml_extension in self.db_xml_extensions:
            xml_extension_tag_uids.extend(
                [
                    xml_extension_tag.uid
                    for xml_extension_tag in db_xml_extension.xml_extension_tags
                ]
            )

        rs, _ = self._repos.odm_xml_extension_tag_repository.find_all(
            filter_by={"uid": {"v": xml_extension_tag_uids, "op": "eq"}},
        )

        rs = sorted(rs, key=lambda elm: elm.name)

        self.db_xml_extension_tags = [
            self.odm_xml_extension_tag_service._transform_aggregate_root_to_pydantic_model(
                concept_ar
            )
            for concept_ar in rs
        ]

    def _create_missing_xml_extensions(self):
        missing_prefixes = sorted(
            list(
                set(self.extension_prefixes.keys())
                - {
                    db_xml_extension.prefix
                    for db_xml_extension in self.db_xml_extensions
                }
            )
        )

        new_xml_extensions = []
        for missing_prefix in missing_prefixes:
            rs = self._create(
                self._repos.odm_xml_extension_repository,
                self.odm_xml_extension_service,
                new_xml_extensions,
                OdmXmlExtensionPostInput(
                    name=missing_prefix.upper(),
                    prefix=missing_prefix,
                    namespace=self.extension_prefixes[missing_prefix],
                ),
            )

            self._approve(
                self._repos.odm_xml_extension_repository,
                self.odm_xml_extension_service,
                rs,
            )

        self.db_xml_extensions.extend(new_xml_extensions)

    def _create_missing_xml_extension_attributes(self, elm_attributes):
        new_xml_extension_attributes = []

        for elm_attribute in elm_attributes:
            if not isinstance(elm_attribute, minidom.Attr) or not elm_attribute.prefix:
                continue

            if not self._attribute_exists(
                elm_attribute.prefix, elm_attribute.localName
            ):
                rs = self._create(
                    self._repos.odm_xml_extension_attribute_repository,
                    self.odm_xml_extension_attribute_service,
                    new_xml_extension_attributes,
                    OdmXmlExtensionAttributePostInput(
                        name=elm_attribute.localName,
                        xml_extension_uid=next(
                            db_xml_extension.uid
                            for db_xml_extension in self.db_xml_extensions
                            if db_xml_extension.prefix == elm_attribute.prefix
                        ),
                        xml_extension_tag_uid=None,
                    ),
                )

                self._approve(
                    self._repos.odm_xml_extension_attribute_repository,
                    self.odm_xml_extension_attribute_service,
                    rs,
                )

        self.db_xml_extension_attributes.extend(new_xml_extension_attributes)

    def _create_missing_xml_extension_tags(self, elm_tags):
        new_xml_extension_tags = []

        for elm_tag in elm_tags:
            if not isinstance(elm_tag, minidom.Element) or not elm_tag.prefix:
                continue

            if not self.tag_exists(elm_tag.prefix, elm_tag.localName):
                rs = self._create(
                    self._repos.odm_xml_extension_tag_repository,
                    self.odm_xml_extension_tag_service,
                    new_xml_extension_tags,
                    OdmXmlExtensionTagPostInput(
                        name=elm_tag.localName,
                        xml_extension_uid=next(
                            db_xml_extension.uid
                            for db_xml_extension in self.db_xml_extensions
                            if db_xml_extension.prefix == elm_tag.prefix
                        ),
                    ),
                )

                self._approve(
                    self._repos.odm_xml_extension_tag_repository,
                    self.odm_xml_extension_tag_service,
                    rs,
                )

        self.db_xml_extension_tags.extend(new_xml_extension_tags)

    def _create_missing_xml_extension_tag_attributes(self, elm_tags):
        for elm_tag in elm_tags:
            if not isinstance(elm_tag, minidom.Element) or not elm_tag.prefix:
                continue

            new_xml_extension_tag_attributes = []
            for tag_attribute in elm_tag.attributes.values():
                if (
                    not isinstance(tag_attribute, minidom.Attr)
                    or not tag_attribute.prefix
                ):
                    continue

                if not self._tag_attribute_exists(
                    tag_attribute.prefix, tag_attribute.localName
                ):
                    rs = self._create(
                        self._repos.odm_xml_extension_attribute_repository,
                        self.odm_xml_extension_attribute_service,
                        new_xml_extension_tag_attributes,
                        OdmXmlExtensionAttributePostInput(
                            name=tag_attribute.localName,
                            xml_extension_uid=None,
                            xml_extension_tag_uid=next(
                                db_xml_extension_tag.uid
                                for db_xml_extension_tag in self.db_xml_extension_tags
                                if db_xml_extension_tag.xml_extension.prefix
                                == tag_attribute.prefix
                                and db_xml_extension_tag.name == elm_tag.localName
                            ),
                        ),
                    )

                    self._approve(
                        self._repos.odm_xml_extension_attribute_repository,
                        self.odm_xml_extension_attribute_service,
                        rs,
                    )

            self.db_xml_extension_attributes.extend(new_xml_extension_tag_attributes)

    def _create_relationship_for_xml_extension_attributes(
        self,
        uid: str,
        elm_attributes,
        repository: OdmGenericRepository,
    ):
        odm_xml_extension_relations: Sequence[OdmXmlExtensionRelationPostInput] = []
        for elm_attribute in elm_attributes:
            if (
                not isinstance(elm_attribute, minidom.Attr)
                or not elm_attribute.prefix
                or (
                    elm_attribute.prefix == self.OSB_PREFIX
                    and elm_attribute.localName
                    in self.EXCLUDED_OSB_XML_EXTENSION_ATTRIBUTES
                )
            ):
                continue

            xml_extension_attribute_uid = next(
                db_xml_extension_attribute.uid
                for db_xml_extension_attribute in self.db_xml_extension_attributes
                if elm_attribute.localName == db_xml_extension_attribute.name
                and (
                    db_xml_extension_attribute.xml_extension
                    and elm_attribute.prefix
                    == db_xml_extension_attribute.xml_extension.prefix
                )
            )

            odm_xml_extension_relations.append(
                OdmXmlExtensionRelationPostInput(
                    uid=xml_extension_attribute_uid, value=elm_attribute.nodeValue
                )
            )

        try:
            for odm_xml_extension_relation in odm_xml_extension_relations:
                repository.add_relation(
                    uid=uid,
                    relation_uid=odm_xml_extension_relation.uid,
                    relationship_type=RelationType.XML_EXTENSION_ATTRIBUTE,
                    parameters={"value": odm_xml_extension_relation.value},
                )
        except ValueError as exception:
            raise exceptions.ValidationException(exception.args[0])

    def _create_relationship_for_xml_extension_tags(
        self,
        uid: str,
        elm_tags,
        repository: OdmGenericRepository,
    ):
        odm_xml_extension_relations: Sequence[OdmXmlExtensionRelationPostInput] = []
        for elm_tag in elm_tags:
            if (
                not isinstance(elm_tag, minidom.Element)
                or not elm_tag.prefix
                or (
                    elm_tag.prefix == self.OSB_PREFIX
                    and elm_tag.localName in self.EXCLUDED_OSB_XML_EXTENSION_TAGS
                )
            ):
                continue

            xml_extension_tag_uid = next(
                db_xml_extension_tag.uid
                for db_xml_extension_tag in self.db_xml_extension_tags
                if elm_tag.localName == db_xml_extension_tag.name
                and (
                    db_xml_extension_tag.xml_extension
                    and elm_tag.prefix == db_xml_extension_tag.xml_extension.prefix
                )
            )

            odm_xml_extension_relations.append(
                OdmXmlExtensionRelationPostInput(
                    uid=xml_extension_tag_uid,
                    value=elm_tag.firstChild.nodeValue if elm_tag.firstChild else "",
                )
            )

        try:
            for odm_xml_extension_relation in odm_xml_extension_relations:
                repository.add_relation(
                    uid=uid,
                    relation_uid=odm_xml_extension_relation.uid,
                    relationship_type=RelationType.XML_EXTENSION_TAG,
                    parameters={"value": odm_xml_extension_relation.value},
                )
        except ValueError as exception:
            raise exceptions.ValidationException(exception.args[0])

    def _create_relationship_for_xml_extension_tag_attributes(
        self,
        uid: str,
        elm_tags,
        repository: OdmGenericRepository,
    ):
        for elm_tag in elm_tags:
            if (
                not isinstance(elm_tag, minidom.Element)
                or not elm_tag.prefix
                or (
                    elm_tag.prefix == self.OSB_PREFIX
                    and elm_tag.localName in self.EXCLUDED_OSB_XML_EXTENSION_TAGS
                )
            ):
                continue

            odm_xml_extension_relations: Sequence[OdmXmlExtensionRelationPostInput] = []
            for tag_attribute in elm_tag.attributes.values():
                if (
                    not isinstance(tag_attribute, minidom.Attr)
                    or not tag_attribute.prefix
                    or (
                        tag_attribute.prefix == self.OSB_PREFIX
                        and tag_attribute.localName
                        in self.EXCLUDED_OSB_XML_EXTENSION_ATTRIBUTES
                    )
                ):
                    continue

                xml_extension_tag_attribute_uid = next(
                    db_xml_extension_attribute.uid
                    for db_xml_extension_attribute in self.db_xml_extension_attributes
                    if tag_attribute.localName == db_xml_extension_attribute.name
                    and (
                        db_xml_extension_attribute.xml_extension_tag
                        and tag_attribute.prefix
                        == next(
                            (
                                db_xml_extension_tag.xml_extension.prefix
                                for db_xml_extension_tag in self.db_xml_extension_tags
                                if db_xml_extension_tag.uid
                                == db_xml_extension_attribute.xml_extension_tag.uid
                            ),
                            None,
                        )
                    )
                )

                odm_xml_extension_relations.append(
                    OdmXmlExtensionRelationPostInput(
                        uid=xml_extension_tag_attribute_uid,
                        value=tag_attribute.nodeValue,
                    )
                )

            try:
                for odm_xml_extension_relation in odm_xml_extension_relations:
                    repository.add_relation(
                        uid=uid,
                        relation_uid=odm_xml_extension_relation.uid,
                        relationship_type=RelationType.XML_EXTENSION_TAG_ATTRIBUTE,
                        parameters={"value": odm_xml_extension_relation.value},
                    )
            except ValueError as exception:
                raise exceptions.ValidationException(exception.args[0])

    def _set_unit_definitions(self):
        measurement_unit_oids = {
            measurement_unit.getAttribute("OID")
            for measurement_unit in self.measurement_units
        }

        rs, _ = self._repos.unit_definition_repository.find_all(
            filter_by={"name": {"v": measurement_unit_oids, "op": "eq"}},
        )

        rs_names = {item.name for item in rs}

        non_existing_measurement_unit_oids = measurement_unit_oids - rs_names

        if non_existing_measurement_unit_oids:
            raise exceptions.BusinessLogicException(
                f"MeasurementUnits identified by following OIDs {non_existing_measurement_unit_oids} don't match any Unit Definition."
            )

        self.db_unit_definitions = [
            UnitDefinitionModel.from_unit_definition_ar(
                unit_definition_ar,
                find_term_by_uid=self._repos.ct_term_name_repository.find_by_uid,
                find_dictionary_term_by_uid=self._repos.dictionary_term_generic_repository.find_by_uid,
            )
            for unit_definition_ar in rs
        ]

    def _set_unit_definition_uids_by_ucum_uid(self):
        self.unit_definition_uids_by_ucum_uid = {
            db_unit_definition.ucum.term_uid: db_unit_definition.uid
            for db_unit_definition in self.db_unit_definitions
            if db_unit_definition.ucum
        }

    def _set_measurement_unit_names_by_oid(self):
        self.measurement_unit_names_by_oid = {
            measurement_unit.getAttribute("OID"): measurement_unit.getAttribute("Name")
            for measurement_unit in self.measurement_units
        }

    def _set_ct_term_attributes(self):
        rs = self._repos.ct_term_attributes_repository.find_all(
            filter_by={
                "nci_preferred_name": {
                    "v": [
                        domain.split(":", 1)[-1]
                        for item_group_def in self.item_group_defs
                        for domain in item_group_def.getAttribute("Domain").split("|")
                        if domain
                    ],
                    "op": "eq",
                }
            }
        )

        self.db_ct_term_attributes = [
            self.ct_term_attributes_service._transform_aggregate_root_to_pydantic_model(
                ct_codelist_ar
            )
            for ct_codelist_ar in rs.items
        ]

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
                            lang=description["lang"],
                            description=description["description"],
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
            self._create_missing_xml_extension_attributes(item_def.attributes.values())
            self._create_missing_xml_extension_tags(item_def.childNodes)
            self._create_missing_xml_extension_tag_attributes(item_def.childNodes)

            unit_definitions = [
                OdmItemUnitDefinitionRelationshipInput(
                    uid=self.unit_definition_uids_by_ucum_uid[
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

            rs = self._create(
                self._repos.odm_item_repository,
                self.odm_item_service,
                self.db_items,
                OdmItemPostInput(
                    oid=item_def.getAttribute("OID"),
                    name=item_def.getAttribute("Name"),
                    prompt=item_def.getAttribute("Prompt"),
                    datatype=item_def.getAttribute("DataType"),
                    length=item_def.getAttribute("Length"),
                    significant_digits=None,
                    sas_field_name=item_def.getAttribute("SASFieldName"),
                    sds_var_name=item_def.getAttribute("SDSVarName"),
                    origin=item_def.getAttribute("Origin"),
                    comment=None,
                    descriptions=[
                        self._create_description(
                            name=description["name"],
                            lang=description["lang"],
                            description=description["description"],
                            instruction=item_def.getAttribute(self.OSB_INSTRUCTION),
                            sponsor_instruction=item_def.getAttribute(
                                self.OSB_SPONSOR_INSTRUCTION
                            ),
                        ).uid
                        for description in descriptions
                    ],
                    alias_uids=[],
                    unit_definitions=unit_definitions,
                    codelist_uid=codelist.getAttribute("Name") if codelist else None,
                    terms=[],
                ),
            )

            self.odm_item_service._manage_terms(
                rs.uid,
                [
                    OdmItemTermRelationshipInput(
                        uid=codelist_item.getAttribute("osb:OID"),
                        mandatory=codelist_item.getAttribute("Mandatory"),
                        order=codelist_item.getAttribute("OrderNumber"),
                    )
                    for codelist_item in codelist.getElementsByTagName("CodeListItem")
                ]
                if codelist
                else [],
            )
            self.odm_item_service._manage_unit_definitions(rs.uid, unit_definitions)

            self._create_relationship_for_xml_extension_attributes(
                rs.uid, item_def.attributes.values(), self._repos.odm_item_repository
            )
            self._create_relationship_for_xml_extension_tags(
                rs.uid, item_def.childNodes, self._repos.odm_item_repository
            )
            self._create_relationship_for_xml_extension_tag_attributes(
                rs.uid, item_def.childNodes, self._repos.odm_item_repository
            )
            self._approve(self._repos.odm_item_repository, self.odm_item_service, rs)

    def _create_item_groups_with_relations(self):
        for item_group_def in self.item_group_defs:
            descriptions = self._extract_descriptions(item_group_def)
            self._create_missing_xml_extension_attributes(
                item_group_def.attributes.values()
            )
            self._create_missing_xml_extension_tags(item_group_def.childNodes)
            self._create_missing_xml_extension_tag_attributes(item_group_def.childNodes)

            rs = self._create(
                self._repos.odm_item_group_repository,
                self.odm_item_group_service,
                self.db_item_groups,
                OdmItemGroupPostInput(
                    oid=item_group_def.getAttribute("OID"),
                    name=item_group_def.getAttribute("Name"),
                    origin=item_group_def.getAttribute("Origin"),
                    repeating=item_group_def.getAttribute("Repeating"),
                    is_reference_data="no",  # missing in odm
                    purpose=item_group_def.getAttribute("Purpose"),
                    sas_dataset_name=item_group_def.getAttribute("SASDatasetName"),
                    comment=None,
                    descriptions=[
                        self._create_description(
                            name=description["name"],
                            lang=description["lang"],
                            description=description["description"],
                            instruction=item_group_def.getAttribute(
                                self.OSB_INSTRUCTION
                            ),
                            sponsor_instruction=item_group_def.getAttribute(
                                self.OSB_SPONSOR_INSTRUCTION
                            ),
                        ).uid
                        for description in descriptions
                    ],
                    alias_uids=[],
                    sdtm_domain_uids=[
                        db_ct_term_attribute.term_uid
                        for db_ct_term_attribute in self.db_ct_term_attributes
                        for domain in item_group_def.getAttribute("Domain").split("|")
                        if domain
                        and domain.split(":", 1)[-1]
                        == db_ct_term_attribute.nci_preferred_name
                    ],
                ),
            )

            self._create_relationship_for_xml_extension_attributes(
                rs.uid,
                item_group_def.attributes.values(),
                self._repos.odm_item_group_repository,
            )
            self._create_relationship_for_xml_extension_tags(
                rs.uid, item_group_def.childNodes, self._repos.odm_item_group_repository
            )
            self._create_relationship_for_xml_extension_tag_attributes(
                rs.uid, item_group_def.childNodes, self._repos.odm_item_group_repository
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
            self._create_missing_xml_extension_attributes(form_def.attributes.values())
            self._create_missing_xml_extension_tags(form_def.childNodes)
            self._create_missing_xml_extension_tag_attributes(form_def.childNodes)

            rs = self._create(
                self._repos.odm_form_repository,
                self.odm_form_service,
                self.db_forms,
                OdmFormPostInput(
                    oid=form_def.getAttribute("OID"),
                    name=form_def.getAttribute("Name"),
                    sdtm_version="",
                    repeating=form_def.getAttribute("Repeating"),
                    scope_uid=None,
                    descriptions=[
                        self._create_description(
                            name=description["name"],
                            lang=description["lang"],
                            description=description["description"],
                            instruction=form_def.getAttribute(self.OSB_INSTRUCTION),
                            sponsor_instruction=form_def.getAttribute(
                                self.OSB_SPONSOR_INSTRUCTION
                            ),
                        ).uid
                        for description in descriptions
                    ],
                    alias_uids=[],
                ),
            )

            self._create_relationship_for_xml_extension_attributes(
                rs.uid, form_def.attributes.values(), self._repos.odm_form_repository
            )
            self._create_relationship_for_xml_extension_tags(
                rs.uid, form_def.childNodes, self._repos.odm_form_repository
            )
            self._create_relationship_for_xml_extension_tag_attributes(
                rs.uid, form_def.childNodes, self._repos.odm_form_repository
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
        lang: str = ENG_LANGUAGE,
        description: Optional[str] = None,
        instruction: Optional[str] = None,
        sponsor_instruction: Optional[str] = None,
    ):
        if isinstance(name, minidom.Text):
            name = name.nodeValue

        if not description:
            description = "Please update this description"

        if not instruction:
            instruction = "Please update this instruction"

        if not sponsor_instruction:
            sponsor_instruction = "Please update this sponsor instruction"

        concept_input = OdmDescriptionPostInput(
            name=name,
            language=lang,
            description=description,
            instruction=instruction if lang == ENG_LANGUAGE else None,
            sponsor_instruction=sponsor_instruction if lang == ENG_LANGUAGE else None,
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

    def _get_newly_created_xml_extensions(self):
        try:
            rs, _ = self._repos.odm_xml_extension_repository.find_all(
                filter_by={
                    "uid": {
                        "v": [
                            xml_extension.uid
                            for xml_extension in self.db_xml_extensions
                        ],
                        "op": "eq",
                    }
                },
            )

            rs = sorted(rs, key=lambda elm: elm.name)
        except ValueError as e:
            raise exceptions.ValidationException(e)

        return [
            self.odm_xml_extension_service._transform_aggregate_root_to_pydantic_model(
                concept_ar
            )
            for concept_ar in rs
        ]

    def _get_newly_created_xml_extension_attributes(self):
        try:
            rs, _ = self._repos.odm_xml_extension_attribute_repository.find_all(
                filter_by={
                    "uid": {
                        "v": [
                            xml_extension_attribute.uid
                            for xml_extension_attribute in self.db_xml_extension_attributes
                        ],
                        "op": "eq",
                    }
                },
            )

            rs = sorted(rs, key=lambda elm: elm.name)
        except ValueError as e:
            raise exceptions.ValidationException(e)

        return [
            self.odm_xml_extension_attribute_service._transform_aggregate_root_to_pydantic_model(
                concept_ar
            )
            for concept_ar in rs
        ]

    def _get_newly_created_xml_extension_tags(self):
        try:
            rs, _ = self._repos.odm_xml_extension_tag_repository.find_all(
                filter_by={
                    "uid": {
                        "v": [
                            xml_extension_tag.uid
                            for xml_extension_tag in self.db_xml_extension_tags
                        ],
                        "op": "eq",
                    }
                },
            )

            rs = sorted(rs, key=lambda elm: elm.name)
        except ValueError as e:
            raise exceptions.ValidationException(e)

        return [
            self.odm_xml_extension_tag_service._transform_aggregate_root_to_pydantic_model(
                concept_ar
            )
            for concept_ar in rs
        ]

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

    def _attribute_exists(self, prefix, attribute_name):
        if (
            prefix == self.OSB_PREFIX
            and attribute_name in self.EXCLUDED_OSB_XML_EXTENSION_ATTRIBUTES
        ):
            return True

        for db_xml_extension_attribute in self.db_xml_extension_attributes:
            if attribute_name == db_xml_extension_attribute.name and (
                db_xml_extension_attribute.xml_extension
                and prefix == db_xml_extension_attribute.xml_extension.prefix
            ):
                return True
        return False

    def tag_exists(self, prefix, tag_name):
        if (
            prefix == self.OSB_PREFIX
            and tag_name in self.EXCLUDED_OSB_XML_EXTENSION_TAGS
        ):
            return True

        for db_xml_extension_tag in self.db_xml_extension_tags:
            if tag_name == db_xml_extension_tag.name and (
                db_xml_extension_tag.xml_extension
                and prefix == db_xml_extension_tag.xml_extension.prefix
            ):
                return True
        return False

    def _tag_attribute_exists(self, prefix, attribute_name):
        if (
            prefix == self.OSB_PREFIX
            and attribute_name in self.EXCLUDED_OSB_XML_EXTENSION_ATTRIBUTES
        ):
            return True

        for db_xml_extension_attribute in self.db_xml_extension_attributes:
            if attribute_name == db_xml_extension_attribute.name and (
                db_xml_extension_attribute.xml_extension_tag
                and prefix
                == next(
                    (
                        db_xml_extension_tag.xml_extension.prefix
                        for db_xml_extension_tag in self.db_xml_extension_tags
                        if db_xml_extension_tag.uid
                        == db_xml_extension_attribute.xml_extension_tag.uid
                    ),
                    None,
                )
            ):
                return True
        return False
