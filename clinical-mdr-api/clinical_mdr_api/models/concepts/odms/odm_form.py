from typing import Callable, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from clinical_mdr_api.domains.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domains.concepts.odms.alias import OdmAliasAR
from clinical_mdr_api.domains.concepts.odms.description import OdmDescriptionAR
from clinical_mdr_api.domains.concepts.odms.form import OdmFormAR, OdmFormRefVO
from clinical_mdr_api.domains.concepts.odms.item_group import OdmItemGroupRefVO
from clinical_mdr_api.domains.concepts.odms.vendor_attribute import (
    OdmVendorAttributeAR,
    OdmVendorAttributeRelationVO,
    OdmVendorElementAttributeRelationVO,
)
from clinical_mdr_api.domains.concepts.odms.vendor_element import (
    OdmVendorElementRelationVO,
)
from clinical_mdr_api.domains.concepts.utils import RelationType
from clinical_mdr_api.domains.controlled_terminologies.ct_term_attributes import (
    CTTermAttributesAR,
)
from clinical_mdr_api.models.concepts.activities.activity import (
    ActivityHierarchySimpleModel,
)
from clinical_mdr_api.models.concepts.concept import (
    ConceptModel,
    ConceptPatchInput,
    ConceptPostInput,
)
from clinical_mdr_api.models.concepts.odms.odm_alias import OdmAliasSimpleModel
from clinical_mdr_api.models.concepts.odms.odm_common_models import (
    OdmRefVendorPostInput,
)
from clinical_mdr_api.models.concepts.odms.odm_description import (
    OdmDescriptionBatchPatchInput,
    OdmDescriptionPostInput,
    OdmDescriptionSimpleModel,
)
from clinical_mdr_api.models.concepts.odms.odm_item_group import OdmItemGroupRefModel
from clinical_mdr_api.models.concepts.odms.odm_vendor_attribute import (
    OdmVendorAttributeRelationModel,
    OdmVendorElementAttributeRelationModel,
)
from clinical_mdr_api.models.concepts.odms.odm_vendor_element import (
    OdmVendorElementRelationModel,
)
from clinical_mdr_api.models.controlled_terminologies.ct_term import (
    SimpleCTTermAttributes,
)
from clinical_mdr_api.models.utils import booltostr


class OdmForm(ConceptModel):
    oid: Optional[str] = Field(None, nullable=True)
    repeating: Optional[str] = Field(None, nullable=True)
    sdtm_version: Optional[str] = Field(None, nullable=True)
    scope: Optional[SimpleCTTermAttributes] = Field(None, nullable=True)
    descriptions: List[OdmDescriptionSimpleModel] = Field(None, nullable=True)
    aliases: List[OdmAliasSimpleModel]
    activity_groups: List[ActivityHierarchySimpleModel]
    item_groups: List[OdmItemGroupRefModel]
    vendor_elements: List[OdmVendorElementRelationModel]
    vendor_attributes: List[OdmVendorAttributeRelationModel]
    vendor_element_attributes: List[OdmVendorElementAttributeRelationModel]
    possible_actions: List[str]

    @classmethod
    def from_odm_form_ar(
        cls,
        odm_form_ar: OdmFormAR,
        find_term_callback: Callable[[str], Optional[CTTermAttributesAR]],
        find_odm_description_by_uid: Callable[[str], Optional[OdmDescriptionAR]],
        find_odm_alias_by_uid: Callable[[str], Optional[OdmAliasAR]],
        find_activity_group_by_uid: Callable[[str], Optional[ActivityGroupAR]],
        find_odm_item_group_by_uid_with_form_relation: Callable[
            [str, str], Optional[OdmItemGroupRefVO]
        ],
        find_odm_vendor_attribute_by_uid: Callable[
            [str], Optional[OdmVendorAttributeAR]
        ],
        find_odm_vendor_element_by_uid_with_odm_element_relation: Callable[
            [str, str, RelationType], Optional[OdmVendorElementRelationVO]
        ],
        find_odm_vendor_attribute_by_uid_with_odm_element_relation: Callable[
            [str, str, RelationType, bool],
            Union[
                OdmVendorAttributeRelationVO,
                OdmVendorElementAttributeRelationVO,
                None,
            ],
        ],
    ) -> "OdmForm":
        return cls(
            uid=odm_form_ar._uid,
            oid=odm_form_ar.concept_vo.oid,
            name=odm_form_ar.concept_vo.name,
            sdtm_version=odm_form_ar.concept_vo.sdtm_version,
            repeating=booltostr(odm_form_ar.concept_vo.repeating),
            library_name=odm_form_ar.library.name,
            start_date=odm_form_ar.item_metadata.start_date,
            end_date=odm_form_ar.item_metadata.end_date,
            status=odm_form_ar.item_metadata.status.value,
            version=odm_form_ar.item_metadata.version,
            change_description=odm_form_ar.item_metadata.change_description,
            user_initials=odm_form_ar.item_metadata.user_initials,
            scope=SimpleCTTermAttributes.from_term_uid(
                uid=odm_form_ar.concept_vo.scope_uid,
                find_term_by_uid=find_term_callback,
            ),
            descriptions=sorted(
                [
                    OdmDescriptionSimpleModel.from_odm_description_uid(
                        uid=description_uid,
                        find_odm_description_by_uid=find_odm_description_by_uid,
                    )
                    for description_uid in odm_form_ar.concept_vo.description_uids
                ],
                key=lambda item: item.name,
            ),
            aliases=sorted(
                [
                    OdmAliasSimpleModel.from_odm_alias_uid(
                        uid=alias_uid,
                        find_odm_alias_by_uid=find_odm_alias_by_uid,
                    )
                    for alias_uid in odm_form_ar.concept_vo.alias_uids
                ],
                key=lambda item: item.name,
            ),
            activity_groups=sorted(
                [
                    ActivityHierarchySimpleModel.from_activity_uid(
                        uid=activity_group_uid,
                        find_activity_by_uid=find_activity_group_by_uid,
                    )
                    for activity_group_uid in odm_form_ar.concept_vo.activity_group_uids
                ],
                key=lambda item: item.name,
            ),
            item_groups=sorted(
                [
                    OdmItemGroupRefModel.from_odm_item_group_uid(
                        uid=item_group_uid,
                        form_uid=odm_form_ar._uid,
                        find_odm_item_group_by_uid_with_form_relation=find_odm_item_group_by_uid_with_form_relation,
                        find_odm_vendor_attribute_by_uid=find_odm_vendor_attribute_by_uid,
                    )
                    for item_group_uid in odm_form_ar.concept_vo.item_group_uids
                ],
                key=lambda item: item.order_number,
            ),
            vendor_elements=sorted(
                [
                    OdmVendorElementRelationModel.from_uid(
                        uid=vendor_element_uid,
                        odm_element_uid=odm_form_ar._uid,
                        odm_element_type=RelationType.FORM,
                        find_by_uid_with_odm_element_relation=find_odm_vendor_element_by_uid_with_odm_element_relation,
                    )
                    for vendor_element_uid in odm_form_ar.concept_vo.vendor_element_uids
                ],
                key=lambda item: item.name,
            ),
            vendor_attributes=sorted(
                [
                    OdmVendorAttributeRelationModel.from_uid(
                        uid=vendor_attribute_uid,
                        odm_element_uid=odm_form_ar._uid,
                        odm_element_type=RelationType.FORM,
                        find_by_uid_with_odm_element_relation=find_odm_vendor_attribute_by_uid_with_odm_element_relation,
                        vendor_element_attribute=False,
                    )
                    for vendor_attribute_uid in odm_form_ar.concept_vo.vendor_attribute_uids
                ],
                key=lambda item: item.name,
            ),
            vendor_element_attributes=sorted(
                [
                    OdmVendorElementAttributeRelationModel.from_uid(
                        uid=vendor_element_attribute_uid,
                        odm_element_uid=odm_form_ar._uid,
                        odm_element_type=RelationType.FORM,
                        find_by_uid_with_odm_element_relation=find_odm_vendor_attribute_by_uid_with_odm_element_relation,
                    )
                    for vendor_element_attribute_uid in odm_form_ar.concept_vo.vendor_element_attribute_uids
                ],
                key=lambda item: item.name,
            ),
            possible_actions=sorted(
                [_.value for _ in odm_form_ar.get_possible_actions()]
            ),
        )


