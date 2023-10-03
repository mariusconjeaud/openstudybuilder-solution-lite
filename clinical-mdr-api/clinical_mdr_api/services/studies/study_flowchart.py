import logging
import sys
from collections import defaultdict
from itertools import count
from typing import Iterable, Mapping, Sequence

import yattag
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Inches
from opencensus.trace import execution_context

from clinical_mdr_api import config
from clinical_mdr_api.models import (
    CTTermName,
    StudyActivitySchedule,
    StudySelectionActivity,
    StudyVisit,
)
from clinical_mdr_api.models.study_selections.table_with_headers import (
    TableHeader,
    TableWithHeaders,
)
from clinical_mdr_api.services.controlled_terminologies.ct_term_name import (
    CTTermNameService,
)
from clinical_mdr_api.services.studies.study_activity_schedule import (
    StudyActivityScheduleService,
)
from clinical_mdr_api.services.studies.study_activity_selection import (
    StudyActivitySelectionService,
)
from clinical_mdr_api.services.studies.study_visit import StudyVisitService
from clinical_mdr_api.services.utils.docx_builder import DocxBuilder

# TODO LOCALIZATION
_ = {
    "study_epoch": "Study epoch",
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
    "fchGroup": ("Table lvl 1", WD_STYLE_TYPE.PARAGRAPH),
    "group": ("Table lvl 2", WD_STYLE_TYPE.PARAGRAPH),
    "subGroup": ("Table lvl 3", WD_STYLE_TYPE.PARAGRAPH),
    "activity": ("Table lvl 4", WD_STYLE_TYPE.PARAGRAPH),
    "cell": ("Table Text", WD_STYLE_TYPE.PARAGRAPH),
}


class ActivityRow:
    def __init__(self, level, uid, name, selection_uid=None, show=True):
        self.level = level
        self.uid = uid
        self.selection_uid = selection_uid
        self.name = name
        self.shown = int(show)
        self.cells = defaultdict(int)


