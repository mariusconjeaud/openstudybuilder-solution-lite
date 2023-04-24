from clinical_mdr_api.domain_repositories.models._utils import (
    LATEST_VERSION_ORDER_BY,
    CustomNodeSet,
)
from clinical_mdr_api.domain_repositories.models.standard_data_model import (
    DataModelRoot,
)
from clinical_mdr_api.domain_repositories.neomodel_ext_item_repository import (
    NeomodelExtBaseRepository,
)
from clinical_mdr_api.models.standard_data_models.data_model import DataModel


class DataModelRepository(NeomodelExtBaseRepository):
    root_class = DataModelRoot
    return_model = DataModel

    def get_neomodel_extension_query(self) -> CustomNodeSet:
        return (
            DataModelRoot.nodes.fetch_relations(
                "has_library",
                "has_latest_value",
            )
            .fetch_optional_relations_and_collect("has_latest_value__implements")
            .fetch_optional_single_relation_of_type(
                {
                    "has_version": ("latest_version", LATEST_VERSION_ORDER_BY),
                }
            )
        )
