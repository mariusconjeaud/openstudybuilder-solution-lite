from neomodel import db

from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.models.syntax import (
    ObjectiveTemplateRoot,
    ObjectiveTemplateValue,
)
from clinical_mdr_api.domain_repositories.syntax_templates.generic_syntax_template_repository import (
    GenericSyntaxTemplateRepository,
)
from clinical_mdr_api.domains.syntax_templates.objective_template import (
    ObjectiveTemplateAR,
)
from clinical_mdr_api.domains.syntax_templates.template import InstantiationCountsVO
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryVO


class ObjectiveTemplateRepository(GenericSyntaxTemplateRepository[ObjectiveTemplateAR]):
    root_class = ObjectiveTemplateRoot
    value_class = ObjectiveTemplateValue

    def check_exists_by_name_in_study(self, name: str, study_uid: str) -> bool:
        query = """
            MATCH (study_root:StudyRoot{uid:$study_uid})-[:LATEST]->(:StudyValue)-[:HAS_STUDY_OBJECTIVE]->(:StudyObjective)-
            [:HAS_SELECTED_OBJECTIVE]->(:ObjectiveValue)<-[:LATEST]-(or:ObjectiveRoot)<-[:HAS_OBJECTIVE]-(:ObjectiveTemplateRoot)-[:LATEST]->(otv:ObjectiveTemplateValue {name:$name})
            RETURN or
            """
        result, _ = db.cypher_query(query, {"study_uid": study_uid, "name": name})

        return len(result) > 0 and len(result[0]) > 0

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        *,
        root: ObjectiveTemplateRoot,
        library: Library,
        relationship: VersionRelationship,
        value: ObjectiveTemplateValue,
        study_count: int = 0,
        counts: InstantiationCountsVO = None,
    ) -> ObjectiveTemplateAR:
        return ObjectiveTemplateAR.from_repository_values(
            uid=root.uid,
            sequence_id=root.sequence_id,
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=(lambda _: library.is_editable),
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
            template=self._get_template(value),
            is_confirmatory_testing=root.is_confirmatory_testing,
            study_count=study_count,
            counts=counts,
        )

    def _create(self, item: ObjectiveTemplateAR) -> ObjectiveTemplateAR:
        """
        This method calls the generic _create method, then extends it to add specific actions
        Specific actions are :
        * Set is_confirmatory_testing property
        * Attaching root node to indication nodes
        * Attaching root node to category nodes
        """
        root, item = super()._create(item)

        root.is_confirmatory_testing = item.is_confirmatory_testing
        self._db_save_node(root)

        if item.indications:
            for indication in item.indications:
                if indication:
                    root.has_indication.connect(self._get_indication(indication.uid))
        if item.categories:
            for category in item.categories:
                if category and category[0]:
                    root.has_category.connect(self._get_category(category[0].uid))

        return item
