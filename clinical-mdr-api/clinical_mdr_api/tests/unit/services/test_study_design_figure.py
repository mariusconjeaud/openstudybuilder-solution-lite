import datetime
from collections import OrderedDict

from clinical_mdr_api.models import (
    CTTermName,
    StudyDesignCell,
    StudySelectionArmWithConnectedBranchArms,
    StudySelectionElement,
)
from clinical_mdr_api.models.study_epoch import StudyEpoch
from clinical_mdr_api.services.study_design_figure import StudyDesignFigureService
from clinical_mdr_api.tests.unit.services.test_study_flowchart import (
    STUDY_VISITS as _STUDY_VISITS,
)

STUDY_UID = "Study_000001"

USER_INITIALS = "unknown-user"

STUDY_ARMS = OrderedDict(
    (
        (
            "StudyArm_000009",
            StudySelectionArmWithConnectedBranchArms(
                study_uid=STUDY_UID,
                order=1,
                arm_uid="StudyArm_000009",
                name="NPH insulin",
                short_name="NPH insulin",
                description=None,
                code="A",
                arm_colour="#FFFDE7FF",
                randomization_group="A",
                number_of_subjects=50,
                arm_type=CTTermName(
                    term_uid="CTTerm_000081",
                    codelist_uid="CTCodelist_000022",
                    sponsor_preferred_name="Investigational Arm",
                    sponsor_preferred_name_sentence_case="investigational arm",
                    order=1,
                    start_date=datetime.datetime(2022, 7, 14, 11, 18, 29, 635044),
                ),
                start_date=datetime.datetime(2022, 8, 25, 19, 32, 11, 640636),
                user_initials=USER_INITIALS,
            ),
        ),
        (
            "StudyArm_000011",
            StudySelectionArmWithConnectedBranchArms(
                study_uid=STUDY_UID,
                order=2,
                arm_uid="StudyArm_000011",
                name="Metformin",
                short_name="Metformin is longer",
                description=None,
                code="B",
                arm_colour="#FFEBEEFF",
                randomization_group="B",
                number_of_subjects=50,
                arm_type=CTTermName(
                    term_uid="CTTerm_000081",
                    codelist_uid="CTCodelist_000022",
                    sponsor_preferred_name="Investigational Arm",
                    sponsor_preferred_name_sentence_case="investigational arm",
                    order=1,
                    start_date=datetime.datetime(2022, 7, 14, 11, 18, 29, 635044),
                ),
                start_date=datetime.datetime(2022, 8, 25, 9, 33, 24, 232339),
                user_initials=USER_INITIALS,
            ),
        ),
        (
            "StudyArm_000045",
            StudySelectionArmWithConnectedBranchArms(
                study_uid=STUDY_UID,
                order=3,
                arm_uid="StudyArm_000045",
                name="Another arm",
                short_name="Another arm",
                description=None,
                code=None,
                arm_colour="#F3E5F5FF",
                randomization_group=None,
                number_of_subjects=None,
                arm_type=None,
                start_date=datetime.datetime(2022, 8, 25, 19, 32, 0, 886693),
                user_initials=USER_INITIALS,
            ),
        ),
        (
            "StudyArm_000048",
            StudySelectionArmWithConnectedBranchArms(
                study_uid=STUDY_UID,
                order=4,
                arm_uid="StudyArm_000048",
                name="More arms",
                short_name="More arms",
                description=None,
                code=None,
                arm_colour="#E8EAF6FF",
                randomization_group=None,
                number_of_subjects=None,
                arm_type=None,
                start_date=datetime.datetime(2022, 8, 25, 19, 46, 11, 300649),
                user_initials=USER_INITIALS,
            ),
        ),
    )
)

