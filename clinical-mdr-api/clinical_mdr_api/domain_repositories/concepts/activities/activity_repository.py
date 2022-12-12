from typing import Optional, Sequence, Tuple

from neomodel import Q

from clinical_mdr_api.domain.concepts.activities.activity import ActivityAR, ActivityVO
from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
)
from clinical_mdr_api.domain_repositories.concepts.concept_generic_repository import (
    ConceptGenericRepository,
)
from clinical_mdr_api.domain_repositories.models._utils import convert_to_datetime
from clinical_mdr_api.domain_repositories.models.activities import (
    ActivityRoot,
    ActivitySubGroupRoot,
    ActivityValue,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)
from clinical_mdr_api.models.activities.activity import Activity, ActivityORM
from clinical_mdr_api.repositories._utils import (
    FilterOperator,
    decrement_page_number,
    get_order_by_clause,
    transform_filters_into_neomodel,
)


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
                activity_subgroup=input_dict.get("activity_subgroup").get("uid"),
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
    ) -> ActivityAR:
        sub_group_value = value.in_subgroup.get_or_none()
        if sub_group_value is not None:
            sub_group = sub_group_value.has_latest_value.get_or_none().uid
        return ActivityAR.from_repository_values(
            uid=root.uid,
            concept_vo=ActivityVO.from_repository_values(
                name=value.name,
                name_sentence_case=value.name_sentence_case,
                definition=value.definition,
                abbreviation=value.abbreviation,
                activity_subgroup=sub_group,
            ),
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=(lambda _: library.is_editable),
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
        )

    def find_all_activities(
        self,
        library: Optional[str] = None,
        sort_by: Optional[dict] = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: Optional[dict] = None,
        # pylint:disable=unused-argument
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
        total_count: bool = False,
        **kwargs,
    ) -> Tuple[Sequence[ActivityORM], int]:
        (neomodel_filter, q_filters) = self.create_query_filter_statement_neomodel(
            library=library, filter_by=filter_by, **kwargs
        )
        sort_paths = get_order_by_clause(sort_by=sort_by, model=ActivityORM)
        page_number = decrement_page_number(page_number)
        nodes = (
            ActivityRoot.nodes.fetch_relations(
                "has_library",
                "has_latest_value__in_subgroup__has_latest_value",
                "has_latest_value__in_subgroup__in_group__has_latest_value",
            )
            .fetch_optional_relations_into_one_variable(
                {
                    "latest_draft": "latest_version",
                    "latest_final": "latest_version",
                    "latest_retired": "latest_version",
                }
            )
            .order_by(sort_paths[0] if len(sort_paths) > 0 else "uid")
            .filter(*q_filters, **neomodel_filter)
            .limit_results(page_size)
            .skip_results(page_number * page_size)
            .to_relation_trees()
        )
        all_activities = [
            ActivityORM.from_orm(activity_node) for activity_node in nodes
        ]
        if total_count:
            len_query = ActivityRoot.nodes.filter(*q_filters, **neomodel_filter)
            all_nodes = len(len_query)
        return all_activities, all_nodes if total_count else 0

    def create_query_filter_statement_neomodel(
        self, library: Optional[str] = None, filter_by: Optional[dict] = None, **kwargs
    ) -> Tuple[dict, Sequence[Q]]:
        neomodel_filter, q_filters = transform_filters_into_neomodel(
            filter_by=filter_by, model=ActivityORM
        )
        if library:
            neomodel_filter["has_library__name"] = library
        if kwargs.get("activity_subgroup_uid") is not None:
            neomodel_filter[
                "has_latest_value__in_subgroup__has_latest_value__uid"
            ] = kwargs.get("activity_subgroup_uid")
        if kwargs.get("activity_names") is not None:
            q_filters.append(Q(has_latest_value__name__in=kwargs.get("activity_names")))
        if kwargs.get("activity_subgroup_names") is not None:
            q_filters.append(
                Q(
                    has_latest_value__in_subgroup__name__in=kwargs.get(
                        "activity_subgroup_names"
                    )
                )
            )
        if kwargs.get("activity_group_names") is not None:
            q_filters.append(
                Q(
                    has_latest_value__in_subgroup__in_group__name__in=kwargs.get(
                        "activity_group_names"
                    )
                )
            )
        return neomodel_filter, q_filters

    def _create_new_value_node(self, ar: ActivityAR) -> ActivityValue:
        value_node = super()._create_new_value_node(ar=ar)
        value_node.save()
        sub_group_root = ActivitySubGroupRoot.nodes.get_or_none(
            uid=ar.concept_vo.activity_subgroup
        )
        sub_group_value = sub_group_root.has_latest_value.get_or_none()
        value_node.in_subgroup.connect(sub_group_value)
        return value_node

    def _has_data_changed(self, ar: ActivityAR, value: ActivityValue) -> bool:
        are_concept_properties_changed = super()._has_data_changed(ar=ar, value=value)
        are_rels_changed = False
        sub_group = value.in_subgroup.get_or_none()
        if sub_group is not None:
            sub_group_uid = sub_group.has_latest_value.get_or_none().uid
            are_rels_changed = ar.concept_vo.activity_subgroup != sub_group_uid
        return are_concept_properties_changed or are_rels_changed

    def get_template_activities(
        self, root_class: type, template_uid: str
    ) -> Optional[Sequence[ActivityAR]]:
        """
        This method returns the activities for the template with provided uid

        :param root_class: The class of the root node for the template
        :param template_uid: UID of the template
        :return Sequence[ActivityAR]:
        """
        template = root_class.nodes.get(uid=template_uid)
        activity_nodes = template.has_activity.all()
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
            head([(concept_value)-[:IN_SUB_GROUP]->(activity_sub_group_value:ActivitySubGroupValue)<-[:LATEST]-
            (activity_sub_group_root:ActivitySubGroupRoot) | {uid:activity_sub_group_root.uid, name:activity_sub_group_value.name}]) AS activity_subgroup,
            head([(concept_value)-[:IN_SUB_GROUP]->(:ActivitySubGroupValue)-[:IN_GROUP]->(activity_group_value:ActivityGroupValue)<-[:LATEST]-
            (activity_group_root:ActivityGroupRoot) | {uid:activity_group_root.uid, name:activity_group_value.name}]) AS activity_group
        """
