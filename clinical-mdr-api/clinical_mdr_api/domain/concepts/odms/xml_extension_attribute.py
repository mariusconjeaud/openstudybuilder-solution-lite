from dataclasses import dataclass
from typing import Callable, Optional, Sequence, Tuple

from clinical_mdr_api.domain.concepts.concept_base import ConceptVO
from clinical_mdr_api.domain.concepts.odms.odm_ar_base import OdmARBase
from clinical_mdr_api.domain.concepts.odms.xml_extension import OdmXmlExtensionAR
from clinical_mdr_api.domain.concepts.odms.xml_extension_tag import OdmXmlExtensionTagAR
from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)
from clinical_mdr_api.exceptions import BusinessLogicException


@dataclass(frozen=True)
class OdmXmlExtensionAttributeVO(ConceptVO):
    data_type: str
    xml_extension_uid: Optional[str]
    xml_extension_tag_uid: Optional[str]

    @classmethod
    def from_repository_values(
        cls,
        name: str,
        data_type: str,
        xml_extension_uid: Optional[str],
        xml_extension_tag_uid: Optional[str],
    ) -> "OdmXmlExtensionAttributeVO":

        return cls(
            name=name,
            data_type=data_type,
            xml_extension_uid=xml_extension_uid,
            xml_extension_tag_uid=xml_extension_tag_uid,
            name_sentence_case=None,
            definition=None,
            abbreviation=None,
            is_template_parameter=False,
        )

    def validate(
        self,
        find_odm_xml_extension_callback: Callable[[str], Optional[OdmXmlExtensionAR]],
        find_odm_xml_extension_tag_callback: Callable[
            [str], Optional[OdmXmlExtensionTagAR]
        ],
        find_odm_xml_extension_attribute_callback: Callable[
            [dict], Optional[Tuple[Sequence["OdmXmlExtensionAttributeAR"], int]]
        ],
    ) -> None:

        if self.xml_extension_uid is not None:
            if not find_odm_xml_extension_callback(self.xml_extension_uid):
                raise BusinessLogicException(
                    f"ODM XML Extension Attribute tried to connect to non existing ODM XML Extension identified by uid ({self.xml_extension_uid})."
                )

        if self.xml_extension_tag_uid is not None:
            if not find_odm_xml_extension_tag_callback(self.xml_extension_tag_uid):
                raise BusinessLogicException(
                    "ODM XML Extension Attribute tried to connect to non existing"
                    f" ODM XML Extension Tag identified by uid ({self.xml_extension_tag_uid})."
                )

        odm_xml_extension_attributes, _ = find_odm_xml_extension_attribute_callback(
            filter_by={"name": {"v": [self.name], "op": "eq"}}
        )
        for odm_xml_extension_attribute in odm_xml_extension_attributes:
            if (
                self.xml_extension_uid is not None
                and odm_xml_extension_attribute.concept_vo.xml_extension_uid
                == self.xml_extension_uid
            ) or (
                self.xml_extension_tag_uid is not None
                and odm_xml_extension_attribute.concept_vo.xml_extension_tag_uid
                == self.xml_extension_tag_uid
            ):
                raise BusinessLogicException(
                    f"ODM XML Extension Attribute with name ({self.name}) already exists."
                )


@dataclass
class OdmXmlExtensionAttributeAR(OdmARBase):
    _concept_vo: OdmXmlExtensionAttributeVO

    @property
    def name(self) -> str:
        return self._concept_vo.name

    @property
    def concept_vo(self) -> OdmXmlExtensionAttributeVO:
        return self._concept_vo

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        concept_vo: OdmXmlExtensionAttributeVO,
        library: Optional[LibraryVO],
        item_metadata: LibraryItemMetadataVO,
    ) -> "OdmXmlExtensionAttributeAR":
        return cls(
            _uid=uid,
            _concept_vo=concept_vo,
            _library=library,
            _item_metadata=item_metadata,
        )

    @classmethod
    def from_input_values(
        cls,
        author: str,
        concept_vo: OdmXmlExtensionAttributeVO,
        library: LibraryVO,
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
        find_odm_xml_extension_callback: Callable[
            [str], Optional[OdmXmlExtensionAR]
        ] = lambda _: None,
        find_odm_xml_extension_tag_callback: Callable[
            [str], Optional[OdmXmlExtensionTagAR]
        ] = lambda _: None,
        find_odm_xml_extension_attribute_callback: Callable[
            [dict], Optional[Tuple[Sequence["OdmXmlExtensionAttributeAR"], int]]
        ] = lambda _: None,
    ) -> "OdmXmlExtensionAttributeAR":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        concept_vo.validate(
            find_odm_xml_extension_callback=find_odm_xml_extension_callback,
            find_odm_xml_extension_tag_callback=find_odm_xml_extension_tag_callback,
            find_odm_xml_extension_attribute_callback=find_odm_xml_extension_attribute_callback,
        )

        return cls(
            _uid=generate_uid_callback(),
            _item_metadata=item_metadata,
            _library=library,
            _concept_vo=concept_vo,
        )

    def edit_draft(
        self,
        author: str,
        change_description: Optional[str],
        concept_vo: OdmXmlExtensionAttributeVO,
        concept_exists_by_name_callback: Callable[[str], bool] = lambda _: True,
    ) -> None:
        """
        Creates a new draft version for the object.
        """

        if self._concept_vo != concept_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self._concept_vo = concept_vo


@dataclass(frozen=True)
class OdmXmlExtensionAttributeRelationVO:
    uid: str
    name: str
    data_type: str
    value: str
    xml_extension_uid: str

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        name: str,
        data_type: str,
        value: str,
        xml_extension_uid: str,
    ) -> "OdmXmlExtensionAttributeRelationVO":
        return cls(
            uid=uid,
            name=name,
            data_type=data_type,
            value=value,
            xml_extension_uid=xml_extension_uid,
        )


@dataclass(frozen=True)
class OdmXmlExtensionAttributeTagRelationVO:
    uid: str
    name: str
    data_type: str
    value: str
    xml_extension_tag_uid: str

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        name: str,
        data_type: str,
        value: str,
        xml_extension_tag_uid: str,
    ) -> "OdmXmlExtensionAttributeTagRelationVO":
        return cls(
            uid=uid,
            name=name,
            data_type=data_type,
            value=value,
            xml_extension_tag_uid=xml_extension_tag_uid,
        )
