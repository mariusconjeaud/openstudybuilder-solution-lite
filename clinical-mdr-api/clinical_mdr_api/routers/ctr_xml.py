"""Study disclosure router"""

from fastapi import Path
from fastapi.responses import Response

from clinical_mdr_api.routers import _generic_descriptions
from clinical_mdr_api.routers.study import router
from clinical_mdr_api.services.ctr_xml_service import CTRXMLService

StudyUID = Path(None, description="The unique id of the study.")


class XMLResponse(Response):
    media_type = "text/xml"


@router.get(
    "/studies/{uid}/ctr/odm.xml",
    summary="Returns study disclosure document in CTR ODM XML format",
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
    response_class=XMLResponse,
)
def get_study_flowchart_html(
    uid: str = StudyUID,
) -> str:
    return CTRXMLService().get_ctr_odm(uid)
