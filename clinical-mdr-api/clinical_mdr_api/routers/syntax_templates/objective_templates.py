"""Objective templates router."""

from typing import Any, List, Optional, Sequence

from fastapi import APIRouter, Body, Depends, Path, Query, Request, Response
from fastapi import status as fast_api_status
from pydantic.types import Json

from clinical_mdr_api import config, models
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryItemStatus
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.models.syntax_pre_instances.objective_pre_instance import (
    ObjectivePreInstanceCreateInput,
)
from clinical_mdr_api.models.syntax_templates.objective_template import (
    ObjectiveTemplateNameInput,
    ObjectiveTemplateWithCount,
)
from clinical_mdr_api.models.syntax_templates.template_parameter_term import (
    MultiTemplateParameterTerm,
)
from clinical_mdr_api.models.utils import CustomPage
from clinical_mdr_api.oauth import get_current_user_id
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.routers import _generic_descriptions, decorators
from clinical_mdr_api.services.syntax_pre_instances.objective_pre_instances import (
    ObjectivePreInstanceService,
)
from clinical_mdr_api.services.syntax_templates.objective_templates import (
    ObjectiveTemplateService,
)

router = APIRouter()

Service = ObjectiveTemplateService

# Argument definitions
ObjectiveTemplateUID = Path(
    None, description="The unique id of the objective template."
)

PARAMETERS_NOTE = """**Parameters in the 'name' property**:

The 'name' of an objective template may contain parameters, that can - and usually will - be replaced with concrete values once an objective is created out of the objective template.

Parameters are referenced by simple strings in square brackets [] that match existing parameters defined in the MDR repository.

See the *[GET] /parameter-templates/* endpoint for available terms.

The objective template will be linked to those parameters defined in the 'name' property.

You may use an arbitrary number of parameters and you may use the same parameter multiple times within the same objective template 'name'.

*Example*:

name='MORE TESTING of the superiority in the efficacy of [Intervention] with [Activity] and [Activity] in [Timeframe].'

'Intervention', 'Activity' and 'Timeframe' are parameters."""


