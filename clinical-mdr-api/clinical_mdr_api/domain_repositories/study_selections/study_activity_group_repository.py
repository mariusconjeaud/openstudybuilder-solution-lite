import datetime
from dataclasses import dataclass

from clinical_mdr_api.domain_repositories.generic_repository import (
    manage_previous_connected_study_selection_relationships,
)
from clinical_mdr_api.domain_repositories.models._utils import (
    convert_to_datetime,
    to_relation_trees,
)
from clinical_mdr_api.domain_repositories.models.activities import (
    ActivityGroupRoot,
    ActivityGroupValue,
)
from clinical_mdr_api.domain_repositories.models.study import StudyValue
from clinical_mdr_api.domain_repositories.models.study_audit_trail import StudyAction
from clinical_mdr_api.domain_repositories.models.study_selections import (
    StudyActivityGroup,
    StudyActivitySubGroup,
    StudySelection,
)
from clinical_mdr_api.domain_repositories.study_selections.study_activity_base_repository import (
    StudySelectionActivityBaseRepository,
)
from clinical_mdr_api.domains.study_selections.study_selection_activity_group import (
    StudySelectionActivityGroupAR,
    StudySelectionActivityGroupVO,
)


@dataclass
class SelectionHistory:
    """Class for selection history items"""

    study_selection_uid: str
    study_activity_subgroup_selection_uid: str
    activity_group_uid: str
    user_initials: str
    change_type: str
    start_date: datetime.datetime
    show_activity_group_in_protocol_flowchart: bool | None
    activity_group_order: int | None
    end_date: datetime.datetime | None
    activity_group_version: str | None


