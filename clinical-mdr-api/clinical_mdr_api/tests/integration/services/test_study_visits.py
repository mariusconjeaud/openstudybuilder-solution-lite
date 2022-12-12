import unittest

from neomodel import db

from clinical_mdr_api.domain.study_selection.study_epoch import StudyEpochVO, TimelineAR
from clinical_mdr_api.domain.study_selection.study_visit import StudyVisitVO
from clinical_mdr_api.exceptions import ValidationException
from clinical_mdr_api.models import StudyVisit
from clinical_mdr_api.models.study_epoch import StudyEpochEditInput
from clinical_mdr_api.models.study_visit import (
    StudyVisitCreateInput,
    StudyVisitEditInput,
)
from clinical_mdr_api.services.study_epoch import StudyEpochService
from clinical_mdr_api.services.study_visit import StudyVisitService
from clinical_mdr_api.tests.integration.utils.api import inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_CT_CATALOGUE_CYPHER,
    STARTUP_STUDY_LIST_CYPHER,
)
from clinical_mdr_api.tests.integration.utils.method_library import (
    create_library_data,
    create_study_epoch,
    create_study_visit_codelists,
    create_visit_with_update,
    generate_study_root,
    get_unit_uid_by_name,
    preview_visit_with_update,
    update_visit_with_update,
)


