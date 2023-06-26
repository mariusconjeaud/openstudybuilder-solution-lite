"""Study chart router."""
import os
from typing import Optional

from fastapi import Depends, Path, Query
from fastapi.responses import HTMLResponse, StreamingResponse

from clinical_mdr_api.models.study_selections.table_with_headers import TableWithHeaders
from clinical_mdr_api.oauth import get_current_user_id
from clinical_mdr_api.routers import _generic_descriptions
from clinical_mdr_api.routers import studies_router as router
from clinical_mdr_api.services.studies.study import StudyService
from clinical_mdr_api.services.studies.study_flowchart import StudyFlowchartService

StudyUID = Path(None, description="The unique id of the study.")

time_unit_query = Query(
    "days",
    regex="^(weeks|days)$",
    description="The preferred time unit, either days or weeks.",
)


@router.get(
    "/{uid}/flowchart",
    summary="Returns Study Protocol Flowchart table",
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
    response_model=TableWithHeaders,
)
def get_study_flowchart(
    uid: str = StudyUID,
    time_unit: Optional[str] = time_unit_query,
    current_user_id: str = Depends(get_current_user_id),
) -> TableWithHeaders:
    StudyService(user=current_user_id).check_if_study_exists(uid)
    return StudyFlowchartService(current_user_id=current_user_id).get_table(
        uid, time_unit
    )


@router.get(
    "/{uid}/flowchart.html",
    summary="Builds and returns an HTML document with Study Protocol Flowchart table",
    responses={
        200: {"content": {"text/html": {"schema": {"type": "string"}}}},
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_study_flowchart_html(
    uid: str = StudyUID,
    time_unit: Optional[str] = time_unit_query,
    current_user_id: str = Depends(get_current_user_id),
) -> HTMLResponse:
    StudyService(user=current_user_id).check_if_study_exists(uid)
    return HTMLResponse(
        StudyFlowchartService(current_user_id=current_user_id).get_html_document(
            uid, time_unit
        )
    )


@router.get(
    "/{uid}/flowchart.docx",
    summary="Builds and returns a DOCX document with Study Protocol Flowchart table",
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
    uid: str = StudyUID,
    time_unit: Optional[str] = time_unit_query,
    current_user_id: str = Depends(get_current_user_id),
) -> StreamingResponse:
    StudyService(user=current_user_id).check_if_study_exists(uid)
    docx = StudyFlowchartService(current_user_id=current_user_id).get_docx_document(
        uid, time_unit
    )
    stream = docx.get_document_stream()
    size = stream.seek(0, os.SEEK_END)
    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{uid} flowchart.docx"',
            "Content-Length": f"{size:d}",
        },
    )
