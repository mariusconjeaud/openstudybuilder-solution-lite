from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.models.syntax import (
    ObjectivePreInstanceRoot,
    ObjectivePreInstanceValue,
    ObjectiveTemplateRoot,
)
from clinical_mdr_api.domain_repositories.syntax_instances.generic_syntax_instance_repository import (
    GenericSyntaxInstanceRepository,
)
from clinical_mdr_api.domains.syntax_pre_instances.objective_pre_instance import (
    ObjectivePreInstanceAR,
)
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryVO


class ObjectivePreInstanceRepository(
    GenericSyntaxInstanceRepository[ObjectivePreInstanceAR]
):
    root_class = ObjectivePreInstanceRoot
    value_class = ObjectivePreInstanceValue
    template_class = ObjectiveTemplateRoot

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        *,
        root: ObjectivePreInstanceRoot,
        library: Library,
        relationship: VersionRelationship,
        value: ObjectivePreInstanceValue,
        study_count: int = 0,
    ):
        return ObjectivePreInstanceAR.from_repository_values(
            uid=root.uid,
            sequence_id=root.sequence_id,
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=(lambda _: library.is_editable),
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
            template=self._get_template(root, value, relationship.start_date),
            is_confirmatory_testing=root.is_confirmatory_testing,
            study_count=study_count,
        )

    def _create(self, item: ObjectivePreInstanceAR) -> ObjectivePreInstanceAR:
        """
        This method calls the generic _create method, then extends it to add specific actions
        Specific actions are :
        * Attaching root node to indication nodes
        * Attaching root node to category nodes
        """
        root, item = super()._create(item)

        root.is_confirmatory_testing = item.is_confirmatory_testing
        self._db_save_node(root)

        for indication in item.indications or []:
            if indication:
                root.has_indication.connect(self._get_indication(indication.uid))
        for category in item.categories or []:
            if category and category[0]:
                root.has_category.connect(self._get_category(category[0].uid))

        return item
