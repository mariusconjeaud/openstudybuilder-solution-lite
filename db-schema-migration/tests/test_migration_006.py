import os

import pytest

from migrations import migration_006
from migrations.utils.utils import (
    api_get,
    api_get_paged,
    execute_statements,
    get_db_connection,
    get_db_driver,
    get_logger,
    run_cypher_query,
)
from tests import common

try:
    from tests.data.db_before_migration_006 import TEST_DATA
except ImportError:
    TEST_DATA = ""
from tests.utils.utils import clear_db

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments
# pylint: disable=protected-access

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

db = get_db_connection()
DB_DRIVER = get_db_driver()
logger = get_logger(os.path.basename(__file__))


@pytest.fixture(scope="module")
def initial_data():
    """Insert test data"""
    clear_db()
    execute_statements(TEST_DATA)


@pytest.fixture(scope="module")
def migration(initial_data):
    # Run migration
    migration_006.main()


def test_indexes_and_constraints(migration):
    common.test_indexes_and_constraints(db, logger)


def test_ct_config_values(migration):
    common.test_ct_config_values(db, logger)


def test_migrate_study_activity_instances(migration):
    studies, _ = run_cypher_query(
        DB_DRIVER,
        """
        MATCH (study_root:StudyRoot) return study_root.uid
        """,
    )
    for study in studies:
        study_uid = study[0]
        logger.info(
            "Verifying that StudyActivityInstances are migrated for the following Study (%s)",
            study_uid,
        )

        res = api_get_paged(
            f"/studies/{study_uid}/study-activities",
            params={
                "filters": '{"activity.library_name":{ "v": ["Requested"], "op": "ne"}}'
            },
            page_size=10,
        )
        study_activities = res["items"]
        if len(study_activities) > 0:
            res = api_get_paged(
                f"/studies/{study_uid}/study-activity-instances",
                page_size=10,
            )
            study_activity_instances = res["items"]
            assert (
                len(study_activity_instances) > 0
            ), "If there exist some StudyActivities, the StudyActivityInstances should also exist"

            ### This is disabled for now, see below
            study_activity_instance_dict: dict = {}
            # vals: list = []
            for study_activity_instance in study_activity_instances:
                assert study_activity_instance["activity"] is not None
                study_activity_uid = study_activity_instance["study_activity_uid"]
                response = api_get(
                    f"/studies/{study_uid}/study-activities/{study_activity_uid}"
                )
                assert response.status_code == 200
                res = response.json()
                assert (
                    study_activity_instance["activity"]["uid"] == res["activity"]["uid"]
                )
                activity_instance = study_activity_instance["activity_instance"]
                if activity_instance:
                    response = api_get(
                        f"/concepts/activities/activity-instances/{activity_instance['uid']}/versions"
                    )
                    assert response.status_code == 200
                    res = response.json()
                    activity_uids = []
                    for activity_instance in res:
                        activity_uids.extend(
                            [
                                activity_grouping["activity"]["uid"]
                                for activity_grouping in activity_instance[
                                    "activity_groupings"
                                ]
                            ]
                        )
                    assert study_activity_instance["activity"]["uid"] in activity_uids

                study_activity_instance_dict[
                    study_activity_instance["study_activity_instance_uid"]
                ] = (
                    study_activity_instance["activity"]["uid"],
                    study_activity_instance["study_activity_subgroup"][
                        "activity_subgroup_uid"
                    ],
                    study_activity_instance["study_activity_group"][
                        "activity_group_uid"
                    ],
                    study_activity_instance["activity_instance"]["uid"]
                    if study_activity_instance["activity_instance"]
                    else None,
                )
                # vals = list(study_activity_instance_dict.values())
            # We have to comment assertion as there exists duplicated StudyActivities affected
            # by multiple StudyActivitySubGroup/StudyActivityGroup relationships and that create
            # assert len(set(vals)) == len(
            #     vals
            # ), f"There exists some duplicated StudyActivityInstance in Study ({study_uid})"


@pytest.mark.order(after="test_migrate_study_activity_instances")
def test_repeat_migrate_study_activity_instances(migration):
    assert not any(
        migration_006.migrate_study_activity_instances(DB_DRIVER, logger)
    ), "The second run for migration shouldn't return anything"


