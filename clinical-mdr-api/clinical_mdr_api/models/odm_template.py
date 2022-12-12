from datetime import date
from typing import Callable, Dict, List, Optional, Sequence

from pydantic import BaseModel, Field

from clinical_mdr_api.domain.concepts.odms.form import OdmFormRefVO
from clinical_mdr_api.domain.concepts.odms.template import OdmTemplateAR
from clinical_mdr_api.models.concept import (
    ConceptModel,
    ConceptPatchInput,
    ConceptPostInput,
)
from clinical_mdr_api.models.odm_form import OdmFormRefModel


class OdmTemplate(ConceptModel):
    oid: Optional[str]
    effective_date: Optional[date]
    retired_date: Optional[date]
    description: Optional[str]
    forms: Sequence[OdmFormRefModel]
    possible_actions: List[str]

    @classmethod
    def from_odm_template_ar(
        cls,
        odm_template_ar: OdmTemplateAR,
        find_odm_form_by_uid_with_template_relation: Callable[
            [str, str], Optional[OdmFormRefVO]
        ],
    ) -> "OdmTemplate":
        return cls(
            uid=odm_template_ar._uid,
            name=odm_template_ar.concept_vo.name,
            oid=odm_template_ar.concept_vo.oid,
            effective_date=odm_template_ar.concept_vo.effective_date,
            retired_date=odm_template_ar.concept_vo.retired_date,
            description=odm_template_ar.concept_vo.description,
            library_name=odm_template_ar.library.name,
            start_date=odm_template_ar.item_metadata.start_date,
            end_date=odm_template_ar.item_metadata.end_date,
            status=odm_template_ar.item_metadata.status.value,
            version=odm_template_ar.item_metadata.version,
            change_description=odm_template_ar.item_metadata.change_description,
            user_initials=odm_template_ar.item_metadata.user_initials,
            forms=sorted(
                [
                    OdmFormRefModel.from_odm_form_uid(
                        uid=form_uid,
                        template_uid=odm_template_ar._uid,
                        find_odm_form_by_uid_with_template_relation=find_odm_form_by_uid_with_template_relation,
                    )
                    for form_uid in odm_template_ar.concept_vo.form_uids
                ],
                key=lambda item: item.order_number,
            ),
            possible_actions=sorted(
                [_.value for _ in odm_template_ar.get_possible_actions()]
            ),
        )


class OdmTemplatePostInput(ConceptPostInput):
    oid: Optional[str]
    effective_date: Optional[date]
    retired_date: Optional[date]
    description: Optional[str]


class OdmTemplatePatchInput(ConceptPatchInput):
    oid: Optional[str]
    effective_date: Optional[date]
    retired_date: Optional[date]
    description: Optional[str]


class OdmTemplateFormPostInput(BaseModel):
    uid: str
    order_number: int
    mandatory: str
    locked: str = "No"
    collection_exception_condition_oid: Optional[str]


class OdmTemplateVersion(OdmTemplate):
    """
    Class for storing OdmTemplates and calculation of differences
    """

    changes: Dict[str, bool] = Field(
        None,
        description=(
            "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
            "The field names in this object here refer to the field names of the timeframe (e.g. name, start_date, ..)."
        ),
    )
