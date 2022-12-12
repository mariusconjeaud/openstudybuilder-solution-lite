import sys
import unittest
from typing import Dict

from neomodel import db  # type: ignore

from clinical_mdr_api.domain.study_definition_aggregate.root import StudyDefinitionAR
from clinical_mdr_api.domain_repositories.clinical_programme.clinical_programme_repository import (
    ClinicalProgrammeRepository,
)
from clinical_mdr_api.domain_repositories.project.project_repository import (
    ProjectRepository,
)
from clinical_mdr_api.domain_repositories.study_definition.study_definition_repository_impl import (
    StudyDefinitionRepositoryImpl,
)
from clinical_mdr_api.tests.integration.domain_repositories._utils import (
    wipe_study_definition_repository,  # type: ignore
)
from clinical_mdr_api.tests.integration.domain_repositories._utils import (
    current_function_name,
    wipe_clinical_programme_repository,
    wipe_project_repository,
)
from clinical_mdr_api.tests.integration.utils.api import inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_PARAMETERS_CYPHER,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils
from clinical_mdr_api.tests.unit.domain.clinical_programme_aggregate.test_clinical_programme import (
    create_random_clinical_programme,
)
from clinical_mdr_api.tests.unit.domain.project_aggregate.test_project import (
    create_random_project,
)
from clinical_mdr_api.tests.unit.domain.study_definition_aggregate.test_root import (
    create_random_study,
    make_random_study_metadata_edit,
)
from clinical_mdr_api.tests.unit.domain.utils import random_str


