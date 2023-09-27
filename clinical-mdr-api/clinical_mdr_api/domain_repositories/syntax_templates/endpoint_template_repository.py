from neomodel import db

from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.models.syntax import (
    EndpointTemplateRoot,
    EndpointTemplateValue,
)
from clinical_mdr_api.domain_repositories.syntax_templates.generic_syntax_template_repository import (
    GenericSyntaxTemplateRepository,
)
from clinical_mdr_api.domains.syntax_templates.endpoint_template import (
    EndpointTemplateAR,
)
from clinical_mdr_api.domains.syntax_templates.template import InstantiationCountsVO
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryVO


class EndpointTemplateRepository(GenericSyntaxTemplateRepository[EndpointTemplateAR]):
    root_class = EndpointTemplateRoot
    value_class = EndpointTemplateValue

    def check_exists_by_name_in_study(self, name: str, study_uid: str) -> bool:
        query = """
            MATCH (study_root:StudyRoot{uid:$study_uid})-[:LATEST]->(:StudyValue)-[:HAS_STUDY_ENDPOINT]->(:StudyEndpoint)-
            [:HAS_SELECTED_ENDPOINT]->(:EndpointValue)<-[:LATEST]-(:EndpointRoot)<-[:HAS_ENDPOINT]-(er:EndpointTemplateRoot)-[:LATEST]->(etv:EndpointTemplateValue {name:$name})
            RETURN er
            """
        result, _ = db.cypher_query(query, {"study_uid": study_uid, "name": name})
        return len(result) > 0 and len(result[0]) > 0

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        *,
        root: EndpointTemplateRoot,
        library: Library,
        relationship: VersionRelationship,
        value: EndpointTemplateValue,
        study_count: int = 0,
        counts: InstantiationCountsVO = None,
    ) -> EndpointTemplateAR:
        return EndpointTemplateAR.from_repository_values(
            uid=root.uid,
            sequence_id=root.sequence_id,
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=(lambda _: library.is_editable),
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
            template=self._get_template(value),
            study_count=study_count,
            counts=counts,
        )

    def _create(self, item: EndpointTemplateAR) -> EndpointTemplateAR:
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
