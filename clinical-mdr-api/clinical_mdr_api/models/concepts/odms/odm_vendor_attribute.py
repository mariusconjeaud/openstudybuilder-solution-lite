import re
from typing import Callable, Dict, List, Optional

from pydantic import BaseModel, Field, root_validator, validator

from clinical_mdr_api.domains.concepts.odms.vendor_attribute import (
    OdmVendorAttributeAR,
    OdmVendorAttributeRelationVO,
    OdmVendorElementAttributeRelationVO,
)
from clinical_mdr_api.domains.concepts.odms.vendor_element import OdmVendorElementAR
from clinical_mdr_api.domains.concepts.odms.vendor_namespace import OdmVendorNamespaceAR
from clinical_mdr_api.domains.concepts.utils import RelationType, VendorCompatibleType
from clinical_mdr_api.models.concepts.concept import (
    ConceptModel,
    ConceptPatchInput,
    ConceptPostInput,
)
from clinical_mdr_api.models.concepts.odms.odm_common_models import (
    OdmVendorElementSimpleModel,
    OdmVendorNamespaceSimpleModel,
)


class OdmVendorAttribute(ConceptModel):
    compatible_types: List[str]
    data_type: Optional[str] = Field(None, nullable=True)
    value_regex: Optional[str] = Field(None, nullable=True)
    vendor_namespace: Optional[OdmVendorNamespaceSimpleModel] = Field(
        None, nullable=True
    )
    vendor_element: Optional[OdmVendorElementSimpleModel] = Field(None, nullable=True)
    possible_actions: List[str]

    @classmethod
    def from_odm_vendor_attribute_ar(
        cls,
        odm_vendor_attribute_ar: OdmVendorAttributeAR,
        find_odm_vendor_namespace_by_uid: Callable[
            [str], Optional[OdmVendorNamespaceAR]
        ],
        find_odm_vendor_element_by_uid: Callable[[str], Optional[OdmVendorElementAR]],
    ) -> "OdmVendorAttribute":
        return cls(
            uid=odm_vendor_attribute_ar._uid,
            name=odm_vendor_attribute_ar.concept_vo.name,
            compatible_types=odm_vendor_attribute_ar.concept_vo.compatible_types,
            data_type=odm_vendor_attribute_ar.concept_vo.data_type,
            value_regex=odm_vendor_attribute_ar.concept_vo.value_regex,
            library_name=odm_vendor_attribute_ar.library.name,
            start_date=odm_vendor_attribute_ar.item_metadata.start_date,
            end_date=odm_vendor_attribute_ar.item_metadata.end_date,
            status=odm_vendor_attribute_ar.item_metadata.status.value,
            version=odm_vendor_attribute_ar.item_metadata.version,
            change_description=odm_vendor_attribute_ar.item_metadata.change_description,
            user_initials=odm_vendor_attribute_ar.item_metadata.user_initials,
            vendor_namespace=OdmVendorNamespaceSimpleModel.from_odm_vendor_namespace_uid(
                uid=odm_vendor_attribute_ar.concept_vo.vendor_namespace_uid,
                find_odm_vendor_namespace_by_uid=find_odm_vendor_namespace_by_uid,
            ),
            vendor_element=OdmVendorElementSimpleModel.from_odm_vendor_element_uid(
                uid=odm_vendor_attribute_ar.concept_vo.vendor_element_uid,
                find_odm_vendor_element_by_uid=find_odm_vendor_element_by_uid,
            ),
            possible_actions=sorted(
                [_.value for _ in odm_vendor_attribute_ar.get_possible_actions()]
            ),
        )


