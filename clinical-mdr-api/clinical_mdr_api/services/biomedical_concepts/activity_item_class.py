from clinical_mdr_api.domain.biomedical_concepts.activity_item_class import (
    ActivityItemClassAR,
    ActivityItemClassVO,
)
from clinical_mdr_api.domain.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.domain_repositories.biomedical_concepts.activity_item_class_repository import (
    ActivityItemClassRepository,
)
from clinical_mdr_api.models.biomedical_concepts.activity_item_class import (
    ActivityItemClass,
    ActivityItemClassCreateInput,
    ActivityItemClassEditInput,
    ActivityItemClassVersion,
)
from clinical_mdr_api.services.neomodel_ext_generic import (
    NeomodelExtGenericService,
    _AggregateRootType,
)


class ActivityItemClassService(NeomodelExtGenericService):
    repository_interface = ActivityItemClassRepository
    api_model_class = ActivityItemClass
    version_class = ActivityItemClassVersion

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: ActivityItemClassAR
    ) -> ActivityItemClass:
        return ActivityItemClass.from_activity_item_class_ar(
            activity_item_class_ar=item_ar,
            find_activity_instance_class_by_uid=self._repos.activity_instance_class_repository.find_by_uid_2,
        )

    def _create_aggregate_root(
        self, item_input: ActivityItemClassCreateInput, library: LibraryVO
    ) -> _AggregateRootType:
        return ActivityItemClassAR.from_input_values(
            author=self.user_initials,
            activity_item_class_vo=ActivityItemClassVO.from_repository_values(
                name=item_input.name,
                order=item_input.order,
                mandatory=item_input.mandatory,
                activity_instance_class_uids=item_input.activity_instance_class_uids,
            ),
            library=library,
            generate_uid_callback=self.repository.generate_uid,
            activity_instance_class_exists=self._repos.activity_instance_class_repository.check_exists_final_version,
            activity_item_class_exists_by_name_callback=self._repos.activity_item_class_repository.check_exists_by_name,
        )

    def _edit_aggregate(
        self, item: ActivityItemClassAR, item_edit_input: ActivityItemClassEditInput
    ) -> ActivityItemClassAR:
        item.edit_draft(
            author=self.user_initials,
            change_description=item_edit_input.change_description,
            activity_item_class_vo=ActivityItemClassVO.from_repository_values(
                name=item_edit_input.name,
                order=item_edit_input.order,
                mandatory=item_edit_input.mandatory,
                activity_instance_class_uids=item_edit_input.activity_instance_class_uids,
            ),
            activity_instance_class_exists=self._repos.activity_instance_class_repository.check_exists_final_version,
            activity_item_class_exists_by_name_callback=self._repos.activity_item_class_repository.check_exists_by_name,
        )
        return item
