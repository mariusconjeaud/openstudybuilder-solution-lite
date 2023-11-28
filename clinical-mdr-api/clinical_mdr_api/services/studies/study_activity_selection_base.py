import abc
from typing import Any, TypeVar

from neomodel import db

from clinical_mdr_api import exceptions
from clinical_mdr_api.domain_repositories.study_selections.study_activity_base_repository import (
    StudySelectionActivityBaseRepository,
)
from clinical_mdr_api.domains.study_selections.study_selection_activity import (
    StudySelectionActivityVO,
)
from clinical_mdr_api.domains.study_selections.study_selection_activity_group import (
    StudySelectionActivityGroupVO,
)
from clinical_mdr_api.domains.study_selections.study_selection_activity_subgroup import (
    StudySelectionActivitySubGroupVO,
)
from clinical_mdr_api.domains.study_selections.study_soa_group_selection import (
    StudySoAGroupVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryItemStatus
from clinical_mdr_api.models import (
    StudySelectionActivityCreateInput,
    StudySelectionActivityInput,
)
from clinical_mdr_api.models.utils import BaseModel, GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services._utils import (
    service_level_generic_filtering,
    service_level_generic_header_filtering,
)
from clinical_mdr_api.services.concepts.activities.activity_group_service import (
    ActivityGroupService,
)
from clinical_mdr_api.services.concepts.activities.activity_sub_group_service import (
    ActivitySubGroupService,
)
from clinical_mdr_api.services.studies.study_selection_base import StudySelectionMixin

_AggregateRootType = TypeVar("_AggregateRootType")
_VOType = TypeVar("_VOType")  # pylint: disable=invalid-name


class StudyActivitySelectionBaseService(StudySelectionMixin):
    _repos: MetaRepository
    repository_interface: type
    selected_object_repository_interface: type

    def __init__(self, author):
        self._repos = MetaRepository()
        self.author = author

    @property
    def repository(self) -> StudySelectionActivityBaseRepository[_AggregateRootType]:
        assert self._repos is not None
        return self.repository_interface()

    @property
    def selected_object_repository(self):
        assert self._repos is not None
        return self.selected_object_repository_interface()

    @abc.abstractmethod
    def _transform_all_to_response_model(
        self,
        study_selection: _AggregateRootType,
    ) -> list[BaseModel]:
        raise NotImplementedError

    @abc.abstractmethod
    def _transform_from_ar_and_order_to_response_model(
        self,
        study_selection_activity_ar: _AggregateRootType,
        activity_order: int,
        accepted_version: bool | None = None,
    ) -> BaseModel:
        raise NotImplementedError

    @abc.abstractmethod
    def _transform_history_to_response_model(
        self, study_selection_history: list[Any], study_uid: str
    ) -> list[BaseModel]:
        raise NotImplementedError

    @abc.abstractmethod
    def _create_value_object(
        self,
        study_uid: str,
        selection_create_input: StudySelectionActivityCreateInput,
        study_soa_group_selection_uid: str,
        study_activity_subgroup_selection_uid: str | None,
        study_activity_group_selection_uid: str | None,
    ):
        raise NotImplementedError

    def _create_activity_subgroup_selection_value_object(
        self,
        study_uid: str,
        selection_create_input: StudySelectionActivityCreateInput,
    ):
        activity_subgroup_service = ActivitySubGroupService()
        activity_subgroup_uid = selection_create_input.activity_subgroup_uid
        activity_subgroup_ar = activity_subgroup_service.repository.find_by_uid_2(
            activity_subgroup_uid, for_update=True
        )
        if not activity_subgroup_uid:
            raise exceptions.NotFoundException(
                f"There is no activity subgroup identified by provided uid ({activity_subgroup_uid})"
            )

        if activity_subgroup_ar.item_metadata.status in [
            LibraryItemStatus.DRAFT,
            LibraryItemStatus.RETIRED,
        ]:
            raise exceptions.BusinessLogicException(
                f"There is no approved activity subgroup identified by provided uid ({activity_subgroup_uid})"
            )

        # create new VO to add
        new_selection = StudySelectionActivitySubGroupVO.from_input_values(
            study_uid=study_uid,
            user_initials=self.author,
            activity_subgroup_uid=activity_subgroup_uid,
            activity_subgroup_version=activity_subgroup_ar.item_metadata.version,
            generate_uid_callback=self._repos.study_activity_subgroup_repository.generate_uid,
        )
        return new_selection

    def _create_activity_group_selection_value_object(
        self,
        study_uid: str,
        selection_create_input: StudySelectionActivityCreateInput,
    ):
        activity_group_service = ActivityGroupService()
        activity_group_uid = selection_create_input.activity_group_uid
        activity_group_ar = activity_group_service.repository.find_by_uid_2(
            activity_group_uid, for_update=True
        )
        if not activity_group_uid:
            raise exceptions.NotFoundException(
                f"There is no activity group identified by provided uid ({activity_group_uid})"
            )

        if activity_group_ar.item_metadata.status in [
            LibraryItemStatus.DRAFT,
            LibraryItemStatus.RETIRED,
        ]:
            raise exceptions.BusinessLogicException(
                f"There is no approved activity group identified by provided uid ({activity_group_uid})"
            )

        # create new VO to add
        new_selection = StudySelectionActivityGroupVO.from_input_values(
            study_uid=study_uid,
            user_initials=self.author,
            activity_group_uid=activity_group_uid,
            activity_group_version=activity_group_ar.item_metadata.version,
            generate_uid_callback=self._repos.study_activity_group_repository.generate_uid,
        )
        return new_selection

    def _patch_soa_group_selection_value_object(
        self,
        study_uid: str,
        current_study_activity: StudySelectionActivityVO,
        selection_create_input: StudySelectionActivityInput,
    ):
        selection_aggregate = self._repos.study_soa_group_repository.find_by_study(
            study_uid=study_uid, for_update=True
        )
        assert selection_aggregate is not None
        new_selection, _ = selection_aggregate.get_specific_object_selection(
            study_selection_uid=current_study_activity.study_soa_group_uid
        )
        is_soa_group_changed = (
            current_study_activity.soa_group_term_uid
            != selection_create_input.soa_group_term_uid
        )
        if is_soa_group_changed:
            soa_group_term_uid = selection_create_input.soa_group_term_uid
            ct_term_ar = self._repos.ct_term_name_repository.find_by_uid(
                soa_group_term_uid
            )
            if not ct_term_ar:
                raise exceptions.NotFoundException(
                    f"There is no SoAGroup CTTerm identified by provided uid ({soa_group_term_uid})"
                )

            if ct_term_ar.item_metadata.status in [
                LibraryItemStatus.DRAFT,
                LibraryItemStatus.RETIRED,
            ]:
                raise exceptions.BusinessLogicException(
                    f"There is no approved SoAGroup CTTerm identified by provided uid ({soa_group_term_uid})"
                )
            # create new VO to add
            new_selection = StudySoAGroupVO.from_input_values(
                study_uid=study_uid,
                user_initials=self.author,
                soa_group_term_uid=soa_group_term_uid,
                generate_uid_callback=lambda: current_study_activity.study_soa_group_uid,
            )
            # let the aggregate update the value object
            selection_aggregate.update_selection(
                updated_study_object_selection=new_selection,
                ct_term_level_exist_callback=self._repos.ct_term_name_repository.term_specific_exists_by_uid,
            )
            # sync with DB and save the update
            self._repos.study_soa_group_repository.save(
                selection_aggregate, self.author
            )

        return new_selection

    def _create_soa_group_selection_value_object(
        self,
        study_uid: str,
        selection_create_input: StudySelectionActivityCreateInput
        | StudySelectionActivityInput,
    ):
        soa_group_term_uid = selection_create_input.soa_group_term_uid
        ct_term_ar = self._repos.ct_term_name_repository.find_by_uid(soa_group_term_uid)
        if not ct_term_ar:
            raise exceptions.NotFoundException(
                f"There is no SoAGroup CTTerm identified by provided uid ({soa_group_term_uid})"
            )

        if ct_term_ar.item_metadata.status in [
            LibraryItemStatus.DRAFT,
            LibraryItemStatus.RETIRED,
        ]:
            raise exceptions.BusinessLogicException(
                f"There is no approved SoAGroup CTTerm identified by provided uid ({soa_group_term_uid})"
            )

        # create new VO to add
        new_selection = StudySoAGroupVO.from_input_values(
            study_uid=study_uid,
            user_initials=self.author,
            soa_group_term_uid=soa_group_term_uid,
            generate_uid_callback=self._repos.study_soa_group_repository.generate_uid,
        )
        return new_selection

    @abc.abstractmethod
    def _patch_prepare_new_study_activity(
        self,
        request_study_activity: BaseModel,
        current_study_activity: _VOType,
    ) -> _VOType:
        raise NotImplementedError

    def make_selection(
        self,
        study_uid: str,
        selection_create_input: StudySelectionActivityCreateInput,
    ) -> BaseModel:
        repos = self._repos
        try:
            with db.transaction:
                # StudySoAGroup selection
                study_soa_group_selection = (
                    self._create_soa_group_selection_value_object(
                        study_uid=study_uid,
                        selection_create_input=selection_create_input,
                    )
                )
                # add VO to aggregate
                study_soa_group_aggregate = (
                    self._repos.study_soa_group_repository.find_by_study(
                        study_uid=study_uid, for_update=True
                    )
                )
                assert study_soa_group_aggregate is not None
                study_soa_group_aggregate.add_object_selection(
                    study_soa_group_selection,
                )
                # sync with DB and save the update
                self._repos.study_soa_group_repository.save(
                    study_soa_group_aggregate, self.author
                )

                study_activity_subgroup_selection_uid: str | None = None
                # StudyActivitySubGroup selection
                if selection_create_input.activity_subgroup_uid:
                    # create new VO to add
                    study_activity_subgroup_selection = (
                        self._create_activity_subgroup_selection_value_object(
                            study_uid=study_uid,
                            selection_create_input=selection_create_input,
                        )
                    )
                    # add VO to aggregate
                    study_activity_subgroup_aggregate = (
                        self._repos.study_activity_subgroup_repository.find_by_study(
                            study_uid=study_uid, for_update=True
                        )
                    )
                    assert study_activity_subgroup_aggregate is not None
                    study_activity_subgroup_aggregate.add_object_selection(
                        study_activity_subgroup_selection,
                        self._repos.activity_subgroup_repository.check_exists_final_version,
                    )
                    # sync with DB and save the update
                    self._repos.study_activity_subgroup_repository.save(
                        study_activity_subgroup_aggregate, self.author
                    )
                    study_activity_subgroup_selection_uid = (
                        study_activity_subgroup_selection.study_selection_uid
                    )

                study_activity_group_selection_uid: str | None = None
                # StudyActivityGroup selection
                if (
                    selection_create_input.activity_subgroup_uid
                    and selection_create_input.activity_group_uid
                ):
                    # create new VO to add
                    study_activity_group_selection = (
                        self._create_activity_group_selection_value_object(
                            study_uid=study_uid,
                            selection_create_input=selection_create_input,
                        )
                    )
                    # add VO to aggregate
                    study_activity_group_aggregate = (
                        self._repos.study_activity_group_repository.find_by_study(
                            study_uid=study_uid, for_update=True
                        )
                    )
                    assert study_activity_group_aggregate is not None
                    study_activity_group_aggregate.add_object_selection(
                        study_activity_group_selection,
                        self._repos.activity_group_repository.check_exists_final_version,
                    )
                    # sync with DB and save the update
                    self._repos.study_activity_group_repository.save(
                        study_activity_group_aggregate, self.author
                    )
                    study_activity_group_selection_uid = (
                        study_activity_group_selection.study_selection_uid
                    )

                # StudyActivitySelection
                # create new VO to add
                study_activity_selection = self._create_value_object(
                    study_uid=study_uid,
                    selection_create_input=selection_create_input,
                    study_soa_group_selection_uid=study_soa_group_selection.study_selection_uid,
                    study_activity_subgroup_selection_uid=study_activity_subgroup_selection_uid,
                    study_activity_group_selection_uid=study_activity_group_selection_uid,
                )
                # add VO to aggregate
                study_activity_aggregate = self.repository.find_by_study(
                    study_uid=study_uid, for_update=True
                )
                assert study_activity_aggregate is not None
                study_activity_aggregate.add_object_selection(
                    study_activity_selection,
                    self.selected_object_repository.check_exists_final_version,
                    self._repos.ct_term_name_repository.term_specific_exists_by_uid,
                )
                study_activity_aggregate.validate()
                # sync with DB and save the update
                self.repository.save(study_activity_aggregate, self.author)

                study_activity_aggregate = self.repository.find_by_study(
                    study_uid=study_uid, for_update=True
                )
                # Fetch the new selection which was just added
                (
                    _,
                    order,
                ) = study_activity_aggregate.get_specific_object_selection(
                    study_activity_selection.study_selection_uid
                )

                # add the activity and return
                return self._transform_from_ar_and_order_to_response_model(
                    study_selection_activity_ar=study_activity_aggregate,
                    activity_order=order,
                )
        finally:
            repos.close()

    @db.transaction
    def get_all_selections_for_all_studies(
        self,
        project_name: str | None = None,
        project_number: str | None = None,
        sort_by: dict | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        total_count: bool = False,
        **kwargs,
    ) -> GenericFilteringReturn[BaseModel]:
        selection_ars = self.repository.find_all(
            project_name=project_name, project_number=project_number, **kwargs
        )

        # In order for filtering to work, we need to unwind the aggregated AR object first
        # Unwind ARs
        selections = []
        for selection_ar in selection_ars:
            parsed_selections = self._transform_all_to_response_model(selection_ar)
            for selection in parsed_selections:
                selections.append(selection)

        # Do filtering, sorting, pagination and count
        filtered_items = service_level_generic_filtering(
            items=selections,
            filter_by=filter_by,
            filter_operator=filter_operator,
            sort_by=sort_by,
            total_count=total_count,
            page_number=page_number,
            page_size=page_size,
        )
        return filtered_items

    def get_all_selection(
        self,
        study_uid: str,
        sort_by: dict | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        total_count: bool = False,
        study_value_version: str | None = None,
        **kwargs,
    ) -> GenericFilteringReturn[BaseModel]:
        repos = self._repos
        try:
            activity_selection_ar = self.repository.find_by_study(
                study_uid, study_value_version=study_value_version, **kwargs
            )
            assert activity_selection_ar is not None

            filtered_items = service_level_generic_filtering(
                items=self._transform_all_to_response_model(activity_selection_ar),
                filter_by=filter_by,
                filter_operator=filter_operator,
                sort_by=sort_by,
                total_count=total_count,
                page_number=page_number,
                page_size=page_size,
            )

            return filtered_items
        finally:
            repos.close()

    @db.transaction
    def get_all_selection_audit_trail(self, study_uid: str) -> list[BaseModel]:
        repos = self._repos
        try:
            try:
                selection_history = self.repository.find_selection_history(study_uid)
            except ValueError as value_error:
                raise exceptions.NotFoundException(value_error.args[0])

            return self._transform_history_to_response_model(
                selection_history, study_uid
            )
        finally:
            repos.close()

    @db.transaction
    def get_specific_selection_audit_trail(
        self, study_uid: str, study_selection_uid: str
    ) -> list[BaseModel]:
        repos = self._repos
        try:
            try:
                selection_history = self.repository.find_selection_history(
                    study_uid, study_selection_uid
                )
            except ValueError as value_error:
                raise exceptions.NotFoundException(value_error.args[0])

            return self._transform_history_to_response_model(
                selection_history, study_uid
            )
        finally:
            repos.close()

    @db.transaction
    def get_specific_selection(
        self,
        study_uid: str,
        study_selection_uid: str,
        study_value_version: str | None = None,
    ) -> BaseModel:
        (
            selection_aggregate,
            new_selection,
            order,
        ) = self._get_specific_activity_selection_by_uids(
            study_uid, study_selection_uid, study_value_version=study_value_version
        )
        return self._transform_from_ar_and_order_to_response_model(
            study_selection_activity_ar=selection_aggregate,
            activity_order=order,
            accepted_version=new_selection.accepted_version,
        )

    @db.transaction
    def patch_selection(
        self,
        study_uid: str,
        study_selection_uid: str,
        selection_update_input: BaseModel,
    ) -> BaseModel:
        repos = self._repos
        try:
            # Load aggregate
            selection_aggregate = self.repository.find_by_study(
                study_uid=study_uid, for_update=True
            )

            assert selection_aggregate is not None

            # Load the current VO for updates
            current_vo, order = selection_aggregate.get_specific_object_selection(
                study_selection_uid=study_selection_uid
            )

            # merge current with updates
            updated_selection = self._patch_prepare_new_study_activity(
                request_study_activity=selection_update_input,
                current_study_activity=current_vo,
            )

            # let the aggregate update the value object
            selection_aggregate.update_selection(
                updated_study_object_selection=updated_selection,
                object_exist_callback=self.selected_object_repository.final_or_replaced_retired_activity_exists,
                ct_term_level_exist_callback=self._repos.ct_term_name_repository.term_specific_exists_by_uid,
            )
            selection_aggregate.validate()

            # sync with DB and save the update
            self.repository.save(selection_aggregate, self.author)

            # Fetch the new selection which was just updated
            _, order = selection_aggregate.get_specific_object_selection(
                study_selection_uid
            )

            # add the activity and return
            return self._transform_from_ar_and_order_to_response_model(
                study_selection_activity_ar=selection_aggregate,
                activity_order=order,
            )
        finally:
            repos.close()

    def get_distinct_values_for_header(
        self,
        field_name: str,
        study_uid: str | None = None,
        search_string: str | None = "",
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        result_count: int = 10,
        study_value_version: str | None = None,
    ):
        all_items = self.get_all_selection(
            study_uid=study_uid, study_value_version=study_value_version
        )

        header_values = service_level_generic_header_filtering(
            items=all_items.items,
            field_name=field_name,
            search_string=search_string,
            filter_by=filter_by,
            filter_operator=filter_operator,
            result_count=result_count,
        )

        return header_values

    @db.transaction
    def set_new_order(
        self, study_uid: str, study_selection_uid: str, new_order: int
    ) -> BaseModel:
        repos = self._repos
        try:
            # Load aggregate
            selection_aggregate = self.repository.find_by_study(
                study_uid=study_uid, for_update=True
            )

            # remove the connection
            assert selection_aggregate is not None
            selection_aggregate.set_new_order_for_selection(
                study_selection_uid, new_order, self.author
            )

            # sync with DB and save the update
            self.repository.save(selection_aggregate, self.author)

            # Fetch the new selection which was just added
            _, order = selection_aggregate.get_specific_object_selection(
                study_selection_uid
            )

            # add the activity and return
            return self._transform_from_ar_and_order_to_response_model(
                study_selection_activity_ar=selection_aggregate,
                activity_order=order,
            )
        finally:
            repos.close()
