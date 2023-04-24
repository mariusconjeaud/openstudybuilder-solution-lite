import time
from mdr_standards_import.scripts.entities.cdisc_data_models.data_model_type import (
    DataModelType,
)
from mdr_standards_import.scripts.utils import parse_ig_name, sanitize_string

USER_INITIALS = None
DATA_MODEL_ROOT_LABEL = "DataModelRoot"
DATA_MODEL_VALUE_LABEL = "DataModelValue"
DATA_MODEL_IG_ROOT_LABEL = "DataModelIGRoot"
DATA_MODEL_IG_VALUE_LABEL = "DataModelIGValue"
CLASS_ROOT_LABEL = "DatasetClassRoot"
CLASS_VALUE_LABEL = "DatasetClassValue"
SCENARIO_ROOT_LABEL = "DatasetScenarioRoot"
SCENARIO_VALUE_LABEL = "DatasetScenarioValue"
DATASET_ROOT_LABEL = "DatasetRoot"
DATASET_VALUE_LABEL = "DatasetValue"
CLASS_VARIABLE_ROOT_LABEL = "ClassVariableRoot"
CLASS_VARIABLE_VALUE_LABEL = "ClassVariableValue"
DATASET_VARIABLE_ROOT_LABEL = "DatasetVariableRoot"
DATASET_VARIABLE_VALUE_LABEL = "DatasetVariableValue"
SCENARIO_VARIABLE_VALUE_LABEL = "ScenarioVariableImplementation"
VERSION_TO_DATA_MODEL_REL_TYPE = "CONTAINS_DATA_MODEL"
VERSION_TO_DATA_MODEL_IG_REL_TYPE = "CONTAINS_DATA_MODEL_IG"
VERSION_TO_CLASS_REL_TYPE = "CONTAINS_DATASET_CLASS"
VERSION_TO_DATASET_REL_TYPE = "CONTAINS_DATASET"
VERSION_TO_SCENARIO_REL_TYPE = "CONTAINS_DATASET_SCENARIO"
VERSION_TO_CLASS_VARIABLE_REL_TYPE = "CONTAINS_CLASS_VARIABLE"
VERSION_TO_DATASET_VARIABLE_REL_TYPE = "CONTAINS_DATASET_VARIABLE"
CATALOGUE_TO_DATA_MODEL_REL_TYPE = "HAS_DATA_MODEL"
CATALOGUE_TO_DATA_MODEL_IG_REL_TYPE = "HAS_DATA_MODEL_IG"
CATALOGUE_TO_CLASS_ROOT_REL_TYPE = "HAS_DATASET_CLASS"
CATALOGUE_TO_DATASET_ROOT_REL_TYPE = "HAS_DATASET"
CATALOGUE_TO_SCENARIO_REL_TYPE = "HAS_DATASET_SCENARIO"
CATALOGUE_TO_CLASS_VARIABLE_ROOT_REL_TYPE = "HAS_CLASS_VARIABLE"
CATALOGUE_TO_DATASET_VARIABLE_ROOT_REL_TYPE = "HAS_DATASET_VARIABLE"
CLASS_TO_CLASS_VARIABLE_ROOT_REL_TYPE = "HAS_CLASS_VARIABLE"
CLASS_TO_DATASET_VARIABLE_ROOT_REL_TYPE = "HAS_DATASET_VARIABLE"
CLASS_TO_SCENARIO_REL_TYPE = "HAS_DATASET_SCENARIO"
SCENARIO_TO_VARIABLE_REL_TYPE = "HAS_DATASET_VARIABLE"
VARIABLE_TO_SCENARIO_VARIABLE_REL_TYPE = "HAS_SCENARIO_IMPLEMENTATION"
VERSION_TO_SCENARIO_VARIABLE_REL_TYPE = "CONTAINS_SCENARIO_VARIABLE"
SCENARIO_VARIABLE_TO_SCENARIO_REL_TYPE = "IMPLEMENTS_SCENARIO"


def import_from_cdisc_db_into_mdr(
    catalogue: str,
    version_number: str,
    cdisc_neo4j_driver,
    cdisc_db_name: str,
    mdr_neo4j_driver,
    mdr_db_name: str,
    user_initials: str,
):

    global USER_INITIALS
    USER_INITIALS = user_initials

    start_time = time.time()

    if catalogue is None or version_number is None:
        print(
            f"WARNING: No catalogue or version number specified. Not importing anything."
        )
        return

    with cdisc_neo4j_driver.session(database=cdisc_db_name) as session:
        # TODO : Uncomment when inconsistencies are implemented
        # with session.begin_transaction() as tx:
        #     print_ignored_stats(tx, catalogue, version_number)
        #     tx.commit()

        # read from the CDISC DB
        version_data = session.read_transaction(get_version, catalogue, version_number)
        classes_data = session.read_transaction(get_classes, catalogue, version_number)
        scenarios_data = session.read_transaction(
            get_scenarios, catalogue, version_number
        )
        variables_data = session.read_transaction(
            get_variables, catalogue, version_number
        )

        session.close()

        if len(version_data) > 0 and "version" in version_data[0]:
            with mdr_neo4j_driver.session(database=mdr_db_name) as session:

                # write to the clinical MDR db
                print("==  * Merging structure nodes and relationships.")
                session.write_transaction(
                    merge_structure_nodes_and_relationships,
                    version_data[0]["version"],
                    classes_data,
                    scenarios_data,
                    variables_data,
                )

                print("==  * Merging Data Model / Implementation Guide.")
                session.write_transaction(merge_data_model, version_data[0]["version"])


                print("==  * Merging Classes.")
                added_classes, updated_classes, unchanged_classes = session.write_transaction(
                    merge_classes, version_data[0]["version"], classes_data
                )
                print(f"==      Added classes:       {added_classes:6}")
                print(f"==      Updated classes:     {updated_classes:6}")
                print(f"==      Unchanged classes:   {unchanged_classes:6}")

                print("==  * Merging Scenarii.")
                added_scenarii, updated_scenarii, unchanged_scenarii = session.write_transaction(
                    merge_scenarios, version_data[0]["version"], scenarios_data
                )
                print(f"==      Added scenarii:      {added_scenarii:6}")
                print(f"==      Updated scenarii:    {updated_scenarii:6}")
                print(f"==      Unchanged scenarii:  {unchanged_scenarii:6}")

                print("==  * Merging Variables.")
                added_variables, updated_variables, unchanged_variables = session.write_transaction(
                    merge_variables, version_data[0]["version"], variables_data
                )
                print(f"==      Added variables:     {added_variables:6}")
                print(f"==      Updated variables:   {updated_variables:6}")
                print(f"==      Unchanged variables: {unchanged_variables:6}")

                session.close()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"== Duration: {round(elapsed_time, 1)} seconds")
    print("============================================")


def get_version(tx, catalogue: str, prefixed_version_number: str):
    version_data = tx.run(
        """
        MATCH (import:DataModelImport{catalogue: $catalogue, version_number: $prefixed_version_number})-[:INCLUDES]->(version)
        WHERE NOT (:Inconsistency)-[:AFFECTS_VERSION]->(version)
        RETURN
            version{uid: version.name, catalogue: $catalogue, data_model_type: import.data_model_type, implements_data_model: import.implements_data_model, .*} AS version
        """,
        catalogue=catalogue,
        prefixed_version_number=prefixed_version_number,
    ).data()
    for item in version_data:
        item["version"]["uid"] = sanitize_string(item["version"]["uid"])

    return version_data