STUDY_EPOCHS = OrderedDict(
    (
        (
            "StudyEpoch_000001",
            StudyEpoch(
                study_uid=STUDY_UID,
                start_rule="Subject must sign informed consent",
                epoch="C48262_SCREENING",
                epoch_subtype="C48262_SCREENING",
                order=1,
                duration=15,
                color_hash="#A5D6A7FF",
                uid="StudyEpoch_000001",
                epoch_name="Screening",
                epoch_subtype_name="Screening",
                epoch_type="CTTerm_000001",
                start_day=-14,
                end_day=1,
                start_date="2022-07-16 09:13:42",
                status="DRAFT",
                user_initials="TODO Initials",
                possible_actions=["edit", "delete", "lock"],
                change_description="Initial Version",
                study_visit_count=1,
            ),
        ),
        (
            "StudyEpoch_000002",
            StudyEpoch(
                study_uid=STUDY_UID,
                start_rule="Subject must fulfil randomisation criteria",
                epoch="C101526_TREATMENT",
                epoch_subtype="C101526_TREATMENT",
                order=2,
                duration=63,
                color_hash="#2E7D32FF",
                uid="StudyEpoch_000002",
                epoch_name="Treatment",
                epoch_subtype_name="Treatment",
                epoch_type="C101526_TREATMENT",
                start_day=1,
                end_day=64,
                start_date="2022-07-16 09:13:42",
                status="DRAFT",
                user_initials="TODO Initials",
                possible_actions=["edit", "delete", "lock"],
                change_description="Initial Version",
                study_visit_count=9,
            ),
        ),
        (
            "StudyEpoch_000042",
            StudyEpoch(
                study_uid=STUDY_UID,
                start_rule="",
                epoch="CTTerm_000007",
                epoch_subtype="CTTerm_000007",
                order=3,
                description="Treatment Extension",
                duration=119,
                color_hash="#80DEEAFF",
                uid="StudyEpoch_000042",
                epoch_name="Extension",
                epoch_subtype_name="Extension",
                epoch_type="C101526_TREATMENT",
                start_day=64,
                end_day=183,
                start_date="2022-08-26 02:06:50",
                status="DRAFT",
                user_initials="TODO Initials",
                possible_actions=["edit", "delete", "lock"],
                change_description="Initial Version",
                study_visit_count=1,
            ),
        ),
        (
            "StudyEpoch_000003",
            StudyEpoch(
                study_uid=STUDY_UID,
                start_rule="Subject must attend follow-up visit",
                epoch="C99158_FOLLOW-UP",
                epoch_subtype="C99158_FOLLOW-UP",
                order=4,
                duration=183,
                color_hash="#009688FF",
                uid="StudyEpoch_000003",
                epoch_name="Follow-up",
                epoch_subtype_name="Follow-up",
                epoch_type="CTTerm_000003",
                start_day=183,
                end_day=366,
                start_date="2022-08-26 02:06:50",
                status="DRAFT",
                user_initials="TODO Initials",
                possible_actions=["edit", "delete", "lock"],
                change_description="Initial Version",
                study_visit_count=1,
            ),
        ),
        (
            "StudyEpoch_000034",
            StudyEpoch(
                study_uid=STUDY_UID,
                epoch="CTTerm_000008",
                epoch_subtype="CTTerm_000008",
                order=5,
                description="Hula lula",
                duration=7,
                color_hash="#C5CAE9FF",
                uid="StudyEpoch_000034",
                epoch_name="Elimination",
                epoch_subtype_name="Elimination",
                epoch_type="CTTerm_000003",
                start_day=366,
                end_day=373,
                start_date="2022-08-26 02:06:50",
                status="DRAFT",
                user_initials="TODO Initials",
                possible_actions=["edit", "delete", "lock"],
                change_description="Initial Version",
                study_visit_count=1,
            ),
        ),
        (
            "StudyEpoch_000041",
            StudyEpoch(
                study_uid=STUDY_UID,
                epoch="CTTerm_000005",
                epoch_subtype="CTTerm_000005",
                order=6,
                duration=0,
                color_hash="#80CBC4FF",
                uid="StudyEpoch_000041",
                epoch_name="Dose Escalation",
                epoch_subtype_name="Dose Escalation",
                epoch_type="C101526_TREATMENT",
                start_date="2022-08-26 02:06:50",
                status="DRAFT",
                user_initials="TODO Initials",
                possible_actions=["edit", "delete", "lock", "reorder"],
                change_description="Initial Version",
                study_visit_count=0,
            ),
        ),
    )
)

STUDY_ELEMENTS = OrderedDict(
    (
        (
            "StudyElement_000018",
            StudySelectionElement(
                study_uid=STUDY_UID,
                order=1,
                start_rule=None,
                end_rule=None,
                description=None,
                element_uid="StudyElement_000018",
                name="Screening",
                short_name="Screening",
                code="CTTerm_000130",
                planned_duration=None,
                element_colour=None,
                element_type=None,
                element_subtype=CTTermName(
                    term_uid="CTTerm_000135",
                    codelist_uid="CTCodelist_000024",
                    sponsor_preferred_name="Screening",
                    sponsor_preferred_name_sentence_case="screening",
                    order=1,
                    start_date=datetime.datetime(2022, 7, 14, 11, 18, 43, 459307),
                ),
                study_compound_dosing_count=0,
                start_date=datetime.datetime(2022, 7, 22, 9, 57, 9, 373874),
                user_initials=USER_INITIALS,
            ),
        ),
        (
            "StudyElement_000020",
            StudySelectionElement(
                study_uid=STUDY_UID,
                order=2,
                start_rule=None,
                end_rule=None,
                description=None,
                element_uid="StudyElement_000020",
                name="NPH insulin",
                short_name="NPH insulin",
                code="CTTerm_000129",
                planned_duration=None,
                element_colour=None,
                element_type=None,
                element_subtype=CTTermName(
                    term_uid="CTTerm_000131",
                    codelist_uid="CTCodelist_000024",
                    sponsor_preferred_name="Treatment",
                    sponsor_preferred_name_sentence_case="treatment",
                    order=3,
                    start_date=datetime.datetime(2022, 7, 14, 11, 18, 42, 889737),
                ),
                study_compound_dosing_count=0,
                start_date=datetime.datetime(2022, 7, 22, 9, 57, 10, 406127),
                user_initials=USER_INITIALS,
            ),
        ),
        (
            "StudyElement_000022",
            StudySelectionElement(
                study_uid=STUDY_UID,
                order=3,
                start_rule=None,
                end_rule=None,
                description=None,
                element_uid="StudyElement_000022",
                name="Metformin",
                short_name="Metformin",
                code="CTTerm_000129",
                planned_duration=None,
                element_colour=None,
                element_type=None,
                element_subtype=CTTermName(
                    term_uid="CTTerm_000131",
                    codelist_uid="CTCodelist_000024",
                    sponsor_preferred_name="Treatment",
                    sponsor_preferred_name_sentence_case="treatment",
                    order=3,
                    start_date=datetime.datetime(2022, 7, 14, 11, 18, 42, 889737),
                ),
                study_compound_dosing_count=0,
                start_date=datetime.datetime(2022, 7, 22, 9, 57, 10, 503358),
                user_initials=USER_INITIALS,
            ),
        ),
        (
            "StudyElement_000024",
            StudySelectionElement(
                study_uid=STUDY_UID,
                order=4,
                start_rule=None,
                end_rule=None,
                description=None,
                element_uid="StudyElement_000024",
                name="Follow-up",
                short_name="Follow-up",
                code="CTTerm_000130",
                planned_duration=None,
                element_colour=None,
                element_type=None,
                element_subtype=CTTermName(
                    term_uid="CTTerm_000134",
                    codelist_uid="CTCodelist_000024",
                    sponsor_preferred_name="Follow-up",
                    sponsor_preferred_name_sentence_case="follow-up",
                    order=5,
                    start_date=datetime.datetime(2022, 7, 14, 11, 18, 43, 264949),
                ),
                study_compound_dosing_count=0,
                start_date=datetime.datetime(2022, 7, 22, 9, 57, 10, 985130),
                user_initials=USER_INITIALS,
            ),
        ),
    )
)

