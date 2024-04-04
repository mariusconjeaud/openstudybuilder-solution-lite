# pylint: disable=too-many-lines

import datetime
from copy import deepcopy

import pytest

from clinical_mdr_api import config
from clinical_mdr_api.domains.study_selections.study_soa_footnote import SoAItemType
from clinical_mdr_api.models import (
    Activity,
    Footnote,
    Library,
    StudyActivitySchedule,
    StudySelectionActivity,
    StudyVisit,
)
from clinical_mdr_api.models.concepts.activities.activity import (
    ActivityGroupingHierarchySimpleModel,
)
from clinical_mdr_api.models.study_selections.study_selection import (
    SimpleStudyActivityGroup,
    SimpleStudyActivitySubGroup,
    SimpleStudySoAGroup,
)
from clinical_mdr_api.models.study_selections.study_soa_footnote import (
    ReferencedItem,
    StudySoAFootnote,
)
from clinical_mdr_api.models.syntax_instances.footnote import FootnoteTemplateWithType
from clinical_mdr_api.services.studies.study_flowchart import StudyFlowchartService
from clinical_mdr_api.services.utils.table_f import (
    Ref,
    SimpleFootnote,
    TableCell,
    TableRow,
    TableWithFootnotes,
)

USER_INITIALS = "unknown-user"


class MockStudyFlowchartService(StudyFlowchartService):
    def _get_study_visits(self, *_args, **_kwargs):
        return STUDY_VISITS

    def _get_study_activities(self, *_args, **_kwargs):
        return STUDY_ACTIVITIES

    def _get_study_activity_schedules(self, *_args, **_kwargs):
        return STUDY_ACTIVITY_SCHEDULES

    def _get_study_footnotes(self, *_args, **_kwargs):
        return FOOTNOTES

    def _validate_parameters(self, *_args, **_kwargs):
        pass


# pylint: disable=redefined-outer-name
@pytest.fixture(scope="module")
def study_flowchart_service():
    return MockStudyFlowchartService(USER_INITIALS)


def test_get_flowchart_item_uid_coordinates(study_flowchart_service):
    coordinates = study_flowchart_service.get_flowchart_item_uid_coordinates(
        study_uid=""
    )
    assert coordinates == COORDINATES


def test_group_visits(study_flowchart_service):
    visits = study_flowchart_service._get_study_visits()
    grouped_visits = study_flowchart_service._group_visits(visits)

    count_visits = 0
    for study_epoch_uid, epoch_grouping in grouped_visits.items():
        assert isinstance(study_epoch_uid, str)
        assert isinstance(epoch_grouping, dict)

        for visit_group_id, visit_group in epoch_grouping.items():
            assert isinstance(visit_group_id, str)
            assert isinstance(visit_group, list)

            for visit in visit_group:
                count_visits += 1

                assert isinstance(visit, StudyVisit)
                assert study_epoch_uid == visit.study_epoch_uid

                if len(visit_group) == 1:
                    assert visit_group_id == visit.uid
                else:
                    assert visit_group_id == visit.consecutive_visit_group

    assert count_visits == len(visits)


def test_mk_simple_footnotes(study_flowchart_service):
    footnotes: list[StudySoAFootnote] = study_flowchart_service._get_study_footnotes()
    (
        footnote_symbols_by_ref_uid,
        simple_footnotes_by_symbol,
    ) = study_flowchart_service._mk_simple_footnotes(footnotes)

    assert simple_footnotes_by_symbol == EXPECTED_SOA_TABLE.footnotes

    footnotes_uid_to_symbol_mapping = {
        simple_footnote.uid: symbol
        for symbol, simple_footnote in simple_footnotes_by_symbol.items()
    }

    count_references = 0
    for soa_footnote in footnotes:
        assert soa_footnote.footnote.uid in footnotes_uid_to_symbol_mapping
        symbol = footnotes_uid_to_symbol_mapping[soa_footnote.footnote.uid]
        for ref in soa_footnote.referenced_items:
            assert ref.item_uid in footnote_symbols_by_ref_uid
            assert symbol in footnote_symbols_by_ref_uid[ref.item_uid]
            count_references += 1

    assert count_references == sum(
        len(symbols) for symbols in footnote_symbols_by_ref_uid.values()
    )


@pytest.mark.parametrize("time_unit", ["day", "week"])
def test_get_header_rows(study_flowchart_service, time_unit):
    visits = [
        visit
        for visit in study_flowchart_service._get_study_visits()
        if visit.show_visit and visit.study_epoch_name != config.BASIC_EPOCH_NAME
    ]
    grouped_visits = study_flowchart_service._group_visits(visits)

    header_rows = study_flowchart_service._get_header_rows(
        grouped_visits, time_unit=time_unit, footnote_symbols_by_ref_uid={}
    )

    visits = [
        visit_group[0]
        for epoch_grouping in grouped_visits.values()
        for visit_group in epoch_grouping.values()
    ]

    assert len(header_rows) == 4

    for _r, row in enumerate(header_rows):
        assert row.hide is False

        if _r == 0:
            assert (
                len([cell.span for cell in row.cells if cell.span > 0])
                == len(grouped_visits) + 1
            ), "Epoch count mismatch"
        else:
            assert (
                sum(cell.span for cell in row.cells)
                == sum(len(epoch_group) for epoch_group in grouped_visits.values()) + 1
            ), "Visit row count mismatch"

        if _r == 1:
            for _c, cell in enumerate(row.cells[1:]):
                visit = visits[_c]
                assert (
                    cell.text == visit.consecutive_visit_group or visit.visit_short_name
                ), "Error in visit name"

        if _r == 2:
            for _c, cell in enumerate(row.cells[1:]):
                visit = visits[_c]
                if not visit.consecutive_visit_group:
                    expected = (
                        visit.study_day_number
                        if time_unit == "day"
                        else visit.study_week_number
                    )
                    assert cell.text == f"{expected:d}", "Error in day/week number"


def test_get_flowchart_table(study_flowchart_service):
    table = study_flowchart_service.get_flowchart_table(study_uid="", time_unit="day")

    assert table.num_header_rows == EXPECTED_SOA_TABLE.num_header_rows
    assert table.num_header_cols == EXPECTED_SOA_TABLE.num_header_cols
    assert table.title == EXPECTED_SOA_TABLE.title
    assert table.footnotes == EXPECTED_SOA_TABLE.footnotes

    assert table.dict() == EXPECTED_SOA_TABLE.dict()


def test_propagate_hidden_rows():
    table = deepcopy(EXPECTED_SOA_TABLE)
    StudyFlowchartService.propagate_hidden_rows(table)
    assert table.dict() == EXPECTED_PROTOCOL_SOA_TABLE


def test_show_hidden_rows():
    table = deepcopy(EXPECTED_SOA_TABLE)
    StudyFlowchartService.show_hidden_rows(table)

    assert table.num_header_rows == EXPECTED_SOA_TABLE.num_header_rows
    assert table.num_header_cols == EXPECTED_SOA_TABLE.num_header_cols
    assert table.title == EXPECTED_SOA_TABLE.title
    assert table.footnotes == EXPECTED_SOA_TABLE.footnotes
    assert len(table.rows) == len(EXPECTED_SOA_TABLE.rows)

    row: TableRow
    for row, expected_row in zip(table.rows, EXPECTED_SOA_TABLE.rows):
        assert row.cells == expected_row.cells
        assert row.hide is False


