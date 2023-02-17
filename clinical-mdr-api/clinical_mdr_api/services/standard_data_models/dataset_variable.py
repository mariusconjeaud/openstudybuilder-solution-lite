from clinical_mdr_api.domain_repositories.standard_data_models.dataset_variable_repository import (
    DatasetVariableRepository,
)
from clinical_mdr_api.models.standard_data_models.dataset_variable import (
    DatasetVariable,
)
from clinical_mdr_api.services.standard_data_models.standard_data_models_generic import (
    StandardDataModelsGenericService,
)


class DatasetVariableService(StandardDataModelsGenericService):
    repository_interface = DatasetVariableRepository
    api_model_class = DatasetVariable
