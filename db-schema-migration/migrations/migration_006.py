""" Schema migrations needed for release to PROD post Mar 2024."""
from math import ceil, floor
import os

from migrations.common import migrate_ct_config_values, migrate_indexes_and_constraints
from migrations.utils.utils import (
    get_db_driver,
    run_cypher_query,
    get_logger,
    print_counters_table,
    get_db_connection,
)

logger = get_logger(os.path.basename(__file__))
DB_DRIVER = get_db_driver()
DB_CONNECTION = get_db_connection()
MIGRATION_DESC = "schema-migration-release-1.6"


def main():
    logger.info("Running migration on DB '%s'", os.environ["DATABASE_NAME"])

    ### Common migrations
    migrate_indexes_and_constraints(DB_CONNECTION, logger)
    migrate_ct_config_values(DB_CONNECTION, logger)

    ### Release-specific migrations
    # remove_duplicated_study_activities_with_the_same_groupings(DB_DRIVER, logger)
    remove_broken_study_activity_instances(DB_DRIVER, logger)
    migrate_study_activity_instances(DB_DRIVER, logger)
    update_insertion_visit_to_manually_defined_visit(DB_DRIVER, logger)
    fix_study_week_property_for_negative_timings_less_than_one_week(
        DB_DRIVER, logger, MIGRATION_DESC
    )
    fix_duration_properties_for_visits_with_negative_timings(
        DB_DRIVER, logger, MIGRATION_DESC
    )


def remove_duplicated_study_activities_with_the_same_groupings(db_driver, log):
    studies, _ = run_cypher_query(
        db_driver,
        """
        MATCH (study_root:StudyRoot) return study_root.uid
        """,
    )
    contains_updates = []
    for study in studies:
        study_uid = study[0]
        log.info(
            "Removing duplciated StudyActivities with the same groupings for the following Study (%s)",
            study_uid,
        )
        _, summary = run_cypher_query(
            db_driver,
            """
                MATCH (r:StudyRoot{uid:$study_uid})-[:LATEST]->(v:StudyValue)-[:HAS_STUDY_ACTIVITY]->(sa:StudyActivity)-[:HAS_SELECTED_ACTIVITY]->(activity_value)
                MATCH (sa)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_GROUP]->(sg:StudyActivityGroup)-[:HAS_SELECTED_ACTIVITY_GROUP]->(activity_group_value)
                MATCH (sa)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_SUBGROUP]->(ssg:StudyActivitySubGroup)-[:HAS_SELECTED_ACTIVITY_SUBGROUP]->(activity_subgroup_value)
                WITH sa, 
                    head([(activity_value)<-[:HAS_VERSION]-(activity_root) | activity_root]) as activity_root, 
                    head([(activity_subgroup_value)<-[:HAS_VERSION]-(activity_subgroup_root) | activity_subgroup_root]) as activity_subgroup_root, 
                    head([(activity_group_value)<-[:HAS_VERSION]-(activity_group_root) | activity_group_root]) as activity_group_root
                WITH apoc.coll.sortNodes(collect(distinct sa), 'uid') as duplicated_study_activities, activity_root, activity_subgroup_root, activity_group_root
                WHERE size(duplicated_study_activities)>1 
                WITH duplicated_study_activities, head(duplicated_study_activities) as unique_study_activity
                
                UNWIND duplicated_study_activities as duplicated_study_activity
                // get all StudyActivitySchedule assigned to the duplicated StudyActivity
                OPTIONAL MATCH (duplicated_study_activity)-[:STUDY_ACTIVITY_HAS_SCHEDULE]->(study_activity_schedule:StudyActivitySchedule)<-[:STUDY_VISIT_HAS_SCHEDULE]-(study_visit:StudyVisit)
    
                CALL apoc.do.case([
                    // We don't want to copy over the StudyActivitySchedule relationship if it exists
                    study_activity_schedule IS NOT NULL AND study_visit is NOT NULL AND NOT (duplicated_study_activity)-[:STUDY_ACTIVITY_HAS_SCHEDULE]->(study_activity_schedule)<-[:STUDY_VISIT_HAS_SCHEDULE]-(study_visit),
    
                    'MERGE (duplicated_study_activity)-[:STUDY_ACTIVITY_HAS_SCHEDULE]->(study_activity_schedule)<-[:STUDY_VISIT_HAS_SCHEDULE]-(study_visit) RETURN null'
                ],
                '',
                { 
                    study_activity_schedule: study_activity_schedule,
                    study_visit: study_visit,
                    duplicated_study_activity:duplicated_study_activity
                }
                ) yield value


                MATCH (duplicated_study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_SUBGROUP]->(subgroup)--(subgroup_action:StudyAction)
                MATCH (duplicated_study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_GROUP]->(group)--(group_action:StudyAction)
                WHERE duplicated_study_activity <> unique_study_activity
    
                DETACH DELETE duplicated_study_activity, subgroup, subgroup_action, group, group_action
                """,
            params={"study_uid": study_uid},
        )
        counters = summary.counters
        print_counters_table(counters)
        contains_updates.append(counters.contains_updates)
    return contains_updates


