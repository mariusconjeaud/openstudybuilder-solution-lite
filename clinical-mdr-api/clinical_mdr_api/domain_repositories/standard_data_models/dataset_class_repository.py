from clinical_mdr_api.domain_repositories.models._utils import (
    LATEST_VERSION_ORDER_BY,
    CustomNodeSet,
)
from clinical_mdr_api.domain_repositories.models.standard_data_model import (
    DatasetClassRoot,
)
from clinical_mdr_api.domain_repositories.neomodel_ext_item_repository import (
    NeomodelExtBaseRepository,
)
from clinical_mdr_api.models.standard_data_models.dataset_class import DatasetClass


class DatasetClassRepository(NeomodelExtBaseRepository):
    root_class = DatasetClassRoot
    return_model = DatasetClass

    def get_neomodel_extension_query(self) -> CustomNodeSet:
        return (
            DatasetClassRoot.nodes.fetch_relations(
                "has_dataset_class",
                "has_latest_value__has_dataset_class",
            )
            .fetch_optional_relations("has_latest_value__has_parent_class")
            .fetch_optional_single_relation_of_type(
                {
                    "has_version": ("latest_version", LATEST_VERSION_ORDER_BY),
                }
            )
        )
