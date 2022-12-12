from clinical_mdr_api.domain_repositories.standard_data_models.data_model_ig_repository import (
    DataModelIGRepository,
)
from clinical_mdr_api.models.standard_data_models.data_model_ig import DataModelIG
from clinical_mdr_api.services.standard_data_models.standard_data_models_generic import (
    StandardDataModelsGenericService,
)


class DataModelIGService(StandardDataModelsGenericService):
    repository_interface = DataModelIGRepository
    api_model_class = DataModelIG
