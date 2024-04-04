import abc
from typing import Any, Callable, TypeVar

from neomodel import db

from clinical_mdr_api import exceptions
from clinical_mdr_api.domain_repositories.study_selections.study_activity_base_repository import (
    StudySelectionActivityBaseRepository,
)
from clinical_mdr_api.models.utils import BaseModel, GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services._utils import (
    service_level_generic_filtering,
    service_level_generic_header_filtering,
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
    def _get_selected_object_exist_check(
        self,
    ) -> Callable[[str], bool]:
        raise NotImplementedError

    @abc.abstractmethod
    def _transform_all_to_response_model(
        self,
        study_selection: _AggregateRootType,
        study_value_version: str | None = None,
    ) -> list[BaseModel]:
        raise NotImplementedError

    @abc.abstractmethod
    def _transform_from_ar_and_order_to_response_model(
        self,
        study_selection_ar: _AggregateRootType,
        order: int,
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
        selection_create_input: BaseModel,
        **kwargs,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def _patch_prepare_new_value_object(
        self,
        request_object: BaseModel,
        current_object: _VOType,
    ) -> _VOType:
        raise NotImplementedError

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
                items=self._transform_all_to_response_model(
                    activity_selection_ar, study_value_version=study_value_version
                ),
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
            study_selection_ar=selection_aggregate,
            order=order,
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
            updated_selection = self._patch_prepare_new_value_object(
                request_object=selection_update_input,
                current_object=current_vo,
            )

            # let the aggregate update the value object
            selection_aggregate.update_selection(
                updated_study_object_selection=updated_selection,
                object_exist_callback=self._get_selected_object_exist_check(),
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
                selection_aggregate,
                order,
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
                study_selection_ar=selection_aggregate,
                order=order,
            )
        finally:
            repos.close()
