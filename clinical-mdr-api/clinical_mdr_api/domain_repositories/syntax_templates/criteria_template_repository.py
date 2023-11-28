from neomodel import db

from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.models.syntax import (
    CriteriaTemplateRoot,
    CriteriaTemplateValue,
)
from clinical_mdr_api.domain_repositories.syntax_templates.generic_syntax_template_repository import (
    GenericSyntaxTemplateRepository,
)
from clinical_mdr_api.domains.syntax_templates.criteria_template import (
    CriteriaTemplateAR,
)
from clinical_mdr_api.domains.syntax_templates.template import InstantiationCountsVO
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryVO


class CriteriaTemplateRepository(GenericSyntaxTemplateRepository[CriteriaTemplateAR]):
    root_class = CriteriaTemplateRoot
    value_class = CriteriaTemplateValue

    def check_exists_by_name_in_study(self, name: str, study_uid: str) -> bool:
        query = """
            MATCH (study_root:StudyRoot{uid:$study_uid})-[:LATEST]->(:StudyValue)-[:HAS_STUDY_CRITERIA]->(:StudyCriteria)-
            [:HAS_SELECTED_CRITERIA]->(:CriteriaValue)<-[:LATEST]-(cr:CriteriaRoot)<-[:HAS_CRITERIA]-(:CriteriaTemplateRoot)-[:LATEST]->(ctv:CriteriaTemplateValue {name:$name})
            RETURN cr
            """
        result, _ = db.cypher_query(query, {"study_uid": study_uid, "name": name})

        return len(result) > 0 and len(result[0]) > 0

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        *,
        root: CriteriaTemplateRoot,
        library: Library,
        relationship: VersionRelationship,
        value: CriteriaTemplateValue,
        study_count: int = 0,
        counts: InstantiationCountsVO | None = None,
    ) -> CriteriaTemplateAR:
        return CriteriaTemplateAR.from_repository_values(
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

    def _create(self, item: CriteriaTemplateAR) -> CriteriaTemplateAR:
        """
        This method calls the generic _create method, then extends it to add specific actions
        Specific actions are :
        * Attaching root node to type node
        * Attaching root node to indication nodes
        * Attaching root node to category nodes
        * Attaching root node to sub_category nodes
        """
        root, item = super()._create(item)

        if item.type is not None and item.type[0] is not None:
            criteria_type = self._get_template_type(item.type[0].uid)
            root.has_type.connect(criteria_type)
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
