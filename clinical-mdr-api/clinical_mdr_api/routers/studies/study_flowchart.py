"""Study chart router."""
import os

from fastapi import Depends, Path, Query
from fastapi.responses import HTMLResponse, StreamingResponse

from clinical_mdr_api.models.validators import FLOAT_REGEX
from clinical_mdr_api.oauth import get_current_user_id, rbac
from clinical_mdr_api.routers import _generic_descriptions
from clinical_mdr_api.routers import studies_router as router
from clinical_mdr_api.services.studies.study import StudyService
from clinical_mdr_api.services.studies.study_flowchart import (
    DOCX_STYLES,
    StudyFlowchartService,
)
from clinical_mdr_api.services.utils.table_f import (
    TableWithFootnotes,
    table_to_docx,
    table_to_html,
)

STUDY_UID_PATH = Path(None, description="The unique id of the study.")

STUDY_VALUE_VERSION_QUERY = Query(
    None,
    description="StudyValueVersion to extract the StudySelections",
    regex=FLOAT_REGEX,
)

TIME_UNIT_QUERY = Query(
    "days",
    regex="^(weeks|days)$",
    description="The preferred time unit, either days or weeks.",
)


@router.get(
    "/{study_uid}/flowchart/coordinates",
    dependencies=[rbac.STUDY_READ],
    summary="Returns uid to [row,column] coordinates mapping of items included in SoA Protocol Flowchart table",
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
    response_model=dict[str, tuple[int, int]],
)
def get_study_flowchart_coordinates(
    study_uid: str = STUDY_UID_PATH,
    study_value_version: str | None = STUDY_VALUE_VERSION_QUERY,
    current_user_id: str = Depends(get_current_user_id),
) -> dict[str, tuple[int, int]]:
    coordinates = StudyFlowchartService(
        user=current_user_id
    ).get_flowchart_item_uid_coordinates(
        study_uid=study_uid, study_value_version=study_value_version
    )
    return coordinates


@router.get(
    "/{study_uid}/flowchart",
    dependencies=[rbac.STUDY_READ],
    summary="Returns Protocol SoA Flowchart table with footnotes",
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
    response_model=TableWithFootnotes,
    response_model_exclude_none=True,
)
def get_study_flowchart(
    study_uid: str = STUDY_UID_PATH,
    study_value_version: str | None = STUDY_VALUE_VERSION_QUERY,
    time_unit: str | None = TIME_UNIT_QUERY,
    current_user_id: str = Depends(get_current_user_id),
) -> TableWithFootnotes:
    # build internal representation of flowchart
    table = StudyFlowchartService(user=current_user_id).get_flowchart_table(
        study_uid=study_uid,
        time_unit=time_unit,
        study_value_version=study_value_version,
    )

    return table


@router.get(
    "/{study_uid}/flowchart.html",
    dependencies=[rbac.STUDY_READ],
    summary="Builds and returns an HTML document with Protocol SoA Flowchart table with footnotes",
    responses={
        200: {"content": {"text/html": {"schema": {"type": "string"}}}},
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_study_flowchart_html(
    study_uid: str = STUDY_UID_PATH,
    study_value_version: str | None = STUDY_VALUE_VERSION_QUERY,
    time_unit: str | None = TIME_UNIT_QUERY,
    current_user_id: str = Depends(get_current_user_id),
) -> HTMLResponse:
    # build internal representation of flowchart
    table = StudyFlowchartService(user=current_user_id).get_flowchart_table(
        study_uid=study_uid,
        time_unit=time_unit,
        study_value_version=study_value_version,
    )

    # convert flowchart to HTML document
    html = table_to_html(table)

    return HTMLResponse(html)


@router.get(
    "/{study_uid}/flowchart.docx",
    dependencies=[rbac.STUDY_READ],
    summary="Builds and returns a DOCX document with Protocol SoA Flowchart table with footnotes",
    responses={
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {}
            }
        },
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_study_flowchart_docx(
    study_uid: str = STUDY_UID_PATH,
    study_value_version: str | None = STUDY_VALUE_VERSION_QUERY,
    time_unit: str | None = TIME_UNIT_QUERY,
    current_user_id: str = Depends(get_current_user_id),
) -> StreamingResponse:
    # get study_id for constructing download filename
    study = StudyService(user=current_user_id).get_by_uid(
        study_uid, study_value_version=study_value_version
    )
    filename = (
        f"{study.current_metadata.identification_metadata.study_id} flowchart.docx"
    )

    # build internal representation of flowchart
    table = StudyFlowchartService(user=current_user_id).get_flowchart_table(
        study_uid=study_uid,
        time_unit=time_unit,
        study_value_version=study_value_version,
    )

    # convert flowchart to DOCX document applying styles
    docx = table_to_docx(table, styles=DOCX_STYLES)
    stream = docx.get_document_stream()

    # determine the size of the binary DOCX document for HTTP header
    size = stream.seek(0, os.SEEK_END)
    stream.seek(0)

    # send response along with document info in HTTP header
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": f"{size:d}",
        },
    )
