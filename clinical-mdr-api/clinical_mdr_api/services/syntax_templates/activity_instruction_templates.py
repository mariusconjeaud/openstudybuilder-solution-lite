from typing import Optional, Sequence, Tuple

from neomodel import db
from pydantic.main import BaseModel

from clinical_mdr_api import exceptions
from clinical_mdr_api.domain_repositories.models.syntax import (
    ActivityInstructionTemplateRoot,
)
from clinical_mdr_api.domain_repositories.syntax_instances.activity_instruction_repository import (
    ActivityInstructionRepository,
)
from clinical_mdr_api.domain_repositories.syntax_pre_instances.activity_instruction_pre_instance_repository import (
    ActivityInstructionPreInstanceRepository,
)
from clinical_mdr_api.domain_repositories.syntax_templates.activity_instruction_template_repository import (
    ActivityInstructionTemplateRepository,
)
from clinical_mdr_api.domains._utils import generate_seq_id
from clinical_mdr_api.domains.concepts.activities.activity import ActivityAR
from clinical_mdr_api.domains.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domains.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domains.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domains.syntax_templates.activity_instruction_template import (
    ActivityInstructionTemplateAR,
)
from clinical_mdr_api.domains.syntax_templates.template import TemplateVO
from clinical_mdr_api.models.concepts.activities.activity import Activity
from clinical_mdr_api.models.concepts.activities.activity_group import ActivityGroup
from clinical_mdr_api.models.concepts.activities.activity_sub_group import (
    ActivitySubGroup,
)
from clinical_mdr_api.models.dictionaries.dictionary_term import DictionaryTerm
from clinical_mdr_api.models.syntax_templates.activity_instruction_template import (
    ActivityInstructionTemplate,
    ActivityInstructionTemplateCreateInput,
    ActivityInstructionTemplateEditIndexingsInput,
    ActivityInstructionTemplateVersion,
    ActivityInstructionTemplateWithCount,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._utils import (
    raise_404_if_none,
    service_level_generic_filtering,
)
from clinical_mdr_api.services.syntax_templates.generic_syntax_template_service import (
    GenericSyntaxTemplateService,
)


class ActivityInstructionTemplateService(
    GenericSyntaxTemplateService[ActivityInstructionTemplateAR]
):
    aggregate_class = ActivityInstructionTemplateAR
    version_class = ActivityInstructionTemplateVersion
    repository_interface = ActivityInstructionTemplateRepository
    instance_repository_interface = ActivityInstructionRepository
    pre_instance_repository_interface = ActivityInstructionPreInstanceRepository
    root_node_class = ActivityInstructionTemplateRoot

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: ActivityInstructionTemplateAR
    ) -> ActivityInstructionTemplate:
        item_ar = self._set_default_parameter_terms(item_ar)
        cls = (
            ActivityInstructionTemplateWithCount
            if item_ar.counts is not None
            else ActivityInstructionTemplate
        )
        item = cls.from_activity_instruction_template_ar(
            item_ar,
            find_activity_subgroup_by_uid=self._repos.activity_subgroup_repository.find_by_uid_2,
            find_activity_group_by_uid=self._repos.activity_group_repository.find_by_uid_2,
        )
        self._set_indexings(item)
        return item

    def get_all(
        self,
        status: Optional[str] = None,
        return_study_count: bool = True,
        sort_by: Optional[dict] = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: Optional[dict] = None,
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
        total_count: bool = False,
    ) -> GenericFilteringReturn[ActivityInstructionTemplate]:
        all_items = super().get_all(status, return_study_count)

        # The get_all method is only using neomodel, without Cypher query
        # Therefore, the filtering will be done in this service layer
        filtered_items = service_level_generic_filtering(
            items=all_items,
            filter_by=filter_by,
            filter_operator=filter_operator,
            sort_by=sort_by,
            total_count=total_count,
            page_number=page_number,
            page_size=page_size,
        )

        return filtered_items

    def _create_ar_from_input_values(
        self, template: ActivityInstructionTemplateCreateInput
    ) -> ActivityInstructionTemplateAR:
        default_parameter_terms = self._create_default_parameter_entries(
            template_name=template.name,
            default_parameter_terms=template.default_parameter_terms,
        )

        template_vo, library_vo = self._create_template_vo(
            template, default_parameter_terms
        )

        # Get indexings for templates from database
        (
            indications,
            activities,
            activity_groups,
            activity_subgroups,
        ) = self._get_indexings(template)

        # Process item to save
        try:
            item = ActivityInstructionTemplateAR.from_input_values(
                template_value_exists_callback=(
                    lambda _template_vo: self.repository.check_exists_by_name(
                        _template_vo.name
                    )
                ),
                author=self.user_initials,
                template=template_vo,
                library=library_vo,
                generate_uid_callback=self.repository.generate_uid_callback,
                generate_seq_id_callback=generate_seq_id,
                indications=indications,
                activities=activities,
                activity_groups=activity_groups,
                activity_subgroups=activity_subgroups,
            )
        except ValueError as e:
            raise exceptions.ValidationException(e.args[0])

        return item

    @db.transaction
    def patch_indexings(
        self, uid: str, indexings: ActivityInstructionTemplateEditIndexingsInput
    ) -> ActivityInstructionTemplate:
        try:
            self._find_by_uid_or_raise_not_found(uid)
            if indexings.indication_uids is not None:
                self.repository.patch_indications(uid, indexings.indication_uids)
            if indexings.activity_uids is not None:
                self.repository.patch_activities(uid, indexings.activity_uids)
            if indexings.activity_group_uids is not None:
                self.repository.patch_activity_groups(
                    uid, indexings.activity_group_uids
                )
            if indexings.activity_subgroup_uids is not None:
                self.repository.patch_activity_subgroups(
                    uid, indexings.activity_subgroup_uids
                )
        finally:
            self.repository.close()

        return self.get_by_uid(uid)

    def _set_default_parameter_terms(
        self, item: ActivityInstructionTemplateAR
    ) -> ActivityInstructionTemplateAR:
        """This method fetches and sets the default parameter terms for the template

        Args:
            item (ActivityInstructionTemplateAR): The template for which to fetch default parameter terms
        """
        # Get default parameter terms
        default_parameter_terms = self.repository.get_default_parameter_terms(item.uid)

        return ActivityInstructionTemplateAR(
            _uid=item.uid,
            _sequence_id=item.sequence_id,
            _library=item.library,
            _item_metadata=item.item_metadata,
            _counts=item.counts,
            _study_count=item.study_count,
            _indications=item.indications,
            _activities=item.activities,
            _activity_groups=item.activity_groups,
            _activity_subgroups=item.activity_subgroups,
            _template=TemplateVO(
                name=item.template_value.name,
                name_plain=item.template_value.name_plain,
                default_parameter_terms=default_parameter_terms,
                guidance_text=item.template_value.guidance_text,
            ),
        )

    def _set_indexings(self, item: ActivityInstructionTemplate) -> None:
        """
        This method fetches and sets the indexing properties to a syntax activity instruction template.
        """
        if not hasattr(item, "uid"):
            return

        # Get indications
        indications = (
            self._repos.dictionary_term_generic_repository.get_syntax_indications(
                self.root_node_class, item.uid
            )
        )
        if indications:
            item.indications = sorted(
                [
                    DictionaryTerm.from_dictionary_term_ar(indication)
                    for indication in indications
                ],
                key=lambda x: x.term_uid,
            )
        # Get activities
        activities = self._repos.activity_repository.get_syntax_activities(
            self.root_node_class, item.uid
        )
        if activities:
            item.activities = sorted(
                [
                    Activity.from_activity_ar(
                        activity,
                        self._repos.activity_subgroup_repository.find_by_uid_2,
                        self._repos.activity_group_repository.find_by_uid_2,
                    )
                    for activity in activities
                ],
                key=lambda x: x.uid,
            )
        # Get activity groups
        activity_groups = (
            self._repos.activity_group_repository.get_syntax_activity_groups(
                self.root_node_class, item.uid
            )
        )
        if activity_groups:
            item.activity_groups = sorted(
                [
                    ActivityGroup.from_activity_ar(activity)
                    for activity in activity_groups
                ],
                key=lambda x: x.uid,
            )
        # Get activity sub_groups
        activity_subgroups = (
            self._repos.activity_subgroup_repository.get_syntax_activity_subgroups(
                self.root_node_class, item.uid
            )
        )
        if activity_subgroups:
            item.activity_subgroups = sorted(
                [
                    ActivitySubGroup.from_activity_ar(
                        activity, self._repos.activity_group_repository.find_by_uid_2
                    )
                    for activity in activity_subgroups
                ],
                key=lambda x: x.uid,
            )

    def _get_indexings(
        self, template: BaseModel
    ) -> Tuple[
        Sequence[DictionaryTermAR],
        Sequence[ActivityAR],
        Sequence[ActivityGroupAR],
        Sequence[ActivitySubGroupAR],
    ]:
        indications: Sequence[DictionaryTermAR] = []
        activities: Sequence[ActivityAR] = []
        activity_groups: Sequence[ActivityGroupAR] = []
        activity_subgroups: Sequence[ActivitySubGroupAR] = []

        if template.indication_uids and len(template.indication_uids) > 0:
            for uid in template.indication_uids:
                indication = self._repos.dictionary_term_generic_repository.find_by_uid(
                    term_uid=uid
                )
                raise_404_if_none(
                    indication,
                    f"Indication with uid '{uid}' does not exist.",
                )
                indications.append(indication)

        if template.activity_uids and len(template.activity_uids) > 0:
            for uid in template.activity_uids:
                activity = self._repos.activity_repository.find_by_uid_2(uid=uid)
                raise_404_if_none(
                    activity,
                    f"Activity with uid '{uid}' does not exist.",
                )
                activities.append(activity)

        if template.activity_group_uids and len(template.activity_group_uids) > 0:
            for uid in template.activity_group_uids:
                activity_group = self._repos.activity_group_repository.find_by_uid_2(
                    uid=uid
                )
                raise_404_if_none(
                    activity_group,
                    f"Activity group with uid '{uid}' does not exist.",
                )
                activity_groups.append(activity_group)

        if template.activity_subgroup_uids and len(template.activity_subgroup_uids) > 0:
            for uid in template.activity_subgroup_uids:
                activity_subgroup = (
                    self._repos.activity_subgroup_repository.find_by_uid_2(uid=uid)
                )
                raise_404_if_none(
                    activity_subgroup,
                    f"Activity subgroup with uid '{uid}' does not exist.",
                )
                activity_subgroups.append(activity_subgroup)

        return indications, activities, activity_groups, activity_subgroups
