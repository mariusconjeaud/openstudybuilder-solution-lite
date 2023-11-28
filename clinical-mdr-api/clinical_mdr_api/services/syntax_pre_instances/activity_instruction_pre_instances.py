from neomodel import db
from pydantic import BaseModel

from clinical_mdr_api.domain_repositories.models.syntax import (
    ActivityInstructionPreInstanceRoot,
)
from clinical_mdr_api.domain_repositories.syntax_pre_instances.activity_instruction_pre_instance_repository import (
    ActivityInstructionPreInstanceRepository,
)
from clinical_mdr_api.domains.concepts.activities.activity import ActivityAR
from clinical_mdr_api.domains.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domains.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domains.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domains.syntax_pre_instances.activity_instruction_pre_instance import (
    ActivityInstructionPreInstanceAR,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemStatus,
    VersioningException,
)
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.concepts.activities.activity import Activity
from clinical_mdr_api.models.concepts.activities.activity_group import ActivityGroup
from clinical_mdr_api.models.concepts.activities.activity_sub_group import (
    ActivitySubGroup,
)
from clinical_mdr_api.models.dictionaries.dictionary_term import DictionaryTerm
from clinical_mdr_api.models.syntax_pre_instances.activity_instruction_pre_instance import (
    ActivityInstructionPreInstance,
    ActivityInstructionPreInstanceIndexingsInput,
    ActivityInstructionPreInstanceVersion,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._utils import (
    raise_404_if_none,
    service_level_generic_filtering,
)
from clinical_mdr_api.services.syntax_instances.activity_instructions import (
    ActivityInstructionService,
)


class ActivityInstructionPreInstanceService(
    ActivityInstructionService[ActivityInstructionPreInstanceAR]
):
    aggregate_class = ActivityInstructionPreInstanceAR
    repository_interface = ActivityInstructionPreInstanceRepository
    version_class = ActivityInstructionPreInstanceVersion
    template_uid_property = "activity_instruction_template_uid"
    template_name_property = "activity_instruction_template"
    root_node_class = ActivityInstructionPreInstanceRoot

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: ActivityInstructionPreInstanceAR
    ) -> ActivityInstructionPreInstance:
        item = ActivityInstructionPreInstance.from_activity_instruction_pre_instance_ar(
            item_ar,
            find_activity_subgroup_by_uid=self._repos.activity_subgroup_repository.find_by_uid_2,
            find_activity_group_by_uid=self._repos.activity_group_repository.find_by_uid_2,
        )
        self._set_indexings(item)
        return item

    def create_ar_from_input_values(
        self,
        template,
        generate_uid_callback=None,
        study_uid: str | None = None,
        template_uid: str | None = None,
        include_study_endpoints: bool | None = False,
    ) -> ActivityInstructionPreInstanceAR:
        item_ar = super().create_ar_from_input_values(
            template=template,
            generate_uid_callback=generate_uid_callback,
            next_available_sequence_id_callback=self.repository.next_available_sequence_id,
            study_uid=study_uid,
            template_uid=template_uid,
            include_study_endpoints=include_study_endpoints,
        )

        (
            indications,
            activities,
            activity_groups,
            activity_subgroups,
        ) = self._get_indexings(template)

        item_ar._indications = indications
        item_ar._activities = activities
        item_ar._activity_groups = activity_groups
        item_ar._activity_subgroups = activity_subgroups

        return item_ar

    def _set_indexings(self, item: ActivityInstructionPreInstance) -> None:
        """
        This method fetches and sets the indexing properties to a syntax activity instruction pre-instance.
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
    ) -> tuple[
        list[DictionaryTermAR],
        list[ActivityAR],
        list[ActivityGroupAR],
        list[ActivitySubGroupAR],
    ]:
        indications: list[DictionaryTermAR] = []
        activities: list[ActivityAR] = []
        activity_groups: list[ActivityGroupAR] = []
        activity_subgroups: list[ActivitySubGroupAR] = []

        for uid in template.indication_uids:
            indication = self._repos.dictionary_term_generic_repository.find_by_uid(
                term_uid=uid
            )
            raise_404_if_none(
                indication,
                f"Indication with uid '{uid}' does not exist.",
            )
            indications.append(indication)

        for uid in template.activity_uids:
            activity = self._repos.activity_repository.find_by_uid_2(uid=uid)
            raise_404_if_none(
                activity,
                f"Activity with uid '{uid}' does not exist.",
            )
            activities.append(activity)

        for uid in template.activity_group_uids:
            activity_group = self._repos.activity_group_repository.find_by_uid_2(
                uid=uid
            )
            raise_404_if_none(
                activity_group,
                f"Activity group with uid '{uid}' does not exist.",
            )
            activity_groups.append(activity_group)

        for uid in template.activity_subgroup_uids:
            activity_subgroup = self._repos.activity_subgroup_repository.find_by_uid_2(
                uid=uid
            )
            raise_404_if_none(
                activity_subgroup,
                f"Activity subgroup with uid '{uid}' does not exist.",
            )
            activity_subgroups.append(activity_subgroup)

        return indications, activities, activity_groups, activity_subgroups

    def get_all(
        self,
        status: LibraryItemStatus | None = None,
        return_study_count: bool = True,
        sort_by: dict | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        total_count: bool = False,
    ) -> GenericFilteringReturn[ActivityInstructionPreInstance]:
        pre_instances = (
            self._repos.activity_instruction_pre_instance_repository.find_all(
                status=status, return_study_count=return_study_count
            )
        )
        all_items = [
            self._transform_aggregate_root_to_pydantic_model(pre_instance)
            for pre_instance in pre_instances
        ]

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

    @db.transaction
    def patch_indexings(
        self, uid: str, indexings: ActivityInstructionPreInstanceIndexingsInput
    ) -> ActivityInstructionPreInstance:
        try:
            self._find_by_uid_or_raise_not_found(uid)
            if getattr(indexings, "indication_uids", None):
                self.repository.patch_indications(uid, indexings.indication_uids)
            if getattr(indexings, "activity_uids", None):
                self.repository.patch_activities(uid, indexings.activity_uids)
            if getattr(indexings, "activity_group_uids", None):
                self.repository.patch_activity_groups(
                    uid, indexings.activity_group_uids
                )
            if getattr(indexings, "activity_subgroup_uids", None):
                self.repository.patch_activity_subgroups(
                    uid, indexings.activity_subgroup_uids
                )
        finally:
            self.repository.close()

        return self.get_by_uid(uid)

    @db.transaction
    def create_new_version(self, uid: str) -> ActivityInstructionPreInstance:
        try:
            item = self._find_by_uid_or_raise_not_found(uid, for_update=True)
            item._create_new_version(author=self.user_initials)
            self.repository.save(item)
            return self._transform_aggregate_root_to_pydantic_model(item)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e
