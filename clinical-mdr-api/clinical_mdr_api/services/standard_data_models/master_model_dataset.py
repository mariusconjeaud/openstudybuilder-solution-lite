from clinical_mdr_api.domain_repositories.standard_data_models.master_model_dataset_repository import (
    MasterModelDatasetRepository,
)
from clinical_mdr_api.domains.standard_data_models.master_model_dataset import (
    MasterModelDatasetAR,
    MasterModelDatasetVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.models.standard_data_models.master_model_dataset import (
    MasterModelDataset,
    MasterModelDatasetInput,
)
from clinical_mdr_api.services.neomodel_ext_generic import NeomodelExtGenericService


class MasterModelDatasetService(NeomodelExtGenericService):
    repository_interface = MasterModelDatasetRepository
    api_model_class = MasterModelDataset

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: MasterModelDatasetAR
    ) -> MasterModelDataset:
        return MasterModelDataset.from_master_model_dataset_ar(
            master_model_dataset_ar=item_ar,
        )

    def _create_aggregate_root(
        self, item_input: MasterModelDatasetInput, library: LibraryVO
    ) -> MasterModelDatasetAR:
        return MasterModelDatasetAR.from_input_values(
            author=self.user_initials,
            master_model_dataset_vo=MasterModelDatasetVO.from_repository_values(
                master_model_name=item_input.master_model_name,
                master_model_version_number=item_input.master_model_version_number,
                dataset_uid=item_input.dataset_uid,
                description=item_input.description,
                is_basic_std=item_input.is_basic_std,
                xml_path=item_input.xml_path,
                xml_title=item_input.xml_title,
                structure=item_input.structure,
                purpose=item_input.purpose,
                keys=item_input.keys,
                sort_keys=item_input.sort_keys,
                comment=item_input.comment,
                ig_comment=item_input.ig_comment,
                map_domain_flag=item_input.map_domain_flag,
                suppl_qual_flag=item_input.suppl_qual_flag,
                include_in_raw=item_input.include_in_raw,
                gen_raw_seqno_flag=item_input.gen_raw_seqno_flag,
                enrich_build_order=item_input.enrich_build_order,
                activity_instance_class_uid=item_input.activity_instance_class_uid,
            ),
            library=library,
        )

    def _edit_aggregate(
        self, item: MasterModelDatasetAR, item_edit_input: MasterModelDatasetInput
    ) -> MasterModelDatasetAR:
        item.edit_draft(
            author=self.user_initials,
            change_description=item_edit_input.change_description,
            master_model_vo=MasterModelDatasetVO.from_repository_values(
                master_model_name=item_edit_input.master_model_name,
                master_model_version_number=item_edit_input.master_model_version_number,
                dataset_uid=item_edit_input.dataset_uid,
                description=item_edit_input.description,
                is_basic_std=item_edit_input.is_basic_std,
                xml_path=item_edit_input.xml_path,
                xml_title=item_edit_input.xml_title,
                structure=item_edit_input.structure,
                purpose=item_edit_input.purpose,
                keys=item_edit_input.keys,
                sort_keys=item_edit_input.sort_keys,
                comment=item_edit_input.comment,
                ig_comment=item_edit_input.ig_comment,
                map_domain_flag=item_edit_input.map_domain_flag,
                suppl_qual_flag=item_edit_input.suppl_qual_flag,
                include_in_raw=item_edit_input.include_in_raw,
                gen_raw_seqno_flag=item_edit_input.gen_raw_seqno_flag,
                enrich_build_order=item_edit_input.enrich_build_order,
                activity_instance_class_uid=item_edit_input.activity_instance_class_uid,
            ),
        )
        return item