def get_classes(tx, catalogue: str, prefixed_version_number: str):
    classes_data = tx.run(
        """
        MATCH (import:DataModelImport{catalogue: $catalogue, version_number: $prefixed_version_number})
            -[:INCLUDES]->(version)-[:CONTAINS]->(class)
        WHERE NOT (:Inconsistency)-[:AFFECTS_VERSION]->(version)
            AND NOT (:Inconsistency)-[:AFFECTS_CLASS]->(class)
        RETURN class
        """,
        catalogue=catalogue,
        prefixed_version_number=prefixed_version_number,
    ).data()
    for item in classes_data:
        item["class"]["uid"] = sanitize_string(item["class"]["name"])

    return classes_data


def get_scenarios(tx, catalogue: str, prefixed_version_number: str):
    scenarios_data = tx.run(
        """
        MATCH (import:DataModelImport{catalogue: $catalogue, version_number: $prefixed_version_number})
            -[:INCLUDES]->(version)-[:CONTAINS]->(class:DataModelClass)-[:CONTAINS]->(scenario:DataModelScenario)
        WHERE NOT (:Inconsistency)-[:AFFECTS_VERSION]->(version)
            AND NOT (:Inconsistency)-[:AFFECTS_CLASS]->(class)
            AND NOT (:Inconsistency)-[:AFFECTS_SCENARIO]->(scenario)
        RETURN scenario, class.href AS dataset_href
        """,
        catalogue=catalogue,
        prefixed_version_number=prefixed_version_number,
    ).data()
    for item in scenarios_data:
        item["scenario"]["uid"] = sanitize_string(item["scenario"]["title"])

    return scenarios_data


def get_variables(tx, catalogue: str, prefixed_version_number: str):
    variables_data = tx.run(
        """
        MATCH (import:DataModelImport{catalogue: $catalogue, version_number: $prefixed_version_number})
            -[:INCLUDES]->(version)-[:CONTAINS]->(class:DataModelClass)-[:CONTAINS]->(variable:DataModelVariable)
        WHERE NOT (:Inconsistency)-[:AFFECTS_VERSION]->(version)
            AND NOT (:Inconsistency)-[:AFFECTS_CLASS]->(class)
            AND NOT (:Inconsistency)-[:AFFECTS_VARIABLE]->(variable)
        RETURN variable, class.href AS parent_href, "class" AS parent_type
        UNION
        MATCH (import:DataModelImport{catalogue: $catalogue, version_number: $prefixed_version_number})
            -[:INCLUDES]->(version)-[:CONTAINS]->(class:DataModelClass)-[:CONTAINS]->(scenario:DataModelScenario)-[:CONTAINS]->(variable:DataModelVariable)
        WHERE NOT (:Inconsistency)-[:AFFECTS_VERSION]->(version)
            AND NOT (:Inconsistency)-[:AFFECTS_CLASS]->(class)
            AND NOT (:Inconsistency)-[:AFFECTS_SCENARIO]->(scenario)
            AND NOT (:Inconsistency)-[:AFFECTS_VARIABLE]->(variable)
        RETURN variable, scenario.href AS parent_href, "scenario" AS parent_type
        """,
        catalogue=catalogue,
        prefixed_version_number=prefixed_version_number,
    ).data()
    for item in variables_data:
        item["variable"]["uid"] = sanitize_string(item["variable"]["name"])

    return variables_data


def merge_structure_nodes_and_relationships(
    tx, version_data, classes_data, scenarios_data, variables_data
):
    merge_catalogues_and_versions(tx, version_data)
    merge_version_independent_data(
        tx,
        version_data=version_data,
        classes_data=classes_data,
        scenarios_data=scenarios_data,
        variables_data=variables_data,
    )


def merge_catalogues_and_versions(tx, version_data):
    tx.run(
        """
        MERGE (library:Library{name: 'CDISC'})
        ON CREATE SET library.is_editable = false
        WITH library, $version_data as version_data
        MERGE (catalogue:DataModelCatalogue{name: version_data.catalogue})
        ON CREATE SET catalogue.data_model_type = version_data.data_model_type
        MERGE (library)-[:CONTAINS_CATALOGUE]->(catalogue)
        MERGE (version:DataModelVersion{uid: version_data.uid})
        ON CREATE SET
            version.name = version_data.name,
            version.label = version_data.label,
            version.description = version_data.description,
            version.source = version_data.source,
            version.effective_date = date(version_data.effective_date),
            version.registration_status = version_data.registration_status,
            version.href = version_data.href,
            version.implements_data_model = version_data.implements_data_model,
            
            version.import_date = datetime(),
            version.user_initials = $user_initials
        MERGE (catalogue)-[:CONTAINS_VERSION]->(version)
        """,
        version_data=version_data,
        user_initials=USER_INITIALS,
    )


def merge_version_independent_data(
    tx, version_data, classes_data, scenarios_data, variables_data
):
    data_model_root_label = ""
    contains_model_rel_type = ""
    catalogue_to_model_rel_type = ""
    data_model_uid = ""
    class_root_label = ""
    scenario_root_label = SCENARIO_ROOT_LABEL
    variable_root_label = ""
    catalogue_to_dataset_rel_type = ""
    catalogue_to_variable_rel_type = ""
    catalogue_to_scenario_rel_type = CATALOGUE_TO_SCENARIO_REL_TYPE

    if version_data["data_model_type"] == DataModelType.FOUNDATIONAL.value:
        data_model_root_label = DATA_MODEL_ROOT_LABEL
        class_root_label = CLASS_ROOT_LABEL
        variable_root_label = CLASS_VARIABLE_ROOT_LABEL
        contains_model_rel_type = VERSION_TO_DATA_MODEL_REL_TYPE
        catalogue_to_model_rel_type = CATALOGUE_TO_DATA_MODEL_REL_TYPE
        catalogue_to_dataset_rel_type = CATALOGUE_TO_CLASS_ROOT_REL_TYPE
        catalogue_to_variable_rel_type = CLASS_TO_CLASS_VARIABLE_ROOT_REL_TYPE
        data_model_uid = sanitize_string(version_data["catalogue"])

    elif version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        data_model_root_label = DATA_MODEL_IG_ROOT_LABEL
        class_root_label = DATASET_ROOT_LABEL
        variable_root_label = DATASET_VARIABLE_ROOT_LABEL
        contains_model_rel_type = VERSION_TO_DATA_MODEL_IG_REL_TYPE
        catalogue_to_model_rel_type = CATALOGUE_TO_DATA_MODEL_IG_REL_TYPE
        catalogue_to_dataset_rel_type = CATALOGUE_TO_DATASET_ROOT_REL_TYPE
        catalogue_to_variable_rel_type = CLASS_TO_DATASET_VARIABLE_ROOT_REL_TYPE
        data_model_uid = sanitize_string(parse_ig_name(
            catalogue=version_data["catalogue"], href=version_data["href"]
        ))

    query = f"""
        WITH $version_data as version_data
        MATCH (library:Library{{name: 'CDISC'}})
        MATCH (catalogue:DataModelCatalogue{{name: version_data.catalogue}})
        MATCH (version:DataModelVersion{{uid: version_data.uid}})

        MERGE (dm_root:{data_model_root_label}{{uid: $data_model_uid}})
        MERGE (library)-[:{contains_model_rel_type}]->(dm_root)
        MERGE (catalogue)-[:{catalogue_to_model_rel_type}]->(dm_root)

        WITH catalogue
        UNWIND $classes_data AS class
            MERGE (class_root:{class_root_label}{{uid:class.class.uid}})
            MERGE (catalogue)-[:{catalogue_to_dataset_rel_type}]->(class_root)
        WITH catalogue
        UNWIND $variables_data AS variable
            MERGE (variable_root:{variable_root_label}{{uid:variable.variable.uid}})
            MERGE (catalogue)-[:{catalogue_to_variable_rel_type}]->(variable_root)
        WITH catalogue
        UNWIND $scenarios_data AS scenario
            MERGE (scenario_root:{scenario_root_label}{{uid:scenario.scenario.uid}})
            MERGE (catalogue)-[:{catalogue_to_scenario_rel_type}]->(scenario_root)
    """

    tx.run(
        query,
        version_data=version_data,
        classes_data=classes_data,
        scenarios_data=scenarios_data,
        variables_data=variables_data,
        data_model_uid=data_model_uid,
    )


