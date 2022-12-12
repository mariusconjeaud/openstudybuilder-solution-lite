from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field

from clinical_mdr_api.domain.controlled_terminology.ct_codelist_name import (
    CTCodelistNameAR,
)
from clinical_mdr_api.models.library import Library
from clinical_mdr_api.models.utils import BaseModel


class CTCodelistName(BaseModel):
    @classmethod
    def from_ct_codelist_ar(cls, ct_codelist_ar: CTCodelistNameAR) -> "CTCodelistName":
        return cls(
            catalogue_name=ct_codelist_ar.ct_codelist_vo.catalogue_name,
            codelist_uid=ct_codelist_ar.uid,
            name=ct_codelist_ar.name,
            template_parameter=ct_codelist_ar.ct_codelist_vo.is_template_parameter,
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
        cls, ct_codelist_ar: CTCodelistNameAR
    ) -> "CTCodelistName":
        return cls(
            name=ct_codelist_ar.name,
            template_parameter=ct_codelist_ar.ct_codelist_vo.is_template_parameter,
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

    name: str = Field(
        ...,
        title="name",
        description="",
    )

    template_parameter: bool = Field(
        ...,
        title="template_parameter",
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
            "Holds those actions that can be performed on the CTCodelistName. "
            "Actions are: 'approve', 'edit', 'new_version'."
        ),
    )


class CTCodelistNameVersion(CTCodelistName):
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


class CTCodelistNameInput(BaseModel):
    name: Optional[str] = Field(
        None,
        title="name",
        description="",
    )

    template_parameter: Optional[bool] = Field(
        None, title="template_parameter", description=""
    )


class CTCodelistNameEditInput(CTCodelistNameInput):
    change_description: str = Field(None, title="change_description", description="")


class CTCodelistNameCreateInput(CTCodelistNameInput):
    codelist_uid: str = Field(None, title="change_description", description="")
