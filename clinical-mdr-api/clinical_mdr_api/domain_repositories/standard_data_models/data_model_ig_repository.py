from clinical_mdr_api.domain_repositories.models._utils import (
    LATEST_VERSION_ORDER_BY,
    CustomNodeSet,
)
from clinical_mdr_api.domain_repositories.models.standard_data_model import (
    DataModelIGRoot,
)
from clinical_mdr_api.domain_repositories.neomodel_ext_item_repository import (
    NeomodelExtBaseRepository,
)
from clinical_mdr_api.models.standard_data_models.data_model_ig import DataModelIG


class DataModelIGRepository(NeomodelExtBaseRepository):
    root_class = DataModelIGRoot
    return_model = DataModelIG

    def get_neomodel_extension_query(self) -> CustomNodeSet:
        return (
            DataModelIGRoot.nodes.fetch_relations(
                "has_library",
                "has_latest_value",
            )
            .fetch_optional_relations("has_latest_value__implements")
            .fetch_optional_single_relation_of_type(
                {
                    "has_version": ("latest_version", LATEST_VERSION_ORDER_BY),
                }
            )
        )
