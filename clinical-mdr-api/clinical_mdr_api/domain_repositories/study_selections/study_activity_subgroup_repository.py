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
    activity_subgroup_uid: str
    user_initials: str
    change_type: str
    start_date: datetime.datetime
    end_date: datetime.datetime | None
    activity_subgroup_version: str | None


class StudySelectionActivitySubGroupRepository(
    StudySelectionActivityBaseRepository[StudySelectionActivitySubGroupAR]
):
    _aggregate_root_type = StudySelectionActivitySubGroupAR

    def is_repository_based_on_ordered_selection(self):
        return False

    def _create_value_object_from_repository(
        self, selection: dict, acv: bool
    ) -> StudySelectionActivitySubGroupVO:
        return StudySelectionActivitySubGroupVO.from_input_values(
            study_selection_uid=selection["study_selection_uid"],
            study_uid=selection["study_uid"],
            activity_subgroup_uid=selection["activity_subgroup_uid"],
            activity_subgroup_version=selection["activity_subgroup_version"],
            start_date=convert_to_datetime(value=selection["start_date"]),
            user_initials=selection["user_initials"],
            accepted_version=acv,
        )

    def _additional_match(self) -> str:
        return """
            WITH sr, sv
            MATCH (sv)-[:HAS_STUDY_ACTIVITY]->(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_SUBGROUP]->
                (sa:StudyActivitySubGroup)-[:HAS_SELECTED_ACTIVITY_SUBGROUP]->(av:ActivitySubGroupValue)<-[ver:HAS_VERSION]-(ar:ActivitySubGroupRoot)
        """

    def _filter_clause(self, query_parameters: dict, **kwargs) -> str:
        return ""

    def _order_by_query(self):
        return """
            WITH DISTINCT *
            ORDER BY study_activity.order ASC
            MATCH (sa)<-[:AFTER]-(sac:StudyAction)
        """

    def _return_clause(self) -> str:
        return """RETURN DISTINCT
                sr.uid AS study_uid,
                sa.uid AS study_selection_uid,
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
            activity_subgroup_uid=selection["activity_subgroup_uid"],
            activity_subgroup_version=selection["activity_subgroup_version"],
            user_initials=selection["user_initials"],
            change_type=change_type,
            start_date=convert_to_datetime(value=selection["start_date"]),
            end_date=end_date,
        )

    def get_audit_trail_query(self, study_selection_uid: str):
        if study_selection_uid:
            audit_trail_cypher = """
            MATCH (sr:StudyRoot { uid: $study_uid})-[:AUDIT_TRAIL]->(:StudyAction)-[:BEFORE|AFTER]->(sa:StudyActivitySubGroup {uid: $study_selection_uid})
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
                    ORDER BY study_activity.order ASC
                    MATCH (all_sa)<-[:AFTER]-(asa:StudyAction)
                    OPTIONAL MATCH (all_sa)<-[:BEFORE]-(bsa:StudyAction)
                    WITH all_sa, ar, asa, bsa, ver, fgr
                    ORDER BY all_sa.uid, asa.date DESC
                    RETURN
                        all_sa.uid AS study_selection_uid,
                        ar.uid AS activity_subgroup_uid,
                        asa.date AS start_date,
                        asa.user_initials AS user_initials,
                        labels(asa) AS change_type,
                        bsa.date AS end_date,
                        ver.version AS activity_subgroup_version
                    """
        return audit_trail_cypher

    def get_study_selection_node_from_latest_study_value(
        self, study_value: StudyValue, study_selection: StudyActivitySubGroup
    ):
        return StudyActivitySubGroup.nodes.has(has_before=False).get(
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
        study_activity_subgroup_selection_node = StudyActivitySubGroup()
        study_activity_subgroup_selection_node.uid = selection.study_selection_uid
        study_activity_subgroup_selection_node.accepted_version = (
            selection.accepted_version
        )
        study_activity_subgroup_selection_node.save()

        # Connect new node with audit trail
        audit_node.study_selection_metadata_has_after.connect(
            study_activity_subgroup_selection_node
        )
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
        # Our repository guidelines state that repos should have a close method
        # But nothing needs to be done in this one
        pass

    def get_all_study_activity_subgroups_for_study_activity(
        self, study_uid: str, study_activity_uid
    ) -> list[StudyActivitySubGroup]:
        study_activity_subgroups = to_relation_trees(
            StudyActivitySubGroup.nodes.filter(
                study_activity_has_study_activity_subgroup__has_study_activity__latest_value__uid=study_uid,
                study_activity_has_study_activity_subgroup__uid=study_activity_uid,
            ).has(has_before=False)
        ).distinct()
        return study_activity_subgroups
