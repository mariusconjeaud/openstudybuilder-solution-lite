from typing import Callable, List, Optional

from pydantic import BaseModel, Field

from clinical_mdr_api.domain.concepts.concept_base import ConceptARBase
from clinical_mdr_api.domain.concepts.odms.vendor_attribute import OdmVendorAttributeAR


class OdmElementWithParentUid(BaseModel):
    uid: str
    name: str
    parent_uids: List[str]


class OdmVendorRelationPostInput(BaseModel):
    uid: str
    value: str


class OdmVendorsPostInput(BaseModel):
    elements: List[OdmVendorRelationPostInput]
    element_attributes: List[OdmVendorRelationPostInput]
    attributes: List[OdmVendorRelationPostInput]


class OdmRefVendorPostInput(BaseModel):
    attributes: List[OdmVendorRelationPostInput]


class OdmRefVendorAttributeModel(BaseModel):
    @classmethod
    def from_uid(
        cls,
        uid: str,
        value: str,
        find_odm_vendor_attribute_by_uid: Callable[
            [str], Optional[OdmVendorAttributeAR]
        ],
    ) -> Optional["OdmRefVendorAttributeModel"]:
        if uid is not None:
            odm_vendor_attribute_ar = find_odm_vendor_attribute_by_uid(uid)
            if odm_vendor_attribute_ar is not None:
                odm_vendor_element_ref_model = cls(
                    uid=uid,
                    name=odm_vendor_attribute_ar.name,
                    data_type=odm_vendor_attribute_ar.concept_vo.data_type,
                    value_regex=odm_vendor_attribute_ar.concept_vo.value_regex,
                    value=value,
                    vendor_namespace_uid=odm_vendor_attribute_ar.concept_vo.vendor_namespace_uid,
                )
            else:
                odm_vendor_element_ref_model = cls(
                    uid=uid,
                    name=None,
                    data_type=None,
                    value_regex=None,
                    value=None,
                    vendor_namespace_uid=None,
                )
        else:
            odm_vendor_element_ref_model = None
        return odm_vendor_element_ref_model

    uid: str = Field(..., title="uid", description="")
    name: Optional[str] = Field(None, title="name", description="")
    data_type: Optional[str] = Field(None, title="data_type", description="")
    value_regex: Optional[str] = Field(None, title="value_regex", description="")
    value: Optional[str] = Field(None, title="value", description="")
    vendor_namespace_uid: Optional[str] = Field(
        None, title="vendor_namespace_uid", description=""
    )


class OdmRefVendor(BaseModel):
    attributes: List[OdmRefVendorAttributeModel]


class OdmVendorNamespaceSimpleModel(BaseModel):
    @classmethod
    def from_odm_vendor_namespace_uid(
        cls,
        uid: str,
        find_odm_vendor_namespace_by_uid: Callable[[str], Optional[ConceptARBase]],
    ) -> Optional["OdmVendorNamespaceSimpleModel"]:
        if uid is not None:
            odm_vendor_namespace = find_odm_vendor_namespace_by_uid(uid)

            if odm_vendor_namespace is not None:
                simple_odm_vendor_namespace_model = cls(
                    uid=uid,
                    name=odm_vendor_namespace.concept_vo.name,
                    prefix=odm_vendor_namespace.concept_vo.prefix,
                    url=odm_vendor_namespace.concept_vo.url,
                    status=odm_vendor_namespace.item_metadata.status.value,
                    version=odm_vendor_namespace.item_metadata.version,
                    possible_actions=sorted(
                        [_.value for _ in odm_vendor_namespace.get_possible_actions()]
                    ),
                )
            else:
                simple_odm_vendor_namespace_model = cls(
                    uid=uid,
                    name=None,
                    prefix=None,
                    url=None,
                    status=None,
                    version=None,
                    possible_actions=[],
                )
        else:
            simple_odm_vendor_namespace_model = None
        return simple_odm_vendor_namespace_model

    uid: str = Field(..., title="uid", description="")
    name: Optional[str] = Field(None, title="name", description="")
    prefix: Optional[str] = Field(None, title="prefix", description="")
    url: Optional[str] = Field(None, title="url", description="")
    status: Optional[str] = Field(None, title="status", description="")
    version: Optional[str] = Field(None, title="version", description="")
    possible_actions: List[str] = Field(None, title="possible_actions", description="")


class OdmVendorAttributeSimpleModel(BaseModel):
    @classmethod
    def from_odm_vendor_attribute_uid(
        cls,
        uid: str,
        find_odm_vendor_attribute_by_uid: Callable[[str], Optional[ConceptARBase]],
    ) -> Optional["OdmVendorAttributeSimpleModel"]:
        if uid is not None:
            odm_vendor_attribute = find_odm_vendor_attribute_by_uid(uid)

            if odm_vendor_attribute is not None:
                simple_odm_vendor_attribute_model = cls(
                    uid=uid,
                    name=odm_vendor_attribute.concept_vo.name,
                    status=odm_vendor_attribute.item_metadata.status.value,
                    version=odm_vendor_attribute.item_metadata.version,
                    possible_actions=sorted(
                        [_.value for _ in odm_vendor_attribute.get_possible_actions()]
                    ),
                )
            else:
                simple_odm_vendor_attribute_model = cls(
                    uid=uid, name=None, status=None, version=None, possible_actions=[]
                )
        else:
            simple_odm_vendor_attribute_model = None
        return simple_odm_vendor_attribute_model

    uid: str = Field(..., title="uid", description="")
    name: Optional[str] = Field(None, title="name", description="")
    status: Optional[str] = Field(None, title="status", description="")
    version: Optional[str] = Field(None, title="version", description="")
    possible_actions: List[str] = Field(None, title="possible_actions", description="")


class OdmVendorElementSimpleModel(BaseModel):
    @classmethod
    def from_odm_vendor_element_uid(
        cls,
        uid: str,
        find_odm_vendor_element_by_uid: Callable[[str], Optional[ConceptARBase]],
    ) -> Optional["OdmVendorElementSimpleModel"]:
        if uid is not None:
            odm_vendor_element = find_odm_vendor_element_by_uid(uid)

            if odm_vendor_element is not None:
                simple_odm_vendor_element_model = cls(
                    uid=uid,
                    name=odm_vendor_element.concept_vo.name,
                    status=odm_vendor_element.item_metadata.status.value,
                    version=odm_vendor_element.item_metadata.version,
                    possible_actions=sorted(
                        [_.value for _ in odm_vendor_element.get_possible_actions()]
                    ),
                )
            else:
                simple_odm_vendor_element_model = cls(
                    uid=uid, name=None, status=None, version=None, possible_actions=[]
                )
        else:
            simple_odm_vendor_element_model = None
        return simple_odm_vendor_element_model

    uid: str = Field(..., title="uid", description="")
    name: Optional[str] = Field(None, title="name", description="")
    status: Optional[str] = Field(None, title="status", description="")
    version: Optional[str] = Field(None, title="version", description="")
    possible_actions: List[str] = Field(None, title="possible_actions", description="")
