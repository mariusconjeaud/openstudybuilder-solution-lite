from clinical_mdr_api.domain.biomedical_concepts.activity_item import (
    ActivityItemAR,
    ActivityItemVO,
)
from clinical_mdr_api.domain.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.domain_repositories.biomedical_concepts.activity_item_repository import (
    ActivityItemRepository,
)
from clinical_mdr_api.models.biomedical_concepts.activity_item import (
    ActivityItem,
    ActivityItemCreateInput,
    ActivityItemEditInput,
    ActivityItemVersion,
)
from clinical_mdr_api.services.neomodel_ext_generic import NeomodelExtGenericService


class ActivityItemService(NeomodelExtGenericService):
    repository_interface = ActivityItemRepository
    api_model_class = ActivityItem
    version_class = ActivityItemVersion

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: ActivityItemAR
    ) -> ActivityItem:
        return ActivityItem.from_activity_item_ar(
            activity_item_ar=item_ar,
        )

    def _create_aggregate_root(
        self, item_input: ActivityItemCreateInput, library: LibraryVO
    ) -> ActivityItemAR:
        return ActivityItemAR.from_input_values(
            author=self.user_initials,
            activity_item_vo=ActivityItemVO.from_repository_values(
                name=item_input.name,
                activity_item_class_uid=item_input.activity_item_class_uid,
                activity_item_class_name=None,
                ct_term_uid=item_input.ct_term_uid,
                ct_term_name=None,
                unit_definition_uid=item_input.unit_definition_uid,
                unit_definition_name=None,
            ),
            library=library,
            generate_uid_callback=self.repository.generate_uid,
            activity_item_exists_by_name_callback=self._repos.activity_item_repository.check_exists_by_name,
            activity_item_class_exists=self._repos.activity_item_class_repository.check_exists_final_version,
            ct_term_exists=self._repos.ct_term_name_repository.term_exists,
            unit_definition_exists=self._repos.unit_definition_repository.final_concept_exists,
        )

    def _edit_aggregate(
        self, item: ActivityItemAR, item_edit_input: ActivityItemEditInput
    ) -> ActivityItemAR:
        item.edit_draft(
            author=self.user_initials,
            change_description=item_edit_input.change_description,
            activity_item_vo=ActivityItemVO.from_repository_values(
                name=item_edit_input.name,
                activity_item_class_uid=item_edit_input.activity_item_class_uid,
                activity_item_class_name=None,
                ct_term_uid=item_edit_input.ct_term_uid,
                ct_term_name=None,
                unit_definition_uid=item_edit_input.unit_definition_uid,
                unit_definition_name=None,
            ),
            activity_item_exists_by_name_callback=self._repos.activity_item_repository.check_exists_by_name,
            activity_item_class_exists=self._repos.activity_item_class_repository.check_exists_final_version,
            ct_term_exists=self._repos.ct_term_name_repository.term_exists,
            unit_definition_exists=self._repos.unit_definition_repository.final_concept_exists,
        )
        return item
