from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field

from clinical_mdr_api.domain.controlled_terminology.ct_term_name import CTTermNameAR
from clinical_mdr_api.models.library import Library
from clinical_mdr_api.models.utils import BaseModel


class CTTermName(BaseModel):
    @classmethod
    def from_ct_term_ar(cls, ct_term_name_ar: CTTermNameAR) -> "CTTermName":
        return cls(
            term_uid=ct_term_name_ar.uid,
            catalogue_name=ct_term_name_ar.ct_term_vo.catalogue_name,
            codelist_uid=ct_term_name_ar.ct_term_vo.codelist_uid,
            sponsor_preferred_name=ct_term_name_ar.ct_term_vo.name,
            sponsor_preferred_name_sentence_case=ct_term_name_ar.ct_term_vo.name_sentence_case,
            order=ct_term_name_ar.ct_term_vo.order,
            library_name=Library.from_library_vo(ct_term_name_ar.library).name,
            possible_actions=sorted(
                [_.value for _ in ct_term_name_ar.get_possible_actions()]
            ),
            start_date=ct_term_name_ar.item_metadata.start_date,
            end_date=ct_term_name_ar.item_metadata.end_date,
            status=ct_term_name_ar.item_metadata.status.value,
            version=ct_term_name_ar.item_metadata.version,
            change_description=ct_term_name_ar.item_metadata.change_description,
            user_initials=ct_term_name_ar.item_metadata.user_initials,
        )

    @classmethod
    def from_ct_term_ar_without_common_term_fields(
        cls, ct_term_name_ar: CTTermNameAR
    ) -> "CTTermName":
        return cls(
            sponsor_preferred_name=ct_term_name_ar.ct_term_vo.name,
            sponsor_preferred_name_sentence_case=ct_term_name_ar.ct_term_vo.name_sentence_case,
            order=ct_term_name_ar.ct_term_vo.order,
            possible_actions=sorted(
                [_.value for _ in ct_term_name_ar.get_possible_actions()]
            ),
            start_date=ct_term_name_ar.item_metadata.start_date,
            end_date=ct_term_name_ar.item_metadata.end_date,
            status=ct_term_name_ar.item_metadata.status.value,
            version=ct_term_name_ar.item_metadata.version,
            change_description=ct_term_name_ar.item_metadata.change_description,
            user_initials=ct_term_name_ar.item_metadata.user_initials,
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

    sponsor_preferred_name: str = Field(
        ...,
        title="sponsor_preferred_name",
        description="",
    )

    sponsor_preferred_name_sentence_case: str = Field(
        ...,
        title="sponsor_preferred_name_sentence_case",
        description="",
    )

    order: Optional[int] = Field(
        999999,
        title="order",
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
            "Holds those actions that can be performed on the CTTermName. "
            "Actions are: 'approve', 'edit', 'new_version'."
        ),
    )


class CTTermNameVersion(CTTermName):
    """
    Class for storing CTTermName and calculation of differences
    """

    changes: Dict[str, bool] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the objective (e.g. name, start_date, ..)."
        ),
    )


class CTTermNameInput(BaseModel):
    sponsor_preferred_name: Optional[str] = Field(
        None,
        title="sponsor_preferred_name",
        description="",
    )

    sponsor_preferred_name_sentence_case: Optional[str] = Field(
        None,
        title="sponsor_preferred_name_sentence_case",
        description="",
    )


class CTTermNameEditInput(CTTermNameInput):
    change_description: str = Field(None, title="change_description", description="")
