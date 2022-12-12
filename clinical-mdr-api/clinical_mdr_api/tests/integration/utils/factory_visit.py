from clinical_mdr_api.config import (
    DAY_UNIT_CONVERSION_FACTOR_TO_MASTER,
    WEEK_UNIT_CONVERSION_FACTOR_TO_MASTER,
)
from clinical_mdr_api.models import StudyVisit
from clinical_mdr_api.models.study_visit import (
    StudyVisitCreateInput,
    StudyVisitEditInput,
)
from clinical_mdr_api.models.unit_definition import UnitDefinitionPostInput
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services.study_visit import StudyVisitService
from clinical_mdr_api.services.unit_definition import UnitDefinitionService
from clinical_mdr_api.tests.integration.utils.factory_controlled_terminology import (
    create_codelist,
    create_ct_term,
    get_catalogue_name_library_name,
    get_unit_uid_by_name,
)
from clinical_mdr_api.tests.integration.utils.factory_epoch import (
    create_study_epoch,
    create_study_epoch_codelists_ret_cat_and_lib,
)

DAY = {
    "name": "day",
    "library_name": "Sponsor",
    "ct_units": ["unit1-ct-uid"],
    "convertible_unit": True,
    "display_unit": True,
    "master_unit": False,
    "si_unit": True,
    "us_conventional_unit": True,
    "unit_dimension": "TIME_UID",
    "legacy_code": "unit1-legacy-code",
    "molecular_weight_conv_expon": 0,
    "conversion_factor_to_master": DAY_UNIT_CONVERSION_FACTOR_TO_MASTER,
}

WEEK = {
    "name": "week",
    "library_name": "Sponsor",
    "ct_units": ["unit2-ct-uid"],
    "convertible_unit": True,
    "display_unit": True,
    "master_unit": False,
    "si_unit": False,
    "us_conventional_unit": True,
    "unit_dimension": "TIME_UID",
    "legacy_code": "unit2-legacy-code",
    "molecular_weight_conv_expon": 0,
    "conversion_factor_to_master": WEEK_UNIT_CONVERSION_FACTOR_TO_MASTER,
}


def generate_default_input_data_for_visit():
    DAYUID = get_unit_uid_by_name("day")
    WEEKUID = get_unit_uid_by_name("week")
    return {
        "legacy_visit_id": "legacy_visit",
        "legacy_visit_type_alias": "legacyVT",
        "legacy_name": "legacyN",
        "legacy_subname": "",
        "visit_sublabel_codelist_uid": "",
        "visit_sublabel_reference": "",
        "consecutive_visit_group": "",
        "show_visit": True,
        "min_visit_window_value": -1,
        "max_visit_window_value": 1,
        "visit_window_unit_uid": DAYUID,
        "time_unit_uid": WEEKUID,
        "time_value": 12,
        "description": "description",
        "start_rule": "start_rule",
        "end_rule": "end_rule",
        "note": "note",
        "visit_contact_mode_uid": "VisitContactMode_0001",
        "visit_type_uid": "VisitType_0003",
        "time_reference_uid": WEEKUID,
        "is_global_anchor_visit": False,
        "visit_class": "SINGLE_VISIT",
        "visit_subclass": "SINGLE_VISIT",
    }


def create_study_visit_codelists():
    catalogue_name, library_name = get_catalogue_name_library_name()
    create_study_epoch_codelists_ret_cat_and_lib()

    unit_dim_codelist = create_codelist(
        "Unit Dimension", "CTCodelist_UnitDim", catalogue_name, library_name
    )
    create_ct_term(
        unit_dim_codelist.codelist_uid,
        "TIME",
        "TIME_UID",
        1,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        unit_dim_codelist.codelist_uid,
        "WEEK",
        "WEEK_UID",
        2,
        catalogue_name,
        library_name,
    )

    ct_unit_codelist = create_codelist(
        "CT Unit", "CTCodelist_CTUnit", catalogue_name, library_name
    )
    create_ct_term(
        ct_unit_codelist.codelist_uid,
        "ct unit 1",
        "unit1-ct-uid",
        1,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        ct_unit_codelist.codelist_uid,
        "ct unit 2",
        "unit2-ct-uid",
        2,
        catalogue_name,
        library_name,
    )

    unit_service = UnitDefinitionService(
        user_id="some-user", meta_repository=MetaRepository()
    )
    unit_service.post(UnitDefinitionPostInput(**WEEK))
    unit_service.post(UnitDefinitionPostInput(**DAY))

    codelist = create_codelist(
        "VisitType", "CTCodelist_00004", catalogue_name, library_name
    )
    create_ct_term(
        codelist.codelist_uid,
        "BASELINE",
        "VisitType_0001",
        1,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        codelist.codelist_uid,
        "BASELINE2",
        "VisitType_0002",
        2,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        codelist.codelist_uid,
        "Visit Type2",
        "VisitType_0003",
        3,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        codelist.codelist_uid,
        "Visit Type3",
        "VisitType_0004",
        4,
        catalogue_name,
        library_name,
    )

    codelist = create_codelist(
        "Time Point Reference", "CTCodelist_00005", catalogue_name, library_name
    )
    create_ct_term(
        codelist.codelist_uid,
        "BASELINE",
        "VisitSubType_0001",
        1,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        codelist.codelist_uid,
        "BASELINE2",
        "VisitSubType_0002",
        2,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        codelist.codelist_uid,
        "Visit Sub Type2",
        "VisitSubType_0003",
        3,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        codelist.codelist_uid,
        "Visit Sub Type3",
        "VisitSubType_0004",
        4,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        codelist.codelist_uid,
        "Global anchor visit",
        "VisitSubType_0005",
        5,
        catalogue_name,
        library_name,
    )

    codelist = create_codelist(
        "Visit Sub Label", "CTCodelist_00006", catalogue_name, library_name
    )
    create_ct_term(
        codelist.codelist_uid,
        "Visit Sub Label",
        "VisitSubLabel_0001",
        1,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        codelist.codelist_uid,
        "Visit Sub Label1",
        "VisitSubLabel_0002",
        2,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        codelist.codelist_uid,
        "Visit Sub Label2",
        "VisitSubLabel_0003",
        3,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        codelist.codelist_uid,
        "Visit Sub Label3",
        "VisitSubLabel_0004",
        4,
        catalogue_name,
        library_name,
    )

    codelist = create_codelist(
        "Visit Contact Mode", "CTCodelist_00007", catalogue_name, library_name
    )
    create_ct_term(
        codelist.codelist_uid,
        "On Site Visit",
        "VisitContactMode_0001",
        1,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        codelist.codelist_uid,
        "Phone Contact",
        "VisitContactMode_0002",
        2,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        codelist.codelist_uid,
        "Virtual Visit",
        "VisitContactMode_0003",
        3,
        catalogue_name,
        library_name,
    )

    codelist = create_codelist(
        "Epoch Allocation", "CTCodelist_00008", catalogue_name, library_name
    )
    create_ct_term(
        codelist.codelist_uid,
        "Previous Visit",
        "EpochAllocation_0001",
        1,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        codelist.codelist_uid,
        "Current Visit",
        "EpochAllocation_0002",
        2,
        catalogue_name,
        library_name,
    )