STUDY_VISITS = [
    StudyVisit(
        study_epoch_uid="StudyEpoch_000004",
        visit_type_uid="CTTerm_000182",
        time_reference_uid="CTTerm_000122",
        time_value=-14,
        time_unit_uid="UnitDefinition_000364",
        visit_sublabel_codelist_uid=None,
        visit_sublabel_reference=None,
        legacy_visit_id=None,
        legacy_visit_type_alias=None,
        legacy_name=None,
        legacy_subname=None,
        consecutive_visit_group=None,
        show_visit=True,
        min_visit_window_value=0,
        max_visit_window_value=0,
        visit_window_unit_uid="UnitDefinition_000364",
        description=None,
        start_rule=None,
        end_rule=None,
        visit_contact_mode_uid="CTTerm_000081",
        epoch_allocation_uid=None,
        visit_class="SINGLE_VISIT",
        visit_subclass="SINGLE_VISIT",
        is_global_anchor_visit=False,
        uid="StudyVisit_000012",
        study_uid="Study_000002",
        study_epoch_name="Screening",
        epoch_uid="C48262_SCREENING",
        order=1,
        visit_type_name="Screening",
        time_reference_name="Global anchor visit",
        time_unit_name="days",
        visit_contact_mode_name="On Site Visit",
        epoch_allocation_name=None,
        duration_time=-1209600.0,
        duration_time_unit="UnitDefinition_000364",
        study_day_number=-14,
        study_duration_days_label="-15 days",
        study_day_label="Day -14",
        study_week_number=-2,
        study_duration_weeks_label="-3 weeks",
        week_in_study_label="Week -3",
        study_week_label="Week -2",
        visit_number=1,
        visit_subnumber=0,
        unique_visit_number=100,
        visit_subname="Visit 1",
        visit_sublabel=None,
        visit_name="Visit 1",
        visit_short_name="V1",
        visit_window_unit_name="days",
        status="DRAFT",
        start_date=datetime.datetime(
            2023, 9, 25, 11, 41, 55, 138405, tzinfo=datetime.timezone.utc
        ),
        end_date=None,
        user_initials="unknown-user",
        possible_actions=["edit", "delete", "lock"],
        study_activity_count=22,
        change_type=None,
    ),
    StudyVisit(
        study_epoch_uid="StudyEpoch_000005",
        visit_type_uid="CTTerm_000184",
        time_reference_uid="CTTerm_000122",
        time_value=-3,
        time_unit_uid="UnitDefinition_000364",
        visit_sublabel_codelist_uid=None,
        visit_sublabel_reference=None,
        legacy_visit_id=None,
        legacy_visit_type_alias=None,
        legacy_name=None,
        legacy_subname=None,
        consecutive_visit_group=None,
        show_visit=True,
        min_visit_window_value=0,
        max_visit_window_value=0,
        visit_window_unit_uid="UnitDefinition_000364",
        description=None,
        start_rule=None,
        end_rule=None,
        visit_contact_mode_uid="CTTerm_000081",
        epoch_allocation_uid=None,
        visit_class="SINGLE_VISIT",
        visit_subclass="SINGLE_VISIT",
        is_global_anchor_visit=False,
        uid="StudyVisit_000013",
        study_uid="Study_000002",
        study_epoch_name="Run-in",
        epoch_uid="C98779_RUN-IN",
        order=2,
        visit_type_name="Start of run-in",
        time_reference_name="Global anchor visit",
        time_unit_name="days",
        visit_contact_mode_name="On Site Visit",
        epoch_allocation_name=None,
        duration_time=-259200.0,
        duration_time_unit="UnitDefinition_000364",
        study_day_number=-3,
        study_duration_days_label="-4 days",
        study_day_label="Day -3",
        study_week_number=1,
        study_duration_weeks_label="0 weeks",
        week_in_study_label="Week 0",
        study_week_label="Week 1",
        visit_number=2,
        visit_subnumber=0,
        unique_visit_number=200,
        visit_subname="Visit 2",
        visit_sublabel=None,
        visit_name="Visit 2",
        visit_short_name="V2",
        visit_window_unit_name="days",
        status="DRAFT",
        start_date=datetime.datetime(
            2023, 9, 25, 11, 41, 56, 604440, tzinfo=datetime.timezone.utc
        ),
        end_date=None,
        user_initials="unknown-user",
        possible_actions=["edit", "delete", "lock"],
        study_activity_count=9,
        change_type=None,
    ),
    StudyVisit(
        study_epoch_uid="StudyEpoch_000005",
        visit_type_uid="CTTerm_000177",
        time_reference_uid="CTTerm_000122",
        time_value=-2,
        time_unit_uid="UnitDefinition_000364",
        visit_sublabel_codelist_uid=None,
        visit_sublabel_reference=None,
        legacy_visit_id=None,
        legacy_visit_type_alias=None,
        legacy_name=None,
        legacy_subname=None,
        consecutive_visit_group=None,
        show_visit=False,
        min_visit_window_value=0,
        max_visit_window_value=0,
        visit_window_unit_uid="UnitDefinition_000364",
        description=None,
        start_rule=None,
        end_rule=None,
        visit_contact_mode_uid="CTTerm_000081",
        epoch_allocation_uid="CTTerm_000194",
        visit_class="SINGLE_VISIT",
        visit_subclass="SINGLE_VISIT",
        is_global_anchor_visit=False,
        uid="StudyVisit_000014",
        study_uid="Study_000002",
        study_epoch_name="Run-in",
        epoch_uid="C98779_RUN-IN",
        order=3,
        visit_type_name="Pre-treatment",
        time_reference_name="Global anchor visit",
        time_unit_name="days",
        visit_contact_mode_name="On Site Visit",
        epoch_allocation_name="Current Visit",
        duration_time=-172800.0,
        duration_time_unit="UnitDefinition_000364",
        study_day_number=-2,
        study_duration_days_label="-3 days",
        study_day_label="Day -2",
        study_week_number=1,
        study_duration_weeks_label="0 weeks",
        week_in_study_label="Week 0",
        study_week_label="Week 1",
        visit_number=3,
        visit_subnumber=0,
        unique_visit_number=300,
        visit_subname="Visit 3",
        visit_sublabel=None,
        visit_name="Visit 3",
        visit_short_name="V3",
        visit_window_unit_name="days",
        status="DRAFT",
        start_date=datetime.datetime(
            2023, 9, 27, 12, 50, 50, 931022, tzinfo=datetime.timezone.utc
        ),
        end_date=None,
        user_initials="unknown-user",
        possible_actions=["edit", "delete", "lock"],
        study_activity_count=7,
        change_type=None,
    ),
    StudyVisit(
        study_epoch_uid="StudyEpoch_000005",
        visit_type_uid="CTTerm_000177",
        time_reference_uid="CTTerm_000122",
        time_value=-1,
        time_unit_uid="UnitDefinition_000364",
        visit_sublabel_codelist_uid=None,
        visit_sublabel_reference=None,
        legacy_visit_id=None,
        legacy_visit_type_alias=None,
        legacy_name=None,
        legacy_subname=None,
        consecutive_visit_group=None,
        show_visit=True,
        min_visit_window_value=0,
        max_visit_window_value=0,
        visit_window_unit_uid="UnitDefinition_000364",
        description=None,
        start_rule=None,
        end_rule=None,
        visit_contact_mode_uid="CTTerm_000081",
        epoch_allocation_uid=None,
        visit_class="SINGLE_VISIT",
        visit_subclass="SINGLE_VISIT",
        is_global_anchor_visit=False,
        uid="StudyVisit_000015",
        study_uid="Study_000002",
        study_epoch_name="Run-in",
        epoch_uid="C98779_RUN-IN",
        order=4,
        visit_type_name="Pre-treatment",
        time_reference_name="Global anchor visit",
        time_unit_name="days",
        visit_contact_mode_name="On Site Visit",
        epoch_allocation_name=None,
        duration_time=-86400.0,
        duration_time_unit="UnitDefinition_000364",
        study_day_number=-1,
        study_duration_days_label="-2 days",
        study_day_label="Day -1",
        study_week_number=1,
        study_duration_weeks_label="0 weeks",
        week_in_study_label="Week 0",
        study_week_label="Week 1",
        visit_number=4,
        visit_subnumber=0,
        unique_visit_number=400,
        visit_subname="Visit 4",
        visit_sublabel=None,
        visit_name="Visit 4",
        visit_short_name="V4",
        visit_window_unit_name="days",
        status="DRAFT",
        start_date=datetime.datetime(
            2023, 9, 25, 11, 41, 58, 200939, tzinfo=datetime.timezone.utc
        ),
        end_date=None,
        user_initials="unknown-user",
        possible_actions=["edit", "delete", "lock"],
        study_activity_count=7,
        change_type=None,
    ),
    StudyVisit(
        study_epoch_uid="StudyEpoch_000006",
        visit_type_uid="CTTerm_000187",
        time_reference_uid="CTTerm_000122",
        time_value=0,
        time_unit_uid="UnitDefinition_000364",
        visit_sublabel_codelist_uid=None,
        visit_sublabel_reference=None,
        legacy_visit_id=None,
        legacy_visit_type_alias=None,
        legacy_name=None,
        legacy_subname=None,
        consecutive_visit_group="V5-V7",
        show_visit=True,
        min_visit_window_value=0,
        max_visit_window_value=0,
        visit_window_unit_uid="UnitDefinition_000364",
        description="CYCLE 1, TREATMENT DAY 1",
        start_rule=None,
        end_rule=None,
        visit_contact_mode_uid="CTTerm_000081",
        epoch_allocation_uid=None,
        visit_class="SINGLE_VISIT",
        visit_subclass="SINGLE_VISIT",
        is_global_anchor_visit=True,
        uid="StudyVisit_000016",
        study_uid="Study_000002",
        study_epoch_name="Treatment 1",
        epoch_uid="CTTerm_001163",
        order=5,
        visit_type_name="Treatment",
        time_reference_name="Global anchor visit",
        time_unit_name="days",
        visit_contact_mode_name="On Site Visit",
        epoch_allocation_name=None,
        duration_time=0.0,
        duration_time_unit="UnitDefinition_000364",
        study_day_number=1,
        study_duration_days_label="0 days",
        study_day_label="Day 1",
        study_week_number=1,
        study_duration_weeks_label="0 weeks",
        week_in_study_label="Week 0",
        study_week_label="Week 1",
        visit_number=5,
        visit_subnumber=0,
        unique_visit_number=500,
        visit_subname="Visit 5",
        visit_sublabel=None,
        visit_name="Visit 5",
        visit_short_name="V5",
        visit_window_unit_name="days",
        status="DRAFT",
        start_date=datetime.datetime(
            2023, 9, 28, 7, 8, 37, 273657, tzinfo=datetime.timezone.utc
        ),
        end_date=None,
        user_initials="unknown-user",
        possible_actions=["edit", "delete", "lock"],
        study_activity_count=8,
        change_type=None,
    ),
    StudyVisit(
        study_epoch_uid="StudyEpoch_000006",
        visit_type_uid="CTTerm_000187",
        time_reference_uid="CTTerm_000122",
        time_value=2,
        time_unit_uid="UnitDefinition_000364",
        visit_sublabel_codelist_uid=None,
        visit_sublabel_reference=None,
        legacy_visit_id=None,
        legacy_visit_type_alias=None,
        legacy_name=None,
        legacy_subname=None,
        consecutive_visit_group="V5-V7",
        show_visit=True,
        min_visit_window_value=0,
        max_visit_window_value=0,
        visit_window_unit_uid="UnitDefinition_000364",
        description="CYCLE 1, TREATMENT DAY 3",
        start_rule=None,
        end_rule=None,
        visit_contact_mode_uid="CTTerm_000081",
        epoch_allocation_uid=None,
        visit_class="SINGLE_VISIT",
        visit_subclass="SINGLE_VISIT",
        is_global_anchor_visit=False,
        uid="StudyVisit_000017",
        study_uid="Study_000002",
        study_epoch_name="Treatment 1",
        epoch_uid="CTTerm_001163",
        order=6,
        visit_type_name="Treatment",
        time_reference_name="Global anchor visit",
        time_unit_name="days",
        visit_contact_mode_name="On Site Visit",
        epoch_allocation_name=None,
        duration_time=172800.0,
        duration_time_unit="UnitDefinition_000364",
        study_day_number=3,
        study_duration_days_label="2 days",
        study_day_label="Day 3",
        study_week_number=1,
        study_duration_weeks_label="0 weeks",
        week_in_study_label="Week 0",
        study_week_label="Week 1",
        visit_number=6,
        visit_subnumber=0,
        unique_visit_number=600,
        visit_subname="Visit 6",
        visit_sublabel=None,
        visit_name="Visit 6",
        visit_short_name="V6",
        visit_window_unit_name="days",
        status="DRAFT",
        start_date=datetime.datetime(
            2023, 9, 28, 7, 8, 37, 539422, tzinfo=datetime.timezone.utc
        ),
        end_date=None,
        user_initials="unknown-user",
        possible_actions=["edit", "delete", "lock"],
        study_activity_count=8,
        change_type=None,
    ),
    StudyVisit(
        study_epoch_uid="StudyEpoch_000006",
        visit_type_uid="CTTerm_000187",
        time_reference_uid="CTTerm_000122",
        time_value=4,
        time_unit_uid="UnitDefinition_000364",
        visit_sublabel_codelist_uid=None,
        visit_sublabel_reference=None,
        legacy_visit_id=None,
        legacy_visit_type_alias=None,
        legacy_name=None,
        legacy_subname=None,
        consecutive_visit_group="V5-V7",
        show_visit=True,
        min_visit_window_value=0,
        max_visit_window_value=0,
        visit_window_unit_uid="UnitDefinition_000364",
        description="CYCLE 1, TREATMENT DAY 5",
        start_rule=None,
        end_rule=None,
        visit_contact_mode_uid="CTTerm_000081",
        epoch_allocation_uid=None,
        visit_class="SINGLE_VISIT",
        visit_subclass="SINGLE_VISIT",
        is_global_anchor_visit=False,
        uid="StudyVisit_000018",
        study_uid="Study_000002",
        study_epoch_name="Treatment 1",
        epoch_uid="CTTerm_001163",
        order=7,
        visit_type_name="Treatment",
        time_reference_name="Global anchor visit",
        time_unit_name="days",
        visit_contact_mode_name="On Site Visit",
        epoch_allocation_name=None,
        duration_time=345600.0,
        duration_time_unit="UnitDefinition_000364",
        study_day_number=5,
        study_duration_days_label="4 days",
        study_day_label="Day 5",
        study_week_number=1,
        study_duration_weeks_label="0 weeks",
        week_in_study_label="Week 0",
        study_week_label="Week 1",
        visit_number=7,
        visit_subnumber=0,
        unique_visit_number=700,
        visit_subname="Visit 7",
        visit_sublabel=None,
        visit_name="Visit 7",
        visit_short_name="V7",
        visit_window_unit_name="days",
        status="DRAFT",
        start_date=datetime.datetime(
            2023, 9, 28, 7, 8, 37, 794881, tzinfo=datetime.timezone.utc
        ),
        end_date=None,
        user_initials="unknown-user",
        possible_actions=["edit", "delete", "lock"],
        study_activity_count=8,
        change_type=None,
    ),
    StudyVisit(
        study_epoch_uid="StudyEpoch_000007",
        visit_type_uid="CTTerm_000187",
        time_reference_uid="CTTerm_000122",
        time_value=14,
        time_unit_uid="UnitDefinition_000364",
        visit_sublabel_codelist_uid=None,
        visit_sublabel_reference=None,
        legacy_visit_id=None,
        legacy_visit_type_alias=None,
        legacy_name=None,
        legacy_subname=None,
        consecutive_visit_group=None,
        show_visit=True,
        min_visit_window_value=0,
        max_visit_window_value=0,
        visit_window_unit_uid="UnitDefinition_000364",
        description="CYCLE 2, TREATMENT DAY 1",
        start_rule=None,
        end_rule=None,
        visit_contact_mode_uid="CTTerm_000081",
        epoch_allocation_uid=None,
        visit_class="SINGLE_VISIT",
        visit_subclass="SINGLE_VISIT",
        is_global_anchor_visit=False,
        uid="StudyVisit_000019",
        study_uid="Study_000002",
        study_epoch_name="Treatment 2",
        epoch_uid="CTTerm_001162",
        order=8,
        visit_type_name="Treatment",
        time_reference_name="Global anchor visit",
        time_unit_name="days",
        visit_contact_mode_name="On Site Visit",
        epoch_allocation_name=None,
        duration_time=1209600.0,
        duration_time_unit="UnitDefinition_000364",
        study_day_number=15,
        study_duration_days_label="14 days",
        study_day_label="Day 15",
        study_week_number=3,
        study_duration_weeks_label="2 weeks",
        week_in_study_label="Week 2",
        study_week_label="Week 3",
        visit_number=8,
        visit_subnumber=0,
        unique_visit_number=800,
        visit_subname="Visit 8",
        visit_sublabel=None,
        visit_name="Visit 8",
        visit_short_name="V8",
        visit_window_unit_name="days",
        status="DRAFT",
        start_date=datetime.datetime(
            2023, 9, 25, 11, 42, 1, 370897, tzinfo=datetime.timezone.utc
        ),
        end_date=None,
        user_initials="unknown-user",
        possible_actions=["edit", "delete", "lock"],
        study_activity_count=6,
        change_type=None,
    ),
    StudyVisit(
        study_epoch_uid="StudyEpoch_000007",
        visit_type_uid="CTTerm_000187",
        time_reference_uid="CTTerm_000122",
        time_value=16,
        time_unit_uid="UnitDefinition_000364",
        visit_sublabel_codelist_uid=None,
        visit_sublabel_reference=None,
        legacy_visit_id=None,
        legacy_visit_type_alias=None,
        legacy_name=None,
        legacy_subname=None,
        consecutive_visit_group=None,
        show_visit=True,
        min_visit_window_value=0,
        max_visit_window_value=0,
        visit_window_unit_uid="UnitDefinition_000364",
        description="CYCLE 2, TREATMENT DAY 2",
        start_rule=None,
        end_rule=None,
        visit_contact_mode_uid="CTTerm_000081",
        epoch_allocation_uid=None,
        visit_class="SINGLE_VISIT",
        visit_subclass="SINGLE_VISIT",
        is_global_anchor_visit=False,
        uid="StudyVisit_000020",
        study_uid="Study_000002",
        study_epoch_name="Treatment 2",
        epoch_uid="CTTerm_001162",
        order=9,
        visit_type_name="Treatment",
        time_reference_name="Global anchor visit",
        time_unit_name="days",
        visit_contact_mode_name="On Site Visit",
        epoch_allocation_name=None,
        duration_time=1382400.0,
        duration_time_unit="UnitDefinition_000364",
        study_day_number=17,
        study_duration_days_label="16 days",
        study_day_label="Day 17",
        study_week_number=3,
        study_duration_weeks_label="2 weeks",
        week_in_study_label="Week 2",
        study_week_label="Week 3",
        visit_number=9,
        visit_subnumber=0,
        unique_visit_number=900,
        visit_subname="Visit 9",
        visit_sublabel=None,
        visit_name="Visit 9",
        visit_short_name="V9",
        visit_window_unit_name="days",
        status="DRAFT",
        start_date=datetime.datetime(
            2023, 9, 25, 11, 42, 2, 213618, tzinfo=datetime.timezone.utc
        ),
        end_date=None,
        user_initials="unknown-user",
        possible_actions=["edit", "delete", "lock"],
        study_activity_count=7,
        change_type=None,
    ),
    StudyVisit(
        study_epoch_uid="StudyEpoch_000007",
        visit_type_uid="CTTerm_000187",
        time_reference_uid="CTTerm_000122",
        time_value=18,
        time_unit_uid="UnitDefinition_000364",
        visit_sublabel_codelist_uid=None,
        visit_sublabel_reference=None,
        legacy_visit_id=None,
        legacy_visit_type_alias=None,
        legacy_name=None,
        legacy_subname=None,
        consecutive_visit_group=None,
        show_visit=True,
        min_visit_window_value=0,
        max_visit_window_value=0,
        visit_window_unit_uid="UnitDefinition_000364",
        description="CYCLE 2, TREATMENT DAY 5",
        start_rule=None,
        end_rule=None,
        visit_contact_mode_uid="CTTerm_000081",
        epoch_allocation_uid=None,
        visit_class="SINGLE_VISIT",
        visit_subclass="SINGLE_VISIT",
        is_global_anchor_visit=False,
        uid="StudyVisit_000021",
        study_uid="Study_000002",
        study_epoch_name="Treatment 2",
        epoch_uid="CTTerm_001162",
        order=10,
        visit_type_name="Treatment",
        time_reference_name="Global anchor visit",
        time_unit_name="days",
        visit_contact_mode_name="On Site Visit",
        epoch_allocation_name=None,
        duration_time=1555200.0,
        duration_time_unit="UnitDefinition_000364",
        study_day_number=19,
        study_duration_days_label="18 days",
        study_day_label="Day 19",
        study_week_number=3,
        study_duration_weeks_label="2 weeks",
        week_in_study_label="Week 2",
        study_week_label="Week 3",
        visit_number=10,
        visit_subnumber=0,
        unique_visit_number=1000,
        visit_subname="Visit 10",
        visit_sublabel=None,
        visit_name="Visit 10",
        visit_short_name="V10",
        visit_window_unit_name="days",
        status="DRAFT",
        start_date=datetime.datetime(
            2023, 9, 25, 11, 42, 3, 81758, tzinfo=datetime.timezone.utc
        ),
        end_date=None,
        user_initials="unknown-user",
        possible_actions=["edit", "delete", "lock"],
        study_activity_count=10,
        change_type=None,
    ),
    StudyVisit(
        study_epoch_uid="StudyEpoch_000008",
        visit_type_uid="CTTerm_000175",
        time_reference_uid="CTTerm_000122",
        time_value=21,
        time_unit_uid="UnitDefinition_000364",
        visit_sublabel_codelist_uid=None,
        visit_sublabel_reference=None,
        legacy_visit_id=None,
        legacy_visit_type_alias=None,
        legacy_name=None,
        legacy_subname=None,
        consecutive_visit_group=None,
        show_visit=True,
        min_visit_window_value=0,
        max_visit_window_value=0,
        visit_window_unit_uid="UnitDefinition_000364",
        description=None,
        start_rule=None,
        end_rule=None,
        visit_contact_mode_uid="CTTerm_000081",
        epoch_allocation_uid=None,
        visit_class="SINGLE_VISIT",
        visit_subclass="SINGLE_VISIT",
        is_global_anchor_visit=False,
        uid="StudyVisit_000022",
        study_uid="Study_000002",
        study_epoch_name="Follow-up",
        epoch_uid="C99158_FOLLOW-UP",
        order=11,
        visit_type_name="Follow-up",
        time_reference_name="Global anchor visit",
        time_unit_name="days",
        visit_contact_mode_name="On Site Visit",
        epoch_allocation_name=None,
        duration_time=1814400.0,
        duration_time_unit="UnitDefinition_000364",
        study_day_number=22,
        study_duration_days_label="21 days",
        study_day_label="Day 22",
        study_week_number=4,
        study_duration_weeks_label="3 weeks",
        week_in_study_label="Week 3",
        study_week_label="Week 4",
        visit_number=11,
        visit_subnumber=0,
        unique_visit_number=1100,
        visit_subname="Visit 11",
        visit_sublabel=None,
        visit_name="Visit 11",
        visit_short_name="V11",
        visit_window_unit_name="days",
        status="DRAFT",
        start_date=datetime.datetime(
            2023, 9, 25, 11, 42, 4, 15590, tzinfo=datetime.timezone.utc
        ),
        end_date=None,
        user_initials="unknown-user",
        possible_actions=["edit", "delete", "lock"],
        study_activity_count=12,
        change_type=None,
    ),
    StudyVisit(
        study_epoch_uid="StudyEpoch_000009",
        visit_type_uid="CTTerm_000190",
        time_reference_uid=None,
        time_value=None,
        time_unit_uid=None,
        visit_sublabel_codelist_uid=None,
        visit_sublabel_reference=None,
        legacy_visit_id=None,
        legacy_visit_type_alias=None,
        legacy_name=None,
        legacy_subname=None,
        consecutive_visit_group=None,
        show_visit=True,
        min_visit_window_value=-9999,
        max_visit_window_value=9999,
        visit_window_unit_uid="UnitDefinition_000364",
        description=None,
        start_rule=None,
        end_rule=None,
        visit_contact_mode_uid="CTTerm_000079",
        epoch_allocation_uid="CTTerm_000196",
        visit_class="NON_VISIT",
        visit_subclass="SINGLE_VISIT",
        is_global_anchor_visit=False,
        uid="StudyVisit_000023",
        study_uid="Study_000002",
        study_epoch_name="Basic",
        epoch_uid="CTTerm_000009",
        order=29500,
        visit_type_name="Non-visit",
        time_reference_name=None,
        time_unit_name=None,
        visit_contact_mode_name="Virtual Visit",
        epoch_allocation_name="Date Current Visit",
        duration_time=None,
        duration_time_unit=None,
        study_day_number=None,
        study_duration_days_label=None,
        study_day_label=None,
        study_week_number=None,
        study_duration_weeks_label=None,
        week_in_study_label=None,
        study_week_label=None,
        visit_number=29500,
        visit_subnumber=0,
        unique_visit_number=29500,
        visit_subname="Visit 29500",
        visit_sublabel=None,
        visit_name="Visit 29500",
        visit_short_name="29500",
        visit_window_unit_name="days",
        status="DRAFT",
        start_date=datetime.datetime(
            2023, 9, 28, 7, 9, 40, 605585, tzinfo=datetime.timezone.utc
        ),
        end_date=None,
        user_initials="unknown-user",
        possible_actions=["edit", "delete", "lock"],
        study_activity_count=0,
        change_type=None,
    ),
    StudyVisit(
        study_epoch_uid="StudyEpoch_000009",
        visit_type_uid="CTTerm_000192",
        time_reference_uid=None,
        time_value=None,
        time_unit_uid=None,
        visit_sublabel_codelist_uid=None,
        visit_sublabel_reference=None,
        legacy_visit_id=None,
        legacy_visit_type_alias=None,
        legacy_name=None,
        legacy_subname=None,
        consecutive_visit_group=None,
        show_visit=True,
        min_visit_window_value=-9999,
        max_visit_window_value=9999,
        visit_window_unit_uid="UnitDefinition_000364",
        description=None,
        start_rule=None,
        end_rule=None,
        visit_contact_mode_uid="CTTerm_000079",
        epoch_allocation_uid="CTTerm_000196",
        visit_class="UNSCHEDULED_VISIT",
        visit_subclass="SINGLE_VISIT",
        is_global_anchor_visit=False,
        uid="StudyVisit_000024",
        study_uid="Study_000002",
        study_epoch_name="Basic",
        epoch_uid="CTTerm_000009",
        order=29999,
        visit_type_name="Unscheduled",
        time_reference_name=None,
        time_unit_name=None,
        visit_contact_mode_name="Virtual Visit",
        epoch_allocation_name="Date Current Visit",
        duration_time=None,
        duration_time_unit=None,
        study_day_number=None,
        study_duration_days_label=None,
        study_day_label=None,
        study_week_number=None,
        study_duration_weeks_label=None,
        week_in_study_label=None,
        study_week_label=None,
        visit_number=29999,
        visit_subnumber=0,
        unique_visit_number=29999,
        visit_subname="Visit 29999",
        visit_sublabel=None,
        visit_name="Visit 29999",
        visit_short_name="29999",
        visit_window_unit_name="days",
        status="DRAFT",
        start_date=datetime.datetime(
            2023, 9, 28, 7, 9, 58, 725540, tzinfo=datetime.timezone.utc
        ),
        end_date=None,
        user_initials="unknown-user",
        possible_actions=["edit", "delete", "lock"],
        study_activity_count=0,
        change_type=None,
    ),
]

