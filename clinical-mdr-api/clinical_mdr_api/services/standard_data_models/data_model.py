from pydantic import BaseModel

from clinical_mdr_api.domain.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.domain_repositories.standard_data_models.data_model_repository import (
    DataModelRepository,
)
from clinical_mdr_api.models.standard_data_models.data_model import DataModel
from clinical_mdr_api.services.neomodel_ext_generic import (
    NeomodelExtGenericService,
    _AggregateRootType,
)


class DataModelService(NeomodelExtGenericService):
    repository_interface = DataModelRepository
    api_model_class = DataModel
    version_class = None

    def _create_aggregate_root(
        self, item_input: BaseModel, library: LibraryVO
    ) -> _AggregateRootType:
        pass

    def _edit_aggregate(
        self, item: _AggregateRootType, item_edit_input: BaseModel
    ) -> _AggregateRootType:
        pass

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: _AggregateRootType
    ) -> BaseModel:
        pass
