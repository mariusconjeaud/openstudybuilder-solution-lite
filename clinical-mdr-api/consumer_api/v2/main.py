# RESTful API endpoints used by consumers that want to extract data from StudyBuilder


# from fastapi import APIRouter, Query, Request

# from consumer_api.auth import rbac
# from consumer_api.shared import config
# from consumer_api.shared.responses import PaginatedResponse
# from consumer_api.v2 import db as DB
# from consumer_api.v2 import models

# router = APIRouter()


# GET endpoint to retrieve a list of studies
# @router.get(
#     "/studies",
#     dependencies=[rbac.STUDY_READ],
#     response_model=PaginatedResponse[models.Study],
# )
# async def get_studies(
#     request: Request,
#     sort_by: models.SortByStudies = models.SortByStudies.UID,
#     sort_order: models.SortOrder = models.SortOrder.ASC,
#     page_size: int = Query(
#         config.DEFAULT_PAGE_SIZE,
#         ge=0,
#         le=config.MAX_PAGE_SIZE,
#     ),
#     page_number: int = Query(1, ge=1),
# ):
#     """Get a list of studies"""
#     studies = DB.get_studies(
#         sort_by=sort_by,
#         sort_order=sort_order,
#         page_size=page_size,
#         page_number=page_number,
#     )

#     return PaginatedResponse.from_input(
#         request=request,
#         sort_by=sort_by.value,
#         sort_order=sort_order.value,
#         page_size=page_size,
#         page_number=page_number,
#         items=[models.Study.from_input(study) for study in studies],
#     )