def merge_data_model(tx, version_data):
    is_foundational = (
        version_data["data_model_type"] == DataModelType.FOUNDATIONAL.value
    )
    data_model_uid = sanitize_string(
        version_data["catalogue"]
        if is_foundational
        else parse_ig_name(
            catalogue=version_data["catalogue"], href=version_data["href"]
        )
    )
    label_prefix = "DataModel" if is_foundational else "DataModelIG"
    root_label = label_prefix + "Root"
    value_label = label_prefix + "Value"
    version_rel_type = (
        "CONTAINS_DATA_MODEL" if is_foundational else "CONTAINS_DATA_MODEL_IG"
    )
    result = tx.run(
        f"""
        MATCH (dm_root:{root_label}{{uid: $data_model_uid}})-[:HAS_VERSION]->(dm_value:{value_label})
        RETURN DISTINCT dm_value.version_number AS version_number
    """,
        data_model_uid=data_model_uid,
    )
    existing_versions = list(result.value())

    prefixed_version_number = _prettify_version_number(version_data["version_number"])
    version_number = _prettify_version_number(version_data["version_number"], number_only=True)
    if prefixed_version_number not in existing_versions:
        # TODO : Check if other status is possible, like Draft
        # First, add end_date to previous LATEST rel
        # And remove all relationships Root->Value not of type HAS_VERSION
        tx.run(
            f"""
            WITH $version_data as version_data
            MATCH (dm_root:{root_label}{{uid: $data_model_uid}})
            MATCH (dm_root)-[r1:HAS_VERSION]->(:{value_label})<-[:LATEST]-(dm_root)
            SET r1.end_date=datetime(version_data.effective_date), r1.change_description="New version imported from CDISC"
            WITH dm_root
            MATCH (dm_root)-[r2]->(:{value_label})
            WHERE NOT type(r2)='HAS_VERSION'
            DELETE r2
        """,
            version_data=version_data,
            data_model_uid=data_model_uid,
        )
        # Then, create new version with relationships
        tx.run(
            f"""
            WITH $version_data as version_data
            MATCH (dm_root:{root_label}{{uid: $data_model_uid}})
            CREATE (dm_value:{value_label})
            SET
                dm_value.name = version_data.name,
                dm_value.description = version_data.description,
                dm_value.version_number = $prefixed_version_number,
                dm_value.effective_date = date(version_data.effective_date)
            CREATE (dm_root)-[:HAS_VERSION {{
                change_description: "Initial import from CDISC",
                start_date: datetime(version_data.effective_date),
                status: version_data.registration_status,
                user_initials: $user_initials,
                version: $version_number
            }}]->(dm_value)
            CREATE (dm_root)-[:LATEST_FINAL]->(dm_value)
            CREATE (dm_root)-[:LATEST]->(dm_value)
            WITH dm_value, version_data
            MATCH (v:DataModelVersion {{uid: version_data.uid}})
            CREATE (v)-[:{version_rel_type}]->(dm_value)
        """,
            data_model_uid=data_model_uid,
            version_data=version_data,
            version_number=version_number,
            prefixed_version_number=prefixed_version_number,
            user_initials=USER_INITIALS,
        )

    if not is_foundational:
        link_ig_with_data_model(tx, version_data)


def _get_latest_class_version(tx, catalogue, data_model_type, uid):
    model_root_label = ""
    model_value_label = ""
    class_root_label = ""
    catalogue_to_class_rel_type = ""
    if data_model_type == DataModelType.FOUNDATIONAL.value:
        model_root_label = DATA_MODEL_ROOT_LABEL
        model_value_label = DATA_MODEL_VALUE_LABEL
        class_root_label = CLASS_ROOT_LABEL
        catalogue_to_class_rel_type = CATALOGUE_TO_CLASS_ROOT_REL_TYPE
    elif data_model_type == DataModelType.IMPLEMENTATION.value:
        model_root_label = DATA_MODEL_IG_ROOT_LABEL
        model_value_label = DATA_MODEL_IG_VALUE_LABEL
        class_root_label = DATASET_ROOT_LABEL
        catalogue_to_class_rel_type = CATALOGUE_TO_DATASET_ROOT_REL_TYPE
    result = tx.run(
        f"""
                MATCH (catalogue:DataModelCatalogue {{name: $catalogue}})
                    -[:{catalogue_to_class_rel_type}]->(:{class_root_label}{{uid: $uid}})
                    -[:LATEST]->(value)<--(:{model_value_label})<--(:{model_root_label})<--(catalogue)
                RETURN DISTINCT value
                """,
        uid=uid,
        catalogue=catalogue,
    )
    record = result.single()

    return record


def _get_latest_scenario_version(tx, catalogue, data_model_type, uid):
    model_root_label = ""
    model_value_label = ""
    class_value_label = ""
    scenario_root_label = SCENARIO_ROOT_LABEL
    catalogue_to_scenario_rel_type = CATALOGUE_TO_SCENARIO_REL_TYPE
    if data_model_type == DataModelType.FOUNDATIONAL.value:
        model_root_label = DATA_MODEL_ROOT_LABEL
        model_value_label = DATA_MODEL_VALUE_LABEL
        class_value_label = CLASS_VALUE_LABEL
    elif data_model_type == DataModelType.IMPLEMENTATION.value:
        model_root_label = DATA_MODEL_IG_ROOT_LABEL
        model_value_label = DATA_MODEL_IG_VALUE_LABEL
        class_value_label = DATASET_VALUE_LABEL
    result = tx.run(
        f"""
                MATCH (catalogue:DataModelCatalogue {{name: $catalogue}})
                    -[:{catalogue_to_scenario_rel_type}]->(:{scenario_root_label}{{uid: $uid}})
                    -[:LATEST]->(value)
                    <--(:{class_value_label})
                    <--(:{model_value_label})<--(:{model_root_label})<--(catalogue)
                RETURN DISTINCT value
                """,
        uid=uid,
        catalogue=catalogue,
    )
    record = result.single()

    return record


