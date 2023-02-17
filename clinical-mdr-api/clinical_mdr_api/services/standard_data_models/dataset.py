from clinical_mdr_api.domain_repositories.standard_data_models.dataset_repository import (
    DatasetRepository,
)
from clinical_mdr_api.models.standard_data_models.dataset import Dataset
from clinical_mdr_api.services.standard_data_models.standard_data_models_generic import (
    StandardDataModelsGenericService,
)


class DatasetService(StandardDataModelsGenericService):
    repository_interface = DatasetRepository
    api_model_class = Dataset
