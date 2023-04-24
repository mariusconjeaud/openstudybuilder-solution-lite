from clinical_mdr_api.domain.standard_data_models.master_model import (
    MasterModelAR,
    MasterModelVO,
)
from clinical_mdr_api.domain.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.domain_repositories.standard_data_models.master_model_repository import (
    MasterModelRepository,
)
from clinical_mdr_api.models.standard_data_models.master_model import (
    MasterModel,
    MasterModelInput,
)
from clinical_mdr_api.services.neomodel_ext_generic import NeomodelExtGenericService


class MasterModelService(NeomodelExtGenericService):
    repository_interface = MasterModelRepository
    api_model_class = MasterModel

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: MasterModelAR
    ) -> MasterModel:
        return MasterModel.from_master_model_ar(
            master_model_ar=item_ar,
        )

    def _create_aggregate_root(
        self, item_input: MasterModelInput, library: LibraryVO
    ) -> MasterModelAR:
        return MasterModelAR.from_input_values(
            author=self.user_initials,
            master_model_vo=MasterModelVO.from_repository_values(
                ig_uid=item_input.ig_uid,
                ig_version_number=item_input.ig_version_number,
                name=self.repository.generate_name(
                    ig_uid=item_input.ig_uid,
                    ig_version_number=item_input.ig_version_number,
                    version_number=item_input.version_number,
                ),
                version_number=item_input.version_number,
            ),
            library=library,
        )

    def _edit_aggregate(
        self, item: MasterModelAR, item_edit_input: MasterModelInput
    ) -> MasterModelAR:
        item.edit_draft(
            author=self.user_initials,
            change_description=item_edit_input.change_description,
            master_model_vo=MasterModelVO.from_repository_values(
                ig_uid=item_edit_input.ig_uid,
                ig_version_number=item_edit_input.ig_version_number,
                name=self.repository.generate_name(
                    ig_uid=item_edit_input.ig_uid,
                    ig_version_number=item_edit_input.ig_version_number,
                    version_number=item_edit_input.version_number,
                ),
                version_number=item_edit_input.version_number,
            ),
        )
        return item
