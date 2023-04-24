"""Study Protocol Interventions service"""

import logging
from typing import Dict, List, Mapping, Sequence

import yattag
from docx.enum.style import WD_STYLE_TYPE

from clinical_mdr_api import models
from clinical_mdr_api.models.table import Table
from clinical_mdr_api.oauth import get_current_user_id
from clinical_mdr_api.services.study_arm_selection import StudyArmSelectionService
from clinical_mdr_api.services.study_compound_dosing_selection import (
    StudyCompoundDosingSelectionService,
)
from clinical_mdr_api.services.study_compound_selection import (
    StudyCompoundSelectionService,
)
from clinical_mdr_api.services.utils.table import table_to_docx, table_to_html

# For future LOCALIZATION
_gettext = {
    "intervention_or_arm_name": "Intervention/Arm name",
    "intervention_name": "Intervention name",
    "intervention_type": "Intervention type",
    "investigational_or_non_investigational": "Investigational or non-investigational",
    "pharmaceutical_form": "Pharmaceutical form",
    "route_of_administration": "Route of administration",
    "medical_device": "Medical-device (if applicable)",
    "trial_product_strength": "Trial product strength",
    "dose_and_frequency": "Dose and dose frequency",
    "dosing_and_administration": "Dosing instructions and administration",
    "transfer_from_other_therapy": "Transfer from other therapy",
    "sourcing": "Sourcing",
    "packaging_and_labelling": "Packaging and labelling",
    "authorisation_status_in": "Authorisation status in",
    "medical_device_template": "Administered using {device} with a {dispensed_in}",
    "trial_product_strength_template": "{value} {unit}",
    "None": "None",
    "study_interventions": "Study Interventions",
    "no_information": "-",
}.get

log = logging.getLogger(__name__)

# pylint: disable=no-member
DOCX_STYLES = {
    "table": ("SB Table Condensed", WD_STYLE_TYPE.TABLE),
    "header1": ("Table Header lvl1", WD_STYLE_TYPE.PARAGRAPH),
    "header2": ("Table Header lvl2", WD_STYLE_TYPE.PARAGRAPH),
    None: ("Table Text", WD_STYLE_TYPE.PARAGRAPH),
}


