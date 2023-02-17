from clinical_mdr_api.domain_repositories.models._utils import CustomNodeSet
from clinical_mdr_api.domain_repositories.models.standard_data_model import (
    ClassVariableRoot,
)
from clinical_mdr_api.domain_repositories.standard_data_models.standards_generic_repository import (
    StandardsGenericRepository,
)
from clinical_mdr_api.models.standard_data_models.class_variable import ClassVariable


class ClassVariableRepository(StandardsGenericRepository):

    root_class = ClassVariableRoot
    return_model = ClassVariable

    def get_neomodel_extension_query(self) -> CustomNodeSet:
        return (
            ClassVariableRoot.nodes.fetch_relations(
                # remove comment when relationship to Library will be added
                # "has_library",
                "has_class_variable",
                "has_latest_value__has_class_variable",
            )
            .fetch_optional_relations("has_latest_value__implements_class_variable")
            .fetch_optional_relations_into_one_variable(
                {
                    "latest_draft": "latest_version",
                    "latest_final": "latest_version",
                    "latest_retired": "latest_version",
                }
            )
        )