def remove_broken_study_activity_instances(db_driver, log):
    studies, _ = run_cypher_query(
        db_driver,
        """
        MATCH (study_root:StudyRoot) return study_root.uid
        """,
    )
    for study in studies:
        study_uid = study[0]
        log.info(
            "Removing broken StudyActivityInstances for the following Study (%s)",
            study_uid,
        )
        _, _ = run_cypher_query(
            db_driver,
            """
               MATCH (study_activity_instance:StudyActivityInstance)-[:BEFORE|AFTER]-(study_action:StudyAction)
               DETACH DELETE study_activity_instance, study_action
                """,
            params={"study_uid": study_uid},
        )


def migrate_study_activity_instances(db_driver, log):
    studies, _ = run_cypher_query(
        db_driver,
        """
        MATCH (study_root:StudyRoot) return study_root.uid
        """,
    )
    contains_updates = []
    for study in studies:
        study_uid = study[0]
        log.info(
            "Migrating StudyActivityInstances for the following Study (%s)", study_uid
        )
        _, summary = run_cypher_query(
            db_driver,
            """
            MATCH (study_root:StudyRoot {uid: $study_uid})-[:LATEST]->(study_value:StudyValue)-[:HAS_STUDY_ACTIVITY]
                ->(study_activity:StudyActivity)-[:HAS_SELECTED_ACTIVITY]->(activity_value:ActivityValue)
            WHERE NOT (study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_INSTANCE]->() AND
                head([(activity_value)<-[:HAS_VERSION]-(activity_root:ActivityRoot)<-[:CONTAINS_CONCEPT]-(library) | library.name]) <> "Requested"

            WITH DISTINCT study_activity, study_root, study_value, activity_value
            // StudyActivityInstance
            CREATE (study_activity_instance:StudyActivityInstance:StudySelection)
                MERGE (study_activity_instance_counter:Counter {counterId:'StudyActivityInstanceCounter'})
                ON CREATE SET study_activity_instance_counter:StudyActivityInstanceCounter, study_activity_instance_counter.count=1
                WITH *
                CALL apoc.atomic.add(study_activity_instance_counter,'count',1,1) yield oldValue, newValue
                WITH *, toInteger(newValue) as uid_number_study_activity_instance
                SET study_activity_instance.uid = "StudyActivityInstance_"+apoc.text.lpad(""+(uid_number_study_activity_instance), 6, "0")
            MERGE (study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_INSTANCE]->(study_activity_instance)
            MERGE (study_value)-[:HAS_STUDY_ACTIVITY_INSTANCE]->(study_activity_instance)
            MERGE (study_root)-[:AUDIT_TRAIL]->(:Create:StudyAction {user_initials:"schema-migration", date:datetime()})-[:AFTER]->(study_activity_instance)

            WITH study_activity_instance, activity_value
            OPTIONAL MATCH (activity_value)-[:HAS_GROUPING]
                ->(:ActivityGrouping)<-[:HAS_ACTIVITY]-(activity_instance_value:ActivityInstanceValue)
            WITH DISTINCT study_activity_instance, activity_instance_value
            ORDER BY activity_instance_value.is_required_for_activity DESC, activity_instance_value.is_defaulted_for_activity DESC
            CALL apoc.do.case([
                activity_instance_value is not null and not (study_activity_instance)-[:HAS_SELECTED_ACTIVITY_INSTANCE]->(),
                'MERGE (study_activity_instance)-[:HAS_SELECTED_ACTIVITY_INSTANCE]->(activity_instance_value) RETURN null'
            ],
            '',
            {
                activity_instance_value: activity_instance_value,
                study_activity_instance:study_activity_instance
            })
            YIELD value
            RETURN *
            """,
            params={"study_uid": study_uid},
        )
        counters = summary.counters
        print_counters_table(counters)
        contains_updates.append(counters.contains_updates)
    return contains_updates


