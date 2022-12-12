from typing import Optional

from neomodel import db

from clinical_mdr_api import exceptions
from clinical_mdr_api.domain.concepts.activities.activity import ActivityAR, ActivityVO
from clinical_mdr_api.domain_repositories.concepts.activities.activity_repository import (
    ActivityRepository,
)
from clinical_mdr_api.models.activities.activity import (
    Activity,
    ActivityEditInput,
    ActivityInput,
    ActivityORM,
    ActivityVersion,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services.concepts.concept_generic_service import (
    ConceptGenericService,
    _AggregateRootType,
)


class ActivityService(ConceptGenericService[ActivityAR]):
    aggregate_class = ActivityAR
    version_class = ActivityVersion
    repository_interface = ActivityRepository

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: ActivityAR
    ) -> Activity:
        return Activity.from_activity_ar(
            activity_ar=item_ar,
            find_activity_subgroup_by_uid=self._repos.activity_subgroup_repository.find_by_uid_2,
            find_activity_group_by_uid=self._repos.activity_group_repository.find_by_uid_2,
        )

    def _create_aggregate_root(
        self, concept_input: ActivityInput, library
    ) -> _AggregateRootType:
        return ActivityAR.from_input_values(
            author=self.user_initials,
            concept_vo=ActivityVO.from_repository_values(
                name=concept_input.name,
                name_sentence_case=concept_input.name_sentence_case,
                definition=concept_input.definition,
                abbreviation=concept_input.abbreviation,
                activity_subgroup=concept_input.activity_subgroup,
            ),
            library=library,
            generate_uid_callback=self.repository.generate_uid,
            concept_exists_by_name_callback=self._repos.activity_repository.concept_exists_by_name,
            activity_subgroup_exists=self._repos.activity_subgroup_repository.final_concept_exists,
        )

    def _edit_aggregate(
        self, item: ActivityAR, concept_edit_input: ActivityEditInput
    ) -> ActivityAR:
        item.edit_draft(
            author=self.user_initials,
            change_description=concept_edit_input.change_description,
            concept_vo=ActivityVO.from_repository_values(
                name=concept_edit_input.name,
                name_sentence_case=concept_edit_input.name_sentence_case,
                definition=concept_edit_input.definition,
                abbreviation=concept_edit_input.abbreviation,
                activity_subgroup=concept_edit_input.activity_subgroup,
            ),
            concept_exists_by_name_callback=self._repos.activity_repository.concept_exists_by_name,
            activity_subgroup_exists=self._repos.activity_subgroup_repository.final_concept_exists,
        )
        return item

    @db.transaction
    def get_all_concepts(
        self,
        library: Optional[str] = None,
        sort_by: Optional[dict] = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: Optional[dict] = None,
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
        total_count: bool = False,
        only_specific_status: list = None,
        **kwargs,
    ) -> GenericFilteringReturn[ActivityORM]:

        self.enforce_library(library)
        try:
            items, total_count = self.repository.find_all_activities(
                library=library,
                total_count=total_count,
                sort_by=sort_by,
                filter_by=filter_by,
                filter_operator=filter_operator,
                page_number=page_number,
                page_size=page_size,
                only_specific_status=only_specific_status,
                **kwargs,
            )
        except ValueError as e:
            raise exceptions.ValidationException(e)

        all_concepts = GenericFilteringReturn.create(items, total_count)

        return all_concepts
