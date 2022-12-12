from datetime import datetime, timezone
from time import time
from typing import Dict, Optional, Sequence, Union
from xml.dom.minidom import Document

from fastapi import UploadFile

from clinical_mdr_api.domain._utils import ObjectStatus, get_iso_lang_data
from clinical_mdr_api.domain.concepts.odms.odm_xml_definition import (
    ODM,
    Alias,
    Attribute,
    BasicDefinitions,
    CodeList,
    CodeListItem,
    CodeListRef,
    ConditionDef,
    Decode,
    Description,
    FormalExpression,
    FormDef,
    GlobalVariables,
    ItemDef,
    ItemGroupDef,
    ItemGroupRef,
    ItemRef,
    MeasurementUnit,
    MeasurementUnitRef,
    MetaDataVersion,
    OsbDomainColor,
    ProtocolName,
    Question,
    Study,
    StudyDescription,
    StudyName,
    Symbol,
    Tag,
    TranslatedText,
)
from clinical_mdr_api.domain.concepts.utils import ENG_LANGUAGE, TargetType
from clinical_mdr_api.models.odm_form import OdmForm
from clinical_mdr_api.models.odm_item import OdmItem
from clinical_mdr_api.models.odm_item_group import OdmItemGroup
from clinical_mdr_api.services.odm_data_extractor import OdmDataExtractor
from clinical_mdr_api.services.utils.odm_xml_mapper import map_xml


