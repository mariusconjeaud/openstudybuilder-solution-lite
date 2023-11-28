import abc
import datetime
from typing import Generic, TypeVar

from neomodel import db

from clinical_mdr_api.domain_repositories._utils import helpers
from clinical_mdr_api.domain_repositories.models._utils import convert_to_datetime
from clinical_mdr_api.domain_repositories.models.study import StudyRoot, StudyValue
from clinical_mdr_api.domain_repositories.models.study_audit_trail import (
    Create,
    Delete,
    Edit,
    StudyAction,
)
from clinical_mdr_api.domain_repositories.models.study_selections import (
    StudySelection,
    StudySelectionMetadata,
)
from clinical_mdr_api.domains.study_selections.study_selection_base import (
    StudySelectionBaseAR,
    StudySelectionBaseVO,
)

_AggregateRootType = TypeVar("_AggregateRootType")


class StudySelectionActivityBaseRepository(Generic[_AggregateRootType], abc.ABC):
    _aggregate_root_type: StudySelectionBaseAR

    @staticmethod
    def _acquire_write_lock_study_value(uid: str) -> None:
        db.cypher_query(
            """
             MATCH (sr:StudyRoot {uid: $uid})
             REMOVE sr.__WRITE_LOCK__
             RETURN true
            """,
            {"uid": uid},
        )

    @abc.abstractmethod
    def _create_value_object_from_repository(self, selection: dict, acv: bool):
        raise NotImplementedError

    @abc.abstractmethod
    def _additional_match(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _filter_clause(
        self,
        query_parameters: dict,
        **kwargs,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def _return_clause(self):
        raise NotImplementedError

    @abc.abstractmethod
    def generate_uid(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def get_selection_history(
        self, selection: dict, change_type: str, end_date: datetime
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def get_audit_trail_query(self, study_selection_uid: str):
        raise NotImplementedError

    @abc.abstractmethod
    def get_study_selection_node_from_latest_study_value(
        self, study_value: StudyValue, study_selection: StudySelection
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def _add_new_selection(
        self,
        latest_study_value_node: StudyValue,
        order: int,
        selection: StudySelectionBaseVO,
        audit_node: StudyAction,
        last_study_selection_node: StudySelection,
        for_deletion: bool = False,
    ):
        raise NotImplementedError

    def _versioning_query(self):
        return """
        WITH DISTINCT *
            CALL {
                WITH ar, av
                MATCH (ar)-[hv:HAS_VERSION]-(av)
                WHERE hv.status in ['Final', 'Retired']
                WITH hv
                ORDER BY
                    toInteger(split(hv.version, '.')[0]) ASC,
                    toInteger(split(hv.version, '.')[1]) ASC,
                    hv.end_date ASC,
                    hv.start_date ASC
                WITH collect(hv) as hvs
                RETURN last(hvs) as hv_ver
            }
        """

    def _order_by_query(self):
        return """
            WITH DISTINCT *
            ORDER BY sa.order ASC
            MATCH (sa)<-[:AFTER]-(sac:StudyAction)
        """

    def _retrieves_all_data(
        self,
        study_uid: str | None = None,
        project_name: str | None = None,
        project_number: str | None = None,
        study_value_version: str | None = None,
        **kwargs,
    ) -> tuple[_AggregateRootType]:
        query = ""
        query_parameters = {}
        if study_uid:
            if study_value_version:
                query = "MATCH (sr:StudyRoot { uid: $uid})-[l:HAS_VERSION{status:'RELEASED', version:$study_value_version}]->(sv:StudyValue)"
                query_parameters["study_value_version"] = study_value_version
                query_parameters["uid"] = study_uid
            else:
                query = "MATCH (sr:StudyRoot { uid: $uid})-[l:LATEST]->(sv:StudyValue)"
                query_parameters["uid"] = study_uid
        else:
            if study_value_version:
                query = "MATCH (sr:StudyRoot)-[l:HAS_VERSION{status:'RELEASED', version:$study_value_version}]->(sv:StudyValue)"
                query_parameters["study_value_version"] = study_value_version
            else:
                query = "MATCH (sr:StudyRoot)-[l:LATEST]->(sv:StudyValue)"

        # Add project related filters if applicable
        if project_name is not None or project_number is not None:
            query += (
                "-[:HAS_PROJECT]->(:StudyProjectField)<-[:HAS_FIELD]-(proj:Project)"
            )
            filter_list = []
            if project_name is not None:
                filter_list.append("proj.name=$project_name")
                query_parameters["project_name"] = project_name
            if project_number is not None:
                filter_list.append("proj.project_number=$project_number")
                query_parameters["project_number"] = project_number
            query += " WHERE "
            query += " AND ".join(filter_list)

        # Then, match other things for instance Activity
        query += self._additional_match()

        # Filter on extra parameters, for instance ActivityGroupNames
        query += self._filter_clause(query_parameters=query_parameters, **kwargs)
        query += self._versioning_query()
        query += self._order_by_query()
        query += self._return_clause()
        all_activity_selections = db.cypher_query(query, query_parameters)
        all_selections = []
        for selection in helpers.db_result_to_list(all_activity_selections):
            acv = selection.get("accepted_version", False)
            if acv is None:
                acv = False
            selection_vo = self._create_value_object_from_repository(
                selection=selection, acv=acv
            )
            all_selections.append(selection_vo)
        return tuple(all_selections)

    def find_all(
        self,
        project_name: str | None = None,
        project_number: str | None = None,
        **kwargs,
    ) -> list[StudySelectionBaseAR]:
        """
        Finds all the selected study activities for all studies, and create the aggregate
        :return: List of StudySelectionActivityAR, potentially empty
        """
        all_selections = self._retrieves_all_data(
            project_name=project_name, project_number=project_number, **kwargs
        )
        # Create a dictionary, with study_uid as key, and list of selections as value
        selection_aggregate_dict = {}
        selection_aggregates = []
        for selection in all_selections:
            if selection.study_uid in selection_aggregate_dict:
                selection_aggregate_dict[selection.study_uid].append(selection)
            else:
                selection_aggregate_dict[selection.study_uid] = [selection]
        # Then, create the list of AR from the dictionary
        for study_uid, selections in selection_aggregate_dict.items():
            selection_aggregates.append(
                self._aggregate_root_type.from_repository_values(
                    study_uid=study_uid, study_objects_selection=selections
                )
            )
        return selection_aggregates

    def find_by_study(
        self,
        study_uid: str,
        for_update: bool = False,
        study_value_version: str | None = None,
        **kwargs,
    ) -> StudySelectionBaseAR | None:
        if for_update:
            self._acquire_write_lock_study_value(study_uid)
        all_selections = self._retrieves_all_data(
            study_uid,
            study_value_version=study_value_version,
            **kwargs,
        )
        selection_aggregate = self._aggregate_root_type.from_repository_values(
            study_uid=study_uid, study_objects_selection=all_selections
        )
        if for_update:
            selection_aggregate.repository_closure_data = all_selections
        return selection_aggregate

    def _get_audit_node(
        self, study_selection: _AggregateRootType, study_selection_uid: str
    ):
        all_current_ids = []
        for item in study_selection.study_objects_selection:
            all_current_ids.append(item.study_selection_uid)
        all_closure_ids = []
        for item in study_selection.repository_closure_data:
            all_closure_ids.append(item.study_selection_uid)
        # if uid is in current data
        if study_selection_uid in all_current_ids:
            # if uid is in closure data
            if study_selection_uid in all_closure_ids:
                return Edit()
            return Create()
        return Delete()

    def is_repository_based_on_ordered_selection(self):
        return True

    def save(self, study_selection: StudySelectionBaseAR, author: str) -> None:
        assert study_selection.repository_closure_data is not None
        # get the closure_data
        closure_data = study_selection.repository_closure_data
        closure_data_length = len(closure_data)

        # getting the latest study value node
        study_root_node: StudyRoot = StudyRoot.nodes.get(uid=study_selection.study_uid)
        latest_study_value_node: StudyValue = study_root_node.latest_value.get_or_none()

        # process new/changed/deleted elements for each activity
        selections_to_remove = []
        selections_to_add = []

        # check if object is removed from the selection list - delete has been called
        if closure_data_length > len(study_selection.study_objects_selection):
            # remove the last item from old list, as there will no longer be any study activity with that high order
            if self.is_repository_based_on_ordered_selection():
                selections_to_remove.append((len(closure_data), closure_data[-1]))

        # loop through new data - start=1 as order starts at 1 not at 0 and find what needs to be removed and added
        for order, selection in enumerate(
            study_selection.study_objects_selection, start=1
        ):
            # check whether something new is added
            if closure_data_length > order - 1:
                # check if anything has changed
                if selection is not closure_data[order - 1]:
                    # don't modify the item if the change is the order change,
                    # if the item is actually changed (the uid is the same) we should modify it
                    if (
                        self.is_repository_based_on_ordered_selection()
                        or selection.study_selection_uid
                        == closure_data[order - 1].study_selection_uid
                    ):
                        # update the selection by removing the old if the old exists, and adding new selection
                        selections_to_remove.append((order, closure_data[order - 1]))
                        selections_to_add.append((order, selection))
            else:
                # else something new have been added
                selections_to_add.append((order, selection))

        # audit trail nodes dictionary, holds the new nodes created for the audit trail
        audit_trail_nodes = {}

        # loop through and remove selections
        for order, study_activity in selections_to_remove:
            last_study_selection_node = (
                self.get_study_selection_node_from_latest_study_value(
                    study_value=latest_study_value_node, study_selection=study_activity
                )
            )

            audit_node = self._get_audit_node(
                study_selection, study_activity.study_selection_uid
            )
            audit_node = self._set_before_audit_info(
                last_study_selection_node, audit_node, study_root_node, author
            )
            audit_trail_nodes[study_activity.study_selection_uid] = (
                audit_node,
                last_study_selection_node,
            )
            if isinstance(audit_node, Delete):
                self._add_new_selection(
                    latest_study_value_node,
                    order,
                    study_activity,
                    audit_node,
                    last_study_selection_node,
                    True,
                )

        # loop through and add selections
        for order, selection in selections_to_add:
            last_study_selection_node = None
            if selection.study_selection_uid in audit_trail_nodes:
                audit_node, last_study_selection_node = audit_trail_nodes[
                    selection.study_selection_uid
                ]
            else:
                audit_node = Create()
                audit_node.user_initials = selection.user_initials
                audit_node.date = selection.start_date
                audit_node.save()
                study_root_node.audit_trail.connect(audit_node)
            self._add_new_selection(
                latest_study_value_node,
                order,
                selection,
                audit_node,
                last_study_selection_node,
                False,
            )

    @staticmethod
    def _set_before_audit_info(
        study_activity_selection_node: StudySelection,
        audit_node: StudyAction,
        study_root_node: StudyRoot,
        author: str,
    ) -> StudyAction:
        audit_node.user_initials = author
        audit_node.date = datetime.datetime.now(datetime.timezone.utc)
        audit_node.save()

        if isinstance(study_activity_selection_node, StudySelectionMetadata):
            audit_node.study_selection_metadata_has_before.connect(
                study_activity_selection_node
            )
        else:
            audit_node.has_before.connect(study_activity_selection_node)
        study_root_node.audit_trail.connect(audit_node)
        return audit_node

    def _get_selection_with_history(
        self, study_uid: str, study_selection_uid: str = None
    ):
        """
        returns the audit trail for study activity either for a specific selection or for all study activity for the study
        """

        audit_trail_query = self.get_audit_trail_query(
            study_selection_uid=study_selection_uid
        )
        specific_activity_selections_audit_trail = db.cypher_query(
            audit_trail_query,
            {"study_uid": study_uid, "study_selection_uid": study_selection_uid},
        )
        result = []
        for res in helpers.db_result_to_list(specific_activity_selections_audit_trail):
            for action in res["change_type"]:
                if "StudyAction" not in action:
                    change_type = action
            end_date = (
                convert_to_datetime(value=res["end_date"]) if res["end_date"] else None
            )
            result.append(
                self.get_selection_history(
                    selection=res, change_type=change_type, end_date=end_date
                )
            )
        return result

    def find_selection_history(
        self, study_uid: str, study_selection_uid: str | None = None
    ) -> list[dict | None]:
        if study_selection_uid:
            return self._get_selection_with_history(
                study_uid=study_uid, study_selection_uid=study_selection_uid
            )
        return self._get_selection_with_history(study_uid=study_uid)

    def close(self) -> None:
        pass
