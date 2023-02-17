from clinical_mdr_api.domain_repositories.models._utils import CustomNodeSet
from clinical_mdr_api.domain_repositories.models.standard_data_model import (
    DatasetVariableRoot,
)
from clinical_mdr_api.domain_repositories.standard_data_models.standards_generic_repository import (
    StandardsGenericRepository,
)
from clinical_mdr_api.models.standard_data_models.dataset_variable import (
    DatasetVariable,
)


class DatasetVariableRepository(StandardsGenericRepository):

    root_class = DatasetVariableRoot
    return_model = DatasetVariable

    def get_neomodel_extension_query(self) -> CustomNodeSet:
        return DatasetVariableRoot.nodes.fetch_relations(
            # remove comment when relationship to Library will be added
            # "has_library",
            "has_dataset_variable",
            "has_latest_value__has_dataset_variable",
            "has_latest_value__implements_class_variable",
        ).fetch_optional_relations_into_one_variable(
            {
                "latest_draft": "latest_version",
                "latest_final": "latest_version",
                "latest_retired": "latest_version",
            }
        )
