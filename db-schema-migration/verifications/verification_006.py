"""
This modules verifies that database nodes/relations and API endpoints look and behave as expected.

It utilizes tests written for verifying a specific migration,
without inserting any test data and without running any migration script on the target database.
"""

import pytest

from tests import test_migration_006


@pytest.fixture(scope="module")
def migration():
    """
    This method is empty as we do not want to run any migration script here.
    We just wish to run all tests related to a specific migration.
    """


def test_indexes_and_constraints():
    test_migration_006.test_indexes_and_constraints(migration)


def test_migrate_study_activity_instances():
    test_migration_006.test_migrate_study_activity_instances(migration)


# def test_remove_study_activities_with_the_same_groupings():
#     test_migration_006.test_remove_study_activities_with_the_same_groupings(migration)


def test_update_insertion_visit_to_manually_defined():
    test_migration_006.test_update_insertion_visit_to_manually_defined(migration)


def test_fix_duration_properties_for_visits_with_negative_timings():
    test_migration_006.test_fix_duration_properties_for_visits_with_negative_timings(
        migration
    )
