from datetime import datetime
from typing import Callable, Dict, List, Optional, Sequence

from pydantic import Field

from clinical_mdr_api.domain.controlled_terminology.ct_codelist_attributes import (
    CTCodelistAttributesAR,
)
from clinical_mdr_api.models.library import Library
from clinical_mdr_api.models.utils import BaseModel


class CTCodelistAttributes(BaseModel):
    @classmethod
    def from_ct_codelist_ar(
        cls, ct_codelist_ar: CTCodelistAttributesAR
    ) -> "CTCodelistAttributes":
        return cls(
            catalogue_name=ct_codelist_ar.ct_codelist_vo.catalogue_name,
            codelist_uid=ct_codelist_ar.uid,
            parent_codelist_uid=ct_codelist_ar.ct_codelist_vo.parent_codelist_uid,
            child_codelist_uids=ct_codelist_ar.ct_codelist_vo.child_codelist_uids,
            name=ct_codelist_ar.name,
            submission_value=ct_codelist_ar.ct_codelist_vo.submission_value,
            nci_preferred_name=ct_codelist_ar.ct_codelist_vo.preferred_term,
            definition=ct_codelist_ar.ct_codelist_vo.definition,
            extensible=ct_codelist_ar.ct_codelist_vo.extensible,
            library_name=Library.from_library_vo(ct_codelist_ar.library).name,
            start_date=ct_codelist_ar.item_metadata.start_date,
            end_date=ct_codelist_ar.item_metadata.end_date,
            status=ct_codelist_ar.item_metadata.status.value,
            version=ct_codelist_ar.item_metadata.version,
            change_description=ct_codelist_ar.item_metadata.change_description,
            user_initials=ct_codelist_ar.item_metadata.user_initials,
            possible_actions=sorted(
                [_.value for _ in ct_codelist_ar.get_possible_actions()]
            ),
        )

    @classmethod
    def from_ct_codelist_ar_without_common_codelist_fields(
        cls, ct_codelist_ar: CTCodelistAttributesAR
    ) -> "CTCodelistAttributes":
        return cls(
            name=ct_codelist_ar.name,
            submission_value=ct_codelist_ar.ct_codelist_vo.submission_value,
            nci_preferred_name=ct_codelist_ar.ct_codelist_vo.preferred_term,
            definition=ct_codelist_ar.ct_codelist_vo.definition,
            extensible=ct_codelist_ar.ct_codelist_vo.extensible,
            start_date=ct_codelist_ar.item_metadata.start_date,
            end_date=ct_codelist_ar.item_metadata.end_date,
            status=ct_codelist_ar.item_metadata.status.value,
            version=ct_codelist_ar.item_metadata.version,
            change_description=ct_codelist_ar.item_metadata.change_description,
            user_initials=ct_codelist_ar.item_metadata.user_initials,
            possible_actions=sorted(
                [_.value for _ in ct_codelist_ar.get_possible_actions()]
            ),
        )

    catalogue_name: Optional[str] = Field(
        None,
        title="catalogue_name",
        description="",
    )

    codelist_uid: Optional[str] = Field(
        None,
        title="codelist_uid",
        description="",
    )

    parent_codelist_uid: str = Field(
        None, title="parent_codelist_uid", description="", remove_from_wildcard=True
    )

    child_codelist_uids: Optional[Sequence[str]] = Field(
        None, title="child_codelist_uids", description="", remove_from_wildcard=True
    )

    name: str = Field(
        ...,
        title="name",
        description="",
    )

    submission_value: str = Field(
        ...,
        title="submission_value",
        description="",
    )

    nci_preferred_name: str = Field(
        ...,
        title="nci_preferred_name",
        description="",
    )

    definition: str = Field(
        ...,
        title="definition",
        description="",
    )

    extensible: bool = Field(
        ...,
        title="extensible",
        description="",
    )

    library_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    version: Optional[str] = None
    change_description: Optional[str] = None
    user_initials: Optional[str] = None
    possible_actions: Optional[List[str]] = Field(
        None,
        description=(
            "Holds those actions that can be performed on the CTCodelistAttributes. "
            "Actions are: 'approve', 'edit', 'new_version'."
        ),
    )


class CTCodelistAttributesSimpleModel(BaseModel):
    @classmethod
    def from_codelist_uid(
        cls,
        uid: str,
        find_codelist_attribute_by_codelist_uid: Callable[
            [str], Optional[CTCodelistAttributesAR]
        ],
    ) -> Optional["CTCodelistAttributesSimpleModel"]:
        if uid is not None:
            codelist_attribute = find_codelist_attribute_by_codelist_uid(uid)

            if codelist_attribute is not None:
                simple_codelist_attribute_model = cls(
                    uid=uid,
                    name=codelist_attribute._ct_codelist_attributes_vo.name,
                    submission_value=codelist_attribute._ct_codelist_attributes_vo.submission_value,
                    preferred_term=codelist_attribute._ct_codelist_attributes_vo.preferred_term,
                )
            else:
                simple_codelist_attribute_model = cls(
                    uid=uid,
                    name=None,
                    submission_value=None,
                    preferred_term=None,
                )
        else:
            simple_codelist_attribute_model = None
        return simple_codelist_attribute_model

    uid: str = Field(..., title="uid", description="")
    name: Optional[str] = Field(None, title="name", description="")
    submission_value: Optional[str] = Field(
        None, title="submission_value", description=""
    )
    preferred_term: Optional[str] = Field(None, title="preferred_term", description="")


class CTCodelistAttributesVersion(CTCodelistAttributes):
    """
    Class for storing CTCodelistAttributes and calculation of differences
    """

    changes: Dict[str, bool] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective (e.g. name, start_date, ..)."
        ),
    )


class CTCodelistAttributesInput(BaseModel):
    name: Optional[str] = Field(
        None,
        title="name",
        description="",
    )

    submission_value: Optional[str] = Field(
        None,
        title="submission_value",
        description="",
    )

    nci_preferred_name: Optional[str] = Field(
        None,
        title="nci_preferred_name",
        description="",
    )

    definition: Optional[str] = Field(
        None,
        title="definition",
        description="",
    )

    extensible: Optional[bool] = Field(
        None,
        title="extensible",
        description="",
    )


class CTCodelistAttributesEditInput(CTCodelistAttributesInput):
    change_description: str = Field(None, title="change_description", description="")