def _get_latest_variable_version(tx, catalogue, data_model_type, parent_type, uid):
    model_root_label = ""
    model_value_label = ""
    class_value_label = ""
    scenario_value_label = SCENARIO_VALUE_LABEL
    variable_root_label = ""
    scenario_variable_value_label = SCENARIO_VARIABLE_VALUE_LABEL
    catalogue_to_variable_rel_type = ""
    class_to_variable_rel_type = ""
    class_to_scenario_rel_type = CLASS_TO_SCENARIO_REL_TYPE
    scenario_to_variable_rel_type = SCENARIO_TO_VARIABLE_REL_TYPE
    variable_to_scenario_variable_rel_type = VARIABLE_TO_SCENARIO_VARIABLE_REL_TYPE
    scenario_variable_to_scenario_rel_type = SCENARIO_VARIABLE_TO_SCENARIO_REL_TYPE
    if data_model_type == DataModelType.FOUNDATIONAL.value:
        model_root_label = DATA_MODEL_ROOT_LABEL
        model_value_label = DATA_MODEL_VALUE_LABEL
        class_value_label = CLASS_VALUE_LABEL
        variable_root_label = CLASS_VARIABLE_ROOT_LABEL
        catalogue_to_variable_rel_type = CATALOGUE_TO_CLASS_VARIABLE_ROOT_REL_TYPE
        class_to_variable_rel_type = CLASS_TO_CLASS_VARIABLE_ROOT_REL_TYPE
    elif data_model_type == DataModelType.IMPLEMENTATION.value:
        model_root_label = DATA_MODEL_IG_ROOT_LABEL
        model_value_label = DATA_MODEL_IG_VALUE_LABEL
        class_value_label = DATASET_VALUE_LABEL
        variable_root_label = DATASET_VARIABLE_ROOT_LABEL
        catalogue_to_variable_rel_type = CATALOGUE_TO_DATASET_VARIABLE_ROOT_REL_TYPE
        class_to_variable_rel_type = CLASS_TO_DATASET_VARIABLE_ROOT_REL_TYPE

    query = ""

    if parent_type == "class":
        query = f"""
            MATCH (catalogue:DataModelCatalogue {{name: $catalogue}})
                -[:{catalogue_to_variable_rel_type}]->(:{variable_root_label}{{uid: $uid}})
                -[:LATEST]->(value)
                <-[:{class_to_variable_rel_type}]-(:{class_value_label})
                <--(:{model_value_label})<--(:{model_root_label})<--(catalogue)
            RETURN DISTINCT value
        """
    elif parent_type == "scenario":
        query = f"""
            MATCH (catalogue:DataModelCatalogue {{name: $catalogue}})
                -[:{catalogue_to_variable_rel_type}]->(:{variable_root_label}{{uid: $uid}})
                -[:LATEST]->(value)
                <-[:{scenario_to_variable_rel_type}]-(scenario:{scenario_value_label})<-[:{class_to_scenario_rel_type}]-(:{class_value_label})
                <--(:{model_value_label})<--(:{model_root_label})<--(catalogue)
            MATCH (scenario)<-[:{scenario_variable_to_scenario_rel_type}]-(impl:{scenario_variable_value_label})
                <-[:{variable_to_scenario_variable_rel_type}]-(value)
            RETURN DISTINCT apoc.map.mergeList([{{id: id(value)}}, value{{.*}}, impl{{.*}}]) AS value
        """
    result = tx.run(
        query,
        uid=uid,
        catalogue=catalogue,
    )
    record = result.single()

    return record


def merge_classes(tx, version_data, classes_data):
    nbr_unchanged = 0
    nbr_updated = 0
    nbr_new = 0
    for class_data in classes_data:
        _class = class_data.get("class", None)

        record = _get_latest_class_version(
            tx,
            catalogue=version_data["catalogue"],
            data_model_type=version_data["data_model_type"],
            uid=_class["uid"],
        )
        if record is None:
            create_initial_class_value(tx, version_data, _class)
            nbr_new += 1
        else:
            value = record["value"]

            if (
                value.get("title", None) != _class.get("title", None)
                or value.get("label", None) != _class.get("label", None)
                or value.get("description", None) != _class.get("description", None)
            ):
                create_new_version_class(tx, version_data, _class, value.id)
                nbr_updated += 1

            else:
                use_existing_version_class(tx, version_data, _class, value.id)
                nbr_unchanged += 1
    for class_data in [
        c["class"]
        for c in classes_data
        if c["class"]["subclasses"] is not None and len(c["class"]["subclasses"]) > 0
    ]:
        link_class_with_subclasses(
            tx,
            _class=class_data,
            subclasses=class_data.get("subclasses", []),
            prefixed_version_number=_prettify_version_number(version_data["version_number"]),
        )
    return nbr_new, nbr_updated, nbr_unchanged


def merge_scenarios(tx, version_data, scenarios_data):
    nbr_unchanged = 0
    nbr_updated = 0
    nbr_new = 0
    for scenario_data in scenarios_data:
        scenario = scenario_data.get("scenario", None)
        dataset_href = scenario_data.get("dataset_href", None)

        record = _get_latest_scenario_version(
            tx,
            catalogue=version_data["catalogue"],
            data_model_type=version_data["data_model_type"],
            uid=scenario["uid"],
        )
        if record is None:
            create_initial_scenario_value(tx, version_data, scenario, dataset_href)
            nbr_new += 1
        else:
            value = record["value"]

            if value.get("label", None) != scenario.get("label", None):
                create_new_version_scenario(
                    tx, version_data, scenario, dataset_href, value.id
                )
                nbr_updated += 1
            else:
                use_existing_version_scenario(
                    tx, version_data, scenario, dataset_href, value.id
                )
                nbr_unchanged += 1
    return nbr_new, nbr_updated, nbr_unchanged


def merge_variables(tx, version_data, variables_data):
    nbr_unchanged = 0
    nbr_updated = 0
    nbr_new = 0
    for variable_data in variables_data:
        variable = variable_data.get("variable", None)
        parent_href = variable_data.get("parent_href", None)
        parent_type = variable_data.get("parent_type", None)

        # TODO : First check if VariableValue has a changed property - property set is different for class and scenario
        # But then, how to detect if implementation changed ? Probably need to check if latest and new have an implementation linked to same Scenario
        # If so, re-use or create new one depending on changes
        # If not, then crearte new implementation
        record = _get_latest_variable_version(
            tx,
            catalogue=version_data["catalogue"],
            data_model_type=version_data["data_model_type"],
            parent_type=parent_type,
            uid=variable["uid"],
        )
        if record is None:
            create_initial_variable_value(
                tx,
                version_data=version_data,
                variable=variable,
                parent_href=parent_href,
                parent_type=parent_type,
            )
            nbr_new += 1
        else:
            value = record["value"]
            latest_version_id = (
                value.id if hasattr(value, "id") else value.get("id", None)
            )
            if (
                value.get("title", None) != variable.get("title", None)
                or value.get("label", None) != variable.get("label", None)
                or value.get("description", None) != variable.get("description", None)
                or value.get("role", None) != variable.get("role", None)
                or value.get("role_description", None)
                != variable.get("role_description", None)
                or value.get("simple_datatype", None)
                != variable.get("simple_datatype", None)
                or value.get("implementation_notes", None)
                != variable.get("implementation_notes", None)
                or value.get("mapping_instructions", None)
                != variable.get("mapping_instructions", None)
                or value.get("prompt", None) != variable.get("prompt", None)
                or value.get("question_text", None)
                != variable.get("question_text", None)
                or value.get("completion_instructions", None)
                != variable.get("completion_instructions", None)
                or value.get("core", None) != variable.get("core", None)
            ):
                create_new_version_variable(
                    tx,
                    version_data=version_data,
                    variable=variable,
                    parent_href=parent_href,
                    latest_version_id=latest_version_id,
                    parent_type=parent_type,
                )
                nbr_updated += 1

            else:
                use_existing_version_variable(
                    tx,
                    version_data=version_data,
                    variable=variable,
                    parent_href=parent_href,
                    latest_version_id=latest_version_id,
                    parent_type=parent_type,
                )
                nbr_unchanged += 1
    return nbr_new, nbr_updated, nbr_unchanged


