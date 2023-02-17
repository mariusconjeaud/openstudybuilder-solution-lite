from typing import Any, List, Optional

from fastapi import APIRouter, Body, Path, Query
from pydantic.types import Json

from clinical_mdr_api import config
from clinical_mdr_api.models import (
    OdmForm,
    OdmFormActivityGroupPostInput,
    OdmFormItemGroupPostInput,
    OdmFormPatchInput,
    OdmFormPostInput,
)
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.models.odm_common_models import (
    OdmElementWithParentUid,
    OdmVendorRelationPostInput,
)
from clinical_mdr_api.models.utils import CustomPage
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.routers import _generic_descriptions
from clinical_mdr_api.services.odm_forms import OdmFormService

router = APIRouter()

# Argument definitions
OdmFormUID = Path(None, description="The unique id of the ODM Form.")


@router.get(
    "",
    summary="Return every variable related to the selected status and version of the ODM Forms",
    description="",
    response_model=CustomPage[OdmForm],
    status_code=200,
    responses={500: {"model": ErrorResponse, "description": "Internal Server Error"}},
)
def get_all_odm_forms(
    library: Optional[str] = Query(None),
    sort_by: Json = Query(None, description=_generic_descriptions.SORT_BY),
    page_number: Optional[int] = Query(
        1, ge=1, description=_generic_descriptions.PAGE_NUMBER
    ),
    page_size: Optional[int] = Query(
        config.DEFAULT_PAGE_SIZE, ge=0, description=_generic_descriptions.PAGE_SIZE
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
):
    odm_form_service = OdmFormService()
    results = odm_form_service.get_all_concepts(
        library=library,
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
    description="""Allowed parameters include : field name for which to get possible
    values, search string to provide filtering for the field name, additional filters to apply on other fields""",
    response_model=List[Any],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Invalid field name specified",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_distinct_values_for_header(
    library_name: Optional[str] = Query(None),
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
    odm_form_service = OdmFormService()
    return odm_form_service.get_distinct_values_for_header(
        library=library_name,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/templates",
    summary="Get all ODM Forms that belongs to an ODM Template",
    description="",
    response_model=List[OdmElementWithParentUid],
    status_code=200,
    responses={500: {"model": ErrorResponse, "description": "Internal Server Error"}},
)
def get_odm_form_that_belongs_to_template():
    odm_form_service = OdmFormService()
    return odm_form_service.get_forms_that_belongs_to_template()


@router.get(
    "/{uid}",
    summary="Get details on a specific ODM Form (in a specific version)",
    description="",
    response_model=OdmForm,
    status_code=200,
    responses={500: {"model": ErrorResponse, "description": "Internal Server Error"}},
)
def get_odm_form(uid: str = OdmFormUID):
    odm_form_service = OdmFormService()
    return odm_form_service.get_by_uid(uid=uid)


@router.get(
    "/{uid}/relationships",
    summary="Get UIDs of a specific ODM Form's relationships",
    description="",
    response_model=dict,
    status_code=200,
    responses={500: {"model": ErrorResponse, "description": "Internal Server Error"}},
)
def get_active_relationships(uid: str = OdmFormUID):
    odm_form_service = OdmFormService()
    return odm_form_service.get_active_relationships(uid=uid)


@router.get(
    "/{uid}/versions",
    summary="List version history for ODM Form",
    description="""
State before:
 - uid must exist.

Business logic:
 - List version history for ODM Forms.
 - The returned versions are ordered by start_date descending (newest entries first).

State after:
 - No change

Possible errors:
 - Invalid uid.
    """,
    response_model=List[OdmForm],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Form with the specified 'uid' wasn't found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_odm_form_versions(uid: str = OdmFormUID):
    odm_form_service = OdmFormService()
    return odm_form_service.get_version_history(uid=uid)


@router.post(
    "",
    summary="Creates a new Form in 'Draft' status with version 0.1",
    description="",
    response_model=OdmForm,
    status_code=201,
    responses={
        201: {"description": "Created - The ODM Form was successfully created."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The library does not exist.\n"
            "- The library does not allow to add new items.\n",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def create_odm_form(
    odm_form_create_input: OdmFormPostInput = Body(None, description=""),
):
    odm_form_service = OdmFormService()

    return odm_form_service.create_with_relations(concept_input=odm_form_create_input)


@router.patch(
    "/{uid}",
    summary="Update ODM Form",
    description="",
    response_model=OdmForm,
    status_code=200,
    responses={
        200: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Form is not in draft status.\n"
            "- The ODM Form had been in 'Final' status before.\n"
            "- The library does not allow to edit draft versions.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Form with the specified 'uid' wasn't found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def edit_odm_form(
    uid: str = OdmFormUID,
    odm_form_edit_input: OdmFormPatchInput = Body(None, description=""),
):
    odm_form_service = OdmFormService()
    return odm_form_service.update_with_relations(
        uid=uid, concept_edit_input=odm_form_edit_input
    )


@router.post(
    "/{uid}/versions",
    summary=" Create a new version of ODM Form",
    description="""
State before:
 - uid must exist and the ODM Form must be in status Final.

Business logic:
- The ODM Form is changed to a draft state.

State after:
 - ODM Form changed status to Draft and assigned a new minor version number.
 - Audit trail entry must be made with action of creating a new draft version.

Possible errors:
 - Invalid uid or status not Final.
""",
    response_model=OdmForm,
    status_code=201,
    responses={
        201: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The library does not allow to create ODM Forms.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - Reasons include e.g.: \n"
            "- The ODM Form is not in final status.\n"
            "- The ODM Form with the specified 'uid' could not be found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def create_odm_form_version(uid: str = OdmFormUID):
    odm_form_service = OdmFormService()
    return odm_form_service.create_new_version(uid=uid)


@router.post(
    "/{uid}/approvals",
    summary="Approve draft version of ODM Form",
    description="",
    response_model=OdmForm,
    status_code=201,
    responses={
        201: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Form is not in draft status.\n"
            "- The library does not allow to approve ODM Form.\n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Form with the specified 'uid' wasn't found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def approve_odm_form(uid: str = OdmFormUID):
    odm_form_service = OdmFormService()
    return odm_form_service.approve(uid=uid)


@router.delete(
    "/{uid}/activations",
    summary=" Inactivate final version of ODM Form",
    description="",
    response_model=OdmForm,
    status_code=200,
    responses={
        200: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Form is not in final status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Form with the specified 'uid' could not be found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def inactivate_odm_form(uid: str = OdmFormUID):
    odm_form_service = OdmFormService()
    return odm_form_service.inactivate_final(uid=uid)


@router.post(
    "/{uid}/activations",
    summary="Reactivate retired version of a ODM Form",
    description="",
    response_model=OdmForm,
    status_code=200,
    responses={
        200: {"description": "OK."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Form is not in retired status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Form with the specified 'uid' could not be found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def reactivate_odm_form(uid: str = OdmFormUID):
    odm_form_service = OdmFormService()
    return odm_form_service.reactivate_retired(uid=uid)


@router.post(
    "/{uid}/activity-groups",
    summary="Adds activity groups to the ODM Form.",
    description="",
    response_model=OdmForm,
    status_code=201,
    responses={
        201: {
            "description": "Created - The activity groups were successfully added to the ODM Form."
        },
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The activity groups with the specified 'uid' wasn't found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def add_activity_groups_to_odm_form(
    uid: str = OdmFormUID,
    override: bool = Query(
        False,
        description="If true, all existing activity group relationships will be replaced with the provided activity group relationships.",
    ),
    odm_form_activity_group_post_input: List[OdmFormActivityGroupPostInput] = Body(
        None, description=""
    ),
):
    odm_form_service = OdmFormService()
    return odm_form_service.add_activity_groups(
        uid=uid,
        odm_form_activity_group_post_input=odm_form_activity_group_post_input,
        override=override,
    )


@router.post(
    "/{uid}/item-groups",
    summary="Adds item groups to the ODM Form.",
    description="",
    response_model=OdmForm,
    status_code=201,
    responses={
        201: {
            "description": "Created - The item groups were successfully added to the ODM Form."
        },
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The item groups with the specified 'uid' wasn't found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def add_item_groups_to_odm_form(
    uid: str = OdmFormUID,
    override: bool = Query(
        False,
        description="If true, all existing item group relationships will be replaced with the provided item group relationships.",
    ),
    odm_form_item_group_post_input: List[OdmFormItemGroupPostInput] = Body(
        None, description=""
    ),
):
    odm_form_service = OdmFormService()
    return odm_form_service.add_item_groups(
        uid=uid,
        odm_form_item_group_post_input=odm_form_item_group_post_input,
        override=override,
    )


@router.post(
    "/{uid}/vendor-elements",
    summary="Adds ODM Vendor Elements to the ODM Form.",
    description="",
    response_model=OdmForm,
    status_code=201,
    responses={
        201: {
            "description": "Created - The ODM Vendor Elements were successfully added to the ODM Form."
        },
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Vendor Elements with the specified 'uid' wasn't found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def add_vendor_elements_to_odm_form(
    uid: str = OdmFormUID,
    override: bool = Query(
        False,
        description="If true, all existing ODM Vendor Element relationships will be replaced with the provided ODM Vendor Element relationships.",
    ),
    odm_vendor_relation_post_input: List[OdmVendorRelationPostInput] = Body(
        None, description=""
    ),
):
    odm_form_service = OdmFormService()
    return odm_form_service.add_vendor_elements(
        uid=uid,
        odm_vendor_relation_post_input=odm_vendor_relation_post_input,
        override=override,
    )


@router.post(
    "/{uid}/vendor-attributes",
    summary="Adds ODM Vendor Attributes to the ODM Form.",
    description="",
    response_model=OdmForm,
    status_code=201,
    responses={
        201: {
            "description": "Created - The ODM Vendor Attributes were successfully added to the ODM Form."
        },
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Vendor Attributes with the specified 'uid' wasn't found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def add_vendor_attributes_to_odm_form(
    uid: str = OdmFormUID,
    override: bool = Query(
        False,
        description="""If true, all existing ODM Vendor Attribute relationships will
        be replaced with the provided ODM Vendor Attribute relationships.""",
    ),
    odm_vendor_relation_post_input: List[OdmVendorRelationPostInput] = Body(
        None, description=""
    ),
):
    odm_form_service = OdmFormService()
    return odm_form_service.add_vendor_attributes(
        uid=uid,
        odm_vendor_relation_post_input=odm_vendor_relation_post_input,
        override=override,
    )


@router.post(
    "/{uid}/vendor-element-attributes",
    summary="Adds ODM Vendor Element attributes to the ODM Form.",
    description="",
    response_model=OdmForm,
    status_code=201,
    responses={
        201: {
            "description": "Created - The ODM Vendor Element attributes were successfully added to the ODM Form."
        },
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The ODM Vendor Element attributes with the specified 'uid' wasn't found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def add_vendor_element_attributes_to_odm_form(
    uid: str = OdmFormUID,
    override: bool = Query(
        False,
        description="""If true, all existing ODM Vendor Element attribute relationships
        will be replaced with the provided ODM Vendor Element attribute relationships.""",
    ),
    odm_vendor_relation_post_input: List[OdmVendorRelationPostInput] = Body(
        None, description=""
    ),
):
    odm_form_service = OdmFormService()
    return odm_form_service.add_vendor_element_attributes(
        uid=uid,
        odm_vendor_relation_post_input=odm_vendor_relation_post_input,
        override=override,
    )


@router.delete(
    "/{uid}",
    summary="Delete draft version of ODM Form",
    description="",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The ODM Form was successfully deleted."},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The ODM Form is not in draft status.\n"
            "- The ODM Form was already in final state or is in use.\n"
            "- The library does not allow to delete ODM Form.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - An ODM Form with the specified 'uid' could not be found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def delete_odm_form(uid: str = OdmFormUID):
    odm_form_service = OdmFormService()
    odm_form_service.soft_delete(uid=uid)