class StudyInterventionsService:
    @property
    def current_user_id(self):
        return get_current_user_id()

    def get_table(self, study_uid: str) -> Table:
        compounds = self._get_study_compounds(study_uid)
        arms = self._get_arms_for_compounds(study_uid)
        dosings = self._get_compound_dosings(study_uid)
        table = self.mk_table(compounds, arms, dosings)
        return table

    def get_html(self, study_uid: str) -> str:
        table = self.get_table(study_uid)
        doc = table_to_html(
            table, id_="StudyInterventionsTable", title=_gettext("study_interventions")
        )
        return yattag.indent(doc.getvalue())

    def get_docx(self, study_uid: str):
        table = self.get_table(study_uid)
        docx = table_to_docx(table, DOCX_STYLES)
        return docx

    @staticmethod
    def mk_table(
        compounds: Sequence[models.StudySelectionCompound],
        arms: Mapping[str, Sequence[models.StudySelectionArm]],
        dosings: Mapping[str, Sequence[models.StudyCompoundDosing]],
    ) -> Table:
        table = Table.new()
        table.num_header_rows = 1
        table.num_header_columns = 1

        r = 0
        table.data[r][0] = _gettext("intervention_or_arm_name")
        table.meta[r][0]["class"] = "header1"
        for c, cmp in enumerate(compounds, start=1):
            table.data[r][c] = StudyInterventionsService._arm_txt(cmp, arms)
            table.meta[r][c]["class"] = "header2"

        r += 1
        table.data[r][0] = _gettext("intervention_name")
        table.meta[r][0]["class"] = "header2"
        for c, cmp in enumerate(compounds, start=1):
            table.data[r][c] = cmp.compound.name if cmp.compound.name else ""

        r += 1
        table.data[r][0] = _gettext("intervention_type")
        table.meta[r][0]["class"] = "header2"
        for c, cmp in enumerate(compounds, start=1):
            table.data[r][c] = (
                cmp.type_of_treatment.name if cmp.type_of_treatment else ""
            )

        r += 1
        table.data[r][0] = _gettext("investigational_or_non_investigational")
        table.meta[r][0]["class"] = "header2"
        for c, _ in enumerate(compounds, start=1):
            table.data[r][c] = "?"  # TODO

        r += 1
        table.data[r][0] = _gettext("pharmaceutical_form")
        table.meta[r][0]["class"] = "header2"
        for c, cmp in enumerate(compounds, start=1):
            table.data[r][c] = cmp.dosage_form.name if cmp.dosage_form else ""

        r += 1
        table.data[r][0] = _gettext("route_of_administration")
        table.meta[r][0]["class"] = "header2"
        for c, cmp in enumerate(compounds, start=1):
            table.data[r][c] = (
                cmp.route_of_administration.name if cmp.route_of_administration else ""
            )

        r += 1
        table.data[r][0] = _gettext("medical_device")
        table.meta[r][0]["class"] = "header2"
        for c, cmp in enumerate(compounds, start=1):
            m = {
                "device": cmp.device.name if cmp.device else _gettext("None"),
                "dispensed_in": (
                    cmp.dispensed_in.name if cmp.dispensed_in else _gettext("None")
                ),
            }
            table.data[r][c] = _gettext("medical_device_template").format_map(m)

        r += 1
        table.data[r][0] = _gettext("trial_product_strength")
        table.meta[r][0]["class"] = "header2"
        for c, cmp in enumerate(compounds, start=1):
            if cmp.strength_value:
                m = {
                    "unit": cmp.strength_value.unit_label,
                    "value": cmp.strength_value.value,
                }
                table.data[r][c] = _gettext(
                    "trial_product_strength_template"
                ).format_map(m)
            else:
                table.data[r][c] = ""

        r += 1
        table.data[r][0] = _gettext("dose_and_frequency")
        table.meta[r][0]["class"] = "header2"
        for c, cmp in enumerate(compounds, start=1):
            table.data[r][c] = StudyInterventionsService._dosing_txt(cmp, dosings)

        r += 1
        table.data[r][0] = _gettext("dosing_and_administration")
        table.meta[r][0]["class"] = "header2"
        for c, cmp in enumerate(compounds, start=1):
            table.data[r][c] = cmp.other_info or _gettext("no_information")

        r += 1
        table.data[r][0] = _gettext("transfer_from_other_therapy")
        table.meta[r][0]["class"] = "header2"
        for c, _ in enumerate(compounds, start=1):
            table.data[r][c] = "?"  # TODO

        r += 1
        table.data[r][0] = _gettext("sourcing")
        table.meta[r][0]["class"] = "header2"
        for c, _ in enumerate(compounds, start=1):
            table.data[r][c] = "?"  # TODO

        r += 1
        table.data[r][0] = _gettext("packaging_and_labelling")
        table.meta[r][0]["class"] = "header2"
        for c, _ in enumerate(compounds, start=1):
            table.data[r][c] = "?"  # TODO

        r += 1
        table.data[r][0] = _gettext("authorisation_status_in")
        table.meta[r][0]["class"] = "header2"
        for c, _ in enumerate(compounds, start=1):
            table.data[r][c] = "?"  # TODO

        return table

    @staticmethod
    def _dosing_txt(compounds, dosings):
        return "\n".join(
            f"{dosing.dose_value.value if dosing.dose_value else ''} "
            f"{dosing.dose_value.unit_label if dosing.dose_value else ''} "
            f"{dosing.dose_frequency.name if dosing.dose_frequency else ''}".strip()
            for dosing in dosings.get(compounds.study_compound_uid, [])
        ) or _gettext("no_information")

    @staticmethod
    def _arm_txt(compound, arms):
        return "\n".join(
            arm.name for arm in arms.get(compound.study_compound_uid, [])
        ) or _gettext("no_information")

    def _get_study_compounds(
        self, study_uid
    ) -> Sequence[models.StudySelectionCompound]:
        return (
            StudyCompoundSelectionService(author=self.current_user_id)
            .get_all_selection(
                study_uid=study_uid,
            )
            .items
        )

    def _get_arms_for_compounds(
        self, study_uid
    ) -> Mapping[str, List[models.StudySelectionArm]]:
        arms = {
            arm.arm_uid: arm
            for arm in StudyArmSelectionService(author=self.current_user_id)
            .get_all_selection(
                study_uid=study_uid,
            )
            .items
        }

        mapping = StudyCompoundSelectionService(
            author=self.current_user_id
        ).get_compound_uid_to_arm_uids_mapping(study_uid)

        return {
            compound_uid: [arms[arm_uid] for arm_uid in arm_uids]
            for compound_uid, arm_uids in mapping.items()
        }

    def _get_compound_dosings(
        self, study_uid: str
    ) -> Dict[str, List[models.StudyCompoundDosing]]:
        results = (
            StudyCompoundDosingSelectionService(author=self.current_user_id)
            .get_all_compound_dosings(study_uid)
            .items
        )

        mapping = {}
        for dosing in results:
            key = dosing.study_compound.study_compound_uid
            mapping.setdefault(key, []).append(dosing)

        return mapping