@router.get(
    "",
    summary="Returns all objective templates in their latest/newest version.",
    description=f"""
Allowed parameters include : filter on fields, sort by field name with sort direction, pagination.

{_generic_descriptions.DATA_EXPORTS_HEADER}
""",
    response_model=CustomPage[models.ObjectiveTemplate],
    status_code=200,
    responses={
        200: {
            "content": {
                "text/csv": {
                    "example": """
"library","uid","name","start_date","end_date","status","version","change_description","user_initials"
"Sponsor","826d80a7-0b6a-419d-8ef1-80aa241d7ac7","First  [ComparatorIntervention]","2020-10-22T10:19:29+00:00",,"Draft","0.1","Initial version","NdSJ"
"""
                },
                "text/xml": {
                    "example": """
                    <?xml version="1.0" encoding="UTF-8" ?><root><data type="list"><item type="dict"><uid type="str">e9117175-918f-489e-9a6e-65e0025233a6</uid><name type="str">Alamakota</name><start_date type="str">2020-11-19T11:51:43.000Z</start_date><status type="str">Draft</status><version type="str">0.2</version><change_description type="str">Test</change_description><user_initials type="str">TODO Initials</user_initials></item></data></root>
"""
                },
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
            }
        },
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "library=library.name",
            "uid",
            "name_plain",
            "name",
            "indications=indications.name",
            "category=categories.name.sponsor_preferred_name",
            "is_confirmatory_testing",
            "start_date",
            "end_date",
            "status",
            "version",
            "change_description",
            "user_initials",
        ],
        "formats": [
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/xml",
            "application/json",
        ],
    }
)
# pylint: disable=unused-argument
def get_objective_templates(
    request: Request,  # request is actually required by the allow_exports decorator
    status: Optional[LibraryItemStatus] = Query(
        None,
        description="If specified, only those objective templates will be returned that are currently in the specified status. "
        "This may be particularly useful if the objective template has "
        "a) a 'Draft' and a 'Final' status or "
        "b) a 'Draft' and a 'Retired' status at the same time "
        "and you are interested in the 'Final' or 'Retired' status.\n"
        "Valid values are: 'Final', 'Draft' or 'Retired'.",
    ),
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
) -> CustomPage[models.ObjectiveTemplate]:
    results = Service(current_user_id).get_all(
        status=status,
        return_study_count=True,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
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
        500: _generic_descriptions.ERROR_500,
    },
)
def get_distinct_values_for_header(
    current_user_id: str = Depends(get_current_user_id),
    status: Optional[LibraryItemStatus] = Query(
        None,
        description="If specified, only those objective templates will be returned that are currently in the specified status. "
        "This may be particularly useful if the objective template has "
        "a) a 'Draft' and a 'Final' status or "
        "b) a 'Draft' and a 'Retired' status at the same time "
        "and you are interested in the 'Final' or 'Retired' status.\n"
        "Valid values are: 'Final', 'Draft' or 'Retired'.",
    ),
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
    return Service(current_user_id).get_distinct_values_for_header(
        status=status,
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.get(
    "/audit-trail",
    summary="",
    description="",
    response_model=CustomPage[models.ObjectiveTemplate],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def retrieve_audit_trail(
    page_number: Optional[int] = Query(
        1, ge=1, description=_generic_descriptions.PAGE_NUMBER
    ),
    page_size: Optional[int] = Query(
        config.DEFAULT_PAGE_SIZE,
        ge=0,
        le=config.MAX_PAGE_SIZE,
        description=_generic_descriptions.PAGE_SIZE,
    ),
    total_count: Optional[bool] = Query(
        False, description=_generic_descriptions.TOTAL_COUNT
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    results = Service(current_user_id).retrieve_audit_trail(
        page_number=page_number, page_size=page_size, total_count=total_count
    )

    return CustomPage.create(
        items=results.items, total=results.total_count, page=page_number, size=page_size
    )


@router.get(
    "/{uid}",
    summary="Returns the latest/newest version of a specific objective template identified by 'uid'.",
    description="""If multiple request query parameters are used, then they need to
    match all at the same time (they are combined with the AND operation).""",
    response_model=ObjectiveTemplateWithCount,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The objective template with the specified 'uid' (and the specified date/time and/or status) wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_objective_template(
    uid: str = ObjectiveTemplateUID,
    return_instantiation_counts: bool = Query(
        False, description="if specified counts data will be returned along object"
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.ObjectiveTemplate:
    return Service(current_user_id).get_by_uid(
        uid=uid, return_instantiation_counts=bool(return_instantiation_counts)
    )


@router.get(
    "/{uid}/versions",
    summary="Returns the version history of a specific objective template identified by 'uid'.",
    description=f"""
The returned versions are ordered by `start_date` descending (newest entries first).

{_generic_descriptions.DATA_EXPORTS_HEADER}
""",
    response_model=List[models.ObjectiveTemplateVersion],
    status_code=200,
    responses={
        200: {
            "content": {
                "text/csv": {
                    "example": """
"library";"uid";"name";"start_date";"end_date";"status";"version";"change_description";"user_initials"
"Sponsor";"826d80a7-0b6a-419d-8ef1-80aa241d7ac7";"First  [ComparatorIntervention]";"2020-10-22T10:19:29+00:00";;"Draft";"0.1";"Initial version";"NdSJ"
"""
                },
                "text/xml": {
                    "example": """
                    <?xml version="1.0" encoding="UTF-8" ?><root><data type="list"><item type="dict"><name type="str">Alamakota</name><start_date type="str">2020-11-19 11:51:43+00:00</start_date><end_date type="str">None</end_date><status type="str">Draft</status><version type="str">0.2</version><change_description type="str">Test</change_description><user_initials type="str">TODO Initials</user_initials></item><item type="dict"><name type="str">Alamakota</name><start_date type="str">2020-11-19 11:51:07+00:00</start_date><end_date type="str">2020-11-19 11:51:43+00:00</end_date><status type="str">Draft</status><version type="str">0.1</version><change_description type="str">Initial version</change_description><user_initials type="str">TODO user initials</user_initials></item></data></root>
"""
                },
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
            }
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The objective template with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "library=library.name",
            "name",
            "change_description",
            "status",
            "version",
            "start_date",
            "end_date",
            "user_initials",
        ],
        "formats": [
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/xml",
            "application/json",
        ],
    }
)
# pylint: disable=unused-argument
def get_objective_template_versions(
    request: Request,  # request is actually required by the allow_exports decorator
    uid: str = ObjectiveTemplateUID,
    current_user_id: str = Depends(get_current_user_id),
):
    return Service(current_user_id).get_version_history(uid=uid)


@router.get(
    "/{uid}/versions/{version}",
    summary="Returns a specific version of a specific objective template identified by 'uid' and 'version'.",
    description="**Multiple versions**:\n\n"
    "Technically, there can be multiple versions of the objective template with the same version number. "
    "This is due to the fact, that the version number remains the same when inactivating or reactivating an objective template "
    "(switching between 'Final' and 'Retired' status). \n\n"
    "In that case the latest/newest representation is returned.",
    response_model=models.ObjectiveTemplate,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The objective template with the specified 'uid' and 'version' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_objective_template_version(
    uid: str = ObjectiveTemplateUID,
    version: str = Path(
        None,
        description="A specific version number of the objective template. "
        "The version number is specified in the following format: \\<major\\>.\\<minor\\> where \\<major\\> and \\<minor\\> are digits.\n"
        "E.g. '0.1', '0.2', '1.0', ...",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    return Service(current_user_id).get_specific_version(uid=uid, version=version)


@router.get(
    "/{uid}/releases",
    summary="List all final versions of a template identified by 'uid', including number of studies using a specific version",
    description="",
    response_model=List[models.ObjectiveTemplate],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The objective template with the specified 'uid' wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_objective_template_releases(
    uid: str = ObjectiveTemplateUID, current_user_id: str = Depends(get_current_user_id)
):
    return Service(current_user_id).get_releases(uid=uid, return_study_count=False)


@router.post(
    "",
    summary="Creates a new objective template in 'Draft' status.",
    description="""This request is only valid if the objective template
* belongs to a library that allows creating (the 'is_editable' property of the library needs to be true).

If the request succeeds:
* The status will be automatically set to 'Draft'.
* The 'change_description' property will be set automatically.
* The 'version' property will be set to '0.1'.
* The objective template will be linked to a library.

"""
    + PARAMETERS_NOTE,
    response_model=models.ObjectiveTemplate,
    status_code=201,
    responses={
        201: {
            "description": "Created - The objective template was successfully created."
        },
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The objective template name is not valid.\n"
            "- The library does not allow to create objective templates.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The library with the specified 'library_name' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def create_objective_template(
    objective_template: models.ObjectiveTemplateCreateInput = Body(
        description="The objective template that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.ObjectiveTemplate:
    return Service(current_user_id).create(objective_template)


@router.patch(
    "/{uid}",
    summary="Updates the objective template identified by 'uid'.",
    description="""This request is only valid if the objective template
* is in 'Draft' status and
* belongs to a library that allows editing (the 'is_editable' property of the library needs to be true). 

If the request succeeds:
* The 'version' property will be increased automatically by +0.1.
* The status will remain in 'Draft'.

Parameters in the 'name' property can only be changed if the objective template has never been approved.
Once the objective template has been approved, only the surrounding text (excluding the parameters) can be changed.

"""
    + PARAMETERS_NOTE,
    response_model=models.ObjectiveTemplate,
    status_code=200,
    responses={
        200: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The objective template is not in draft status.\n"
            "- The objective template name is not valid.\n"
            "- The library does not allow to edit draft versions.\n"
            "- The change of parameters of previously approved objective templates.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The objective template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def edit(
    uid: str = ObjectiveTemplateUID,
    objective_template: models.ObjectiveTemplateEditInput = Body(
        description="The new content of the objective template including the change description.",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.ObjectiveTemplate:
    return Service(current_user_id).edit_draft(uid=uid, template=objective_template)


@router.patch(
    "/{uid}/indexings",
    summary="Updates the indexings of the objective template identified by 'uid'.",
    description="""This request is only valid if the template
    * belongs to a library that allows editing (the 'is_editable' property of the library needs to be true).
    
    This is version independent : it won't trigger a status or a version change.
    """,
    response_model=models.ObjectiveTemplate,
    status_code=200,
    responses={
        200: {
            "description": "No content - The indexings for this template were successfully updated."
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def patch_indexings(
    uid: str = ObjectiveTemplateUID,
    indexings: models.ObjectiveTemplateEditIndexingsInput = Body(
        description="The lists of UIDs for the new indexings to be set, grouped by indexings to be updated.",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.ObjectiveTemplate:
    return Service(current_user_id).patch_indexings(uid=uid, indexings=indexings)


@router.patch(
    "/{uid}/default-parameter-terms",
    summary="Edit the default parameter terms of the objective template identified by 'uid'.",
    description="""This request is only valid if the objective template
* is in 'Draft' status and
* belongs to a library that allows editing (the 'is_editable' property of the library needs to be true). 

If the request succeeds:
* The 'version' property will be increased automatically by +0.1.
* The status will remain in 'Draft'.

This endpoint can be used to either :
* Create a new set of default parameter terms
* Edit an existing set of default parameter terms

""",
    response_model=models.ObjectiveTemplate,
    status_code=200,
    responses={
        200: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The objective template is not in draft status.\n"
            "- The objective template name is not valid.\n"
            "- The library does not allow to edit draft versions.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The objective template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def patch_default_parameter_terms(
    uid: str = ObjectiveTemplateUID,
    set_number: Optional[int] = Body(
        description="Optionally, the set number of the default parameter terms to be patched. If not set, a new set will be created.",
    ),
    default_parameter_terms: Sequence[MultiTemplateParameterTerm] = Body(
        description="The set of default parameter terms.\n"
        "If empty and an existing set_number is passed, the set will be deleted.",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.ObjectiveTemplate:
    return Service(current_user_id).patch_default_parameter_terms(
        uid=uid,
        set_number=set_number,
        default_parameter_terms=default_parameter_terms,
    )


@router.post(
    "/{uid}/versions",
    summary="Creates a new version of the objective template identified by 'uid'.",
    description="""This request is only valid if the objective template
* is in 'Final' or 'Retired' status only (so no latest 'Draft' status exists) and
* belongs to a library that allows editing (the 'is_editable' property of the library needs to be true).

If the request succeeds:
* The latest 'Final' or 'Retired' version will remain the same as before.
* The status of the new version will be automatically set to 'Draft'.
* The 'version' property of the new version will be automatically set to the version of the latest 'Final' or 'Retired' version increased by +0.1.

Parameters in the 'name' property cannot be changed with this request.
Only the surrounding text (excluding the parameters) can be changed.
""",
    response_model=models.ObjectiveTemplate,
    status_code=201,
    responses={
        201: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The objective template is not in final or retired status or has a draft status.\n"
            "- The objective template name is not valid.\n"
            "- The library does not allow to create a new version.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The objective template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def create_new_version(
    uid: str = ObjectiveTemplateUID,
    objective_template: models.ObjectiveTemplateEditInput = Body(
        description="The content of the objective template for the new 'Draft' version including the change description.",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> models.ObjectiveTemplate:
    # return service.create_new_version_of_final_or_retired(uid, objective_template)
    # TODO: do sth not to mislead static code analysis
    return Service(current_user_id).create_new_version(
        uid=uid, template=objective_template
    )


@router.post(
    "/{uid}/approvals",
    summary="Approves the objective template identified by 'uid'.",
    description="""This request is only valid if the objective template
* is in 'Draft' status and
* belongs to a library that allows editing (the 'is_editable' property of the library needs to be true).

If the request succeeds:
* The status will be automatically set to 'Final'.
* The 'change_description' property will be set automatically.
* The 'version' property will be increased automatically to the next major version.
    """,
    response_model=models.ObjectiveTemplate,
    status_code=201,
    responses={
        201: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The objective template is not in draft status.\n"
            "- The library does not allow to approve drafts.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The objective template with the specified 'uid' could not be found.",
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflict - there are objectives created from template and cascade is false",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def approve(
    uid: str = ObjectiveTemplateUID,
    cascade: bool = False,
    current_user_id: str = Depends(get_current_user_id),
):
    """
    Approves objective template. Fails with 409 if there is some objectives created
    from this template and cascade is false
    """
    if not cascade:
        return Service(current_user_id).approve(uid=uid)
    return Service(current_user_id).approve_cascade(uid=uid)


@router.delete(
    "/{uid}/activations",
    summary="Inactivates/deactivates the objective template identified by 'uid' and its Pre-Instances.",
    description="""This request is only valid if the objective template
* is in 'Final' status only (so no latest 'Draft' status exists).

If the request succeeds:
* The status will be automatically set to 'Retired'.
* The 'change_description' property will be set automatically. 
* The 'version' property will remain the same as before.
    """,
    response_model=models.ObjectiveTemplate,
    status_code=200,
    responses={
        200: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The objective template is not in final status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The objective template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def inactivate(
    uid: str = ObjectiveTemplateUID, current_user_id: str = Depends(get_current_user_id)
) -> models.ObjectiveTemplate:
    # return service.inactivate_final(uid)
    # TODO: do sth to make static code analysis work for this code
    return Service(current_user_id).inactivate_final(uid=uid)


@router.post(
    "/{uid}/activations",
    summary="Reactivates the objective template identified by 'uid' and its Pre-Instances.",
    description="""This request is only valid if the objective template
* is in 'Retired' status only (so no latest 'Draft' status exists).

If the request succeeds:
* The status will be automatically set to 'Final'.
* The 'change_description' property will be set automatically. 
* The 'version' property will remain the same as before.
    """,
    response_model=models.ObjectiveTemplate,
    status_code=200,
    responses={
        200: {"description": "OK."},
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The objective template is not in retired status.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The objective template with the specified 'uid' could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def reactivate(
    uid: str = ObjectiveTemplateUID, current_user_id: str = Depends(get_current_user_id)
) -> models.ObjectiveTemplate:
    # return service.reactivate_retired(uid)
    # TODO: do sth to allow for static code analysis of this code
    return Service(current_user_id).reactivate_retired(uid)


@router.delete(
    "/{uid}",
    summary="Deletes the objective template identified by 'uid'.",
    description="""This request is only valid if \n
* the objective template is in 'Draft' status and
* the objective template has never been in 'Final' status and
* the objective template has no references to any objectives and
* the objective template belongs to a library that allows deleting (the 'is_editable' property of the library needs to be true).""",
    response_model=None,
    status_code=204,
    responses={
        204: {
            "description": "No Content - The objective template was successfully deleted."
        },
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The objective template is not in draft status.\n"
            "- The objective template was already in final state or is in use.\n"
            "- The library does not allow to delete objective templates.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - An objective template with the specified uid could not be found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def delete_objective_template(
    uid: str = ObjectiveTemplateUID, current_user_id: str = Depends(get_current_user_id)
) -> None:
    # service.soft_delete(uid)
    Service(current_user_id).soft_delete(uid)
    return Response(status_code=fast_api_status.HTTP_204_NO_CONTENT)


# TODO this endpoint potentially returns duplicated entries (by intention, currently).
#       however: check if that is ok with regard to the data volume we expect in the future. is paging needed?
@router.get(
    "/{uid}/parameters",
    summary="Returns all parameters used in the objective template identified by 'uid'. Includes the available terms per parameter.",
    description="""The returned parameters are ordered
0. as they occur in the objective template

Per parameter, the parameter.terms are ordered by
0. term.name ascending

Note that parameters may be used multiple times in templates.
In that case, the same parameter (with the same terms) is included multiple times in the response.
    """,
    response_model=List[models.TemplateParameter],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_parameters(
    uid: str = Path(None, description="The unique id of the objective template."),
    study_uid: Optional[str] = Query(
        None,
        description="Optionally, the uid of the study to subset the parameters to (e.g. for StudyEndpoints parameters)",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    return Service(current_user_id).get_parameters(
        uid=uid, study_uid=study_uid, include_study_endpoints=True
    )


@router.post(
    "/pre-validate",
    summary="Validates the content of an objective template without actually processing it.",
    description="""Be aware that - even if this request is accepted - there is no guarantee that
a following request to e.g. *[POST] /objective-templates* or *[PATCH] /objective-templates/{uid}*
with the same content will succeed.

"""
    + PARAMETERS_NOTE,
    status_code=202,
    responses={
        202: {
            "description": "Accepted. The content is valid and may be submitted in another request."
        },
        400: {
            "model": ErrorResponse,
            "description": "Forbidden. The content is invalid - Reasons include e.g.: \n"
            "- The syntax of the 'name' is not valid.\n"
            "- One of the parameters wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def pre_validate(
    objective_template: ObjectiveTemplateNameInput = Body(
        description="The content of the objective template that shall be validated.",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    # service.validate(objective_template)
    Service(current_user_id).validate_template_syntax(objective_template.name)


@router.post(
    "/{uid}/pre-instances",
    summary="Create a Pre-Instance",
    description="",
    response_model=models.ObjectivePreInstance,
    status_code=201,
    responses={
        201: {
            "description": "Created - The objective pre-instance was successfully created."
        },
        400: {
            "model": ErrorResponse,
            "description": "Forbidden - Reasons include e.g.: \n"
            "- The objective template is not in draft status.\n"
            "- The objective template name is not valid.\n"
            "- The library does not allow to edit draft versions.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The objective template with the specified 'uid' could not be found.",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def create_pre_instance(
    uid: str = ObjectiveTemplateUID,
    pre_instance: ObjectivePreInstanceCreateInput = Body(description=""),
) -> models.ObjectiveTemplate:
    return ObjectivePreInstanceService().create(
        template=pre_instance,
        template_uid=uid,
    )