STUDY_ACTIVITIES = [
    StudySelectionActivity(
        study_uid="Study_000002",
        order=1,
        project_number=None,
        project_name=None,
        show_activity_in_protocol_flowchart=True,
        show_activity_subgroup_in_protocol_flowchart=True,
        show_activity_group_in_protocol_flowchart=True,
        show_soa_group_in_protocol_flowchart=True,
        study_activity_uid="StudyActivity_000033",
        study_activity_subgroup=SimpleStudyActivitySubGroup(
            study_activity_subgroup_uid="StudyActivitySubGroup_000033",
            activity_subgroup_uid="ActivitySubGroup_000016",
            activity_subgroup_name="Informed Consent and Demography",
        ),
        study_activity_group=SimpleStudyActivityGroup(
            study_activity_group_uid="StudyActivityGroup_000033",
            activity_group_uid="ActivityGroup_000010",
            activity_group_name="Informed Consent and Demography",
        ),
        study_soa_group=SimpleStudySoAGroup(
            study_soa_group_uid="StudySoAGroup_000033",
            soa_group_term_uid="CTTerm_000066",
            soa_group_name="SUBJECT RELATED INFORMATION",
        ),
        activity=Activity(
            start_date=datetime.datetime(2023, 9, 25, 11, 34, 8, 76019),
            end_date=None,
            status="Final",
            version="1.0",
            change_description="Approved version",
            user_initials="unknown-user",
            uid="Activity_000059",
            name="Informed Consent Obtained",
            name_sentence_case="informed consent obtained",
            definition=None,
            abbreviation=None,
            library_name="Sponsor",
            possible_actions=["inactivate", "new_version"],
            nci_concept_id=None,
            activity_groupings=[
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000010",
                    activity_group_name="Informed Consent and Demography",
                    activity_subgroup_uid="ActivitySubGroup_000016",
                    activity_subgroup_name="Informed Consent and Demography",
                ),
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000013",
                    activity_group_name="Informed Consent",
                    activity_subgroup_uid="ActivitySubGroup_000026",
                    activity_subgroup_name="Informed Consent",
                ),
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000015",
                    activity_group_name="Future Research Biosample Consent",
                    activity_subgroup_uid="ActivitySubGroup_000029",
                    activity_subgroup_name="Future Research Biosample Consent",
                ),
            ],
            request_rationale=None,
            replaced_by_activity=None,
            is_data_collected=False,
        ),
        start_date=datetime.datetime(2023, 9, 26, 22, 7, 17, 577489),
        user_initials="unknown-user",
        end_date=None,
        status=None,
        change_type=None,
        latest_activity=None,
        accepted_version=False,
    ),
    StudySelectionActivity(
        study_uid="Study_000002",
        order=2,
        project_number=None,
        project_name=None,
        show_activity_in_protocol_flowchart=True,
        show_activity_subgroup_in_protocol_flowchart=False,
        show_activity_group_in_protocol_flowchart=False,
        show_soa_group_in_protocol_flowchart=True,
        study_activity_uid="StudyActivity_000034",
        study_activity_subgroup=SimpleStudyActivitySubGroup(
            study_activity_subgroup_uid="StudyActivitySubGroup_000034",
            activity_subgroup_uid="ActivitySubGroup_000018",
            activity_subgroup_name="Eligibility Criteria",
        ),
        study_activity_group=SimpleStudyActivityGroup(
            study_activity_group_uid="StudyActivityGroup_000034",
            activity_group_uid="ActivityGroup_000011",
            activity_group_name="Eligibility Criteria",
        ),
        study_soa_group=SimpleStudySoAGroup(
            study_soa_group_uid="StudySoAGroup_000034",
            soa_group_term_uid="CTTerm_000066",
            soa_group_name="SUBJECT RELATED INFORMATION",
        ),
        activity=Activity(
            start_date=datetime.datetime(2023, 9, 25, 11, 34, 5, 65621),
            end_date=None,
            status="Final",
            version="1.0",
            change_description="Approved version",
            user_initials="unknown-user",
            uid="Activity_000041",
            name="Eligibility Criteria Met",
            name_sentence_case="eligibility criteria met",
            definition=None,
            abbreviation=None,
            library_name="Sponsor",
            possible_actions=["inactivate", "new_version"],
            nci_concept_id=None,
            activity_groupings=[
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000011",
                    activity_group_name="Eligibility Criteria",
                    activity_subgroup_uid="ActivitySubGroup_000018",
                    activity_subgroup_name="Eligibility Criteria",
                )
            ],
            request_rationale=None,
            replaced_by_activity=None,
            is_data_collected=False,
        ),
        start_date=datetime.datetime(2023, 9, 28, 12, 15, 35, 762079),
        user_initials="unknown-user",
        end_date=None,
        status=None,
        change_type=None,
        latest_activity=None,
        accepted_version=False,
    ),
    StudySelectionActivity(
        study_uid="Study_000002",
        order=3,
        project_number=None,
        project_name=None,
        show_activity_in_protocol_flowchart=False,
        show_activity_subgroup_in_protocol_flowchart=False,
        show_activity_group_in_protocol_flowchart=True,
        show_soa_group_in_protocol_flowchart=True,
        study_activity_uid="StudyActivity_000035",
        study_activity_subgroup=SimpleStudyActivitySubGroup(
            study_activity_subgroup_uid="StudyActivitySubGroup_000035",
            activity_subgroup_uid="ActivitySubGroup_000030",
            activity_subgroup_name="Medical History/Concomitant Illness",
        ),
        study_activity_group=SimpleStudyActivityGroup(
            study_activity_group_uid="StudyActivityGroup_000035",
            activity_group_uid="ActivityGroup_000017",
            activity_group_name="Medical History/Concomitant Illness",
        ),
        study_soa_group=SimpleStudySoAGroup(
            study_soa_group_uid="StudySoAGroup_000035",
            soa_group_term_uid="CTTerm_000066",
            soa_group_name="SUBJECT RELATED INFORMATION",
        ),
        activity=Activity(
            start_date=datetime.datetime(2023, 9, 25, 11, 34, 8, 699174),
            end_date=None,
            status="Final",
            version="1.0",
            change_description="Approved version",
            user_initials="unknown-user",
            uid="Activity_000062",
            name="Medical History/Concomitant Illness",
            name_sentence_case="medical history/concomitant illness",
            definition=None,
            abbreviation=None,
            library_name="Sponsor",
            possible_actions=["inactivate", "new_version"],
            nci_concept_id=None,
            activity_groupings=[
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000017",
                    activity_group_name="Medical History/Concomitant Illness",
                    activity_subgroup_uid="ActivitySubGroup_000030",
                    activity_subgroup_name="Medical History/Concomitant Illness",
                )
            ],
            request_rationale=None,
            replaced_by_activity=None,
            is_data_collected=False,
        ),
        start_date=datetime.datetime(2023, 9, 28, 7, 18, 2, 633400),
        user_initials="unknown-user",
        end_date=None,
        status=None,
        change_type=None,
        latest_activity=None,
        accepted_version=False,
    ),
    StudySelectionActivity(
        study_uid="Study_000002",
        order=4,
        project_number=None,
        project_name=None,
        show_activity_in_protocol_flowchart=False,
        show_activity_subgroup_in_protocol_flowchart=True,
        show_activity_group_in_protocol_flowchart=False,
        show_soa_group_in_protocol_flowchart=True,
        study_activity_uid="StudyActivity_000036",
        study_activity_subgroup=SimpleStudyActivitySubGroup(
            study_activity_subgroup_uid="StudyActivitySubGroup_000036",
            activity_subgroup_uid="ActivitySubGroup_000010",
            activity_subgroup_name="Body Measurements",
        ),
        study_activity_group=SimpleStudyActivityGroup(
            study_activity_group_uid="StudyActivityGroup_000036",
            activity_group_uid="ActivityGroup_000005",
            activity_group_name="Body Measurements",
        ),
        study_soa_group=SimpleStudySoAGroup(
            study_soa_group_uid="StudySoAGroup_000036",
            soa_group_term_uid="CTTerm_000066",
            soa_group_name="SUBJECT RELATED INFORMATION",
        ),
        activity=Activity(
            start_date=datetime.datetime(2023, 9, 25, 11, 34, 7, 274454),
            end_date=None,
            status="Final",
            version="1.0",
            change_description="Approved version",
            user_initials="unknown-user",
            uid="Activity_000054",
            name="Height",
            name_sentence_case="height",
            definition=None,
            abbreviation=None,
            library_name="Sponsor",
            possible_actions=["inactivate", "new_version"],
            nci_concept_id=None,
            activity_groupings=[
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000005",
                    activity_group_name="Body Measurements",
                    activity_subgroup_uid="ActivitySubGroup_000010",
                    activity_subgroup_name="Body Measurements",
                )
            ],
            request_rationale=None,
            replaced_by_activity=None,
            is_data_collected=False,
        ),
        start_date=datetime.datetime(2023, 9, 28, 12, 15, 14, 847955),
        user_initials="unknown-user",
        end_date=None,
        status=None,
        change_type=None,
        latest_activity=None,
        accepted_version=False,
    ),
    StudySelectionActivity(
        study_uid="Study_000002",
        order=5,
        project_number=None,
        project_name=None,
        show_activity_in_protocol_flowchart=False,
        show_activity_subgroup_in_protocol_flowchart=True,
        show_activity_group_in_protocol_flowchart=False,
        show_soa_group_in_protocol_flowchart=True,
        study_activity_uid="StudyActivity_000037",
        study_activity_subgroup=SimpleStudyActivitySubGroup(
            study_activity_subgroup_uid="StudyActivitySubGroup_000037",
            activity_subgroup_uid="ActivitySubGroup_000010",
            activity_subgroup_name="Body Measurements",
        ),
        study_activity_group=SimpleStudyActivityGroup(
            study_activity_group_uid="StudyActivityGroup_000037",
            activity_group_uid="ActivityGroup_000005",
            activity_group_name="Body Measurements",
        ),
        study_soa_group=SimpleStudySoAGroup(
            study_soa_group_uid="StudySoAGroup_000037",
            soa_group_term_uid="CTTerm_000066",
            soa_group_name="SUBJECT RELATED INFORMATION",
        ),
        activity=Activity(
            start_date=datetime.datetime(2023, 9, 25, 11, 34, 2, 443094),
            end_date=None,
            status="Final",
            version="1.0",
            change_description="Approved version",
            user_initials="unknown-user",
            uid="Activity_000025",
            name="Weight",
            name_sentence_case="weight",
            definition=None,
            abbreviation=None,
            library_name="Sponsor",
            possible_actions=["inactivate", "new_version"],
            nci_concept_id=None,
            activity_groupings=[
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000005",
                    activity_group_name="Body Measurements",
                    activity_subgroup_uid="ActivitySubGroup_000010",
                    activity_subgroup_name="Body Measurements",
                )
            ],
            request_rationale=None,
            replaced_by_activity=None,
            is_data_collected=False,
        ),
        start_date=datetime.datetime(2023, 9, 28, 12, 15, 14, 549807),
        user_initials="unknown-user",
        end_date=None,
        status=None,
        change_type=None,
        latest_activity=None,
        accepted_version=False,
    ),
    StudySelectionActivity(
        study_uid="Study_000002",
        order=6,
        project_number=None,
        project_name=None,
        show_activity_in_protocol_flowchart=False,
        show_activity_subgroup_in_protocol_flowchart=False,
        show_activity_group_in_protocol_flowchart=True,
        show_soa_group_in_protocol_flowchart=True,
        study_activity_uid="StudyActivity_000038",
        study_activity_subgroup=SimpleStudyActivitySubGroup(
            study_activity_subgroup_uid="StudyActivitySubGroup_000038",
            activity_subgroup_uid="ActivitySubGroup_000021",
            activity_subgroup_name="Haematology",
        ),
        study_activity_group=SimpleStudyActivityGroup(
            study_activity_group_uid="StudyActivityGroup_000038",
            activity_group_uid="ActivityGroup_000004",
            activity_group_name="Laboratory Assessments",
        ),
        study_soa_group=SimpleStudySoAGroup(
            study_soa_group_uid="StudySoAGroup_000038",
            soa_group_term_uid="CTTerm_000066",
            soa_group_name="SUBJECT RELATED INFORMATION",
        ),
        activity=Activity(
            start_date=datetime.datetime(2023, 9, 25, 11, 34, 5, 630967),
            end_date=None,
            status="Final",
            version="1.0",
            change_description="Approved version",
            user_initials="unknown-user",
            uid="Activity_000044",
            name="Erythrocytes",
            name_sentence_case="erythrocytes",
            definition=None,
            abbreviation=None,
            library_name="Sponsor",
            possible_actions=["inactivate", "new_version"],
            nci_concept_id=None,
            activity_groupings=[
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000003",
                    activity_group_name="AE Requiring Additional Data",
                    activity_subgroup_uid="ActivitySubGroup_000004",
                    activity_subgroup_name="Laboratory Assessment",
                ),
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000004",
                    activity_group_name="Laboratory Assessments",
                    activity_subgroup_uid="ActivitySubGroup_000006",
                    activity_subgroup_name="Urinalysis",
                ),
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000004",
                    activity_group_name="Laboratory Assessments",
                    activity_subgroup_uid="ActivitySubGroup_000021",
                    activity_subgroup_name="Haematology",
                ),
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000004",
                    activity_group_name="Laboratory Assessments",
                    activity_subgroup_uid="ActivitySubGroup_000022",
                    activity_subgroup_name="Urine Dipstick",
                ),
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000004",
                    activity_group_name="Laboratory Assessments",
                    activity_subgroup_uid="ActivitySubGroup_000023",
                    activity_subgroup_name="Urinalysis - Urine Dipstick",
                ),
            ],
            request_rationale=None,
            replaced_by_activity=None,
            is_data_collected=False,
        ),
        start_date=datetime.datetime(2023, 9, 28, 12, 15, 4, 769418),
        user_initials="unknown-user",
        end_date=None,
        status=None,
        change_type=None,
        latest_activity=None,
        accepted_version=False,
    ),
    StudySelectionActivity(
        study_uid="Study_000002",
        order=7,
        project_number=None,
        project_name=None,
        show_activity_in_protocol_flowchart=False,
        show_activity_subgroup_in_protocol_flowchart=True,
        show_activity_group_in_protocol_flowchart=True,
        show_soa_group_in_protocol_flowchart=True,
        study_activity_uid="StudyActivity_000039",
        study_activity_subgroup=SimpleStudyActivitySubGroup(
            study_activity_subgroup_uid="StudyActivitySubGroup_000039",
            activity_subgroup_uid="ActivitySubGroup_000009",
            activity_subgroup_name="Vital Signs",
        ),
        study_activity_group=SimpleStudyActivityGroup(
            study_activity_group_uid="StudyActivityGroup_000039",
            activity_group_uid="ActivityGroup_000006",
            activity_group_name="Vital Signs",
        ),
        study_soa_group=SimpleStudySoAGroup(
            study_soa_group_uid="StudySoAGroup_000039",
            soa_group_term_uid="CTTerm_000066",
            soa_group_name="SUBJECT RELATED INFORMATION",
        ),
        activity=Activity(
            start_date=datetime.datetime(2023, 9, 25, 11, 34, 2, 671856),
            end_date=None,
            status="Final",
            version="1.0",
            change_description="Approved version",
            user_initials="unknown-user",
            uid="Activity_000027",
            name="Systolic Blood Pressure",
            name_sentence_case="systolic blood pressure",
            definition=None,
            abbreviation=None,
            library_name="Sponsor",
            possible_actions=["inactivate", "new_version"],
            nci_concept_id=None,
            activity_groupings=[
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000006",
                    activity_group_name="Vital Signs",
                    activity_subgroup_uid="ActivitySubGroup_000009",
                    activity_subgroup_name="Vital Signs",
                )
            ],
            request_rationale=None,
            replaced_by_activity=None,
            is_data_collected=False,
        ),
        start_date=datetime.datetime(2023, 9, 28, 12, 14, 20, 686382),
        user_initials="unknown-user",
        end_date=None,
        status=None,
        change_type=None,
        latest_activity=None,
        accepted_version=False,
    ),
    StudySelectionActivity(
        study_uid="Study_000002",
        order=8,
        project_number=None,
        project_name=None,
        show_activity_in_protocol_flowchart=False,
        show_activity_subgroup_in_protocol_flowchart=True,
        show_activity_group_in_protocol_flowchart=True,
        show_soa_group_in_protocol_flowchart=True,
        study_activity_uid="StudyActivity_000040",
        study_activity_subgroup=SimpleStudyActivitySubGroup(
            study_activity_subgroup_uid="StudyActivitySubGroup_000040",
            activity_subgroup_uid="ActivitySubGroup_000009",
            activity_subgroup_name="Vital Signs",
        ),
        study_activity_group=SimpleStudyActivityGroup(
            study_activity_group_uid="StudyActivityGroup_000040",
            activity_group_uid="ActivityGroup_000006",
            activity_group_name="Vital Signs",
        ),
        study_soa_group=SimpleStudySoAGroup(
            study_soa_group_uid="StudySoAGroup_000040",
            soa_group_term_uid="CTTerm_000066",
            soa_group_name="SUBJECT RELATED INFORMATION",
        ),
        activity=Activity(
            start_date=datetime.datetime(2023, 9, 25, 11, 34, 2, 546360),
            end_date=None,
            status="Final",
            version="1.0",
            change_description="Approved version",
            user_initials="unknown-user",
            uid="Activity_000026",
            name="Diastolic Blood Pressure",
            name_sentence_case="diastolic blood pressure",
            definition=None,
            abbreviation=None,
            library_name="Sponsor",
            possible_actions=["inactivate", "new_version"],
            nci_concept_id=None,
            activity_groupings=[
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000006",
                    activity_group_name="Vital Signs",
                    activity_subgroup_uid="ActivitySubGroup_000009",
                    activity_subgroup_name="Vital Signs",
                )
            ],
            request_rationale=None,
            replaced_by_activity=None,
            is_data_collected=False,
        ),
        start_date=datetime.datetime(2023, 9, 26, 21, 44, 47, 302977),
        user_initials="unknown-user",
        end_date=None,
        status=None,
        change_type=None,
        latest_activity=None,
        accepted_version=False,
    ),
    StudySelectionActivity(
        study_uid="Study_000002",
        order=9,
        project_number=None,
        project_name=None,
        show_activity_in_protocol_flowchart=False,
        show_activity_subgroup_in_protocol_flowchart=True,
        show_activity_group_in_protocol_flowchart=True,
        show_soa_group_in_protocol_flowchart=True,
        study_activity_uid="StudyActivity_000041",
        study_activity_subgroup=SimpleStudyActivitySubGroup(
            study_activity_subgroup_uid="StudyActivitySubGroup_000041",
            activity_subgroup_uid="ActivitySubGroup_000016",
            activity_subgroup_name="Informed Consent and Demography",
        ),
        study_activity_group=SimpleStudyActivityGroup(
            study_activity_group_uid="StudyActivityGroup_000041",
            activity_group_uid="ActivityGroup_000010",
            activity_group_name="Informed Consent and Demography",
        ),
        study_soa_group=SimpleStudySoAGroup(
            study_soa_group_uid="StudySoAGroup_000041",
            soa_group_term_uid="CTTerm_000066",
            soa_group_name="SUBJECT RELATED INFORMATION",
        ),
        activity=Activity(
            start_date=datetime.datetime(2023, 9, 25, 11, 34, 4, 279777),
            end_date=None,
            status="Final",
            version="1.0",
            change_description="Approved version",
            user_initials="unknown-user",
            uid="Activity_000037",
            name="Date of Birth",
            name_sentence_case="date of birth",
            definition=None,
            abbreviation=None,
            library_name="Sponsor",
            possible_actions=["inactivate", "new_version"],
            nci_concept_id=None,
            activity_groupings=[
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000010",
                    activity_group_name="Informed Consent and Demography",
                    activity_subgroup_uid="ActivitySubGroup_000016",
                    activity_subgroup_name="Informed Consent and Demography",
                ),
                ActivityGroupingHierarchySimpleModel(
                    activity_group_uid="ActivityGroup_000009",
                    activity_group_name="Demography",
                    activity_subgroup_uid="ActivitySubGroup_000017",
                    activity_subgroup_name="Demography",
                ),
            ],
            request_rationale=None,
            replaced_by_activity=None,
            is_data_collected=False,
        ),
        start_date=datetime.datetime(2023, 9, 28, 7, 17, 27, 538325),
        user_initials="unknown-user",
        end_date=None,
        status=None,
        change_type=None,
        latest_activity=None,
        accepted_version=False,
    ),
]