class OdmVendorAttributeRelationModel(BaseModel):
    @classmethod
    def from_uid(
        cls,
        uid: str,
        odm_element_uid: str,
        odm_element_type: RelationType,
        find_by_uid_with_odm_element_relation: Callable[
            [str, str, RelationType, bool], Optional[OdmVendorAttributeRelationVO]
        ],
        vendor_element_attribute: bool = True,
    ) -> Optional["OdmVendorAttributeRelationModel"]:
        if uid is not None:
            odm_vendor_attribute_ref_vo = find_by_uid_with_odm_element_relation(
                uid, odm_element_uid, odm_element_type, vendor_element_attribute
            )
            if odm_vendor_attribute_ref_vo is not None:
                odm_vendor_element_ref_model = cls(
                    uid=uid,
                    name=odm_vendor_attribute_ref_vo.name,
                    data_type=odm_vendor_attribute_ref_vo.data_type,
                    value_regex=odm_vendor_attribute_ref_vo.value_regex,
                    value=odm_vendor_attribute_ref_vo.value,
                    vendor_namespace_uid=odm_vendor_attribute_ref_vo.vendor_namespace_uid,
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


class OdmVendorElementAttributeRelationModel(BaseModel):
    @classmethod
    def from_uid(
        cls,
        uid: str,
        odm_element_uid: str,
        odm_element_type: RelationType,
        find_by_uid_with_odm_element_relation: Callable[
            [str, str, RelationType, bool],
            Optional[OdmVendorElementAttributeRelationVO],
        ],
        vendor_element_attribute: bool = True,
    ) -> Optional["OdmVendorElementAttributeRelationModel"]:
        if uid is not None:
            odm_vendor_element_attribute_ref_vo = find_by_uid_with_odm_element_relation(
                uid, odm_element_uid, odm_element_type, vendor_element_attribute
            )
            if odm_vendor_element_attribute_ref_vo is not None:
                odm_vendor_element_ref_model = cls(
                    uid=uid,
                    name=odm_vendor_element_attribute_ref_vo.name,
                    data_type=odm_vendor_element_attribute_ref_vo.data_type,
                    value_regex=odm_vendor_element_attribute_ref_vo.value_regex,
                    value=odm_vendor_element_attribute_ref_vo.value,
                    vendor_element_uid=odm_vendor_element_attribute_ref_vo.vendor_element_uid,
                )
            else:
                odm_vendor_element_ref_model = cls(
                    uid=uid,
                    name=None,
                    data_type=None,
                    value_regex=None,
                    value=None,
                    vendor_element_uid=None,
                )
        else:
            odm_vendor_element_ref_model = None
        return odm_vendor_element_ref_model

    uid: str = Field(..., title="uid", description="")
    name: Optional[str] = Field(None, title="name", description="")
    data_type: Optional[str] = Field(None, title="data_type", description="")
    value_regex: Optional[str] = Field(None, title="value_regex", description="")
    value: Optional[str] = Field(None, title="value", description="")
    vendor_element_uid: Optional[str] = Field(
        None, title="vendor_element_uid", description=""
    )


class OdmVendorAttributePostInput(ConceptPostInput):
    compatible_types: List[VendorCompatibleType] = []
    data_type: str = "string"
    value_regex: Optional[str] = None
    vendor_namespace_uid: Optional[str] = None
    vendor_element_uid: Optional[str] = None

    @validator("value_regex")
    @classmethod
    def value_regex_must_be_valid_regex(cls, v):
        return get_regex_if_valid(v)

    @validator("name")
    @classmethod
    def name_may_only_contain_letters(cls, v):
        if re.search("[^a-zA-Z]", v):
            raise ValueError("may only contain letters")
        return v

    @root_validator()
    @classmethod
    def one_and_only_one_of_the_two_uids_must_be_present(cls, values):
        if (
            not values["vendor_element_uid"] and not values["vendor_namespace_uid"]
        ) or (values["vendor_element_uid"] and values["vendor_namespace_uid"]):
            raise ValueError(
                "Either vendor_namespace_uid or vendor_element_uid must be provided"
            )

        return values


class OdmVendorAttributePatchInput(ConceptPatchInput):
    compatible_types: List[VendorCompatibleType]
    data_type: Optional[str]
    value_regex: Optional[str]

    @validator("value_regex")
    @classmethod
    def value_regex_must_be_valid_regex(cls, v):
        return get_regex_if_valid(v)


class OdmVendorAttributeVersion(OdmVendorAttribute):
    """
    Class for storing OdmVendorAttribute and calculation of differences
    """

    changes: Optional[Dict[str, bool]] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective (e.g. name, start_date, ..)."
        ),
        nullable=True,
    )


def get_regex_if_valid(regex: Optional[str]):
    if regex:
        try:
            re.compile(regex)
            return regex
        except re.error as exc:
            raise ValueError("Provided regex is invalid.") from exc
    return regex
