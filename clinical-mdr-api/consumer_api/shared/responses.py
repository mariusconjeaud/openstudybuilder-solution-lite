import datetime
from typing import Generic, TypeVar

from fastapi import Request
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from requests.utils import requote_uri

from consumer_api.shared import config
from consumer_api.shared.common import urlencode_link

T = TypeVar("T")


class ErrorResponse(BaseModel):
    type: str = Field(..., description="Exception class.")
    message: str = Field(..., description="More information about the error.")
    time: datetime.datetime = Field(
        ..., description="The point in time when the error occurred."
    )
    path: str = Field(..., description="The url/path of the request.")
    method: str = Field(..., description="The HTTP method of the request.")

    def __init__(self, request: Request, exception: Exception, **data) -> None:
        super().__init__(
            type=type(exception).__name__,
            message=str(getattr(exception, "msg", None) or exception),
            time=datetime.datetime.now(datetime.UTC).strftime(config.DATE_TIME_FORMAT),
            path=str(request.url),
            method=request.method,
            **data,
        )


class PaginatedResponse(GenericModel, Generic[T]):
    """
    Paginated response model
    """

    self: str = Field(..., description="Pagination link pointing to the current page")
    prev: str = Field(..., description="Pagination link pointing to the previous page")
    next: str = Field(..., description="Pagination link pointing to the next page")
    items: list[T] = Field(..., description="List of items")

    @classmethod
    def from_input(
        cls,
        request: Request,
        sort_by: str,
        sort_order: str,
        page_size: int,
        page_number: int,
        items: list[T],
        query_param_names: list[str] | None = None,
    ):
        path = request.url.path

        # Extract query parameters not related to sorting/pagination from the request
        query_params = ""
        if query_param_names:
            for query_param_name in query_param_names:
                query_param_val = request.query_params.get(query_param_name)
                if query_param_val:
                    query_params = (
                        f"{query_params}{query_param_name}={query_param_val}&"
                    )
        query_params = requote_uri(query_params)

        prev_page_number = page_number - 1 if page_number > 1 else 1

        self_link = f"{path}?{query_params}sort_by={sort_by}&sort_order={sort_order}&page_size={page_size}&page_number={page_number}"
        prev_link = f"{path}?{query_params}sort_by={sort_by}&sort_order={sort_order}&page_size={page_size}&page_number={prev_page_number}"
        next_link = f"{path}?{query_params}sort_by={sort_by}&sort_order={sort_order}&page_size={page_size}&page_number={page_number+1}"

        return cls(
            self=urlencode_link(self_link),
            prev=urlencode_link(prev_link),
            next=urlencode_link(next_link),
            items=items,
        )