STUDY_ACTIVITY_SCHEDULES = [
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000237",
        study_activity_uid="StudyActivity_000033",
        study_activity_name="Informed Consent Obtained",
        study_visit_uid="StudyVisit_000021",
        study_visit_name="Visit 10",
        start_date=datetime.datetime(2023, 9, 28, 12, 16, 13, 789294),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000224",
        study_activity_uid="StudyActivity_000033",
        study_activity_name="Informed Consent Obtained",
        study_visit_uid="StudyVisit_000018",
        study_visit_name="Visit 7",
        start_date=datetime.datetime(2023, 9, 28, 7, 18, 41, 289272),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000223",
        study_activity_uid="StudyActivity_000033",
        study_activity_name="Informed Consent Obtained",
        study_visit_uid="StudyVisit_000017",
        study_visit_name="Visit 6",
        start_date=datetime.datetime(2023, 9, 28, 7, 18, 41, 200554),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000222",
        study_activity_uid="StudyActivity_000033",
        study_activity_name="Informed Consent Obtained",
        study_visit_uid="StudyVisit_000016",
        study_visit_name="Visit 5",
        start_date=datetime.datetime(2023, 9, 28, 7, 18, 41, 106152),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000180",
        study_activity_uid="StudyActivity_000033",
        study_activity_name="Informed Consent Obtained",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 44, 925699),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000167",
        study_activity_uid="StudyActivity_000033",
        study_activity_name="Informed Consent Obtained",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 40, 4090),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000239",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000013",
        study_visit_name="Visit 2",
        start_date=datetime.datetime(2023, 9, 28, 12, 16, 36, 941563),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000148",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000014",
        study_visit_name="Visit 3",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 29, 963794),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000174",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 42, 799372),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000150",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000015",
        study_visit_name="Visit 4",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 30, 666424),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000146",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000013",
        study_visit_name="Visit 2",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 29, 284104),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000209",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000017",
        study_visit_name="Visit 6",
        start_date=datetime.datetime(2023, 9, 28, 7, 8, 33, 792658),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000152",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000016",
        study_visit_name="Visit 5",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 31, 375534),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000186",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000015",
        study_visit_name="Visit 4",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 47, 957960),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000184",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000016",
        study_visit_name="Visit 5",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 47, 259826),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000213",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000018",
        study_visit_name="Visit 7",
        start_date=datetime.datetime(2023, 9, 28, 7, 8, 35, 538906),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000172",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 41, 800992),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000140",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 27, 180162),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000207",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000017",
        study_visit_name="Visit 6",
        start_date=datetime.datetime(2023, 9, 28, 7, 8, 33, 659383),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000215",
        study_activity_uid="StudyActivity_000041",
        study_activity_name="Date of Birth",
        study_visit_uid="StudyVisit_000018",
        study_visit_name="Visit 7",
        start_date=datetime.datetime(2023, 9, 28, 7, 8, 35, 692353),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000235",
        study_activity_uid="StudyActivity_000040",
        study_activity_name="Diastolic Blood Pressure",
        study_visit_uid="StudyVisit_000021",
        study_visit_name="Visit 10",
        start_date=datetime.datetime(2023, 9, 28, 12, 14, 53, 81287),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000232",
        study_activity_uid="StudyActivity_000040",
        study_activity_name="Diastolic Blood Pressure",
        study_visit_uid="StudyVisit_000019",
        study_visit_name="Visit 8",
        start_date=datetime.datetime(2023, 9, 28, 12, 14, 12, 896228),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000231",
        study_activity_uid="StudyActivity_000040",
        study_activity_name="Diastolic Blood Pressure",
        study_visit_uid="StudyVisit_000018",
        study_visit_name="Visit 7",
        start_date=datetime.datetime(2023, 9, 28, 12, 14, 11, 30893),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000230",
        study_activity_uid="StudyActivity_000040",
        study_activity_name="Diastolic Blood Pressure",
        study_visit_uid="StudyVisit_000017",
        study_visit_name="Visit 6",
        start_date=datetime.datetime(2023, 9, 28, 12, 14, 10, 952933),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000229",
        study_activity_uid="StudyActivity_000040",
        study_activity_name="Diastolic Blood Pressure",
        study_visit_uid="StudyVisit_000016",
        study_visit_name="Visit 5",
        start_date=datetime.datetime(2023, 9, 28, 12, 14, 10, 870893),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000228",
        study_activity_uid="StudyActivity_000040",
        study_activity_name="Diastolic Blood Pressure",
        study_visit_uid="StudyVisit_000014",
        study_visit_name="Visit 3",
        start_date=datetime.datetime(2023, 9, 28, 12, 14, 2, 996469),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000227",
        study_activity_uid="StudyActivity_000040",
        study_activity_name="Diastolic Blood Pressure",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 28, 12, 14, 1, 609735),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000212",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000018",
        study_visit_name="Visit 7",
        start_date=datetime.datetime(2023, 9, 28, 7, 8, 35, 462210),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000210",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000017",
        study_visit_name="Visit 6",
        start_date=datetime.datetime(2023, 9, 28, 7, 8, 33, 886820),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000177",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000013",
        study_visit_name="Visit 2",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 43, 881792),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000145",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000013",
        study_visit_name="Visit 2",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 28, 934309),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000216",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000018",
        study_visit_name="Visit 7",
        start_date=datetime.datetime(2023, 9, 28, 7, 8, 35, 761803),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000187",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000015",
        study_visit_name="Visit 4",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 48, 294076),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000185",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000016",
        study_visit_name="Visit 5",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 47, 610633),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000171",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 41, 454736),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000137",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 25, 836096),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000206",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000017",
        study_visit_name="Visit 6",
        start_date=datetime.datetime(2023, 9, 28, 7, 8, 33, 595642),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000147",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000014",
        study_visit_name="Visit 3",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 29, 622008),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000163",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000022",
        study_visit_name="Visit 11",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 37, 404001),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000151",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000016",
        study_visit_name="Visit 5",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 31, 24714),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000179",
        study_activity_uid="StudyActivity_000039",
        study_activity_name="Systolic Blood Pressure",
        study_visit_uid="StudyVisit_000014",
        study_visit_name="Visit 3",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 44, 578341),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000181",
        study_activity_uid="StudyActivity_000038",
        study_activity_name="Erythrocytes",
        study_visit_uid="StudyVisit_000015",
        study_visit_name="Visit 4",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 45, 285530),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000139",
        study_activity_uid="StudyActivity_000038",
        study_activity_name="Erythrocytes",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 26, 830628),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000173",
        study_activity_uid="StudyActivity_000038",
        study_activity_name="Erythrocytes",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 42, 455121),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000165",
        study_activity_uid="StudyActivity_000038",
        study_activity_name="Erythrocytes",
        study_visit_uid="StudyVisit_000022",
        study_visit_name="Visit 11",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 38, 392756),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000166",
        study_activity_uid="StudyActivity_000038",
        study_activity_name="Erythrocytes",
        study_visit_uid="StudyVisit_000015",
        study_visit_name="Visit 4",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 39, 653893),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000141",
        study_activity_uid="StudyActivity_000037",
        study_activity_name="Weight",
        study_visit_uid="StudyVisit_000013",
        study_visit_name="Visit 2",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 27, 524314),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000136",
        study_activity_uid="StudyActivity_000037",
        study_activity_name="Weight",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 25, 471663),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000143",
        study_activity_uid="StudyActivity_000037",
        study_activity_name="Weight",
        study_visit_uid="StudyVisit_000019",
        study_visit_name="Visit 8",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 28, 215687),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000142",
        study_activity_uid="StudyActivity_000037",
        study_activity_name="Weight",
        study_visit_uid="StudyVisit_000016",
        study_visit_name="Visit 5",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 27, 860010),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000208",
        study_activity_uid="StudyActivity_000037",
        study_activity_name="Weight",
        study_visit_uid="StudyVisit_000017",
        study_visit_name="Visit 6",
        start_date=datetime.datetime(2023, 9, 28, 7, 8, 33, 734000),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000170",
        study_activity_uid="StudyActivity_000037",
        study_activity_name="Weight",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 41, 88442),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000144",
        study_activity_uid="StudyActivity_000037",
        study_activity_name="Weight",
        study_visit_uid="StudyVisit_000022",
        study_visit_name="Visit 11",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 28, 558020),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000211",
        study_activity_uid="StudyActivity_000037",
        study_activity_name="Weight",
        study_visit_uid="StudyVisit_000018",
        study_visit_name="Visit 7",
        start_date=datetime.datetime(2023, 9, 28, 7, 8, 35, 385759),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000176",
        study_activity_uid="StudyActivity_000037",
        study_activity_name="Weight",
        study_visit_uid="StudyVisit_000016",
        study_visit_name="Visit 5",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 43, 507686),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000205",
        study_activity_uid="StudyActivity_000037",
        study_activity_name="Weight",
        study_visit_uid="StudyVisit_000017",
        study_visit_name="Visit 6",
        start_date=datetime.datetime(2023, 9, 28, 7, 8, 33, 509835),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000214",
        study_activity_uid="StudyActivity_000037",
        study_activity_name="Weight",
        study_visit_uid="StudyVisit_000018",
        study_visit_name="Visit 7",
        start_date=datetime.datetime(2023, 9, 28, 7, 8, 35, 607005),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000175",
        study_activity_uid="StudyActivity_000037",
        study_activity_name="Weight",
        study_visit_uid="StudyVisit_000013",
        study_visit_name="Visit 2",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 43, 151406),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000221",
        study_activity_uid="StudyActivity_000036",
        study_activity_name="Height",
        study_visit_uid="StudyVisit_000020",
        study_visit_name="Visit 9",
        start_date=datetime.datetime(2023, 9, 28, 7, 18, 20, 595234),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000169",
        study_activity_uid="StudyActivity_000036",
        study_activity_name="Height",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 40, 711597),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000220",
        study_activity_uid="StudyActivity_000036",
        study_activity_name="Height",
        study_visit_uid="StudyVisit_000014",
        study_visit_name="Visit 3",
        start_date=datetime.datetime(2023, 9, 28, 7, 18, 16, 760068),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000219",
        study_activity_uid="StudyActivity_000035",
        study_activity_name="Medical History/Concomitant Illness",
        study_visit_uid="StudyVisit_000022",
        study_visit_name="Visit 11",
        start_date=datetime.datetime(2023, 9, 28, 7, 17, 58, 133816),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000218",
        study_activity_uid="StudyActivity_000035",
        study_activity_name="Medical History/Concomitant Illness",
        study_visit_uid="StudyVisit_000013",
        study_visit_name="Visit 2",
        start_date=datetime.datetime(2023, 9, 28, 7, 17, 53, 408971),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000217",
        study_activity_uid="StudyActivity_000035",
        study_activity_name="Medical History/Concomitant Illness",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 28, 7, 17, 50, 576524),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000134",
        study_activity_uid="StudyActivity_000034",
        study_activity_name="Eligibility Criteria Met",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 24, 778118),
        user_initials="unknown-user",
        end_date=None,
    ),
    StudyActivitySchedule(
        study_uid="Study_000002",
        study_activity_schedule_uid="StudyActivitySchedule_000168",
        study_activity_uid="StudyActivity_000034",
        study_activity_name="Eligibility Criteria Met",
        study_visit_uid="StudyVisit_000012",
        study_visit_name="Visit 1",
        start_date=datetime.datetime(2023, 9, 25, 11, 42, 40, 366106),
        user_initials="unknown-user",
        end_date=None,
    ),
]

