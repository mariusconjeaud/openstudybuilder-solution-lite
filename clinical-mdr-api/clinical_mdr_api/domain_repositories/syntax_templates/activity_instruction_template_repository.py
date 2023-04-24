from typing import Optional

from clinical_mdr_api.domain.syntax_templates.activity_instruction_template import (
    ActivityInstructionTemplateAR,
)
from clinical_mdr_api.domain.syntax_templates.template import InstantiationCountsVO
from clinical_mdr_api.domain.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.models.syntax import (
    ActivityInstructionTemplateRoot,
    ActivityInstructionTemplateValue,
)
from clinical_mdr_api.domain_repositories.syntax_templates.generic_syntax_template_repository import (
    GenericSyntaxTemplateRepository,
)


class ActivityInstructionTemplateRepository(
    GenericSyntaxTemplateRepository[ActivityInstructionTemplateAR]
):
    root_class = ActivityInstructionTemplateRoot
    value_class = ActivityInstructionTemplateValue

    def check_exists_by_name_in_study(self, name: str, study_uid: str) -> bool:
        raise NotImplementedError()

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        *,
        root: ActivityInstructionTemplateRoot,
        library: Library,
        relationship: VersionRelationship,
        value: ActivityInstructionTemplateValue,
        study_count: Optional[int] = None,
        counts: Optional[InstantiationCountsVO] = None,
    ) -> ActivityInstructionTemplateAR:
        return ActivityInstructionTemplateAR.from_repository_values(
            uid=root.uid,
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=(lambda _: library.is_editable),
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
            template=self._get_template(value),
            study_count=study_count,
            counts=counts,
        )

    def _create(
        self, item: ActivityInstructionTemplateAR
    ) -> ActivityInstructionTemplateAR:
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