class TestStudyDefinitionRepository(unittest.TestCase):
    TEST_DB_NAME = "studydeftest"

    @classmethod
    def setUpClass(cls) -> None:
        inject_and_clear_db(cls.TEST_DB_NAME)
        db.cypher_query(STARTUP_PARAMETERS_CYPHER)

        wipe_study_definition_repository()
        wipe_project_repository()
        wipe_clinical_programme_repository()

        clinical_programme_repo = ClinicalProgrammeRepository()
        cls.created_clinical_programme = create_random_clinical_programme(
            clinical_programme_repo.generate_uid
        )
        clinical_programme_repo.save(cls.created_clinical_programme)

        project_repo = ProjectRepository()
        cls.created_project = create_random_project(
            clinical_programme_uid=cls.created_clinical_programme.uid,
            generate_uid_callback=project_repo.generate_uid,
        )
        project_repo.save(cls.created_project)

        cls.project_to_amend = create_random_project(
            clinical_programme_uid=cls.created_clinical_programme.uid,
            generate_uid_callback=project_repo.generate_uid,
        )
        project_repo.save(cls.project_to_amend)

        TestUtils.create_library()
        TestUtils.create_library(name="UCUM", is_editable=True)
        TestUtils.create_ct_catalogue()
        codelist = TestUtils.create_ct_codelist()
        TestUtils.create_study_ct_data_map(codelist_uid=codelist.codelist_uid)
        TestUtils.create_study_fields_configuration()

    def test__find_by_uid__non_existing_uid__returns_none(self):
        with db.transaction:
            # given
            non_existing_uid = f"this-uid-for-sure-does-not-exists-especially-after-adding-this-{random_str()}"
            repository = StudyDefinitionRepositoryImpl(f"{current_function_name()}")

            # when
            result = repository.find_by_uid(non_existing_uid)
            repository.close()

            # then
            self.assertIsNone(result)

    def test__create__exists(self):
        with db.transaction:
            # given
            repository1 = StudyDefinitionRepositoryImpl(current_function_name())
            created_study = create_random_study(
                generate_uid_callback=repository1.generate_uid,
                new_id_metadata_fixed_values={
                    "project_number": self.created_project.project_number
                },
                is_study_after_create=True,
            )
            # when
            repository1.save(created_study)
            repository1.close()

        # then
        with db.transaction:
            repository2 = StudyDefinitionRepositoryImpl(current_function_name())
            retrieved_study = repository2.find_by_uid(created_study.uid)
            repository2.close()
        print("CRE", created_study)
        print("RET", retrieved_study)
        self.assertEqual(retrieved_study, created_study)

    def test__save__locked__locked(self):
        def can_lock(_: StudyDefinitionAR) -> bool:
            return _.current_metadata.id_metadata.study_id is not None

        # given
        with db.transaction:
            repository1 = StudyDefinitionRepositoryImpl(current_function_name())
            created_study = create_random_study(
                condition=can_lock,
                generate_uid_callback=repository1.generate_uid,
                new_id_metadata_fixed_values={
                    "project_number": self.created_project.project_number
                },
            )
            repository1.save(created_study)
            repository1.close()

        # when
        with db.transaction:
            repository2 = StudyDefinitionRepositoryImpl(current_function_name())
            study_to_lock = repository2.find_by_uid(created_study.uid, for_update=True)
            study_to_lock.lock(
                locked_version_info="locked version",
                locked_version_author=current_function_name(),
            )
            repository2.save(study_to_lock)
            repository2.close()

        # then
        with db.transaction:
            repository3 = StudyDefinitionRepositoryImpl(current_function_name())
            locked_study = repository3.find_by_uid(created_study.uid)
            repository3.close()
        print("LOCKED", locked_study)
        self.assertEqual(
            locked_study.current_metadata.ver_metadata,
            study_to_lock.current_metadata.ver_metadata,
        )
        self.assertEqual(locked_study, study_to_lock)

    def test__save__after_metadata_edit_with_different_values__result(self):
        # given
        with db.transaction:
            repository1 = StudyDefinitionRepositoryImpl(current_function_name())
            created_study = create_random_study(
                repository1.generate_uid,
                new_id_metadata_fixed_values={
                    "project_number": self.created_project.project_number
                },
                is_study_after_create=True,
            )
            repository1.save(created_study)
            repository1.close()

        # when
        with db.transaction:
            repository2 = StudyDefinitionRepositoryImpl(current_function_name())
            amended_study = repository2.find_by_uid(created_study.uid, for_update=True)
            assert (
                amended_study == created_study
            )  # this is not the test just making sure we are on track here
            make_random_study_metadata_edit(
                amended_study,
                new_id_metadata_fixed_values={
                    "project_number": self.project_to_amend.project_number,
                    "study_number": created_study.current_metadata.id_metadata.study_number,
                },
            )
            repository2.save(amended_study)
            repository2.close()

        # then
        with db.transaction:
            repository3 = StudyDefinitionRepositoryImpl(current_function_name())
            final_retrieved_study = repository3.find_by_uid(created_study.uid)
            repository3.close()

        self.assertEqual(final_retrieved_study, amended_study)

    def test__save__after_metadata_edit_with_same_values__result(self):
        # given
        with db.transaction:
            repository1 = StudyDefinitionRepositoryImpl(current_function_name())
            created_study = create_random_study(
                repository1.generate_uid,
                new_id_metadata_fixed_values={
                    "project_number": self.created_project.project_number
                },
                is_study_after_create=True,
            )
            repository1.save(created_study)
            repository1.close()

        # when
        with db.transaction:
            repository2 = StudyDefinitionRepositoryImpl(current_function_name())
            amended_study = repository2.find_by_uid(created_study.uid, for_update=True)
            assert (
                amended_study == created_study
            )  # this is not the test just making sure we are on track here
            amended_study.edit_metadata(
                new_id_metadata=amended_study.current_metadata.id_metadata,
                project_exists_callback=(lambda _: True),
            )
            repository2.save(amended_study)
            repository2.close()

        # then
        with db.transaction:
            repository3 = StudyDefinitionRepositoryImpl(current_function_name())
            final_retrieved_study = repository3.find_by_uid(created_study.uid)
            repository3.close()

        self.assertEqual(final_retrieved_study, amended_study)

    def test__save__after_unlock__result(self):
        # given
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            created_study = create_random_study(
                generate_uid_callback=repo.generate_uid,
                new_id_metadata_fixed_values={
                    "project_number": self.created_project.project_number
                },
                is_study_after_create=True,
            )
            repo.save(created_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            amended_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                amended_study == created_study
            )  # not a test, just making sure we are on track
            make_random_study_metadata_edit(
                amended_study,
                new_id_metadata_condition=(lambda _: _.study_number is not None),
                new_id_metadata_fixed_values={
                    "project_number": self.project_to_amend.project_number,
                    "study_number": created_study.current_metadata.id_metadata.study_number,
                },
            )
            repo.save(amended_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            locked_study = repo.find_by_uid(created_study.uid, for_update=True)
            print("LCK", locked_study)
            print("LCK", amended_study)
            assert (
                locked_study == amended_study
            )  # not a test, just making sure we're on track
            locked_study.lock(
                locked_version_info="very important version",
                locked_version_author=current_function_name(),
            )
            repo.save(locked_study)
            repo.close()

        # when
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            unlocked_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                unlocked_study == locked_study
            )  # not a test, just making sure we're on track
            unlocked_study.unlock()
            repo.save(unlocked_study)
            repo.close()

        # then
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            final_retrieved_study = repo.find_by_uid(created_study.uid)
            repo.close()

        self.assertEqual(final_retrieved_study, unlocked_study)

    def test__save__after_release__result(self):
        # given
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            created_study = create_random_study(
                generate_uid_callback=repo.generate_uid,
                new_id_metadata_fixed_values={
                    "project_number": self.created_project.project_number
                },
                is_study_after_create=True,
            )
            repo.save(created_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            amended_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                amended_study == created_study
            )  # not a test, just making sure we are on track
            make_random_study_metadata_edit(
                amended_study,
                new_id_metadata_fixed_values={
                    "project_number": self.project_to_amend.project_number,
                    "study_number": created_study.current_metadata.id_metadata.study_number,
                },
            )
            repo.save(amended_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            released_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                released_study == amended_study
            )  # not a test, just making sure we're on track
            released_study.release()
            repo.save(released_study)
            repo.close()

        # then
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            final_retrieved_study = repo.find_by_uid(created_study.uid)
            repo.close()

        self.assertEqual(final_retrieved_study, released_study)

    def test__save__after_release_and_edit__result(self):
        # given
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            created_study = create_random_study(
                generate_uid_callback=repo.generate_uid,
                new_id_metadata_fixed_values={
                    "project_number": self.created_project.project_number
                },
                is_study_after_create=True,
            )
            repo.save(created_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            amended_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                amended_study == created_study
            )  # not a test, just making sure we are on track
            make_random_study_metadata_edit(
                amended_study,
                new_id_metadata_fixed_values={
                    "project_number": self.project_to_amend.project_number,
                    "study_number": created_study.current_metadata.id_metadata.study_number,
                },
            )
            repo.save(amended_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            released_study = repo.find_by_uid(created_study.uid, for_update=True)
            print(
                "REL",
                released_study._draft_metadata.study_intervention.drug_study_indication_null_value_code,
            )
            print(
                "AMD",
                amended_study._draft_metadata.study_intervention.drug_study_indication_null_value_code,
            )
            assert (
                released_study == amended_study
            )  # not a test, just making sure we're on track
            released_study.release()
            repo.save(released_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            amended_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                amended_study == released_study
            )  # not a test, just making sure we are on track
            make_random_study_metadata_edit(
                amended_study,
                new_id_metadata_fixed_values={
                    "project_number": self.project_to_amend.project_number,
                    "study_number": created_study.current_metadata.id_metadata.study_number,
                },
            )
            repo.save(amended_study)
            repo.close()

        # then
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            final_retrieved_study = repo.find_by_uid(created_study.uid)
            repo.close()
        print(
            "FIN",
            final_retrieved_study.current_metadata.id_metadata.study_number,
            created_study.current_metadata.id_metadata.study_number,
        )
        print(
            "FIN",
            final_retrieved_study.current_metadata.id_metadata.project_number,
            amended_study.current_metadata.id_metadata.project_number,
        )
        self.assertEqual(final_retrieved_study, amended_study)

    def test__save__after_lock_unlock_release_lock__result(self):
        # given
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            created_study = create_random_study(
                generate_uid_callback=repo.generate_uid,
                new_id_metadata_fixed_values={
                    "project_number": self.created_project.project_number
                },
                is_study_after_create=True,
            )
            repo.save(created_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            amended_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                amended_study == created_study
            )  # not a test, just making sure we are on track
            make_random_study_metadata_edit(
                amended_study,
                new_id_metadata_condition=(
                    lambda _: _.project_number is not None
                    and _.study_number is not None
                ),
                new_id_metadata_fixed_values={
                    "project_number": self.project_to_amend.project_number,
                    "study_number": created_study.current_metadata.id_metadata.study_number,
                },
            )
            repo.save(amended_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            locked_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                locked_study == amended_study
            )  # not a test, just making sure we're on track
            locked_study.lock(
                locked_version_info="very important version",
                locked_version_author=current_function_name(),
            )
            repo.save(locked_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            unlocked_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                unlocked_study == locked_study
            )  # not a test, just making sure we are on track
            unlocked_study.unlock()
            repo.save(unlocked_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            released_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                released_study == unlocked_study
            )  # not a test, just making sure we are on track
            released_study.release()
            repo.save(released_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            locked_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                locked_study == released_study
            )  # not a test, just making sure we are on track
            locked_study.lock(
                locked_version_author=current_function_name(),
                locked_version_info="another very important version",
            )
            repo.save(locked_study)
            repo.close()

        # then
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            final_retrieved_study = repo.find_by_uid(created_study.uid)
            repo.close()

        self.assertEqual(final_retrieved_study, locked_study)

    def test__save__after_lock_unlock_release_lock_and_edits_in_between__result(self):
        # given
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            created_study = create_random_study(
                generate_uid_callback=repo.generate_uid,
                new_id_metadata_fixed_values={
                    "project_number": self.created_project.project_number
                },
                is_study_after_create=True,
            )
            repo.save(created_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            amended_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                amended_study == created_study
            )  # not a test, just making sure we are on track
            make_random_study_metadata_edit(
                amended_study,
                new_id_metadata_condition=(lambda _: _.study_number is not None),
                new_id_metadata_fixed_values={
                    "project_number": self.project_to_amend.project_number,
                    "study_number": created_study.current_metadata.id_metadata.study_number,
                },
            )
            repo.save(amended_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            locked_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                locked_study == amended_study
            )  # not a test, just making sure we're on track
            locked_study.lock(
                locked_version_info="very important version",
                locked_version_author=current_function_name(),
            )
            repo.save(locked_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            unlocked_study = repo.find_by_uid(created_study.uid, for_update=True)
            assert (
                unlocked_study == locked_study
            )  # not a test, just making sure we are on track
            unlocked_study.unlock()
            repo.save(unlocked_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            amended_study = repo.find_by_uid(created_study.uid, for_update=True)
            print("amended_study", amended_study)
            print("unlocked_study", unlocked_study)
            assert (
                amended_study == unlocked_study
            )  # not a test, just making sure we are on track
            make_random_study_metadata_edit(
                amended_study,
                new_id_metadata_condition=(
                    lambda _: _.project_number is not None
                    and _.study_number is not None
                ),
                new_id_metadata_fixed_values={
                    "project_number": self.project_to_amend.project_number,
                    "study_number": created_study.current_metadata.id_metadata.study_number,
                },
            )
            repo.save(amended_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            released_study = repo.find_by_uid(created_study.uid, for_update=True)
            print("released_study", released_study)
            print("amended_study", amended_study)
            assert (
                released_study == amended_study
            )  # not a test, just making sure we are on track
            released_study.release()
            repo.save(released_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            amended_study = repo.find_by_uid(created_study.uid, for_update=True)
            print("amended_study", amended_study)
            print("released_study", released_study)
            assert (
                amended_study == released_study
            )  # not a test, just making sure we are on track
            make_random_study_metadata_edit(
                amended_study,
                new_id_metadata_condition=(lambda _: _.project_number is not None),
                new_id_metadata_fixed_values={
                    "project_number": self.project_to_amend.project_number,
                    "study_number": created_study.current_metadata.id_metadata.study_number,
                },
            )
            repo.save(amended_study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            locked_study = repo.find_by_uid(created_study.uid, for_update=True)
            print("locked_study", locked_study)
            print("amended_study", amended_study)
            assert (
                locked_study == amended_study
            )  # not a test, just making sure we are on track
            locked_study.lock(
                locked_version_author=current_function_name(),
                locked_version_info="another very important version",
            )
            repo.save(locked_study)
            repo.close()

        # then
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            final_retrieved_study = repo.find_by_uid(created_study.uid)
            repo.close()

        self.assertEqual(final_retrieved_study, locked_study)

    def test__find_all__results(self):
        # given
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            test_studies = [
                create_random_study(
                    repo.generate_uid,
                    new_id_metadata_fixed_values={
                        "project_number": self.created_project.project_number
                    },
                    is_study_after_create=True,
                )
                for _ in range(0, 10)
            ]
            for study in test_studies:
                repo.save(study)
            repo.close()

        # when
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            all_studies_in_db = repo.find_all(
                page_number=1, page_size=sys.maxsize
            ).items
            repo.close()

        # then
        # we check if all test_studies are in all_studies_in_db
        # to achieve this we build a dictionary first
        db_studies: Dict[str, StudyDefinitionAR] = {}
        for _study in all_studies_in_db:
            db_studies[_study.uid] = _study

        # then we go by test_studies and assert all of them are in the dictionary
        for test_study in test_studies:
            with self.subTest():
                self.assertEqual(db_studies[test_study.uid], test_study)

    def test__find_all__with_custom_sort_order__success(self):
        # given
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            test_studies = [
                create_random_study(
                    repo.generate_uid,
                    new_id_metadata_fixed_values={
                        "project_number": self.created_project.project_number
                    },
                    is_study_after_create=True,
                )
                for _ in range(0, 10)
            ]
            for study in test_studies:
                repo.save(study)
            repo.close()

        # when
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            all_studies_in_db = repo.find_all(
                page_number=1, page_size=sys.maxsize
            ).items
            repo.close()

        # then
        # we check if all test_studies are in all_studies_in_db
        # to achieve this we build a dictionary first
        # TODO: would be nice to do the sort order check as well (not doing that currently)
        db_studies: Dict[str, StudyDefinitionAR] = {}
        for _study in all_studies_in_db:
            db_studies[_study.uid] = _study

        # then we go by test_studies and assert all of them are in the dictionary
        for test_study in test_studies:
            with self.subTest():
                self.assertEqual(db_studies[test_study.uid], test_study)

    def test__find_by_id__find_for_update_without_transaction__failure(self):
        # given
        uid = "some-uid"

        # then
        with self.assertRaises(SystemError):

            # when
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            repo.find_by_uid(uid, for_update=True)

    def test__save__after_create_and_closing_transaction__failure(self):
        # given
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            study = create_random_study(
                generate_uid_callback=repo.generate_uid,
                new_id_metadata_fixed_values={
                    "project_number": self.created_project.project_number
                },
            )

        # then
        with self.assertRaises(SystemError):

            # when
            repo.save(study)

    def test__save__after_retrieve_for_update_and_closing_transaction__failure(self):
        # given
        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            study = create_random_study(
                generate_uid_callback=repo.generate_uid,
                new_id_metadata_fixed_values={
                    "project_number": self.created_project.project_number
                },
            )
            repo.save(study)
            repo.close()

        with db.transaction:
            repo = StudyDefinitionRepositoryImpl(current_function_name())
            study = repo.find_by_uid(study.uid, for_update=True)

        # then
        with self.assertRaises(SystemError):

            # when
            repo.save(study)
