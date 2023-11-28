import logging
from typing import Iterable, Mapping

from docx.enum.style import WD_STYLE_TYPE
from opencensus.trace import execution_context

from clinical_mdr_api import config
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
    "study_epoch": "Procedure",
    "visit_short_name": "Visit short name",
    "study_week": "Study week",
    "study_day": "Study day",
    "visit_window": "Visit window (days)",
    "protocol_flowchart": "Protocol Flowchart",
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
        to optional study_value_version. Raises ValidationException if time_unit is not "days" or "weeks".

        Args:
            study_uid (str): The unique identifier of the study.
            study_value_version (str | None): The version of the study to check. Defaults to None.
            time_unit (str): The preferred time unit, either "days" or "weeks".
        """
        StudyService(user=self.user).check_if_study_uid_and_version_exists(
            study_uid, study_value_version=study_value_version
        )

        if time_unit not in (None, "days", "weeks"):
            raise ValidationException("time_unit has to be 'days' or 'weeks'")

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
                .get_all_selection(study_uid, study_value_version=study_value_version)
                .items
            )

    @staticmethod
    def _group_study_activity_schedules(
        activities: Mapping[str, StudySelectionActivity],
        activity_schedules: Iterable[StudyActivitySchedule],
    ) -> dict[str, dict[str, dict[str, dict[str, list[StudySelectionActivity]]]]]:
        """
        Builds a graph of StudyActivitySchedules from nested dicts indexed by
        soa_group_term_uid -> activity_group_uid -> activity_subgroup_uid -> study_activity_uid -> study_visit_uid -> StudyActivitySchedule
        """

        grouped = {}

        # sort by activity order
        ordered_activity_schedules = sorted(
            activity_schedules, key=lambda sas: activities[sas.study_activity_uid].order
        )

        for study_activity_schedule in ordered_activity_schedules:
            study_selection_activity: StudySelectionActivity = activities[
                study_activity_schedule.study_activity_uid
            ]

            grouped.setdefault(
                study_selection_activity.study_soa_group.soa_group_term_uid, {}
            ).setdefault(
                study_selection_activity.study_activity_group.activity_group_uid, {}
            ).setdefault(
                study_selection_activity.study_activity_subgroup.activity_subgroup_uid,
                {},
            ).setdefault(
                study_selection_activity.study_activity_uid, {}
            )[
                study_activity_schedule.study_visit_uid
            ] = study_activity_schedule

        return grouped

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

        activity_schedules = self._get_study_activity_schedules(
            study_uid, study_value_version=study_value_version
        )

        activities = {
            a.study_activity_uid: a
            for a in self._get_study_activities(
                study_uid, study_value_version=study_value_version
            )
        }
        grouped_activities = self._group_study_activity_schedules(
            activities, activity_schedules
        )

        visits = {
            v.uid: v
            for v in self._get_study_visits(
                study_uid, study_value_version=study_value_version
            )
        }
        grouped_visits = self._group_visits(visits.values())

        coordinates = {}

        col = 1
        for study_epoch_uid, visit_groups in grouped_visits.items():
            coordinates[study_epoch_uid] = (0, col)
            for group in visit_groups.values():
                visit: StudyVisit = group[0]
                coordinates[visit.uid] = (1, col)
                col += 1

        row = 2
        prev_soa_group_term_uid = None
        prev_activity_group_uid = None
        prev_activity_subgroup_uid = None

        for soa_group_term_uid, soa_grouping in grouped_activities.items():
            for activity_group_uid, grouping in soa_grouping.items():
                for activity_subgroup_uid, subgrouping in grouping.items():
                    for study_activity_uid, activity_schedules in subgrouping.items():
                        study_selection_activity: StudySelectionActivity = activities[
                            study_activity_uid
                        ]

                        if soa_group_term_uid != prev_soa_group_term_uid:
                            prev_soa_group_term_uid = soa_group_term_uid

                            coordinates[
                                study_selection_activity.study_soa_group.study_soa_group_uid
                            ] = (row, 0)
                            row += 1

                        if prev_activity_group_uid != activity_group_uid:
                            prev_activity_group_uid = activity_group_uid

                            coordinates[
                                study_selection_activity.study_activity_group.study_activity_group_uid
                            ] = (row, 0)
                            row += 1

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

                        for study_activity_schedule in activity_schedules.values():
                            coordinates[
                                study_activity_schedule.study_activity_schedule_uid
                            ] = (
                                row,
                                visits[study_activity_schedule.study_visit_uid].order,
                            )

                        row += 1

        return coordinates

    def get_flowchart_table(
        self, study_uid: str, time_unit: str, study_value_version: str | None = None
    ) -> TableWithFootnotes:
        """
        Builds protocol SoA flowchart table

        Args:
            study_uid (str): The unique identifier of the study.
            time_unit (str): The preferred time unit, either "days" or "weeks".
            study_value_version (str | None): The version of the study to check. Defaults to None.

        Returns:
            TableWithFootnotes: Protocol SoA flowchart table with footnotes.
        """

        self._validate_parameters(
            study_uid, study_value_version=study_value_version, time_unit=time_unit
        )

        # uid mapping of activities for lookup from schedules
        activities = {
            a.study_activity_uid: a
            for a in self._get_study_activities(
                study_uid, study_value_version=study_value_version
            )
        }

        study_activity_schedules = self._get_study_activity_schedules(
            study_uid, study_value_version=study_value_version
        )
        # graph of StudyActivitySchedules nested dicts:  soa_group_term_uid -> activity_group_uid ->
        # -> activity_subgroup_uid -> study_activity_uid -> study_visit_uid -> StudyActivitySchedule
        grouped_activities = self._group_study_activity_schedules(
            activities, study_activity_schedules
        )

        # mapping of referenced item uid to list of footnote symbols (to display in table cell)
        footnote_symbols_by_ref_uid: dict[str, list[str]] = {}
        # mapping of footnote symbols to SimpleFootnote model to print footnotes at end of document
        simple_footnotes_by_symbol: dict[str, Footnote] = {}
        for symbol, soa_footnote in enumerate_letters(
            self._get_study_footnotes(
                study_uid, study_value_version=study_value_version
            )
        ):
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
            grouped_activities, grouped_visits, activities, footnote_symbols_by_ref_uid
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
        if time_unit == "days":
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
                            ref=Ref(type_="StudyEpoch", uid=visit.study_epoch_uid),
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

                    if time_unit == "days":
                        if visit.study_day_number is not None:
                            visit_timing = f"{visit.study_day_number:d}-{group[-1].study_day_number:d}"
                    elif visit.study_week_number is not None:
                        visit_timing = f"{visit.study_week_number:d}-{group[-1].study_week_number:d}"

                # Single Visit
                else:
                    visit_name = visit.visit_short_name

                    if time_unit == "days":
                        if visit.study_day_number is not None:
                            visit_timing = f"{visit.study_day_number:d}"
                    elif visit.study_week_number is not None:
                        visit_timing = f"{visit.study_week_number:d}"

                # Visit name cell
                rows[1].cells.append(
                    TableCell(
                        visit_name,
                        style="header2",
                        ref=Ref(type_="StudyVisit", uid=visit.uid),
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
        grouped_activities: dict[
            str, dict[str, dict[str, dict[str, list[StudySelectionActivity]]]]
        ],
        grouped_visits: dict[str, dict[str, list[StudyVisit]]],
        activities: Mapping[str, StudySelectionActivity],
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

        rows = []

        prev_soa_group_term_uid = None
        prev_activity_group_uid = None
        prev_activity_subgroup_uid = None

        for soa_group_term_uid, soa_grouping in grouped_activities.items():
            for activity_group_uid, grouping in soa_grouping.items():
                for activity_subgroup_uid, subgrouping in grouping.items():
                    for study_activity_uid, activity_schedules in subgrouping.items():
                        study_selection_activity: StudySelectionActivity = activities[
                            study_activity_uid
                        ]

                        # Add SoA Group header
                        if soa_group_term_uid != prev_soa_group_term_uid:
                            prev_soa_group_term_uid = soa_group_term_uid

                            soa_row = cls._get_soa_group_row(
                                study_selection_activity,
                                footnote_symbols_by_ref_uid,
                                num_visits,
                            )

                            rows.append(soa_row)

                        # Add Activity Group header
                        if prev_activity_group_uid != activity_group_uid:
                            prev_activity_group_uid = activity_group_uid

                            grp_row = cls._get_activity_group_row(
                                study_selection_activity,
                                footnote_symbols_by_ref_uid,
                                num_visits,
                            )

                            rows.append(grp_row)

                        # Add Activity Sub-Group header
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
                                ref=Ref(
                                    type_="StudyActivity",
                                    uid=study_selection_activity.study_activity_uid,
                                ),
                                footnotes=footnote_symbols_by_ref_uid.get(
                                    study_selection_activity.study_activity_uid
                                ),
                            )
                        )

                        # Iterate over the ordered list of visible Visit uids to see if the Activity was scheduled
                        for i, study_visit_uid in enumerate(visible_visit_uids_ordered):
                            study_activity_schedule: StudyActivitySchedule = (
                                activity_schedules.get(study_visit_uid)
                            )

                            # Append a cell with tick-mark if Activity was scheduled
                            if study_activity_schedule:
                                row.cells.append(
                                    TableCell(
                                        SOA_CHECK_MARK,
                                        style="activitySchedule",
                                        ref=Ref(
                                            type_="StudyActivitySchedule",
                                            uid=study_activity_schedule.study_activity_schedule_uid,
                                        ),
                                        footnotes=footnote_symbols_by_ref_uid.get(
                                            study_activity_schedule.study_activity_schedule_uid
                                        ),
                                    )
                                )

                                # If Activity row is hidden, add check-mark to the upper next visible activity group
                                # (practically overwrites the cell text at the given index in the act-group row)
                                if (
                                    not study_selection_activity.show_activity_in_protocol_flowchart
                                ):
                                    if (
                                        study_selection_activity.show_activity_subgroup_in_protocol_flowchart
                                    ):
                                        subgrp_row.cells[i + 1].text = SOA_CHECK_MARK
                                    elif (
                                        study_selection_activity.show_activity_group_in_protocol_flowchart
                                    ):
                                        grp_row.cells[i + 1].text = SOA_CHECK_MARK

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
                ref=Ref(
                    type_="CTTermName",
                    uid=study_selection_activity.study_soa_group.study_soa_group_uid,
                ),
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

        group_name = study_selection_activity.study_activity_group.activity_group_uid
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
                ref=Ref(
                    type_="StudyActivityGroup",
                    uid=study_selection_activity.study_activity_group.study_activity_group_uid,
                ),
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
            study_selection_activity.study_activity_subgroup.study_activity_subgroup_uid
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
                ref=Ref(
                    type_="StudyActivitySubGroup",
                    uid=study_selection_activity.study_activity_subgroup.study_activity_subgroup_uid,
                ),
                footnotes=footnote_symbols_by_ref_uid.get(
                    study_selection_activity.study_activity_subgroup.study_activity_subgroup_uid
                ),
            )
        )

        # fill the row with empty cells for visits #
        row.cells += [TableCell() for _ in range(num_visits)]

        return row
