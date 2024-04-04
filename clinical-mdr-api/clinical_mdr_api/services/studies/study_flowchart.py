import logging
from typing import Iterable, Mapping, Sequence

from docx.enum.style import WD_STYLE_TYPE
from neomodel import db
from opencensus.trace import execution_context

from clinical_mdr_api import config
from clinical_mdr_api.domains.study_selections.study_soa_footnote import SoAItemType
from clinical_mdr_api.exceptions import ValidationException
from clinical_mdr_api.models import (
    Footnote,
    StudyActivitySchedule,
    StudySelectionActivity,
    StudyVisit,
)
from clinical_mdr_api.models.study_selections.study_soa_footnote import StudySoAFootnote
from clinical_mdr_api.services.studies.study import StudyService
from clinical_mdr_api.services.studies.study_activity_schedule import (
    StudyActivityScheduleService,
)
from clinical_mdr_api.services.studies.study_activity_selection import (
    StudyActivitySelectionService,
)
from clinical_mdr_api.services.studies.study_soa_footnote import StudySoAFootnoteService
from clinical_mdr_api.services.studies.study_visit import StudyVisitService
from clinical_mdr_api.services.utils.table_f import (
    Ref,
    SimpleFootnote,
    TableCell,
    TableRow,
    TableWithFootnotes,
)
from clinical_mdr_api.utils.iter import enumerate_letters

SOA_CHECK_MARK = "X"

# Strings prepared for localization
_ = {
    "study_epoch": "",
    "protocol_section": "Protocol Section",
    "visit_short_name": "Visit short name",
    "study_week": "Study week",
    "study_day": "Study day",
    "visit_window": "Visit window (days)",
    "protocol_flowchart": "Protocol Flowchart",
    "no_study_group": "(not selected)",
    "no_study_subgroup": "(not selected)",
}.get

log = logging.getLogger(__name__)

# pylint: disable=no-member
DOCX_STYLES = {
    "table": ("SB Table Condensed", WD_STYLE_TYPE.TABLE),
    "header1": ("Table Header lvl1", WD_STYLE_TYPE.PARAGRAPH),
    "header2": ("Table Header lvl2", WD_STYLE_TYPE.PARAGRAPH),
    "header3": ("Table Header lvl2", WD_STYLE_TYPE.PARAGRAPH),
    "header4": ("Table Header lvl2", WD_STYLE_TYPE.PARAGRAPH),
    "soaGroup": ("Table lvl 1", WD_STYLE_TYPE.PARAGRAPH),
    "group": ("Table lvl 2", WD_STYLE_TYPE.PARAGRAPH),
    "subGroup": ("Table lvl 3", WD_STYLE_TYPE.PARAGRAPH),
    "activity": ("Table lvl 4", WD_STYLE_TYPE.PARAGRAPH),
    "cell": ("Table Text", WD_STYLE_TYPE.PARAGRAPH),
}


