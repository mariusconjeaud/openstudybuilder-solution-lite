"""ActivityItem hierarchies router."""
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, Path, Query, Response, status
from pydantic.types import Json
from starlette.requests import Request

from clinical_mdr_api import config
from clinical_mdr_api.models.biomedical_concepts.activity_item import (
    ActivityItem,
    ActivityItemCreateInput,
    ActivityItemEditInput,
)
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.models.utils import CustomPage
from clinical_mdr_api.oauth import get_current_user_id
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.routers import _generic_descriptions, decorators
from clinical_mdr_api.services.biomedical_concepts.activity_item import (
    ActivityItemService,
)

router = APIRouter()

ActivityItemUID = Path(None, description="The unique id of the ActivityItem")


@router.get(
    "",
    summary="List all activity items (for a given library)",
    description=f"""
State before:
 - The library must exist (if specified)

Business logic:
 - List all activity items in their latest version, including properties derived from connected activity item class,
 controlled terminology terms and unit definitions.

State after:
 - No change

Possible errors:
 - Invalid library name specified.

{_generic_descriptions.DATA_EXPORTS_HEADER}
""",
    response_model=CustomPage[ActivityItem],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.allow_exports(
    {
        "defaults": ["uid", "name", "start_date", "status", "version"],
        "formats": [
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/xml",
            "application/json",
        ],
    }
)
# pylint: disable=unused-argument
def get_activity_items(
    request: Request,  # request is actually required by the allow_exports decorator
    sort_by: Json = Query(None, description=_generic_descriptions.SORT_BY),
    page_number: Optional[int] = Query(
        1, ge=1, description=_generic_descriptions.PAGE_NUMBER
    ),
    page_size: Optional[int] = Query(
        config.DEFAULT_PAGE_SIZE,
        ge=0,
        le=config.MAX_PAGE_SIZE,
        description=_generic_descriptions.PAGE_SIZE,
    ),
    filters: Optional[Json] = Query(
        None,
        description=_generic_descriptions.FILTERS,
        example=_generic_descriptions.FILTERS_EXAMPLE,
    ),
    operator: Optional[str] = Query("and", description=_generic_descriptions.OPERATOR),
    total_count: Optional[bool] = Query(
        False, description=_generic_descriptions.TOTAL_COUNT
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    activity_item_service = ActivityItemService(user=current_user_id)
    results = activity_item_service.get_all_items(
        sort_by=sort_by,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
    )
    return CustomPage.create(
        items=results.items, total=results.total_count, page=page_number, size=page_size
    )


@router.get(
    "/headers",
    summary="Returns possible values from the database for a given header",
    description="Allowed parameters include : field name for which to get possible values, "
    "search string to provide filtering for the field name, additional filters to apply on other fields",
    response_model=List[Any],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Invalid field name specified",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_distinct_values_for_header(
    current_user_id: str = Depends(get_current_user_id),
    field_name: str = Query(..., description=_generic_descriptions.HEADER_FIELD_NAME),
    search_string: Optional[str] = Query(
        "", description=_generic_descriptions.HEADER_SEARCH_STRING
    ),
    filters: Optional[Json] = Query(
        None,
        description=_generic_descriptions.FILTERS,
        example=_generic_descriptions.FILTERS_EXAMPLE,
    ),
    operator: Optional[str] = Query("and", description=_generic_descriptions.OPERATOR),
    result_count: Optional[int] = Query(
        10, description=_generic_descriptions.HEADER_RESULT_COUNT
    ),
):
    activity_item_service = ActivityItemService(user=current_user_id)
    return activity_item_service.get_distinct_values_for_header(
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/{uid}",
    summary="Get details on a specific activity item",
    description="""
State before:
 - an activity item with uid must exist.

State after:
 - No change

Possible errors:
 - ActivityItem not found
 """,
    response_model=ActivityItem,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_activity_item(
    uid: str = ActivityItemUID,
    current_user_id: str = Depends(get_current_user_id),
):
    activity_item_service = ActivityItemService(user=current_user_id)
    return activity_item_service.get_by_uid(uid=uid)


@router.get(
    "/{uid}/versions",
    summary="List version history for activity items",
    description="""
State before:
 - uid must exist.

Business logic:
 - List version history for activity items.
 - The returned versions are ordered by start_date descending (newest entries first).

State after:
 - No change

Possible errors:
 - Invalid uid.
    """,
    response_model=List[ActivityItem],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The activity with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_versions(
    uid: str = ActivityItemUID,
    current_user_id: str = Depends(get_current_user_id),
):
    activity_item_service = ActivityItemService(user=current_user_id)
    return activity_item_service.get_version_history(uid=uid)


@router.post(
    "",
    summary="Creates new activity item.",
    description="""
State before:
 - The specified library allows creation of concepts (the 'is_editable' property of the library needs to be true).

Business logic:
 - New node is created for the activity item with the set properties.
 - relationships to specified activity item class is created (as in the model) and optional relationships
 to controlled terminology term and unit definition are created.
 - The status of the new created version will be automatically set to 'Draft'.
 - The 'version' property of the new version will be automatically set to 0.1.
 - The 'change_description' property will be set automatically to 'Initial version'.

State after:
 - ActivityItem is created in status Draft and assigned an initial minor version number as 0.1.
 - The relationship between ActivityItem and ActivityItem is created.
 - Audit trail entry must be made with action of creating new Draft version.

Possible errors:
 - Invalid library or activity item class, control terminology, unit definition uid specified.
""",
    response_model=ActivityItem,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        201: {"description": "Created - The activity item was successfully created."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The library does not exist.\n"
            "- The library does not allow to add new items.\n",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def create(
    activity_item_input: ActivityItemCreateInput = Body(description=""),
    current_user_id: str = Depends(get_current_user_id),
):
    activity_item_service = ActivityItemService(user=current_user_id)
    return activity_item_service.create(item_input=activity_item_input)


@router.patch(
    "/{uid}",
    summary="Update activity item",
    description="""
State before:
 - uid must exist and activity item must exist in status draft.
 - The activity item must belongs to a library that allows deleting (the 'is_editable' property of the library needs to be true).

Business logic:
 - If activity item exist in status draft then attributes are updated.
- If the linked activity item class, ct terms, unit definition are updated, the relationships are updated to point 
to the update node.

State after:
 - attributes are updated for the item.
 - Audit trail entry must be made with update of attributes.

Possible errors:
 - Invalid uid.

""",
    response_model=ActivityItem,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        200: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The activity item is not in draft status.\n"
            "- The activity item had been in 'Final' status before.\n"
            "- The library does not allow to edit draft versions.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The activity item with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def edit(
    uid: str = ActivityItemUID,
    activity_item_input: ActivityItemEditInput = Body(description=""),
    current_user_id: str = Depends(get_current_user_id),
):
    activity_item_service = ActivityItemService(user=current_user_id)
    return activity_item_service.edit_draft(
        uid=uid, item_edit_input=activity_item_input
    )


@router.post(
    "/{uid}/versions",
    summary=" Create a new version of activity item",
    description="""
State before:
 - uid must exist and the activity item must be in status Final.

Business logic:
- The activity item is changed to a draft state.

State after:
 - ActivityItem changed status to Draft and assigned a new minor version number.
 - Audit trail entry must be made with action of creating a new draft version.

Possible errors:
 - Invalid uid or status not Final.
""",
    response_model=ActivityItem,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        201: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The library does not allow to create activity item classes.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Reasons include e.g.: \n"
            "- The activity item is not in final status.\n"
            "- The activity item with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def new_version(
    uid: str = ActivityItemUID,
    current_user_id: str = Depends(get_current_user_id),
):
    activity_item_service = ActivityItemService(user=current_user_id)
    return activity_item_service.create_new_version(uid=uid)


@router.post(
    "/{uid}/approvals",
    summary="Approve draft version of activity item",
    description="""
State before:
 - uid must exist and activity item must be in status Draft.

Business logic:
 - The latest 'Draft' version will remain the same as before.
 - The status of the new approved version will be automatically set to 'Final'.
 - The 'version' property of the new version will be automatically set to the version of the latest 'Final' version increased by +1.0.
 - The 'change_description' property will be set automatically 'Approved version'.

State after:
 - ActivityItem changed status to Final and assigned a new major version number.
 - Audit trail entry must be made with action of approving to new Final version.

Possible errors:
 - Invalid uid or status not Draft.
    """,
    response_model=ActivityItem,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        201: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The activity item is not in draft status.\n"
            "- The library does not allow to approve activity item.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The activity item with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def approve(
    uid: str = ActivityItemUID,
    current_user_id: str = Depends(get_current_user_id),
):
    activity_item_service = ActivityItemService(user=current_user_id)
    return activity_item_service.approve(uid=uid)


@router.delete(
    "/{uid}/activations",
    summary=" Inactivate final version of activity item",
    description="""
State before:
 - uid must exist and activity item must be in status Final.

Business logic:
 - The latest 'Final' version will remain the same as before.
 - The status will be automatically set to 'Retired'.
 - The 'change_description' property will be set automatically.
 - The 'version' property will remain the same as before.

State after:
 - Activity item changed status to Retired.
 - Audit trail entry must be made with action of inactivating to retired version.

Possible errors:
 - Invalid uid or status not Final.
    """,
    response_model=ActivityItem,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        200: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "BusinessLogicException - Reasons include e.g.: \n"
            "- The activity itm is not in final status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The activity item with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def inactivate(
    uid: str = ActivityItemUID,
    current_user_id: str = Depends(get_current_user_id),
):
    activity_item_service = ActivityItemService(user=current_user_id)
    return activity_item_service.inactivate_final(uid=uid)


@router.post(
    "/{uid}/activations",
    summary="Reactivate retired version of a activity item",
    description="""
State before:
 - uid must exist and activity item must be in status Retired.

Business logic:
 - The latest 'Retired' version will remain the same as before.
 - The status will be automatically set to 'Final'.
 - The 'change_description' property will be set automatically.
 - The 'version' property will remain the same as before.

State after:
 - ActivityItem changed status to Final.
 - An audit trail entry must be made with action of reactivating to final version.

Possible errors:
 - Invalid uid or status not Retired.
    """,
    response_model=ActivityItem,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        200: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The activity item is not in retired status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The activity item with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def reactivate(
    uid: str = ActivityItemUID,
    current_user_id: str = Depends(get_current_user_id),
):
    activity_item_service = ActivityItemService(user=current_user_id)
    return activity_item_service.reactivate_retired(uid=uid)


@router.delete(
    "/{uid}",
    summary="Delete draft version of activity item",
    description="""
State before:
 - uid must exist
 - The concept must be in status Draft in a version less then 1.0 (never been approved).
 - The concept must belongs to a library that allows deleting (the 'is_editable' property of the library needs to be true).

Business logic:
 - The draft concept is deleted.

State after:
 - ActivityItem is successfully deleted.

Possible errors:
 - Invalid uid or status not Draft or exist in version 1.0 or above (previously been approved) or not in an editable library.
    """,
    response_model=None,
    status_code=204,
    responses={
        204: {
            "description": "No Content - The activity item was successfully deleted."
        },
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The activity item is not in draft status.\n"
            "- The activity item was already in final state or is in use.\n"
            "- The library does not allow to delete activity item class.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - An activity item with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def delete_activity_item(
    uid: str = ActivityItemUID,
    current_user_id: str = Depends(get_current_user_id),
):
    activity_item_service = ActivityItemService(user=current_user_id)
    activity_item_service.soft_delete(uid=uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
