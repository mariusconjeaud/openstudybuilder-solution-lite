from clinical_mdr_api.domain_repositories.standard_data_models.class_variable_repository import (
    ClassVariableRepository,
)
from clinical_mdr_api.models.standard_data_models.class_variable import ClassVariable
from clinical_mdr_api.services.standard_data_models.standard_data_models_generic import (
    StandardDataModelsGenericService,
)


class ClassVariableService(StandardDataModelsGenericService):
    repository_interface = ClassVariableRepository
    api_model_class = ClassVariable