COORDINATES = {
    "StudyEpoch_000004": (0, 1),
    "StudyVisit_000012": (1, 1),
    "StudyEpoch_000005": (0, 2),
    "StudyVisit_000013": (1, 2),
    "StudyVisit_000014": (1, 3),
    "StudyVisit_000015": (1, 4),
    "StudyEpoch_000006": (0, 5),
    "StudyVisit_000016": (1, 5),
    "StudyEpoch_000007": (0, 6),
    "StudyVisit_000019": (1, 6),
    "StudyVisit_000020": (1, 7),
    "StudyVisit_000021": (1, 8),
    "StudyEpoch_000008": (0, 9),
    "StudyVisit_000022": (1, 9),
    "StudyEpoch_000009": (0, 10),
    "StudyVisit_000023": (1, 10),
    "StudyVisit_000024": (1, 11),
    "StudySoAGroup_000033": (2, 0),
    "StudyActivityGroup_000033": (3, 0),
    "StudyActivitySubGroup_000033": (4, 0),
    "StudyActivity_000033": (5, 0),
    "StudyActivitySchedule_000237": (5, 10),
    "StudyActivitySchedule_000224": (5, 7),
    "StudyActivitySchedule_000223": (5, 6),
    "StudyActivitySchedule_000222": (5, 5),
    "StudyActivitySchedule_000167": (5, 1),
    "StudyActivity_000041": (6, 0),
    "StudyActivitySchedule_000146": (6, 2),
    "StudyActivitySchedule_000148": (6, 3),
    "StudyActivitySchedule_000140": (6, 1),
    "StudyActivitySchedule_000186": (6, 4),
    "StudyActivitySchedule_000207": (6, 6),
    "StudyActivitySchedule_000184": (6, 5),
    "StudyActivitySchedule_000215": (6, 7),
    "StudyActivityGroup_000034": (7, 0),
    "StudyActivitySubGroup_000034": (8, 0),
    "StudyActivity_000034": (9, 0),
    "StudyActivitySchedule_000168": (9, 1),
    "StudyActivityGroup_000035": (10, 0),
    "StudyActivitySubGroup_000035": (11, 0),
    "StudyActivity_000035": (12, 0),
    "StudyActivitySchedule_000219": (12, 11),
    "StudyActivitySchedule_000218": (12, 2),
    "StudyActivitySchedule_000217": (12, 1),
    "StudyActivityGroup_000036": (13, 0),
    "StudyActivitySubGroup_000036": (14, 0),
    "StudyActivity_000036": (15, 0),
    "StudyActivitySchedule_000221": (15, 9),
    "StudyActivitySchedule_000169": (15, 1),
    "StudyActivitySchedule_000220": (15, 3),
    "StudyActivity_000037": (16, 0),
    "StudyActivitySchedule_000175": (16, 2),
    "StudyActivitySchedule_000170": (16, 1),
    "StudyActivitySchedule_000143": (16, 8),
    "StudyActivitySchedule_000176": (16, 5),
    "StudyActivitySchedule_000205": (16, 6),
    "StudyActivitySchedule_000144": (16, 11),
    "StudyActivitySchedule_000214": (16, 7),
    "StudyActivityGroup_000038": (17, 0),
    "StudyActivitySubGroup_000038": (18, 0),
    "StudyActivity_000038": (19, 0),
    "StudyActivitySchedule_000166": (19, 4),
    "StudyActivitySchedule_000173": (19, 1),
    "StudyActivitySchedule_000165": (19, 11),
    "StudyActivityGroup_000039": (20, 0),
    "StudyActivitySubGroup_000039": (21, 0),
    "StudyActivity_000039": (22, 0),
    "StudyActivitySchedule_000216": (22, 7),
    "StudyActivitySchedule_000206": (22, 6),
    "StudyActivitySchedule_000145": (22, 2),
    "StudyActivitySchedule_000187": (22, 4),
    "StudyActivitySchedule_000151": (22, 5),
    "StudyActivitySchedule_000137": (22, 1),
    "StudyActivitySchedule_000179": (22, 3),
    "StudyActivitySchedule_000163": (22, 11),
    "StudyActivity_000040": (23, 0),
    "StudyActivitySchedule_000235": (23, 10),
    "StudyActivitySchedule_000232": (23, 8),
    "StudyActivitySchedule_000231": (23, 7),
    "StudyActivitySchedule_000230": (23, 6),
    "StudyActivitySchedule_000229": (23, 5),
    "StudyActivitySchedule_000228": (23, 3),
    "StudyActivitySchedule_000227": (23, 1),
}