def create_initial_class_value(tx, version_data, _class):
    model_value_label = ""
    class_root_label = ""
    class_value_label = ""
    model_to_class_rel_type = ""
    version_to_model_rel_type = ""
    version_to_class_rel_type = ""
    prefixed_version_number = _prettify_version_number(version_data["version_number"])
    if version_data["data_model_type"] == DataModelType.FOUNDATIONAL.value:
        model_value_label = DATA_MODEL_VALUE_LABEL
        class_root_label = CLASS_ROOT_LABEL
        class_value_label = CLASS_VALUE_LABEL
        model_to_class_rel_type = CATALOGUE_TO_CLASS_ROOT_REL_TYPE
        version_to_model_rel_type = VERSION_TO_DATA_MODEL_REL_TYPE
        version_to_class_rel_type = VERSION_TO_CLASS_REL_TYPE
    elif version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        model_value_label = DATA_MODEL_IG_VALUE_LABEL
        class_root_label = DATASET_ROOT_LABEL
        class_value_label = DATASET_VALUE_LABEL
        model_to_class_rel_type = CATALOGUE_TO_DATASET_ROOT_REL_TYPE
        version_to_model_rel_type = VERSION_TO_DATA_MODEL_IG_REL_TYPE
        version_to_class_rel_type = VERSION_TO_DATASET_REL_TYPE

    # TODO use a new relationship type instead of HAS_VERSION, and remove LATEST&LATEST_FINAL?
    tx.run(
        f"""
            MATCH (root:{class_root_label}{{uid: $uid}})
            CREATE (value: {class_value_label})
            SET
               value.title = $class_data.title,
               value.label = $class_data.label,
               value.description = $class_data.description
            CREATE (root)-[:LATEST]->(value)
            CREATE (root)-[:LATEST_FINAL]->(value)
            CREATE (root)-[:HAS_VERSION{{
                start_date: datetime($effective_date),
                status: 'Final',
                change_description: 'Imported from CDISC',
                user_initials: $user_initials
            }}]->(value)

            WITH value
            MATCH (dmv:DataModelVersion {{href: $version_href}})-[{version_to_model_rel_type}]->(model_value:{model_value_label})
            MERGE (dmv)-[contains_class:{version_to_class_rel_type}]->(value)
            MERGE (model_value)-[has_class:{model_to_class_rel_type}]->(value)
            SET contains_class.href=$class_data.href, has_class.ordinal = $class_data.ordinal

            WITH value
            MATCH ()-[rel]->(prior_value_node)<-[:HAS_VERSION]-(prior_root_node)
            WHERE rel.href=$class_data.prior_version AND (rel:{VERSION_TO_CLASS_REL_TYPE} OR rel:{VERSION_TO_DATASET_REL_TYPE})
            CALL apoc.do.when($uid<>prior_root_node.uid,
                'WITH $value AS value, $prior_value_node AS prior_value_node CREATE (value)<-[rep:REPLACED_BY]-(prior_value_node) SET rep.catalogue=$catalogue, rep.version_number=$prefixed_version_number RETURN rep',
                '',
                {{prior_value_node: prior_value_node, value: value, catalogue: $class_data.catalogue, prefixed_version_number: $prefixed_version_number}}
            )
            YIELD value AS result
            RETURN result
        """,
        uid=_class["uid"],
        effective_date=version_data["effective_date"],
        class_data=_class,
        version_href=version_data["href"],
        prefixed_version_number=prefixed_version_number,
        user_initials=USER_INITIALS,
    )

    if version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        link_dataset_with_class(tx, _class, prefixed_version_number)


def create_new_version_class(tx, version_data, _class, latest_version_id):
    model_value_label = ""
    class_value_label = ""
    model_to_class_rel_type = ""
    version_to_model_rel_type = ""
    version_to_class_rel_type = ""
    prefixed_version_number = _prettify_version_number(version_data["version_number"])
    if version_data["data_model_type"] == DataModelType.FOUNDATIONAL.value:
        model_value_label = DATA_MODEL_VALUE_LABEL
        class_value_label = CLASS_VALUE_LABEL
        model_to_class_rel_type = CATALOGUE_TO_CLASS_ROOT_REL_TYPE
        version_to_model_rel_type = VERSION_TO_DATA_MODEL_REL_TYPE
        version_to_class_rel_type = VERSION_TO_CLASS_REL_TYPE
    elif version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        model_value_label = DATA_MODEL_IG_VALUE_LABEL
        class_value_label = DATASET_VALUE_LABEL
        model_to_class_rel_type = CATALOGUE_TO_DATASET_ROOT_REL_TYPE
        version_to_model_rel_type = VERSION_TO_DATA_MODEL_IG_REL_TYPE
        version_to_class_rel_type = VERSION_TO_DATASET_REL_TYPE
    # TODO use a new relationship type instead of HAS_VERSION, and remove LATEST&LATEST_FINAL?
    tx.run(
        f"""
            MATCH (root{{uid: $uid}})-[latest:LATEST]->(value)
                <-[latest_final:LATEST_FINAL]-(root)
            WHERE id(value)=$latest_version_id
            MATCH (root)-[has_version:HAS_VERSION]->(value)
            SET has_version.end_date = datetime($effective_date)
            DELETE latest, latest_final

            WITH root, has_version.version AS version
            CREATE (new_value: {class_value_label})
            SET
               new_value.title = $class_data.title,
               new_value.label = $class_data.label,
               new_value.description = $class_data.description
            CREATE (root)-[:LATEST]->(new_value)
            CREATE (root)-[:LATEST_FINAL]->(new_value)
            CREATE (root)-[:HAS_VERSION{{
                start_date: datetime($effective_date),
                status: 'Final',
                change_description: 'Imported from CDISC',
                user_initials: $user_initials
            }}]->(new_value)

            WITH new_value
            MATCH (dmv:DataModelVersion {{href: $version_href}})-[{version_to_model_rel_type}]->(model_value:{model_value_label})
            MERGE (dmv)-[contains_class:{version_to_class_rel_type}]->(new_value)
            CREATE (model_value)-[has_class:{model_to_class_rel_type}]->(new_value)
            SET contains_class.href=$class_data.href, has_class.ordinal = $class_data.ordinal

            WITH new_value
            MATCH ()-[rel]->(prior_value_node)<-[:HAS_VERSION]-(prior_root_node)
            WHERE rel.href=$class_data.prior_version AND (rel:{VERSION_TO_CLASS_REL_TYPE} OR rel:{VERSION_TO_DATASET_REL_TYPE})
            CALL apoc.do.when($uid<>prior_root_node.uid,
                'WITH $new_value AS new_value, $prior_value_node AS prior_value_node CREATE (new_value)<-[rep:REPLACED_BY]-(prior_value_node) SET rep.catalogue=$catalogue, rep.version_number=$prefixed_version_number RETURN rep',
                '',
                {{prior_value_node: prior_value_node, new_value: new_value, catalogue: $class_data.catalogue, prefixed_version_number: $prefixed_version_number}}
            )
            YIELD value AS result
            RETURN result
        """,
        uid=_class["uid"],
        latest_version_id=latest_version_id,
        effective_date=version_data["effective_date"],
        class_data=_class,
        version_href=version_data["href"],
        prefixed_version_number=prefixed_version_number,
        user_initials=USER_INITIALS,
    )

    if version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        link_dataset_with_class(tx, _class, prefixed_version_number)


