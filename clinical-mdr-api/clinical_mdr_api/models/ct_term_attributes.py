from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field

from clinical_mdr_api.domain.controlled_terminology.ct_term_attributes import (
    CTTermAttributesAR,
)
from clinical_mdr_api.models.library import Library
from clinical_mdr_api.models.utils import BaseModel


class CTTermAttributes(BaseModel):
    @classmethod
    def from_ct_term_ar(
        cls, ct_term_attributes_ar: CTTermAttributesAR
    ) -> "CTTermAttributes":
        return cls(
            term_uid=ct_term_attributes_ar.uid,
            catalogue_name=ct_term_attributes_ar.ct_term_vo.catalogue_name,
            codelist_uid=ct_term_attributes_ar.ct_term_vo.codelist_uid,
            concept_id=ct_term_attributes_ar.ct_term_vo.concept_id,
            code_submission_value=ct_term_attributes_ar.ct_term_vo.code_submission_value,
            name_submission_value=ct_term_attributes_ar.ct_term_vo.name_submission_value,
            nci_preferred_name=ct_term_attributes_ar.ct_term_vo.preferred_term,
            definition=ct_term_attributes_ar.ct_term_vo.definition,
            library_name=Library.from_library_vo(ct_term_attributes_ar.library).name,
            possible_actions=sorted(
                [_.value for _ in ct_term_attributes_ar.get_possible_actions()]
            ),
            start_date=ct_term_attributes_ar.item_metadata.start_date,
            end_date=ct_term_attributes_ar.item_metadata.end_date,
            status=ct_term_attributes_ar.item_metadata.status.value,
            version=ct_term_attributes_ar.item_metadata.version,
            change_description=ct_term_attributes_ar.item_metadata.change_description,
            user_initials=ct_term_attributes_ar.item_metadata.user_initials,
        )

    @classmethod
    def from_ct_term_ar_without_common_term_fields(
        cls, ct_term_attributes_ar: CTTermAttributesAR
    ) -> "CTTermAttributes":
        return cls(
            concept_id=ct_term_attributes_ar.ct_term_vo.concept_id,
            code_submission_value=ct_term_attributes_ar.ct_term_vo.code_submission_value,
            name_submission_value=ct_term_attributes_ar.ct_term_vo.name_submission_value,
            nci_preferred_name=ct_term_attributes_ar.ct_term_vo.preferred_term,
            definition=ct_term_attributes_ar.ct_term_vo.definition,
            possible_actions=sorted(
                [_.value for _ in ct_term_attributes_ar.get_possible_actions()]
            ),
            start_date=ct_term_attributes_ar.item_metadata.start_date,
            end_date=ct_term_attributes_ar.item_metadata.end_date,
            status=ct_term_attributes_ar.item_metadata.status.value,
            version=ct_term_attributes_ar.item_metadata.version,
            change_description=ct_term_attributes_ar.item_metadata.change_description,
            user_initials=ct_term_attributes_ar.item_metadata.user_initials,
        )

    term_uid: Optional[str] = Field(
        None,
        title="term_uid",
        description="",
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

    concept_id: Optional[str] = Field(
        ...,
        title="concept_id",
        description="",
    )

    code_submission_value: Optional[str] = Field(
        ...,
        title="code_submission_value",
        description="",
    )

    name_submission_value: Optional[str] = Field(
        ...,
        title="name_submission_value",
        description="",
    )

    nci_preferred_name: str = Field(
        ...,
        title="nci_preferred_name",
        description="",
    )

    definition: str = Field(
        ..., title="definition", description="", remove_from_wildcard=True
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
            "Holds those actions that can be performed on the CTTermAttributes. "
            "Actions are: 'approve', 'edit', 'new_version'."
        ),
    )


class CTTermAttributesVersion(CTTermAttributes):
    """
    Class for storing CTTermAttributes and calculation of differences
    """

    changes: Dict[str, bool] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective (e.g. name, start_date, ..)."
        ),
    )


class CTTermAttributesInput(BaseModel):

    code_submission_value: Optional[str] = Field(
        None,
        title="code_submission_value",
        description="",
    )

    name_submission_value: Optional[str] = Field(
        None,
        title="name_submission_value",
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


class CTTermAttributesEditInput(CTTermAttributesInput):
    change_description: str = Field(None, title="change_description", description="")
