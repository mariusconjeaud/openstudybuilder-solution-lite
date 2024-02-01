from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.models.syntax import (
    ActivityInstructionPreInstanceRoot,
    ActivityInstructionPreInstanceValue,
    ActivityInstructionTemplateRoot,
)
from clinical_mdr_api.domain_repositories.syntax_instances.generic_syntax_instance_repository import (
    GenericSyntaxInstanceRepository,
)
from clinical_mdr_api.domains.syntax_pre_instances.activity_instruction_pre_instance import (
    ActivityInstructionPreInstanceAR,
)
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryVO


class ActivityInstructionPreInstanceRepository(
    GenericSyntaxInstanceRepository[ActivityInstructionPreInstanceAR]
):
    root_class = ActivityInstructionPreInstanceRoot
    value_class = ActivityInstructionPreInstanceValue
    template_class = ActivityInstructionTemplateRoot

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        root: ActivityInstructionPreInstanceRoot,
        library: Library,
        relationship: VersionRelationship,
        value: ActivityInstructionPreInstanceValue,
        study_count: int = 0,
        **_kwargs,
    ):
        return ActivityInstructionPreInstanceAR.from_repository_values(
            uid=root.uid,
            sequence_id=root.sequence_id,
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
        root, item = super()._create(item)

        for indication in item.indications or []:
            if indication:
                root.has_indication.connect(self._get_indication(indication.uid))
        for activity in item.activities or []:
            if activity:
                root.has_activity.connect(self._get_activity(activity.uid))
        for group in item.activity_groups or []:
            if group:
                root.has_activity_group.connect(self._get_activity_group(group.uid))
        for group in item.activity_subgroups or []:
            if group:
                root.has_activity_subgroup.connect(
                    self._get_activity_subgroup(group.uid)
                )

        return item
