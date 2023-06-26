from typing import Optional, Sequence, Tuple

from clinical_mdr_api.domain_repositories.concepts.concept_generic_repository import (
    ConceptGenericRepository,
)
from clinical_mdr_api.domain_repositories.models._utils import convert_to_datetime
from clinical_mdr_api.domain_repositories.models.activities import (
    ActivityGroupRoot,
    ActivityGroupValue,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)
from clinical_mdr_api.domains.concepts.activities.activity_group import (
    ActivityGroupAR,
    ActivityGroupVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
)
from clinical_mdr_api.models.concepts.activities.activity_group import ActivityGroup


class ActivityGroupRepository(ConceptGenericRepository[ActivityGroupAR]):
    root_class = ActivityGroupRoot
    value_class = ActivityGroupValue
    return_model = ActivityGroup

    def _create_aggregate_root_instance_from_cypher_result(
        self, input_dict: dict
    ) -> ActivityGroupAR:
        major, minor = input_dict.get("version").split(".")
        return ActivityGroupAR.from_repository_values(
            uid=input_dict.get("uid"),
            concept_vo=ActivityGroupVO.from_repository_values(
                name=input_dict.get("name"),
                name_sentence_case=input_dict.get("name_sentence_case"),
                definition=input_dict.get("definition"),
                abbreviation=input_dict.get("abbreviation"),
            ),
            library=LibraryVO.from_input_values_2(
                library_name=input_dict.get("library_name"),
                is_library_editable_callback=(
                    lambda _: input_dict.get("is_library_editable")
                ),
            ),
            item_metadata=LibraryItemMetadataVO.from_repository_values(
                change_description=input_dict.get("change_description"),
                status=LibraryItemStatus(input_dict.get("status")),
                author=input_dict.get("user_initials"),
                start_date=convert_to_datetime(value=input_dict.get("start_date")),
                end_date=None,
                major_version=int(major),
                minor_version=int(minor),
            ),
        )

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        root: VersionRoot,
        library: Optional[Library],
        relationship: VersionRelationship,
        value: VersionValue,
    ) -> ActivityGroupAR:
        return ActivityGroupAR.from_repository_values(
            uid=root.uid,
            concept_vo=ActivityGroupVO.from_repository_values(
                name=value.name,
                name_sentence_case=value.name_sentence_case,
                definition=value.definition,
                abbreviation=value.abbreviation,
            ),
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=(lambda _: library.is_editable),
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
        )

    def create_query_filter_statement(
        self, library: Optional[str] = None, **kwargs
    ) -> Tuple[str, dict]:
        (
            filter_statements_from_concept,
            filter_query_parameters,
        ) = super().create_query_filter_statement(library=library)
        filter_parameters = []
        if kwargs.get("activity_subgroup_names") is not None:
            activity_subgroup_names = kwargs.get("activity_subgroup_names")
            filter_by_activity_subgroup_names = """
            size([(concept_value)<-[:IN_GROUP]-(v:ActivitySubGroupValue) WHERE v.name IN $activity_subgroup_names | v.name]) > 0"""
            filter_parameters.append(filter_by_activity_subgroup_names)
            filter_query_parameters["activity_subgroup_names"] = activity_subgroup_names
        if kwargs.get("activity_names") is not None:
            activity_names = kwargs.get("activity_names")
            filter_by_activity_names = """
            size([(concept_value)<-[:IN_GROUP]-()<-[:IN_SUB_GROUP]-(v:ActivityValue) WHERE v.name IN $activity_names | v.name]) > 0"""
            filter_parameters.append(filter_by_activity_names)
            filter_query_parameters["activity_names"] = activity_names
        extended_filter_statements = " AND ".join(filter_parameters)
        if filter_statements_from_concept != "":
            if len(extended_filter_statements) > 0:
                filter_statements_to_return = " AND ".join(
                    [filter_statements_from_concept, extended_filter_statements]
                )
            else:
                filter_statements_to_return = filter_statements_from_concept
        else:
            filter_statements_to_return = (
                "WHERE " + extended_filter_statements
                if len(extended_filter_statements) > 0
                else ""
            )
        return filter_statements_to_return, filter_query_parameters

    def specific_alias_clause(self) -> str:
        # concept_value property comes from the main part of the query
        # which is specified in the activity_generic_repository_impl
        return """
        WITH *,
            head([(concept_value)<-[:IN_GROUP]-(activity_sub_group_value:ActivitySubGroupValue)<-[:HAS_VERSION]-
            (activity_sub_group_root:ActivitySubGroupRoot) | {uid:activity_sub_group_root.uid, name:activity_sub_group_value.name}]) AS activity_subgroup,
            head([(concept_value)<-[:IN_GROUP]-(activity_sub_group_value:ActivitySubGroupValue)<-[:IN_SUBGROUP]
            -(activity_value:ActivityValue)<-[:HAS_VERSION]-(activity_root:ActivityRoot) | {uid:activity_root.uid, name:activity_value.name}]) AS activity
        """

    def specific_header_match_clause(self) -> Optional[str]:
        return " MATCH (concept_value)<-[:IN_GROUP]-()<-[:IN_SUB_GROUP]-() "

    def _create_new_value_node(self, ar: ActivityGroupAR) -> ActivityGroupValue:
        value_node = super()._create_new_value_node(ar=ar)
        value_node.save()
        return value_node

    def get_syntax_activity_groups(
        self, root_class: type, syntax_uid: str
    ) -> Optional[Sequence[ActivityGroupAR]]:
        """
        This method returns the activity groups for the syntax with provided uid

        :param root_class: The class of the root node for the syntax
        :param syntax_uid: UID of the syntax
        :return Sequence[ActivityGroupAR]:
        """
        syntax = root_class.nodes.get(uid=syntax_uid)
        activity_group_nodes = syntax.has_activity_group.all()
        if activity_group_nodes:
            groups = []
            for node in activity_group_nodes:
                group = self.find_by_uid_2(uid=node.uid)
                groups.append(group)
            return groups
        return None
