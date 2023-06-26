from clinical_mdr_api.domain_repositories.library_item_repository import (
    LibraryItemRepositoryImplBase,
    _AggregateRootType,
)
from clinical_mdr_api.domain_repositories.models._utils import (
    LATEST_VERSION_ORDER_BY,
    CustomNodeSet,
)
from clinical_mdr_api.domain_repositories.models.biomedical_concepts import (
    ActivityItemClassRoot,
    ActivityItemRoot,
    ActivityItemValue,
)
from clinical_mdr_api.domain_repositories.models.concepts import UnitDefinitionRoot
from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    CTTermRoot,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.neomodel_ext_item_repository import (
    NeomodelExtBaseRepository,
)
from clinical_mdr_api.domains.biomedical_concepts.activity_item import (
    ActivityItemAR,
    ActivityItemVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.models.biomedical_concepts.activity_item import ActivityItem


class ActivityItemRepository(
    NeomodelExtBaseRepository, LibraryItemRepositoryImplBase[_AggregateRootType]
):
    root_class = ActivityItemRoot
    value_class = ActivityItemValue
    return_model = ActivityItem

    def get_neomodel_extension_query(self) -> CustomNodeSet:
        return (
            ActivityItemRoot.nodes.fetch_relations(
                "has_latest_value",
                "has_library",
                "has_activity_item_class__has_latest_value",
            )
            .fetch_optional_relations(
                "has_latest_value__has_ct_term__has_name_root__has_latest_value",
                "has_latest_value__has_unit_definition__has_latest_value",
            )
            .fetch_optional_single_relation_of_type(
                {
                    "has_version": ("latest_version", LATEST_VERSION_ORDER_BY),
                }
            )
        )

    def _has_data_changed(self, ar: ActivityItemAR, value: ActivityItemValue) -> bool:
        return (
            ar.activity_item_vo.name != value.name
            or ar.activity_item_vo.ct_term_uid != value.has_ct_term.get_or_none()
            or ar.activity_item_vo.unit_definition_uid
            != value.has_unit_definition.get_or_none()
            or ar.activity_item_vo.activity_item_class_uid
            != value.has_version.single().has_activity_item_class.get()
        )

    def _get_or_create_value(
        self, root: ActivityItemRoot, ar: ActivityItemAR
    ) -> ActivityItemValue:
        for itm in root.has_version.all():
            if not self._has_data_changed(ar, itm):
                return itm
        latest_draft = root.latest_draft.get_or_none()
        if latest_draft and not self._has_data_changed(ar, latest_draft):
            return latest_draft
        latest_final = root.latest_final.get_or_none()
        if latest_final and not self._has_data_changed(ar, latest_final):
            return latest_final
        latest_retired = root.latest_retired.get_or_none()
        if latest_retired and not self._has_data_changed(ar, latest_retired):
            return latest_retired
        new_value = ActivityItemValue(
            name=ar.activity_item_vo.name,
        )
        self._db_save_node(new_value)
        activity_item_class = ActivityItemClassRoot.nodes.get_or_none(
            uid=ar.activity_item_vo.activity_item_class_uid
        )
        root.has_activity_item_class.connect(activity_item_class)
        if ar.activity_item_vo.ct_term_uid:
            ct_term_root = CTTermRoot.nodes.get_or_none(
                uid=ar.activity_item_vo.ct_term_uid
            )
            new_value.has_ct_term.connect(ct_term_root)
        if ar.activity_item_vo.unit_definition_uid:
            unit_definition = UnitDefinitionRoot.nodes.get_or_none(
                uid=ar.activity_item_vo.unit_definition_uid
            )
            new_value.has_unit_definition.connect(unit_definition)
        return new_value

    def generate_uid(self) -> str:
        return ActivityItemRoot.get_next_free_uid_and_increment_counter()

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        *,
        root: ActivityItemRoot,
        library: Library,
        relationship: VersionRelationship,
        value: ActivityItemValue,
    ) -> ActivityItemAR:
        activity_item_class = root.has_activity_item_class.get()
        ct_term = value.has_ct_term.get_or_none()
        unit_definition = value.has_unit_definition.get_or_none()
        return ActivityItemAR.from_repository_values(
            uid=root.uid,
            activity_item_vo=ActivityItemVO.from_repository_values(
                name=value.name,
                activity_item_class_uid=activity_item_class.uid,
                activity_item_class_name=activity_item_class.has_latest_value.get_or_none().name,
                ct_term_uid=ct_term.uid if ct_term else None,
                ct_term_name=ct_term.has_name_root.get_or_none()
                .has_latest_value.get_or_none()
                .name
                if ct_term
                else None,
                unit_definition_uid=unit_definition.uid if unit_definition else None,
                unit_definition_name=unit_definition.has_latest_value.get_or_none().name
                if unit_definition
                else None,
            ),
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=(lambda _: library.is_editable),
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
        )

    def _maintain_parameters(
        self,
        versioned_object: _AggregateRootType,
        root: ActivityItemRoot,
        value: ActivityItemValue,
    ) -> None:
        pass
