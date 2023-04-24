from clinical_mdr_api.domain.concepts.activities.activity_instance import (
    ActivityInstanceAR,
    ActivityInstanceVO,
    SimpleActivityItemVO,
)
from clinical_mdr_api.domain.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.domain_repositories.concepts.activities.activity_instance_repository import (
    ActivityInstanceRepository,
)
from clinical_mdr_api.exceptions import NotFoundException
from clinical_mdr_api.models.activities.activity_instance import (
    ActivityInstance,
    ActivityInstanceCreateInput,
    ActivityInstanceEditInput,
    ActivityInstanceOverview,
    ActivityInstanceVersion,
)
from clinical_mdr_api.services.concepts.concept_generic_service import (
    ConceptGenericService,
    _AggregateRootType,
)


class ActivityInstanceService(ConceptGenericService[ActivityInstanceAR]):
    aggregate_class = ActivityInstanceAR
    repository_interface = ActivityInstanceRepository
    version_class = ActivityInstanceVersion

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: ActivityInstanceAR
    ) -> ActivityInstance:
        return ActivityInstance.from_activity_ar(
            activity_ar=item_ar,
            find_activity_hierarchy_by_uid=self._repos.activity_repository.find_by_uid_2,
            find_activity_subgroup_by_uid=self._repos.activity_subgroup_repository.find_by_uid_2,
            find_activity_group_by_uid=self._repos.activity_group_repository.find_by_uid_2,
        )

    def _create_aggregate_root(
        self, concept_input: ActivityInstanceCreateInput, library: LibraryVO
    ) -> _AggregateRootType:
        return ActivityInstanceAR.from_input_values(
            author=self.user_initials,
            concept_vo=ActivityInstanceVO.from_repository_values(
                name=concept_input.name,
                name_sentence_case=concept_input.name_sentence_case,
                definition=concept_input.definition,
                abbreviation=concept_input.abbreviation,
                topic_code=concept_input.topic_code,
                adam_param_code=concept_input.adam_param_code,
                legacy_description=concept_input.legacy_description,
                activity_uids=concept_input.activities,
                activity_instance_class_uid=concept_input.activity_instance_class_uid,
                activity_instance_class_name=None,
                activity_items=[
                    SimpleActivityItemVO.from_repository_values(
                        uid=activity_item_uid,
                        name=None,
                        activity_item_class_uid=None,
                        activity_item_class_name=None,
                    )
                    for activity_item_uid in concept_input.activity_item_uids
                ]
                if concept_input.activity_item_uids
                else None,
            ),
            library=library,
            generate_uid_callback=self.repository.generate_uid,
            concept_exists_by_name_callback=self.repository.concept_exists_by_name,
            activity_instance_class_exists_by_uid_callback=self._repos.activity_instance_class_repository.check_exists_final_version,
            activity_hierarchy_exists_by_uid_callback=self._repos.activity_repository.final_concept_exists,
            activity_item_exists_by_uid_callback=self._repos.activity_item_repository.check_exists_final_version,
        )

    def _edit_aggregate(
        self, item: ActivityInstanceAR, concept_edit_input: ActivityInstanceEditInput
    ) -> ActivityInstanceAR:
        item.edit_draft(
            author=self.user_initials,
            change_description=concept_edit_input.change_description,
            concept_vo=ActivityInstanceVO.from_repository_values(
                name=concept_edit_input.name,
                name_sentence_case=concept_edit_input.name_sentence_case,
                definition=concept_edit_input.definition,
                abbreviation=concept_edit_input.abbreviation,
                topic_code=concept_edit_input.topic_code,
                adam_param_code=concept_edit_input.adam_param_code,
                legacy_description=concept_edit_input.legacy_description,
                activity_uids=concept_edit_input.activities,
                activity_instance_class_uid=concept_edit_input.activity_instance_class_uid,
                activity_instance_class_name=None,
                activity_items=[
                    SimpleActivityItemVO.from_repository_values(
                        uid=activity_item_uid,
                        name=None,
                        activity_item_class_uid=None,
                        activity_item_class_name=None,
                    )
                    for activity_item_uid in concept_edit_input.activity_item_uids
                ]
                if concept_edit_input.activity_item_uids
                else [],
            ),
            concept_exists_by_name_callback=self.repository.concept_exists_by_name,
            activity_instance_class_exists_by_uid_callback=self._repos.activity_instance_class_repository.check_exists_final_version,
            activity_hierarchy_exists_by_uid_callback=self._repos.activity_repository.final_concept_exists,
            activity_item_exists_by_uid_callback=self._repos.activity_item_repository.check_exists_final_version,
        )
        return item

    def get_activity_instance_overview(
        self, activity_instance_uid: str
    ) -> ActivityInstanceOverview:
        if not self.repository.final_concept_exists(uid=activity_instance_uid):
            raise NotFoundException(
                f"Cannot find ActivityInstance with the following uid ({activity_instance_uid}) in status (Final)"
            )
        overview = (
            self._repos.activity_instance_repository.get_activity_instance_overview(
                uid=activity_instance_uid
            )
        )
        return ActivityInstanceOverview.from_repository_input(overview=overview)
