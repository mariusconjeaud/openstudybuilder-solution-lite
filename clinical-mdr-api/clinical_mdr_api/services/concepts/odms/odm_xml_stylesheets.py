import re
from os import listdir, path

from clinical_mdr_api.config import XML_STYLESHEET_DIR_PATH
from clinical_mdr_api.exceptions import BusinessLogicException, ValidationException
from clinical_mdr_api.services._utils import strip_suffix


class OdmXmlStylesheetService:
    @staticmethod
    def get_available_stylesheet_names():
        dir_files = listdir(XML_STYLESHEET_DIR_PATH)

        rs = []
        for file in dir_files:
            if file.endswith(".xsl"):
                rs.append(strip_suffix(file, ".xsl"))
        return sorted(rs)

    @staticmethod
    def get_xml_filename_by_name(stylesheet: str):
        if re.search("[^a-zA-Z0-9-]", stylesheet):
            raise ValidationException(
                "Stylesheet name must only contain letters, numbers and hyphens."
            )

        filename = XML_STYLESHEET_DIR_PATH + stylesheet + ".xsl"
        if path.exists(filename):
            return filename

        raise BusinessLogicException(f"Stylesheet with name ({stylesheet}) not found.")

    @staticmethod
    def get_specific_stylesheet(stylesheet: str):
        with open(
            OdmXmlStylesheetService.get_xml_filename_by_name(stylesheet),
            mode="r",
            encoding="utf-8",
        ) as f:
            return f.read()
