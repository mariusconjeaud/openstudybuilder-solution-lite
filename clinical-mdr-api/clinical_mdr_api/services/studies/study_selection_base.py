"""Base classes/mixins related to study selection."""

from clinical_mdr_api import exceptions
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryItemStatus
from clinical_mdr_api.models.concepts.activities.activity import Activity
from clinical_mdr_api.models.concepts.compound import Compound
from clinical_mdr_api.models.concepts.compound_alias import CompoundAlias
from clinical_mdr_api.models.controlled_terminologies.ct_term import (
    CTTermName,
    SimpleTermModel,
)
from clinical_mdr_api.models.study_selections.study_selection import (
    StudySelectionBranchArmWithoutStudyArm,
)
from clinical_mdr_api.models.syntax_instances.criteria import Criteria
from clinical_mdr_api.models.syntax_instances.endpoint import Endpoint
from clinical_mdr_api.models.syntax_instances.objective import Objective
from clinical_mdr_api.models.syntax_instances.timeframe import Timeframe
from clinical_mdr_api.models.syntax_templates.criteria_template import CriteriaTemplate
from clinical_mdr_api.models.syntax_templates.endpoint_template import EndpointTemplate
from clinical_mdr_api.models.syntax_templates.objective_template import (
    ObjectiveTemplate,
)