STUDY_DESIGN_CELLS = (
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000011",
        study_arm_uid="StudyArm_000009",
        study_arm_name="NPH insulin",
        study_epoch_uid="StudyEpoch_000001",
        study_epoch_name="Screening",
        study_element_uid="StudyElement_000018",
        study_element_name="Screening",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 16, 9, 37, 25, 904287),
        user_initials=USER_INITIALS,
        order=1,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000012",
        study_arm_uid="StudyArm_000009",
        study_arm_name="NPH insulin",
        study_epoch_uid="StudyEpoch_000002",
        study_epoch_name="Treatment",
        study_element_uid="StudyElement_000020",
        study_element_name="NPH insulin",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 16, 9, 37, 25, 749029),
        user_initials=USER_INITIALS,
        order=2,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000013",
        study_arm_uid="StudyArm_000009",
        study_arm_name="NPH insulin",
        study_epoch_uid="StudyEpoch_000003",
        study_epoch_name="Follow-up",
        study_element_uid="StudyElement_000024",
        study_element_name="Follow-up",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 16, 9, 37, 25, 583916),
        user_initials=USER_INITIALS,
        order=3,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000014",
        study_arm_uid="StudyArm_000009",
        study_arm_name="NPH insulin",
        study_epoch_uid="StudyEpoch_000034",
        study_epoch_name="Elimination",
        study_element_uid="StudyElement_000020",
        study_element_name="NPH insulin",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 16, 9, 37, 25, 309418),
        user_initials=USER_INITIALS,
        order=4,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000015",
        study_arm_uid="StudyArm_000011",
        study_arm_name="Metformin",
        study_epoch_uid="StudyEpoch_000001",
        study_epoch_name="Screening",
        study_element_uid="StudyElement_000018",
        study_element_name="Screening",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 16, 9, 35, 11, 107228),
        user_initials=USER_INITIALS,
        order=5,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000016",
        study_arm_uid="StudyArm_000011",
        study_arm_name="Metformin",
        study_epoch_uid="StudyEpoch_000002",
        study_epoch_name="Treatment",
        study_element_uid="StudyElement_000022",
        study_element_name="Metformin",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 16, 9, 35, 12, 69303),
        user_initials=USER_INITIALS,
        order=6,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000017",
        study_arm_uid="StudyArm_000011",
        study_arm_name="Metformin",
        study_epoch_uid="StudyEpoch_000003",
        study_epoch_name="Follow-up",
        study_element_uid="StudyElement_000024",
        study_element_name="Follow-up",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 16, 9, 35, 12, 323734),
        user_initials=USER_INITIALS,
        order=7,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000018",
        study_arm_uid="StudyArm_000011",
        study_arm_name="Metformin",
        study_epoch_uid="StudyEpoch_000034",
        study_epoch_name="Elimination",
        study_element_uid="StudyElement_000022",
        study_element_name="Metformin",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 16, 9, 35, 12, 591836),
        user_initials=USER_INITIALS,
        order=8,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000039",
        study_arm_uid="StudyArm_000045",
        study_arm_name="Another arm",
        study_epoch_uid="StudyEpoch_000002",
        study_epoch_name="Treatment",
        study_element_uid="StudyElement_000020",
        study_element_name="NPH insulin",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 25, 22, 54, 8, 133786),
        user_initials=USER_INITIALS,
        order=9,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000042",
        study_arm_uid="StudyArm_000045",
        study_arm_name="Another arm",
        study_epoch_uid="StudyEpoch_000003",
        study_epoch_name="Follow-up",
        study_element_uid="StudyElement_000020",
        study_element_name="NPH insulin",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 26, 2, 7, 34, 231184),
        user_initials=USER_INITIALS,
        order=10,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000044",
        study_arm_uid="StudyArm_000009",
        study_arm_name="NPH insulin",
        study_epoch_uid="StudyEpoch_000042",
        study_epoch_name="Extension",
        study_element_uid="StudyElement_000020",
        study_element_name="NPH insulin",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 26, 2, 7, 34, 318480),
        user_initials=USER_INITIALS,
        order=11,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000045",
        study_arm_uid="StudyArm_000011",
        study_arm_name="Metformin",
        study_epoch_uid="StudyEpoch_000042",
        study_epoch_name="Extension",
        study_element_uid="StudyElement_000022",
        study_element_name="Metformin",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 26, 2, 8, 31, 590352),
        user_initials=USER_INITIALS,
        order=12,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000046",
        study_arm_uid="StudyArm_000045",
        study_arm_name="Another arm",
        study_epoch_uid="StudyEpoch_000042",
        study_epoch_name="Extension",
        study_element_uid="StudyElement_000022",
        study_element_name="Metformin",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 26, 2, 8, 31, 765647),
        user_initials=USER_INITIALS,
        order=13,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000047",
        study_arm_uid="StudyArm_000009",
        study_arm_name="NPH insulin",
        study_epoch_uid="StudyEpoch_000042",
        study_epoch_name="Extension",
        study_element_uid="StudyElement_000020",
        study_element_name="NPH insulin",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 26, 2, 7, 59, 750359),
        user_initials=USER_INITIALS,
        order=14,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000048",
        study_arm_uid="StudyArm_000011",
        study_arm_name="Metformin",
        study_epoch_uid="StudyEpoch_000042",
        study_epoch_name="Extension",
        study_element_uid="StudyElement_000020",
        study_element_name="NPH insulin",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 26, 2, 8, 0, 315389),
        user_initials=USER_INITIALS,
        order=15,
    ),
    StudyDesignCell(
        study_uid=STUDY_UID,
        design_cell_uid="StudyDesignCell_000049",
        study_arm_uid="StudyArm_000045",
        study_arm_name="Another arm",
        study_epoch_uid="StudyEpoch_000042",
        study_epoch_name="Extension",
        study_element_uid="StudyElement_000020",
        study_element_name="NPH insulin",
        transition_rule=None,
        start_date=datetime.datetime(2022, 8, 26, 2, 8, 0, 807474),
        user_initials=USER_INITIALS,
        order=16,
    ),
)

