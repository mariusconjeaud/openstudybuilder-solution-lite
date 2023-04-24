from typing import Optional

from clinical_mdr_api.domain.syntax_pre_instances.objective_pre_instance import (
    ObjectivePreInstanceAR,
)
from clinical_mdr_api.domain.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)
from clinical_mdr_api.domain_repositories.models.syntax import (
    ObjectivePreInstanceRoot,
    ObjectivePreInstanceValue,
    ObjectiveTemplateRoot,
)
from clinical_mdr_api.domain_repositories.syntax_instances.generic_syntax_instance_repository import (
    GenericSyntaxInstanceRepository,
)


class ObjectivePreInstanceRepository(
    GenericSyntaxInstanceRepository[ObjectivePreInstanceAR]
):
    root_class = ObjectivePreInstanceRoot
    value_class = ObjectivePreInstanceValue
    template_class = ObjectiveTemplateRoot

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        *,
        root: VersionRoot,
        library: Library,
        relationship: VersionRelationship,
        value: VersionValue,
        study_count: Optional[int] = None,
    ):
        return ObjectivePreInstanceAR.from_repository_values(
            uid=root.uid,
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
        item = super()._create(item)
        root = self.root_class.nodes.get(uid=item.uid)

        root.is_confirmatory_testing = item.is_confirmatory_testing
        self._db_save_node(root)

        if item.indications:
            for indication in item.indications:
                indication = self._get_indication(indication.uid)
                root.has_indication.connect(indication)
        if item.categories:
            for category in item.categories:
                category = self._get_category(category[0].uid)
                root.has_category.connect(category)

        return item
