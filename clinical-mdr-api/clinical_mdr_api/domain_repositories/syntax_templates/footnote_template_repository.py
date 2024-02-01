from neomodel import db

from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.models.syntax import (
    FootnoteTemplateRoot,
    FootnoteTemplateValue,
)
from clinical_mdr_api.domain_repositories.syntax_templates.generic_syntax_template_repository import (
    GenericSyntaxTemplateRepository,
)
from clinical_mdr_api.domains.syntax_templates.footnote_template import (
    FootnoteTemplateAR,
)
from clinical_mdr_api.domains.syntax_templates.template import InstantiationCountsVO
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryVO


class FootnoteTemplateRepository(GenericSyntaxTemplateRepository[FootnoteTemplateAR]):
    root_class = FootnoteTemplateRoot
    value_class = FootnoteTemplateValue

    def check_exists_by_name_in_study(self, name: str, study_uid: str) -> bool:
        query = """
            MATCH (study_root:StudyRoot{uid:$study_uid})-[:LATEST]->(:StudyValue)-[:HAS_STUDY_FOOTNOTE]->(:StudyFootnote)-
            [:HAS_SELECTED_FOOTNOTE]->(:FootnoteValue)<-[:LATEST]-(cr:FootnoteRoot)<-[:HAS_FOOTNOTE]-(:FootnoteTemplateRoot)-[:LATEST]->(ctv:FootnoteTemplateValue {name:$name})
            RETURN cr
            """
        result, _ = db.cypher_query(query, {"study_uid": study_uid, "name": name})

        return len(result) > 0 and len(result[0]) > 0

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        root: FootnoteTemplateRoot,
        library: Library,
        relationship: VersionRelationship,
        value: FootnoteTemplateValue,
        study_count: int = 0,
        counts: InstantiationCountsVO | None = None,
    ) -> FootnoteTemplateAR:
        return FootnoteTemplateAR.from_repository_values(
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

    def _create(self, item: FootnoteTemplateAR) -> FootnoteTemplateAR:
        """
        This method calls the generic _create method, then extends it to add specific actions
        Specific actions are :
        * Attaching root node to type node
        * Attaching root node to indication nodes
        * Attaching root node to activity, activity group, activity sub group nodes
        """
        root, item = super()._create(item)

        if item.type and item.type[0]:
            footnote_type = self._get_template_type(item.type[0].uid)
            root.has_type.connect(footnote_type)

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