def use_existing_version_class(tx, version_data, _class, latest_version_id):
    model_value_label = ""
    model_to_class_rel_type = ""
    version_to_model_rel_type = ""
    version_to_class_rel_type = ""
    prefixed_version_number = _prettify_version_number(version_data["version_number"])
    if version_data["data_model_type"] == DataModelType.FOUNDATIONAL.value:
        model_value_label = DATA_MODEL_VALUE_LABEL
        model_to_class_rel_type = CATALOGUE_TO_CLASS_ROOT_REL_TYPE
        version_to_model_rel_type = VERSION_TO_DATA_MODEL_REL_TYPE
        version_to_class_rel_type = VERSION_TO_CLASS_REL_TYPE
    elif version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        model_value_label = DATA_MODEL_IG_VALUE_LABEL
        model_to_class_rel_type = CATALOGUE_TO_DATASET_ROOT_REL_TYPE
        version_to_model_rel_type = VERSION_TO_DATA_MODEL_IG_REL_TYPE
        version_to_class_rel_type = VERSION_TO_DATASET_REL_TYPE
    tx.run(
        f"""
            MATCH (value)
            WHERE id(value)=$latest_version_id
            MATCH (dmv:DataModelVersion {{href: $version_href}})-[{version_to_model_rel_type}]->(model_value:{model_value_label})
            MERGE (dmv)-[contains_class:{version_to_class_rel_type}]->(value)
            CREATE (model_value)-[has_class:{model_to_class_rel_type}]->(value)
            SET contains_class.href=$class_data.href, has_class.ordinal = $class_data.ordinal

            WITH value
            MATCH ()-[rel]->(prior_value_node)<-[:HAS_VERSION]-(prior_root_node)
            WHERE rel.href=$class_data.prior_version AND (rel:{VERSION_TO_CLASS_REL_TYPE} OR rel:{VERSION_TO_DATASET_REL_TYPE})
            CALL apoc.do.when($uid<>prior_root_node.uid,
                'WITH $value AS value, $prior_value_node AS prior_value_node CREATE (value)<-[rep:REPLACED_BY]-(prior_value_node) SET rep.catalogue=$catalogue, rep.version_number=$prefixed_version_number RETURN rep',
                '',
                {{prior_value_node: prior_value_node, value: value, catalogue: $class_data.catalogue, prefixed_version_number: $prefixed_version_number}}
            )
            YIELD value AS result
            RETURN result
        """,
        uid=_class["uid"],
        latest_version_id=latest_version_id,
        class_data=_class,
        version_href=version_data["href"],
        prefixed_version_number=prefixed_version_number,
    )

    if version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        link_dataset_with_class(tx, _class, prefixed_version_number)


def create_initial_scenario_value(tx, version_data, scenario, dataset_href):
    prefixed_version_number = _prettify_version_number(version_data["version_number"])
    class_value_label = ""
    scenario_root_label = SCENARIO_ROOT_LABEL
    scenario_value_label = SCENARIO_VALUE_LABEL
    class_to_scenario_rel_type = CLASS_TO_SCENARIO_REL_TYPE
    version_to_class_rel_type = ""
    version_to_scenario_rel_type = VERSION_TO_SCENARIO_REL_TYPE
    if version_data["data_model_type"] == DataModelType.FOUNDATIONAL.value:
        class_value_label = CLASS_VALUE_LABEL
        version_to_class_rel_type = VERSION_TO_CLASS_REL_TYPE
    elif version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        class_value_label = DATASET_VALUE_LABEL
        version_to_class_rel_type = VERSION_TO_DATASET_REL_TYPE

    # TODO use a new relationship type instead of HAS_VERSION, and remove LATEST&LATEST_FINAL?
    tx.run(
        f"""
            MATCH (root:{scenario_root_label}{{uid: $uid}})
            CREATE (value:{scenario_value_label})
            SET
               value.label = $scenario_data.label
            CREATE (root)-[:LATEST]->(value)
            CREATE (root)-[:LATEST_FINAL]->(value)
            CREATE (root)-[:HAS_VERSION{{
                start_date: datetime($effective_date),
                status: 'Final',
                change_description: 'Imported from CDISC',
                user_initials: $user_initials
            }}]->(value)

            WITH value
            MATCH (dmv:DataModelVersion {{href: $version_href}})-[rel:{version_to_class_rel_type}]->(class_value:{class_value_label})
                WHERE rel.href=$dataset_href
            MERGE (dmv)-[contains_scenario:{version_to_scenario_rel_type} {{href: $scenario_data.href}}]->(value)
            MERGE (class_value)-[has_scenario:{class_to_scenario_rel_type}]->(value)
            SET contains_scenario.href=$scenario_data.href, has_scenario.ordinal = $scenario_data.ordinal, has_scenario.version_number = $prefixed_version_number
        """,
        uid=scenario["uid"],
        effective_date=version_data["effective_date"],
        prefixed_version_number=prefixed_version_number,
        scenario_data=scenario,
        version_href=version_data["href"],
        dataset_href=dataset_href,
        user_initials=USER_INITIALS,
    )


def create_new_version_scenario(
    tx, version_data, scenario, dataset_href, latest_version_id
):
    prefixed_version_number = _prettify_version_number(version_data["version_number"])
    class_value_label = ""
    scenario_value_label = SCENARIO_VALUE_LABEL
    class_to_scenario_rel_type = CLASS_TO_SCENARIO_REL_TYPE
    version_to_class_rel_type = ""
    version_to_scenario_rel_type = VERSION_TO_SCENARIO_REL_TYPE
    if version_data["data_model_type"] == DataModelType.FOUNDATIONAL.value:
        class_value_label = CLASS_VALUE_LABEL
        version_to_class_rel_type = VERSION_TO_CLASS_REL_TYPE
    elif version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        class_value_label = DATASET_VALUE_LABEL
        version_to_class_rel_type = VERSION_TO_DATASET_REL_TYPE

    # TODO use a new relationship type instead of HAS_VERSION, and remove LATEST&LATEST_FINAL?
    tx.run(
        f"""
        MATCH (root{{uid: $uid}})-[latest:LATEST]->(value)
            <-[latest_final:LATEST_FINAL]-(root)
        WHERE id(value)=$latest_version_id
        MATCH (root)-[has_version:HAS_VERSION]->(value)
        SET has_version.end_date = datetime($effective_date)
        DELETE latest, latest_final

        WITH root, has_version.version AS version
        CREATE (new_value: {scenario_value_label})
        SET
            new_value.label = $scenario_data.label
        CREATE (root)-[:LATEST]->(new_value)
        CREATE (root)-[:LATEST_FINAL]->(new_value)
        CREATE (root)-[:HAS_VERSION{{
            start_date: datetime($effective_date),
            status: 'Final',
            change_description: 'Imported from CDISC',
            user_initials: $user_initials
        }}]->(new_value)

        WITH new_value
        MATCH (dmv:DataModelVersion {{href: $version_href}})-[rel:{version_to_class_rel_type}]->(class_value:{class_value_label})
            WHERE rel.href=$dataset_href
        MERGE (dmv)-[contains_scenario:{version_to_scenario_rel_type} {{href: $scenario_data.href}}]->(new_value)
        CREATE (class_value)-[has_scenario:{class_to_scenario_rel_type}]->(new_value)
        SET contains_scenario.href=$scenario_data.href, has_scenario.ordinal = $scenario_data.ordinal, has_scenario.version_number = $prefixed_version_number
        """,
        uid=scenario["uid"],
        latest_version_id=latest_version_id,
        effective_date=version_data["effective_date"],
        prefixed_version_number=prefixed_version_number,
        scenario_data=scenario,
        version_href=version_data["href"],
        dataset_href=dataset_href,
        user_initials=USER_INITIALS,
    )


def use_existing_version_scenario(
    tx, version_data, scenario, dataset_href, latest_version_id
):
    prefixed_version_number = _prettify_version_number(version_data["version_number"])
    class_value_label = ""
    class_to_scenario_rel_type = CLASS_TO_SCENARIO_REL_TYPE
    version_to_class_rel_type = ""
    version_to_scenario_rel_type = VERSION_TO_SCENARIO_REL_TYPE
    if version_data["data_model_type"] == DataModelType.FOUNDATIONAL.value:
        class_value_label = CLASS_VALUE_LABEL
        version_to_class_rel_type = VERSION_TO_CLASS_REL_TYPE
    elif version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        class_value_label = DATASET_VALUE_LABEL
        version_to_class_rel_type = VERSION_TO_DATASET_REL_TYPE

    tx.run(
        f"""
        MATCH (value)
        WHERE id(value)=$latest_version_id
        MATCH (dmv:DataModelVersion {{href: $version_href}})-[rel:{version_to_class_rel_type}]->(class_value:{class_value_label})
            WHERE rel.href=$dataset_href
        MERGE (dmv)-[:{version_to_scenario_rel_type} {{href: $scenario_data.href}}]->(value)
        CREATE (class_value)-[has_scenario:{class_to_scenario_rel_type}]->(value)
        SET has_scenario.ordinal = $scenario_data.ordinal, has_scenario.version_number = $prefixed_version_number
        """,
        uid=scenario["uid"],
        latest_version_id=latest_version_id,
        effective_date=version_data["effective_date"],
        prefixed_version_number=prefixed_version_number,
        scenario_data=scenario,
        version_href=version_data["href"],
        dataset_href=dataset_href,
    )