class StudySelectionActivityGroupRepository(
    StudySelectionActivityBaseRepository[StudySelectionActivityGroupAR]
):
    _aggregate_root_type = StudySelectionActivityGroupAR

    def _create_value_object_from_repository(
        self, selection: dict, acv: bool
    ) -> StudySelectionActivityGroupVO:
        return StudySelectionActivityGroupVO.from_input_values(
            study_selection_uid=selection["study_selection_uid"],
            study_activity_subgroup_selection_uid=selection[
                "study_activity_subgroup_selection_uid"
            ],
            study_uid=selection["study_uid"],
            activity_group_uid=selection["activity_group_uid"],
            activity_group_version=selection["activity_group_version"],
            activity_group_order=selection["activity_group_order"],
            show_activity_group_in_protocol_flowchart=selection[
                "show_activity_group_in_protocol_flowchart"
            ],
            start_date=convert_to_datetime(value=selection["start_date"]),
            user_initials=selection["user_initials"],
            accepted_version=acv,
        )

    def _additional_match(self) -> str:
        return """
            WITH sr, sv
            MATCH (sv)-[:HAS_STUDY_ACTIVITY_GROUP]->(sa:StudyActivityGroup)-[:HAS_SELECTED_ACTIVITY_GROUP]->(av:ActivityGroupValue)<-[ver:HAS_VERSION]-(ar:ActivityGroupRoot)
            MATCH (sa)<-[:STUDY_ACTIVITY_SUBGROUP_HAS_STUDY_ACTIVITY_GROUP]-(study_activity_subgroup)
        """

    def _filter_clause(self, query_parameters: dict, **kwargs) -> str:
        return ""

    def _return_clause(self) -> str:
        return """RETURN DISTINCT
                study_activity_subgroup.uid AS study_activity_subgroup_selection_uid,
                sr.uid AS study_uid,
                sa.order AS activity_group_order,
                sa.uid AS study_selection_uid,
                sa.show_activity_group_in_protocol_flowchart AS show_activity_group_in_protocol_flowchart,
                sa.accepted_version AS accepted_version,
                ar.uid AS activity_group_uid,
                sac.date AS start_date,
                sac.user_initials AS user_initials,
                hv_ver.version AS activity_group_version"""

    def get_selection_history(
        self, selection: dict, change_type: str, end_date: datetime
    ):
        return SelectionHistory(
            study_selection_uid=selection["study_selection_uid"],
            study_activity_subgroup_selection_uid=selection[
                "study_activity_subgroup_selection_uid"
            ],
            activity_group_uid=selection["activity_group_uid"],
            activity_group_order=selection["activity_group_order"],
            activity_group_version=selection["activity_group_version"],
            user_initials=selection["user_initials"],
            change_type=change_type,
            start_date=convert_to_datetime(value=selection["start_date"]),
            show_activity_group_in_protocol_flowchart=selection[
                "show_activity_group_in_protocol_flowchart"
            ],
            end_date=end_date,
        )

    def get_audit_trail_query(self, study_selection_uid: str):
        if study_selection_uid:
            audit_trail_cypher = """
            MATCH (sr:StudyRoot { uid: $study_uid})-[:AUDIT_TRAIL]->(:StudyAction)-[:BEFORE|AFTER]->(sa:StudyActivityGroup { uid: $study_selection_uid})
            <-[:STUDY_ACTIVITY_SUBGROUP_HAS_STUDY_ACTIVITY_GROUP]-(study_activity_subgroup:StudyActivitySubgroup)
            WITH sa, study_activity_subgroup
            MATCH (sa)-[:AFTER|BEFORE*0..]-(all_sa:StudyActivityGroup)
            WITH distinct(all_sa), study_activity_subgroup
            """
        else:
            audit_trail_cypher = """
            MATCH (sr:StudyRoot { uid: $study_uid})-[:AUDIT_TRAIL]->(:StudyAction)-[:BEFORE|AFTER]->(all_sa:StudyActivityGroup)
            <-[:STUDY_ACTIVITY_SUBGROUP_HAS_STUDY_ACTIVITY_GROUP]-(study_activity_subgroup:StudyActivitySubgroup)
            WITH DISTINCT all_sa, study_activity_subgroup
            """
        audit_trail_cypher += """
                    MATCH (all_sa)-[:HAS_SELECTED_ACTIVITY_GROUP]->(av:ActivityGroupValue)

                    CALL {
                      WITH av
                      MATCH (av) <-[ver]-(ar:ActivityGroupRoot)
                      WHERE ver.status = "Final"
                      RETURN ver as ver, ar as ar
                      ORDER BY ver.start_date DESC
                      LIMIT 1
                    }

                    WITH DISTINCT all_sa, ar, ver, study_activity_subgroup
                    ORDER BY all_sa.order ASC
                    MATCH (all_sa)<-[:AFTER]-(asa:StudyAction)
                    OPTIONAL MATCH (all_sa)<-[:BEFORE]-(bsa:StudyAction)
                    WITH all_sa, ar, asa, bsa, ver, fgr, study_activity_subgroup
                    ORDER BY all_sa.uid, asa.date DESC
                    RETURN
                        study_activity_subgroup.uid AS study_activity_subgroup_selection_uid,
                        all_sa.order AS activity_group_order,
                        all_sa.uid AS study_selection_uid,
                        all_sa.show_activity_group_in_protocol_flowchart AS show_activity_group_in_protocol_flowchart,
                        ar.uid AS activity_group_uid,
                        asa.date AS start_date,
                        asa.user_initials AS user_initials,
                        labels(asa) AS change_type,
                        bsa.date AS end_date,
                        ver.version AS activity_group_version
                    """
        return audit_trail_cypher

    def get_study_selection_node_from_latest_study_value(
        self, study_value: StudyValue, study_selection: StudySelection
    ):
        return study_value.has_study_activity_group.get(
            uid=study_selection.study_selection_uid
        )

    def _add_new_selection(
        self,
        latest_study_value_node: StudyValue,
        order: int,
        selection: StudySelectionActivityGroupVO,
        audit_node: StudyAction,
        last_study_selection_node: StudyActivityGroup,
        for_deletion: bool = False,
    ):
        # find the activity group value
        activity_group_root_node: ActivityGroupRoot = ActivityGroupRoot.nodes.get(
            uid=selection.activity_group_uid
        )
        latest_activity_group_value_node: ActivityGroupValue = (
            activity_group_root_node.get_value_for_version(
                selection.activity_group_version
            )
        )
        # Create new activity group selection
        study_activity_group_selection_node = StudyActivityGroup(
            order=order,
            show_activity_group_in_protocol_flowchart=selection.show_activity_group_in_protocol_flowchart,
        )
        study_activity_group_selection_node.uid = selection.study_selection_uid
        study_activity_group_selection_node.accepted_version = (
            selection.accepted_version
        )
        study_activity_group_selection_node.save()
        if not for_deletion:
            # Connect new node with study value
            latest_study_value_node.has_study_activity_group.connect(
                study_activity_group_selection_node
            )
        # Connect new node with Study Activity SubGroup
        study_activity_subgroup_node = StudyActivitySubGroup.nodes.has(
            has_before=False
        ).get(uid=selection.study_activity_subgroup_selection_uid)
        study_activity_group_selection_node.study_activity_subgroup_has_study_activity_group.connect(
            study_activity_subgroup_node
        )
        # Connect new node with audit trail
        audit_node.has_after.connect(study_activity_group_selection_node)
        # Connect new node with Activity subgroup value
        study_activity_group_selection_node.has_selected_activity_group.connect(
            latest_activity_group_value_node
        )

        if last_study_selection_node:
            manage_previous_connected_study_selection_relationships(
                previous_item=last_study_selection_node,
                study_value_node=latest_study_value_node,
                new_item=study_activity_group_selection_node,
                exclude_study_selection_relationships=[StudyActivitySubGroup],
            )

    def generate_uid(self) -> str:
        return StudyActivityGroup.get_next_free_uid_and_increment_counter()

    def close(self) -> None:
        pass

    def get_all_study_activity_groups_for_study_activity_subgroup(
        self, study_uid: str, study_activity_subgroup_uid
    ) -> list[StudyActivityGroup]:
        study_activity_groups = to_relation_trees(
            StudyActivityGroup.nodes.filter(
                has_study_activity_group__study_root__uid=study_uid,
                study_activity_subgroup_has_study_activity_group__uid=study_activity_subgroup_uid,
            ).has(has_before=False)
        ).distinct()
        return study_activity_groups
