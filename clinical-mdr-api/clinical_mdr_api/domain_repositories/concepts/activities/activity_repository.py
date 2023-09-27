from typing import Sequence

from neomodel import db

from clinical_mdr_api import exceptions
from clinical_mdr_api.domain_repositories.concepts.concept_generic_repository import (
    ConceptGenericRepository,
)
from clinical_mdr_api.domain_repositories.models._utils import (
    convert_to_datetime,
    to_relation_trees,
)
from clinical_mdr_api.domain_repositories.models.activities import (
    ActivityGrouping,
    ActivityRoot,
    ActivityValidGroup,
    ActivityValue,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)
from clinical_mdr_api.domains.concepts.activities.activity import (
    ActivityAR,
    ActivityGroupingVO,
    ActivityVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
)
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.concepts.activities.activity import Activity


class ActivityRepository(ConceptGenericRepository[ActivityAR]):
    root_class = ActivityRoot
    value_class = ActivityValue
    return_model = Activity

    def _create_aggregate_root_instance_from_cypher_result(
        self, input_dict: dict
    ) -> ActivityAR:
        major, minor = input_dict.get("version").split(".")
        return ActivityAR.from_repository_values(
            uid=input_dict.get("uid"),
            concept_vo=ActivityVO.from_repository_values(
                name=input_dict.get("name"),
                name_sentence_case=input_dict.get("name_sentence_case"),
                definition=input_dict.get("definition"),
                abbreviation=input_dict.get("abbreviation"),
                activity_groupings=[
                    ActivityGroupingVO(
                        activity_group_uid=activity_grouping.get("activity_group_uid"),
                        activity_subgroup_uid=activity_grouping.get(
                            "activity_subgroup_uid"
                        ),
                    )
                    for activity_grouping in input_dict.get("activity_groupings")
                ],
                request_rationale=input_dict.get("request_rationale"),
                replaced_by_activity=input_dict.get("replaced_by_activity"),
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
        library: Library | None,
        relationship: VersionRelationship,
        value: VersionValue,
    ) -> ActivityAR:
        replaced_activity = value.replaced_by_activity.get_or_none()
        activity_groupings_nodes = value.has_grouping.all()
        activity_groupings = []
        for activity_grouping in activity_groupings_nodes:
            activity_valid_groups = activity_grouping.in_subgroup.all()
            for activity_valid_group in activity_valid_groups:
                activity_groupings.append(
                    {
                        "activity_group_uid": activity_valid_group.in_group.get()
                        .has_version.single()
                        .uid,
                        "activity_subgroup_uid": activity_valid_group.has_group.get()
                        .has_version.single()
                        .uid,
                    }
                )
        return ActivityAR.from_repository_values(
            uid=root.uid,
            concept_vo=ActivityVO.from_repository_values(
                name=value.name,
                name_sentence_case=value.name_sentence_case,
                definition=value.definition,
                abbreviation=value.abbreviation,
                activity_groupings=[
                    ActivityGroupingVO(
                        activity_group_uid=activity_grouping.get("activity_group_uid"),
                        activity_subgroup_uid=activity_grouping.get(
                            "activity_subgroup_uid"
                        ),
                    )
                    for activity_grouping in activity_groupings
                ],
                request_rationale=value.request_rationale,
                replaced_by_activity=replaced_activity.uid
                if replaced_activity
                else None,
            ),
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=(lambda _: library.is_editable),
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
        )

    def create_query_filter_statement(
        self, library: str | None = None, **kwargs
    ) -> tuple[str, dict]:
        (
            filter_statements_from_concept,
            filter_query_parameters,
        ) = super().create_query_filter_statement(library=library)
        filter_parameters = []
        if (activity_subgroup_uid := kwargs.get("activity_subgroup_uid")) is not None:
            filter_by_activity_subgroup_uid = """
            $activity_subgroup_uid IN [(concept_value)-[:HAS_GROUPING]->(:ActivityGrouping)-[:IN_SUBGROUP]->
            (:ActivityValidGroup)<-[:HAS_GROUP]-(activity_subgroup_value:ActivitySubGroupValue)
            <-[:HAS_VERSION]-(activity_subgroup_root:ActivitySubGroupRoot) | activity_subgroup_root.uid]"""
            filter_parameters.append(filter_by_activity_subgroup_uid)
            filter_query_parameters["activity_subgroup_uid"] = activity_subgroup_uid
        if kwargs.get("activity_names") is not None:
            activity_names = kwargs.get("activity_names")
            filter_by_activity_names = "concept_value.name IN $activity_names"
            filter_parameters.append(filter_by_activity_names)
            filter_query_parameters["activity_names"] = activity_names
        if kwargs.get("activity_subgroup_names") is not None:
            activity_subgroup_names = kwargs.get("activity_subgroup_names")
            filter_by_activity_subgroup_names = """
            size([(concept_value)-[:HAS_GROUPING]->(:ActivityGrouping)-[:IN_SUBGROUP]->
            (:ActivityValidGroup)<-[:HAS_GROUP]-(asgv:ActivitySubGroupValue) WHERE asgv.name IN $activity_subgroup_names | asgv.name]) > 0"""
            filter_parameters.append(filter_by_activity_subgroup_names)
            filter_query_parameters["activity_subgroup_names"] = activity_subgroup_names
        if kwargs.get("activity_group_names") is not None:
            activity_group_names = kwargs.get("activity_group_names")
            filter_by_activity_group_names = """
            size([(concept_value)-[:HAS_GROUPING]->(:ActivityGrouping)-[:IN_SUBGROUP]->
            (:ActivityValidGroup)-[:IN_GROUP]->(agv:ActivityGroupValue) WHERE agv.name IN $activity_group_names | agv.name]) > 0"""
            filter_parameters.append(filter_by_activity_group_names)
            filter_query_parameters["activity_group_names"] = activity_group_names
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

    def _create_new_value_node(self, ar: ActivityAR) -> ActivityValue:
        value_node: ActivityValue = super()._create_new_value_node(ar=ar)
        value_node.request_rationale = ar.concept_vo.request_rationale
        value_node.save()
        for activity_grouping in ar.concept_vo.activity_groupings:
            # create ActivityGrouping node
            activity_grouping_node = ActivityGrouping(
                uid=ActivityGrouping.get_next_free_uid_and_increment_counter()
            )
            activity_grouping_node.save()

            # link ActivityValue and ActivityGrouping nodes
            value_node.has_grouping.connect(activity_grouping_node)

            # find related ActivityValidGroup node
            activity_valid_group_node = to_relation_trees(
                ActivityValidGroup.nodes.filter(
                    in_group__has_latest_value__uid=activity_grouping.activity_group_uid,
                    has_group__has_latest_value__uid=activity_grouping.activity_subgroup_uid,
                )
            ).distinct()
            if len(activity_valid_group_node) == 0:
                raise BusinessLogicException(
                    f"The ActivityValidGroup node wasn't found for subgroup ({activity_grouping.activity_subgroup_uid}) "
                    f"and group ({activity_grouping.activity_group_uid})"
                )
            activity_valid_group_node = activity_valid_group_node[0]

            # link ActivityGrouping and ActivityValidGroup
            activity_grouping_node.in_subgroup.connect(activity_valid_group_node)

        return value_node

    def _has_data_changed(self, ar: ActivityAR, value: ActivityValue) -> bool:
        are_concept_properties_changed = super()._has_data_changed(ar=ar, value=value)
        are_props_changed = ar.concept_vo.request_rationale != value.request_rationale

        activity_subgroup_uids = []
        activity_group_uids = []
        activity_grouping_nodes = value.has_grouping.all()
        for activity_grouping_node in activity_grouping_nodes:
            activity_valid_group_nodes = activity_grouping_node.in_subgroup.all()
            for activity_valid_group_node in activity_valid_group_nodes:
                activity_subgroup_uids.append(
                    activity_valid_group_node.has_group.get().has_version.single().uid
                )
                activity_group_uids.append(
                    activity_valid_group_node.in_group.get().has_version.single().uid
                )

        are_rels_changed = sorted(
            [
                activity_grouping.activity_group_uid
                for activity_grouping in ar.concept_vo.activity_groupings
            ]
        ) != sorted(activity_group_uids) or sorted(
            [
                activity_grouping.activity_subgroup_uid
                for activity_grouping in ar.concept_vo.activity_groupings
            ]
        ) != sorted(
            activity_subgroup_uids
        )
        return are_concept_properties_changed or are_rels_changed or are_props_changed

    def get_syntax_activities(
        self, root_class: type, syntax_uid: str
    ) -> Sequence[ActivityAR] | None:
        """
        This method returns the activities for the syntax with provided uid

        :param root_class: The class of the root node for the syntax
        :param syntax_uid: UID of the syntax
        :return Sequence[ActivityAR]:
        """
        syntax = root_class.nodes.get(uid=syntax_uid)
        activity_nodes = syntax.has_activity.all()
        if activity_nodes:
            activities = []
            for node in activity_nodes:
                activity = self.find_by_uid_2(uid=node.uid)
                activities.append(activity)
            return activities
        return None

    def specific_alias_clause(self) -> str:
        # concept_value property comes from the main part of the query
        # which is specified in the activity_generic_repository_impl
        return """
        WITH *,
            concept_value.request_rationale AS request_rationale,
            apoc.coll.toSet([(concept_value)-[:HAS_GROUPING]->(:ActivityGrouping)-[:IN_SUBGROUP]->(activity_valid_group:ActivityValidGroup)
            <-[:HAS_GROUP]-(activity_subgroup_value)<-[:HAS_VERSION]-(activity_subgroup_root:ActivitySubGroupRoot)
             | {
                 activity_subgroup_uid:activity_subgroup_root.uid, 
                 activity_group_uid: head([(activity_valid_group)-[:IN_GROUP]->(:ActivityGroupValue)
                 <-[:HAS_VERSION]-(activity_group_root:ActivityGroupRoot) | activity_group_root.uid])
             }]) AS activity_groupings,
            head([(concept_value)-[:REPLACED_BY_ACTIVITY]->(replacing_activity_root:ActivityRoot) | replacing_activity_root.uid]) AS replaced_by_activity
        """

    def replace_request_with_sponsor_activity(
        self, activity_request_uid: str, sponsor_activity_uid: str
    ) -> None:
        replace_activity_request_with_sponsor_activity_query = """
            MATCH (:ActivityRoot {uid: $activity_request_uid})-[:LATEST]->(activity_request_value:ActivityValue)
            MATCH (replacing_activity_root:ActivityRoot {uid: $sponsor_activity_uid})
            WITH activity_request_value, replacing_activity_root
            MERGE (activity_request_value)-[:REPLACED_BY_ACTIVITY]->(replacing_activity_root)
        """
        db.cypher_query(
            replace_activity_request_with_sponsor_activity_query,
            {
                "activity_request_uid": activity_request_uid,
                "sponsor_activity_uid": sponsor_activity_uid,
            },
        )

    def final_or_replaced_retired_activity_exists(self, uid: str) -> bool:
        query = f"""
            MATCH (concept_root:{self.root_class.__label__} {{uid: $uid}})-[:LATEST_FINAL]->(concept_value)
            RETURN concept_root
            """
        result, _ = db.cypher_query(query, {"uid": uid})
        exists = len(result) > 0 and len(result[0]) > 0
        if not exists:
            query = f"""
                MATCH (concept_root:{self.root_class.__label__} {{uid: $uid}})-[:LATEST_RETIRED]->(concept_value)
                -[:REPLACED_BY_ACTIVITY]->(:ActivityRoot)
                RETURN concept_root
                """
            result, _ = db.cypher_query(query, {"uid": uid})
            exists = len(result) > 0 and len(result[0]) > 0
        return exists

    def get_activity_overview(self, uid: str) -> dict:
        query = """
        MATCH (activity_root:ActivityRoot {uid:$uid})-[:LATEST]->(activity_value:ActivityValue)
        WITH DISTINCT activity_root,activity_value,
            head([(library)-[:CONTAINS_CONCEPT]->(activity_root) | library.name]) AS activity_library_name,
            apoc.coll.toSet([(activity_value)-[:HAS_GROUPING]->(:ActivityGrouping)<-[:HAS_ACTIVITY]-
            (activity_instance_value:ActivityInstanceValue)-[:ACTIVITY_INSTANCE_CLASS]->
            (activity_instance_class_root:ActivityInstanceClassRoot)-[:LATEST]->(activity_instance_class_value:ActivityInstanceClassValue)
            | {
                activity_instance_library_name: head([(library)-[:CONTAINS_CONCEPT]->
                (activity_instance_root:ActivityInstanceRoot)-[:HAS_VERSION]->(activity_instance_value) | library.name]),
                name:activity_instance_value.name,
                name_sentence_case:activity_instance_value.name_sentence_case,
                abbreviation:activity_instance_value.abbreviation,
                definition:activity_instance_value.definition,
                adam_param_code:activity_instance_value.adam_param_code,
                topic_code:activity_instance_value.topic_code,
                activity_instance_class: activity_instance_class_value
            }]) AS activity_instances,
            [(activity_value)-[:HAS_GROUPING]->(:ActivityGrouping)-[:IN_SUBGROUP]->(activity_valid_group:ActivityValidGroup)
            <-[:HAS_GROUP]-(activity_subgroup_value:ActivitySubGroupValue) | 
                {
                    activity_subgroup_value:activity_subgroup_value, 
                    activity_group_value:head([(activity_valid_group)-[:IN_GROUP]->(activity_group_value) | activity_group_value])
                }
            ] AS hierarchy
        WITH *,
            apoc.coll.sortMaps(activity_instances, '^name') as activity_instances
        RETURN
            hierarchy,
            activity_value,
            activity_library_name,
            activity_instances
        """
        result_array, attribute_names = db.cypher_query(
            query=query, params={"uid": uid}
        )
        if len(result_array) != 1:
            raise exceptions.BusinessLogicException(
                f"The overview query returned broken data: {result_array}"
            )
        overview = result_array[0]
        overview_dict = {}
        for overview_prop, attribute_name in zip(overview, attribute_names):
            overview_dict[attribute_name] = overview_prop
        return overview_dict
