from typing import Optional

from neomodel import db

from clinical_mdr_api import exceptions
from clinical_mdr_api.domain.syntax_templates.criteria_template import (
    CriteriaTemplateAR,
)
from clinical_mdr_api.domain.syntax_templates.template import InstantiationCountsVO
from clinical_mdr_api.domain.versioned_object_aggregate import LibraryVO
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
        study_count: Optional[int] = None,
        counts: InstantiationCountsVO = None,
    ) -> CriteriaTemplateAR:
        return CriteriaTemplateAR.from_repository_values(
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

    def _create(self, item: CriteriaTemplateAR) -> CriteriaTemplateAR:
        """
        This method calls the generic _create method, then extends it to add specific actions
        Specific actions are :
        * Attaching root node to type node
        * Attaching root node to indication nodes
        * Attaching root node to category nodes
        * Attaching root node to sub_category nodes
        """
        item = super()._create(item)
        root = self.root_class.nodes.get(uid=item.uid)

        if item.type is not None:
            criteria_type = self._get_criteria_type(item.type[0].uid)
            root.has_type.connect(criteria_type)
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

    def get_criteria_type_uid(self, template_uid: str) -> str:
        """
        :param: template_uid
        :return: uid of the criteria type or None if not found

        Returns the uid of the Criteria type node for the template identified by uid
        Returns a NotFoundError is a template with provided uid doesn't exist
        """
        root = CriteriaTemplateRoot.nodes.get_or_none(uid=template_uid)
        if root is None:
            raise exceptions.NotFoundException(
                f"Criteria template with uid {template_uid} does not exist"
            )

        ct_term = root.has_type.get()
        return ct_term.uid

    def check_exists_by_name_and_type_in_library(
        self, name: str, library: str, type_uid: str
    ) -> bool:
        query = f"""
            MATCH (:Library {{name: $library}})-[:{self.root_class.LIBRARY_REL_LABEL}]->(root:{self.root_class.__label__})-[:LATEST_FINAL|LATEST_DRAFT|LATEST_RETIRED|LATEST]->(:{self.value_class.__label__} {{name: $name}})
            WITH DISTINCT root
            MATCH (type {{uid: $typeUid}})<-[:HAS_TYPE]-(root)
            RETURN root
            """
        result, _ = db.cypher_query(
            query, {"name": name, "library": library, "typeUid": type_uid}
        )
        return len(result) > 0 and len(result[0]) > 0
