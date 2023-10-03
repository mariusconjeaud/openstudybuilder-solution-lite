"""
Tests for /studies/{uid}/study-activities endpoints
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import logging

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api.main import app
from clinical_mdr_api.models.study_selections.study import Study
from clinical_mdr_api.models.syntax_templates.template_parameter_term import (
    IndexedTemplateParameterTerm,
    MultiTemplateParameterTerm,
)
from clinical_mdr_api.tests.integration.utils.api import (
    drop_db,
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_ACTIVITIES,
    STARTUP_ACTIVITY_GROUPS,
    STARTUP_ACTIVITY_SUB_GROUPS,
    STARTUP_CT_CATALOGUE_CYPHER,
    STARTUP_STUDY_LIST_CYPHER,
    get_codelist_with_term_cypher,
)
from clinical_mdr_api.tests.integration.utils.factory_visit import (
    generate_default_input_data_for_visit,
)
from clinical_mdr_api.tests.integration.utils.method_library import (
    create_library_data,
    create_study_epoch,
    create_study_visit_codelists,
    get_unit_uid_by_name,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils

log = logging.getLogger(__name__)

study: Study
epoch_uid: str
DAYUID: str
visits_basic_data: str
activity_instruction: str


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "studyactivityapi"
    inject_and_clear_db(db_name)
    inject_base_data()
    global study
    study = TestUtils.create_study()

    db.cypher_query(STARTUP_ACTIVITY_GROUPS)
    db.cypher_query(STARTUP_ACTIVITY_SUB_GROUPS)
    db.cypher_query(STARTUP_ACTIVITIES)
    db.cypher_query(
        get_codelist_with_term_cypher(
            "EFFICACY", "Flowchart Group", term_uid="term_efficacy_uid"
        )
    )
    db.cypher_query(
        get_codelist_with_term_cypher(
            "EFFICACY", "Flowchart Group", term_uid="informed_consent_uid"
        )
    )
    db.cypher_query(STARTUP_STUDY_LIST_CYPHER)
    db.cypher_query(STARTUP_CT_CATALOGUE_CYPHER)
    create_library_data()
    create_study_visit_codelists(create_unit_definitions=False)
    study_epoch = create_study_epoch("EpochSubType_0001", study_uid=study.uid)
    global epoch_uid
    epoch_uid = study_epoch.uid
    global DAYUID
    DAYUID = get_unit_uid_by_name("day")
    global visits_basic_data
    visits_basic_data = generate_default_input_data_for_visit().copy()

    # Create Template Parameter
    TestUtils.create_template_parameter("TextValue")
    TestUtils.create_template_parameter("StudyActivityInstruction")

    text_value_1 = TestUtils.create_text_value()

    activity_group = TestUtils.create_activity_group(name="test activity group")
    activity_subgroup = TestUtils.create_activity_subgroup(
        name="test activity subgroup", activity_groups=[activity_group.uid]
    )
    activity = TestUtils.create_activity(
        name="test activity",
        library_name="Sponsor",
        activity_groups=[activity_group.uid],
        activity_subgroups=[activity_subgroup.uid],
    )

    indications_library_name = "SNOMED"
    indications_codelist = TestUtils.create_dictionary_codelist(
        name="DiseaseDisorder", library_name=indications_library_name
    )
    dictionary_term_indication = TestUtils.create_dictionary_term(
        codelist_uid=indications_codelist.codelist_uid,
        library_name=indications_library_name,
    )

    parameter_terms = [
        MultiTemplateParameterTerm(
            position=1,
            conjunction="",
            terms=[
                IndexedTemplateParameterTerm(
                    index=1,
                    name=text_value_1.name,
                    uid=text_value_1.uid,
                    type="TextValue",
                )
            ],
        )
    ]

    activity_instruction_template = TestUtils.create_activity_instruction_template(
        name="Default name with [TextValue]",
        guidance_text="Default guidance text",
        library_name="Sponsor",
        default_parameter_terms=parameter_terms,
        indication_uids=[dictionary_term_indication.term_uid],
        activity_uids=[activity.uid],
        activity_group_uids=[activity_group.uid],
        activity_subgroup_uids=[activity_subgroup.uid],
    )

    # Create some activity_instructions
    global activity_instruction
    activity_instruction = TestUtils.create_activity_instruction(
        activity_instruction_template_uid=activity_instruction_template.uid,
        library_name="Sponsor",
        parameter_terms=parameter_terms,
        approve=True,
    )

    yield
    drop_db(db_name)


def test_activity_modify_actions_on_locked_study(api_client):
    response = api_client.post(
        f"/studies/{study.uid}/study-activities",
        json={
            "activity_uid": "activity_root1",
            "activity_subgroup_uid": "activity_subgroup_root1",
            "activity_group_uid": "activity_group_root1",
            "flowchart_group_uid": "term_efficacy_uid",
        },
    )
    res = response.json()
    assert response.status_code == 201

    # get all activities
    response = api_client.get(
        f"/studies/{study.uid}/study-activities/audit-trail/",
    )
    res = response.json()
    assert response.status_code == 200
    old_res = res
    study_activity_uid = res[0]["study_activity_uid"]

    # update study title to be able to lock it
    response = api_client.patch(
        f"/studies/{study.uid}",
        json={"current_metadata": {"study_description": {"study_title": "new title"}}},
    )
    assert response.status_code == 200

    # Lock
    response = api_client.post(
        f"/studies/{study.uid}/lock",
        json={"change_description": "Lock 1"},
    )
    assert response.status_code == 201

    response = api_client.post(
        f"/studies/{study.uid}/study-activities",
        json={
            "activity_uid": "activity_root2",
            "activity_subgroup_uid": "activity_subgroup_root2",
            "activity_group_uid": "activity_group_root2",
            "flowchart_group_uid": "term_efficacy_uid",
        },
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."
    # edit activity
    response = api_client.patch(
        f"/studies/{study.uid}/study-activities/{study_activity_uid}",
        json={"flowchart_group_uid": "term_efficacy_uid"},
    )
    res = response.json()
    assert response.status_code == 400
    assert res["message"] == f"Study with specified uid '{study.uid}' is locked."

    # get all history when was locked
    response = api_client.get(
        f"/studies/{study.uid}/study-activities/audit-trail/",
    )
    res = response.json()
    assert response.status_code == 200
    assert old_res == res

    # Unlock -- Study remain unlocked
    response = api_client.post(f"/studies/{study.uid}/unlock")
    assert response.status_code == 201

    response = api_client.delete(
        f"/studies/{study.uid}/study-activities/{study_activity_uid}",
    )
    assert response.status_code == 204


def test_cascade_delete_on_activities_schedules(api_client):
    response = api_client.post(
        f"/studies/{study.uid}/study-activities",
        json={
            "activity_uid": "activity_root1",
            "activity_subgroup_uid": "activity_subgroup_root1",
            "activity_group_uid": "activity_group_root1",
            "flowchart_group_uid": "term_efficacy_uid",
        },
    )
    res = response.json()
    assert response.status_code == 201
    study_activity_uid = res["study_activity_uid"]

    # create visit
    inputs = {
        "study_epoch_uid": epoch_uid,
        "visit_type_uid": "VisitType_0001",
        "show_visit": True,
        "time_reference_uid": "VisitSubType_0001",
        "time_value": 0,
        "time_unit_uid": DAYUID,
        "visit_class": "SINGLE_VISIT",
        "visit_subclass": "SINGLE_VISIT",
        "is_global_anchor_visit": True,
    }
    datadict = visits_basic_data
    datadict.update(inputs)
    response = api_client.post(
        f"/studies/{study.uid}/study-visits",
        json=datadict,
    )
    res = response.json()
    study_visit_uid = res["uid"]
    assert response.status_code == 201

    # add activity schedule
    response = api_client.post(
        f"/studies/{study.uid}/study-activity-schedules",
        json={
            "study_activity_uid": study_activity_uid,
            "study_visit_uid": study_visit_uid,
        },
    )
    res = response.json()
    assert response.status_code == 201

    # delete activity
    response = api_client.delete(
        f"/studies/{study.uid}/study-activities/{study_activity_uid}",
    )
    assert response.status_code == 204

    # check if the activities schedules have been deleted
    response = api_client.get(
        f"/studies/{study.uid}/study-activity-schedules/",
    )
    res = response.json()
    assert response.status_code == 200
    assert res == []

    # clean visits from test
    response = api_client.delete(
        f"/studies/{study.uid}/study-visits/{study_visit_uid}",
    )
    assert response.status_code == 204


@pytest.mark.parametrize(
    "export_format",
    [
        pytest.param("text/csv"),
        pytest.param("text/xml"),
        pytest.param(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    ],
)
def test_get_study_activities_csv_xml_excel(api_client, export_format):
    url = f"/studies/{study.uid}/study-activities"
    TestUtils.verify_exported_data_format(api_client, export_format, url)


def test_maintain_outbound_rels(api_client):
    response = api_client.post(
        f"/studies/{study.uid}/study-activities",
        json={
            "activity_uid": "activity_root1",
            "activity_subgroup_uid": "activity_subgroup_root1",
            "activity_group_uid": "activity_group_root1",
            "flowchart_group_uid": "term_efficacy_uid",
        },
    )
    res = response.json()
    assert response.status_code == 201
    study_activity_uid = res["study_activity_uid"]

    # create visit
    inputs = {
        "study_epoch_uid": epoch_uid,
        "visit_type_uid": "VisitType_0001",
        "show_visit": True,
        "time_reference_uid": "VisitSubType_0001",
        "time_value": 0,
        "time_unit_uid": DAYUID,
        "visit_class": "SINGLE_VISIT",
        "visit_subclass": "SINGLE_VISIT",
        "is_global_anchor_visit": True,
    }
    datadict = visits_basic_data
    datadict.update(inputs)
    response = api_client.post(
        f"/studies/{study.uid}/study-visits",
        json=datadict,
    )
    res = response.json()
    assert response.status_code == 201
    study_visit_uid = res["uid"]

    # add activity schedule
    response = api_client.post(
        f"/studies/{study.uid}/study-activity-schedules",
        json={
            "study_activity_uid": study_activity_uid,
            "study_visit_uid": study_visit_uid,
        },
    )
    assert response.status_code == 201

    # add activity instruction
    response = api_client.post(
        f"/studies/{study.uid}/study-activity-instructions/batch",
        json=[
            {
                "method": "POST",
                "content": {
                    "activity_instruction_uid": activity_instruction.uid,
                    "study_activity_uid": study_activity_uid,
                },
            }
        ],
    )
    assert response.status_code == 207

    # patch visits to be sure that the outbound relationship (Visits-->ActivitySchedule) is maintained
    inputs = {
        "uid": study_visit_uid,
        "description": "new description",
    }
    datadict = visits_basic_data
    datadict.update(inputs)
    response = api_client.patch(
        f"/studies/{study.uid}/study-visits/{study_visit_uid}",
        json=datadict,
    )
    assert response.status_code == 200

    # patch activities to be sure that the outbound relationship (Activity-->ActivitySchedule) is maintained
    response = api_client.patch(
        f"/studies/{study.uid}/study-activities/{study_activity_uid}",
        json={
            "flowchart_group_uid": "informed_consent_uid",
        },
    )
    assert response.status_code == 200

    # check if the activities schedules maintained the trace to StudyVisits new version
    response = api_client.get(
        f"/studies/{study.uid}/study-activity-schedules/",
    )
    res = response.json()
    assert response.status_code == 200
    assert res[0]["study_visit_uid"] == study_visit_uid
    assert res[0]["study_activity_uid"] == study_activity_uid

    # clean visits from test
    response = api_client.delete(
        f"/studies/{study.uid}/study-visits/{study_visit_uid}",
    )
    assert response.status_code == 204

    # check if the activities schedules were cascade deleted by StudyVisit deletion
    response = api_client.get(
        f"/studies/{study.uid}/study-activity-schedules/",
    )
    res = response.json()
    assert len(res) == 0

    # clean activities from test
    response = api_client.delete(
        f"/studies/{study.uid}/study-activities/{study_activity_uid}",
    )
    assert response.status_code == 204

    # check if the activities instructions were cascade deleted by a StudyActivity deletion
    response = api_client.get(
        f"/studies/{study.uid}/study-activity-instructions/",
    )
    res = response.json()
    assert len(res) == 0