FOOTNOTES = [
    StudySoAFootnote(
        uid="StudySoAFootnote_000011",
        study_uid="Study_000002",
        order=1,
        modified=datetime.datetime(2023, 9, 28, 14, 2, 41, 550812),
        referenced_items=[
            ReferencedItem(
                item_uid="StudyEpoch_000004",
                item_name="Screening",
                item_type=SoAItemType.STUDY_EPOCH,
            ),
            ReferencedItem(
                item_uid="StudyVisit_000015",
                item_name="V4",
                item_type=SoAItemType.STUDY_VISIT,
            ),
        ],
        footnote=Footnote(
            uid="Footnote_000011",
            name="<p>A lovestruck Romeo sing the streets of serenade</p>",
            name_plain="A lovestruck Romeo sing the streets of serenade",
            start_date=datetime.datetime(2023, 9, 26, 21, 42, 25, 947953),
            end_date=None,
            status="Final",
            version="1.0",
            change_description="Approved version",
            user_initials="unknown-user",
            possible_actions=["inactivate"],
            footnote_template=FootnoteTemplateWithType(
                name="<p>A lovestruck Romeo sing the streets of serenade</p>",
                name_plain="A lovestruck Romeo sing the streets of serenade",
                uid="FootnoteTemplate_000012",
                sequence_id="FSA12",
                library_name="User Defined",
                type=None,
            ),
            parameter_terms=[],
            library=Library(name="User Defined", is_editable=True),
            study_count=0,
        ),
        footnote_template=None,
    ),
    StudySoAFootnote(
        uid="StudySoAFootnote_000012",
        study_uid="Study_000002",
        order=2,
        modified=datetime.datetime(2023, 9, 28, 14, 5, 43, 56490),
        referenced_items=[
            ReferencedItem(
                item_uid="StudyActivity_000039",
                item_name="Systolic Blood Pressure",
                item_type=SoAItemType.STUDY_ACTIVITY,
            ),
            ReferencedItem(
                item_uid="StudyActivity_000038",
                item_name="Erythrocytes",
                item_type=SoAItemType.STUDY_ACTIVITY,
            ),
            ReferencedItem(
                item_uid="StudyActivitySubGroup_000036",
                item_name="Body Measurements",
                item_type=SoAItemType.STUDY_ACTIVITY_SUBGROUP,
            ),
            ReferencedItem(
                item_uid="StudyActivitySubGroup_000037",
                item_name="Body Measurements",
                item_type=SoAItemType.STUDY_ACTIVITY_SUBGROUP,
            ),
            ReferencedItem(
                item_uid="StudyActivitySubGroup_000038",
                item_name="Haematology",
                item_type=SoAItemType.STUDY_ACTIVITY_SUBGROUP,
            ),
            ReferencedItem(
                item_uid="StudyActivityGroup_000038",
                item_name="Laboratory Assessments",
                item_type=SoAItemType.STUDY_ACTIVITY_GROUP,
            ),
            ReferencedItem(
                item_uid="StudyVisit_000012",
                item_name="V1",
                item_type=SoAItemType.STUDY_VISIT,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000144",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000147",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
        ],
        footnote=Footnote(
            uid="Footnote_000012",
            name="<p>Laying everybody low with the love song that he made</p>",
            name_plain="Laying everybody low with the love song that he made",
            start_date=datetime.datetime(2023, 9, 26, 21, 43, 13, 45570),
            end_date=None,
            status="Final",
            version="1.0",
            change_description="Approved version",
            user_initials="unknown-user",
            possible_actions=["inactivate"],
            footnote_template=FootnoteTemplateWithType(
                name="<p>Laying everybody low with the love song that he made</p>",
                name_plain="Laying everybody low with the love song that he made",
                uid="FootnoteTemplate_000013",
                sequence_id="FSA13",
                library_name="User Defined",
                type=None,
            ),
            parameter_terms=[],
            library=Library(name="User Defined", is_editable=True),
            study_count=0,
        ),
        footnote_template=None,
    ),
    StudySoAFootnote(
        uid="StudySoAFootnote_000013",
        study_uid="Study_000002",
        order=3,
        modified=datetime.datetime(2023, 9, 28, 14, 5, 13, 667573),
        referenced_items=[
            ReferencedItem(
                item_uid="StudyActivitySchedule_000142",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000176",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000205",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000137",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000175",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000220",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000208",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000214",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000211",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
        ],
        footnote=Footnote(
            uid="Footnote_000013",
            name="<p>Finds a convenient streetlight, steps out of the shade</p>",
            name_plain="Finds a convenient streetlight, steps out of the shade",
            start_date=datetime.datetime(2023, 9, 26, 21, 43, 48, 36499),
            end_date=None,
            status="Final",
            version="1.0",
            change_description="Approved version",
            user_initials="unknown-user",
            possible_actions=["inactivate"],
            footnote_template=FootnoteTemplateWithType(
                name="<p>Finds a convenient streetlight, steps out of the shade</p>",
                name_plain="Finds a convenient streetlight, steps out of the shade",
                uid="FootnoteTemplate_000014",
                sequence_id="FSA14",
                library_name="User Defined",
                type=None,
            ),
            parameter_terms=[],
            library=Library(name="User Defined", is_editable=True),
            study_count=0,
        ),
        footnote_template=None,
    ),
    StudySoAFootnote(
        uid="StudySoAFootnote_000014",
        study_uid="Study_000002",
        order=4,
        modified=datetime.datetime(2023, 9, 28, 14, 5, 13, 838614),
        referenced_items=[
            ReferencedItem(
                item_uid="StudyActivity_000039",
                item_name="Systolic Blood Pressure",
                item_type=SoAItemType.STUDY_ACTIVITY,
            ),
            ReferencedItem(
                item_uid="StudyActivitySubGroup_000038",
                item_name="Haematology",
                item_type=SoAItemType.STUDY_ACTIVITY_SUBGROUP,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000221",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000211",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000176",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000142",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000235",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000214",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000208",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000205",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
            ReferencedItem(
                item_uid="StudyActivitySchedule_000145",
                item_name=None,
                item_type=SoAItemType.STUDY_ACTIVITY_SCHEDULE,
            ),
        ],
        footnote=Footnote(
            uid="Footnote_000008",
            name='<p>Says something like "You and me babe, how about it?"</p>',
            name_plain='Says something like "You and me babe, how about it?"',
            start_date=datetime.datetime(2023, 9, 26, 10, 50, 43, 523495),
            end_date=None,
            status="Final",
            version="1.0",
            change_description="Approved version",
            user_initials="unknown-user",
            possible_actions=["inactivate"],
            footnote_template=FootnoteTemplateWithType(
                name='<p>Says something like "You and me babe, how about it?"</p>',
                name_plain='Says something like "You and me babe, how about it?"',
                uid="FootnoteTemplate_000009",
                sequence_id="FSA9",
                library_name="User Defined",
                type=None,
            ),
            parameter_terms=[],
            library=Library(name="User Defined", is_editable=True),
            study_count=0,
        ),
        footnote_template=None,
    ),
]

EXPECTED_SOA_TABLE = TableWithFootnotes(
    rows=[
        TableRow(
            cells=[
                TableCell(
                    text="",
                    span=1,
                    style="header1",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="Screening",
                    span=1,
                    style="header1",
                    refs=[Ref(type="StudyEpoch", uid="StudyEpoch_000004")],
                    footnotes=["a"],
                    vertical=True,
                ),
                TableCell(
                    text="Run-in",
                    span=2,
                    style="header1",
                    refs=[Ref(type="StudyEpoch", uid="StudyEpoch_000005")],
                    footnotes=None,
                    vertical=True,
                ),
                TableCell(
                    text="", span=0, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="Treatment 1",
                    span=1,
                    style="header1",
                    refs=[Ref(type="StudyEpoch", uid="StudyEpoch_000006")],
                    footnotes=None,
                    vertical=True,
                ),
                TableCell(
                    text="Treatment 2",
                    span=3,
                    style="header1",
                    refs=[Ref(type="StudyEpoch", uid="StudyEpoch_000007")],
                    footnotes=None,
                    vertical=True,
                ),
                TableCell(
                    text="", span=0, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=0, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="Follow-up",
                    span=1,
                    style="header1",
                    refs=[Ref(type="StudyEpoch", uid="StudyEpoch_000008")],
                    footnotes=None,
                    vertical=True,
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Visit short name",
                    span=1,
                    style="header2",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="V1",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000012")],
                    footnotes=["b"],
                    vertical=None,
                ),
                TableCell(
                    text="V2",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000013")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="V4",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000015")],
                    footnotes=["a"],
                    vertical=None,
                ),
                TableCell(
                    text="V5-V7",
                    span=1,
                    style="header2",
                    refs=[
                        Ref(type="StudyVisit", uid="StudyVisit_000016"),
                        Ref(type="StudyVisit", uid="StudyVisit_000017"),
                        Ref(type="StudyVisit", uid="StudyVisit_000018"),
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="V8",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000019")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="V9",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000020")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="V10",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000021")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="V11",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000022")],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Study day",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="-14",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="-3",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="-1",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="1-5",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="15",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="17",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="19",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="22",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Visit window (days)",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="SUBJECT RELATED INFORMATION",
                    span=1,
                    style="soaGroup",
                    refs=[Ref(type="StudySoAGroup", uid="StudySoAGroup_000033")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Informed Consent and Demography",
                    span=1,
                    style="group",
                    refs=[
                        Ref(type="StudyActivityGroup", uid="StudyActivityGroup_000033")
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Informed Consent and Demography",
                    span=1,
                    style="subGroup",
                    refs=[
                        Ref(
                            type="StudyActivitySubGroup",
                            uid="StudyActivitySubGroup_000033",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Informed Consent Obtained",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000033")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000167",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000222",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000237",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Date of Birth",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000041")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000140",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000146",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000186",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000184",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Eligibility Criteria",
                    span=1,
                    style="group",
                    refs=[
                        Ref(type="StudyActivityGroup", uid="StudyActivityGroup_000034")
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Eligibility Criteria",
                    span=1,
                    style="subGroup",
                    refs=[
                        Ref(
                            type="StudyActivitySubGroup",
                            uid="StudyActivitySubGroup_000034",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Eligibility Criteria Met",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000034")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000168",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Medical History/Concomitant Illness",
                    span=1,
                    style="group",
                    refs=[
                        Ref(type="StudyActivityGroup", uid="StudyActivityGroup_000035")
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Medical History/Concomitant Illness",
                    span=1,
                    style="subGroup",
                    refs=[
                        Ref(
                            type="StudyActivitySubGroup",
                            uid="StudyActivitySubGroup_000035",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Medical History/Concomitant Illness",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000035")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000217",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000218",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000219",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Body Measurements",
                    span=1,
                    style="group",
                    refs=[
                        Ref(type="StudyActivityGroup", uid="StudyActivityGroup_000036")
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Body Measurements",
                    span=1,
                    style="subGroup",
                    refs=[
                        Ref(
                            type="StudyActivitySubGroup",
                            uid="StudyActivitySubGroup_000036",
                        )
                    ],
                    footnotes=["b"],
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Height",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000036")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000169",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000221",
                        )
                    ],
                    footnotes=["d"],
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Weight",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000037")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000170",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000175",
                        )
                    ],
                    footnotes=["c"],
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000176",
                        )
                    ],
                    footnotes=["c", "d"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000143",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000144",
                        )
                    ],
                    footnotes=["b"],
                    vertical=None,
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Laboratory Assessments",
                    span=1,
                    style="group",
                    refs=[
                        Ref(type="StudyActivityGroup", uid="StudyActivityGroup_000038")
                    ],
                    footnotes=["b"],
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Haematology",
                    span=1,
                    style="subGroup",
                    refs=[
                        Ref(
                            type="StudyActivitySubGroup",
                            uid="StudyActivitySubGroup_000038",
                        )
                    ],
                    footnotes=["b", "d"],
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Erythrocytes",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000038")],
                    footnotes=["b"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000173",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000166",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000165",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Vital Signs",
                    span=1,
                    style="group",
                    refs=[
                        Ref(type="StudyActivityGroup", uid="StudyActivityGroup_000039")
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Vital Signs",
                    span=1,
                    style="subGroup",
                    refs=[
                        Ref(
                            type="StudyActivitySubGroup",
                            uid="StudyActivitySubGroup_000039",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Systolic Blood Pressure",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000039")],
                    footnotes=["b", "d"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000137",
                        )
                    ],
                    footnotes=["c"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000145",
                        )
                    ],
                    footnotes=["d"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000187",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000151",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000163",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Diastolic Blood Pressure",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000040")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000227",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000229",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000232",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000235",
                        )
                    ],
                    footnotes=["d"],
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, ref=None, footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
    ],
    footnotes={
        "a": SimpleFootnote(
            uid="Footnote_000011",
            text_html="<p>A lovestruck Romeo sing the streets of serenade</p>",
            text_plain="A lovestruck Romeo sing the streets of serenade",
        ),
        "b": SimpleFootnote(
            uid="Footnote_000012",
            text_html="<p>Laying everybody low with the love song that he made</p>",
            text_plain="Laying everybody low with the love song that he made",
        ),
        "c": SimpleFootnote(
            uid="Footnote_000013",
            text_html="<p>Finds a convenient streetlight, steps out of the shade</p>",
            text_plain="Finds a convenient streetlight, steps out of the shade",
        ),
        "d": SimpleFootnote(
            uid="Footnote_000008",
            text_html='<p>Says something like "You and me babe, how about it?"</p>',
            text_plain='Says something like "You and me babe, how about it?"',
        ),
    },
    num_header_rows=4,
    num_header_cols=1,
    title="Protocol Flowchart",
)

