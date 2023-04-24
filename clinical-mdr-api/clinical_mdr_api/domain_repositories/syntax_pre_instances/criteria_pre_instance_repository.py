from typing import Optional

from clinical_mdr_api.domain.syntax_pre_instances.criteria_pre_instance import (
    CriteriaPreInstanceAR,
)
from clinical_mdr_api.domain.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)
from clinical_mdr_api.domain_repositories.models.syntax import (
    CriteriaPreInstanceRoot,
    CriteriaPreInstanceValue,
    CriteriaTemplateRoot,
)
from clinical_mdr_api.domain_repositories.syntax_instances.generic_syntax_instance_repository import (
    GenericSyntaxInstanceRepository,
)


class CriteriaPreInstanceRepository(
    GenericSyntaxInstanceRepository[CriteriaPreInstanceAR]
):
    root_class = CriteriaPreInstanceRoot
    value_class = CriteriaPreInstanceValue
    template_class = CriteriaTemplateRoot

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        *,
        root: VersionRoot,
        library: Library,
        relationship: VersionRelationship,
        value: VersionValue,
        study_count: Optional[int] = None,
    ):
        return CriteriaPreInstanceAR.from_repository_values(
            uid=root.uid,
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=(lambda _: library.is_editable),
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
            template=self._get_template(root, value, relationship.start_date),
            study_count=study_count,
        )

    def _create(self, item: CriteriaPreInstanceAR) -> CriteriaPreInstanceAR:
        """
        This method calls the generic _create method, then extends it to add specific actions
        Specific actions are :
        * Attaching root node to indication nodes
        * Attaching root node to category nodes
        * Attaching root node to sub_category nodes
        """
        item = super()._create(item)
        root = self.root_class.nodes.get(uid=item.uid)

        if item.indications:
            for indication in item.indications:
                indication = self._get_indication(indication.uid)
                root.has_indication.connect(indication)
        if item.categories:
            for category in item.categories:
                category = self._get_category(category[0].uid)
                root.has_category.connect(category)
        if item.sub_categories:
            for category in item.sub_categories:
                category = self._get_category(category[0].uid)
                root.has_subcategory.connect(category)

        return item
