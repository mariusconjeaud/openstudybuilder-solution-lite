from typing import Optional

from pydantic import validator

from clinical_mdr_api.domain.configurations import CTConfigAR
from clinical_mdr_api.models.concept import NoLibraryConceptModelNoName
from clinical_mdr_api.models.utils import BaseModel


class CTConfigBaseModel(BaseModel):
    study_field_name: Optional[str]
    study_field_data_type: Optional[str]
    study_field_null_value_code: Optional[str]

    configured_codelist_uid: Optional[str]
    configured_term_uid: Optional[str]

    study_field_grouping: Optional[str]
    study_field_name_api: Optional[str]
    is_dictionary_term: Optional[bool]


class CTConfigModel(CTConfigBaseModel, NoLibraryConceptModelNoName):
    @classmethod
    def from_ct_config_ar(cls, ct_config_definition_ar: CTConfigAR) -> "CTConfigModel":
        return CTConfigModel(
            uid=ct_config_definition_ar.uid,
            study_field_name=ct_config_definition_ar.value.study_field_name,
            study_field_data_type=ct_config_definition_ar.value.study_field_data_type,
            study_field_null_value_code=ct_config_definition_ar.value.study_field_null_value_code,
            configured_codelist_uid=ct_config_definition_ar.value.configured_codelist_uid,
            configured_term_uid=ct_config_definition_ar.value.configured_term_uid,
            study_field_grouping=ct_config_definition_ar.value.study_field_grouping,
            study_field_name_api=ct_config_definition_ar.value.study_field_name_api,
            is_dictionary_term=ct_config_definition_ar.value.is_dictionary_term,
            start_date=ct_config_definition_ar.item_metadata.start_date,
            status=ct_config_definition_ar.item_metadata.status.value,
            version=ct_config_definition_ar.item_metadata.version,
            user_initials=ct_config_definition_ar.item_metadata.user_initials,
            change_description=ct_config_definition_ar.item_metadata.change_description,
        )


class CTConfigPostInput(CTConfigBaseModel):
    # field used to create a configuration based on codelist name
    configured_codelist_name: Optional[str]

    @validator("*")
    # pylint:disable=no-self-argument
    def replace_empty_string_with_none(cls, field):
        if field == "":
            return None
        return field


class CTConfigPatchInput(CTConfigBaseModel):
    change_description: str