class OdmXmlExporterService:
    odm_data_extractor: OdmDataExtractor
    xml_document: Document
    odm: ODM
    used_xml_extensions: Dict[str, dict]
    allowed_extensions: Sequence[str]

    mapper: Optional[UploadFile] = None

    XML_LANG = "xml:lang"
    OSB_VERSION = "osb:version"
    OSB_LANG = "osb:lang"
    OSB_INSTRUCTION = "osb:instruction"
    OSB_SPONSOR_INSTRUCTION = "osb:sponsorInstruction"

    def __init__(
        self,
        target_uid: str,
        target_type: TargetType,
        status: Sequence[ObjectStatus],
        allowed_extensions: Sequence[str],
        stylesheet: Optional[str],
        mapper: Optional[UploadFile],
        unit_definition_service,
    ):
        self.odm_data_extractor = OdmDataExtractor(
            target_uid,
            target_type,
            [elm.name for elm in status],
            unit_definition_service,
        )
        self.mapper = mapper
        self.allowed_extensions = allowed_extensions
        self.used_xml_extensions = {}

        for uid, ext in self.odm_data_extractor.odm_xml_extensions.items():
            if not self.allowed_extensions:
                self.used_xml_extensions[uid] = ext
            else:
                for allowed in self.allowed_extensions:
                    if allowed == ext["prefix"]:
                        self.used_xml_extensions[uid] = ext

        self.odm = self._create_odm_object()
        self.xml_document = Document()
        if stylesheet:
            self.xml_document.appendChild(
                self.xml_document.createProcessingInstruction(
                    "xml-stylesheet", f'type="text/xsl" href="{stylesheet}"'
                )
            )

    def get_odm_xml(self):
        doc = self._generate_odm_xml(self.odm, self.xml_document)

        map_xml(self.xml_document, self.mapper)

        return doc.toprettyxml(encoding="utf-8")

    def _generate_odm_xml(self, odm_element, current_xml_element):
        if hasattr(odm_element, "_custom_tag_name") and isinstance(
            odm_element._custom_tag_name, str
        ):
            new_xml_element = self.xml_document.createElement(
                odm_element._custom_tag_name
            )
        else:
            new_xml_element = self.xml_document.createElement(
                odm_element.__class__.__name__
            )

        attributes = odm_element.__dict__.items()

        for attribute_name, attribute_value in attributes:
            if isinstance(attribute_value, Attribute):
                attribute_value.value = str(attribute_value.value)
                if ":" in attribute_value.name:
                    prefix, _ = attribute_value.name.split(":")
                    new_xml_element.setAttributeNS(
                        prefix, attribute_value.name, attribute_value.value
                    )
                else:
                    new_xml_element.setAttribute(
                        attribute_value.name, attribute_value.value
                    )
            elif isinstance(attribute_value, str):
                if attribute_name == "_custom_tag_name":
                    continue
                new_xml_element.appendChild(
                    self.xml_document.createTextNode(attribute_value)
                )
            elif isinstance(attribute_value, list):
                for odm_element_from_list in attribute_value:
                    self._generate_odm_xml(odm_element_from_list, new_xml_element)
            else:
                self._generate_odm_xml(attribute_value, new_xml_element)

        current_xml_element.appendChild(new_xml_element)

        return self.xml_document

    def _get_osb_elm_or_none_value(self, elm: Union[list, dict]):
        if not self.allowed_extensions or "osb" in self.allowed_extensions:
            return elm

        if isinstance(elm, list):
            return []

        if isinstance(elm, dict):
            return {}

        return None

    def _create_xml_extension_attributes_of(
        self, target: Union[OdmForm, OdmItemGroup, OdmItem]
    ) -> Dict[str, Attribute]:
        attributes = {}

        for xml_extension_attribute in target.xml_extension_attributes:
            odm_xml_extension = self.odm_data_extractor.odm_xml_extensions[
                xml_extension_attribute.xml_extension_uid
            ]
            if not self.allowed_extensions or (
                odm_xml_extension["prefix"] in self.allowed_extensions
            ):
                attributes[xml_extension_attribute.name] = Attribute(
                    f"{odm_xml_extension['prefix']}:{xml_extension_attribute.name}",
                    xml_extension_attribute.value,
                )

        return attributes

    def _create_xml_extension_tags_of(
        self, target: Union[OdmForm, OdmItemGroup, OdmItem]
    ) -> Dict[str, Tag]:
        tags = {}

        for xml_extension_tag in target.xml_extension_tags:
            odm_xml_extension_tag = self.odm_data_extractor.odm_xml_extension_tags[
                xml_extension_tag.uid
            ]["xml_extension"]
            if not self.allowed_extensions or (
                odm_xml_extension_tag["prefix"] in self.allowed_extensions
            ):
                tags[xml_extension_tag.name] = Tag(
                    _custom_tag_name=f"{self.odm_data_extractor.odm_xml_extension_tags[xml_extension_tag.uid]['xml_extension']['prefix']}"
                    f":{xml_extension_tag.name}",
                    _string=xml_extension_tag.value,
                    **{
                        xml_extension_tag_attribute.name: Attribute(
                            # pylint:disable=line-too-long
                            f"{self.odm_data_extractor.odm_xml_extension_tags[xml_extension_tag_attribute.xml_extension_tag_uid]['xml_extension']['prefix']}:{xml_extension_tag_attribute.name}",
                            xml_extension_tag_attribute.value,
                        )
                        for xml_extension_tag_attribute in target.xml_extension_tag_attributes
                        if xml_extension_tag_attribute.xml_extension_tag_uid
                        == xml_extension_tag.uid
                    },
                )

        return tags

    def _create_odm_object(self):
        def create_odm_form_def():
            return [
                FormDef(
                    oid=Attribute("OID", form.oid),
                    name=Attribute("Name", form.name),
                    repeating=Attribute("Repeating", form.repeating),
                    **self._get_osb_elm_or_none_value(
                        {
                            "version": Attribute(self.OSB_VERSION, form.version),
                            "instruction": Attribute(
                                self.OSB_INSTRUCTION,
                                next(
                                    (
                                        description.instruction
                                        for description in form.descriptions
                                        if description.language == ENG_LANGUAGE
                                        and description.instruction
                                    ),
                                    None,
                                ),
                            ),
                            "sponsor_instruction": Attribute(
                                self.OSB_SPONSOR_INSTRUCTION,
                                next(
                                    (
                                        description.sponsor_instruction
                                        for description in form.descriptions
                                        if description.language == ENG_LANGUAGE
                                        and description.sponsor_instruction
                                    ),
                                    None,
                                ),
                            ),
                        }
                    ),
                    **self._create_xml_extension_attributes_of(form),
                    **self._create_xml_extension_tags_of(form),
                    description=Description(
                        [
                            TranslatedText(
                                description.description,
                                lang=Attribute(
                                    self.XML_LANG,
                                    get_iso_lang_data(
                                        q=description.language, return_key="639-1"
                                    ),
                                ),
                                **self._get_osb_elm_or_none_value(
                                    {
                                        "version": Attribute(
                                            self.OSB_VERSION, description.version
                                        )
                                    }
                                ),
                            )
                            for description in form.descriptions
                            if description.description
                        ]
                    ),
                    aliases=[
                        Alias(
                            name=Attribute("Name", alias.name),
                            context=Attribute("Context", alias.context),
                            **self._get_osb_elm_or_none_value(
                                {"version": Attribute(self.OSB_VERSION, alias.version)}
                            ),
                        )
                        for alias in form.aliases
                    ],
                    item_group_refs=[
                        ItemGroupRef(
                            item_group_oid=Attribute("ItemGroupOID", item_group.oid),
                            mandatory=Attribute("Mandatory", item_group.mandatory),
                            order_number=Attribute(
                                "OrderNumber", item_group.order_number
                            ),
                            collection_exception_condition_oid=Attribute(
                                "CollectionExceptionConditionOID",
                                item_group.collection_exception_condition_oid,
                            ),
                            **self._get_osb_elm_or_none_value(
                                {"locked": Attribute("osb:locked", item_group.locked)}
                            ),
                        )
                        for item_group in form.item_groups
                    ],
                )
                for form in self.odm_data_extractor.odm_forms
            ]

        def create_odm_item_group_def():
            SDTM_MSG_COLOURS = ["#bfffff", "#ffff96", "#96ff96", "#ffbf9c"]

            return [
                ItemGroupDef(
                    oid=Attribute("OID", item_group.oid),
                    name=Attribute("Name", item_group.name),
                    purpose=Attribute("Purpose", item_group.purpose),
                    repeating=Attribute("Repeating", item_group.repeating),
                    sas_dataset_name=Attribute(
                        "SASDatasetName", item_group.sas_dataset_name
                    ),
                    domain=Attribute(
                        "Domain",
                        "|".join(
                            [
                                f"{sdtm_domain.code_submission_value}:{sdtm_domain.preferred_term}"
                                for sdtm_domain in item_group.sdtm_domains
                            ]
                        ),
                    )
                    if item_group.sdtm_domains
                    else "",
                    **self._get_osb_elm_or_none_value(
                        {
                            "version": Attribute(self.OSB_VERSION, item_group.version),
                            "instruction": Attribute(
                                self.OSB_INSTRUCTION,
                                next(
                                    (
                                        description.instruction
                                        for description in item_group.descriptions
                                        if description.language == ENG_LANGUAGE
                                        and description.instruction
                                    ),
                                    None,
                                ),
                            ),
                            "sponsor_instruction": Attribute(
                                self.OSB_SPONSOR_INSTRUCTION,
                                next(
                                    (
                                        description.sponsor_instruction
                                        for description in item_group.descriptions
                                        if description.language == ENG_LANGUAGE
                                        and description.sponsor_instruction
                                    ),
                                    None,
                                ),
                            ),
                        }
                    ),
                    **self._create_xml_extension_attributes_of(item_group),
                    **self._create_xml_extension_tags_of(item_group),
                    osb_domain_colors=self._get_osb_elm_or_none_value(
                        [
                            OsbDomainColor(
                                f"{sdtm_domain.code_submission_value}:{SDTM_MSG_COLOURS[idx]};"
                            )
                            for idx, sdtm_domain in enumerate(item_group.sdtm_domains)
                        ]
                    )
                    if item_group.sdtm_domains
                    else [],
                    description=Description(
                        [
                            TranslatedText(
                                description.description,
                                lang=Attribute(
                                    self.XML_LANG,
                                    get_iso_lang_data(
                                        q=description.language, return_key="639-1"
                                    ),
                                ),
                                **self._get_osb_elm_or_none_value(
                                    {
                                        "version": Attribute(
                                            self.OSB_VERSION, description.version
                                        )
                                    }
                                ),
                            )
                            for description in item_group.descriptions
                            if description.description
                        ]
                    ),
                    aliases=[
                        Alias(
                            name=Attribute("Name", alias.name),
                            context=Attribute("Context", alias.context),
                            **self._get_osb_elm_or_none_value(
                                {"version": Attribute(self.OSB_VERSION, alias.version)}
                            ),
                        )
                        for alias in item_group.aliases
                    ],
                    item_refs=[
                        ItemRef(
                            item_oid=Attribute("ItemOID", item.oid),
                            mandatory=Attribute("Mandatory", item.mandatory),
                            order_number=Attribute("OrderNumber", item.order_number),
                            method_oid=Attribute("MethodOID", item.method_oid),
                            collection_exception_condition_oid=Attribute(
                                "CollectionExceptionConditionOID",
                                item.collection_exception_condition_oid,
                            ),
                            **self._get_osb_elm_or_none_value(
                                {
                                    "Sdv": Attribute("osb:sdv", item.sdv),
                                    "Locked": Attribute("osb:locked", item.locked),
                                    "DataEntryRequired": Attribute(
                                        "osb:dataEntryRequired",
                                        item.data_entry_required,
                                    ),
                                }
                            ),
                        )
                        for item in item_group.items
                    ],
                )
                for item_group in self.odm_data_extractor.odm_item_groups
            ]

        def create_odm_item_def():
            return [
                ItemDef(
                    oid=Attribute("OID", item.oid),
                    name=Attribute("Name", item.name),
                    origin=Attribute("Origin", item.origin),
                    datatype=Attribute("DataType", item.datatype.lower()),
                    length=Attribute("Length", item.length),
                    sas_field_name=Attribute("SASFieldName", item.sas_field_name),
                    sds_var_name=Attribute("SDSVarName", item.sds_var_name),
                    **self._get_osb_elm_or_none_value(
                        {
                            "version": Attribute(self.OSB_VERSION, item.version),
                            "instruction": Attribute(
                                self.OSB_INSTRUCTION,
                                next(
                                    (
                                        description.instruction
                                        for description in item.descriptions
                                        if description.language == ENG_LANGUAGE
                                        and description.instruction
                                    ),
                                    None,
                                ),
                            ),
                            "sponsor_instruction": Attribute(
                                self.OSB_SPONSOR_INSTRUCTION,
                                next(
                                    (
                                        description.sponsor_instruction
                                        for description in item.descriptions
                                        if description.language == ENG_LANGUAGE
                                        and description.sponsor_instruction
                                    ),
                                    None,
                                ),
                            ),
                        }
                    ),
                    **self._create_xml_extension_attributes_of(item),
                    **self._create_xml_extension_tags_of(item),
                    aliases=[
                        Alias(
                            name=Attribute("Name", alias.name),
                            context=Attribute("Context", alias.context),
                            **self._get_osb_elm_or_none_value(
                                {"version": Attribute(self.OSB_VERSION, alias.version)}
                            ),
                        )
                        for alias in item.aliases
                    ],
                    description=Description(
                        [
                            TranslatedText(
                                description.description,
                                lang=Attribute(
                                    self.XML_LANG,
                                    get_iso_lang_data(
                                        q=description.language, return_key="639-1"
                                    ),
                                ),
                                **self._get_osb_elm_or_none_value(
                                    {
                                        "version": Attribute(
                                            self.OSB_VERSION, description.version
                                        )
                                    }
                                ),
                            )
                            for description in item.descriptions
                            if description.description
                        ]
                    ),
                    question=Question(
                        [
                            TranslatedText(
                                description.name,
                                lang=Attribute(
                                    self.XML_LANG,
                                    get_iso_lang_data(
                                        q=description.language, return_key="639-1"
                                    ),
                                ),
                                **self._get_osb_elm_or_none_value(
                                    {
                                        "version": Attribute(
                                            self.OSB_VERSION, description.version
                                        )
                                    }
                                ),
                            )
                            for description in item.descriptions
                            if description.name
                        ]
                    ),
                    codelist_ref=CodeListRef(
                        codelist_oid=Attribute(
                            "CodeListOID",
                            f"{item.codelist.submission_value}@{item.oid}"
                            if item.codelist
                            else None,
                        )
                    ),
                    measurement_unit_refs=[
                        MeasurementUnitRef(
                            measurement_unit_oid=Attribute(
                                "MeasurementUnitOID", unit_definition.name
                            )
                        )
                        for unit_definition in item.unit_definitions
                    ],
                )
                for item in self.odm_data_extractor.odm_items
            ]

        def create_odm_condition_def():
            return [
                ConditionDef(
                    oid=Attribute("OID", condition.oid),
                    name=Attribute("Name", condition.name),
                    **self._get_osb_elm_or_none_value(
                        {"version": Attribute(self.OSB_VERSION, condition.version)}
                    ),
                    formal_expressions=[
                        FormalExpression(
                            _string=formal_expression.expression,
                            context=Attribute("Context", formal_expression.context),
                            **self._get_osb_elm_or_none_value(
                                {
                                    "version": Attribute(
                                        self.OSB_VERSION, formal_expression.version
                                    )
                                }
                            ),
                        )
                        for formal_expression in condition.formal_expressions
                    ],
                    aliases=[
                        Alias(
                            name=Attribute("Name", alias.name),
                            context=Attribute("Context", alias.context),
                            **self._get_osb_elm_or_none_value(
                                {"version": Attribute(self.OSB_VERSION, alias.version)}
                            ),
                        )
                        for alias in condition.aliases
                    ],
                    description=Description(
                        [
                            TranslatedText(
                                description.description,
                                lang=Attribute(
                                    self.XML_LANG,
                                    get_iso_lang_data(
                                        q=description.language, return_key="639-1"
                                    ),
                                ),
                                **self._get_osb_elm_or_none_value(
                                    {
                                        "version": Attribute(
                                            self.OSB_VERSION, description.version
                                        )
                                    }
                                ),
                            )
                            for description in condition.descriptions
                            if description.description
                        ]
                    ),
                )
                for condition in self.odm_data_extractor.odm_conditions
            ]

        def create_odm_codelist():
            codelists = []

            for codelist in self.odm_data_extractor.codelists:
                items = self.odm_data_extractor.get_items_by_codelist_uid(
                    codelist.codelist_uid
                )

                for item in items:
                    terms_by_uid = {
                        term.term_uid: {
                            "mandatory": term.mandatory,
                            "order": term.order,
                        }
                        for term in item.terms
                    }

                    codelists.append(
                        CodeList(
                            oid=Attribute(
                                "OID", f"{codelist.submission_value}@{item.oid}"
                            ),
                            name=Attribute("Name", codelist.codelist_uid),
                            datatype=Attribute("DataType", "string"),
                            sas_format_name=Attribute(
                                "SASFormatName", codelist.submission_value
                            ),
                            codelist_items=[
                                CodeListItem(
                                    coded_value=Attribute(
                                        "CodedValue",
                                        codelist_item["code_submission_value"],
                                    ),
                                    decode=Decode(
                                        TranslatedText(
                                            codelist_item["nci_preferred_name"],
                                            Attribute(
                                                self.XML_LANG,
                                                get_iso_lang_data(
                                                    q="eng", return_key="639-1"
                                                ),
                                            ),
                                        )
                                    ),
                                    order_number=Attribute(
                                        "OrderNumber",
                                        terms_by_uid.get(codelist_item["term_uid"]).get(
                                            "order"
                                        ),
                                    ),
                                    mandatory=Attribute(
                                        "Mandatory",
                                        terms_by_uid.get(codelist_item["term_uid"]).get(
                                            "mandatory"
                                        ),
                                    ),
                                    **self._get_osb_elm_or_none_value(
                                        {
                                            "OID": Attribute(
                                                "osb:OID", codelist_item["term_uid"]
                                            )
                                        }
                                    ),
                                )
                                for codelist_item in self.odm_data_extractor.ct_terms
                                if codelist.codelist_uid
                                == codelist_item["codelist_uid"]
                                and codelist_item["term_uid"] in terms_by_uid
                            ],
                        )
                    )

            return codelists

        def create_odm_measurement_unit():
            unit_definition_uids = []
            unit_definitions = []
            for unit_definition in self.odm_data_extractor.unit_definitions:
                if unit_definition.ucum is not None:
                    if unit_definition.ucum.term_uid in unit_definition_uids:
                        continue
                    unit_definition_uids.append(unit_definition.ucum.term_uid)
                    unit_definitions.append(
                        MeasurementUnit(
                            oid=Attribute("OID", unit_definition.name),
                            name=Attribute("Name", unit_definition.ucum.term_uid),
                            symbol=Symbol(
                                TranslatedText(
                                    unit_definition.name,
                                    lang=Attribute(
                                        self.XML_LANG,
                                        get_iso_lang_data(q="eng", return_key="639-1"),
                                    ),
                                )
                            ),
                        )
                    )

            return unit_definitions

        return ODM(
            odm_ns=Attribute("xmlns:odm", "http://www.cdisc.org/ns/odm/v1.3"),
            odm_version=Attribute("ODMVersion", "1.3.2"),
            file_type=Attribute("FileType", "Snapshot"),
            file_oid=Attribute("FileOID", f"OID.{int(time() * 1_000)}"),
            creation_date_time=Attribute(
                "CreationDateTime", datetime.now(timezone.utc)
            ),
            granularity=Attribute("Granularity", "All"),
            study=Study(
                oid=Attribute(
                    "OID",
                    f"{self.odm_data_extractor.target_name}-{self.odm_data_extractor.target_uid}",
                ),
                meta_data_version=MetaDataVersion(
                    oid=Attribute("OID", "MDV.0.1"),
                    name=Attribute("Name", "MDV.0.1"),
                    description=Attribute("Description", "Draft version"),
                    form_defs=create_odm_form_def(),
                    item_group_defs=create_odm_item_group_def(),
                    item_defs=create_odm_item_def(),
                    condition_defs=create_odm_condition_def(),
                    codelists=create_odm_codelist(),
                ),
                basic_definitions=BasicDefinitions(
                    measurement_units=create_odm_measurement_unit()
                ),
                global_variables=GlobalVariables(
                    protocol_name=ProtocolName(self.odm_data_extractor.target_name),
                    study_name=StudyName(self.odm_data_extractor.target_name),
                    study_description=StudyDescription(
                        self.odm_data_extractor.target_name
                    ),
                ),
            ),
            **{
                used_xml_extension["prefix"]: Attribute(
                    f"xmlns:{used_xml_extension['prefix']}",
                    used_xml_extension["namespace"],
                )
                for used_xml_extension in self.used_xml_extensions.values()
                if not self.allowed_extensions
                or used_xml_extension["prefix"] in self.allowed_extensions
            },
        )
