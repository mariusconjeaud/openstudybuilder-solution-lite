from clinical_mdr_api.domain_repositories.standard_data_models.master_model_variable_repository import (
    MasterModelVariableRepository,
)
from clinical_mdr_api.domains.standard_data_models.master_model_variable import (
    MasterModelVariableAR,
    MasterModelVariableVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.models.standard_data_models.master_model_variable import (
    MasterModelVariable,
    MasterModelVariableInput,
)
from clinical_mdr_api.services.neomodel_ext_generic import NeomodelExtGenericService


class MasterModelVariableService(NeomodelExtGenericService):
    repository_interface = MasterModelVariableRepository
    api_model_class = MasterModelVariable

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: MasterModelVariableAR
    ) -> MasterModelVariable:
        return MasterModelVariable.from_master_model_variable_ar(
            master_model_variable_ar=item_ar,
        )

    def _create_aggregate_root(
        self, item_input: MasterModelVariableInput, library: LibraryVO
    ) -> MasterModelVariableAR:
        return MasterModelVariableAR.from_input_values(
            author=self.user_initials,
            master_model_variable_vo=MasterModelVariableVO.from_repository_values(
                dataset_uid=item_input.dataset_uid,
                variable_uid=item_input.variable_uid,
                master_model_version_number=item_input.master_model_version_number,
                description=item_input.description,
                is_basic_std=item_input.is_basic_std,
                variable_type=item_input.variable_type,
                length=item_input.length,
                display_format=item_input.display_format,
                xml_datatype=item_input.xml_datatype,
                xml_codelist=item_input.xml_codelist,
                xml_codelist_multi=item_input.xml_codelist_multi,
                core=item_input.core,
                role=item_input.role,
                term=item_input.term,
                algorithm=item_input.algorithm,
                qualifiers=item_input.qualifiers,
                comment=item_input.comment,
                ig_comment=item_input.ig_comment,
                map_var_flag=item_input.map_var_flag,
                fixed_mapping=item_input.fixed_mapping,
                include_in_raw=item_input.include_in_raw,
                nn_internal=item_input.nn_internal,
                value_lvl_where_cols=item_input.value_lvl_where_cols,
                value_lvl_label_col=item_input.value_lvl_label_col,
                value_lvl_collect_ct_val=item_input.value_lvl_collect_ct_val,
                value_lvl_ct_codelist_id_col=item_input.value_lvl_ct_codelist_id_col,
                enrich_build_order=item_input.enrich_build_order,
                enrich_rule=item_input.enrich_rule,
                xml_codelist_values=item_input.xml_codelist_values,
                activity_item_class_uid=item_input.activity_item_class_uid,
            ),
            library=library,
        )

    def _edit_aggregate(
        self, item: MasterModelVariableAR, item_edit_input: MasterModelVariableInput
    ) -> MasterModelVariableAR:
        item.edit_draft(
            author=self.user_initials,
            change_description=item_edit_input.change_description,
            master_model_vo=MasterModelVariableVO.from_repository_values(
                dataset_uid=item_edit_input.dataset_uid,
                variable_uid=item_edit_input.variable_uid,
                master_model_version_number=item_edit_input.master_model_version_number,
                description=item_edit_input.description,
                is_basic_std=item_edit_input.is_basic_std,
                variable_type=item_edit_input.variable_type,
                length=item_edit_input.length,
                display_format=item_edit_input.display_format,
                xml_datatype=item_edit_input.xml_datatype,
                xml_codelist=item_edit_input.xml_codelist,
                xml_codelist_multi=item_edit_input.xml_codelist_multi,
                core=item_edit_input.core,
                role=item_edit_input.role,
                term=item_edit_input.term,
                algorithm=item_edit_input.algorithm,
                qualifiers=item_edit_input.qualifiers,
                comment=item_edit_input.comment,
                ig_comment=item_edit_input.ig_comment,
                map_var_flag=item_edit_input.map_var_flag,
                fixed_mapping=item_edit_input.fixed_mapping,
                include_in_raw=item_edit_input.include_in_raw,
                nn_internal=item_edit_input.nn_internal,
                value_lvl_where_cols=item_edit_input.value_lvl_where_cols,
                value_lvl_label_col=item_edit_input.value_lvl_label_col,
                value_lvl_collect_ct_val=item_edit_input.value_lvl_collect_ct_val,
                value_lvl_ct_codelist_id_col=item_edit_input.value_lvl_ct_codelist_id_col,
                enrich_build_order=item_edit_input.enrich_build_order,
                enrich_rule=item_edit_input.enrich_rule,
                xml_codelist_values=item_edit_input.xml_codelist_values,
                activity_item_class_uid=item_edit_input.activity_item_class_uid,
            ),
        )
        return item