def build_version_query(
    value_node_variable_name: str,
    parent_type: str,
    version_data: dict,
    create_version: bool = True,
):
    class_value_label = ""
    scenario_value_label = SCENARIO_VALUE_LABEL
    variable_value_label = ""
    scenario_variable_value_label = SCENARIO_VARIABLE_VALUE_LABEL
    variable_value_to_scenario_variable_value_rel_type = (
        VARIABLE_TO_SCENARIO_VARIABLE_REL_TYPE
    )
    class_to_variable_rel_type = ""
    scenario_to_variable_rel_type = SCENARIO_TO_VARIABLE_REL_TYPE
    version_to_class_rel_type = ""
    version_to_scenario_rel_type = VERSION_TO_SCENARIO_REL_TYPE
    version_to_variable_rel_type = ""
    version_to_scenario_variable_rel_type = VERSION_TO_SCENARIO_VARIABLE_REL_TYPE
    scenario_variable_to_scenario_rel_type = SCENARIO_VARIABLE_TO_SCENARIO_REL_TYPE
    if version_data["data_model_type"] == DataModelType.FOUNDATIONAL.value:
        class_value_label = CLASS_VALUE_LABEL
        variable_value_label = CLASS_VARIABLE_VALUE_LABEL
        class_to_variable_rel_type = CLASS_TO_CLASS_VARIABLE_ROOT_REL_TYPE
        version_to_class_rel_type = VERSION_TO_CLASS_REL_TYPE
        version_to_variable_rel_type = VERSION_TO_CLASS_VARIABLE_REL_TYPE
    elif version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        class_value_label = DATASET_VALUE_LABEL
        variable_value_label = DATASET_VARIABLE_VALUE_LABEL
        class_to_variable_rel_type = CLASS_TO_DATASET_VARIABLE_ROOT_REL_TYPE
        version_to_class_rel_type = VERSION_TO_DATASET_REL_TYPE
        version_to_variable_rel_type = VERSION_TO_DATASET_VARIABLE_REL_TYPE

    create = f"""
            CREATE ({value_node_variable_name}:{variable_value_label})
            SET
               {value_node_variable_name}.title = $variable_data.title,
               {value_node_variable_name}.label = $variable_data.label,
               {value_node_variable_name}.simple_datatype = $variable_data.simple_datatype
    """
    with_clause = f" WITH {value_node_variable_name} "

    # TODO use a new relationship type instead of HAS_VERSION, and remove LATEST&LATEST_FINAL?
    versioning = f"""
        , root
        CREATE (root)-[:LATEST]->({value_node_variable_name})
        CREATE (root)-[:LATEST_FINAL]->({value_node_variable_name})
        CREATE (root)-[:HAS_VERSION{{
            start_date: datetime($effective_date),
            status: 'Final',
            change_description: 'Imported from CDISC',
            user_initials: $user_initials
        }}]->({value_node_variable_name})
    """

    variable_parents = ""

    codelists = """
        UNWIND $variable_data.codelists AS codelist
        MATCH (c:CTCodelistRoot {uid: codelist})
    """

    prior_version = f"""
        MATCH ()-[rel]->(prior_value_node)<-[:HAS_VERSION]-(prior_root_node)
        WHERE rel.href=$variable_data.prior_version AND (rel:{VERSION_TO_CLASS_VARIABLE_REL_TYPE} OR rel:{VERSION_TO_DATASET_VARIABLE_REL_TYPE})
        CALL apoc.do.when($uid<>prior_root_node.uid,
            'WITH ${value_node_variable_name} AS {value_node_variable_name}, $prior_value_node AS prior_value_node CREATE ({value_node_variable_name})<-[rep:REPLACED_BY]-(prior_value_node) SET rep.catalogue=$catalogue, rep.version_number=$prefixed_version_number RETURN rep',
            '',
            {{prior_value_node: prior_value_node, {value_node_variable_name}: {value_node_variable_name}, catalogue: $variable_data.catalogue, prefixed_version_number: $prefixed_version_number}}
        )
        YIELD value AS result
        RETURN result
    """

    if parent_type == "class":
        create += f""",
               {value_node_variable_name}.description = $variable_data.description,
               {value_node_variable_name}.role = $variable_data.role,
               {value_node_variable_name}.role_description = $variable_data.role_description,
               {value_node_variable_name}.implementation_notes = $variable_data.implementation_notes,
               {value_node_variable_name}.mapping_instructions = $variable_data.mapping_instructions,
               {value_node_variable_name}.prompt = $variable_data.prompt,
               {value_node_variable_name}.question_text = $variable_data.question_text,
               {value_node_variable_name}.completion_instructions = $variable_data.completion_instructions,
               {value_node_variable_name}.core = $variable_data.core
        """

        variable_parents = f"""
            MATCH (dmv:DataModelVersion {{href: $version_href}})-[rel:{version_to_class_rel_type}]->(class_value:{class_value_label})
                WHERE rel.href=$parent_href
            MERGE (dmv)-[:{version_to_variable_rel_type} {{href: $variable_data.href}}]->({value_node_variable_name})
            MERGE (class_value)-[has_variable:{class_to_variable_rel_type} {{
                ordinal: $variable_data.ordinal,
                version_number: $prefixed_version_number
            }}]->({value_node_variable_name})
        """

        codelists += f"""
            MERGE ({value_node_variable_name})-[:REFERENCES_CODELIST]->(c)
        """

    elif parent_type == "scenario":
        scenario_value_variable_name = "scenario_variable_value"
        create += f"""
            CREATE ({scenario_value_variable_name}:{scenario_variable_value_label})
            SET
               {scenario_value_variable_name}.description = $variable_data.description,
               {scenario_value_variable_name}.role = $variable_data.role,
               {scenario_value_variable_name}.role_description = $variable_data.role_description,
               {scenario_value_variable_name}.implementation_notes = $variable_data.implementation_notes,
               {scenario_value_variable_name}.mapping_instructions = $variable_data.mapping_instructions,
               {scenario_value_variable_name}.prompt = $variable_data.prompt,
               {scenario_value_variable_name}.question_text = $variable_data.question_text,
               {scenario_value_variable_name}.completion_instructions = $variable_data.completion_instructions,
               {scenario_value_variable_name}.core = $variable_data.core
            CREATE ({value_node_variable_name})-[var_sc_rel:{variable_value_to_scenario_variable_value_rel_type}]->({scenario_value_variable_name})
            SET var_sc_rel.version_number = $prefixed_version_number
        """

        variable_parents = f"""
            MATCH (dmv:DataModelVersion {{href: $version_href}})-[rel:{version_to_scenario_rel_type}]->(scenario_value:{scenario_value_label})
                WHERE rel.href=$parent_href
            MERGE (dmv)-[:{version_to_variable_rel_type} {{href: $variable_data.href}}]->({value_node_variable_name})
            MERGE (scenario_value)-[has_variable:{scenario_to_variable_rel_type} {{
                ordinal: $variable_data.ordinal,
                version_number: $prefixed_version_number
            }}]->({value_node_variable_name})
            MERGE (dmv)-[contains_scenario_variable:{version_to_scenario_variable_rel_type}]->({scenario_value_variable_name})
            MERGE ({scenario_value_variable_name})-[:{scenario_variable_to_scenario_rel_type}]->(scenario_value)
        """

        codelists += f"""
            MERGE ({scenario_value_variable_name})-[:REFERENCES_CODELIST]->(c)
        """

        with_clause += f", {scenario_value_variable_name}"

    if create_version is True:
        full_query = with_clause.join(
            [create, versioning, variable_parents, codelists, prior_version]
        )
    else:
        full_query = with_clause.join([variable_parents, prior_version])

    return full_query


