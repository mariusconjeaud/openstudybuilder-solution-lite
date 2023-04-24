import datetime
from typing import Optional, Sequence

from aenum import extend_enum
from neomodel import db

from clinical_mdr_api import config as settings
from clinical_mdr_api import exceptions
from clinical_mdr_api.domain.study_definition_aggregate.study_metadata import (
    StudyStatus,
)
from clinical_mdr_api.domain.study_selection.study_disease_milestone import (
    StudyDiseaseMilestoneType,
    StudyDiseaseMilestoneVO,
)
from clinical_mdr_api.models.study_disease_milestone import (
    StudyDiseaseMilestone,
    StudyDiseaseMilestoneCreateInput,
    StudyDiseaseMilestoneEditInput,
    StudyDiseaseMilestoneVersion,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services._utils import (
    calculate_diffs,
    calculate_diffs_history,
    fill_missing_values_in_base_model_from_reference_base_model,
)


class StudyDiseaseMilestoneService:
    def __init__(self, author="NA"):
        self._repos = MetaRepository()
        self.repo = self._repos.study_disease_milestone_repository
        self.author = author
        self._create_ctlist_map()

    def _create_ctlist_map(self):
        self.study_disease_milestone_types = self.repo.create_ctlist_definition(
            settings.STUDY_DISEASE_MILESTONE_TYPE_NAME
        )
        for uid, name_definition in self.study_disease_milestone_types.items():
            if uid not in StudyDiseaseMilestoneType._member_map_:
                extend_enum(
                    StudyDiseaseMilestoneType,
                    uid,
                    name_definition["name"],
                    name_definition["definition"],
                )

    def _transform_all_to_response_model(
        self,
        disease_milestone: StudyDiseaseMilestoneVO,
    ) -> StudyDiseaseMilestone:
        return StudyDiseaseMilestone(
            uid=disease_milestone.uid,
            study_uid=disease_milestone.study_uid,
            order=disease_milestone.order,
            status=disease_milestone.status.value,
            start_date=disease_milestone.start_date.strftime(settings.DATE_TIME_FORMAT),
            user_initials=disease_milestone.author,
            disease_milestone_type=disease_milestone.disease_milestone_type,
            disease_milestone_type_named=disease_milestone.disease_milestone_type_named,
            disease_milestone_type_definition=disease_milestone.disease_milestone_type_definition,
            repetition_indicator=disease_milestone.repetition_indicator,
        )

    def _instantiate_disease_milestone_items(
        self,
        study_disease_milestone_create_input: StudyDiseaseMilestoneCreateInput,
    ):
        dm_type = StudyDiseaseMilestoneType[
            study_disease_milestone_create_input.disease_milestone_type
        ]
        return dm_type

    @db.transaction
    def get_all_disease_milestones(
        self,
        study_uid: str,
        sort_by: Optional[dict] = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: Optional[dict] = None,
        filter_operator: FilterOperator = FilterOperator.AND,
        total_count: bool = False,
        **kwargs,
    ) -> GenericFilteringReturn[StudyDiseaseMilestone]:
        try:
            items, total_count = self.repo.find_all_disease_milestone(
                study_uid=study_uid,
                sort_by=sort_by,
                page_number=page_number,
                page_size=page_size,
                filter_by=filter_by,
                filter_operator=filter_operator,
                total_count=total_count,
                **kwargs,
            )

            all_items = [
                self._transform_all_to_response_model(disease_milestone)
                for disease_milestone in items
            ]
        except ValueError as e:
            raise exceptions.ValidationException(e)

        study_disease_milestones = GenericFilteringReturn.create(all_items, total_count)
        return study_disease_milestones

    @db.transaction
    def find_by_uid(self, uid: str) -> StudyDiseaseMilestone:
        repos = self._repos
        try:
            study_disease_milestone = self.repo.find_by_uid(uid=uid)

            return self._transform_all_to_response_model(study_disease_milestone)
        except ValueError as e:
            raise exceptions.ValidationException(e.args[0])
        finally:
            repos.close()

    def _validate_creation(
        self,
        disease_milestone_input: StudyDiseaseMilestoneCreateInput,
        all_disease_milestones: Sequence[StudyDiseaseMilestoneVO],
    ):
        used_types = [
            disease_milestone.dm_type.name
            for disease_milestone in all_disease_milestones
        ]
        if disease_milestone_input.disease_milestone_type in used_types:
            raise ValueError(
                f'Value "{disease_milestone_input.disease_milestone_type}" in field Type is not unique for the study'
            )
        if disease_milestone_input.disease_milestone_type not in [
            i.name for i in StudyDiseaseMilestoneType
        ]:
            raise ValueError("Invalid value for study Disease Milestone type")

    def _validate_update(
        self,
        disease_milestone_input: StudyDiseaseMilestoneCreateInput,
        study_disease_milestone: StudyDiseaseMilestoneVO,
    ):
        if (
            disease_milestone_input.disease_milestone_type
            != study_disease_milestone.disease_milestone_type
        ):
            all_disease_milestones = self.repo.find_all_disease_milestones_by_study(
                study_uid=study_disease_milestone.study_uid
            )
            used_types = [
                disease_milestone.dm_type.name
                for disease_milestone in all_disease_milestones
            ]
            if disease_milestone_input.disease_milestone_type in used_types:
                raise ValueError(
                    "There can exist only one Study DiseaseMilestone for type."
                )

        if (
            disease_milestone_input.disease_milestone_type is not None
            and disease_milestone_input.disease_milestone_type
            not in [i.name for i in StudyDiseaseMilestoneType]
        ):
            raise ValueError("Invalid value for study disease_milestone type")

    def _from_input_values(
        self,
        study_uid: str,
        study_disease_milestone_create_input: StudyDiseaseMilestoneCreateInput,
    ):
        disease_milestone_type = self._instantiate_disease_milestone_items(
            study_disease_milestone_create_input=study_disease_milestone_create_input,
        ).name

        return StudyDiseaseMilestoneVO(
            study_uid=study_uid,
            order=study_disease_milestone_create_input.order,
            start_date=datetime.datetime.now(datetime.timezone.utc),
            status=StudyStatus.DRAFT,
            author=self.author,
            disease_milestone_type=disease_milestone_type,
            disease_milestone_type_named=self.study_disease_milestone_types[
                disease_milestone_type
            ]["name"],
            disease_milestone_type_definition=self.study_disease_milestone_types[
                disease_milestone_type
            ]["definition"],
            repetition_indicator=study_disease_milestone_create_input.repetition_indicator,
        )

    def _edit_study_disease_milestone_vo(
        self,
        study_disease_milestone_to_edit: StudyDiseaseMilestoneVO,
        study_disease_milestone_edit_input: StudyDiseaseMilestoneEditInput,
    ) -> StudyDiseaseMilestoneVO:
        dm_type: Optional[StudyDiseaseMilestoneType] = None
        if (
            study_disease_milestone_to_edit.disease_milestone_type
            != study_disease_milestone_edit_input.disease_milestone_type
        ):
            dm_type = StudyDiseaseMilestoneType[
                study_disease_milestone_edit_input.disease_milestone_type
            ]

        study_disease_milestone_to_edit.edit_core_properties(
            disease_milestone_type=dm_type.name
            if dm_type
            else study_disease_milestone_to_edit.disease_milestone_type,
            repetition_indicator=study_disease_milestone_edit_input.repetition_indicator,
        )

    @db.transaction
    def create(
        self,
        study_uid: str,
        study_disease_milestone_input: StudyDiseaseMilestoneCreateInput,
    ):
        all_disease_milestones = self.repo.find_all_disease_milestones_by_study(
            study_uid
        )
        self._validate_creation(study_disease_milestone_input, all_disease_milestones)
        created_study_disease_milestone = self._from_input_values(
            study_uid,
            study_disease_milestone_create_input=study_disease_milestone_input,
        )

        if study_disease_milestone_input.order:
            if len(all_disease_milestones) + 1 < created_study_disease_milestone.order:
                raise ValueError("Order is too big.")
            if created_study_disease_milestone.order < 1:
                raise ValueError("Order must be greater than 0.")

            for disease_milestone in all_disease_milestones[
                created_study_disease_milestone.order - 1 :
            ]:
                disease_milestone.order += 1
                self.repo.save(disease_milestone)
        else:
            created_study_disease_milestone.order = len(all_disease_milestones) + 1
        updated_item = self.repo.save(created_study_disease_milestone)
        return self._transform_all_to_response_model(updated_item)

    @db.transaction
    def edit(
        self,
        study_disease_milestone_uid: str,
        study_disease_milestone_input: StudyDiseaseMilestoneEditInput,
    ):
        study_disease_milestone = self.repo.find_by_uid(study_disease_milestone_uid)
        self._validate_update(study_disease_milestone_input, study_disease_milestone)
        fill_missing_values_in_base_model_from_reference_base_model(
            base_model_with_missing_values=study_disease_milestone_input,
            reference_base_model=self._transform_all_to_response_model(
                study_disease_milestone
            ),
        )
        self._edit_study_disease_milestone_vo(
            study_disease_milestone_to_edit=study_disease_milestone,
            study_disease_milestone_edit_input=study_disease_milestone_input,
        )

        updated_item = self.repo.save(study_disease_milestone)

        return self._transform_all_to_response_model(updated_item)

    @db.transaction
    def reorder(self, study_disease_milestone_uid: str, new_order: int):
        new_order -= 1
        disease_milestone = self.repo.find_by_uid(study_disease_milestone_uid)
        study_disease_milestones = self.repo.find_all_disease_milestones_by_study(
            disease_milestone.study_uid
        )
        old_order = 0
        for i, disease_milestone_checked in enumerate(study_disease_milestones):
            if disease_milestone_checked.uid == study_disease_milestone_uid:
                old_order = i
                disease_milestone = disease_milestone_checked

        if new_order < 0:
            raise ValueError("New order cannot be lesser than 1")
        if new_order > len(study_disease_milestones) - 1:
            raise ValueError(
                f"New order cannot be greater than {len(study_disease_milestones)}"
            )
        if new_order > old_order:
            start_order = old_order + 1
            end_order = new_order + 1
            order_modifier = 0
        else:
            start_order = new_order
            end_order = old_order
            order_modifier = 2
        for i in range(start_order, end_order):
            replaced_disease_milestone = study_disease_milestones[i]
            replaced_disease_milestone.set_order(i + order_modifier)
            self.repo.save(replaced_disease_milestone)
        disease_milestone.set_order(new_order + 1)
        self.repo.save(disease_milestone)
        study_disease_milestones = self.repo.find_all_disease_milestones_by_study(
            disease_milestone.study_uid
        )
        return self._transform_all_to_response_model(disease_milestone)

    @db.transaction
    def delete(self, study_disease_milestone_uid: str):
        study_disease_milestone = self.repo.find_by_uid(study_disease_milestone_uid)

        self.repo.save(study_disease_milestone, delete_flag=True)
        all_disease_milestones_in_study = (
            self.repo.find_all_disease_milestones_by_study(
                study_disease_milestone.study_uid
            )
        )
        for disease_milestone in all_disease_milestones_in_study[
            study_disease_milestone.order - 1 :
        ]:
            disease_milestone.order -= 1
            self.repo.save(disease_milestone)

    @db.transaction
    def audit_trail(
        self,
        disease_milestone_uid: str,
        study_uid: str,
    ) -> Sequence[StudyDiseaseMilestoneVersion]:
        all_versions = self.repo.get_all_versions(
            uid=disease_milestone_uid, study_uid=study_uid
        )
        versions = [
            self._transform_all_to_response_model(_).dict() for _ in all_versions
        ]
        data = calculate_diffs(versions, StudyDiseaseMilestoneVersion)
        return data

    @db.transaction
    def audit_trail_all_disease_milestones(
        self,
        study_uid: str,
    ) -> Sequence[StudyDiseaseMilestoneVersion]:
        data = calculate_diffs_history(
            get_all_object_versions=self.repo.get_all_disease_milestone_versions,
            transform_all_to_history_model=self._transform_all_to_response_model,
            study_uid=study_uid,
            version_object_class=StudyDiseaseMilestoneVersion,
        )
        return data

    def get_distinct_values_for_header(
        self,
        field_name: str,
        search_string: Optional[str] = "",
        filter_by: Optional[dict] = None,
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
        result_count: int = 10,
        **kwargs,
    ) -> Sequence:
        header_values = self.repo.get_distinct_headers(
            field_name=field_name,
            search_string=search_string,
            filter_by=filter_by,
            filter_operator=filter_operator,
            result_count=result_count,
            **kwargs,
        )
        return header_values