class OdmFormRefModel(BaseModel):
    @classmethod
    def from_odm_form_uid(
        cls,
        uid: str,
        study_event_uid: str,
        find_odm_form_by_uid_with_study_event_relation: Callable[
            [str, str], Optional[OdmFormRefVO]
        ],
    ) -> Optional["OdmFormRefModel"]:
        if uid is not None:
            odm_form_ref_vo = find_odm_form_by_uid_with_study_event_relation(
                uid, study_event_uid
            )
            if odm_form_ref_vo is not None:
                odm_form_ref_model = cls(
                    uid=uid,
                    name=odm_form_ref_vo.name,
                    order_number=odm_form_ref_vo.order_number,
                    mandatory=odm_form_ref_vo.mandatory,
                    locked=odm_form_ref_vo.locked,
                    collection_exception_condition_oid=odm_form_ref_vo.collection_exception_condition_oid,
                )
            else:
                odm_form_ref_model = cls(
                    uid=uid,
                    name=None,
                    order_number=None,
                    mandatory=None,
                    locked=None,
                    collection_exception_condition_oid=None,
                )
        else:
            odm_form_ref_model = None
        return odm_form_ref_model

    uid: str = Field(..., title="uid", description="")
    name: Optional[str] = Field(None, title="name", description="")
    order_number: Optional[int] = Field(None, title="order_number", description="")
    mandatory: Optional[str] = Field(None, title="mandatory", description="")
    locked: Optional[str] = Field(None, title="locked", description="")
    collection_exception_condition_oid: Optional[str] = Field(
        None, title="collection_exception_condition_oid", description=""
    )


class OdmFormPostInput(ConceptPostInput):
    oid: Optional[str]
    sdtm_version: Optional[str]
    repeating: str
    scope_uid: Optional[str] = None
    descriptions: List[Union[OdmDescriptionPostInput, str]]
    alias_uids: List[str]


class OdmFormPatchInput(ConceptPatchInput):
    oid: Optional[str]
    sdtm_version: Optional[str]
    repeating: Optional[str]
    scope_uid: Optional[str]
    descriptions: List[
        Union[OdmDescriptionBatchPatchInput, OdmDescriptionPostInput, str]
    ]
    alias_uids: List[str]


class OdmFormItemGroupPostInput(BaseModel):
    uid: str
    order_number: int
    mandatory: str
    collection_exception_condition_oid: Optional[str]
    vendor: OdmRefVendorPostInput


class OdmFormActivityGroupPostInput(BaseModel):
    uid: str


class OdmFormVersion(OdmForm):
    """
    Class for storing OdmForm and calculation of differences
    """

    changes: Optional[Dict[str, bool]] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective (e.g. name, start_date, ..)."
        ),
        nullable=True,
    )
