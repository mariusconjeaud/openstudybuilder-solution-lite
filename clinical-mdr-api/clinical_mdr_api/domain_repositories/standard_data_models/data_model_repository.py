from clinical_mdr_api.domain_repositories.models._utils import CustomNodeSet
from clinical_mdr_api.domain_repositories.models.standard_data_model import (
    DataModelRoot,
)
from clinical_mdr_api.domain_repositories.standard_data_models.standards_generic_repository import (
    StandardsGenericRepository,
)
from clinical_mdr_api.models.standard_data_models.data_model import DataModel


class DataModelRepository(StandardsGenericRepository):

    root_class = DataModelRoot
    return_model = DataModel

    def get_neomodel_extension_query(self) -> CustomNodeSet:
        return (
            DataModelRoot.nodes.fetch_relations(
                "has_library",
                "has_latest_value",
            )
            .fetch_optional_relations_and_collect("has_latest_value__implements")
            .fetch_optional_relations_into_one_variable(
                {
                    "latest_draft": "latest_version",
                    "latest_final": "latest_version",
                    "latest_retired": "latest_version",
                }
            )
        )