class StudyFlowchartService:
    """Assemble and visualize Study Protocol Flowchart data"""

    def __init__(self, current_user_id: str) -> None:
        self._current_user_id = current_user_id
        self._epoch_terms = None

    def get_epoch_ct_term_names(self) -> Sequence[CTTermName]:
        tracer = execution_context.get_opencensus_tracer()
        with tracer.span("StudyFlowchartService.get_epoch_ct_term_names"):
            return (
                CTTermNameService(user=self._current_user_id)
                .get_all_ct_terms(codelist_name="Epoch")
                .items
            )

    def get_study_activity_schedules(
        self, study_uid: str
    ) -> Sequence[StudyActivitySchedule]:
        tracer = execution_context.get_opencensus_tracer()
        with tracer.span("StudyFlowchartService.get_study_activity_schedules"):
            return StudyActivityScheduleService(
                author=self._current_user_id
            ).get_all_schedules(study_uid)

    def get_study_visits(self, study_uid: str) -> Sequence[StudyVisit]:
        tracer = execution_context.get_opencensus_tracer()
        with tracer.span("StudyFlowchartService.get_study_visits"):
            result = (
                StudyVisitService(self._current_user_id).get_all_visits(study_uid).items
            )
            return [
                study_visit
                for study_visit in result
                if study_visit.study_epoch_name != config.BASIC_EPOCH_NAME
            ]

    @staticmethod
    def iter_visits_grouped(study_visits: Sequence[StudyVisit]):
        visit_group = []

        for visit in study_visits:
            if not visit_group:
                visit_group = [visit]

            elif (
                visit_group[0].consecutive_visit_group
                and visit_group[0].consecutive_visit_group
                == visit.consecutive_visit_group
            ):
                visit_group.append(visit)

            else:
                yield visit_group
                visit_group = [visit]

        if visit_group:
            yield visit_group

    def get_study_activities(self, study_uid: str) -> Sequence[StudySelectionActivity]:
        tracer = execution_context.get_opencensus_tracer()
        with tracer.span("StudyFlowchartService.get_study_activities"):
            return (
                StudyActivitySelectionService(author=self._current_user_id)
                .get_all_selection(study_uid)
                .items
            )

    @property
    def epoch_terms(self) -> Mapping[str, CTTermName]:
        """Returns a dict of Objects of Epoch term names indexed by term_uid"""
        if self._epoch_terms is None:
            self._epoch_terms = {t.term_uid: t for t in self.get_epoch_ct_term_names()}
        return self._epoch_terms

    def get_docx_document(self, study_uid: str, time_unit: str) -> DocxBuilder:
        table = self.get_table(study_uid, time_unit)
        assert len(table.headers)

        tracer = execution_context.get_opencensus_tracer()
        with tracer.span("StudyFlowchartService._build_docx_document"):
            docx = DocxBuilder(
                styles=DOCX_STYLES, landscape=True, margins=[0.5, 0.5, 0.5, 0.5]
            )
            # Create table with actual number of columns and rows for all headers
            tablex = docx.create_table(
                num_rows=len(table.headers), num_columns=len(table.headers[0].data) - 1
            )

            # Set width of first column
            tablex.columns[0].width = Inches(4)

            # Update header rows
            for r, header in enumerate(table.headers):
                rowx = tablex.rows[r]
                style, span = header.data.pop(0), header.spans.pop(0)

                prev_cell = None
                for txt, span, c in zip(header.data, header.spans, count()):
                    cellx = rowx.cells[c]

                    if span == 0 and prev_cell:
                        # Merge cell with previous cell, will preserve the paragraph (text) from the previous one
                        cellx = prev_cell.merge(cellx)

                    else:
                        cellx.text = txt
                        if r == 0 and c > 0:
                            # Text flow in first header row is vertical except first column
                            docx.set_vertical_cell_direction(cellx, "btLr")

                    prev_cell = cellx

                # Apply paragraph style on all cells of the row
                docx.format_row(rowx, [DOCX_STYLES[style][0]] * len(rowx.cells))

                # Set row to repeat after a page break
                docx.repeat_table_header(rowx)

            # Append data rows
            for data in table.data:
                rowx = docx.add_row(tablex, data[1:])
                # Look up actual style name, style of first column is the first member of data, "cell" otherwise
                docx.format_row(
                    rowx,
                    [DOCX_STYLES[data[0]][0]]
                    + [DOCX_STYLES["cell"][0]] * (len(data) - 2),
                )

            return docx

    def get_html_document(self, study_uid: str, time_unit: str) -> str:
        table = self.get_table(study_uid, time_unit)

        tracer = execution_context.get_opencensus_tracer()
        with tracer.span("StudyFlowchartService._build_html_document"):
            doc, tag, _text, line = yattag.Doc().ttl()
            doc.asis("<!DOCTYPE html>")

            with tag("html", lang="en"):
                with tag("head"):
                    line("title", _("protocol_flowchart"))

                with tag("body"):
                    with tag("table", id="ProtocolFlowchartTable"):
                        with tag("thead"):
                            for header in table.headers:
                                klass, span = header.data.pop(0), header.spans.pop(0)
                                with tag("tr", klass=klass):
                                    for cell, span in zip(header.data, header.spans):
                                        if span == 0:
                                            continue
                                        if span > 1:
                                            line("th", cell, colspan=span)
                                        else:
                                            line("th", cell)

                        with tag("tbody"):
                            for row in table.data:
                                with tag("tr", klass=row.pop(0)):
                                    for i, cell in enumerate(row):
                                        line(("td" if i else "th"), str(cell))

            return yattag.indent(doc.getvalue())

    def get_table(
        self, study_uid: str, time_unit: str, use_uid_instead_of_name: bool = False
    ) -> TableWithHeaders:
        tracer = execution_context.get_opencensus_tracer()
        with tracer.span("StudyFlowchartService.get_table"):
            study_visits_grouped = tuple(
                self.iter_visits_grouped(self.get_study_visits(study_uid))
            )

            headers = self.get_table_headers(
                study_visits_grouped, time_unit, use_uid_instead_of_name
            )
            study_activities = self.get_study_activities(study_uid)

            activity_schedules = defaultdict(list)
            for schedule in self.get_study_activity_schedules(study_uid):
                activity_schedules[schedule.study_activity_uid].append(
                    (schedule.study_visit_uid, schedule.study_activity_schedule_uid)
                )

            activity_rows = self.get_activity_rows(
                study_activities, activity_schedules, use_uid_instead_of_name
            )

            data_rows = []
            for act_row in activity_rows:
                if use_uid_instead_of_name:
                    data_rows.append(
                        [
                            act_row.selection_uid
                            if act_row.selection_uid
                            else act_row.uid
                        ]
                        + [
                            act_row.cells.get(visit[0].uid) or ""
                            for visit in study_visits_grouped
                        ]
                    )
                elif act_row.shown:
                    data_rows.append(
                        [act_row.level, act_row.name]
                        + [
                            act_row.cells.get(visit[0].uid) and "X" or ""
                            for visit in study_visits_grouped
                        ]
                    )

            return TableWithHeaders(headers=headers, data=data_rows)

    def get_table_headers(
        self,
        study_visits_grouped: Iterable[list[StudyVisit]],
        time_unit: str,
        use_uid_instead_of_name: bool = False,
    ) -> list[TableHeader]:
        """Returns a list of TableHeaders for Study Flowchart table"""
        headers = [TableHeader(data=[f"header{i + 1}"], spans=[1]) for i in range(4)]

        # First column of headers
        headers[0].append(_("study_epoch"))
        headers[1].append(_("visit_short_name"))
        if time_unit == "days":
            headers[2].append(_("study_day"))
        else:
            headers[2].append(_("study_week"))
        headers[3].append(_("visit_window"))

        # For each visit as a column, append a cell to each of the header rows
        last_epoch_uid = None
        for group in study_visits_grouped:
            visit = group[0]
            visit_timing = ""

            if len(group) > 1:
                visit_name = f"{visit.visit_short_name} - {group[-1].visit_short_name}"

                if time_unit == "days":
                    if visit.study_day_number is not None:
                        visit_timing = (
                            f"{visit.study_day_number:d}-{group[-1].study_day_number:d}"
                        )
                elif visit.study_week_number is not None:
                    visit_timing = (
                        f"{visit.study_week_number:d}-{group[-1].study_week_number:d}"
                    )

            else:
                visit_name = visit.visit_short_name

                if time_unit == "days":
                    if visit.study_day_number is not None:
                        visit_timing = f"{visit.study_day_number:d}"
                elif visit.study_week_number is not None:
                    visit_timing = f"{visit.study_week_number:d}"

            if visit.epoch_uid == last_epoch_uid:
                # Same epoch as in the previous column
                headers[0].append("", span=0)

            else:
                # Use Epoch term names
                try:
                    if not use_uid_instead_of_name:
                        headers[0].append(
                            self.epoch_terms[visit.epoch_uid].sponsor_preferred_name
                        )
                    else:
                        headers[0].append(visit.study_epoch_uid)
                except KeyError:
                    log.warning(
                        "Epoch UID '%s' was not found in epoch terms", visit.epoch_uid
                    )
                    headers[0].append(visit.visit_type_name)

            last_epoch_uid = visit.epoch_uid
            if not use_uid_instead_of_name:
                headers[1].append(visit_name)
            else:
                headers[1].append(visit.uid)

            headers[2].append(visit_timing)

            visit_window = ""
            if None not in (visit.min_visit_window_value, visit.max_visit_window_value):
                if visit.min_visit_window_value * -1 == visit.max_visit_window_value:
                    visit_window = f"±{visit.max_visit_window_value:d}"
                else:
                    visit_window = f"{visit.min_visit_window_value:+d}/{visit.max_visit_window_value:+d}"
            headers[3].append(visit_window)

        return headers

    @staticmethod
    def sort_study_activities(study_activities: Sequence[StudySelectionActivity]):
        """
        Returns a list of sorted StudyActivities

        Study activities are sorted by flowchart_group -> activity_group -> activity_subgroup
        """
        # sort list of study activities to group them by flowchart_group->activity_group->activity_subgroup
        uniq_flowchart_groups = defaultdict(dict)

        for study_activity in study_activities:
            flowchart_group = study_activity.flowchart_group.term_uid
            uniq_flowchart_groups[flowchart_group].setdefault(
                "order", len(uniq_flowchart_groups)
            )
            # the sort order of activity_groups and activity_subgroups is kept for each flowchart_group
            # because we may have the same activity_subgroups, activity_groups for different flowchart_group
            uniq_flowchart_groups[flowchart_group].setdefault("groups_order", dict())
            uniq_flowchart_groups[flowchart_group].setdefault("subgroups_order", dict())

            # create list of unique activity_groups in the order they should be sorted
            if study_activity.activity.activity_groupings:
                for grouping in study_activity.activity.activity_groupings:
                    activity_group = grouping.activity_group_uid
                    uniq_flowchart_groups[flowchart_group]["groups_order"].setdefault(
                        activity_group,
                        len(uniq_flowchart_groups[flowchart_group]["groups_order"]),
                    )

            # create list of unique activity_subgroups in the order they should be sorted
            if study_activity.activity.activity_groupings:
                for grouping in study_activity.activity.activity_groupings:
                    activity_subgroup = grouping.activity_subgroup_uid
                    uniq_flowchart_groups[flowchart_group][
                        "subgroups_order"
                    ].setdefault(
                        activity_subgroup,
                        len(uniq_flowchart_groups[flowchart_group]["subgroups_order"]),
                    )

        return sorted(
            study_activities,
            key=lambda sa: (
                uniq_flowchart_groups[sa.flowchart_group.term_uid]["order"],
                uniq_flowchart_groups[sa.flowchart_group.term_uid]["groups_order"][
                    sa.activity.activity_groupings[0].activity_group_uid
                ]
                if sa.activity.activity_groupings
                else sys.maxsize,
                uniq_flowchart_groups[sa.flowchart_group.term_uid]["subgroups_order"][
                    sa.activity.activity_groupings[0].activity_subgroup_uid
                ]
                if sa.activity.activity_groupings
                else sys.maxsize,
            ),
        )

    @staticmethod
    def get_activity_rows(
        study_activities: Sequence[StudySelectionActivity],
        activity_schedules: Mapping[str, Sequence[str]],
        use_uid_instead_of_name: bool,
    ) -> list[ActivityRow]:
        """
        Returns a list of ActivityRows

        Includes all study_activity activities, but also adding parent groups before, when they change or new
        """
        rows = []
        fch_group, ass_group, ass_subgroup = None, None, None

        study_activities = StudyFlowchartService.sort_study_activities(
            study_activities=study_activities
        )

        for study_activity in study_activities:
            # Create a row for Flowchart group if not yet created
            grp = study_activity.flowchart_group
            if grp and (not fch_group or grp.term_uid != fch_group.uid):
                ass_group = None
                ass_subgroup = None

                fch_group = ActivityRow(
                    level="fchGroup",
                    uid=grp.term_uid,
                    name=grp.sponsor_preferred_name,
                    show=True,
                )
                rows.append(fch_group)

            # Create a row for Activity group if not yet created
            study_activity_group = study_activity.study_activity_group
            if study_activity_group.study_activity_group_uid:
                if (
                    not ass_group
                    or study_activity_group.activity_group_uid != ass_group.uid
                ):
                    ass_subgroup = None

                    show = study_activity.show_activity_group_in_protocol_flowchart
                    ass_group = ActivityRow(
                        level="group",
                        uid=study_activity_group.activity_group_uid,
                        name=study_activity_group.activity_group_name,
                        show=show,
                        selection_uid=study_activity_group.study_activity_group_uid
                        if study_activity_group.study_activity_group_uid
                        else None,
                    )
                    rows.append(ass_group)

            # Create a row for Activity subgroup if not yet created
            study_activity_subgroup = study_activity.study_activity_subgroup
            if study_activity_subgroup.study_activity_subgroup_uid:
                if (
                    not ass_subgroup
                    or study_activity_subgroup.activity_subgroup_uid != ass_subgroup.uid
                ):
                    show = study_activity.show_activity_subgroup_in_protocol_flowchart
                    ass_subgroup = ActivityRow(
                        level="subGroup",
                        uid=study_activity_subgroup.activity_subgroup_uid,
                        name=study_activity_subgroup.activity_subgroup_name,
                        show=show,
                        selection_uid=study_activity_subgroup.study_activity_subgroup_uid
                        if study_activity_subgroup.study_activity_subgroup_uid
                        else None,
                    )
                    rows.append(ass_subgroup)

            # Create a row for the Activity
            activity = study_activity.activity
            show = study_activity.show_activity_in_protocol_flowchart
            ass = ActivityRow(
                level="activity",
                uid=activity.uid,
                name=activity.name,
                show=show,
                selection_uid=study_activity.study_activity_uid,
            )
            rows.append(ass)

            # Tick cells for scheduled visits, and also tick for parent groups if activity is hidden
            for study_visit_uid, study_activity_schedule_uid in activity_schedules.get(
                study_activity.study_activity_uid, []
            ):
                if use_uid_instead_of_name:
                    ass.cells[study_visit_uid] = study_activity_schedule_uid
                else:
                    ass.cells[study_visit_uid] += 1
                if not show:
                    if ass_subgroup and ass_subgroup.shown:
                        ass_subgroup.cells[study_visit_uid] += 1
                    elif ass_group and ass_group.shown:
                        ass_group.cells[study_visit_uid] += 1

        return rows