class TestStudyVisitManagement(unittest.TestCase):
    TPR_LABEL = "ParameterName"

    def setUp(self):
        inject_and_clear_db("studiesvisitstest")
        db.cypher_query(STARTUP_STUDY_LIST_CYPHER)
        db.cypher_query(STARTUP_CT_CATALOGUE_CYPHER)

        create_library_data()

        self.study = generate_study_root()
        create_study_visit_codelists()

        self.epoch1 = create_study_epoch("EpochSubType_0001")
        self.epoch2 = create_study_epoch("EpochSubType_0002")
        self.epoch3 = create_study_epoch("EpochSubType_0003")
        self.DAYUID = get_unit_uid_by_name("day")

    def test__list__visits_studies(self):
        inputs = dict(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=0,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=True,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        preview = preview_visit_with_update(self.study.uid, **inputs)
        print("PREVIEW", preview)
        self.assertEqual(preview.order, 1)
        self.assertEqual(preview.visit_number, 1)
        self.assertEqual(preview.unique_visit_number, 100)

        create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=0,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=True,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0003",
            time_reference_uid="VisitSubType_0001",
            time_value=12,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0003",
            time_reference_uid="VisitSubType_0001",
            time_value=10,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        inputs = dict(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0004",
            time_reference_uid="VisitSubType_0001",
            time_value=20,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        preview = preview_visit_with_update(self.study.uid, **inputs)
        print("PREVIEW", preview)
        self.assertEqual(preview.order, 4)
        self.assertEqual(preview.visit_number, 4)
        self.assertEqual(preview.unique_visit_number, 400)

        v3 = create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0004",
            time_reference_uid="VisitSubType_0001",
            time_value=20,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        self.assertEqual(v3.unique_visit_number, preview.unique_visit_number)
        v4 = create_visit_with_update(
            study_epoch_uid=self.epoch2.uid,
            visit_type_uid="VisitType_0002",
            time_reference_uid="VisitSubType_0001",
            time_value=30,
            time_unit_uid=self.DAYUID,
            visit_sublabel_codelist_uid="VisitSubLabel_0001",
            visit_sublabel_reference=None,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="ANCHOR_VISIT_IN_GROUP_OF_SUBV",
        )
        v5 = create_visit_with_update(
            study_epoch_uid=self.epoch2.uid,
            visit_type_uid="VisitType_0003",
            time_reference_uid="VisitSubType_0002",
            time_value=31,
            time_unit_uid=self.DAYUID,
            visit_sublabel_codelist_uid="VisitSubLabel_0002",
            visit_sublabel_reference=v4.uid,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV",
        )
        visit_service: StudyVisitService = StudyVisitService()
        visits = visit_service.get_all_visits(self.study.uid)
        self.assertEqual(len(visits.items), 6)

        v3new: StudyVisit = visit_service.find_by_uid(v3.uid)
        self.assertEqual(v3new.order, 4)
        self.assertEqual(v3new.visit_number, 4)
        self.assertEqual(v3new.unique_visit_number, 400)

        self.assertEqual(v3new.study_day_number, 21)
        self.assertEqual(v3new.min_visit_window_value, -1)
        self.assertEqual(v3new.max_visit_window_value, 1)

        v5new: StudyVisit = visit_service.find_by_uid(v4.uid)
        self.assertEqual(v5new.order, 5)
        self.assertEqual(v5new.visit_number, 5)
        print("V%sub", v5new)
        self.assertEqual(v5new.unique_visit_number, 500)

        v6new: StudyVisit = visit_service.find_by_uid(v5.uid)
        self.assertEqual(v6new.order, 5)
        self.assertEqual(v5new.visit_number, 5)
        print("V%sub", v6new)
        self.assertEqual(v6new.unique_visit_number, 510)

        references = visit_service.get_all_references(self.study.uid)
        self.assertEqual(len(references), 2)
        visit: StudyVisit = references[0]
        self.assertEqual(visit.visit_type_name, "BASELINE")
        visit: StudyVisit = references[1]
        self.assertEqual(visit.visit_type_name, "BASELINE2")

        inputs = dict(
            study_epoch_uid=self.epoch2.uid,
            visit_type_uid="VisitType_0003",
            time_reference_uid="VisitSubType_0002",
            time_value=40,
            time_unit_uid=self.DAYUID,
            visit_sublabel_codelist_uid="VisitSubLabel_0003",
            visit_sublabel_reference=v4.uid,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV",
        )
        preview = preview_visit_with_update(self.study.uid, **inputs)
        print("PREVIEW", preview)
        self.assertEqual(preview.unique_visit_number, 520)

        epoch_service: StudyEpochService = StudyEpochService()
        epochs = epoch_service.get_all_epochs(self.study.uid).items
        self.assertEqual(len(epochs), 3)
        epoch1 = epochs[0]
        epoch2 = epochs[1]
        study_epochs = epoch_service.repo.find_all_epochs_by_study(self.study.uid)

        epoch = epoch_service.find_by_uid(epoch1.uid)
        start_rule = "New start rule"
        end_rule = "New end rule"
        edit_input = StudyEpochEditInput(
            study_uid=epoch.study_uid,
            start_rule=start_rule,
            end_rule=end_rule,
            change_description="rules change",
        )
        epoch_service.edit(
            study_epoch_uid=epoch.uid,
            study_epoch_input=edit_input,
        )

        visit_repo = epoch_service._repos.study_visit_repository
        study_visits = visit_repo.find_all_visits_by_study_uid(self.study.uid)
        timeline = TimelineAR(self.study.uid, _visits=study_visits)
        epochs = timeline.collect_visits_to_epochs(study_epochs)
        visit_vo: StudyVisitVO
        epoch_vo: StudyEpochVO
        for visit_vo in timeline.ordered_study_visits:
            print(
                "VIS",
                visit_vo.uid,
                visit_vo.study_day_number,
                visit_vo.get_unified_window(),
            )
            self.assertEqual(
                visit_vo.get_unified_window(),
                (visit_vo.study_day_number - 1, visit_vo.study_day_number + 1),
            )

        for v in study_visits:
            if v.uid == v3.uid:
                visit3_vo: StudyVisitVO = v
                self.assertEqual(visit3_vo.study_day_number, 21)
                self.assertEqual(visit3_vo.study_week_number, 3)
        for epoch_vo in study_epochs:
            print(
                "EPOCH", epoch_vo.uid, epoch_vo.get_start_day(), epoch_vo.get_end_day()
            )
        print("EPOCH 1", epoch1)
        print("EPOCH 2", epoch2)
        self.assertEqual(epoch1.start_day, 1)
        self.assertEqual(epoch1.end_day, 31)
        self.assertEqual(epoch2.start_day, epoch1.end_day)
        self.assertEqual(epoch2.end_day, 62)

        v3update = update_visit_with_update(
            v3new.uid,
            uid=v3new.uid,
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0004",
            time_reference_uid="VisitSubType_0001",
            time_value=25,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        self.assertEqual(v3update.study_day_number, 26)

    def test__create__props_are_correctly_saved(self):
        visit_service = StudyVisitService()

        input_values = dict(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=0,
            time_unit_uid=self.DAYUID,
            visit_contact_mode_uid="VisitContactMode_0002",
            max_visit_window_value=10,
            min_visit_window_value=0,
            show_visit=True,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
            epoch_allocation_uid="EpochAllocation_0002",
        )
        visit = create_visit_with_update(**input_values)
        visit_after_create = visit_service.find_by_uid(uid=visit.uid)
        self.assertEqual(
            visit_after_create.visit_contact_mode_uid,
            input_values["visit_contact_mode_uid"],
        )
        self.assertEqual(
            visit_after_create.max_visit_window_value,
            input_values["max_visit_window_value"],
        )
        self.assertEqual(
            visit_after_create.min_visit_window_value,
            input_values["min_visit_window_value"],
        )
        self.assertEqual(
            visit_after_create.time_unit_uid, input_values["time_unit_uid"]
        )
        self.assertEqual(visit_after_create.time_value, input_values["time_value"])
        self.assertEqual(visit_after_create.show_visit, input_values["show_visit"])
        self.assertEqual(
            visit_after_create.time_reference_uid, input_values["time_reference_uid"]
        )
        self.assertEqual(
            visit_after_create.visit_type_uid, input_values["visit_type_uid"]
        )
        self.assertEqual(
            visit_after_create.epoch_allocation_uid,
            input_values["epoch_allocation_uid"],
        )

    def test__edit_visit_successfully_handled(self):
        visit_service = StudyVisitService()
        visit = create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=0,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=True,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
            epoch_allocation_uid="EpochAllocation_0001",
        )

        edit_input = dict(
            uid=visit.uid,
            study_epoch_uid=visit.study_epoch_uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=7,
            time_unit_uid=self.DAYUID,
            visit_contact_mode_uid="VisitContactMode_0002",
            max_visit_window_value=10,
            min_visit_window_value=0,
            visit_window_unit_uid=visit.visit_window_unit_uid,
            show_visit=True,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
            epoch_allocation_uid="EpochAllocation_0002",
        )
        visit_service.edit(
            study_uid=visit.study_uid,
            study_visit_uid=visit.uid,
            study_visit_input=StudyVisitEditInput(**edit_input),
        )
        visit_after_update = visit_service.find_by_uid(uid=visit.uid)
        self.assertEqual(
            visit_after_update.visit_contact_mode_uid,
            edit_input["visit_contact_mode_uid"],
        )
        self.assertEqual(
            visit_after_update.max_visit_window_value,
            edit_input["max_visit_window_value"],
        )
        self.assertEqual(
            visit_after_update.min_visit_window_value,
            edit_input["min_visit_window_value"],
        )
        self.assertEqual(visit_after_update.time_unit_uid, edit_input["time_unit_uid"])
        self.assertEqual(visit_after_update.time_value, edit_input["time_value"])
        self.assertEqual(visit_after_update.show_visit, edit_input["show_visit"])
        self.assertEqual(
            visit_after_update.time_reference_uid, edit_input["time_reference_uid"]
        )
        self.assertEqual(
            visit_after_update.visit_type_uid, edit_input["visit_type_uid"]
        )
        self.assertEqual(
            visit_after_update.epoch_allocation_uid, edit_input["epoch_allocation_uid"]
        )

    def test__version_visits(self):
        visit_service = StudyVisitService()
        visit = create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=0,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=True,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
            epoch_allocation_uid="EpochAllocation_0001",
        )

        edit_input = dict(
            uid=visit.uid,
            study_epoch_uid=visit.study_epoch_uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=7,
            time_unit_uid=self.DAYUID,
            visit_contact_mode_uid="VisitContactMode_0002",
            max_visit_window_value=10,
            min_visit_window_value=0,
            visit_window_unit_uid=visit.visit_window_unit_uid,
            show_visit=True,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
            epoch_allocation_uid="EpochAllocation_0002",
        )
        visit_service.edit(
            study_uid=visit.study_uid,
            study_visit_uid=visit.uid,
            study_visit_input=StudyVisitEditInput(**edit_input),
        )
        visit_after_update = visit_service.find_by_uid(uid=visit.uid)
        self.assertEqual(
            visit_after_update.visit_contact_mode_uid,
            edit_input["visit_contact_mode_uid"],
        )
        self.assertEqual(
            visit_after_update.max_visit_window_value,
            edit_input["max_visit_window_value"],
        )
        self.assertEqual(
            visit_after_update.min_visit_window_value,
            edit_input["min_visit_window_value"],
        )
        self.assertEqual(visit_after_update.time_unit_uid, edit_input["time_unit_uid"])
        self.assertEqual(visit_after_update.time_value, edit_input["time_value"])
        self.assertEqual(visit_after_update.show_visit, edit_input["show_visit"])
        self.assertEqual(
            visit_after_update.time_reference_uid, edit_input["time_reference_uid"]
        )
        self.assertEqual(
            visit_after_update.visit_type_uid, edit_input["visit_type_uid"]
        )
        self.assertEqual(
            visit_after_update.epoch_allocation_uid, edit_input["epoch_allocation_uid"]
        )

        visit_service.audit_trail(
            visit_uid=visit.uid,
            study_uid=visit.study_uid,
        )

        time_value = 30
        create_visit_with_update(
            study_epoch_uid=self.epoch2.uid,
            visit_type_uid="VisitType_0002",
            time_reference_uid="VisitSubType_0001",
            time_value=time_value,
            time_unit_uid=self.DAYUID,
            visit_sublabel_codelist_uid="VisitSubLabel_0001",
            visit_sublabel_reference=None,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="ANCHOR_VISIT_IN_GROUP_OF_SUBV",
        )
        visits_versions = visit_service.audit_trail_all_visits(
            study_uid=visit.study_uid,
        )

        current_visit = visits_versions[0]
        previous_visit = visits_versions[1]
        current_visit_2 = visits_versions[2]
        self.assertEqual(
            current_visit.visit_contact_mode_uid, edit_input["visit_contact_mode_uid"]
        )
        self.assertEqual(
            current_visit.max_visit_window_value, edit_input["max_visit_window_value"]
        )
        self.assertEqual(
            current_visit.min_visit_window_value, edit_input["min_visit_window_value"]
        )
        self.assertEqual(current_visit.time_unit_uid, edit_input["time_unit_uid"])
        self.assertEqual(current_visit.time_value, edit_input["time_value"])
        self.assertEqual(current_visit.show_visit, edit_input["show_visit"])
        self.assertEqual(
            current_visit.time_reference_uid, edit_input["time_reference_uid"]
        )
        self.assertEqual(current_visit.visit_type_uid, edit_input["visit_type_uid"])
        self.assertEqual(
            current_visit.epoch_allocation_uid, edit_input["epoch_allocation_uid"]
        )
        self.assertEqual(current_visit.uid, previous_visit.uid)
        self.assertGreater(current_visit.start_date, previous_visit.start_date)
        self.assertEqual(previous_visit.changes, {})
        self.assertEqual(current_visit_2.changes, {})

    def test__create_subvisits_uvn__reordered_successfully(self):
        visit_service = StudyVisitService()
        create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=0,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=True,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        time_value = 30
        first_visit_in_seq_of_subvisits = create_visit_with_update(
            study_epoch_uid=self.epoch2.uid,
            visit_type_uid="VisitType_0002",
            time_reference_uid="VisitSubType_0001",
            time_value=time_value,
            time_unit_uid=self.DAYUID,
            visit_sublabel_codelist_uid="VisitSubLabel_0001",
            visit_sublabel_reference=None,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="ANCHOR_VISIT_IN_GROUP_OF_SUBV",
        )
        sub_visit_uvn = 200
        # we add so many subvists as there is a logic of
        # recalculating subvists unique-visit-numbers when we exceed allowed limits
        for i in range(1, 21):
            create_visit_with_update(
                study_epoch_uid=self.epoch2.uid,
                visit_type_uid="VisitType_0003",
                time_reference_uid="VisitSubType_0005",
                time_value=time_value + i,
                time_unit_uid=self.DAYUID,
                visit_sublabel_codelist_uid="VisitSubLabel_0002",
                visit_sublabel_reference=first_visit_in_seq_of_subvisits.uid,
                is_global_anchor_visit=False,
                visit_class="SINGLE_VISIT",
                visit_subclass="ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV",
            )
            # check unique visit numbers before recalculation
            if i == 9:
                all_visits = visit_service.get_all_visits(
                    study_uid=self.study.uid
                ).items
                for sub_idx, sub_visit in enumerate(all_visits[1:]):
                    if (
                        sub_visit.visit_subclass
                        == "ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV"
                    ):
                        self.assertEqual(
                            sub_visit.study_day_number - 1,
                            time_value + time_value + sub_idx,
                        )
                    self.assertEqual(
                        sub_visit.unique_visit_number, sub_visit_uvn + sub_idx * 10
                    )
            # check unique visit numbers after first recalculation
            if i == 10:
                all_visits = visit_service.get_all_visits(
                    study_uid=self.study.uid
                ).items
                for sub_idx, sub_visit in enumerate(all_visits[1:]):
                    if (
                        sub_visit.visit_subclass
                        == "ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV"
                    ):
                        self.assertEqual(
                            sub_visit.study_day_number - 1,
                            time_value + time_value + sub_idx,
                        )
                    self.assertEqual(
                        sub_visit.unique_visit_number, sub_visit_uvn + sub_idx * 5
                    )
            # check unique visit numbers after second recalculation
            if i == 20:
                all_visits = visit_service.get_all_visits(
                    study_uid=self.study.uid
                ).items
                for sub_idx, sub_visit in enumerate(all_visits[1:]):
                    if (
                        sub_visit.visit_subclass
                        == "ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV"
                    ):
                        self.assertEqual(
                            sub_visit.study_day_number - 1,
                            time_value + time_value + sub_idx,
                        )
                    self.assertEqual(
                        sub_visit.unique_visit_number, sub_visit_uvn + sub_idx * 1
                    )
        create_visit_with_update(
            study_epoch_uid=self.epoch2.uid,
            visit_type_uid="VisitType_0003",
            time_reference_uid="VisitSubType_0005",
            time_value=-1,
            time_unit_uid=self.DAYUID,
            visit_sublabel_codelist_uid="VisitSubLabel_0002",
            visit_sublabel_reference=first_visit_in_seq_of_subvisits.uid,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV",
        )

        all_visits = visit_service.get_all_visits(study_uid=self.study.uid).items

        all_visits = [visit for visit in all_visits if visit.visit_number == 2]

        self.assertEqual(all_visits[0].unique_visit_number, sub_visit_uvn)
        self.assertEqual(all_visits[0].study_day_number - 1, time_value - 1)
        self.assertEqual(all_visits[1].unique_visit_number, sub_visit_uvn + 1)
        self.assertEqual(all_visits[1].study_day_number - 1, time_value)

    def test__get_global_anchor_visit(self):
        visit_service = StudyVisitService()

        global_anchor_visit = visit_service.get_global_anchor_visit(
            study_uid=self.study.uid
        )
        self.assertIsNone(global_anchor_visit)

        vis = create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=0,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=True,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        global_anchor_visit = visit_service.get_global_anchor_visit(
            study_uid=self.study.uid
        )
        self.assertEqual(global_anchor_visit.uid, vis.uid)
        self.assertEqual(global_anchor_visit.visit_name, vis.visit_name)
        self.assertEqual(global_anchor_visit.visit_type_name, vis.visit_type_name)

    def test__get_anchor_visits_in_a_group_of_subvisits(self):
        visit_service = StudyVisitService()

        anchor_visits = visit_service.get_anchor_visits_in_a_group_of_subvisits(
            study_uid=self.study.uid
        )
        self.assertEqual(anchor_visits, [])

        create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=0,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=True,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        anchor_visit = create_visit_with_update(
            study_epoch_uid=self.epoch2.uid,
            visit_type_uid="VisitType_0002",
            time_reference_uid="VisitSubType_0001",
            time_value=30,
            time_unit_uid=self.DAYUID,
            visit_sublabel_codelist_uid="VisitSubLabel_0001",
            visit_sublabel_reference=None,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="ANCHOR_VISIT_IN_GROUP_OF_SUBV",
        )
        anchor_visits = visit_service.get_anchor_visits_in_a_group_of_subvisits(
            study_uid=self.study.uid
        )
        self.assertEqual(len(anchor_visits), 1)
        self.assertEqual(anchor_visit.uid, anchor_visits[0].uid)
        self.assertEqual(anchor_visit.visit_name, anchor_visits[0].visit_name)
        self.assertEqual(anchor_visit.visit_type_name, anchor_visits[0].visit_type_name)

    def test__epochs_durations_are_calculated_properly_when_having_empty_epoch(self):

        epoch_service = StudyEpochService()

        create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=0,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        create_visit_with_update(
            study_epoch_uid=self.epoch3.uid,
            visit_type_uid="VisitType_0003",
            time_reference_uid="VisitSubType_0001",
            time_value=10,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        create_visit_with_update(
            study_epoch_uid=self.epoch3.uid,
            visit_type_uid="VisitType_0003",
            time_reference_uid="VisitSubType_0001",
            time_value=30,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )

        study_epochs = epoch_service.get_all_epochs(self.study.uid).items
        self.assertEqual(len(study_epochs), 3)
        self.assertEqual(study_epochs[0].start_day, 1)
        self.assertEqual(study_epochs[0].duration, 0)
        self.assertEqual(study_epochs[0].end_day, 1)
        self.assertEqual(study_epochs[1].start_day, 1)
        self.assertEqual(study_epochs[1].duration, 10)
        self.assertEqual(study_epochs[1].end_day, 11)
        self.assertEqual(study_epochs[2].start_day, 11)
        self.assertEqual(study_epochs[2].duration, 20)
        self.assertEqual(study_epochs[2].end_day, 31)

    def test__epochs_durations_are_calculated_properly_when_having_last_epoch_with_one_visit(
        self,
    ):

        epoch_service = StudyEpochService()

        create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=0,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0003",
            time_reference_uid="VisitSubType_0001",
            time_value=10,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        create_visit_with_update(
            study_epoch_uid=self.epoch2.uid,
            visit_type_uid="VisitType_0003",
            time_reference_uid="VisitSubType_0001",
            time_value=30,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        create_visit_with_update(
            study_epoch_uid=self.epoch2.uid,
            visit_type_uid="VisitType_0003",
            time_reference_uid="VisitSubType_0001",
            time_value=40,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        create_visit_with_update(
            study_epoch_uid=self.epoch3.uid,
            visit_type_uid="VisitType_0003",
            time_reference_uid="VisitSubType_0001",
            time_value=50,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        study_epochs = epoch_service.get_all_epochs(self.study.uid).items
        self.assertEqual(len(study_epochs), 3)
        self.assertEqual(study_epochs[0].start_day, 1)
        self.assertEqual(study_epochs[0].duration, 30)
        self.assertEqual(study_epochs[0].end_day, 31)
        self.assertEqual(study_epochs[1].start_day, 31)
        self.assertEqual(study_epochs[1].duration, 20)
        self.assertEqual(study_epochs[1].end_day, 51)
        self.assertEqual(study_epochs[2].start_day, 51)
        self.assertEqual(study_epochs[2].duration, 7)
        self.assertEqual(study_epochs[2].end_day, 58)

    def test__create_visit_with_duplicated_timing__error_raised(self):
        create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=0,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=True,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        with self.assertRaises(ValidationException):
            create_visit_with_update(
                study_epoch_uid=self.epoch1.uid,
                visit_type_uid="VisitType_0001",
                time_reference_uid="VisitSubType_0001",
                time_value=0,
                time_unit_uid=self.DAYUID,
                is_global_anchor_visit=True,
                visit_class="SINGLE_VISIT",
                visit_subclass="SINGLE_VISIT",
            )

    def test__create_unscheduled_visit_without_time_data__no_error_is_raised(self):

        visit_service: StudyVisitService = StudyVisitService()
        create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=0,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=True,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0002",
            time_reference_uid="VisitSubType_0001",
            time_value=10,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        non_visit_input = {
            "study_epoch_uid": self.epoch1.uid,
            "consecutive_visit_group": "",
            "show_visit": True,
            "description": "description",
            "start_rule": "start_rule",
            "end_rule": "end_rule",
            "note": "note",
            "visit_contact_mode_uid": "VisitContactMode_0001",
            "visit_type_uid": "VisitType_0003",
            "is_global_anchor_visit": False,
            "visit_class": "NON_VISIT",
        }
        visit_input = StudyVisitCreateInput(**non_visit_input)
        visit_service.create(study_uid=self.study.uid, study_visit_input=visit_input)

        all_visits = visit_service.get_all_visits(study_uid=self.study.uid).items

        self.assertEqual(len(all_visits), 3)
        self.assertEqual(all_visits[0].time_value, 0)
        self.assertEqual(all_visits[1].time_value, 10)
        self.assertEqual(all_visits[2].time_value, None)
        self.assertEqual(all_visits[2].time_reference_uid, None)
        self.assertEqual(all_visits[2].time_reference_name, None)
        self.assertEqual(all_visits[2].visit_number, 29500)
        self.assertEqual(all_visits[2].min_visit_window_value, -9999)
        self.assertEqual(all_visits[2].max_visit_window_value, 9999)

    def test__create_special_visit(self):

        visit_service: StudyVisitService = StudyVisitService()
        create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0001",
            time_reference_uid="VisitSubType_0001",
            time_value=0,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=True,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        special_visit_anchor = create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0002",
            time_reference_uid="VisitSubType_0001",
            time_value=10,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        create_visit_with_update(
            study_epoch_uid=self.epoch1.uid,
            visit_type_uid="VisitType_0003",
            time_reference_uid="VisitSubType_0001",
            time_value=15,
            time_unit_uid=self.DAYUID,
            is_global_anchor_visit=False,
            visit_class="SINGLE_VISIT",
            visit_subclass="SINGLE_VISIT",
        )
        special_visit_input = {
            "study_epoch_uid": self.epoch1.uid,
            "consecutive_visit_group": "",
            "show_visit": True,
            "description": "description",
            "start_rule": "start_rule",
            "end_rule": "end_rule",
            "note": "note",
            "visit_contact_mode_uid": "VisitContactMode_0001",
            "visit_type_uid": "VisitType_0003",
            "is_global_anchor_visit": False,
            "visit_class": "SPECIAL_VISIT",
            "visit_sublabel_reference": special_visit_anchor.uid,
        }
        visit_input = StudyVisitCreateInput(**special_visit_input)
        visit_service.create(study_uid=self.study.uid, study_visit_input=visit_input)

        all_visits = visit_service.get_all_visits(study_uid=self.study.uid).items

        self.assertEqual(len(all_visits), 4)
        self.assertEqual(all_visits[0].time_value, 0)
        self.assertEqual(all_visits[1].time_value, 10)
        self.assertEqual(all_visits[2].time_value, None)
        self.assertEqual(all_visits[2].time_reference_uid, None)
        self.assertEqual(all_visits[2].time_reference_name, None)
        self.assertEqual(all_visits[2].visit_number, special_visit_anchor.visit_number)
        self.assertEqual(
            all_visits[2].visit_short_name, special_visit_anchor.visit_short_name + "A"
        )
        self.assertEqual(all_visits[3].time_value, 15)

        with self.assertRaises(ValidationException):
            visit_service.create(
                study_uid=self.study.uid, study_visit_input=visit_input
            )
