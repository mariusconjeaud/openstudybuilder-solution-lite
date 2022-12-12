from abc import ABC
from typing import Optional, Sequence

from neomodel import db
from pydantic import BaseModel

from clinical_mdr_api import exceptions
from clinical_mdr_api.exceptions import ValidationException
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._meta_repository import MetaRepository


class StandardDataModelsGenericService(ABC):
    object_name: str
    _repos: MetaRepository
    user_initials: Optional[str]
    repository_interface: type
    api_model_class: BaseModel

    def __init__(self, user: Optional[str] = None):
        self.user_initials = user if user is not None else "TODO user initials"
        self._repos = MetaRepository(self.user_initials)

    def __del__(self):
        self._repos.close()

    @property
    def repository(self):
        assert self._repos is not None
        return self.repository_interface()

    @db.transaction
    def get_all_standards(
        self,
        sort_by: Optional[dict] = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: Optional[dict] = None,
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
        total_count: bool = False,
        **kwargs,
    ) -> GenericFilteringReturn[BaseModel]:

        try:
            items, total_count = self.repository.find_all(
                total_count=total_count,
                sort_by=sort_by,
                filter_by=filter_by,
                filter_operator=filter_operator,
                page_number=page_number,
                page_size=page_size,
                **kwargs,
            )
        except ValueError as e:
            raise exceptions.ValidationException(e)

        all_concepts = GenericFilteringReturn.create(items, total_count)

        return all_concepts

    def get_distinct_values_for_header(
        self,
        field_name: str,
        search_string: Optional[str] = "",
        filter_by: Optional[dict] = None,
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
        result_count: int = 10,
        **kwargs,
    ) -> Sequence:

        header_values = self.repository.get_distinct_headers(
            field_name=field_name,
            search_string=search_string,
            filter_by=filter_by,
            filter_operator=filter_operator,
            result_count=result_count,
            **kwargs,
        )

        return header_values

    @db.transaction
    def get_by_uid(
        self,
        uid: str,
    ):
        item = self.repository.find_by_uid(uid=uid)
        if len(item) == 0:
            raise exceptions.NotFoundException(
                f"{self.api_model_class.__class__} with uid {uid} does not exist."
            )
        if len(item) > 1:
            raise ValidationException(
                f"Returned more than one {self.api_model_class.__class__} with uid {uid}"
            )
        return self.api_model_class.from_orm(item[0])
