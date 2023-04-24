import datetime
from typing import List, Sequence

from fastapi import status
from neomodel import db

from clinical_mdr_api import exceptions, models
from clinical_mdr_api.domain.study_selection.study_activity_schedule import (
    StudyActivityScheduleVO,
)
from clinical_mdr_api.domain_repositories.models._utils import to_relation_trees
from clinical_mdr_api.domain_repositories.models.study_selections import (
    StudyActivitySchedule as StudyActivityScheduleNeoModel,
)
from clinical_mdr_api.domain_repositories.study_selection.study_activity_schedule_repository import (
    SelectionHistory,
)
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services.study_endpoint_selection import StudySelectionMixin


class StudyActivityScheduleService(StudySelectionMixin):
    _repos: MetaRepository

    def __init__(self, author: str):
        self._repos = MetaRepository()
        self.author = author

    @db.transaction
    def get_all_schedules(
        self, study_uid: str
    ) -> Sequence[models.StudyActivitySchedule]:
        return [
            models.StudyActivitySchedule.from_orm(sas_node)
            for sas_node in to_relation_trees(
                StudyActivityScheduleNeoModel.nodes.fetch_relations(
                    "has_after",
                    "study_visit__has_visit_name__has_latest_value",
                    "study_activity__has_selected_activity",
                ).filter(study_value__study_root__uid=study_uid)
            )
        ]

    def get_all_schedules_for_specific_visit(
        self, study_uid: str, study_visit_uid: str
    ) -> Sequence[models.StudyActivitySchedule]:
        return [
            models.StudyActivitySchedule.from_orm(sas_node)
            for sas_node in to_relation_trees(
                StudyActivityScheduleNeoModel.nodes.fetch_relations(
                    "has_after",
                    "study_visit__has_visit_name__has_latest_value",
                    "study_activity__has_selected_activity",
                ).filter(
                    study_value__study_root__uid=study_uid,
                    study_visit__uid=study_visit_uid,
                )
            )
        ]

    def get_all_schedules_for_specific_activity(
        self, study_uid: str, study_activity_uid: str
    ) -> Sequence[models.StudyActivitySchedule]:
        return [
            models.StudyActivitySchedule.from_orm(sas_node)
            for sas_node in to_relation_trees(
                StudyActivityScheduleNeoModel.nodes.fetch_relations(
                    "has_after",
                    "study_visit__has_visit_name__has_latest_value",
                    "study_activity__has_selected_activity",
                    "study_activity__has_study_activity",
                ).filter(
                    study_value__study_root__uid=study_uid,
                    study_activity__uid=study_activity_uid,
                )
            )
        ]

    @db.transaction
    def get_specific_schedule(
        self, study_uid: str, schedule_uid: str
    ) -> models.StudyActivitySchedule:
        sas_node = to_relation_trees(
            StudyActivityScheduleNeoModel.nodes.fetch_relations(
                "study_activity", "study_visit", "has_after"
            ).filter(study_value__study_root__uid=study_uid, uid=schedule_uid)
        )
        if sas_node is None or len(sas_node) == 0:
            raise exceptions.NotFoundException(
                f"Not Found - The study activity schedule with the specified 'uid' {schedule_uid} could not be found.",
            )
        return models.StudyDesignCell.from_orm(sas_node[0])

    def _from_input_values(
        self, study_uid: str, schedule_input: models.StudyActivityScheduleCreateInput
    ) -> StudyActivityScheduleVO:
        return StudyActivityScheduleVO(
            study_uid=study_uid,
            study_activity_uid=schedule_input.study_activity_uid,
            study_activity_name=None,
            study_visit_uid=schedule_input.study_visit_uid,
            study_visit_name=None,
            note=schedule_input.note,
            user_initials=self.author,
            start_date=datetime.datetime.now(datetime.timezone.utc),
        )

    @db.transaction
    def create(
        self, study_uid: str, schedule_input: models.StudyActivityScheduleCreateInput
    ) -> models.StudyActivitySchedule:
        schedule_vo = self._repos.study_activity_schedule_repository.save(
            self._from_input_values(study_uid, schedule_input), self.author
        )
        return models.StudyActivitySchedule.from_vo(schedule_vo)

    @db.transaction
    def delete(self, study_uid: str, schedule_uid: str):
        try:
            self._repos.study_activity_schedule_repository.delete(
                study_uid, schedule_uid, self.author
            )
        finally:
            self._repos.close()

    def _transform_history_to_response_model(
        self, study_selection_history: List[SelectionHistory], study_uid: str
    ) -> Sequence[models.StudyActivitySchedule]:
        result = []
        for history in study_selection_history:
            result.append(
                models.StudyActivityScheduleHistory(
                    study_uid=study_uid,
                    study_activity_schedule_uid=history.study_selection_uid,
                    study_activity_uid=history.study_activity_uid,
                    study_visit_uid=history.study_visit_uid,
                    note=history.note,
                    modified=history.start_date,
                )
            )
        return result

    @db.transaction
    def get_all_schedules_audit_trail(
        self, study_uid: str
    ) -> Sequence[models.StudyActivityScheduleHistory]:
        repos = self._repos
        try:
            try:
                selection_history = (
                    repos.study_activity_schedule_repository.find_selection_history(
                        study_uid
                    )
                )
            except ValueError as value_error:
                raise exceptions.NotFoundException(value_error.args[0])

            return self._transform_history_to_response_model(
                selection_history, study_uid
            )
        finally:
            repos.close()

    @db.transaction
    def get_specific_selection_audit_trail(
        self, study_uid: str, schedule_uid: str
    ) -> Sequence[models.StudyActivitySchedule]:
        repos = self._repos
        try:
            try:
                selection_history = (
                    repos.study_activity_schedule_repository.find_selection_history(
                        study_uid, schedule_uid
                    )
                )
            except ValueError as value_error:
                raise exceptions.NotFoundException(value_error.args[0])

            return self._transform_history_to_response_model(
                selection_history, study_uid
            )
        finally:
            repos.close()

    def handle_batch_operations(
        self,
        study_uid: str,
        operations: Sequence[models.StudyActivityScheduleBatchInput],
    ) -> Sequence[models.StudyActivityScheduleBatchOutput]:
        results = []
        for operation in operations:
            result = {}
            item = None
            try:
                if operation.method == "POST":
                    item = self.create(study_uid, operation.content)
                    response_code = status.HTTP_201_CREATED
                else:
                    self.delete(study_uid, operation.content.uid)
                    response_code = status.HTTP_204_NO_CONTENT
            except exceptions.MDRApiBaseException as error:
                result["response_code"] = error.status_code
                result["content"] = models.error.BatchErrorResponse(message=str(error))
            else:
                result["response_code"] = response_code
                if item:
                    result["content"] = item.dict()
            finally:
                results.append(models.StudyActivityScheduleBatchOutput(**result))
        return results
