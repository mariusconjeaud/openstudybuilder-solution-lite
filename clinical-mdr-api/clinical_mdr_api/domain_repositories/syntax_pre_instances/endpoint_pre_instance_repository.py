from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.models.syntax import (
    EndpointPreInstanceRoot,
    EndpointPreInstanceValue,
    EndpointTemplateRoot,
)
from clinical_mdr_api.domain_repositories.syntax_instances.generic_syntax_instance_repository import (
    GenericSyntaxInstanceRepository,
)
from clinical_mdr_api.domains.syntax_pre_instances.endpoint_pre_instance import (
    EndpointPreInstanceAR,
)
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryVO


class EndpointPreInstanceRepository(
    GenericSyntaxInstanceRepository[EndpointPreInstanceAR]
):
    root_class = EndpointPreInstanceRoot
    value_class = EndpointPreInstanceValue
    template_class = EndpointTemplateRoot

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        *,
        root: EndpointPreInstanceRoot,
        library: Library,
        relationship: VersionRelationship,
        value: EndpointPreInstanceValue,
        study_count: int = 0,
    ):
        return EndpointPreInstanceAR.from_repository_values(
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

    def _create(self, item: EndpointPreInstanceAR) -> EndpointPreInstanceAR:
        """
        This method calls the generic _create method, then extends it to add specific actions
        Specific actions are :
        * Attaching root node to indication nodes
        * Attaching root node to category nodes
        * Attaching root node to sub_category nodes
        """
        root, item = super()._create(item)

        for indication in item.indications or []:
            if indication:
                root.has_indication.connect(self._get_indication(indication.uid))
        for category in item.categories or []:
            if category and category[0]:
                root.has_category.connect(self._get_category(category[0].uid))
        for category in item.sub_categories or []:
            if category and category[0]:
                root.has_subcategory.connect(self._get_category(category[0].uid))

        return item
