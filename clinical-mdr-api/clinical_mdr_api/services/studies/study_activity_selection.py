from fastapi import status
from neomodel import db

from clinical_mdr_api import exceptions, models
from clinical_mdr_api.domain_repositories.concepts.activities.activity_repository import (
    ActivityRepository,
)
from clinical_mdr_api.domain_repositories.study_selections.study_activity_repository import (
    SelectionHistory,
    StudySelectionActivityRepository,
)
from clinical_mdr_api.domains.study_selections.study_selection_activity import (
    StudySelectionActivityAR,
    StudySelectionActivityVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryItemStatus
from clinical_mdr_api.models import StudySelectionActivityRequestUpdate
from clinical_mdr_api.models.error import BatchErrorResponse
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services._utils import (
    fill_missing_values_in_base_model_from_reference_base_model,
)
from clinical_mdr_api.services.concepts.activities.activity_service import (
    ActivityService,
)
from clinical_mdr_api.services.studies.study_activity_instruction import (
    StudyActivityInstructionService,
)
from clinical_mdr_api.services.studies.study_activity_schedule import (
    StudyActivityScheduleService,
)
from clinical_mdr_api.services.studies.study_activity_selection_base import (
    StudyActivitySelectionBaseService,
)


class StudyActivitySelectionService(StudyActivitySelectionBaseService):
    _repos: MetaRepository
    repository_interface = StudySelectionActivityRepository
    selected_object_repository_interface = ActivityRepository

    def _transform_from_ar_and_order_to_response_model(
        self,
        study_selection_activity_ar: StudySelectionActivityAR,
        activity_order: int,
        accepted_version: bool = False,
    ) -> models.StudySelectionActivity:
        return models.StudySelectionActivity.from_study_selection_activity_ar_and_order(
            study_selection_activity_ar=study_selection_activity_ar,
            activity_order=activity_order,
            accepted_version=accepted_version,
            get_activity_by_uid_callback=self._transform_latest_activity_model,
            get_activity_by_uid_version_callback=self._transform_activity_model,
            get_ct_term_flowchart_group=self._find_by_uid_or_raise_not_found,
        )

    def _create_value_object(
        self,
        study_uid: str,
        selection_create_input: models.StudySelectionActivityCreateInput,
        study_soa_group_selection_uid: str,
        study_activity_subgroup_selection_uid: str | None,
        study_activity_group_selection_uid: str | None,
    ):
        activity_service = ActivityService()
        activity_uid = selection_create_input.activity_uid
        activity_ar = activity_service.repository.find_by_uid_2(
            activity_uid, for_update=True
        )
        if not activity_ar:
            raise exceptions.NotFoundException(
                f"There is no activity identified by provided uid ({activity_uid})"
            )

        if activity_ar.item_metadata.status in [
            LibraryItemStatus.DRAFT,
            LibraryItemStatus.RETIRED,
        ]:
            raise exceptions.BusinessLogicException(
                f"There is no approved activity identified by provided uid ({activity_uid})"
            )
        if (
            selection_create_input.activity_subgroup_uid
            and selection_create_input.activity_subgroup_uid
            not in [
                grouping.activity_subgroup_uid
                for grouping in activity_ar.concept_vo.activity_groupings
            ]
        ):
            raise exceptions.BusinessLogicException(
                f"The specified subgroup ({selection_create_input.activity_subgroup_uid}) is not linked with ({activity_ar.name}) Activity"
            )
        if (
            selection_create_input.activity_group_uid
            and selection_create_input.activity_group_uid
            not in [
                grouping.activity_group_uid
                for grouping in activity_ar.concept_vo.activity_groupings
            ]
        ):
            raise exceptions.BusinessLogicException(
                f"The specified group ({selection_create_input.activity_group_uid}) is not linked with ({activity_ar.name}) Activity"
            )
        # create new VO to add
        new_selection = StudySelectionActivityVO.from_input_values(
            study_uid=study_uid,
            user_initials=self.author,
            activity_uid=activity_uid,
            activity_name=activity_ar.name,
            activity_version=activity_ar.item_metadata.version,
            soa_group_term_uid=selection_create_input.soa_group_term_uid,
            study_soa_group_uid=study_soa_group_selection_uid,
            study_activity_subgroup_uid=study_activity_subgroup_selection_uid,
            study_activity_group_uid=study_activity_group_selection_uid,
            activity_order=None,
            generate_uid_callback=self.repository.generate_uid,
            activity_subgroup_uid=selection_create_input.activity_subgroup_uid,
            activity_group_uid=selection_create_input.activity_group_uid,
        )
        return new_selection

    def _transform_all_to_response_model(
        self,
        study_selection: StudySelectionActivityAR,
    ) -> list[models.StudySelectionActivity]:
        result = []
        for order, selection in enumerate(
            study_selection.study_objects_selection, start=1
        ):
            result.append(
                self._transform_from_ar_and_order_to_response_model(
                    study_selection_activity_ar=study_selection,
                    activity_order=order,
                    accepted_version=selection.accepted_version,
                )
            )
        return result

    def _transform_history_to_response_model(
        self, study_selection_history: list[SelectionHistory], study_uid: str
    ) -> list[models.StudySelectionActivityCore]:
        result = []
        for history in study_selection_history:
            result.append(
                models.StudySelectionActivityCore.from_study_selection_history(
                    study_selection_history=history,
                    study_uid=study_uid,
                    get_activity_by_uid_version_callback=self._transform_activity_model,
                    get_ct_term_flowchart_group=self._find_by_uid_or_raise_not_found,
                )
            )
        return result

    @db.transaction
    def delete_selection(self, study_uid: str, study_selection_uid: str):
        repos = self._repos
        # StudyActivitySchedule and StudyActivityInstruction Services for cascade delete if any
        study_activity_schedules_service = StudyActivityScheduleService(
            author=self.author
        )
        study_activity_instructions_service = StudyActivityInstructionService(
            author=self.author
        )
        try:
            # Load aggregate
            selection_aggregate = repos.study_activity_repository.find_by_study(
                study_uid=study_uid, for_update=True
            )

            # Load aggregate
            study_activity_schedules = study_activity_schedules_service.get_all_schedules_for_specific_activity(
                study_uid=study_uid, study_activity_uid=study_selection_uid
            )
            for study_activity_schedule in study_activity_schedules:
                self._repos.study_activity_schedule_repository.delete(
                    study_uid,
                    study_activity_schedule.study_activity_schedule_uid,
                    self.author,
                )

            study_activity_instructions = study_activity_instructions_service.get_all_study_instructions_for_specific_study_activity(
                study_uid=study_uid, study_activity_uid=study_selection_uid
            )
            for study_activity_instruction in study_activity_instructions:
                self._repos.study_activity_instruction_repository.delete(
                    study_uid,
                    study_activity_instruction.study_activity_instruction_uid,
                    self.author,
                )

            study_activity_subgroups = repos.study_activity_subgroup_repository.get_all_study_activity_subgroups_for_study_activity(
                study_uid=study_uid, study_activity_uid=study_selection_uid
            )
            for study_activity_subgroup in study_activity_subgroups:
                # delete study activity subgroup
                (
                    study_activity_subgroup_ar,
                    _,
                    _,
                ) = self._get_specific_activity_subgroup_selection_by_uids(
                    study_uid=study_uid,
                    study_selection_uid=study_activity_subgroup.uid,
                    for_update=True,
                )
                study_activity_subgroup_ar.remove_object_selection(
                    study_activity_subgroup.uid
                )
                repos.study_activity_subgroup_repository.save(
                    study_activity_subgroup_ar, self.author
                )
            study_activity_groups = repos.study_activity_group_repository.get_all_study_activity_groups_for_study_activity(
                study_uid=study_uid, study_activity_uid=study_selection_uid
            )
            for study_activity_group in study_activity_groups:
                # delete study activity group
                (
                    study_activity_group_ar,
                    _,
                    _,
                ) = self._get_specific_activity_group_selection_by_uids(
                    study_uid=study_uid,
                    study_selection_uid=study_activity_group.uid,
                    for_update=True,
                )
                study_activity_group_ar.remove_object_selection(
                    study_activity_group.uid
                )
                repos.study_activity_group_repository.save(
                    study_activity_group_ar, self.author
                )

            study_soa_groups = repos.study_soa_group_repository.get_all_study_soa_groups_for_study_activity(
                study_uid=study_uid, study_activity_uid=study_selection_uid
            )
            for study_soa_group in study_soa_groups:
                # delete study soa group
                (
                    study_soa_group_ar,
                    _,
                    _,
                ) = self._get_specific_soa_group_selection_by_uids(
                    study_uid=study_uid,
                    study_selection_uid=study_soa_group.uid,
                    for_update=True,
                )
                study_soa_group_ar.remove_object_selection(study_soa_group.uid)
                repos.study_soa_group_repository.save(study_soa_group_ar, self.author)

            # remove the connection
            assert selection_aggregate is not None
            selection_aggregate.remove_object_selection(study_selection_uid)

            # sync with DB and save the update
            repos.study_activity_repository.save(selection_aggregate, self.author)
        finally:
            repos.close()

    def _patch_prepare_new_study_activity(
        self,
        request_study_activity: models.StudySelectionActivityInput
        | StudySelectionActivityRequestUpdate,
        current_study_activity: StudySelectionActivityVO,
    ) -> StudySelectionActivityVO:
        # transform current to input model
        transformed_current = models.StudySelectionActivityInput(
            show_activity_group_in_protocol_flowchart=current_study_activity.show_activity_group_in_protocol_flowchart,
            show_activity_subgroup_in_protocol_flowchart=current_study_activity.show_activity_subgroup_in_protocol_flowchart,
            show_activity_in_protocol_flowchart=current_study_activity.show_activity_in_protocol_flowchart,
            show_soa_group_in_protocol_flowchart=current_study_activity.show_soa_group_in_protocol_flowchart,
            soa_group_term_uid=current_study_activity.soa_group_term_uid,
        )

        # fill the missing from the inputs
        fill_missing_values_in_base_model_from_reference_base_model(
            base_model_with_missing_values=request_study_activity,
            reference_base_model=transformed_current,
        )
        # update StudySoAGroup selection
        updated_soa_selection = self._patch_soa_group_selection_value_object(
            study_uid=current_study_activity.study_uid,
            current_study_activity=current_study_activity,
            selection_create_input=request_study_activity,
        )

        return StudySelectionActivityVO.from_input_values(
            study_uid=current_study_activity.study_uid,
            activity_uid=request_study_activity.replaced_activity_uid
            if isinstance(
                request_study_activity, models.StudySelectionActivityRequestUpdate
            )
            else current_study_activity.activity_uid,
            activity_version=current_study_activity.activity_version,
            activity_order=current_study_activity.activity_order,
            activity_name=current_study_activity.activity_name,
            soa_group_term_uid=updated_soa_selection.soa_group_term_uid,
            study_soa_group_uid=updated_soa_selection.study_selection_uid,
            study_selection_uid=current_study_activity.study_selection_uid,
            study_activity_subgroup_uid=current_study_activity.study_activity_subgroup_uid,
            activity_subgroup_uid=current_study_activity.activity_subgroup_uid,
            study_activity_group_uid=current_study_activity.study_activity_group_uid,
            activity_group_uid=current_study_activity.activity_group_uid,
            show_activity_group_in_protocol_flowchart=request_study_activity.show_activity_group_in_protocol_flowchart,
            show_activity_subgroup_in_protocol_flowchart=request_study_activity.show_activity_subgroup_in_protocol_flowchart,
            show_activity_in_protocol_flowchart=request_study_activity.show_activity_in_protocol_flowchart,
            show_soa_group_in_protocol_flowchart=request_study_activity.show_soa_group_in_protocol_flowchart,
            user_initials=self.author,
        )

    def handle_batch_operations(
        self,
        study_uid: str,
        operations: list[models.StudySelectionActivityBatchInput],
    ) -> list[models.StudySelectionActivityBatchOutput]:
        results = []
        for operation in operations:
            result = {}
            item = None
            try:
                if operation.method == "PATCH":
                    item = self.patch_selection(
                        study_uid,
                        operation.content.study_activity_uid,
                        operation.content.content,
                    )
                    response_code = status.HTTP_200_OK
                elif operation.method == "DELETE":
                    self.delete_selection(
                        study_uid, operation.content.study_activity_uid
                    )
                    response_code = status.HTTP_204_NO_CONTENT
                else:
                    item = self.make_selection(study_uid, operation.content)
                    response_code = status.HTTP_201_CREATED
            except exceptions.MDRApiBaseException as error:
                result["response_code"] = error.status_code
                result["content"] = BatchErrorResponse(message=str(error))
            else:
                result["response_code"] = response_code
                result["content"] = item
            finally:
                results.append(models.StudySelectionActivityBatchOutput(**result))
        return results

    def update_activity_request_with_sponsor_activity(
        self,
        study_uid: str,
        study_selection_uid: str,
    ) -> models.StudySelectionActivity:
        repos = self._repos
        # Load aggregate
        selection_aggregate = repos.study_activity_repository.find_by_study(
            study_uid=study_uid, for_update=True
        )

        assert selection_aggregate is not None
        # Load the current VO for updates
        current_vo, _ = selection_aggregate.get_specific_object_selection(
            study_selection_uid=study_selection_uid
        )
        activity_ar = self._repos.activity_repository.find_by_uid_2(
            current_vo.activity_uid
        )
        return self.patch_selection(
            study_uid=study_uid,
            study_selection_uid=study_selection_uid,
            selection_update_input=StudySelectionActivityRequestUpdate(
                replaced_activity_uid=activity_ar.concept_vo.replaced_by_activity
            ),
        )