def create_initial_variable_value(tx, version_data, variable, parent_href, parent_type):
    prefixed_version_number = _prettify_version_number(version_data["version_number"])
    variable_root_label = ""
    if version_data["data_model_type"] == DataModelType.FOUNDATIONAL.value:
        variable_root_label = CLASS_VARIABLE_ROOT_LABEL
    elif version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        variable_root_label = DATASET_VARIABLE_ROOT_LABEL

    initial_part = f"""
        MATCH (root:{variable_root_label}{{uid: $uid}})
        WITH root
    """

    full_query = initial_part + build_version_query(
        value_node_variable_name="value",
        parent_type=parent_type,
        version_data=version_data,
    )

    tx.run(
        full_query,
        uid=variable["uid"],
        effective_date=version_data["effective_date"],
        prefixed_version_number=prefixed_version_number,
        variable_data=variable,
        version_href=version_data["href"],
        parent_href=parent_href,
        user_initials=USER_INITIALS,
    )

    if version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        link_variable_with_variable(tx, version_data, variable, prefixed_version_number)


def create_new_version_variable(
    tx, version_data, variable, parent_href, latest_version_id, parent_type
):
    prefixed_version_number = _prettify_version_number(version_data["version_number"])

    initial_part = """
        MATCH (root{uid: $uid})-[latest:LATEST]->(value)
            <-[latest_final:LATEST_FINAL]-(root)
        WHERE id(value)=$latest_version_id
        MATCH (root)-[has_version:HAS_VERSION]->(value)
        SET has_version.end_date = datetime($effective_date)
        DELETE latest, latest_final

        WITH root
    """

    full_query = initial_part + build_version_query(
        value_node_variable_name="new_value",
        parent_type=parent_type,
        version_data=version_data,
    )
    tx.run(
        full_query,
        uid=variable["uid"],
        latest_version_id=latest_version_id,
        effective_date=version_data["effective_date"],
        prefixed_version_number=prefixed_version_number,
        variable_data=variable,
        version_href=version_data["href"],
        parent_href=parent_href,
        user_initials=USER_INITIALS,
    )

    if version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        link_variable_with_variable(tx, version_data, variable, prefixed_version_number)


def use_existing_version_variable(
    tx, version_data, variable, parent_href, latest_version_id, parent_type
):
    prefixed_version_number = _prettify_version_number(version_data["version_number"])

    initial_part = """
        MATCH (value)
        WHERE id(value)=$latest_version_id
    """

    full_query = initial_part + build_version_query(
        value_node_variable_name="value",
        parent_type=parent_type,
        create_version=False,
        version_data=version_data,
    )

    tx.run(
        full_query,
        uid=variable["uid"],
        latest_version_id=latest_version_id,
        effective_date=version_data["effective_date"],
        prefixed_version_number=prefixed_version_number,
        variable_data=variable,
        version_href=version_data["href"],
        parent_href=parent_href,
    )

    if version_data["data_model_type"] == DataModelType.IMPLEMENTATION.value:
        link_variable_with_variable(tx, version_data, variable, prefixed_version_number)


def link_ig_with_data_model(tx, version_data):
    tx.run(
        """
        MATCH (ig:DataModelIGValue {name:$ig_name})
        MATCH (:DataModelVersion {href:$implements})-[:CONTAINS_DATA_MODEL]->(dm:DataModelValue)
        MERGE (ig)-[:IMPLEMENTS]->(dm)
    """,
        ig_name=version_data["name"],
        implements=version_data["implements_data_model"],
    )


def link_dataset_with_class(tx, _class, prefixed_version_number):
    if "implements_class" in _class:
        tx.run(
            f"""
                MATCH (:DataModelVersion)-[rel:{VERSION_TO_CLASS_REL_TYPE}]->(class_value:DatasetClassValue)
                WHERE rel.href=$class_href
                MATCH (:DatasetRoot {{uid: $uid}})-[:LATEST]->(dataset_value)
                MERGE (dataset_value)-[:IMPLEMENTS_DATASET_CLASS {{
                    catalogue: $catalogue,
                    version_number: $prefixed_version_number
                }}]->(class_value)
            """,
            uid=_class["uid"],
            class_href=_class["implements_class"],
            catalogue=_class["catalogue"],
            prefixed_version_number=prefixed_version_number,
        )


def link_class_with_subclasses(tx, _class, subclasses, prefixed_version_number):
    tx.run(
        f"""
            UNWIND $subclasses AS subclass_href
            MATCH (:DataModelVersion)-[rel]->(class_value)
            WHERE rel.href=$class_href AND type(rel) IN ["{VERSION_TO_CLASS_REL_TYPE}", "{VERSION_TO_DATASET_REL_TYPE}"]
            MATCH (:DataModelVersion)-[rel_sub:{VERSION_TO_CLASS_REL_TYPE}]->(subclass_value)
            WHERE rel_sub.href=subclass_href AND type(rel_sub) IN ["{VERSION_TO_CLASS_REL_TYPE}", "{VERSION_TO_DATASET_REL_TYPE}"]
            MERGE (class_value)<-[:HAS_PARENT_CLASS {{
                catalogue: $catalogue,
                version_number: $prefixed_version_number
            }}]-(subclass_value)
        """,
        class_href=_class["href"],
        subclasses=subclasses,
        catalogue=_class["catalogue"],
        prefixed_version_number=prefixed_version_number,
    )


def link_variable_with_variable(tx, version_data, variable, prefixed_version_number):
    match = f"""
        UNWIND $classes_href AS class_href
        MATCH ()-[rel]->(target_variable_value)
        WHERE rel.href=class_href AND (rel:{VERSION_TO_CLASS_VARIABLE_REL_TYPE} OR rel:{VERSION_TO_DATASET_VARIABLE_REL_TYPE})
        MATCH (n {{uid: $uid}})-->(source_variable_value)<--(source_dmv:DataModelVersion {{name: $source_version}})
        WHERE n:DatasetVariableRoot OR n:ClassVariableRoot
    """

    common_params = {
        "uid": variable["uid"],
        "source_version": version_data["name"],
        "prefixed_version_number": prefixed_version_number,
    }

    if "implements_variables" in variable and len(variable["implements_variables"]) > 0:
        tx.run(
            f"""
                {match}
                MERGE (source_variable_value)-[:IMPLEMENTS_VARIABLE{{
                    catalogue: $catalogue,
                    version_number: $prefixed_version_number
                }}]->(target_variable_value)
            """,
            classes_href=variable["implements_variables"],
            catalogue=variable["catalogue"],
            **common_params,
        )

    if "mapping_targets" in variable and len(variable["mapping_targets"]) > 0:
        tx.run(
            f"""
                {match}
                MERGE (source_variable_value)-[:HAS_MAPPING_TARGET{{
                    version_number: $prefixed_version_number
                }}]->(target_variable_value)
            """,
            classes_href=variable["mapping_targets"],
            **common_params,
        )


def _prettify_version_number(version_number: str, number_only=False):
    version = version_number.replace("-", ".")
    if number_only:
        parts = version.split(".")
        nbr_parts = 2
        if len(parts)>2 and parts[-3].isnumeric():
            # the version is major.minor.patch
            nbr_parts = 3
        version = ".".join(parts[-nbr_parts:])
    return version
