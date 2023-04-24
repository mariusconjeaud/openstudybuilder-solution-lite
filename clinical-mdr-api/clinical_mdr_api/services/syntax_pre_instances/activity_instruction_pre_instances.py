from typing import Optional, Sequence, Tuple, cast

from pydantic import BaseModel

from clinical_mdr_api.domain.concepts.activities.activity import ActivityAR
from clinical_mdr_api.domain.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domain.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domain.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domain.library.library_ar import LibraryAR
from clinical_mdr_api.domain.syntax_pre_instances.activity_instruction_pre_instance import (
    ActivityInstructionPreInstanceAR,
)
from clinical_mdr_api.domain.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.domain_repositories.models.syntax import (
    ActivityInstructionPreInstanceRoot,
)
from clinical_mdr_api.domain_repositories.syntax_pre_instances.activity_instruction_pre_instance_repository import (
    ActivityInstructionPreInstanceRepository,
)
from clinical_mdr_api.exceptions import NotFoundException
from clinical_mdr_api.models.activities.activity import Activity
from clinical_mdr_api.models.activities.activity_group import ActivityGroup
from clinical_mdr_api.models.activities.activity_sub_group import ActivitySubGroup
from clinical_mdr_api.models.dictionary_term import DictionaryTerm
from clinical_mdr_api.models.syntax_pre_instances.activity_instruction_pre_instance import (
    ActivityInstructionPreInstance,
    ActivityInstructionPreInstanceVersion,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._utils import service_level_generic_filtering
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
        return ActivityInstructionPreInstance.from_activity_instruction_pre_instance_ar(
            item_ar,
            find_activity_subgroup_by_uid=self._repos.activity_subgroup_repository.find_by_uid_2,
            find_activity_group_by_uid=self._repos.activity_group_repository.find_by_uid_2,
        )

    def create_ar_from_input_values(
        self,
        template,
        generate_uid_callback=None,
        study_uid: Optional[str] = None,
        template_uid: Optional[str] = None,
        include_study_endpoints: Optional[bool] = False,
    ) -> ActivityInstructionPreInstanceAR:
        parameter_terms = self._create_parameter_entries(
            template,
            template_uid=template_uid,
            study_uid=study_uid,
            include_study_endpoints=include_study_endpoints,
        )

        template_uid = template_uid or getattr(template, self.template_uid_property)

        template_vo = self.parametrized_template_vo_class.from_input_values_2(
            template_uid=template_uid,
            parameter_terms=parameter_terms,
            get_final_template_vo_by_template_uid_callback=self._get_template_vo_by_template_uid,
        )

        try:
            library_vo = LibraryVO.from_input_values_2(
                library_name=template.library_name,
                is_library_editable_callback=(
                    lambda name: (
                        cast(
                            LibraryAR, self._repos.library_repository.find_by_name(name)
                        ).is_editable
                        if self._repos.library_repository.find_by_name(name) is not None
                        else None
                    )
                ),
            )
        except ValueError as exc:
            raise NotFoundException(
                f"The library with the name='{template.library_name}' could not be found."
            ) from exc

        (
            indications,
            activities,
            activity_groups,
            activity_subgroups,
        ) = self._get_indexings(template)

        item = ActivityInstructionPreInstanceAR.from_input_values(
            author=self.user_initials,
            template=template_vo,
            library=library_vo,
            generate_uid_callback=self.repository.generate_uid_callback,
            indications=indications,
            activities=activities,
            activity_groups=activity_groups,
            activity_subgroups=activity_subgroups,
        )
        return item

    def _set_indexings(self, item: ActivityInstructionPreInstance) -> None:
        """
        This method fetches and sets the indexing properties to a syntax activity instruction pre instance.
        """
        # Get indications
        indications = (
            self._repos.dictionary_term_generic_repository.get_syntax_indications(
                self.root_node_class, item.uid
            )
        )
        if indications:
            item.indications = [
                DictionaryTerm.from_dictionary_term_ar(indication)
                for indication in indications
            ]
        # Get activities
        activities = self._repos.activity_repository.get_syntax_activities(
            self.root_node_class, item.uid
        )
        if activities:
            item.activities = [
                Activity.from_activity_ar(
                    activity,
                    self._repos.activity_subgroup_repository.find_by_uid_2,
                    self._repos.activity_group_repository.find_by_uid_2,
                )
                for activity in activities
            ]
        # Get activity groups
        activity_groups = (
            self._repos.activity_group_repository.get_syntax_activity_groups(
                self.root_node_class, item.uid
            )
        )
        if activity_groups:
            item.activity_groups = [
                ActivityGroup.from_activity_ar(activity) for activity in activity_groups
            ]
        # Get activity sub_groups
        activity_subgroups = (
            self._repos.activity_subgroup_repository.get_syntax_activity_subgroups(
                self.root_node_class, item.uid
            )
        )
        if activity_subgroups:
            item.activity_subgroups = [
                ActivitySubGroup.from_activity_ar(
                    activity, self._repos.activity_group_repository.find_by_uid_2
                )
                for activity in activity_subgroups
            ]

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
                indications.append(indication)

        if template.activity_uids and len(template.activity_uids) > 0:
            for uid in template.activity_uids:
                activity = self._repos.activity_repository.find_by_uid_2(uid=uid)
                activities.append(activity)

        if template.activity_group_uids and len(template.activity_group_uids) > 0:
            for uid in template.activity_group_uids:
                activity_group = self._repos.activity_group_repository.find_by_uid_2(
                    uid=uid
                )
                activity_groups.append(activity_group)

        if template.activity_subgroup_uids and len(template.activity_subgroup_uids) > 0:
            for uid in template.activity_subgroup_uids:
                activity_subgroup = (
                    self._repos.activity_subgroup_repository.find_by_uid_2(uid=uid)
                )
                activity_subgroups.append(activity_subgroup)

        return indications, activities, activity_groups, activity_subgroups

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
    ) -> GenericFilteringReturn[ActivityInstructionPreInstance]:
        pre_instances = (
            self._repos.activity_instruction_pre_instance_repository.find_all()
        )
        all_items = []
        for pre_instance in pre_instances:
            item = self._transform_aggregate_root_to_pydantic_model(pre_instance)
            self._set_indexings(item)
            all_items.append(item)

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
