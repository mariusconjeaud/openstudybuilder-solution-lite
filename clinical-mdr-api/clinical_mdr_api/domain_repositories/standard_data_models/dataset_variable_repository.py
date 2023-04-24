from clinical_mdr_api.domain_repositories.models._utils import (
    LATEST_VERSION_ORDER_BY,
    CustomNodeSet,
)
from clinical_mdr_api.domain_repositories.models.standard_data_model import (
    DatasetVariableRoot,
)
from clinical_mdr_api.domain_repositories.neomodel_ext_item_repository import (
    NeomodelExtBaseRepository,
)
from clinical_mdr_api.models.standard_data_models.dataset_variable import (
    DatasetVariable,
)


class DatasetVariableRepository(NeomodelExtBaseRepository):
    root_class = DatasetVariableRoot
    return_model = DatasetVariable

    def get_neomodel_extension_query(self) -> CustomNodeSet:
        return (
            DatasetVariableRoot.nodes.fetch_relations(
                "has_dataset_variable",
                "has_latest_value__has_dataset_variable",
                "has_latest_value__implements_variable",
            )
            .fetch_optional_relations("has_latest_value__has_mapping_target")
            .fetch_optional_single_relation_of_type(
                {
                    "has_version": ("latest_version", LATEST_VERSION_ORDER_BY),
                }
            )
        )
