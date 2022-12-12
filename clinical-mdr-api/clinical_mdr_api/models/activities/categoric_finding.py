from typing import Callable, Optional

from clinical_mdr_api.domain.concepts.activities.activity import ActivityAR
from clinical_mdr_api.domain.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domain.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domain.concepts.activities.categoric_finding import (
    CategoricFindingAR,
)
from clinical_mdr_api.domain.controlled_terminology.ct_term_name import CTTermNameAR
from clinical_mdr_api.models import Library
from clinical_mdr_api.models.activities.activity import ActivityHierarchySimpleModel
from clinical_mdr_api.models.activities.finding import (
    Finding,
    FindingCreateInput,
    FindingEditInput,
    FindingVersion,
)
from clinical_mdr_api.models.ct_term import SimpleTermModel


class CategoricFinding(Finding):
    categoric_response_value: Optional[SimpleTermModel]
    categoric_response_list: Optional[SimpleTermModel]

    @classmethod
    def from_activity_ar(
        cls,
        activity_ar: CategoricFindingAR,
        find_term_by_uid: Callable[[str], Optional[CTTermNameAR]],
        find_activity_hierarchy_by_uid: Callable[[str], Optional[ActivityAR]],
        find_activity_subgroup_by_uid: Callable[[str], Optional[ActivitySubGroupAR]],
        find_activity_group_by_uid: Callable[[str], Optional[ActivityGroupAR]],
    ) -> "CategoricFinding":

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
            categoric_response_value=SimpleTermModel.from_ct_code(
                c_code=activity_ar.concept_vo.categoric_response_value_uid,
                find_term_by_uid=find_term_by_uid,
            ),
            categoric_response_list=SimpleTermModel.from_ct_code(
                c_code=activity_ar.concept_vo.categoric_response_list_uid,
                find_term_by_uid=find_term_by_uid,
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


class CategoricFindingCreateInput(FindingCreateInput):
    categoric_response_value: Optional[str] = None
    categoric_response_list: Optional[str] = None


class CategoricFindingEditInput(FindingEditInput):
    categoric_response_value: Optional[str]
    categoric_response_list: Optional[str]


class CategoricFindingVersion(FindingVersion, CategoricFinding):
    pass
