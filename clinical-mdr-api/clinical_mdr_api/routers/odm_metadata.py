from typing import Optional, Sequence

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile
from fastapi.responses import StreamingResponse

from clinical_mdr_api.domain._utils import ObjectStatus
from clinical_mdr_api.domain.concepts.utils import TargetType
from clinical_mdr_api.models.error import ErrorResponse
from clinical_mdr_api.services.odm_clinspark_import import OdmClinicalXmlImporterService
from clinical_mdr_api.services.odm_csv_exporter import OdmCsvExporterService
from clinical_mdr_api.services.odm_xml_exporter import OdmXmlExporterService
from clinical_mdr_api.services.odm_xml_importer import OdmXmlImporterService
from clinical_mdr_api.services.unit_definition import UnitDefinitionService

router = APIRouter()


MAPPER_DESCRIPTION = """Only CSV format is supported.\n\n
Following headers must exist: `type`, `parent`, `from_name`, `to_name` and `to_alias`\n\n
Allowed values for `type` are: `attribute` and `tag`\n\n
Allowed values for `to_alias` and `from_alias` are: `true` and `false`. Anything other than `true` is considered `false`\n\n
If `to_alias` is true `type` must be `attribute`\n\n
If `to_alias` is true `to_name` is ignored\n\n
If `from_alias` is true `alias_context` must be provided\n\n
If `parent` is empty or `*` is given then the mapping will apply to all occurrences in the entire XML file"""


@router.post(
    "/xmls/export",
    summary="Export ODM XML",
    description="",
    status_code=200,
    responses={500: {"model": ErrorResponse, "description": "Internal Server Error"}},
)
def get_odm_xml(
    target_uid: str,
    target_type: TargetType,
    status: Sequence[ObjectStatus] = Query(
        [ObjectStatus.LATEST_FINAL, ObjectStatus.LATEST_RETIRED]
    ),
    allowed_extensions: Sequence[str] = Query([]),
    stylesheet: Optional[str] = None,
    mapper: Optional[UploadFile] = File(
        default=None,
        description=MAPPER_DESCRIPTION,
    ),
    unit_definition_service: UnitDefinitionService = Depends(),
):
    odm_xml_export_service = OdmXmlExporterService(
        target_uid,
        target_type,
        status,
        allowed_extensions,
        stylesheet,
        mapper,
        unit_definition_service,
    )
    xml = odm_xml_export_service.get_odm_xml()

    return Response(content=xml, media_type="application/xml")


@router.post(
    "/csvs/export",
    summary="Export ODM CSV",
    description="",
    status_code=200,
    responses={500: {"model": ErrorResponse, "description": "Internal Server Error"}},
)
def get_odm_csv(target_uid: str, target_type: TargetType):
    odm_csv_exporter_service = OdmCsvExporterService(target_uid, target_type)
    csv_data = odm_csv_exporter_service.get_odm_csv()

    return StreamingResponse(
        iter(csv_data),
        200,
        {"Content-Disposition": "attachment; filename=odm_metadata.csv"},
        "text/csv",
    )


@router.post(
    "/xmls/import",
    summary="Import ODM XML",
    description="",
    status_code=201,
    responses={500: {"model": ErrorResponse, "description": "Internal Server Error"}},
)
def store_odm_xml(
    xml: UploadFile = File(
        description="The ODM XML file to upload.",
    ),
    mapper: Optional[UploadFile] = File(
        default=None,
        description=MAPPER_DESCRIPTION,
    ),
):
    odm_xml_importer_service = OdmXmlImporterService(xml, mapper)
    return odm_xml_importer_service.store_odm_xml()


@router.post(
    "/clinspark/import",
    summary="Import Clinspark XML",
    description="",
    status_code=201,
    responses={500: {"model": ErrorResponse, "description": "Internal Server Error"}},
)
def store_odm_clinspark_xml(
    xml: UploadFile = File(
        description="The Clinspark ODM XML file to upload.",
    ),
):
    odm_xml_importer_service = OdmClinicalXmlImporterService(xml)
    return odm_xml_importer_service.store_odm_xml()
