from clinical_mdr_api.domain_repositories.models._utils import CustomNodeSet
from clinical_mdr_api.domain_repositories.models.standard_data_model import (
    DatasetClassRoot,
)
from clinical_mdr_api.domain_repositories.standard_data_models.standards_generic_repository import (
    StandardsGenericRepository,
)
from clinical_mdr_api.models.standard_data_models.dataset_class import DatasetClass


class DatasetClassRepository(StandardsGenericRepository):

    root_class = DatasetClassRoot
    return_model = DatasetClass

    def get_neomodel_extension_query(self) -> CustomNodeSet:
        return DatasetClassRoot.nodes.fetch_relations(
            # remove comment when relationship to Library will be added
            # "has_library",
            "has_dataset_class",
            "has_latest_value__has_dataset_class",
        ).fetch_optional_relations_into_one_variable(
            {
                "latest_draft": "latest_version",
                "latest_final": "latest_version",
                "latest_retired": "latest_version",
            }
        )
