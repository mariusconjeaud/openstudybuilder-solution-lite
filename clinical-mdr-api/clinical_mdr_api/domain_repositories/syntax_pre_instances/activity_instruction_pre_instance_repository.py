from typing import Optional

from clinical_mdr_api.domain.syntax_pre_instances.activity_instruction_pre_instance import (
    ActivityInstructionPreInstanceAR,
)
from clinical_mdr_api.domain.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)
from clinical_mdr_api.domain_repositories.models.syntax import (
    ActivityInstructionPreInstanceRoot,
    ActivityInstructionPreInstanceValue,
    ActivityInstructionTemplateRoot,
)
from clinical_mdr_api.domain_repositories.syntax_instances.generic_syntax_instance_repository import (
    GenericSyntaxInstanceRepository,
)


class ActivityInstructionPreInstanceRepository(
    GenericSyntaxInstanceRepository[ActivityInstructionPreInstanceAR]
):
    root_class = ActivityInstructionPreInstanceRoot
    value_class = ActivityInstructionPreInstanceValue
    template_class = ActivityInstructionTemplateRoot

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        *,
        root: VersionRoot,
        library: Library,
        relationship: VersionRelationship,
        value: VersionValue,
        study_count: Optional[int] = None,
    ):
        return ActivityInstructionPreInstanceAR.from_repository_values(
            uid=root.uid,
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=(lambda _: library.is_editable),
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
            template=self._get_template(root, value, relationship.start_date),
            study_count=study_count,
        )

    def _create(
        self, item: ActivityInstructionPreInstanceAR
    ) -> ActivityInstructionPreInstanceAR:
        """
        This method calls the generic _create method, then extends it to add specific actions
        Specific actions are :
        * Attaching root node to indication nodes
        * Attaching root node to activity, activity group, activity sub group nodes
        """
        item = super()._create(item)
        root = self.root_class.nodes.get(uid=item.uid)

        if item.indications:
            for indication in item.indications:
                indication = self._get_indication(indication.uid)
                root.has_indication.connect(indication)
        if item.activities:
            for activity in item.activities:
                activity = self._get_activity(activity.uid)
                root.has_activity.connect(activity)
        if item.activity_groups:
            for group in item.activity_groups:
                group = self._get_activity_group(group.uid)
                root.has_activity_group.connect(group)
        if item.activity_subgroups:
            for group in item.activity_subgroups:
                group = self._get_activity_subgroup(group.uid)
                root.has_activity_subgroup.connect(group)

        return item