def update_insertion_visit_to_manually_defined_visit(db_driver, log):
    log.info(
        "Updating INSERTION_VISIT to MANUALLY_DEFINED_VISIT as visit_class property."
    )
    _, summary = run_cypher_query(
        db_driver,
        """
            MATCH (study_visit:StudyVisit) 
            WHERE study_visit.visit_class = "INSERTION_VISIT"
            SET study_visit.visit_class = "MANUALLY_DEFINED_VISIT"
        """,
    )
    counters = summary.counters
    print_counters_table(counters)
    return counters.contains_updates


def fix_study_week_property_for_negative_timings_less_than_one_week(
    db_driver, log, migration_description
):
    study_visits, _ = run_cypher_query(
        db_driver,
        """
        MATCH (study_visit:StudyVisit)-[:HAS_STUDY_DAY]->(:StudyDayRoot)-[:LATEST]->(study_day_value:StudyDayValue)
        MATCH (study_visit:StudyVisit)-[:HAS_STUDY_WEEK]->(:StudyWeekRoot)-[:LATEST]->(study_week_value:StudyWeekValue)
        WHERE study_day_value.value < 1
        RETURN study_visit.uid, study_day_value.value, study_week_value.value, elementId(study_visit)
    """,
    )
    contains_updates = []
    for study_visit in study_visits:
        study_visit_uid = study_visit[0]
        study_day_value = study_visit[1]
        study_week_value = study_visit[2]
        study_visit_element_id = study_visit[3]

        fixed_study_week_value = floor(study_day_value / 7)
        if fixed_study_week_value != study_week_value:
            log.info(
                "Fixing StudyVisits StudyWeek for %s Visit with negative timings from the following interval -7<value<0",
                study_visit_uid,
            )
            # StudyWeek
            study_week, _ = run_cypher_query(
                db_driver,
                """
                MATCH (study_visit:StudyVisit)
                WHERE elementId(study_visit)=$study_visit_element_id
                MATCH (study_visit:StudyVisit)-[:HAS_STUDY_WEEK]->(study_week_root:StudyWeekRoot)-[:LATEST]->(study_week_value:StudyWeekValue{value:$value})
                WHERE NOT (study_visit)-[:HAS_STUDY_WEEK]->(study_week_root)
                RETURN study_week_root.uid
            """,
                params={
                    "study_visit_element_id": study_visit_element_id,
                    "value": fixed_study_week_value,
                },
            )
            if study_week:
                _, summary = run_cypher_query(
                    db_driver,
                    """
                        MATCH (study_visit:StudyVisit)-[old_has_study_week:HAS_STUDY_WEEK]->(:StudyWeekRoot)
                        WHERE elementId(study_visit)=$study_visit_element_id
                        MATCH (new_study_week_node:StudyWeekRoot {uid:$study_week_uid})
                        MERGE (study_visit)-[:HAS_STUDY_WEEK]->(new_study_week_node)
                        DETACH DELETE old_has_study_week
                    """,
                    params={
                        "study_visit_element_id": study_visit_element_id,
                        "study_week_uid": study_week[0][0],
                    },
                )
            else:
                _, summary = run_cypher_query(
                    db_driver,
                    """
                        MATCH (study_visit:StudyVisit)-[old_has_study_week:HAS_STUDY_WEEK]->(:StudyWeekRoot)
                        WHERE elementId(study_visit)=$study_visit_element_id
                        // Create StudyWeek
                        CREATE (study_week_root:SimpleConceptRoot:ConceptRoot:NumericValueRoot:StudyWeekRoot:TemplateParameterTermRoot)
                        CREATE (study_week_value:SimpleConceptValue:ConceptValue:NumericValue:StudyWeekValue:TemplateParameterTermValue)
                        SET study_week_value.value=toFloat($study_week_value)
                        SET study_week_value.name='Week ' + toInteger($study_week_value)
                        SET study_week_value.name_sentence_case='week ' + toInteger($study_week_value)
                            MERGE (study_week_counter:Counter {counterId:'StudyWeekCounter'})
                            ON CREATE SET study_week_counter:StudyWeekCounter, study_week_counter.count=1
                            WITH *
                            CALL apoc.atomic.add(study_week_counter,'count',1,1) yield oldValue, newValue
                            WITH *, toInteger(newValue) as uid_number_study_week
                            SET study_week_root.uid = "StudyWeek_"+apoc.text.lpad(""+(uid_number_study_week), 6, "0")
                        MERGE (study_visit)-[:HAS_STUDY_WEEK]->(study_week_root)
                        DETACH DELETE old_has_study_week
                        WITH study_week_root, study_week_value
                        MATCH (sponsor_library:Library {name:'Sponsor'})
                        MERGE (sponsor_library)-[:CONTAINS_CONCEPT]->(study_week_root)
                        MERGE (study_week_root)-[:LATEST_FINAL]->(study_week_value)
                        MERGE (study_week_root)-[:LATEST]->(study_week_value)
                        MERGE (study_week_root)-[has_version:HAS_VERSION]->(study_week_value)
                        SET has_version.change_description=$migration_description
                        SET has_version.start_date=datetime()
                        SET has_version.status='Final'
                        SET has_version.user_initials=$migration_description
                        SET has_version.version='1.0'
                        MERGE (tp:TemplateParameter {
                            name: "StudyWeek"
                        })
                        MERGE (study_duration_weeks_root)<-[:HAS_PARAMETER_TERM]-(tp)
                    """,
                    params={
                        "study_visit_element_id": study_visit_element_id,
                        "study_week_value": fixed_study_week_value,
                        "migration_description": migration_description,
                    },
                )
            counters = summary.counters
            print_counters_table(counters)
            contains_updates.append(counters.contains_updates)
    return contains_updates


