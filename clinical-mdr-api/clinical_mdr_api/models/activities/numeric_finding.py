from typing import Callable, Optional

from clinical_mdr_api.domain.concepts.activities.activity import ActivityAR
from clinical_mdr_api.domain.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domain.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domain.concepts.activities.numeric_finding import NumericFindingAR
from clinical_mdr_api.domain.controlled_terminology.ct_term_name import CTTermNameAR
from clinical_mdr_api.domain.unit_definition.unit_definition import UnitDefinitionAR
from clinical_mdr_api.models import Library
from clinical_mdr_api.models.activities.activity import ActivityHierarchySimpleModel
from clinical_mdr_api.models.activities.finding import (
    Finding,
    FindingCreateInput,
    FindingEditInput,
    FindingVersion,
)
from clinical_mdr_api.models.ct_term import SimpleTermModel


class NumericFinding(Finding):
    molecular_weight: Optional[int]
    convert_to_si_unit: Optional[bool]
    convert_to_us_conventional_unit: Optional[bool]
    unit_dimension: Optional[SimpleTermModel]
    unit_definition: Optional[SimpleTermModel]

    @classmethod
    def from_activity_ar(
        cls,
        activity_ar: NumericFindingAR,
        find_term_by_uid: Callable[[str], Optional[CTTermNameAR]],
        find_unit_definition_by_uid: Callable[[str], Optional[UnitDefinitionAR]],
        find_activity_hierarchy_by_uid: Callable[[str], Optional[ActivityAR]],
        find_activity_subgroup_by_uid: Callable[[str], Optional[ActivitySubGroupAR]],
        find_activity_group_by_uid: Callable[[str], Optional[ActivityGroupAR]],
    ) -> "NumericFinding":

        activity_subgroup_uids = [
            find_activity_hierarchy_by_uid(activity_uid).concept_vo.activity_subgroup
            for activity_uid in activity_ar.concept_vo.activity_uids
        ]
        activity_group_uids = [
            find_activity_subgroup_by_uid(subgroup_uid).concept_vo.activity_group
            for subgroup_uid in activity_subgroup_uids
        ]

        sdtm_variable = cls._get_term_model(
            activity_ar.concept_vo, "sdtm_variable_uid", "sdtm_variable_name"
        )
        sdtm_subcat = cls._get_term_model(
            activity_ar.concept_vo, "sdtm_subcat_uid", "sdtm_subcat_name"
        )
        sdtm_cat = cls._get_term_model(
            activity_ar.concept_vo, "sdtm_cat_uid", "sdtm_cat_name"
        )
        sdtm_domain = cls._get_term_model(
            activity_ar.concept_vo, "sdtm_domain_uid", "sdtm_domain_name"
        )
        specimen = cls._get_term_model(
            activity_ar.concept_vo, "specimen_uid", "specimen_name"
        )

        return cls(
            uid=activity_ar.uid,
            type=activity_ar.concept_vo.activity_type,
            name=activity_ar.name,
            name_sentence_case=activity_ar.concept_vo.name_sentence_case,
            definition=activity_ar.concept_vo.definition,
            abbreviation=activity_ar.concept_vo.abbreviation,
            topic_code=activity_ar.concept_vo.topic_code,
            adam_param_code=activity_ar.concept_vo.adam_param_code,
            legacy_description=activity_ar.concept_vo.legacy_description,
            sdtm_variable=sdtm_variable,
            sdtm_subcat=sdtm_subcat,
            sdtm_cat=sdtm_cat,
            sdtm_domain=sdtm_domain,
            activities=sorted(
                [
                    ActivityHierarchySimpleModel.from_activity_uid(
                        uid=activity,
                        find_activity_by_uid=find_activity_hierarchy_by_uid,
                    )
                    for activity in activity_ar.concept_vo.activity_uids
                ],
                key=lambda item: item.name,
            ),
            activity_subgroups=sorted(
                [
                    ActivityHierarchySimpleModel.from_activity_uid(
                        uid=activity_subgroup,
                        find_activity_by_uid=find_activity_subgroup_by_uid,
                    )
                    for activity_subgroup in activity_subgroup_uids
                ],
                key=lambda item: item.name,
            ),
            activity_groups=sorted(
                [
                    ActivityHierarchySimpleModel.from_activity_uid(
                        uid=activity_group,
                        find_activity_by_uid=find_activity_group_by_uid,
                    )
                    for activity_group in activity_group_uids
                ],
                key=lambda item: item.name,
            ),
            value_sas_display_format=activity_ar.concept_vo.value_sas_display_format,
            specimen=specimen,
            test_code=SimpleTermModel.from_ct_code(
                c_code=activity_ar.concept_vo.test_code_uid,
                find_term_by_uid=find_term_by_uid,
            ),
            molecular_weight=activity_ar.concept_vo.molecular_weight,
            convert_to_si_unit=activity_ar.concept_vo.convert_to_si_unit,
            convert_to_us_conventional_unit=activity_ar.concept_vo.convert_to_us_conventional_unit,
            unit_dimension=SimpleTermModel.from_ct_code(
                c_code=activity_ar.concept_vo.unit_dimension_uid,
                find_term_by_uid=find_term_by_uid,
            ),
            unit_definition=SimpleTermModel.from_ct_code(
                c_code=activity_ar.concept_vo.unit_definition_uid,
                find_term_by_uid=find_unit_definition_by_uid,
            ),
            library_name=Library.from_library_vo(activity_ar.library).name,
            start_date=activity_ar.item_metadata.start_date,
            end_date=activity_ar.item_metadata.end_date,
            status=activity_ar.item_metadata.status.value,
            version=activity_ar.item_metadata.version,
            change_description=activity_ar.item_metadata.change_description,
            user_initials=activity_ar.item_metadata.user_initials,
            possible_actions=sorted(
                [_.value for _ in activity_ar.get_possible_actions()]
            ),
        )


class NumericFindingCreateInput(FindingCreateInput):
    molecular_weight: Optional[int] = None
    convert_to_si_unit: Optional[bool] = None
    convert_to_us_conventional_unit: Optional[bool] = None
    unit_dimension: Optional[str] = None
    unit_definition: Optional[str] = None


class NumericFindingEditInput(FindingEditInput):
    molecular_weight: Optional[int]
    convert_to_si_unit: Optional[bool]
    convert_to_us_conventional_unit: Optional[bool]
    unit_dimension: Optional[str]
    unit_definition: Optional[str]


class NumericFindingVersion(FindingVersion, NumericFinding):
    pass
