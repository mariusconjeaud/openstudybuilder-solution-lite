from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.models.syntax import (
    FootnotePreInstanceRoot,
    FootnotePreInstanceValue,
    FootnoteTemplateRoot,
)
from clinical_mdr_api.domain_repositories.syntax_instances.generic_syntax_instance_repository import (
    GenericSyntaxInstanceRepository,
)
from clinical_mdr_api.domains.syntax_pre_instances.footnote_pre_instance import (
    FootnotePreInstanceAR,
)
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryVO


class FootnotePreInstanceRepository(
    GenericSyntaxInstanceRepository[FootnotePreInstanceAR]
):
    root_class = FootnotePreInstanceRoot
    value_class = FootnotePreInstanceValue
    template_class = FootnoteTemplateRoot

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        root: FootnotePreInstanceRoot,
        library: Library,
        relationship: VersionRelationship,
        value: FootnotePreInstanceValue,
        study_count: int = 0,
        **_kwargs,
    ):
        return FootnotePreInstanceAR.from_repository_values(
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

    def _create(self, item: FootnotePreInstanceAR) -> FootnotePreInstanceAR:
        """
        This method calls the generic _create method, then extends it to add specific actions
        Specific actions are :
        * Attaching root node to indication nodes
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
