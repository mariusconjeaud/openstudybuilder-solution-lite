from typing import Tuple

from neomodel import RelationshipDefinition

from clinical_mdr_api.domain_repositories.library_item_repository import (
    LibraryItemRepositoryImplBase,
)
from clinical_mdr_api.domain_repositories.models._utils import (
    LATEST_VERSION_ORDER_BY,
    CustomNodeSet,
    to_relation_trees,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.models.standard_data_model import (
    DataModelIGRoot,
    MasterModelValue,
)
from clinical_mdr_api.domain_repositories.neomodel_ext_item_repository import (
    NeomodelExtBaseRepository,
)
from clinical_mdr_api.domains.standard_data_models.master_model import (
    MasterModelAR,
    MasterModelMetadataVO,
    MasterModelVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemStatus,
    LibraryVO,
)
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.standard_data_models.master_model import MasterModel


class MasterModelRepository(
    NeomodelExtBaseRepository, LibraryItemRepositoryImplBase[MasterModelAR]
):
    root_class = DataModelIGRoot
    value_class = MasterModelValue
    return_model = MasterModel

    def get_neomodel_extension_query(self) -> CustomNodeSet:
        return DataModelIGRoot.nodes.fetch_relations(
            "has_library",
            "has_latest_master_model_value__extends_version",
        ).fetch_optional_single_relation_of_type(
            {
                "has_master_model_version": ("latest_version", LATEST_VERSION_ORDER_BY),
            }
        )

    def generate_name(self, ig_uid: str, ig_version_number: str, version_number: str):
        name = "_".join(
            [
                str.lower(ig_uid),
                "mastermodel",
                ig_version_number,
                f"NN{version_number}",
            ]
        )
        return name

    def _find_latest_version_number(self, ig_uid: str) -> int:
        ig = DataModelIGRoot.nodes.get_or_none(uid=ig_uid)
        if ig is None:
            raise BusinessLogicException(
                f"The target Implementation Guide {ig_uid} does not exist in the database."
            )

        latest_master_model = to_relation_trees(
            DataModelIGRoot.nodes.filter(uid=ig_uid)
            .fetch_relations("has_latest_master_model_value")
            .fetch_optional_single_relation_of_type(
                {
                    "has_master_model_version": (
                        "latest_version",
                        LATEST_VERSION_ORDER_BY,
                    ),
                }
            )
        )
        if latest_master_model is None or not latest_master_model:
            return 0

        return int(MasterModel.from_orm(latest_master_model[0]).version)

    def _has_data_changed(self, ar: MasterModelAR, value: MasterModelValue) -> bool:
        return ar.master_model_vo.name != value.name

    def _create(self, item: MasterModelAR) -> MasterModelAR:
        """
        Overrides generic LibraryItemRepository method
        """
        relation_data: MasterModelMetadataVO = item.item_metadata
        root = DataModelIGRoot.nodes.get_or_none(uid=item.uid)

        if root is None:
            raise BusinessLogicException(
                f"The target Implementation Guide {item.uid} does not exist in the database."
            )

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
        self, root_node: DataModelIGRoot
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
    ) -> MasterModelMetadataVO:
        major = relationship.version
        return MasterModelMetadataVO.from_repository_values(
            change_description=relationship.change_description,
            status=LibraryItemStatus(relationship.status),
            author=relationship.user_initials,
            start_date=relationship.start_date,
            end_date=relationship.end_date,
            major_version=int(major),
            minor_version=0,
        )

    def _get_or_create_value(
        self, root: DataModelIGRoot, ar: MasterModelAR
    ) -> MasterModelValue:
        for itm in root.has_master_model_version.all():
            if not self._has_data_changed(ar, itm):
                return itm
        latest_draft = root.latest_master_model_draft.get_or_none()
        if latest_draft and not self._has_data_changed(ar, latest_draft):
            return latest_draft
        latest_final = root.latest_master_model_final.get_or_none()
        if latest_final and not self._has_data_changed(ar, latest_final):
            return latest_final
        latest_retired = root.latest_master_model_retired.get_or_none()
        if latest_retired and not self._has_data_changed(ar, latest_retired):
            return latest_retired

        new_value = MasterModelValue(
            name=ar.master_model_vo.name,
        )
        self._db_save_node(new_value)

        ig_versions = root.has_version.filter(
            version_number=ar.master_model_vo.ig_version_number
        )
        if ig_versions is None or len(ig_versions) == 0:
            raise BusinessLogicException(
                f"The target version {ar.master_model_vo.ig_version_number}"
                f" for the Implementation Guide {ar.master_model_vo.ig_uid} does not exist in the database."
            )

        new_value.extends_version.connect(ig_versions[0])

        return new_value

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        *,
        root: DataModelIGRoot,
        library: Library,
        relationship: VersionRelationship,
        value: MasterModelValue,
    ) -> MasterModelAR:
        return MasterModelAR.from_repository_values(
            ig_uid=root.uid,
            master_model_vo=MasterModelVO.from_repository_values(
                ig_uid=root.uid,
                ig_version_number=relationship.version,
                name=value.name,
                version_number=None,
            ),
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=(lambda _: library.is_editable),
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
        )

    def _maintain_parameters(
        self,
        versioned_object: MasterModelAR,
        root: DataModelIGRoot,
        value: MasterModelValue,
    ) -> None:
        pass
