from typing import Sequence, Tuple

from neomodel import RelationshipDefinition

from clinical_mdr_api.domain.standard_data_models.master_model_dataset import (
    MasterModelDatasetAR,
    MasterModelDatasetMetadataVO,
    MasterModelDatasetVO,
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
)
from clinical_mdr_api.domain_repositories.models.biomedical_concepts import (
    ActivityInstanceClassRoot,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.models.standard_data_model import (
    DataModelIGRoot,
    DatasetRoot,
    DatasetVariableRoot,
    MasterModelDatasetValue,
    MasterModelValue,
)
from clinical_mdr_api.domain_repositories.neomodel_ext_item_repository import (
    NeomodelExtBaseRepository,
)
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.standard_data_models.master_model_dataset import (
    MasterModelDataset,
)


class MasterModelDatasetRepository(
    NeomodelExtBaseRepository, LibraryItemRepositoryImplBase[MasterModelDatasetAR]
):
    root_class = DatasetRoot
    value_class = MasterModelDatasetValue
    return_model = MasterModelDataset

    def get_neomodel_extension_query(self) -> CustomNodeSet:
        return (
            DatasetRoot.nodes.fetch_relations(
                "has_latest_master_model_value__has_dataset", "has_dataset__has_library"
            )
            .fetch_optional_relations(
                "has_latest_master_model_value__has_activity_instance_class"
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
        self, ar: MasterModelDatasetAR, value: MasterModelDatasetValue
    ) -> bool:
        return (
            ar.master_model_dataset_vo.description != value.description
            or ar.master_model_dataset_vo.is_basic_std != value.is_basic_std
            or ar.master_model_dataset_vo.xml_path != value.xml_path
            or ar.master_model_dataset_vo.xml_title != value.xml_title
            or ar.master_model_dataset_vo.structure != value.structure
            or ar.master_model_dataset_vo.purpose != value.purpose
            or ar.master_model_dataset_vo.comment != value.comment
            or ar.master_model_dataset_vo.ig_comment != value.ig_comment
            or ar.master_model_dataset_vo.map_domain_flag != value.map_domain_flag
            or ar.master_model_dataset_vo.suppl_qual_flag != value.suppl_qual_flag
            or ar.master_model_dataset_vo.include_in_raw != value.include_in_raw
            or ar.master_model_dataset_vo.gen_raw_seqno_flag != value.gen_raw_seqno_flag
            or ar.master_model_dataset_vo.enrich_build_order != value.enrich_build_order
        )

    def _create(self, item: MasterModelDatasetAR) -> MasterModelDatasetAR:
        """
        Overrides generic LibraryItemRepository method
        """
        relation_data: MasterModelDatasetMetadataVO = item.item_metadata
        root = DatasetRoot.nodes.get_or_none(uid=item.uid)

        if root is None:
            root = DatasetRoot(uid=item.uid).save()

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
        self, root_node: DatasetRoot
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
    ) -> MasterModelDatasetMetadataVO:
        major = relationship.version
        return MasterModelDatasetMetadataVO.from_repository_values(
            change_description=relationship.change_description,
            status=LibraryItemStatus(relationship.status),
            author=relationship.user_initials,
            start_date=relationship.start_date,
            end_date=relationship.end_date,
            major_version=int(major),
            minor_version=0,
        )

    def _get_or_create_value(
        self, root: DatasetRoot, ar: MasterModelDatasetAR
    ) -> MasterModelValue:
        for itm in root.has_master_model_version.all():
            if not self._has_data_changed(ar, itm):
                return itm

        new_value = MasterModelDatasetValue(
            description=ar.master_model_dataset_vo.description,
            is_basic_std=ar.master_model_dataset_vo.is_basic_std,
            xml_path=ar.master_model_dataset_vo.xml_path,
            xml_title=ar.master_model_dataset_vo.xml_title,
            structure=ar.master_model_dataset_vo.structure,
            purpose=ar.master_model_dataset_vo.purpose,
            comment=ar.master_model_dataset_vo.comment,
            ig_comment=ar.master_model_dataset_vo.ig_comment,
            map_domain_flag=ar.master_model_dataset_vo.map_domain_flag,
            suppl_qual_flag=ar.master_model_dataset_vo.suppl_qual_flag,
            include_in_raw=ar.master_model_dataset_vo.include_in_raw,
            gen_raw_seqno_flag=ar.master_model_dataset_vo.gen_raw_seqno_flag,
            enrich_build_order=ar.master_model_dataset_vo.enrich_build_order,
        )
        self._db_save_node(new_value)

        # Create relations
        # Find key & sort-key variable nodes
        if ar.master_model_dataset_vo.keys is not None:
            keys = DatasetVariableRoot.nodes.filter(
                uid__in=ar.master_model_dataset_vo.keys
            )
            keys_dict = {key.uid: key for key in keys}
            for index, key in enumerate(ar.master_model_dataset_vo.keys):
                if key in keys_dict:
                    new_value.has_key.connect(keys_dict[key], {"order": index})

        if ar.master_model_dataset_vo.sort_keys is not None:
            sort_keys = DatasetVariableRoot.nodes.filter(
                uid__in=ar.master_model_dataset_vo.sort_keys
            )
            sort_keys_dict = {key.uid: key for key in sort_keys}
            for index, key in enumerate(ar.master_model_dataset_vo.sort_keys):
                if key in sort_keys_dict:
                    new_value.has_sort_key.connect(keys_dict[key], {"order": index})

        # Connect with MasterModelValue node
        parent_node = MasterModelValue.nodes.get_or_none(
            name=ar.master_model_dataset_vo.master_model_name
        )
        if parent_node is None:
            raise BusinessLogicException(
                f"The given Master Model version {ar.master_model_dataset_vo.master_model_name} does not exist in the database."
            )
        new_value.has_dataset.connect(parent_node)

        # Find Instance class
        if ar.master_model_dataset_vo.activity_instance_class_uid is not None:
            activity_instance_class = ActivityInstanceClassRoot.nodes.get_or_none(
                uid=ar.master_model_dataset_vo.activity_instance_class_uid
            )
            new_value.has_activity_instance_class.connect(activity_instance_class)

        return new_value

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        *,
        root: DatasetRoot,
        library: Library,
        relationship: VersionRelationship,
        value: MasterModelDatasetValue,
    ) -> MasterModelDatasetAR:
        master_model: MasterModelValue = value.has_dataset.get_or_none()
        master_model_name = None
        master_model_version = None
        if master_model is not None:
            # TODO : Get the keys and sort keys
            data_model_ig: DataModelIGRoot = (
                master_model.has_master_model_version.single()
            )
            master_model_name = master_model.name
            rels: Sequence[
                VersionRelationship
            ] = master_model.has_master_model_version.all_relationships(data_model_ig)
            master_model_version = rels[0].version
        return MasterModelDatasetAR.from_repository_values(
            dataset_uid=root.uid,
            master_model_dataset_vo=MasterModelDatasetVO.from_repository_values(
                master_model_name=master_model_name,
                master_model_version_number=master_model_version,
                dataset_uid=root.uid,
                description=value.description,
                is_basic_std=value.is_basic_std,
                xml_path=value.xml_path,
                xml_title=value.xml_title,
                structure=value.structure,
                purpose=value.purpose,
                keys=None,
                sort_keys=None,
                comment=value.comment,
                ig_comment=value.ig_comment,
                map_domain_flag=value.map_domain_flag,
                suppl_qual_flag=value.suppl_qual_flag,
                include_in_raw=value.include_in_raw,
                gen_raw_seqno_flag=value.gen_raw_seqno_flag,
                enrich_build_order=value.enrich_build_order,
                activity_instance_class_uid=None,
            ),
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=(lambda _: library.is_editable),
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
        )

    def _maintain_parameters(
        self,
        versioned_object: MasterModelDatasetAR,
        root: DatasetRoot,
        value: MasterModelDatasetValue,
    ) -> None:
        pass