STUDY_VISITS = OrderedDict((visit.uid, visit) for visit in _STUDY_VISITS.items)

MATRIX = [
    [
        {},
        {
            "klass": "epoch",
            "id": "StudyEpoch_000001",
            "text": "Screening",
            "colors": ("#a5d6a7", "#204621", "#000"),
            "margin": 10,
            "paddings": (3, 3),
        },
        {
            "klass": "epoch",
            "id": "StudyEpoch_000002",
            "text": "Treatment",
            "colors": ("#2e7d32", "#1b4b1e", "#fff"),
            "margin": 10,
            "paddings": (3, 3),
        },
        {
            "klass": "epoch",
            "id": "StudyEpoch_000042",
            "text": "Extension",
            "colors": ("#80deea", "#0e4f58", "#000"),
            "margin": 10,
            "paddings": (3, 3),
        },
        {
            "klass": "epoch",
            "id": "StudyEpoch_000003",
            "text": "Follow-up",
            "colors": ("#009688", "#00665c", "#fff"),
            "margin": 10,
            "paddings": (3, 3),
        },
        {
            "klass": "epoch",
            "id": "StudyEpoch_000034",
            "text": "Elimination",
            "colors": ("#c5cae9", "#1c224a", "#000"),
            "margin": 10,
            "paddings": (3, 3),
        },
        {
            "klass": "epoch",
            "id": "StudyEpoch_000041",
            "text": "Dose Escalation",
            "colors": ("#80cbc4", "#1e4844", "#000"),
            "margin": 10,
            "paddings": (3, 3),
        },
    ],
    [
        {
            "klass": "arm",
            "id": "StudyArm_000009",
            "text": "NPH insulin",
            "colors": ("#fffde7", "#665d00", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {
            "klass": "element",
            "id": "StudyElement_000018",
            "text": "Screening",
            "colors": ("#d2e4f3", "#153651", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {
            "klass": "element",
            "id": "StudyElement_000020",
            "text": "NPH insulin",
            "colors": ("#d2e4f3", "#153651", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {
            "klass": "element",
            "id": "StudyElement_000020",
            "text": "NPH insulin",
            "colors": ("#d2e4f3", "#153651", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {
            "klass": "element",
            "id": "StudyElement_000024",
            "text": "Follow-up",
            "colors": ("#d2e4f3", "#153651", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {
            "klass": "element",
            "id": "StudyElement_000020",
            "text": "NPH insulin",
            "colors": ("#d2e4f3", "#153651", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {},
    ],
    [
        {
            "klass": "arm",
            "id": "StudyArm_000011",
            "text": "Metformin is longer",
            "colors": ("#ffebee", "#66000f", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {
            "klass": "element",
            "id": "StudyElement_000018",
            "text": "Screening",
            "colors": ("#d2e4f3", "#153651", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {
            "klass": "element",
            "id": "StudyElement_000022",
            "text": "Metformin",
            "colors": ("#d2e4f3", "#153651", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {
            "klass": "element",
            "id": "StudyElement_000020",
            "text": "NPH insulin",
            "colors": ("#d2e4f3", "#153651", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {
            "klass": "element",
            "id": "StudyElement_000024",
            "text": "Follow-up",
            "colors": ("#d2e4f3", "#153651", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {
            "klass": "element",
            "id": "StudyElement_000022",
            "text": "Metformin",
            "colors": ("#d2e4f3", "#153651", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {},
    ],
    [
        {
            "klass": "arm",
            "id": "StudyArm_000045",
            "text": "Another arm",
            "colors": ("#f3e5f5", "#441c4a", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {},
        {
            "klass": "element",
            "id": "StudyElement_000020",
            "text": "NPH insulin",
            "colors": ("#d2e4f3", "#153651", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {
            "klass": "element",
            "id": "StudyElement_000020",
            "text": "NPH insulin",
            "colors": ("#d2e4f3", "#153651", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {
            "klass": "element",
            "id": "StudyElement_000020",
            "text": "NPH insulin",
            "colors": ("#d2e4f3", "#153651", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {},
        {},
    ],
    [
        {
            "klass": "arm",
            "id": "StudyArm_000048",
            "text": "More arms",
            "colors": ("#e8eaf6", "#1d2349", "#000"),
            "margin": 5,
            "paddings": (5, 5),
        },
        {},
        {},
        {},
        {},
        {},
        {},
    ],
]

VISIT_IDS = {
    "StudyVisit_000021",
    "StudyVisit_000022",
    "StudyVisit_000044",
    "StudyVisit_000031",
    "StudyVisit_000045",
}

TIMELINE = {
    "labels": [
        [
            {
                "id": "CTTerm_000171",
                "klass": "visit-type",
                "paddings": (0, 0),
                "text": "Screening",
                "width": 114,
                "x": 175,
                "y": 227,
                "height": 20,
                "lines": ((25, 16, "Screening"),),
            },
            {
                "id": "CTTerm_000176",
                "klass": "visit-type",
                "paddings": (0, 0),
                "text": "Treatment",
                "width": 270,
                "x": 299,
                "y": 227,
                "height": 20,
                "lines": ((102, 16, "Treatment"),),
            },
            {
                "id": "CTTerm_000161",
                "klass": "visit-type",
                "paddings": (0, 0),
                "text": "Follow-up",
                "width": 130,
                "x": 579,
                "y": 227,
                "height": 20,
                "lines": ((31, 16, "Follow-up"),),
            },
            {
                "id": "CTTerm_000164",
                "klass": "visit-type",
                "paddings": (0, 0),
                "text": "Post treatment activity",
                "width": 130,
                "x": 719,
                "y": 218,
                "height": 39,
                "lines": ((18, 16, "Post treatment"), (41, 35, "activity")),
            },
        ],
        [
            {
                "id": "StudyVisit_000021",
                "klass": "visit-timing",
                "paddings": (0, 0),
                "text": "Week -2",
                "x": 175,
                "y": 279,
                "width": 53,
                "height": 15,
                "lines": ((0, 16, "Week -2"),),
            },
            {
                "id": "StudyVisit_000022",
                "klass": "visit-timing",
                "paddings": (0, 0),
                "text": "Week 1",
                "x": 299,
                "y": 279,
                "width": 48,
                "height": 15,
                "lines": ((0, 16, "Week 1"),),
            },
            {
                "id": "StudyVisit_000044",
                "klass": "visit-timing",
                "paddings": (0, 0),
                "text": "Week 10",
                "x": 439,
                "y": 279,
                "width": 56,
                "height": 15,
                "lines": ((0, 16, "Week 10"),),
            },
            {
                "id": "StudyVisit_000031",
                "klass": "visit-timing",
                "paddings": (0, 0),
                "text": "Week 27",
                "x": 579,
                "y": 279,
                "width": 56,
                "height": 15,
                "lines": ((0, 16, "Week 27"),),
            },
            {
                "id": "StudyVisit_000045",
                "klass": "visit-timing",
                "paddings": (0, 0),
                "text": "Week 53",
                "x": 719,
                "y": 279,
                "width": 56,
                "height": 15,
                "lines": ((0, 16, "Week 53"),),
            },
        ],
    ],
    "arrows": [
        {"klass": "timeline-arrow", "x1": 175, "x2": 299, "y1": 262, "y2": 262},
        {"klass": "timeline-arrow", "x1": 299, "x2": 579, "y1": 262, "y2": 262},
        {"klass": "timeline-arrow", "x1": 579, "x2": 719, "y1": 262, "y2": 262},
        {"klass": "timeline-arrow", "x1": 719, "x2": 859, "y1": 262, "y2": 262},
        {"klass": "visit-arrow", "x1": 175, "x2": 175, "y1": 276, "y2": 264},
        {"klass": "visit-arrow", "x1": 299, "x2": 299, "y1": 276, "y2": 264},
        {"klass": "visit-arrow", "x1": 439, "x2": 439, "y1": 276, "y2": 264},
        {"klass": "visit-arrow", "x1": 579, "x2": 579, "y1": 276, "y2": 264},
        {"klass": "visit-arrow", "x1": 719, "x2": 719, "y1": 276, "y2": 264},
    ],
}

SVG_DOCUMENT = """
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="1009" height="299">
  <defs>
    <marker id="arrowhead1" viewBox="0 0 6 6" refX="6" refY="3" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 6 3 L 0 6 z" />
    </marker>
    <marker id="arrowhead2" viewBox="0 0 6 6" refX="3" refY="0" markerWidth="6" markerHeight="6" orient="0">
      <path d="M 0 6 L 3 0 L 6 6 z" />
    </marker>
    <marker id="arrowtail1" viewBox="0 0 6 6" refX="3" refY="3" markerWidth="6" markerHeight="6" orient="auto">
      <polyline points="3 0, 3 6" />
    </marker>
  </defs>
  <g id="StudyArm_000009" class="arm" transform="translate(5, 36)">
    <rect x="0" y="0" width="999" height="40" rx="5" ry="5" />
    <text>
      <tspan x="5" y="21">NPH insulin</tspan>
    </text>
  </g>
  <g id="StudyArm_000011" class="arm" transform="translate(5, 81)">
    <rect x="0" y="0" width="999" height="40" rx="5" ry="5" />
    <text>
      <tspan x="5" y="21">Metformin is longer</tspan>
    </text>
  </g>
  <g id="StudyArm_000045" class="arm" transform="translate(5, 126)">
    <rect x="0" y="0" width="999" height="40" rx="5" ry="5" />
    <text>
      <tspan x="5" y="21">Another arm</tspan>
    </text>
  </g>
  <g id="StudyArm_000048" class="arm" transform="translate(5, 171)">
    <rect x="0" y="0" width="999" height="30" rx="5" ry="5" />
    <text>
      <tspan x="5" y="21">More arms</tspan>
    </text>
  </g>
  <g id="StudyEpoch_000001" class="epoch" transform="translate(175, 5)">
    <rect x="0" y="0" width="114" height="201" rx="5" ry="5" />
    <text>
      <tspan x="25" y="19">Screening</tspan>
    </text>
  </g>
  <g id="StudyEpoch_000002" class="epoch" transform="translate(299, 5)">
    <rect x="0" y="0" width="130" height="201" rx="5" ry="5" />
    <text>
      <tspan x="32" y="19">Treatment</tspan>
    </text>
  </g>
  <g id="StudyEpoch_000042" class="epoch" transform="translate(439, 5)">
    <rect x="0" y="0" width="130" height="201" rx="5" ry="5" />
    <text>
      <tspan x="33" y="19">Extension</tspan>
    </text>
  </g>
  <g id="StudyEpoch_000003" class="epoch" transform="translate(579, 5)">
    <rect x="0" y="0" width="130" height="201" rx="5" ry="5" />
    <text>
      <tspan x="31" y="19">Follow-up</tspan>
    </text>
  </g>
  <g id="StudyEpoch_000034" class="epoch" transform="translate(719, 5)">
    <rect x="0" y="0" width="130" height="201" rx="5" ry="5" />
    <text>
      <tspan x="27" y="19">Elimination</tspan>
    </text>
  </g>
  <g id="StudyEpoch_000041" class="epoch" transform="translate(859, 5)">
    <rect x="0" y="0" width="140" height="201" rx="5" ry="5" />
    <text>
      <tspan x="18" y="19">Dose Escalation</tspan>
    </text>
  </g>
  <g id="StudyElement_000018" class="element" transform="translate(180, 41)">
    <rect x="0" y="0" width="104" height="75" rx="5" ry="5" />
    <text>
      <tspan x="5" y="21">Screening</tspan>
    </text>
  </g>
  <g id="StudyElement_000020" class="element" transform="translate(304, 41)">
    <rect x="0" y="0" width="120" height="30" rx="5" ry="5" />
    <text>
      <tspan x="5" y="21">NPH insulin</tspan>
    </text>
  </g>
  <g id="StudyElement_000020" class="element" transform="translate(444, 41)">
    <rect x="0" y="0" width="120" height="120" rx="5" ry="5" />
    <text>
      <tspan x="5" y="21">NPH insulin</tspan>
    </text>
  </g>
  <g id="StudyElement_000024" class="element" transform="translate(584, 41)">
    <rect x="0" y="0" width="120" height="75" rx="5" ry="5" />
    <text>
      <tspan x="5" y="21">Follow-up</tspan>
    </text>
  </g>
  <g id="StudyElement_000020" class="element" transform="translate(724, 41)">
    <rect x="0" y="0" width="120" height="30" rx="5" ry="5" />
    <text>
      <tspan x="5" y="21">NPH insulin</tspan>
    </text>
  </g>
  <g id="StudyElement_000022" class="element" transform="translate(304, 86)">
    <rect x="0" y="0" width="120" height="30" rx="5" ry="5" />
    <text>
      <tspan x="5" y="21">Metformin</tspan>
    </text>
  </g>
  <g id="StudyElement_000022" class="element" transform="translate(724, 86)">
    <rect x="0" y="0" width="120" height="30" rx="5" ry="5" />
    <text>
      <tspan x="5" y="21">Metformin</tspan>
    </text>
  </g>
  <g id="StudyElement_000020" class="element" transform="translate(304, 131)">
    <rect x="0" y="0" width="120" height="30" rx="5" ry="5" />
    <text>
      <tspan x="5" y="21">NPH insulin</tspan>
    </text>
  </g>
  <g id="StudyElement_000020" class="element" transform="translate(584, 131)">
    <rect x="0" y="0" width="120" height="30" rx="5" ry="5" />
    <text>
      <tspan x="5" y="21">NPH insulin</tspan>
    </text>
  </g>
  <g id="CTTerm_000171" class="visit-type" transform="translate(175, 227)">
    <text>
      <tspan x="25" y="16">Screening</tspan>
    </text>
  </g>
  <g id="CTTerm_000176" class="visit-type" transform="translate(299, 227)">
    <text>
      <tspan x="102" y="16">Treatment</tspan>
    </text>
  </g>
  <g id="CTTerm_000161" class="visit-type" transform="translate(579, 227)">
    <text>
      <tspan x="31" y="16">Follow-up</tspan>
    </text>
  </g>
  <g id="CTTerm_000164" class="visit-type" transform="translate(719, 218)">
    <text>
      <tspan x="18" y="16">Post treatment</tspan>
      <tspan x="41" y="35">activity</tspan>
    </text>
  </g>
  <g id="StudyVisit_000021" class="visit-timing" transform="translate(175, 279)">
    <text>
      <tspan x="0" y="16">Week -2</tspan>
    </text>
  </g>
  <g id="StudyVisit_000022" class="visit-timing" transform="translate(299, 279)">
    <text>
      <tspan x="0" y="16">Week 1</tspan>
    </text>
  </g>
  <g id="StudyVisit_000044" class="visit-timing" transform="translate(439, 279)">
    <text>
      <tspan x="0" y="16">Week 10</tspan>
    </text>
  </g>
  <g id="StudyVisit_000031" class="visit-timing" transform="translate(579, 279)">
    <text>
      <tspan x="0" y="16">Week 27</tspan>
    </text>
  </g>
  <g id="StudyVisit_000045" class="visit-timing" transform="translate(719, 279)">
    <text>
      <tspan x="0" y="16">Week 53</tspan>
    </text>
  </g>
  <line class="timeline-arrow" x1="175" x2="299" y1="262" y2="262" />
  <line class="timeline-arrow" x1="299" x2="579" y1="262" y2="262" />
  <line class="timeline-arrow" x1="579" x2="719" y1="262" y2="262" />
  <line class="timeline-arrow" x1="719" x2="859" y1="262" y2="262" />
  <line class="visit-arrow" x1="175" x2="175" y1="276" y2="264" />
  <line class="visit-arrow" x1="299" x2="299" y1="276" y2="264" />
  <line class="visit-arrow" x1="439" x2="439" y1="276" y2="264" />
  <line class="visit-arrow" x1="579" x2="579" y1="276" y2="264" />
  <line class="visit-arrow" x1="719" x2="719" y1="276" y2="264" />
  <style type="text/css">
    text {
      font-family: "Times New Roman";
      font-size: 12pt;
    }
    .arm rect {
      rx: 5px;
      ry: 5px;
      stroke-width: 2px;
    }
    .epoch rect {
      rx: 5px;
      ry: 5px;
      stroke-width: 2px;
    }
    .element rect {
      rx: 5px;
      ry: 5px;
      stroke-width: 1px;
    }
    .timeline-arrow {
      stroke: #AAA;
      stroke-width: 2px;
      marker-start: url(#arrowtail1);
      marker-end: url(#arrowhead1);
      stroke-dasharray: 6 2;
    }
    #arrowtail1 polyline {
      stroke: #AAA;
      stroke-width: 1px;
    }
    #arrowhead1 path {
      fill: #AAA;
    }
    #arrowhead2 path {
      fill: #000;
    }
    .visit-arrow {
      stroke: #000;
      stroke-width: 1px;
      marker-end: url(#arrowhead2);
    }
    #StudyArm_000009 rect {
      fill: #fffde7;
      stroke: #665d00;
    }
    #StudyArm_000009 text {
      fill: #000;
    }
    #StudyArm_000011 rect {
      fill: #ffebee;
      stroke: #66000f;
    }
    #StudyArm_000011 text {
      fill: #000;
    }
    #StudyArm_000045 rect {
      fill: #f3e5f5;
      stroke: #441c4a;
    }
    #StudyArm_000045 text {
      fill: #000;
    }
    #StudyArm_000048 rect {
      fill: #e8eaf6;
      stroke: #1d2349;
    }
    #StudyArm_000048 text {
      fill: #000;
    }
    #StudyEpoch_000001 rect {
      fill: #a5d6a7;
      stroke: #204621;
    }
    #StudyEpoch_000001 text {
      fill: #000;
    }
    #StudyEpoch_000002 rect {
      fill: #2e7d32;
      stroke: #1b4b1e;
    }
    #StudyEpoch_000002 text {
      fill: #fff;
    }
    #StudyEpoch_000042 rect {
      fill: #80deea;
      stroke: #0e4f58;
    }
    #StudyEpoch_000042 text {
      fill: #000;
    }
    #StudyEpoch_000003 rect {
      fill: #009688;
      stroke: #00665c;
    }
    #StudyEpoch_000003 text {
      fill: #fff;
    }
    #StudyEpoch_000034 rect {
      fill: #c5cae9;
      stroke: #1c224a;
    }
    #StudyEpoch_000034 text {
      fill: #000;
    }
    #StudyEpoch_000041 rect {
      fill: #80cbc4;
      stroke: #1e4844;
    }
    #StudyEpoch_000041 text {
      fill: #000;
    }
    #StudyElement_000018 rect {
      fill: #d2e4f3;
      stroke: #153651;
    }
    #StudyElement_000018 text {
      fill: #000;
    }
    #StudyElement_000020 rect {
      fill: #d2e4f3;
      stroke: #153651;
    }
    #StudyElement_000020 text {
      fill: #000;
    }
    #StudyElement_000024 rect {
      fill: #d2e4f3;
      stroke: #153651;
    }
    #StudyElement_000024 text {
      fill: #000;
    }
    #StudyElement_000022 rect {
      fill: #d2e4f3;
      stroke: #153651;
    }
    #StudyElement_000022 text {
      fill: #000;
    }
  </style>
</svg>
""".strip()


class MockStudyDesignFigureService(StudyDesignFigureService):
    @staticmethod
    def _get_study_arms(*_args, **_kwargs):
        return STUDY_ARMS

    @staticmethod
    def _get_study_epochs(*_args, **_kwargs):
        return STUDY_EPOCHS

    @staticmethod
    def _get_study_elements(*_args, **_kwargs):
        return STUDY_ELEMENTS

    @staticmethod
    def _get_study_design_cells(*_args, **_kwargs):
        return STUDY_DESIGN_CELLS

    @staticmethod
    def _get_study_visits(*_args, **_kwargs):
        return STUDY_VISITS


def test_mk_data_matrix():
    table = MockStudyDesignFigureService()._mk_data_matrix(
        STUDY_ARMS, STUDY_EPOCHS, STUDY_ELEMENTS, STUDY_DESIGN_CELLS
    )
    assert table == MATRIX


def test_select_first_visits():
    visits = MockStudyDesignFigureService()._select_first_visits(
        STUDY_VISITS, STUDY_EPOCHS
    )
    visit_ids = {visit["id"] for visit in visits if visit}
    assert visit_ids == VISIT_IDS


def test_mk_timeline():
    # pylint: disable=unused-argument
    def draw_svg(table, timeline, doc_width, doc_height):
        # pylint: disable=unused-variable
        __tracebackhide__ = True
        assert timeline == TIMELINE

    service = MockStudyDesignFigureService()
    service.draw_svg = draw_svg
    service.get_svg_document("")


# pylint: disable=unsupported-membership-test
def test_get_svg_document():
    service = MockStudyDesignFigureService()
    doc: str = service.get_svg_document("")

    assert "</svg>" in doc, "no </svg> tag in document, not an SVG?"
    assert "</defs>" in doc, "no </defs> tag in document, missing defs?"
    assert "</style>" in doc, "no </style> tag in document, missing styles?"

    assert 'class="arm"' in doc, 'class="arm" found, missing arms?'
    assert 'class="epoch"' in doc, 'class="epoch" found, missing epochs?'
    assert (
        'class="element"' in doc
    ), 'class="element" found, missing study design cells?'

    for id_ in STUDY_ARMS.keys():
        assert f'id="{id_}"' in doc, f'arm id="{id_}" not found in document'
    for id_ in STUDY_EPOCHS.keys():
        assert f'id="{id_}"' in doc, f'epoch id="{id_}" not found in document'
    for id_ in STUDY_ELEMENTS.keys():
        assert f'id="{id_}"' in doc, f'element id="{id_}" not found in document'

    assert (
        'class="visit-type"' in doc
    ), 'class="visit-type" found, missing visit type labels?'
    assert (
        'class="visit-timing"' in doc
    ), 'class="visit-timing" found, missing visit milestones?'

    assert (
        'class="timeline-arrow"' in doc
    ), 'class="timeline-arrow" not found, missing timeline arrows?'
    assert (
        'class="timeline-arrow"' in doc
    ), 'class="visit-arrow" not found, missing visit arrows?'
    assert "markerWidth" in doc, '"markerWidth" found, missing arrowhead markers?'

    assert doc == SVG_DOCUMENT