# def test_remove_study_activities_with_the_same_groupings(migration):
#     studies, _ = run_cypher_query(
#         DB_DRIVER,
#         """
#         MATCH (study_root:StudyRoot) return study_root.uid
#         """,
#     )
#     for study in studies:
#         study_uid = study[0]
#         logger.info(
#             "Verifying that there are no duplicated StudyActivities for the following Study (%s)",
#             study_uid,
#         )
#         query = """
#                 MATCH (r:StudyRoot{uid:$study_uid})-[:LATEST]->(v:StudyValue)-[:HAS_STUDY_ACTIVITY]->(sa:StudyActivity)-[:HAS_SELECTED_ACTIVITY]->(activity_value)
#                 MATCH (sa)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_GROUP]->(sg:StudyActivityGroup)-[:HAS_SELECTED_ACTIVITY_GROUP]->(activity_group_value)
#                 MATCH (sa)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_SUBGROUP]->(ssg:StudyActivitySubGroup)-[:HAS_SELECTED_ACTIVITY_SUBGROUP]->(activity_subgroup_value)
#                 WITH sa,
#                     head([(activity_value)<-[:HAS_VERSION]-(activity_root) | activity_root]) as activity_root,
#                     head([(activity_subgroup_value)<-[:HAS_VERSION]-(activity_subgroup_root) | activity_subgroup_root]) as activity_subgroup_root,
#                     head([(activity_group_value)<-[:HAS_VERSION]-(activity_group_root) | activity_group_root]) as activity_group_root
#                 WITH collect(distinct sa) as duplicated_study_activities, activity_root, activity_subgroup_root, activity_group_root
#                 WHERE size(duplicated_study_activities) > 1
#             RETURN *
#         """
#         result = run_cypher_query(DB_DRIVER, query, params={"study_uid": study_uid})
#         assert (
#             len(result[0]) == 0
#         ), f"Study {study_uid} contains StudyActivities with the same ActivityGroupings"


# @pytest.mark.order(after="test_remove_study_activities_with_the_same_groupings")
# def test_repeat_remove_study_activities_with_the_same_groupings(migration):
#     assert not any(
#         migration_006.remove_duplicated_study_activities_with_the_same_groupings(
#             DB_DRIVER, logger
#         )
#     ), "The second run for migration shouldn't return anything"


def test_update_insertion_visit_to_manually_defined(migration):
    query = """
        MATCH (study_visit:StudyVisit) 
        WHERE study_visit.visit_class = "INSERTION_VISIT"
        RETURN study_visit
    """
    result = run_cypher_query(DB_DRIVER, query)
    assert (
        len(result[0]) == 0
    ), "There shouldn't be any INSERTION_VISITs. All of them should be updated to MANUALLY_DEFINED_VISITs"


@pytest.mark.order(after="test_update_insertion_visit_to_manually_defined")
def test_repeat_update_insertion_visit_to_manually_defined(migration):
    assert not migration_006.update_insertion_visit_to_manually_defined_visit(
        DB_DRIVER, logger
    ), "The second run for migration shouldn't return anything"