def fix_duration_properties_for_visits_with_negative_timings(
    db_driver, log, migration_description
):
    study_visits, _ = run_cypher_query(
        db_driver,
        """
        MATCH (study_visit:StudyVisit)-[:HAS_STUDY_DAY]->(:StudyDayRoot)-[:LATEST]->(study_day_value:StudyDayValue)
        MATCH (study_visit)-[:HAS_STUDY_DURATION_DAYS]->(:StudyDurationDaysRoot)-[:LATEST]->(study_duration_days_value:StudyDurationDaysValue)
        MATCH (study_visit)-[:HAS_STUDY_DURATION_WEEKS]->(:StudyDurationWeeksRoot)-[:LATEST]->(study_duration_weeks_value:StudyDurationWeeksValue)
        MATCH (study_visit)-[:HAS_WEEK_IN_STUDY]->(:WeekInStudyRoot)-[:LATEST]->(week_in_study_value:WeekInStudyValue)
        WHERE study_day_value.value < 1
        RETURN study_visit.uid, study_day_value.value, study_duration_days_value.value, study_duration_weeks_value.value, week_in_study_value.value, elementId(study_visit)
    """,
    )
    contains_updates = []
    for study_visit in study_visits:
        study_visit_uid = study_visit[0]
        study_day_value = study_visit[1]
        study_duration_days_value = study_visit[2]
        study_duration_weeks_value = study_visit[3]
        week_in_study_value = study_visit[4]
        study_visit_element_id = study_visit[5]

        # StudyDurationDays
        fixed_study_duration_days_value = study_day_value
        if fixed_study_duration_days_value != study_duration_days_value:
            log.info(
                "Fixing StudyVisits duration properties for %s Visit with negative timings",
                study_visit_uid,
            )
            study_duration_days, _ = run_cypher_query(
                db_driver,
                """
                MATCH (study_visit:StudyVisit)
                WHERE elementId(study_visit)=$study_visit_element_id
                MATCH (study_duration_days_root:StudyDurationDaysRoot)-[:LATEST]-(study_duration_days_value:StudyDurationDaysValue{value:$value})
                WHERE NOT (study_visit)-[:HAS_STUDY_DURATION_DAYS]->(study_duration_days_root)
                RETURN study_duration_days_root.uid
            """,
                params={
                    "study_visit_element_id": study_visit_element_id,
                    "value": fixed_study_duration_days_value,
                },
            )
            if study_duration_days:
                _, summary = run_cypher_query(
                    db_driver,
                    """
                        MATCH (study_visit:StudyVisit)-[old_study_duration_days:HAS_STUDY_DURATION_DAYS]->(:StudyDurationDaysRoot)
                        WHERE elementId(study_visit)=$study_visit_element_id
                        MATCH (new_study_duration_days_node:StudyDurationDaysRoot {uid:$study_duration_days_uid})
                        MERGE (study_visit)-[:HAS_STUDY_DURATION_DAYS]->(new_study_duration_days_node)
                        DETACH DELETE old_study_duration_days
                    """,
                    params={
                        "study_visit_element_id": study_visit_element_id,
                        "study_duration_days_uid": study_duration_days[0][0],
                    },
                )
            else:
                _, summary = run_cypher_query(
                    db_driver,
                    """
                        MATCH (study_visit:StudyVisit)-[old_has_study_duration_days:HAS_STUDY_DURATION_DAYS]->(:StudyDurationDaysRoot)
                        WHERE elementId(study_visit)=$study_visit_element_id
                        // Create StudyDurationDays
                        CREATE (study_duration_days_root:SimpleConceptRoot:ConceptRoot:NumericValueRoot:TemplateParameterTermRoot:StudyDurationDaysRoot)
                        CREATE (study_duration_days_value:SimpleConceptValue:ConceptValue:NumericValue:TemplateParameterTermValue:StudyDurationDaysValue)
                        SET study_duration_days_value.value=toFloat($fixed_study_duration_days_value)
                        SET study_duration_days_value.name=toInteger($fixed_study_duration_days_value) + ' days'
                        SET study_duration_days_value.name_sentence_case=toInteger($fixed_study_duration_days_value) + ' days'
                            MERGE (study_duration_days_counter:Counter {counterId:'StudyDurationDaysCounter'})
                            ON CREATE SET study_duration_days_counter:StudyDurationDaysCounter, study_duration_days_counter.count=1
                            WITH *
                            CALL apoc.atomic.add(study_duration_days_counter,'count',1,1) yield oldValue, newValue
                            WITH *, toInteger(newValue) as uid_number_study_duration_days
                            SET study_duration_days_root.uid = "StudyDurationDays_"+apoc.text.lpad(""+(uid_number_study_duration_days), 6, "0")
                        MERGE (study_visit)-[:HAS_STUDY_DURATION_DAYS]->(study_duration_days_root)
                        DETACH DELETE old_has_study_duration_days
                        WITH study_duration_days_root, study_duration_days_value
                        MATCH (sponsor_library:Library {name:'Sponsor'})
                        MERGE (sponsor_library)-[:CONTAINS_CONCEPT]->(study_duration_days_root)
                        MERGE (study_duration_days_root)-[:LATEST_FINAL]->(study_duration_days_value)
                        MERGE (study_duration_days_root)-[:LATEST]->(study_duration_days_value)
                        MERGE (study_duration_days_root)-[has_version:HAS_VERSION]->(study_duration_days_value)
                        SET has_version.change_description=$migration_description
                        SET has_version.start_date=datetime()
                        SET has_version.status='Final'
                        SET has_version.user_initials=$migration_description
                        SET has_version.version='1.0'
                        MERGE (tp:TemplateParameter {
                            name: "StudyDurationDays"
                        })
                        MERGE (study_duration_weeks_root)<-[:HAS_PARAMETER_TERM]-(tp)
                    """,
                    params={
                        "study_visit_element_id": study_visit_element_id,
                        "fixed_study_duration_days_value": fixed_study_duration_days_value,
                        "migration_description": migration_description,
                    },
                )
            counters = summary.counters
            print_counters_table(counters)
            contains_updates.append(counters.contains_updates)

        # StudyDurationWeeks
        fixed_study_duration_weeks_value = ceil(study_day_value / 7)
        if fixed_study_duration_weeks_value != study_duration_weeks_value:
            study_duration_weeks, _ = run_cypher_query(
                db_driver,
                """
                MATCH (study_visit:StudyVisit)
                WHERE elementId(study_visit)=$study_visit_element_id
                MATCH (study_duration_weeks_root:StudyDurationWeeksRoot)-[:LATEST]-(study_duration_weeks_value:StudyDurationWeeksValue{value:$value})
                WHERE NOT (study_visit)-[:HAS_STUDY_DURATION_WEEKS]->(study_duration_weeks_root)
                RETURN study_duration_weeks_root.uid
            """,
                params={
                    "study_visit_element_id": study_visit_element_id,
                    "value": fixed_study_duration_weeks_value,
                },
            )
            if study_duration_weeks:
                _, summary = run_cypher_query(
                    db_driver,
                    """
                        MATCH (study_visit:StudyVisit)-[old_study_duration_weeks:HAS_STUDY_DURATION_WEEKS]->(:StudyDurationWeeksRoot)
                        WHERE elementId(study_visit)=$study_visit_element_id
                        MATCH (new_study_duration_weeks_node:StudyDurationWeeksRoot {uid:$study_duration_weeks_uid})
                        MERGE (study_visit)-[:HAS_STUDY_DURATION_WEEKS]->(new_study_duration_weeks_node)
                        DETACH DELETE old_study_duration_weeks
                    """,
                    params={
                        "study_visit_element_id": study_visit_element_id,
                        "study_duration_weeks_uid": study_duration_weeks[0][0],
                    },
                )
            else:
                _, summary = run_cypher_query(
                    db_driver,
                    """
                        MATCH (study_visit:StudyVisit)-[old_has_study_duration_weeks:HAS_STUDY_DURATION_WEEKS]->(:StudyDurationWeeksRoot)
                        WHERE elementId(study_visit)=$study_visit_element_id
                        // Create StudyDurationWeeks
                        CREATE (study_duration_weeks_root:SimpleConceptRoot:ConceptRoot:NumericValueRoot:TemplateParameterTermRoot:StudyDurationWeeksRoot)
                        CREATE (study_duration_weeks_value:SimpleConceptValue:ConceptValue:NumericValue:TemplateParameterTermValue:StudyDurationWeeksValue)
                        SET study_duration_weeks_value.value=toFloat($fixed_study_duration_weeks_value)
                        SET study_duration_weeks_value.name=toInteger($fixed_study_duration_weeks_value) + ' weeks'
                        SET study_duration_weeks_value.name_sentence_case=toInteger($fixed_study_duration_weeks_value) + ' weeks'
                            MERGE (study_duration_weeks_counter:Counter {counterId:'StudyDurationWeeksCounter'})
                            ON CREATE SET study_duration_weeks_counter:StudyDurationWeeksCounter, study_duration_weeks_counter.count=1
                            WITH *
                            CALL apoc.atomic.add(study_duration_weeks_counter,'count',1,1) yield oldValue, newValue
                            WITH *, toInteger(newValue) as uid_number_study_duration_weeks
                            SET study_duration_weeks_root.uid = "StudyDurationWeeks_"+apoc.text.lpad(""+(uid_number_study_duration_weeks), 6, "0")
                        MERGE (study_visit)-[:HAS_STUDY_DURATION_WEEKS]->(study_duration_weeks_root)
                        DETACH DELETE old_has_study_duration_weeks
                        WITH study_duration_weeks_root, study_duration_weeks_value
                        MATCH (sponsor_library:Library {name:'Sponsor'})
                        MERGE (sponsor_library)-[:CONTAINS_CONCEPT]->(study_duration_weeks_root)
                        MERGE (study_duration_weeks_root)-[:LATEST_FINAL]->(study_duration_weeks_value)
                        MERGE (study_duration_weeks_root)-[:LATEST]->(study_duration_weeks_value)
                        MERGE (study_duration_weeks_root)-[has_version:HAS_VERSION]->(study_duration_weeks_value)
                        SET has_version.change_description=$migration_description
                        SET has_version.start_date=datetime()
                        SET has_version.status='Final'
                        SET has_version.user_initials=$migration_description
                        SET has_version.version='1.0'
                        MERGE (tp:TemplateParameter {
                            name: "StudyDurationWeeks"
                        })
                        MERGE (study_duration_weeks_root)<-[:HAS_PARAMETER_TERM]-(tp)
                    """,
                    params={
                        "study_visit_element_id": study_visit_element_id,
                        "fixed_study_duration_weeks_value": fixed_study_duration_weeks_value,
                        "migration_description": migration_description,
                    },
                )
            counters = summary.counters
            print_counters_table(counters)
            contains_updates.append(counters.contains_updates)

        # WeekInStudy
        fixed_week_in_study_value = ceil(study_day_value / 7)
        if fixed_week_in_study_value != week_in_study_value:
            week_in_study, _ = run_cypher_query(
                db_driver,
                """
                MATCH (study_visit:StudyVisit)
                WHERE elementId(study_visit)=$study_visit_element_id
                MATCH (week_in_study_root:WeekInStudyRoot)-[:LATEST]-(week_in_study_value:WeekInStudyValue{value:$value})
                WHERE NOT (study_visit)-[:HAS_WEEK_IN_STUDY]->(week_in_study_root)
                RETURN week_in_study_root.uid
            """,
                params={
                    "study_visit_element_id": study_visit_element_id,
                    "value": fixed_week_in_study_value,
                },
            )
            if week_in_study:
                _, summary = run_cypher_query(
                    db_driver,
                    """
                        MATCH (study_visit:StudyVisit)-[old_week_in_study:HAS_WEEK_IN_STUDY]->(:WeekInStudyRoot)
                        WHERE elementId(study_visit)=$study_visit_element_id
                        MATCH (new_week_in_study_root_node:WeekInStudyRoot {uid:$week_in_study_uid})
                        MERGE (study_visit)-[:HAS_WEEK_IN_STUDY]->(new_week_in_study_root_node)
                        DETACH DELETE old_week_in_study
                    """,
                    params={
                        "study_visit_element_id": study_visit_element_id,
                        "week_in_study_uid": week_in_study[0][0],
                    },
                )
            else:
                _, summary = run_cypher_query(
                    db_driver,
                    """
                        MATCH (study_visit:StudyVisit)-[old_has_week_in_study:HAS_WEEK_IN_STUDY]->(:WeekInStudyRoot)
                        WHERE elementId(study_visit)=$study_visit_element_id
                        // Create WeekInStudy
                        CREATE (week_in_study_root:SimpleConceptRoot:ConceptRoot:NumericValueRoot:TemplateParameterTermRoot:WeekInStudyRoot)
                        CREATE (week_in_study_value:SimpleConceptValue:ConceptValue:NumericValue:TemplateParameterTermValue:WeekInStudyValue)
                        SET week_in_study_value.value=toFloat($fixed_week_in_study_value)
                        SET week_in_study_value.name='Week ' + toInteger($fixed_week_in_study_value)
                        SET week_in_study_value.name_sentence_case='week ' + toInteger($fixed_week_in_study_value)
                            MERGE (week_in_study_counter:Counter {counterId:'WeekInStudyCounter'})
                            ON CREATE SET week_in_study_counter:WeekInStudyCounter, week_in_study_counter.count=1
                            WITH *
                            CALL apoc.atomic.add(week_in_study_counter,'count',1,1) yield oldValue, newValue
                            WITH *, toInteger(newValue) as uid_number_week_in_study
                            SET week_in_study_root.uid = "WeekInStudy_"+apoc.text.lpad(""+(uid_number_week_in_study), 6, "0")
                        MERGE (study_visit)-[:HAS_WEEK_IN_STUDY]->(week_in_study_root)
                        DETACH DELETE old_has_week_in_study
                        WITH week_in_study_root, week_in_study_value
                        MATCH (sponsor_library:Library {name:'Sponsor'})
                        MERGE (sponsor_library)-[:CONTAINS_CONCEPT]->(week_in_study_root)
                        MERGE (week_in_study_root)-[:LATEST_FINAL]->(week_in_study_value)
                        MERGE (week_in_study_root)-[:LATEST]->(week_in_study_value)
                        MERGE (week_in_study_root)-[has_version:HAS_VERSION]->(week_in_study_value)
                        SET has_version.change_description=$migration_description
                        SET has_version.start_date=datetime()
                        SET has_version.status='Final'
                        SET has_version.user_initials=$migration_description
                        SET has_version.version='1.0'
                        MERGE (tp:TemplateParameter {
                            name: "WeekInStudy"
                        })
                        MERGE (week_in_study_root)<-[:HAS_PARAMETER_TERM]-(tp)
                    """,
                    params={
                        "study_visit_element_id": study_visit_element_id,
                        "fixed_week_in_study_value": fixed_week_in_study_value,
                        "migration_description": migration_description,
                    },
                )
            counters = summary.counters
            print_counters_table(counters)
            contains_updates.append(counters.contains_updates)

    return contains_updates


if __name__ == "__main__":
    main()