EXPECTED_PROTOCOL_SOA_TABLE = TableWithFootnotes(
    rows=[
        TableRow(
            cells=[
                TableCell(
                    text="",
                    span=1,
                    style="header1",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="Screening",
                    span=1,
                    style="header1",
                    refs=[Ref(type="StudyEpoch", uid="StudyEpoch_000004")],
                    footnotes=["a"],
                    vertical=True,
                ),
                TableCell(
                    text="Run-in",
                    span=2,
                    style="header1",
                    refs=[Ref(type="StudyEpoch", uid="StudyEpoch_000005")],
                    footnotes=None,
                    vertical=True,
                ),
                TableCell(
                    text="", span=0, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="Treatment 1",
                    span=1,
                    style="header1",
                    refs=[Ref(type="StudyEpoch", uid="StudyEpoch_000006")],
                    footnotes=None,
                    vertical=True,
                ),
                TableCell(
                    text="Treatment 2",
                    span=3,
                    style="header1",
                    refs=[Ref(type="StudyEpoch", uid="StudyEpoch_000007")],
                    footnotes=None,
                    vertical=True,
                ),
                TableCell(
                    text="", span=0, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=0, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="Follow-up",
                    span=1,
                    style="header1",
                    refs=[Ref(type="StudyEpoch", uid="StudyEpoch_000008")],
                    footnotes=None,
                    vertical=True,
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Visit short name",
                    span=1,
                    style="header2",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="V1",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000012")],
                    footnotes=["b"],
                    vertical=None,
                ),
                TableCell(
                    text="V2",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000013")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="V4",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000015")],
                    footnotes=["a"],
                    vertical=None,
                ),
                TableCell(
                    text="V5-V7",
                    span=1,
                    style="header2",
                    refs=[
                        Ref(type="StudyVisit", uid="StudyVisit_000016"),
                        Ref(type="StudyVisit", uid="StudyVisit_000017"),
                        Ref(type="StudyVisit", uid="StudyVisit_000018"),
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="V8",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000019")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="V9",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000020")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="V10",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000021")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="V11",
                    span=1,
                    style="header2",
                    refs=[Ref(type="StudyVisit", uid="StudyVisit_000022")],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Study day",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="-14",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="-3",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="-1",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="1-5",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="15",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="17",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="19",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="22",
                    span=1,
                    style="header3",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Visit window (days)",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="±0",
                    span=1,
                    style="header4",
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="SUBJECT RELATED INFORMATION",
                    span=1,
                    style="soaGroup",
                    refs=[Ref(type="StudySoAGroup", uid="StudySoAGroup_000033")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Informed Consent and Demography",
                    span=1,
                    style="group",
                    refs=[
                        Ref(type="StudyActivityGroup", uid="StudyActivityGroup_000033")
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Informed Consent and Demography",
                    span=1,
                    style="subGroup",
                    refs=[
                        Ref(
                            type="StudyActivitySubGroup",
                            uid="StudyActivitySubGroup_000033",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Informed Consent Obtained",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000033")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000167",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000222",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000237",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Date of Birth",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000041")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000140",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000146",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000186",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000184",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Eligibility Criteria",
                    span=1,
                    style="group",
                    refs=[
                        Ref(type="StudyActivityGroup", uid="StudyActivityGroup_000034")
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Eligibility Criteria",
                    span=1,
                    style="subGroup",
                    refs=[
                        Ref(
                            type="StudyActivitySubGroup",
                            uid="StudyActivitySubGroup_000034",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Eligibility Criteria Met",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000034")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000168",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Medical History/Concomitant Illness",
                    span=1,
                    style="group",
                    refs=[
                        Ref(type="StudyActivityGroup", uid="StudyActivityGroup_000035")
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Medical History/Concomitant Illness",
                    span=1,
                    style="subGroup",
                    refs=[
                        Ref(
                            type="StudyActivitySubGroup",
                            uid="StudyActivitySubGroup_000035",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Medical History/Concomitant Illness",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000035")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000217",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000218",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000219",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Body Measurements",
                    span=1,
                    style="group",
                    refs=[
                        Ref(type="StudyActivityGroup", uid="StudyActivityGroup_000036")
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Body Measurements",
                    span=1,
                    style="subGroup",
                    refs=[
                        Ref(
                            type="StudyActivitySubGroup",
                            uid="StudyActivitySubGroup_000036",
                        )
                    ],
                    footnotes=["b"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=["c"],
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=["c", "d"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=["d"],
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=["b"],
                    vertical=None,
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Height",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000036")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000169",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000221",
                        )
                    ],
                    footnotes=["d"],
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Weight",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000037")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000170",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000175",
                        )
                    ],
                    footnotes=["c"],
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000176",
                        )
                    ],
                    footnotes=["c", "d"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000143",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000144",
                        )
                    ],
                    footnotes=["b"],
                    vertical=None,
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Laboratory Assessments",
                    span=1,
                    style="group",
                    refs=[
                        Ref(type="StudyActivityGroup", uid="StudyActivityGroup_000038")
                    ],
                    footnotes=["b"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Haematology",
                    span=1,
                    style="subGroup",
                    refs=[
                        Ref(
                            type="StudyActivitySubGroup",
                            uid="StudyActivitySubGroup_000038",
                        )
                    ],
                    footnotes=["b", "d"],
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Erythrocytes",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000038")],
                    footnotes=["b"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000173",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000166",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000165",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Vital Signs",
                    span=1,
                    style="group",
                    refs=[
                        Ref(type="StudyActivityGroup", uid="StudyActivityGroup_000039")
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Vital Signs",
                    span=1,
                    style="subGroup",
                    refs=[
                        Ref(
                            type="StudyActivitySubGroup",
                            uid="StudyActivitySubGroup_000039",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=["c"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=["d"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=["d"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style=None,
                    refs=[],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=False,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Systolic Blood Pressure",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000039")],
                    footnotes=["b", "d"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000137",
                        )
                    ],
                    footnotes=["c"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000145",
                        )
                    ],
                    footnotes=["d"],
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000187",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000151",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000163",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
            ],
            hide=True,
        ),
        TableRow(
            cells=[
                TableCell(
                    text="Diastolic Blood Pressure",
                    span=1,
                    style="activity",
                    refs=[Ref(type="StudyActivity", uid="StudyActivity_000040")],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000227",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000229",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000232",
                        )
                    ],
                    footnotes=None,
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, refs=[], footnotes=None, vertical=None
                ),
                TableCell(
                    text="X",
                    span=1,
                    style="activitySchedule",
                    refs=[
                        Ref(
                            type="StudyActivitySchedule",
                            uid="StudyActivitySchedule_000235",
                        )
                    ],
                    footnotes=["d"],
                    vertical=None,
                ),
                TableCell(
                    text="", span=1, style=None, ref=None, footnotes=None, vertical=None
                ),
            ],
            hide=True,
        ),
    ],
    footnotes={
        "a": SimpleFootnote(
            uid="Footnote_000011",
            text_html="<p>A lovestruck Romeo sing the streets of serenade</p>",
            text_plain="A lovestruck Romeo sing the streets of serenade",
        ),
        "b": SimpleFootnote(
            uid="Footnote_000012",
            text_html="<p>Laying everybody low with the love song that he made</p>",
            text_plain="Laying everybody low with the love song that he made",
        ),
        "c": SimpleFootnote(
            uid="Footnote_000013",
            text_html="<p>Finds a convenient streetlight, steps out of the shade</p>",
            text_plain="Finds a convenient streetlight, steps out of the shade",
        ),
        "d": SimpleFootnote(
            uid="Footnote_000008",
            text_html='<p>Says something like "You and me babe, how about it?"</p>',
            text_plain='Says something like "You and me babe, how about it?"',
        ),
    },
    num_header_rows=4,
    num_header_cols=1,
    title="Protocol Flowchart",
)