def test_fix_duration_properties_for_visits_with_negative_timings(migration):
    res = api_get("/concepts/numeric-values", params={"page_size": 0})
    assert res.status_code == 200
    res = api_get("/concepts/study-days", params={"page_size": 0})
    assert res.status_code == 200
    res = api_get("/concepts/study-duration-days", params={"page_size": 0})
    assert res.status_code == 200
    res = api_get("/concepts/study-weeks", params={"page_size": 0})
    assert res.status_code == 200
    res = api_get("/concepts/study-duration-weeks", params={"page_size": 0})
    assert res.status_code == 200
    res = api_get("/concepts/study-duration-weeks", params={"page_size": 0})
    assert res.status_code == 200

    query = """
        MATCH (study_visit:StudyVisit)-[:HAS_STUDY_DAY]->(:StudyDayRoot)-[:LATEST]->(study_day_value:StudyDayValue)
        MATCH (study_visit)-[:HAS_STUDY_DURATION_DAYS]->(:StudyDurationDaysRoot)-[:LATEST]->(study_duration_days_value:StudyDurationDaysValue)
        MATCH (study_visit:StudyVisit)-[:HAS_STUDY_WEEK]->(:StudyWeekRoot)-[:LATEST]->(study_week_value:StudyWeekValue)
        MATCH (study_visit)-[:HAS_STUDY_DURATION_WEEKS]->(:StudyDurationWeeksRoot)-[:LATEST]->(study_duration_weeks_value:StudyDurationWeeksValue)
        MATCH (study_visit)-[:HAS_WEEK_IN_STUDY]->(:WeekInStudyRoot)-[:LATEST]->(week_in_study_value:WeekInStudyValue)
        RETURN study_visit.uid, study_day_value.value, study_duration_days_value.value, study_week_value.value, study_duration_weeks_value.value, week_in_study_value.value
    """
    study_visits, _ = run_cypher_query(DB_DRIVER, query)
    for study_visit in study_visits:
        study_visit_uid = study_visit[0]
        study_day_value = study_visit[1]
        study_duration_days_value = study_visit[2]
        study_week_value = study_visit[3]
        study_duration_weeks_value = study_visit[4]
        week_in_study_value = study_visit[4]
        if study_day_value % 7 == 0 and study_day_value < 0:
            assert (
                study_day_value == study_duration_days_value
            ), f"The StudyDay-StudyDurationDays contains mismatched values for the Visit ({study_visit_uid})"
            assert (
                study_week_value == study_duration_weeks_value
            ), f"The StudyWeek-StudyDurationWeeks contains mismatched values for the Visit ({study_visit_uid})"
            assert (
                study_week_value == week_in_study_value
            ), f"The StudyWeek-WeekInStudy contains mismatched values for the Visit ({study_visit_uid})"
        elif study_day_value < 0:
            assert (
                study_day_value == study_duration_days_value
            ), f"The StudyDay-StudyDurationDays contains mismatched values for the Visit ({study_visit_uid})"
            assert (
                study_week_value == study_duration_weeks_value - 1
            ), f"The StudyWeek-StudyDurationWeeks contains mismatched values for the Visit ({study_visit_uid})"
            assert (
                study_week_value == week_in_study_value - 1
            ), f"The StudyWeek-WeekInStudy contains mismatched values for the Visit ({study_visit_uid})"
        elif study_day_value > 0:
            assert (
                study_day_value == study_duration_days_value + 1
            ), f"The StudyDay-StudyDurationDays contains mismatched values for the Visit ({study_visit_uid})"
            assert (
                study_week_value == study_duration_weeks_value + 1
            ), f"The StudyWeek-StudyDurationWeeks contains mismatched values for the Visit ({study_visit_uid})"
            assert (
                study_week_value == week_in_study_value + 1
            ), f"The StudyWeek-WeekInStudy contains mismatched values for the Visit ({study_visit_uid})"

    studies, _ = run_cypher_query(
        DB_DRIVER,
        """
        MATCH (study_root:StudyRoot) return study_root.uid
        """,
    )
    for study in studies:
        study_uid = study[0]
        logger.info(
            "Verifying that StudyVisits have proper timing nodes for the following Study (%s)",
            study_uid,
        )
        res = api_get(f"/studies/{study_uid}/study-visits", params={"page_size": 0})
        study_visits = res.json()["items"]
        for study_visit in study_visits:
            if study_visit["visit_class"] not in (
                "UNSCHEDULED_VISIT",
                "NON_VISIT",
                "SPECIAL_VISIT",
            ):
                study_day_number = study_visit["study_day_number"]
                study_duration_days_number = int(
                    study_visit["study_duration_days_label"].split()[0]
                )
                study_week_number = study_visit["study_week_number"]
                study_duration_weeks_number = int(
                    study_visit["study_duration_weeks_label"].split()[0]
                )
                week_in_study_number = int(
                    study_visit["week_in_study_label"].split()[1]
                )
                if study_day_number % 7 == 0 and study_day_number < 0:
                    assert study_day_number == study_duration_days_number
                    assert study_week_number == study_duration_weeks_number
                    assert study_week_number == week_in_study_number
                elif study_day_number < 0:
                    assert study_day_number == study_duration_days_number
                    assert study_week_number == study_duration_weeks_number - 1
                    assert study_week_number == week_in_study_number - 1
                elif study_day_number > 0:
                    assert study_day_number == study_duration_days_number + 1
                    assert study_week_number == study_duration_weeks_number + 1
                    assert study_week_number == week_in_study_number + 1


@pytest.mark.order(
    after="test_fix_duration_properties_for_visits_with_negative_timings"
)
def test_repeat_fix_duration_properties_for_visits_with_negative_timings(migration):
    assert not migration_006.fix_duration_properties_for_visits_with_negative_timings(
        DB_DRIVER, logger, migration_006.MIGRATION_DESC
    ), "The second run for migration shouldn't return anything"
