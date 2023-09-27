from typing import Any, Sequence

from fastapi import APIRouter, Body, Depends, Path, Query, Response
from fastapi import status as response_status
from pydantic.types import Json
from starlette.requests import Request

from clinical_mdr_api import config, exceptions
from clinical_mdr_api.domains.study_definition_aggregates.study_metadata import (
    StudyComponentEnum,
    StudyStatus,
)
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.models.study_selections.study import (
    CompactStudy,
    StatusChangeDescription,
    Study,
    StudyCreateInput,
    StudyFieldAuditTrailEntry,
    StudyPatchRequestJsonModel,
    StudyPreferredTimeUnit,
    StudyPreferredTimeUnitInput,
    StudyProtocolTitle,
)
from clinical_mdr_api.models.utils import CustomPage
from clinical_mdr_api.oauth import get_current_user_id, rbac
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.routers import _generic_descriptions, decorators
from clinical_mdr_api.services.studies.study import StudyService

# Prefixed with "/studies"
router = APIRouter()

StudyUID = Path(None, description="The unique id of the study.")


@router.get(
    "",
    dependencies=[rbac.STUDY_READ],
    summary="Returns all studies in their latest/newest version.",
    description=f"""
Allowed parameters include : filter on fields, sort by field name with sort direction, pagination

{_generic_descriptions.DATA_EXPORTS_HEADER}
""",
    response_model=CustomPage[CompactStudy],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "uid",
            "current_metadata.identification_metadata.clinical_programme_name",
            "current_metadata.identification_metadata.project_number",
            "current_metadata.identification_metadata.project_name",
            "current_metadata.identification_metadata.study_number",
            "current_metadata.identification_metadata.study_id",
            "current_metadata.identification_metadata.study_acronym",
            "current_metadata.study_description.study_title",
            "current_metadata.version_metadata.study_status",
            "current_metadata.version_metadata.version_timestamp",
            "current_metadata.version_metadata.version_author",
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
def get_all(
    request: Request,  # request is actually required by the allow_exports decorator
    has_study_objective: bool
    | None = Query(
        default=None,
        description="Optionaly, filter studies based on the existence of related study objectives or not",
    ),
    has_study_endpoint: bool
    | None = Query(
        default=None,
        description="Optionaly, filter studies based on the existence of related study endpoints or not",
    ),
    has_study_criteria: bool
    | None = Query(
        default=None,
        description="Optionaly, filter studies based on the existence of related study criteria or not",
    ),
    has_study_activity: bool
    | None = Query(
        default=None,
        description="Optionaly, filter studies based on the existence of related study activities or not",
    ),
    has_study_activity_instruction: bool
    | None = Query(
        default=None,
        description="Optionaly, filter studies based on the existence of related study activity instruction or not",
    ),
    sort_by: Json = Query(None, description=_generic_descriptions.SORT_BY),
    page_number: int
    | None = Query(1, ge=1, description=_generic_descriptions.PAGE_NUMBER),
    page_size: int
    | None = Query(
        config.DEFAULT_PAGE_SIZE,
        ge=0,
        le=config.MAX_PAGE_SIZE,
        description=_generic_descriptions.PAGE_SIZE,
    ),
    filters: Json
    | None = Query(
        None,
        description=_generic_descriptions.FILTERS,
        example=_generic_descriptions.FILTERS_EXAMPLE,
    ),
    operator: str | None = Query("and", description=_generic_descriptions.OPERATOR),
    total_count: bool
    | None = Query(False, description=_generic_descriptions.TOTAL_COUNT),
    deleted: bool = Query(
        default=False,
        description="Indicates whether to return 'Active' Studies or 'Deleted' ones.",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> CustomPage[CompactStudy]:
    study_service = StudyService(user=current_user_id)
    results = study_service.get_all(
        has_study_objective=has_study_objective,
        has_study_endpoint=has_study_endpoint,
        has_study_criteria=has_study_criteria,
        has_study_activity=has_study_activity,
        has_study_activity_instruction=has_study_activity_instruction,
        page_number=page_number,
        page_size=page_size,
        total_count=total_count,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
        deleted=deleted,
    )

    return CustomPage.create(
        items=results.items, total=results.total, page=page_number, size=page_size
    )


@router.get(
    "/headers",
    dependencies=[rbac.STUDY_READ],
    summary="Returns possibles values from the database for a given header",
    description="""Allowed parameters include : field name for which to get possible
    values, search string to provide filtering for the field name, additional filters to apply on other fields""",
    response_model=list[Any],
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
    search_string: str
    | None = Query("", description=_generic_descriptions.HEADER_SEARCH_STRING),
    filters: Json
    | None = Query(
        None,
        description=_generic_descriptions.FILTERS,
        example=_generic_descriptions.FILTERS_EXAMPLE,
    ),
    operator: str | None = Query("and", description=_generic_descriptions.OPERATOR),
    result_count: int
    | None = Query(10, description=_generic_descriptions.HEADER_RESULT_COUNT),
):
    study_service = StudyService(user=current_user_id)
    return study_service.get_distinct_values_for_header(
        field_name=field_name,
        search_string=search_string,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        result_count=result_count,
    )


@router.post(
    "/{uid}/lock",
    dependencies=[rbac.STUDY_WRITE],
    summary="Locks a Study with specified uid",
    description="The Study is locked, which means that the LATEST_LOCKED relationship in the database is created."
    "The first locked version obtains number '1' and each next locked version "
    "is incremented number of the last locked version. "
    "The Study exists in the LOCKED state after successful lock",
    response_model=Study,
    status_code=201,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "ValidationException - The business rules were not met",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The study with the specified 'uid'.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def lock(
    current_user_id: str = Depends(get_current_user_id),
    uid: str = StudyUID,
    lock_description: StatusChangeDescription = Body(
        description="The description of the locked version."
    ),
):
    study_service = StudyService(user=current_user_id)
    return study_service.lock(
        uid=uid, change_description=lock_description.change_description
    )


@router.post(
    "/{uid}/unlock",
    dependencies=[rbac.STUDY_WRITE],
    summary="Unlocks a Study with specified uid",
    description="The Study is unlocked, which means that the new DRAFT version of a Study is created"
    " and the Study exists in the DRAFT state.",
    response_model=Study,
    status_code=201,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "ValidationException - The business rules were not met",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The study with the specified 'uid'.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def unlock(
    current_user_id: str = Depends(get_current_user_id),
    uid: str = StudyUID,
):
    study_service = StudyService(user=current_user_id)
    return study_service.unlock(uid=uid)


@router.post(
    "/{uid}/release",
    dependencies=[rbac.STUDY_WRITE],
    summary="Releases a Study with specified uid",
    description="The Study is released, which means that 'snapshot' of the Study is created in the database"
    "and the LATEST_RELEASED relationship is created that points to the created snapshot."
    "What's more the new LATEST_DRAFT node is created that describes the new Draft Study after releasing.",
    response_model=Study,
    status_code=201,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "ValidationException - The business rules were not met",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The study with the specified 'uid'.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def release(
    current_user_id: str = Depends(get_current_user_id),
    uid: str = StudyUID,
    release_description: StatusChangeDescription = Body(
        description="The description of the release version."
    ),
):
    study_service = StudyService(user=current_user_id)
    return study_service.release(
        uid=uid, change_description=release_description.change_description
    )


@router.delete(
    "/{uid}",
    dependencies=[rbac.STUDY_WRITE],
    summary="Deletes a Study",
    description="""
State before:
 - uid must exist
 - The Study must be in status Draft and it couldn't be locked before.

Business logic:
 - The draft Study is deleted.

State after:
 - Study is successfully deleted.

Possible errors:
 - Invalid uid or status not Draft or Study was previously locked.
    """,
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "No Content - The Study was successfully deleted."},
        400: {
            "model": ErrorResponse,
            "description": "ValidationException - The business rules were not met",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The study with the specified 'uid'.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def delete_activity(
    uid: str = StudyUID, current_user_id: str = Depends(get_current_user_id)
):
    study_service = StudyService(user=current_user_id)
    study_service.soft_delete(uid=uid)
    return Response(status_code=response_status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{uid}",
    dependencies=[rbac.STUDY_WRITE],
    summary="Request to change some aspects (parts) of a specific study definition identified by 'uid'.",
    description="The request to change (some aspect) of the state of current aggregate. "
    "There are some special cases and considerations:\n"
    "* patching study_status in current_metadata.version_metadata is considered as the request for"
    "  locking/unlocking/releasing the study definition and should not be combined with any other"
    "  changes\n"
    "* there are many business rules that apply in different patching scenario or state of the"
    "  study definition. If request is not compliant it will fail with 403 and response body"
    "  will (hopefully) explain what is wrong.\n"
    "* the method may be invoked with dry=true query param. if that's the case it wokrs the same"
    "  except that any change made to the resource are not persisted (however all validations are"
    "  performed.\n",
    response_model=Study,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Some application/business rules forbid to process the request. Expect more detailed"
            " information in response body.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The study with the specified 'uid'.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def patch(
    uid: str = StudyUID,
    dry: bool = Query(
        False,
        description="If specified the operation does full validation and returns either 200 or 403 but"
        "nothing is persisted.",
    ),
    study_patch_request: StudyPatchRequestJsonModel = Body(
        description="The request with the structure similar to the GET /{uid} response. Carrying only those"
        "fields requested to change.",
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> Study:
    study_service = StudyService(user=current_user_id)
    if study_patch_request is None:
        raise exceptions.ValidationException("No data to patch was provided.")
    response = study_service.patch(uid, dry, study_patch_request)
    return response


@router.get(
    "/{uid}",
    dependencies=[rbac.STUDY_READ],
    summary="Returns the current state of a specific study definition identified by 'uid'.",
    description="If multiple request query parameters are used, then they need to match all at the same time"
    " (they are combined with the AND operation).",
    response_model=Study,
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The study with the specified 'uid'"
            " (and the specified date/time and/or status) wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get(
    uid: str = StudyUID,  # ,
    fields: str
    | None = Query(
        default=None,
        description="Parameter specifies which parts of the whole Study Definition representation to retrieve. In"
        " the form of comma separated name of the fields prefixed by (optional) `+` "
        " if the client wishes"
        " to retrieve the field or `-` if the client wants to skip the field."
        " If not specified identification metadata and version metadata are retrieved."
        " If value starts with `+` or `-` above default is extended or reduced by the specified fields"
        " otherwise (if not started with `+` or `-`) provided fields specification"
        " replaces the default. The `uid` and `study_status` fields will be always returned"
        " as they are mandatory fields for the Study API model. Currently supported fields are"
        " `current_metadata.identification_metadata`, `current_metadata.high_level_study_design`"
        " ,`current_metadata.study_population` and `current_metadata.study_intervention`"
        " , `current_metadata.study_description`.",
    ),
    current_user_id: str = Depends(get_current_user_id),
    # at_specified_date_time: datetime | None = Query(
    #     None,
    #     description="If specified, the latest/newest representation of the study at"
    #     " this point in time is returned.\n"
    #     "The point in time needs to be specified in ISO 8601 format including the timezone, e.g.: "
    #     "'2020-10-31T16:00:00+02:00' for October 31, 2020 at 4pm in UTC+2 timezone. "
    #     "If the timezone is omitted, UTC±0 is assumed.",
    # ),
    status: StudyStatus
    | None = Query(
        None,
        description="If specified, the last representation of the study in that status is returned (if existent)."
        "Valid values are: 'Released', 'Draft' or 'Locked'.",
    ),
    version: str
    | None = Query(
        None,
        description=r"If specified, the latest/newest representation of the study in that version is returned. "
        r"Only exact matches are considered. "
        r"The version is specified as an integer number: "
        r"E.g. 0, 1, 2, ...",
    ),
):
    study_service = StudyService(user=current_user_id)
    study_definition = study_service.get_by_uid(
        uid=uid,
        fields=fields,
        at_specified_date_time=None,
        status=status,
        version=version,
    )
    return study_definition


@router.get(
    "/{uid}/snapshot-history",
    dependencies=[rbac.STUDY_READ],
    summary="Returns the history of study snapshot definitions",
    description="It returns the history of changes made to the specified Study Definition Snapshot."
    "The returned history should reflect HAS_VERSION relationships in the database between StudyRoot and StudyValue nodes",
    response_model=CustomPage[CompactStudy],
    response_model_exclude_unset=True,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The study with the specified 'uid'"
            " (and the specified date/time and/or status) wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_snapshot_history(
    uid: str = StudyUID,  # ,
    sort_by: Json = Query(None, description=_generic_descriptions.SORT_BY),
    page_number: int
    | None = Query(1, ge=1, description=_generic_descriptions.PAGE_NUMBER),
    page_size: int
    | None = Query(
        config.DEFAULT_PAGE_SIZE,
        ge=0,
        le=config.MAX_PAGE_SIZE,
        description=_generic_descriptions.PAGE_SIZE,
    ),
    filters: Json
    | None = Query(
        None,
        description=_generic_descriptions.FILTERS,
        example=_generic_descriptions.FILTERS_EXAMPLE,
    ),
    operator: str | None = Query("and", description=_generic_descriptions.OPERATOR),
    total_count: bool
    | None = Query(False, description=_generic_descriptions.TOTAL_COUNT),
    current_user_id: str = Depends(get_current_user_id),
):
    study_service = StudyService(user=current_user_id)
    snapshot_history = study_service.get_study_snapshot_history(
        study_uid=uid,
        page_number=page_number,
        page_size=page_size,
        filter_by=filters,
        filter_operator=FilterOperator.from_str(operator),
        sort_by=sort_by,
        total_count=total_count,
    )
    return CustomPage.create(
        items=snapshot_history.items,
        total=snapshot_history.total,
        page=page_number,
        size=page_size,
    )


@router.get(
    "/{uid}/fields-audit-trail",
    dependencies=[rbac.STUDY_READ],
    summary="Returns the audit trail for the fields of a specific study definition identified by 'uid'.",
    description="Actions on the study are grouped by date of edit."
    "Optionally select which subset of fields should be reflected in the audit trail.",
    response_model=Sequence[StudyFieldAuditTrailEntry],
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The study with the specified 'uid'"
            " wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_fields_audit_trail(
    uid: str = StudyUID,  # ,
    sections: str
    | None = Query(
        default=None,
        description="""
Optionally specify a list of sections to filter the audit trail by. 
Each section name must be preceded by a `+` or a `-`.

Valid values are:

- identification_metadata
- registry_identifiers
- version_metadata
- high_level_study_design
- study_population
- study_intervention
- study_description

Example valid input: `-identification_metadata,+study_population`.

If no filters are specified, the entire audit trail is returned.
""",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    study_service = StudyService(user=current_user_id)
    study_fields_audit_trail = study_service.get_fields_audit_trail_by_uid(
        uid=uid, sections=sections
    )
    return study_fields_audit_trail


@router.post(
    "",
    dependencies=[rbac.STUDY_WRITE],
    summary="Creates a new Study Definition.",
    description="""
If the request succeeds new DRAFT Study Definition will be with initial identification data as provided in 
request body with new unique uid generated and returned in response body.
        """,
    response_model=Study,
    response_model_exclude_unset=True,
    status_code=201,
    responses={
        201: {"description": "Created - The study was successfully created."},
        400: {
            "model": ErrorResponse,
            "description": "Some application/business rules forbid to process the request. Expect more detailed"
            " information in response body.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def create(
    study_create_input: StudyCreateInput = Body(
        description="Related parameters of the objective that shall be created."
    ),
    current_user_id: str = Depends(get_current_user_id),
) -> Study:
    study_service = StudyService(user=current_user_id)
    return study_service.create(study_create_input)


@router.get(
    "/{uid}/protocol-title",
    dependencies=[rbac.STUDY_READ],
    summary="Retrieve all information related to Protocol Title",
    description="""
State before:
 - Study-uid must exist

Business logic:
 - Retrieve Study title, Universal Trial Number, EudraCT number, IND number, Study phase fields
 - Retrieve all names of study compounds associated to {uid} and where type of treatment is equal to Investigational Product

State after:
 - No change
""",
    response_model=StudyProtocolTitle,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The study with the specified 'uid'"
            " wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_protocol_title(
    uid: str = StudyUID, current_user_id: str = Depends(get_current_user_id)
):
    study_service = StudyService(user=current_user_id)
    return study_service.get_protocol_title(uid)


@router.patch(
    "/{uid}/copy-component",
    dependencies=[rbac.STUDY_WRITE],
    summary="Copy study form from another study",
    description="""
State before:
 - uid must exist
 - reference_study_uid must exist

Business logic:
 - if overwrite is set to false, then the projection of the copy will be returned
 - if overwrite is set to true, then the component referenced as a component_to_copy will be copied
 from the study referenced by reference_study_uid to the study referenced by uid.

State after:
 - The specific form is copied or projected into a study referenced by uid 'uid'.
""",
    response_model=Study,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The study with the specified 'uid'"
            " wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def copy_simple_form_from_another_study(
    uid: str = StudyUID,
    reference_study_uid: str = Query(
        ..., description="The uid of the study to copy component from"
    ),
    component_to_copy: StudyComponentEnum = Query(
        ..., description="The uid of the study to copy component from"
    ),
    overwrite: bool = Query(
        False,
        description="Indicates whether to overwrite the component of the study referenced by the uid"
        "or return a projection",
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    study_service = StudyService(user=current_user_id)
    return study_service.copy_component_from_another_study(
        uid=uid,
        reference_study_uid=reference_study_uid,
        component_to_copy=component_to_copy,
        overwrite=overwrite,
    )


@router.get(
    "/{uid}/time-units",
    dependencies=[rbac.STUDY_READ],
    summary="Gets a study preferred time unit",
    response_model=StudyPreferredTimeUnit,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The study or unit definition with the specified 'uid'"
            " wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def get_preferred_time_unit(
    uid: str = StudyUID,
    current_user_id: str = Depends(get_current_user_id),
):
    study_service = StudyService(user=current_user_id)
    return study_service.get_study_preferred_time_unit(
        study_uid=uid,
    )


@router.patch(
    "/{uid}/time-units",
    dependencies=[rbac.STUDY_WRITE],
    summary="Edits a study preferred time unit",
    response_model=StudyPreferredTimeUnit,
    status_code=200,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found - The study or unit definition with the specified 'uid'"
            " wasn't found.",
        },
        500: _generic_descriptions.ERROR_500,
    },
)
def patch_preferred_time_unit(
    uid: str = StudyUID,
    preferred_time_unit_input: StudyPreferredTimeUnitInput = Body(
        ..., description="Data needed to create a study preferred time unit"
    ),
    current_user_id: str = Depends(get_current_user_id),
):
    study_service = StudyService(user=current_user_id)
    return study_service.patch_study_preferred_time_unit(
        study_uid=uid, unit_definition_uid=preferred_time_unit_input.unit_definition_uid
    )