class StudySelectionMixin:
    def _transform_latest_endpoint_model(self, endpoint_uid: str) -> Endpoint:
        endpoint_repo = self._repos.endpoint_repository
        endpoint = endpoint_repo.find_by_uid_2(
            uid=endpoint_uid, status=LibraryItemStatus.FINAL
        )
        if endpoint is None:
            endpoint = endpoint_repo.find_by_uid_2(
                uid=endpoint_uid, status=LibraryItemStatus.RETIRED
            )
        return Endpoint.from_endpoint_ar(endpoint)

    def _transform_endpoint_model(
        self, endpoint_uid: str, objective_version: str
    ) -> Endpoint:
        endpoint_repo = self._repos.endpoint_repository
        endpoint = endpoint_repo.find_by_uid_2(
            uid=endpoint_uid, version=objective_version
        )
        return Endpoint.from_endpoint_ar(endpoint)

    def _transform_latest_endpoint_template_model(
        self, endpoint_template_uid: str
    ) -> EndpointTemplate:
        endpoint_template_repo = self._repos.endpoint_template_repository
        endpoint_template = endpoint_template_repo.find_by_uid_2(
            uid=endpoint_template_uid, status=LibraryItemStatus.FINAL
        )
        if endpoint_template is None:
            endpoint_template = endpoint_template_repo.find_by_uid_2(
                uid=endpoint_template_uid, status=LibraryItemStatus.RETIRED
            )
        return EndpointTemplate.from_endpoint_template_ar(endpoint_template)

    def _transform_endpoint_template_model(
        self, endpoint_template_uid: str, endpoint_template_version: str
    ) -> EndpointTemplate:
        endpoint_template_repo = self._repos.endpoint_template_repository
        endpoint_template = endpoint_template_repo.find_by_uid_2(
            uid=endpoint_template_uid, version=endpoint_template_version
        )
        return EndpointTemplate.from_endpoint_template_ar(endpoint_template)

    def _transform_latest_objective_model(self, objective_uid: str) -> Objective:
        objective_repo = self._repos.objective_repository
        objective = objective_repo.find_by_uid_2(uid=objective_uid)
        return Objective.from_objective_ar(objective)

    def _transform_objective_model(
        self, objective_uid: str, objective_version: str
    ) -> Objective:
        objective_repo = self._repos.objective_repository
        objective = objective_repo.find_by_uid_2(
            uid=objective_uid, version=objective_version
        )
        return Objective.from_objective_ar(objective)

    def _transform_latest_objective_template_model(
        self, objective_template_uid: str
    ) -> ObjectiveTemplate:
        objective_template_repo = self._repos.objective_template_repository
        objective_template = objective_template_repo.find_by_uid_2(
            uid=objective_template_uid, status=LibraryItemStatus.FINAL
        )
        if objective_template is None:
            objective_template = objective_template_repo.find_by_uid_2(
                uid=objective_template_uid, status=LibraryItemStatus.RETIRED
            )
        return ObjectiveTemplate.from_objective_template_ar(objective_template)

    def _transform_objective_template_model(
        self, objective_template_uid: str, objective_template_version: str
    ) -> ObjectiveTemplate:
        objective_template_repo = self._repos.objective_template_repository
        objective_template = objective_template_repo.find_by_uid_2(
            uid=objective_template_uid, version=objective_template_version
        )
        return ObjectiveTemplate.from_objective_template_ar(objective_template)

    def _transform_latest_timeframe_model(self, timeframe_uid: str) -> Timeframe:
        timeframe_repo = self._repos.timeframe_repository
        timeframe = timeframe_repo.find_by_uid_2(
            uid=timeframe_uid, status=LibraryItemStatus.FINAL
        )
        if timeframe is None:
            timeframe = timeframe_repo.find_by_uid_2(
                uid=timeframe_uid, status=LibraryItemStatus.RETIRED
            )
        return Timeframe.from_timeframe_ar(timeframe)

    def _transform_timeframe_model(
        self, timeframe_uid: str, timeframe_version: str
    ) -> Timeframe:
        timeframe_repo = self._repos.timeframe_repository
        timeframe = timeframe_repo.find_by_uid_2(
            uid=timeframe_uid, version=timeframe_version
        )
        return Timeframe.from_timeframe_ar(timeframe)

    def _transform_latest_criteria_template_model(
        self, criteria_template_uid: str
    ) -> CriteriaTemplate:
        criteria_template_repo = self._repos.criteria_template_repository
        criteria_template = criteria_template_repo.find_by_uid_2(
            uid=criteria_template_uid, status=LibraryItemStatus.FINAL
        )
        if criteria_template is None:
            criteria_template = criteria_template_repo.find_by_uid_2(
                uid=criteria_template_uid, status=LibraryItemStatus.RETIRED
            )
        return CriteriaTemplate.from_criteria_template_ar(criteria_template)

    def _transform_criteria_template_model(
        self, criteria_template_uid: str, criteria_template_version: str
    ) -> CriteriaTemplate:
        criteria_template_repo = self._repos.criteria_template_repository
        criteria_template = criteria_template_repo.find_by_uid_2(
            uid=criteria_template_uid, version=criteria_template_version
        )
        return CriteriaTemplate.from_criteria_template_ar(criteria_template)

    def _transform_latest_criteria_model(self, criteria_uid: str) -> Criteria:
        criteria_repo = self._repos.criteria_repository
        criteria = criteria_repo.find_by_uid_2(
            uid=criteria_uid, status=LibraryItemStatus.FINAL
        )
        if criteria is None:
            criteria = criteria_repo.find_by_uid_2(
                uid=criteria_uid, status=LibraryItemStatus.RETIRED
            )
        return Criteria.from_criteria_ar(
            criteria,
        )

    def _transform_criteria_model(
        self, criteria_uid: str, criteria_version: str
    ) -> Criteria:
        criteria_repo = self._repos.criteria_repository
        criteria = criteria_repo.find_by_uid_2(
            uid=criteria_uid, version=criteria_version
        )
        return Criteria.from_criteria_ar(
            criteria,
        )

    def _transform_latest_activity_model(self, activity_uid: str) -> Activity:
        """Finds the activity with a given UID."""
        return Activity.from_activity_ar(
            activity_ar=self._repos.activity_repository.find_by_uid_2(activity_uid),
            find_activity_subgroup_by_uid=self._repos.activity_subgroup_repository.find_by_uid_2,
            find_activity_group_by_uid=self._repos.activity_group_repository.find_by_uid_2,
        )

    def _transform_activity_model(
        self, activity_uid: str, activity_version: str
    ) -> Activity:
        """Finds the activity with given UID and version."""
        return Activity.from_activity_ar(
            activity_ar=self._repos.activity_repository.find_by_uid_2(
                activity_uid, version=activity_version
            ),
            find_activity_subgroup_by_uid=self._repos.activity_subgroup_repository.find_by_uid_2,
            find_activity_group_by_uid=self._repos.activity_group_repository.find_by_uid_2,
        )

    def _transform_compound_model(self, compound_uid: str) -> Compound:
        """
        Finds the compound template parameter value with a given UID.
        """
        return Compound.from_compound_ar(
            compound_ar=self._repos.compound_repository.find_by_uid_2(compound_uid),
            find_term_by_uid=self._repos.ct_term_name_repository.find_by_uid,
            find_dictionary_term_by_uid=self._repos.dictionary_term_generic_repository.find_by_uid_2,
            find_substance_term_by_uid=self._repos.dictionary_term_substance_repository.find_by_uid_2,
            find_numeric_value_by_uid=self._repos.numeric_value_with_unit_repository.find_by_uid_2,
            find_lag_time_by_uid=self._repos.lag_time_repository.find_by_uid_2,
            find_unit_by_uid=self._repos.unit_definition_repository.find_by_uid_2,
            find_project_by_uid=self._repos.project_repository.find_by_uid,
            find_brand_by_uid=self._repos.brand_repository.find_by_uid,
            find_clinical_programme_by_uid=self._repos.clinical_programme_repository.find_by_uid,
        )

    def _transform_compound_alias_model(self, uid: str) -> CompoundAlias:
        return CompoundAlias.from_ar(
            ar=self._repos.compound_alias_repository.find_by_uid_2(uid),
            find_compound_by_uid=self._repos.compound_repository.find_by_uid_2,
        )

    def find_term_name_by_uid(self, uid):
        """Helper function to find CT term names."""
        return SimpleTermModel.from_ct_code(
            uid, self._repos.ct_term_name_repository.find_by_uid
        )

    def _find_by_uid_or_raise_not_found(
        self,
        term_uid: str,
        codelist_name: str | None = None,
        status: LibraryItemStatus | None = LibraryItemStatus.FINAL,
    ) -> CTTermName:
        if not codelist_name:
            item = self._repos.ct_term_name_repository.find_by_uid(
                term_uid=term_uid,
                at_specific_date=None,
                version=None,
                status=status,
                for_update=False,
            )
            if item is None:
                raise exceptions.NotFoundException(
                    f"Term with uid {term_uid} does not exist, in final status."
                )
            return CTTermName.from_ct_term_ar(item)

        # Specifying the codelist ensures that we get the properties
        # such as "order" from the correct codelist.
        filter_by = {"term_uid": {"v": [term_uid], "op": "eq"}}
        if status:
            filter_by["status"] = {"v": [status.value], "op": "eq"}
        items = self._repos.ct_term_name_repository.find_all(
            codelist_name=codelist_name,
            total_count=False,
            filter_by=filter_by,
            page_number=1,
            page_size=10,
        )

        if len(items.items) == 0:
            raise exceptions.NotFoundException(
                f"Term with uid {term_uid} does not exist in codelist {codelist_name}, in final status."
            )
        return CTTermName.from_ct_term_ar(items.items[0])

    def _find_branch_arms_connected_to_arm_uid(
        self,
        study_uid: str,
        study_arm_uid: str,
        user_initials: str,
        study_value_version: str | None = None,
    ) -> list[StudySelectionBranchArmWithoutStudyArm]:
        branch_arms_vo = (
            self._repos.study_branch_arm_repository.find_by_arm_nested_info(
                study_uid,
                study_arm_uid,
                user_initials,
                study_value_version=study_value_version,
            )
        )
        branch_arms_transformed = (
            [
                StudySelectionBranchArmWithoutStudyArm.from_study_selection_branch_arm_ar_and_order(
                    study_uid=study_uid, selection=i_vo[0], order=i_vo[1]
                )
                for i_vo in branch_arms_vo
            ]
            if branch_arms_vo is not None
            else None
        )

        return branch_arms_transformed

    def _get_specific_objective_selection_by_uids(
        self,
        study_uid: str,
        study_selection_uid: str,
        study_value_version: str | None = None,
        for_update: bool = False,
    ):
        repos = self._repos
        try:
            selection_aggregate = repos.study_objective_repository.find_by_study(
                study_uid,
                for_update=for_update,
                study_value_version=study_value_version,
            )
            assert selection_aggregate is not None
            selection, order = selection_aggregate.get_specific_objective_selection(
                study_selection_uid
            )
            return selection_aggregate, selection, order
        finally:
            repos.close()

    def _get_specific_endpoint_selection_by_uids(
        self,
        study_uid: str,
        study_selection_uid: str,
        study_value_version: str | None = None,
        for_update: bool = False,
    ):
        repos = self._repos
        try:
            selection_aggregate = repos.study_endpoint_repository.find_by_study(
                study_uid,
                for_update=for_update,
                study_value_version=study_value_version,
            )
            assert selection_aggregate is not None
            selection, order = selection_aggregate.get_specific_endpoint_selection(
                study_selection_uid
            )
            return selection_aggregate, selection, order
        finally:
            repos.close()

    def _get_specific_criteria_selection_by_uids(
        self,
        study_uid: str,
        study_selection_uid: str,
        study_value_version: str | None = None,
        for_update: bool = False,
    ):
        repos = self._repos
        try:
            selection_aggregate = repos.study_criteria_repository.find_by_study(
                study_uid,
                for_update=for_update,
                study_value_version=study_value_version,
            )
            assert selection_aggregate is not None
            selection, _ = selection_aggregate.get_specific_criteria_selection(
                study_selection_uid
            )
            if selection is None:
                raise exceptions.NotFoundException(
                    f"Could not find criteria with uid {study_selection_uid}"
                )
            return selection_aggregate, selection
        finally:
            repos.close()

    def _get_specific_activity_selection_by_uids(
        self,
        study_uid: str,
        study_selection_uid: str,
        study_value_version: str | None = None,
        for_update: bool = False,
    ):
        repos = self._repos
        try:
            selection_aggregate = repos.study_activity_repository.find_by_study(
                study_uid,
                for_update=for_update,
                study_value_version=study_value_version,
            )
            assert selection_aggregate is not None
            selection, order = selection_aggregate.get_specific_object_selection(
                study_selection_uid
            )
            if selection is None:
                raise exceptions.NotFoundException(
                    f"Could not find activity with uid {study_selection_uid}"
                )
            return selection_aggregate, selection, order
        finally:
            repos.close()

    def _get_specific_activity_subgroup_selection_by_uids(
        self, study_uid: str, study_selection_uid: str, for_update: bool = False
    ):
        repos = self._repos
        try:
            selection_aggregate = (
                repos.study_activity_subgroup_repository.find_by_study(
                    study_uid, for_update=for_update
                )
            )
            try:
                assert selection_aggregate is not None
                selection, order = selection_aggregate.get_specific_object_selection(
                    study_selection_uid
                )
                if selection is None:
                    raise exceptions.NotFoundException(
                        f"Could not find study activity subgroup with uid {study_selection_uid}"
                    )
                return selection_aggregate, selection, order
            except ValueError as value_error:
                raise exceptions.NotFoundException(value_error.args[0])
        finally:
            repos.close()

    def _get_specific_activity_group_selection_by_uids(
        self, study_uid: str, study_selection_uid: str, for_update: bool = False
    ):
        repos = self._repos
        try:
            selection_aggregate = repos.study_activity_group_repository.find_by_study(
                study_uid, for_update=for_update
            )
            try:
                assert selection_aggregate is not None
                selection, order = selection_aggregate.get_specific_object_selection(
                    study_selection_uid
                )
                if selection is None:
                    raise exceptions.NotFoundException(
                        f"Could not find study activity group with uid {study_selection_uid}"
                    )
                return selection_aggregate, selection, order
            except ValueError as value_error:
                raise exceptions.NotFoundException(value_error.args[0])
        finally:
            repos.close()

    def _get_specific_arm_selection_by_uids(
        self,
        study_uid: str,
        study_selection_uid: str,
        for_update: bool = False,
        study_value_version: str | None = None,
    ):
        repos = self._repos
        try:
            selection_aggregate = repos.study_arm_repository.find_by_study(
                study_uid,
                for_update=for_update,
                study_value_version=study_value_version,
            )
            assert selection_aggregate is not None
            selection, order = selection_aggregate.get_specific_arm_selection(
                study_selection_uid
            )
            return selection_aggregate, selection, order
        finally:
            repos.close()

    def _get_specific_element_selection_by_uids(
        self,
        study_uid: str,
        study_selection_uid: str,
        for_update: bool = False,
        study_value_version: str | None = None,
    ):
        repos = self._repos
        try:
            selection_aggregate = repos.study_element_repository.find_by_study(
                study_uid,
                for_update=for_update,
                study_value_version=study_value_version,
            )
            assert selection_aggregate is not None
            selection, order = selection_aggregate.get_specific_element_selection(
                study_selection_uid
            )
            return selection_aggregate, selection, order
        finally:
            repos.close()

    def _get_specific_branch_arm_selection_by_uids(
        self,
        study_uid: str,
        study_selection_uid: str,
        for_update: bool = False,
        study_value_version: str | None = None,
    ):
        repos = self._repos
        try:
            selection_aggregate = repos.study_branch_arm_repository.find_by_study(
                study_uid,
                for_update=for_update,
                study_value_version=study_value_version,
            )
            assert selection_aggregate is not None
            (
                selection,
                order,
            ) = selection_aggregate.get_specific_branch_arm_selection(
                study_selection_uid
            )
            return selection_aggregate, selection, order
        finally:
            repos.close()

    def _get_specific_cohort_selection_by_uids(
        self,
        study_uid: str,
        study_selection_uid: str,
        for_update: bool = False,
        study_value_version: str | None = None,
    ):
        repos = self._repos
        try:
            selection_aggregate = repos.study_cohort_repository.find_by_study(
                study_uid,
                for_update=for_update,
                study_value_version=study_value_version,
            )
            assert selection_aggregate is not None
            selection, order = selection_aggregate.get_specific_cohort_selection(
                study_selection_uid
            )
            return selection_aggregate, selection, order
        finally:
            repos.close()

    def _get_specific_soa_group_selection_by_uids(
        self, study_uid: str, study_selection_uid: str, for_update: bool = False
    ):
        repos = self._repos
        try:
            selection_aggregate = repos.study_soa_group_repository.find_by_study(
                study_uid, for_update=for_update
            )
            try:
                assert selection_aggregate is not None
                selection, order = selection_aggregate.get_specific_object_selection(
                    study_selection_uid
                )
                if selection is None:
                    raise exceptions.NotFoundException(
                        f"Could not find study soa group with uid {study_selection_uid}"
                    )
                return selection_aggregate, selection, order
            except ValueError as value_error:
                raise exceptions.NotFoundException(value_error.args[0])
        finally:
            repos.close()
