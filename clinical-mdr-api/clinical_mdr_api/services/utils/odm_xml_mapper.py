from codecs import iterdecode
from csv import DictReader
from typing import Optional
from xml.dom.minidom import Document

from fastapi import UploadFile

from clinical_mdr_api.exceptions import BusinessLogicException

MANDATORY_MAPPER_FIELDS = {
    "type",
    "parent",
    "from_name",
    "to_name",
    "to_alias",
    "from_alias",
    "alias_context",
}


def map_xml(xml_document: Document, mapper: Optional[UploadFile]):
    """
    Transform XML Tags and Attributes according to provided CSV mapper configuration.
    - Rename XML Tags and XML Attributes.
    - Create XML Alias Tag based on XML Attributes.
    """
    if not mapper:
        return

    if mapper.content_type != "text/csv":
        raise BusinessLogicException("Only CSV format is supported.")

    dict_reader = DictReader(iterdecode(mapper.file, "utf-8"))

    if not MANDATORY_MAPPER_FIELDS.issubset(dict_reader.fieldnames):
        raise BusinessLogicException(
            f"These headers must be present: {sorted(MANDATORY_MAPPER_FIELDS)}"
        )

    for mapping in dict_reader:
        parent = mapping["parent"] if mapping["parent"] else "*"

        if mapping["type"] == "attribute":
            _map_attributes(
                xml_document,
                mapping["from_name"],
                mapping["to_name"],
                parent,
                (mapping["to_alias"].casefold() == "true"),
            )
        elif mapping["type"] == "tag":
            _map_tags(
                xml_document,
                mapping["from_name"],
                mapping["to_name"],
                parent,
                (mapping["from_alias"].casefold() == "true"),
                mapping["alias_context"],
            )


def _get_tags(xml_document: Document, name: str, parent: str):
    if parent == "*":
        return xml_document.getElementsByTagName(name)

    tags = []
    parent_tags = xml_document.getElementsByTagName(parent)
    for parent_tag in parent_tags:
        tags += parent_tag.getElementsByTagName(name)
    return tags


def _map_tags(
    xml_document: Document,
    from_name: str,
    to_name: str,
    parent: str,
    from_alias: bool = False,
    alias_context: Optional[str] = None,
):
    tags = _get_tags(xml_document, from_name, parent)

    for tag in tags:
        if from_alias and alias_context == tag.getAttribute("Context"):
            tag.parentNode.setAttribute(
                tag.getAttribute("Context"), tag.getAttribute("Name")
            )
            tag.parentNode.removeChild(tag)
        else:
            tag.tagName = to_name
            tag.nodeName = to_name
            if ":" in to_name:
                prefix, _ = to_name.split(":")
                tag.prefix = prefix


def _map_attributes(
    xml_document: Document,
    from_name: str,
    to_name: str,
    parent: str,
    to_alias: bool = False,
):
    tags = xml_document.getElementsByTagName(parent)

    for tag in tags:
        tag_attribute_value = tag.getAttribute(from_name)
        if tag_attribute_value and to_alias:
            alias_tag = xml_document.createElement("Alias")
            alias_tag.setAttribute("Name", tag_attribute_value)
            alias_tag.setAttribute("Context", from_name)
            tag.appendChild(alias_tag)
        elif tag_attribute_value:
            tag.removeAttribute(from_name)
            if ":" in to_name:
                prefix, _ = to_name.split(":")
                tag.setAttributeNS(prefix, to_name, tag_attribute_value)
            else:
                tag.setAttribute(to_name, tag_attribute_value)