class StudyFlowchartService:
    """Assemble Study Protocol SoA Flowchart"""

    def __init__(self, user: str) -> None:
        self.user = user

    def _validate_parameters(
        self,
        study_uid: str,
        study_value_version: str | None = None,
        time_unit: str | None = None,
    ):
        """
        Validates request parameters

        Raises NotFoundException if no Study with study_uid exists, or if Study does not have a version corresponding
        to optional study_value_version. Raises ValidationException if time_unit is not "day" or "week".

        Args:
            study_uid (str): The unique identifier of the study.
            study_value_version (str | None): The version of the study to check. Defaults to None.
            time_unit (str): The preferred time unit, either "day" or "week".
        """
        StudyService(user=self.user).check_if_study_uid_and_version_exists(
            study_uid, study_value_version=study_value_version
        )

        if time_unit not in (None, "day", "week"):
            raise ValidationException("time_unit has to be 'day' or 'week'")

    def _get_study_activity_schedules(
        self, study_uid: str, study_value_version: str | None = None
    ) -> list[StudyActivitySchedule]:
        tracer = execution_context.get_opencensus_tracer()
        with tracer.span("StudyFlowchartService._get_study_activity_schedules"):
            return StudyActivityScheduleService(author=self.user).get_all_schedules(
                study_uid, study_value_version=study_value_version
            )

    def _get_study_visits(
        self, study_uid: str, study_value_version: str | None = None
    ) -> list[StudyVisit]:
        tracer = execution_context.get_opencensus_tracer()
        with tracer.span("StudyFlowchartService._get_study_visits"):
            return (
                StudyVisitService(self.user)
                .get_all_visits(study_uid, study_value_version=study_value_version)
                .items
            )

    def _get_study_footnotes(
        self, study_uid: str, study_value_version: str | None = None
    ) -> list[StudySoAFootnote]:
        tracer = execution_context.get_opencensus_tracer()
        with tracer.span("StudyFlowchartService._get_study_footnotes"):
            return (
                StudySoAFootnoteService(self.user)
                .get_all_by_study_uid(
                    study_uid,
                    sort_by={"order": True},
                    study_value_version=study_value_version,
                )
                .items
            )

    def _get_study_activities(
        self, study_uid: str, study_value_version: str | None = None
    ) -> list[StudySelectionActivity]:
        tracer = execution_context.get_opencensus_tracer()
        with tracer.span("StudyFlowchartService._get_study_activities"):
            return (
                StudyActivitySelectionService(author=self.user)
                .get_all_selection(
                    study_uid,
                    study_value_version=study_value_version,
                    sort_by={"order": True},
                )
                .items
            )

    @staticmethod
    def _sort_study_activities(
        study_selection_activities: list[StudySelectionActivity],
    ):
        """Sort StudySelectionActivities in place, grouping by SoAGroup, ActivityGroup, ActivitySubgroup"""

        soa_groups = {}
        activity_groups = {}
        activity_subgroups = {}
        order_keys = {}

        for activity in study_selection_activities:
            key = []
            key.append(
                soa_groups.setdefault(
                    activity.study_soa_group.soa_group_term_uid,
                    len(soa_groups)
                    if activity.study_soa_group.soa_group_term_uid
                    else -1,
                )
            )
            key.append(
                activity_groups.setdefault(
                    activity.study_activity_group.activity_group_uid,
                    len(activity_groups)
                    if activity.study_activity_group.activity_group_uid
                    else -1,
                )
            )
            key.append(
                activity_subgroups.setdefault(
                    activity.study_activity_subgroup.activity_subgroup_uid,
                    len(activity_subgroups),
                )
            )
            key.append(activity.order)
            order_keys[activity.study_activity_uid] = tuple(key)

        list.sort(
            study_selection_activities,
            key=lambda activity: order_keys.get(activity.study_activity_uid),
        )

    @staticmethod
    def _group_visits(
        visits: Iterable[StudyVisit],
    ) -> dict[str, dict[str, list[StudyVisit]]]:
        """
        Builds a graph of visits from nested dict of
        study_epoch_uid -> [ consecutive_visit_group | visit_uid ] -> [Visits]
        """

        grouped = {}
        visits: list[StudyVisit] = sorted(visits, key=lambda v: v.order)

        for visit in visits:
            grouped.setdefault(visit.study_epoch_uid, {}).setdefault(
                visit.consecutive_visit_group or visit.uid, []
            ).append(visit)

        return grouped

    @staticmethod
    def _mk_simple_footnotes(
        footnotes: Sequence[StudySoAFootnote],
    ) -> tuple[dict[str, list[str]], dict[str, Footnote]]:
        # mapping of referenced item uid to list of footnote symbols (to display in table cell)
        footnote_symbols_by_ref_uid: dict[str, list[str]] = {}

        # mapping of footnote symbols to SimpleFootnote model to print footnotes at end of document
        simple_footnotes_by_symbol: dict[str, Footnote] = {}
        for symbol, soa_footnote in enumerate_letters(footnotes):
            simple_footnotes_by_symbol[symbol] = SimpleFootnote(
                uid=soa_footnote.footnote.uid
                if soa_footnote.footnote
                else soa_footnote.footnote_template.uid,
                text_html=soa_footnote.footnote.name
                if soa_footnote.footnote
                else soa_footnote.footnote_template.name,
                text_plain=soa_footnote.footnote.name_plain
                if soa_footnote.footnote
                else soa_footnote.footnote_template.name_plain,
            )

            for ref in soa_footnote.referenced_items:
                footnote_symbols_by_ref_uid.setdefault(ref.item_uid, []).append(symbol)

        return footnote_symbols_by_ref_uid, simple_footnotes_by_symbol

    def get_flowchart_item_uid_coordinates(
        self, study_uid: str, study_value_version: str | None = None
    ) -> dict[str, tuple[int, int]]:
        """
        Returns mapping of item uid to [row, column] coordinates of item's position in the protocol SoA flowchart.

        Args:
            study_uid (str): The unique identifier of the study.
            study_value_version (str | None): The version of the study to check. Defaults to None.

        Returns:
            dict[str, tuple[int, int]: Mapping item uid to [row, column] coordinates
                                       of item's position in the protocol SoA flowchart.
        """

        self._validate_parameters(study_uid, study_value_version=study_value_version)

        study_activity_schedules: list[
            StudyActivitySchedule
        ] = self._get_study_activity_schedules(
            study_uid, study_value_version=study_value_version
        )

        # StudyActivitySchedules indexed by tuple of [StudyActivity.uid, StudyVisit.uid]
        study_activity_schedules_mapping = {
            (sas.study_activity_uid, sas.study_visit_uid): sas
            for sas in study_activity_schedules
        }

        study_selection_activities: list[
            StudySelectionActivity
        ] = self._get_study_activities(
            study_uid, study_value_version=study_value_version
        )

        self._sort_study_activities(study_selection_activities)

        visits: list[StudyVisit] = self._get_study_visits(
            study_uid, study_value_version=study_value_version
        )

        grouped_visits = self._group_visits(visits)

        coordinates = {}

        col = 1
        for study_epoch_uid, visit_groups in grouped_visits.items():
            coordinates[study_epoch_uid] = (0, col)
            for group in visit_groups.values():
                visit: StudyVisit = group[0]
                coordinates[visit.uid] = (1, col)
                col += 1

        row = 2

        prev_soa_group_uid = False
        prev_activity_group_uid = False
        prev_activity_subgroup_uid = False

        study_selection_activity: StudySelectionActivity
        for study_selection_activity in study_selection_activities:
            soa_group_uid = study_selection_activity.study_soa_group.soa_group_term_uid

            if soa_group_uid != prev_soa_group_uid:
                prev_soa_group_uid = soa_group_uid
                prev_activity_group_uid = False
                prev_activity_subgroup_uid = False

                coordinates[
                    study_selection_activity.study_soa_group.study_soa_group_uid
                ] = (row, 0)
                row += 1

            activity_group_uid = (
                study_selection_activity.study_activity_group.activity_group_uid
            )

            if prev_activity_group_uid != activity_group_uid:
                prev_activity_group_uid = activity_group_uid
                prev_activity_subgroup_uid = False

                coordinates[
                    study_selection_activity.study_activity_group.study_activity_group_uid
                ] = (row, 0)
                row += 1

            activity_subgroup_uid = (
                study_selection_activity.study_activity_subgroup.activity_subgroup_uid
            )

            if prev_activity_subgroup_uid != activity_subgroup_uid:
                prev_activity_subgroup_uid = activity_subgroup_uid

                coordinates[
                    study_selection_activity.study_activity_subgroup.study_activity_subgroup_uid
                ] = (row, 0)
                row += 1

            coordinates[study_selection_activity.study_activity_uid] = (
                row,
                0,
            )

            for visit in visits:
                study_activity_schedule: StudyActivitySchedule = (
                    study_activity_schedules_mapping.get(
                        (study_selection_activity.study_activity_uid, visit.uid)
                    )
                )

                if study_activity_schedule:
                    coordinates[study_activity_schedule.study_activity_schedule_uid] = (
                        row,
                        visit.order,
                    )

            row += 1

        return coordinates

    def get_flowchart_table(
        self,
        study_uid: str,
        time_unit: str,
        study_value_version: str | None = None,
    ) -> TableWithFootnotes:
        """
        Builds protocol SoA flowchart table

        Args:
            study_uid (str): The unique identifier of the study.
            time_unit (str): The preferred time unit, either "day" or "week".
            study_value_version (str | None): The version of the study to check. Defaults to None.

        Returns:
            TableWithFootnotes: Protocol SoA flowchart table with footnotes.
        """

        if not time_unit:
            time_unit = (
                StudyService(user=self.user)
                .get_study_preferred_time_unit(
                    study_uid,
                    for_protocol_soa=True,
                    study_value_version=study_value_version,
                )
                .time_unit_name
            )

        self._validate_parameters(
            study_uid, study_value_version=study_value_version, time_unit=time_unit
        )

        study_selection_activities: list[
            StudySelectionActivity
        ] = self._get_study_activities(
            study_uid, study_value_version=study_value_version
        )

        self._sort_study_activities(study_selection_activities)

        study_activity_schedules: list[
            StudyActivitySchedule
        ] = self._get_study_activity_schedules(
            study_uid, study_value_version=study_value_version
        )

        footnotes: list[StudySoAFootnote] = self._get_study_footnotes(
            study_uid, study_value_version=study_value_version
        )

        (
            footnote_symbols_by_ref_uid,
            simple_footnotes_by_symbol,
        ) = self._mk_simple_footnotes(footnotes)

        # visible visits
        visits = {
            visit.uid: visit
            for visit in self._get_study_visits(
                study_uid, study_value_version=study_value_version
            )
            if visit.show_visit and visit.study_epoch_name != config.BASIC_EPOCH_NAME
        }
        # group visits in nested dict: study_epoch_uid -> [ consecutive_visit_group |  visit_uid ] -> [Visits]
        grouped_visits = self._group_visits(visits.values())

        # first 4 rows of protocol SoA flowchart contains epochs & visits
        header_rows = self._get_header_rows(
            grouped_visits, time_unit, footnote_symbols_by_ref_uid
        )

        # activity rows with grouping headers and check-marks
        activity_rows = self._get_activity_rows(
            study_selection_activities,
            study_activity_schedules,
            grouped_visits,
            footnote_symbols_by_ref_uid,
        )

        table = TableWithFootnotes(
            rows=header_rows + activity_rows,
            num_header_rows=4,
            num_header_cols=1,
            footnotes=simple_footnotes_by_symbol,
            title=_("protocol_flowchart"),
        )

        return table

    @staticmethod
    def _get_header_rows(
        grouped_visits: dict[str, dict[str, list[StudyVisit]]],
        time_unit: str,
        footnote_symbols_by_ref_uid: Mapping[str, list[str]],
    ) -> list[TableRow]:
        """Builds the 4 header rows of protocol SoA flowchart"""

        rows = [TableRow() for _ in range(4)]

        # Header line-1: Epoch names
        rows[0].cells.append(TableCell(text=_("study_epoch"), style="header1"))

        # Header line-2: Visit names
        rows[1].cells.append(TableCell(text=_("visit_short_name"), style="header2"))

        # Header line-3: Visit timing day/week sequence
        if time_unit == "day":
            rows[2].cells.append(TableCell(text=_("study_day"), style="header3"))
        else:
            rows[2].cells.append(TableCell(text=_("study_week"), style="header3"))

        # Header line-4: Visit window
        rows[3].cells.append(TableCell(text=_("visit_window"), style="header4"))

        perv_study_epoch_uid = None
        for study_epoch_uid, visit_groups in grouped_visits.items():
            for group in visit_groups.values():
                visit: StudyVisit = group[0]

                # Open new Epoch column
                if perv_study_epoch_uid != study_epoch_uid:
                    perv_study_epoch_uid = study_epoch_uid

                    rows[0].cells.append(
                        TableCell(
                            text=visit.study_epoch_name,
                            span=len(visit_groups),
                            style="header1",
                            vertical=True,
                            refs=[
                                Ref(
                                    type_=SoAItemType.STUDY_EPOCH.value,
                                    uid=visit.study_epoch_uid,
                                )
                            ],
                            footnotes=footnote_symbols_by_ref_uid.get(
                                visit.study_epoch_uid
                            ),
                        )
                    )

                else:
                    # Add empty cells after Epoch cell with span > 1
                    rows[0].cells.append(TableCell(span=0))

                visit_timing = ""

                # Visit group
                if len(group) > 1:
                    visit_name = visit.consecutive_visit_group

                    if time_unit == "day":
                        if visit.study_day_number is not None:
                            visit_timing = f"{visit.study_day_number:d}-{group[-1].study_day_number:d}"
                    elif visit.study_week_number is not None:
                        visit_timing = f"{visit.study_week_number:d}-{group[-1].study_week_number:d}"

                # Single Visit
                else:
                    visit_name = visit.visit_short_name

                    if time_unit == "day":
                        if visit.study_day_number is not None:
                            visit_timing = f"{visit.study_day_number:d}"
                    elif visit.study_week_number is not None:
                        visit_timing = f"{visit.study_week_number:d}"

                # Visit name cell
                rows[1].cells.append(
                    TableCell(
                        visit_name,
                        style="header2",
                        refs=[
                            Ref(type_=SoAItemType.STUDY_VISIT.value, uid=vis.uid)
                            for vis in group
                        ],
                        footnotes=footnote_symbols_by_ref_uid.get(visit.uid),
                    )
                )

                # Visit timing cell
                rows[2].cells.append(TableCell(visit_timing, style="header3"))

                # Visit window
                visit_window = ""
                if None not in (
                    visit.min_visit_window_value,
                    visit.max_visit_window_value,
                ):
                    if (
                        visit.min_visit_window_value * -1
                        == visit.max_visit_window_value
                    ):
                        # plus-minus sign can be used
                        visit_window = f"±{visit.max_visit_window_value:d}"
                    else:
                        # plus and minus windows are different
                        visit_window = f"{visit.min_visit_window_value:+d}/{visit.max_visit_window_value:+d}"

                # Visit window cell
                rows[3].cells.append(TableCell(visit_window, style="header4"))

        return rows

    @classmethod
    def _get_activity_rows(
        cls,
        study_selection_activities: Sequence[StudySelectionActivity],
        study_activity_schedules: Sequence[StudyActivitySchedule],
        grouped_visits: dict[str, dict[str, list[StudyVisit]]],
        footnote_symbols_by_ref_uid: Mapping[str, list[str]],
    ) -> list[TableRow]:
        """Builds activity rows also adding various group header rows when required"""

        # Ordered StudyVisit.uids of visits to show (showing only the first visit of a consecutive_visit_group)
        visible_visit_uids_ordered = tuple(
            visit_group[0].uid
            for epochs_group in grouped_visits.values()
            for visit_group in epochs_group.values()
        )
        num_visits = len(visible_visit_uids_ordered)

        # StudyActivitySchedules indexed by tuple of [StudyActivity.uid, StudyVisit.uid]
        study_activity_schedules_mapping = {
            (sas.study_activity_uid, sas.study_visit_uid): sas
            for sas in study_activity_schedules
        }

        rows = []

        prev_soa_group_uid = False
        prev_activity_group_uid = False
        prev_activity_subgroup_uid = False

        study_selection_activity: StudySelectionActivity
        for study_selection_activity in study_selection_activities:
            soa_group_uid = study_selection_activity.study_soa_group.soa_group_term_uid

            if soa_group_uid != prev_soa_group_uid:
                prev_soa_group_uid = soa_group_uid
                prev_activity_group_uid = False
                prev_activity_subgroup_uid = False

                soa_row = cls._get_soa_group_row(
                    study_selection_activity,
                    footnote_symbols_by_ref_uid,
                    num_visits,
                )

                rows.append(soa_row)

            # Add Activity Group row
            activity_group_uid = (
                study_selection_activity.study_activity_group.activity_group_uid
            )

            if prev_activity_group_uid != activity_group_uid:
                prev_activity_group_uid = activity_group_uid
                prev_activity_subgroup_uid = False

                grp_row = cls._get_activity_group_row(
                    study_selection_activity,
                    footnote_symbols_by_ref_uid,
                    num_visits,
                )

                rows.append(grp_row)

            # Add Activity Sub-Group row
            activity_subgroup_uid = (
                study_selection_activity.study_activity_subgroup.activity_subgroup_uid
            )

            if prev_activity_subgroup_uid != activity_subgroup_uid:
                prev_activity_subgroup_uid = activity_subgroup_uid

                subgrp_row = cls._get_activity_subgroup_row(
                    study_selection_activity,
                    footnote_symbols_by_ref_uid,
                    num_visits,
                )

                rows.append(subgrp_row)

            # Start Activity row, will append cells visit-by-visit
            rows.append(
                row := TableRow(
                    hide=not study_selection_activity.show_activity_in_protocol_flowchart
                )
            )

            # Activity name cell (Activity row first column)
            row.cells.append(
                TableCell(
                    study_selection_activity.activity.name,
                    style="activity",
                    refs=[
                        Ref(
                            type_=SoAItemType.STUDY_ACTIVITY.value,
                            uid=study_selection_activity.study_activity_uid,
                        )
                    ],
                    footnotes=footnote_symbols_by_ref_uid.get(
                        study_selection_activity.study_activity_uid
                    ),
                )
            )

            # Iterate over the ordered list of visible Visit uids to see if the Activity was scheduled
            for study_visit_uid in visible_visit_uids_ordered:
                study_activity_schedule: StudyActivitySchedule = (
                    study_activity_schedules_mapping.get(
                        (study_selection_activity.study_activity_uid, study_visit_uid)
                    )
                )

                # Append a cell with tick-mark if Activity was scheduled
                if study_activity_schedule:
                    row.cells.append(
                        TableCell(
                            SOA_CHECK_MARK,
                            style="activitySchedule",
                            refs=[
                                Ref(
                                    type_=SoAItemType.STUDY_ACTIVITY_SCHEDULE.value,
                                    uid=study_activity_schedule.study_activity_schedule_uid,
                                )
                            ],
                            footnotes=footnote_symbols_by_ref_uid.get(
                                study_activity_schedule.study_activity_schedule_uid
                            ),
                        )
                    )

                # Append an empty cell if activity was not scheduled
                else:
                    row.cells.append(TableCell())
        return rows

    @staticmethod
    def _get_soa_group_row(
        study_selection_activity: StudySelectionActivity,
        footnote_symbols_by_ref_uid: Mapping[str, list[str]],
        num_visits: int,
    ) -> TableRow:
        """returns TableRow for SoA Group row"""

        row = TableRow(
            hide=not study_selection_activity.show_soa_group_in_protocol_flowchart
        )

        row.cells.append(
            TableCell(
                study_selection_activity.study_soa_group.soa_group_name,
                style="soaGroup",
                refs=[
                    Ref(
                        type_=SoAItemType.STUDY_SOA_GROUP.value,
                        uid=study_selection_activity.study_soa_group.study_soa_group_uid,
                    )
                ],
                footnotes=footnote_symbols_by_ref_uid.get(
                    study_selection_activity.study_soa_group.study_soa_group_uid
                ),
            )
        )

        # fill the row with empty cells for visits #
        row.cells += [TableCell() for _ in range(num_visits)]

        return row

    @staticmethod
    def _get_activity_group_row(
        study_selection_activity: StudySelectionActivity,
        footnote_symbols_by_ref_uid: Mapping[str, list[str]],
        num_visits: int,
    ) -> TableRow:
        """returns TableRow for Activity Group row"""

        group_name = (
            study_selection_activity.study_activity_group.activity_group_name
            if study_selection_activity.study_activity_group.activity_group_uid
            else _("no_study_group")
        )
        for a_g in study_selection_activity.activity.activity_groupings:
            if (
                a_g.activity_group_uid
                == study_selection_activity.study_activity_group.activity_group_uid
            ):
                group_name = a_g.activity_group_name
                break

        row = TableRow(
            hide=not study_selection_activity.show_activity_group_in_protocol_flowchart
        )

        row.cells.append(
            TableCell(
                group_name,
                style="group",
                refs=[
                    Ref(
                        type_=SoAItemType.STUDY_ACTIVITY_GROUP.value,
                        uid=study_selection_activity.study_activity_group.study_activity_group_uid,
                    )
                ]
                if study_selection_activity.study_activity_group.study_activity_group_uid
                else [],
                footnotes=footnote_symbols_by_ref_uid.get(
                    study_selection_activity.study_activity_group.study_activity_group_uid
                ),
            )
        )

        # fill the row with empty cells for visits #
        row.cells += [TableCell() for _ in range(num_visits)]

        return row

    @staticmethod
    def _get_activity_subgroup_row(
        study_selection_activity: StudySelectionActivity,
        footnote_symbols_by_ref_uid: Mapping[str, list[str]],
        num_visits: int,
    ) -> TableRow:
        """returns TableRow for Activity SubGroup row"""

        group_name = (
            study_selection_activity.study_activity_subgroup.activity_subgroup_name
            if study_selection_activity.study_activity_subgroup.activity_subgroup_uid
            else _("no_study_subgroup")
        )
        for a_g in study_selection_activity.activity.activity_groupings:
            if (
                a_g.activity_subgroup_uid
                == study_selection_activity.study_activity_subgroup.activity_subgroup_uid
            ):
                group_name = a_g.activity_subgroup_name
                break

        row = TableRow(
            hide=not study_selection_activity.show_activity_subgroup_in_protocol_flowchart
        )

        row.cells.append(
            TableCell(
                group_name,
                style="subGroup",
                refs=[
                    Ref(
                        type_=SoAItemType.STUDY_ACTIVITY_SUBGROUP.value,
                        uid=study_selection_activity.study_activity_subgroup.study_activity_subgroup_uid,
                    )
                ]
                if study_selection_activity.study_activity_subgroup.study_activity_subgroup_uid
                else [],
                footnotes=footnote_symbols_by_ref_uid.get(
                    study_selection_activity.study_activity_subgroup.study_activity_subgroup_uid
                ),
            )
        )

        # fill the row with empty cells for visits #
        row.cells += [TableCell() for _ in range(num_visits)]

        return row

    @staticmethod
    def show_hidden_rows(table: TableWithFootnotes):
        """Modify table in place to for detailed SoA"""

        row: TableRow
        for row in table.rows:
            # unhide all rows
            row.hide = False

    @staticmethod
    def propagate_hidden_rows(table: TableWithFootnotes):
        """
        Modify table in place to for Protocol SoA

        For hidden activity rows, up-propagate the crosses and footnotes onto the next visible group level.
        """

        soa_group_term_row = None
        activity_group_row = None
        activity_subgroup_row = None

        row: TableRow
        for row in table.rows:
            if not (row.cells and row.cells[0].refs):
                continue

            if row.cells[0].refs[0].type == SoAItemType.STUDY_SOA_GROUP.value:
                soa_group_term_row = row
                activity_group_row = None
                activity_subgroup_row = None

            elif row.cells[0].refs[0].type == SoAItemType.STUDY_ACTIVITY_GROUP.value:
                activity_group_row = row
                activity_subgroup_row = None

            elif row.cells[0].refs[0].type == SoAItemType.STUDY_ACTIVITY_SUBGROUP.value:
                activity_subgroup_row = row

            elif (
                row.hide
                and row.cells[0].refs[0].type == SoAItemType.STUDY_ACTIVITY.value
            ):
                update_row = None

                if activity_group_row and not activity_subgroup_row.hide:
                    update_row = activity_subgroup_row
                elif activity_group_row and not activity_group_row.hide:
                    update_row = activity_group_row
                elif soa_group_term_row and not soa_group_term_row.hide:
                    update_row = soa_group_term_row

                if update_row and len(update_row.cells) == len(row.cells):
                    cell: TableCell
                    for i, cell in enumerate(row.cells[1:], start=1):
                        update_cell: TableCell = update_row.cells[i]

                        update_cell.text = update_cell.text or cell.text

                        if cell.footnotes:
                            if update_cell.footnotes:
                                update_cell.footnotes = sorted(
                                    list(set(update_cell.footnotes + cell.footnotes))
                                )
                            else:
                                update_cell.footnotes = cell.footnotes.copy()

    @staticmethod
    def add_protocol_section_column(table: TableWithFootnotes):
        """Add Protocol Section column to table, updates table in place"""

        table.rows[0].cells.insert(
            1, TableCell(text=_("protocol_section"), style="header1", vertical=True)
        )

        row: TableRow
        for row in table.rows[1:]:
            row.cells.insert(1, TableCell())

    @staticmethod
    def add_coordinates(
        table: TableWithFootnotes, coordinates: Mapping[str, tuple[int, int]]
    ):
        """Append coordinates as if they were footnote references to each table cell"""
        for row in table.rows:
            for cell in row.cells:
                for ref in cell.refs:
                    if ref.uid in coordinates:
                        cell.footnotes = [
                            f"[{','.join(map(str, coordinates[ref.uid]))}]"
                        ]

    @staticmethod
    def download_detailed_soa_content(
        study_uid: str,
        study_value_version: str | None,
        protocol_flowchart: bool = False,
    ) -> list[dict]:
        if not study_value_version:
            query = "MATCH (study_root:StudyRoot{uid:$study_uid})-[has_version:LATEST]-(study_value:StudyValue)"
        else:
            query = "MATCH (study_root:StudyRoot{uid:$study_uid})-[has_version:HAS_VERSION {version:$study_value_version}]-(study_value:StudyValue)"
        query += """
            MATCH (schedule_audit)-[:AFTER]->(study_activity_schedule:StudyActivitySchedule)<-[:HAS_STUDY_ACTIVITY_SCHEDULE]-(study_value)
            MATCH (study_activity_schedule)<-[:STUDY_VISIT_HAS_SCHEDULE]-(study_visit:StudyVisit)<-[:HAS_STUDY_VISIT]-(study_value)
            MATCH (study_visit)<-[:STUDY_EPOCH_HAS_STUDY_VISIT]-(study_epoch:StudyEpoch)<-[:HAS_STUDY_EPOCH]-(study_value)
            MATCH (study_activity_schedule)<-[:STUDY_ACTIVITY_HAS_SCHEDULE]-(study_activity:StudyActivity)<-[:HAS_STUDY_ACTIVITY]-(study_value)
        """
        query += (
            "WHERE study_activity.show_activity_in_protocol_flowchart=true"
            if protocol_flowchart
            else ""
        )
        query += """
        WITH has_version,study_value, study_activity_schedule, study_visit, study_epoch, study_activity,
            head([(study_activity)-[:HAS_SELECTED_ACTIVITY]->(activity_value:ActivityValue) | activity_value]) as activity,
            head([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_SUBGROUP]->(:StudyActivitySubGroup)
                -[:HAS_SELECTED_ACTIVITY_SUBGROUP]->(activity_subgroup_value:ActivitySubGroupValue) | activity_subgroup_value]) as activity_subgroup,
            head([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_GROUP]->(:StudyActivityGroup)
                -[:HAS_SELECTED_ACTIVITY_GROUP]->(activity_group_value:ActivityGroupValue) | activity_group_value]) as activity_group,
            head([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_SOA_GROUP]->(:StudySoAGroup)
                -[:HAS_FLOWCHART_GROUP]->(:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]->(term_name_value:CTTermNameValue) 
                | term_name_value]) as term_name_value,
            head([(study_epoch)-[:HAS_EPOCH]->(:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]-
                (epoch_term:CTTermNameValue) | epoch_term.name]) as epoch_name
        ORDER BY schedule_audit.date
        RETURN
            CASE
                WHEN has_version.status = "RELEASED"
                THEN has_version.version
                ELSE "LATEST on "+apoc.temporal.format(datetime(), 'yyyy-MM-dd HH:mm:ss zzz')
            END as study_version,
            study_value.study_number AS study_number,
            study_visit.short_visit_label AS visit,
            epoch_name AS epoch,
            activity.name AS activity,
            activity_subgroup.name AS activity_subgroup,
            activity_group.name AS activity_group,
            term_name_value.name as soa_group
        """

        result_array, attribute_names = db.cypher_query(
            query,
            params={"study_uid": study_uid, "study_value_version": study_value_version},
        )
        content_rows = []
        for soa_content in result_array:
            content_dict = {}
            for content_prop, attribute_name in zip(soa_content, attribute_names):
                content_dict[attribute_name] = content_prop
            content_rows.append(content_dict)
        return content_rows

    @staticmethod
    def download_operational_soa_content(
        study_uid: str,
        study_value_version: str | None,
    ) -> list[dict]:
        if not study_value_version:
            query = "MATCH (study_root:StudyRoot{uid:$study_uid})-[has_version:LATEST]-(study_value:StudyValue)"
        else:
            query = "MATCH (study_root:StudyRoot{uid:$study_uid})-[has_version:HAS_VERSION {version:$study_value_version}]-(study_value:StudyValue)"
        query += """
            MATCH (schedule_audit)-[:AFTER]->(study_activity_schedule:StudyActivitySchedule)<-[:HAS_STUDY_ACTIVITY_SCHEDULE]-(study_value)
            MATCH (study_activity_schedule)<-[:STUDY_VISIT_HAS_SCHEDULE]-(study_visit:StudyVisit)<-[:HAS_STUDY_VISIT]-(study_value)
            MATCH (study_visit)<-[:STUDY_EPOCH_HAS_STUDY_VISIT]-(study_epoch:StudyEpoch)<-[:HAS_STUDY_EPOCH]-(study_value)
            MATCH (study_activity_schedule)<-[:STUDY_ACTIVITY_INSTANCE_HAS_SCHEDULE]-(study_activity_instance:StudyActivityInstance)
                <-[:HAS_STUDY_ACTIVITY_INSTANCE]-(study_value)
            MATCH (study_activity_instance)<-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_INSTANCE]-(study_activity:StudyActivity)
            WITH has_version,study_value, study_activity_schedule, study_visit, study_epoch, study_activity_instance, study_activity,
                head([(study_activity)-[:HAS_SELECTED_ACTIVITY]->(activity_value:ActivityValue) | activity_value]) as activity,
                head([(study_activity_instance)-[:HAS_SELECTED_ACTIVITY_INSTANCE]->(activity_instance_value:ActivityInstanceValue) | 
                    activity_instance_value]) as activity_instance,
                head([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_SUBGROUP]->(:StudyActivitySubGroup)
                    -[:HAS_SELECTED_ACTIVITY_SUBGROUP]->(activity_subgroup_value:ActivitySubGroupValue) | activity_subgroup_value]) as activity_subgroup,
                head([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_GROUP]->(:StudyActivityGroup)
                    -[:HAS_SELECTED_ACTIVITY_GROUP]->(activity_group_value:ActivityGroupValue) | activity_group_value]) as activity_group,
                head([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_SOA_GROUP]->(:StudySoAGroup)
                    -[:HAS_FLOWCHART_GROUP]->(:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]->(term_name_value:CTTermNameValue) 
                    | term_name_value]) as term_name_value,
                head([(study_epoch)-[:HAS_EPOCH]->(:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]-
                    (epoch_term:CTTermNameValue) | epoch_term.name]) as epoch_name
            ORDER BY schedule_audit.date
            RETURN
                CASE
                    WHEN has_version.status = "RELEASED"
                    THEN has_version.version
                    ELSE "LATEST on "+apoc.temporal.format(datetime(), 'yyyy-MM-dd HH:mm:ss zzz')
                END as study_version,
                study_value.study_number AS study_number,
                study_visit.short_visit_label AS visit,
                epoch_name AS epoch,
                activity.name AS activity,
                activity_instance.name AS activity_instance,
                activity_instance.topic_code AS topic_code,
                activity_instance.adam_param_code AS param_cd,
                activity_subgroup.name AS activity_subgroup,
                activity_group.name AS activity_group,
                term_name_value.name as soa_group
        """

        result_array, attribute_names = db.cypher_query(
            query,
            params={"study_uid": study_uid, "study_value_version": study_value_version},
        )
        content_rows = []
        for soa_content in result_array:
            content_dict = {}
            for content_prop, attribute_name in zip(soa_content, attribute_names):
                content_dict[attribute_name] = content_prop
            content_rows.append(content_dict)
        return content_rows