def create_visit_with_update(**inputs) -> StudyVisit:
    visit_service: StudyVisitService = StudyVisitService()
    datadict = generate_default_input_data_for_visit().copy()
    datadict.update(inputs)
    visit_input = StudyVisitCreateInput(**datadict)
    visit = visit_service.create(study_uid="study_root", study_visit_input=visit_input)
    return visit


def update_visit_with_update(visit_uid: str, **inputs) -> StudyVisit:
    visit_service: StudyVisitService = StudyVisitService()
    datadict = generate_default_input_data_for_visit().copy()
    datadict.update(inputs)
    visit_input = StudyVisitEditInput(**datadict)
    visit = visit_service.edit(
        study_uid="study_root",
        study_visit_uid=visit_uid,
        study_visit_input=visit_input,
    )
    return visit


def preview_visit_with_update(study_uid, **inputs) -> StudyVisit:
    visit_service: StudyVisitService = StudyVisitService()
    datadict = generate_default_input_data_for_visit().copy()
    datadict.update(inputs)
    del datadict["visit_window_unit_uid"]
    visit_input = StudyVisitCreateInput(**datadict)
    preview: StudyVisit = visit_service.preview(study_uid, visit_input)
    return preview


def create_some_visits():
    create_study_visit_codelists()
    epoch1 = create_study_epoch("EpochSubType_0001")
    epoch2 = create_study_epoch("EpochSubType_0002")
    DAYUID = get_unit_uid_by_name("day")
    create_visit_with_update(
        study_epoch_uid=epoch1.uid,
        visit_type_uid="VisitType_0001",
        time_reference_uid="VisitSubType_0001",
        time_value=0,
        time_unit_uid=DAYUID,
    )
    create_visit_with_update(
        study_epoch_uid=epoch1.uid,
        visit_type_uid="VisitType_0003",
        time_reference_uid="VisitSubType_0001",
        time_value=12,
        time_unit_uid=DAYUID,
    )
    create_visit_with_update(
        study_epoch_uid=epoch1.uid,
        visit_type_uid="VisitType_0003",
        time_reference_uid="VisitSubType_0001",
        time_value=10,
        time_unit_uid=DAYUID,
    )

    v3 = create_visit_with_update(
        study_epoch_uid=epoch1.uid,
        visit_type_uid="VisitType_0004",
        time_reference_uid="VisitSubType_0001",
        time_value=20,
        time_unit_uid=DAYUID,
    )
    v4 = create_visit_with_update(
        study_epoch_uid=epoch2.uid,
        visit_type_uid="VisitType_0002",
        time_reference_uid="VisitSubType_0001",
        time_value=30,
        time_unit_uid=DAYUID,
        visit_sublabel_codelist_uid="VisitSubLabel_0001",
        visit_sublabel_reference=None,
        visit_class="SINGLE_VISIT",
        visit_subclass="ANCHOR_VISIT_IN_GROUP_OF_SUBV",
    )
    create_visit_with_update(
        study_epoch_uid=epoch2.uid,
        visit_type_uid="VisitType_0003",
        time_reference_uid="VisitSubType_0002",
        time_value=31,
        time_unit_uid=DAYUID,
        visit_sublabel_codelist_uid="VisitSubLabel_0002",
        visit_sublabel_reference=v4.uid,
        visit_class="SINGLE_VISIT",
        visit_subclass="ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV",
    )

    update_visit_with_update(
        v3.uid,
        uid=v3.uid,
        study_epoch_uid=epoch1.uid,
        visit_type_uid="VisitType_0004",
        time_reference_uid="VisitSubType_0001",
        time_value=35,
        time_unit_uid=DAYUID,
    )
