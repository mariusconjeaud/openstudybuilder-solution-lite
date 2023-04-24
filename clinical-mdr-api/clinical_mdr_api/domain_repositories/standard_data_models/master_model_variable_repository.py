from typing import Tuple

from neomodel import RelationshipDefinition

from clinical_mdr_api.domain.standard_data_models.master_model_variable import (
    MasterModelVariableAR,
    MasterModelVariableMetadataVO,
    MasterModelVariableVO,
)
from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryItemStatus,
    LibraryVO,
)
from clinical_mdr_api.domain_repositories.library_item_repository import (
    LibraryItemRepositoryImplBase,
)
from clinical_mdr_api.domain_repositories.models._utils import (
    LATEST_VERSION_ORDER_BY,
    CustomNodeSet,
    to_relation_trees,
)
from clinical_mdr_api.domain_repositories.models.biomedical_concepts import (
    ActivityItemClassRoot,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.models.standard_data_model import (
    ClassVariableRoot,
    DatasetClassRoot,
    DatasetClassValue,
    DatasetVariableRoot,
    MasterModelValue,
    MasterModelVariableValue,
)
from clinical_mdr_api.domain_repositories.neomodel_ext_item_repository import (
    NeomodelExtBaseRepository,
)
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.standard_data_models.master_model_variable import (
    MasterModelVariable,
)


class MasterModelVariableRepository(
    NeomodelExtBaseRepository, LibraryItemRepositoryImplBase[MasterModelVariableAR]
):
    root_class = DatasetVariableRoot
    value_class = MasterModelVariableValue
    return_model = MasterModelVariable

    def get_neomodel_extension_query(self) -> CustomNodeSet:
        return (
            ClassVariableRoot.nodes.fetch_relations(
                "has_latest_master_model_value__has_variable",
                "has_class_variable__has_library",
            )
            .fetch_optional_relations(
                "has_latest_master_model_value__has_activity_item_class"
            )
            .fetch_optional_single_relation_of_type(
                {
                    "has_master_model_version": (
                        "latest_version",
                        LATEST_VERSION_ORDER_BY,
                    ),
                }
            )
        )

    def _has_data_changed(
        self, ar: MasterModelVariableAR, value: MasterModelVariableValue
    ) -> bool:
        return (
            ar.master_model_variable_vo.description != value.description
            or ar.master_model_variable_vo.is_basic_std != value.is_basic_std
            or ar.master_model_variable_vo.variable_type != value.variable_type
            or ar.master_model_variable_vo.length != value.length
            or ar.master_model_variable_vo.display_format != value.display_format
            or ar.master_model_variable_vo.xml_datatype != value.xml_datatype
            or ar.master_model_variable_vo.xml_codelist != value.xml_codelist
            or ar.master_model_variable_vo.xml_codelist_multi
            != value.xml_codelist_multi
            or ar.master_model_variable_vo.core != value.core
            or ar.master_model_variable_vo.role != value.role
            or ar.master_model_variable_vo.term != value.term
            or ar.master_model_variable_vo.algorithm != value.algorithm
            or ar.master_model_variable_vo.qualifiers != value.qualifiers
            or ar.master_model_variable_vo.comment != value.comment
            or ar.master_model_variable_vo.ig_comment != value.ig_comment
            or ar.master_model_variable_vo.map_var_flag != value.map_var_flag
            or ar.master_model_variable_vo.fixed_mapping != value.fixed_mapping
            or ar.master_model_variable_vo.include_in_raw != value.include_in_raw
            or ar.master_model_variable_vo.nn_internal != value.nn_internal
            or ar.master_model_variable_vo.value_lvl_where_cols
            != value.value_lvl_where_cols
            or ar.master_model_variable_vo.value_lvl_label_col
            != value.value_lvl_label_col
            or ar.master_model_variable_vo.value_lvl_collect_ct_val
            != value.value_lvl_collect_ct_val
            or ar.master_model_variable_vo.value_lvl_ct_codelist_id_col
            != value.value_lvl_ct_codelist_id_col
            or ar.master_model_variable_vo.enrich_build_order
            != value.enrich_build_order
            or ar.master_model_variable_vo.enrich_rule != value.enrich_rule
            or ar.master_model_variable_vo.xml_codelist_values
            != value.xml_codelist_values
        )

    def _create(self, item: MasterModelVariableAR) -> MasterModelVariableAR:
        """
        Overrides generic LibraryItemRepository method
        """
        relation_data: MasterModelVariableMetadataVO = item.item_metadata
        root = ClassVariableRoot.nodes.get_or_none(uid=item.uid)

        if root is None:
            root = ClassVariableRoot(uid=item.uid).save()

        value = self._get_or_create_value(root=root, ar=item)

        (
            root,
            value,
            _,
            _,
            _,
        ) = self._db_create_and_link_nodes(
            root=root,
            value=value,
            rel_properties=self._library_item_metadata_vo_to_datadict(relation_data),
            save_root=False,
        )

        return item

    def _get_version_relation_keys(
        self, root_node: ClassVariableRoot
    ) -> Tuple[
        RelationshipDefinition,
        RelationshipDefinition,
        RelationshipDefinition,
        RelationshipDefinition,
        RelationshipDefinition,
    ]:
        return (
            root_node.has_master_model_version,
            root_node.has_latest_master_model_value,
            root_node.latest_master_model_draft,
            root_node.latest_master_model_final,
            root_node.latest_master_model_retired,
        )

    @staticmethod
    def _library_item_metadata_vo_from_relation(
        relationship: VersionRelationship,
    ) -> MasterModelVariableMetadataVO:
        major = relationship.version
        return MasterModelVariableMetadataVO.from_repository_values(
            change_description=relationship.change_description,
            status=LibraryItemStatus(relationship.status),
            author=relationship.user_initials,
            start_date=relationship.start_date,
            end_date=relationship.end_date,
            major_version=int(major),
            minor_version=0,
        )

    def _get_or_create_value(
        self, root: DatasetVariableRoot, ar: MasterModelVariableAR
    ) -> MasterModelValue:
        for itm in root.has_master_model_version.all():
            if not self._has_data_changed(ar, itm):
                return itm

        new_value = MasterModelVariableValue(
            description=ar.master_model_variable_vo.description,
            is_basic_std=ar.master_model_variable_vo.is_basic_std,
            variable_type=ar.master_model_variable_vo.variable_type,
            length=ar.master_model_variable_vo.length,
            display_format=ar.master_model_variable_vo.display_format,
            xml_datatype=ar.master_model_variable_vo.xml_datatype,
            xml_codelist=ar.master_model_variable_vo.xml_codelist,
            xml_codelist_multi=ar.master_model_variable_vo.xml_codelist_multi,
            core=ar.master_model_variable_vo.core,
            role=ar.master_model_variable_vo.role,
            term=ar.master_model_variable_vo.term,
            algorithm=ar.master_model_variable_vo.algorithm,
            qualifiers=ar.master_model_variable_vo.qualifiers,
            comment=ar.master_model_variable_vo.comment,
            ig_comment=ar.master_model_variable_vo.ig_comment,
            map_var_flag=ar.master_model_variable_vo.map_var_flag,
            fixed_mapping=ar.master_model_variable_vo.fixed_mapping,
            include_in_raw=ar.master_model_variable_vo.include_in_raw,
            nn_internal=ar.master_model_variable_vo.nn_internal,
            value_lvl_where_cols=ar.master_model_variable_vo.value_lvl_where_cols,
            value_lvl_label_col=ar.master_model_variable_vo.value_lvl_label_col,
            value_lvl_collect_ct_val=ar.master_model_variable_vo.value_lvl_collect_ct_val,
            value_lvl_ct_codelist_id_col=ar.master_model_variable_vo.value_lvl_ct_codelist_id_col,
            enrich_build_order=ar.master_model_variable_vo.enrich_build_order,
            enrich_rule=ar.master_model_variable_vo.enrich_rule,
            xml_codelist_values=ar.master_model_variable_vo.xml_codelist_values,
        )
        self._db_save_node(new_value)

        # Connect with MasterModelDatasetValue node
        # dataset_root: DatasetRoot = DatasetRoot.nodes.get_or_none(
        #     uid=ar.master_model_variable_vo.class_uid
        # )

        class_value = to_relation_trees(
            DatasetClassValue.nodes.fetch_relations(
                "version_of", "has_dataset_class__implements"
            ).filter(
                version_of__uid=ar.master_model_variable_vo.class_uid,
                has_dataset_class__implements__version_number="3.2",
            )
        )

        if not class_value:
            raise BusinessLogicException(
                f"The given Dataset {ar.master_model_variable_vo.class_uid} does not exist in the database."
            )
        # latest_dataset_value: MasterModelDatasetValue = (
        #     class_root.has_latest_master_model_value.single()
        # )

        # if latest_dataset_value is None:
        #     raise BusinessLogicException(
        #         f"The given Dataset {ar.master_model_variable_vo.class_uid} does not have a valid latest master model version in the database."
        #     )

        new_value.has_variable.connect(class_value[0])

        # Find Instance class
        if ar.master_model_variable_vo.activity_item_class_uid is not None:
            activity_item_class = ActivityItemClassRoot.nodes.get_or_none(
                uid=ar.master_model_variable_vo.activity_item_class_uid
            )
            new_value.has_activity_item_class.connect(activity_item_class)

        return new_value

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        *,
        root: DatasetVariableRoot,
        library: Library,
        relationship: VersionRelationship,
        value: MasterModelVariableValue,
    ) -> MasterModelVariableAR:
        # TODO : Get the class uid
        class_value: DatasetClassValue = value.has_variable.get_or_none()
        class_uid = None
        if class_value is not None:
            class_root: DatasetClassRoot = class_value.version_of.single()
            if class_root is not None:
                class_uid = class_root.uid
        return MasterModelVariableAR.from_repository_values(
            variable_uid=root.uid,
            master_model_variable_vo=MasterModelVariableVO.from_repository_values(
                class_uid=class_uid,
                variable_uid=root.uid,
                master_model_version_number=None,
                description=value.description,
                is_basic_std=value.is_basic_std,
                variable_type=value.variable_type,
                length=value.length,
                display_format=value.display_format,
                xml_datatype=value.xml_datatype,
                xml_codelist=value.xml_codelist,
                xml_codelist_multi=value.xml_codelist_multi,
                core=value.core,
                role=value.role,
                term=value.term,
                algorithm=value.algorithm,
                qualifiers=value.qualifiers,
                comment=value.comment,
                ig_comment=value.ig_comment,
                map_var_flag=value.map_var_flag,
                fixed_mapping=value.fixed_mapping,
                include_in_raw=value.include_in_raw,
                nn_internal=value.nn_internal,
                value_lvl_where_cols=value.value_lvl_where_cols,
                value_lvl_label_col=value.value_lvl_label_col,
                value_lvl_collect_ct_val=value.value_lvl_collect_ct_val,
                value_lvl_ct_codelist_id_col=value.value_lvl_ct_codelist_id_col,
                enrich_build_order=value.enrich_build_order,
                enrich_rule=value.enrich_rule,
                xml_codelist_values=value.xml_codelist_values,
                activity_item_class_uid=None,
            ),
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=(lambda _: library.is_editable),
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
        )

    def _maintain_parameters(
        self,
        versioned_object: MasterModelVariableAR,
        root: DatasetVariableRoot,
        value: MasterModelVariableValue,
    ) -> None:
        pass
