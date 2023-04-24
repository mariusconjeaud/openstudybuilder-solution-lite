from clinical_mdr_api.domain_repositories.models._utils import (
    LATEST_VERSION_ORDER_BY,
    CustomNodeSet,
)
from clinical_mdr_api.domain_repositories.models.standard_data_model import DatasetRoot
from clinical_mdr_api.domain_repositories.neomodel_ext_item_repository import (
    NeomodelExtBaseRepository,
)
from clinical_mdr_api.models.standard_data_models.dataset import Dataset


class DatasetRepository(NeomodelExtBaseRepository):
    root_class = DatasetRoot
    return_model = Dataset

    def get_neomodel_extension_query(self) -> CustomNodeSet:
        return DatasetRoot.nodes.fetch_relations(
            "has_dataset",
            "has_latest_value__has_dataset",
            "has_latest_value__implements_dataset_class",
        ).fetch_optional_single_relation_of_type(
            {
                "has_version": ("latest_version", LATEST_VERSION_ORDER_BY),
            }
        )
