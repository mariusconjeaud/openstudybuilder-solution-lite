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
    ActivitySubGroupRoot,
    ActivitySubGroupValue,
)
from clinical_mdr_api.domain_repositories.models.study import StudyValue
from clinical_mdr_api.domain_repositories.models.study_audit_trail import StudyAction
from clinical_mdr_api.domain_repositories.models.study_selections import (
    StudyActivity,
    StudyActivitySubGroup,
    StudySelection,
)
from clinical_mdr_api.domain_repositories.study_selections.study_activity_base_repository import (
    StudySelectionActivityBaseRepository,
)
from clinical_mdr_api.domains.study_selections.study_selection_activity_subgroup import (
    StudySelectionActivitySubGroupAR,
    StudySelectionActivitySubGroupVO,
)


@dataclass
class SelectionHistory:
    """Class for selection history items"""

    study_selection_uid: str
    study_activity_selection_uid: str
    activity_subgroup_uid: str
    user_initials: str
    change_type: str
    start_date: datetime.datetime
    show_activity_subgroup_in_protocol_flowchart: bool | None
    activity_subgroup_order: int | None
    end_date: datetime.datetime | None
    activity_subgroup_version: str | None


class StudySelectionActivitySubGroupRepository(
    StudySelectionActivityBaseRepository[StudySelectionActivitySubGroupAR]
):
    _aggregate_root_type = StudySelectionActivitySubGroupAR

    def _create_value_object_from_repository(
        self, selection: dict, acv: bool
    ) -> StudySelectionActivitySubGroupVO:
        return StudySelectionActivitySubGroupVO.from_input_values(
            study_selection_uid=selection["study_selection_uid"],
            study_activity_selection_uid=selection["study_activity_selection_uid"],
            study_uid=selection["study_uid"],
            activity_subgroup_uid=selection["activity_subgroup_uid"],
            activity_subgroup_version=selection["activity_subgroup_version"],
            activity_subgroup_order=selection["activity_subgroup_order"],
            show_activity_subgroup_in_protocol_flowchart=selection[
                "show_activity_subgroup_in_protocol_flowchart"
            ],
            start_date=convert_to_datetime(value=selection["start_date"]),
            user_initials=selection["user_initials"],
            accepted_version=acv,
        )

    def _additional_match(self) -> str:
        return """
            WITH sr, sv
            MATCH (sv)-[:HAS_STUDY_ACTIVITY_SUBGROUP]->(sa:StudyActivitySubGroup)-[:HAS_SELECTED_ACTIVITY_SUBGROUP]->(av:ActivitySubGroupValue)<-[ver:HAS_VERSION]-(ar:ActivitySubGroupRoot)
            MATCH (sa)<-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_SUBGROUP]-(study_activity)
        """

    def _filter_clause(self, query_parameters: dict, **kwargs) -> str:
        return ""

    def _return_clause(self) -> str:
        return """RETURN DISTINCT
                study_activity.uid AS study_activity_selection_uid,
                sr.uid AS study_uid,
                sa.order AS activity_subgroup_order,
                sa.uid AS study_selection_uid,
                sa.show_activity_subgroup_in_protocol_flowchart AS show_activity_subgroup_in_protocol_flowchart,
                sa.accepted_version AS accepted_version,
                ar.uid AS activity_subgroup_uid,
                sac.date AS start_date,
                sac.user_initials AS user_initials,
                hv_ver.version AS activity_subgroup_version"""

    def get_selection_history(
        self, selection: dict, change_type: str, end_date: datetime
    ):
        return SelectionHistory(
            study_selection_uid=selection["study_selection_uid"],
            study_activity_selection_uid=selection["study_activity_selection_uid"],
            activity_subgroup_uid=selection["activity_subgroup_uid"],
            activity_subgroup_order=selection["activity_subgroup_order"],
            activity_subgroup_version=selection["activity_subgroup_version"],
            user_initials=selection["user_initials"],
            change_type=change_type,
            start_date=convert_to_datetime(value=selection["start_date"]),
            show_activity_subgroup_in_protocol_flowchart=selection[
                "show_activity_subgroup_in_protocol_flowchart"
            ],
            end_date=end_date,
        )

    def get_audit_trail_query(self, study_selection_uid: str):
        if study_selection_uid:
            audit_trail_cypher = """
            MATCH (sr:StudyRoot { uid: $study_uid})-[:AUDIT_TRAIL]->(:StudyAction)-[:BEFORE|AFTER]->(sa:StudyActivitySubGroup { uid: $study_selection_uid})
            <-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_SUBGROUP]-(study_activity:StudyActivity)
            WITH sa, study_activity
            MATCH (sa)-[:AFTER|BEFORE*0..]-(all_sa:StudyActivitySubGroup)
            WITH distinct(all_sa), study_activity
            """
        else:
            audit_trail_cypher = """
            MATCH (sr:StudyRoot { uid: $study_uid})-[:AUDIT_TRAIL]->(:StudyAction)-[:BEFORE|AFTER]->(all_sa:StudyActivitySubGroup)
            <-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_SUBGROUP]-(study_activity:StudyActivity)
            WITH DISTINCT all_sa, study_activity
            """
        audit_trail_cypher += """
                    MATCH (all_sa)-[:HAS_SELECTED_ACTIVITY_SUBGROUP]->(av:ActivitySubGroupValue)

                    CALL {
                      WITH av
                      MATCH (av) <-[ver]-(ar:ActivitySubGroupRoot)
                      WHERE ver.status = "Final"
                      RETURN ver as ver, ar as ar
                      ORDER BY ver.start_date DESC
                      LIMIT 1
                    }

                    WITH DISTINCT all_sa, ar, ver, study_activity
                    ORDER BY all_sa.order ASC
                    MATCH (all_sa)<-[:AFTER]-(asa:StudyAction)
                    OPTIONAL MATCH (all_sa)<-[:BEFORE]-(bsa:StudyAction)
                    WITH all_sa, ar, asa, bsa, ver, fgr, study_activity
                    ORDER BY all_sa.uid, asa.date DESC
                    RETURN
                        study_activity.uid AS study_activity_selection_uid,
                        all_sa.order AS activity_subgroup_order,
                        all_sa.uid AS study_selection_uid,
                        all_sa.show_activity_subgroup_in_protocol_flowchart AS show_activity_subgroup_in_protocol_flowchart,
                        ar.uid AS activity_subgroup_uid,
                        asa.date AS start_date,
                        asa.user_initials AS user_initials,
                        labels(asa) AS change_type,
                        bsa.date AS end_date,
                        ver.version AS activity_subgroup_version
                    """
        return audit_trail_cypher

    def get_study_selection_node_from_latest_study_value(
        self, study_value: StudyValue, study_selection: StudySelection
    ):
        return study_value.has_study_activity_subgroup.get(
            uid=study_selection.study_selection_uid
        )

    def _add_new_selection(
        self,
        latest_study_value_node: StudyValue,
        order: int,
        selection: StudySelectionActivitySubGroupVO,
        audit_node: StudyAction,
        last_study_selection_node: StudyActivitySubGroup,
        for_deletion: bool = False,
    ):
        # find the activity subgroup value
        activity_subgroup_root_node: ActivitySubGroupRoot = (
            ActivitySubGroupRoot.nodes.get(uid=selection.activity_subgroup_uid)
        )
        latest_activity_subgroup_value_node: ActivitySubGroupValue = (
            activity_subgroup_root_node.get_value_for_version(
                selection.activity_subgroup_version
            )
        )
        # Create new activity subgroup selection
        study_activity_subgroup_selection_node = StudyActivitySubGroup(
            order=order,
            show_activity_subgroup_in_protocol_flowchart=selection.show_activity_subgroup_in_protocol_flowchart,
        )
        study_activity_subgroup_selection_node.uid = selection.study_selection_uid
        study_activity_subgroup_selection_node.accepted_version = (
            selection.accepted_version
        )
        study_activity_subgroup_selection_node.save()
        if not for_deletion:
            # Connect new node with study value
            latest_study_value_node.has_study_activity_subgroup.connect(
                study_activity_subgroup_selection_node
            )
        # Connect new node with Study Activity
        study_activity_node = StudyActivity.nodes.has(has_before=False).get(
            uid=selection.study_activity_selection_uid
        )
        study_activity_subgroup_selection_node.study_activity_has_study_activity_subgroup.connect(
            study_activity_node
        )
        # Connect new node with audit trail
        audit_node.has_after.connect(study_activity_subgroup_selection_node)
        # Connect new node with Activity subgroup value
        study_activity_subgroup_selection_node.has_selected_activity_subgroup.connect(
            latest_activity_subgroup_value_node
        )

        if last_study_selection_node:
            manage_previous_connected_study_selection_relationships(
                previous_item=last_study_selection_node,
                study_value_node=latest_study_value_node,
                new_item=study_activity_subgroup_selection_node,
                exclude_study_selection_relationships=[StudyActivity],
            )

    def generate_uid(self) -> str:
        return StudyActivitySubGroup.get_next_free_uid_and_increment_counter()

    def close(self) -> None:
        pass

    def get_all_study_activity_subgroups_for_study_activity(
        self, study_uid: str, study_activity_uid
    ) -> list[StudyActivitySubGroup]:
        study_activity_subgroups = to_relation_trees(
            StudyActivitySubGroup.nodes.filter(
                has_study_activity_subgroup__study_root__uid=study_uid,
                study_activity_has_study_activity_subgroup__uid=study_activity_uid,
            ).has(has_before=False)
        ).distinct()
        return study_activity_subgroups
