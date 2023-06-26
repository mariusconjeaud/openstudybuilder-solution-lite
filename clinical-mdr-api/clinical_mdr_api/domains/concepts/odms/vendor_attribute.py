from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from clinical_mdr_api.domains.concepts.concept_base import ConceptVO
from clinical_mdr_api.domains.concepts.odms.odm_ar_base import OdmARBase
from clinical_mdr_api.domains.concepts.odms.vendor_element import OdmVendorElementAR
from clinical_mdr_api.domains.concepts.odms.vendor_namespace import OdmVendorNamespaceAR
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)
from clinical_mdr_api.exceptions import BusinessLogicException


@dataclass(frozen=True)
class OdmVendorAttributeVO(ConceptVO):
    compatible_types: List[str]
    data_type: Optional[str]
    value_regex: Optional[str]
    vendor_namespace_uid: Optional[str]
    vendor_element_uid: Optional[str]

    @classmethod
    def from_repository_values(
        cls,
        name: str,
        compatible_types: List[str],
        data_type: Optional[str],
        value_regex: Optional[str],
        vendor_namespace_uid: Optional[str],
        vendor_element_uid: Optional[str],
    ) -> "OdmVendorAttributeVO":
        return cls(
            name=name,
            compatible_types=compatible_types,
            data_type=data_type,
            value_regex=value_regex,
            vendor_namespace_uid=vendor_namespace_uid,
            vendor_element_uid=vendor_element_uid,
            name_sentence_case=None,
            definition=None,
            abbreviation=None,
            is_template_parameter=False,
        )

    def validate(
        self,
        find_odm_vendor_namespace_callback: Callable[
            [str], Optional[OdmVendorNamespaceAR]
        ],
        find_odm_vendor_element_callback: Callable[[str], Optional[OdmVendorElementAR]],
        find_odm_vendor_attribute_callback: Callable[
            [dict], Optional[Tuple[List["OdmVendorAttributeAR"], int]]
        ],
    ) -> None:
        if self.vendor_namespace_uid is not None:
            if not self.compatible_types:
                raise BusinessLogicException(
                    "compatible_types must be provided for ODM Vendor Attributes belonging to ODM Vendor Namespace."
                )

            if not find_odm_vendor_namespace_callback(self.vendor_namespace_uid):
                raise BusinessLogicException(
                    f"ODM Vendor Attribute tried to connect to non existing ODM Vendor Namespace identified by uid ({self.vendor_namespace_uid})."
                )

        if self.vendor_element_uid is not None:
            if self.compatible_types:
                raise BusinessLogicException(
                    "compatible_types must not be provided for ODM Vendor Attributes belonging to ODM Vendor Element."
                )

            if not find_odm_vendor_element_callback(self.vendor_element_uid):
                raise BusinessLogicException(
                    f"ODM Vendor Attribute tried to connect to non existing ODM Vendor Element identified by uid ({self.vendor_element_uid})."
                )

        odm_vendor_attributes, _ = find_odm_vendor_attribute_callback(
            filter_by={"name": {"v": [self.name], "op": "eq"}}
        )
        for odm_vendor_attribute in odm_vendor_attributes:
            if (
                self.vendor_namespace_uid is not None
                and odm_vendor_attribute.concept_vo.vendor_namespace_uid
                == self.vendor_namespace_uid
            ) or (
                self.vendor_element_uid is not None
                and odm_vendor_attribute.concept_vo.vendor_element_uid
                == self.vendor_element_uid
            ):
                raise BusinessLogicException(
                    f"ODM Vendor Attribute with name ({self.name}) already exists."
                )


@dataclass
class OdmVendorAttributeAR(OdmARBase):
    _concept_vo: OdmVendorAttributeVO

    @property
    def name(self) -> str:
        return self._concept_vo.name

    @property
    def concept_vo(self) -> OdmVendorAttributeVO:
        return self._concept_vo

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        concept_vo: OdmVendorAttributeVO,
        library: Optional[LibraryVO],
        item_metadata: LibraryItemMetadataVO,
    ) -> "OdmVendorAttributeAR":
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
        concept_vo: OdmVendorAttributeVO,
        library: LibraryVO,
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
        find_odm_vendor_namespace_callback: Callable[
            [str], Optional[OdmVendorNamespaceAR]
        ] = lambda _: None,
        find_odm_vendor_element_callback: Callable[
            [str], Optional[OdmVendorElementAR]
        ] = lambda _: None,
        find_odm_vendor_attribute_callback: Callable[
            [dict], Optional[Tuple[List["OdmVendorAttributeAR"], int]]
        ] = lambda _: None,
    ) -> "OdmVendorAttributeAR":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        concept_vo.validate(
            find_odm_vendor_namespace_callback=find_odm_vendor_namespace_callback,
            find_odm_vendor_element_callback=find_odm_vendor_element_callback,
            find_odm_vendor_attribute_callback=find_odm_vendor_attribute_callback,
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
        concept_vo: OdmVendorAttributeVO,
        concept_exists_by_name_callback: Callable[[str], bool] = lambda _: True,
    ) -> None:
        """
        Creates a new draft version for the object.
        """

        if self._concept_vo != concept_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self._concept_vo = concept_vo


@dataclass(frozen=True)
class OdmVendorAttributeRelationVO:
    uid: str
    name: str
    compatible_types: List[str]
    data_type: Optional[str]
    value_regex: Optional[str]
    value: str
    vendor_namespace_uid: str

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        name: str,
        compatible_types: List[str],
        data_type: Optional[str],
        value_regex: Optional[str],
        value: str,
        vendor_namespace_uid: str,
    ) -> "OdmVendorAttributeRelationVO":
        return cls(
            uid=uid,
            name=name,
            compatible_types=compatible_types,
            data_type=data_type,
            value_regex=value_regex,
            value=value,
            vendor_namespace_uid=vendor_namespace_uid,
        )


@dataclass(frozen=True)
class OdmVendorElementAttributeRelationVO:
    uid: str
    name: str
    data_type: Optional[str]
    value_regex: Optional[str]
    value: str
    vendor_element_uid: str

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        name: str,
        data_type: Optional[str],
        value_regex: Optional[str],
        value: str,
        vendor_element_uid: str,
    ) -> "OdmVendorElementAttributeRelationVO":
        return cls(
            uid=uid,
            name=name,
            data_type=data_type,
            value_regex=value_regex,
            value=value,
            vendor_element_uid=vendor_element_uid,
        )
