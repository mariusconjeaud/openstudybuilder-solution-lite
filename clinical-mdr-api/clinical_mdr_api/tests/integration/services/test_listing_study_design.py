import unittest

from clinical_mdr_api.models.listings_study import (
    RegistryIdentifiersListingModel,
    StudyArmListingModel,
    StudyAttributesListingModel,
    StudyCohortListingModel,
    StudyDesignMatrixListingModel,
    StudyElementListingModel,
    StudyEpochListingModel,
    StudyMetadataListingModel,
    StudyPopulationListingModel,
    StudyTypeListingModel,
    StudyVisitListingModel,
)
from clinical_mdr_api.services.listings_study import StudyMetadataListingService
from clinical_mdr_api.services.study import StudyService
from clinical_mdr_api.services.study_epoch import StudyEpochService
from clinical_mdr_api.tests.integration.utils.api import inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import inject_base_data
from clinical_mdr_api.tests.integration.utils.method_library import (
    create_codelist,
    create_ct_term,
    create_some_visits,
    create_study_arm,
    create_study_branch_arm,
    create_study_cohort,
    create_study_design_cell,
    create_study_element,
    create_study_epoch_codelists_ret_cat_and_lib,
    generate_description_json_model,
    get_catalogue_name_library_name,
    high_level_study_design_json_model_to_vo,
    input_metadata_in_study,
    registry_identifiers_json_model_to_vo,
    study_intervention_json_model_to_vo,
    study_population_json_model_to_vo,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils


class TestStudyListing(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        inject_and_clear_db("StudyListingTest")
        TestUtils.create_library(name="UCUM", is_editable=True)
        inject_base_data()
        codelist = TestUtils.create_ct_codelist()
        TestUtils.create_study_ct_data_map(codelist_uid=codelist.codelist_uid)
        study_service = StudyService(user="some_user")
        studies = study_service.get_all()
        cls.study_uid = studies.items[0].uid
        cls.study_number = studies.items[
            0
        ].current_metadata.identification_metadata.study_number
        # Inject study metadata
        input_metadata_in_study(cls.study_uid)
        # Create study epochs
        create_study_epoch_codelists_ret_cat_and_lib(use_test_utils=True)
        catalogue_name, library_name = get_catalogue_name_library_name(
            use_test_utils=True
        )
        study_epoch = TestUtils.create_study_epoch(
            study_uid=cls.study_uid, epoch_subtype="EpochSubType_0001"
        )
        study_epoch2 = TestUtils.create_study_epoch(
            study_uid=cls.study_uid, epoch_subtype="EpochSubType_0002"
        )
        # Create study elements
        element_type_codelist = create_codelist(
            "Element Type", "CTCodelist_ElementType", catalogue_name, library_name
        )
        element_type_term = create_ct_term(
            element_type_codelist.codelist_uid,
            "Element Type",
            "ElementType_0001",
            1,
            catalogue_name,
            library_name,
        )
        element_type_term_2 = create_ct_term(
            element_type_codelist.codelist_uid,
            "Element Type",
            "ElementType_0002",
            2,
            catalogue_name,
            library_name,
        )
        study_elements = [
            create_study_element(element_type_term.uid, cls.study_uid),
            create_study_element(element_type_term_2.uid, cls.study_uid),
        ]

        # Create study arms
        codelist = create_codelist(
            name="Arm Type",
            uid="CTCodelist_00009",
            catalogue=catalogue_name,
            library=library_name,
        )
        arm_type = create_ct_term(
            codelist=codelist.codelist_uid,
            name="Arm Type",
            uid="ArmType_0001",
            order=1,
            catalogue_name=catalogue_name,
            library_name=library_name,
        )

        create_study_arm(
            study_uid=cls.study_uid,
            name="Arm_Name_1",
            short_name="Arm_Short_Name_1",
            code="Arm_code_1",
            description="desc...",
            colour_code="colour...",
            randomization_group="Arm_randomizationGroup",
            number_of_subjects=100,
            arm_type_uid=arm_type.uid,
        )
        create_study_arm(
            study_uid=cls.study_uid,
            name="Arm_Name_2",
            short_name="Arm_Short_Name_2",
            code="Arm_code_2",
            description="desc...",
            colour_code="colour...",
            randomization_group="Arm_randomizationGroup2",
            number_of_subjects=100,
            arm_type_uid=arm_type.uid,
        )
        create_study_arm(
            study_uid=cls.study_uid,
            name="Arm_Name_3",
            short_name="Arm_Short_Name_3",
            code="Arm_code_3",
            description="desc...",
            colour_code="colour...",
            randomization_group="Arm_randomizationGroup3",
            number_of_subjects=100,
            arm_type_uid=arm_type.uid,
        )

        create_study_arm(
            study_uid=cls.study_uid,
            name="Arm_Name_9",
            short_name="Arm_Short_Name_9",
            code="Arm_code_9",
            description="desc...",
            colour_code="colour...",
            randomization_group="Arm_randomizationGroup9",
            number_of_subjects=100,
            arm_type_uid=arm_type.uid,
        )

        # Create study design cells
        create_study_design_cell(
            study_element_uid=study_elements[0].element_uid,
            study_epoch_uid=study_epoch.uid,
            study_arm_uid="StudyArm_000003",
            study_uid=cls.study_uid,
        )
        create_study_design_cell(
            study_element_uid=study_elements[0].element_uid,
            study_epoch_uid=study_epoch2.uid,
            study_arm_uid="StudyArm_000003",
            study_uid=cls.study_uid,
        )

        create_study_design_cell(
            study_element_uid=study_elements[1].element_uid,
            study_epoch_uid=study_epoch2.uid,
            study_arm_uid="StudyArm_000001",
            study_uid=cls.study_uid,
        )

        create_study_design_cell(
            study_element_uid=study_elements[0].element_uid,
            study_epoch_uid=study_epoch2.uid,
            study_arm_uid="StudyArm_000005",
            study_uid=cls.study_uid,
        )

        # Create study branch arms
        create_study_branch_arm(
            study_uid=cls.study_uid,
            name="Branch_Arm_Name_1",
            short_name="Branch_Arm_Short_Name_1",
            code="Branch_Arm_code_1",
            description="desc...",
            colour_code="colour...",
            randomization_group="Branch_Arm_randomizationGroup",
            number_of_subjects=100,
            arm_uid="StudyArm_000003",
        )

        # Create study cohort
        create_study_cohort(
            study_uid=cls.study_uid,
            name="Cohort_Name_1",
            short_name="Cohort_Short_Name_1",
            code="Cohort_code_1",
            description="desc...",
            colour_code="desc...",
            number_of_subjects=100,
            arm_uids=["StudyArm_000001"],
        )

        # Create study visit
        create_some_visits(
            use_test_utils=True,
            create_epoch_codelist=False,
            study_uid=cls.study_uid,
            epoch1=study_epoch,
            epoch2=study_epoch2,
        )

    def test_study_metadata_listing(self):
        self.maxDiff = None
        study_listing_service = StudyMetadataListingService()
        output = study_listing_service.get_study_metadata(self.study_number)
        expected_output = StudyMetadataListingModel(
            study_title=generate_description_json_model(),
            registry_identifiers=RegistryIdentifiersListingModel.from_study_registry_identifiers_vo(
                registry_identifiers_json_model_to_vo(),
                find_term_by_uid=study_listing_service.ct_attr_repo.find_by_uid,
            ),
            study_type=StudyTypeListingModel.from_high_level_study_design_vo(
                high_level_study_design_json_model_to_vo(),
                find_term_by_uid=study_listing_service.ct_attr_repo.find_by_uid,
            ),
            study_attributes=StudyAttributesListingModel.from_study_intervention_vo(
                study_intervention_json_model_to_vo(),
                find_term_by_uid=study_listing_service.ct_attr_repo.find_by_uid,
            ),
            study_population=StudyPopulationListingModel.from_study_population_vo(
                study_population_json_model_to_vo(),
                find_term_by_uid=study_listing_service.ct_attr_repo.find_by_uid,
                find_dictionary_term_by_uid=study_listing_service.dict_term_repo.find_by_uid,
            ),
            study_arms=StudyArmListingModel.from_study_selection_arm_ar(
                study_uid=self.study_uid,
                study_selection_arm_ar=study_listing_service.arm_repo.find_by_study(
                    self.study_uid
                ),
                find_simple_term_arm_type_by_term_uid=study_listing_service.ct_attr_repo.find_by_uid,
                find_multiple_connected_branch_arm=study_listing_service.branch_arm_repo.find_by_arm,
            ),
            study_cohorts=StudyCohortListingModel.from_study_selection_cohort_ar(
                study_selection_cohort_ar=study_listing_service.cohort_repo.find_by_study(
                    self.study_uid,
                ),
                find_arm_by_uid=study_listing_service.arm_repo.find_by_study(
                    self.study_uid,
                ).get_specific_arm_selection,
                find_branch_arm_by_uid=study_listing_service.branch_arm_repo.find_by_study(
                    self.study_uid,
                ).get_specific_branch_arm_selection,
            ),
            study_epochs=StudyEpochListingModel.from_all_study_epochs(
                all_study_epochs=StudyEpochService()
                .get_all_epochs(
                    self.study_uid,
                )
                .items,
                find_term_by_uid=study_listing_service.ct_attr_repo.find_by_uid,
            ),
            study_elements=StudyElementListingModel.from_study_element_ar(
                study_element_ar=study_listing_service.element_repo.find_by_study(
                    self.study_uid,
                ),
                find_term_by_uid=study_listing_service.ct_attr_repo.find_by_uid,
            ),
            study_design_matrix=StudyDesignMatrixListingModel.from_all_study_design_cells(
                all_design_cells=study_listing_service.design_cell_repo.find_all_design_cells_by_study(
                    self.study_uid,
                ),
                find_arm_by_uid=study_listing_service.arm_repo.find_by_study(
                    self.study_uid,
                ).get_specific_arm_selection,
                find_branch_arm_by_uid=study_listing_service.branch_arm_repo.find_by_study(
                    self.study_uid,
                ).get_specific_branch_arm_selection,
            ),
            study_visits=StudyVisitListingModel.from_all_study_visits(
                all_study_visits=study_listing_service.get_all_visits(
                    self.study_uid,
                )
            ),
        )

        # Check study title
        self.assertEqual(output.study_title, expected_output.study_title)

        # Check study identifiers
        self.assertEqual(
            output.registry_identifiers,
            expected_output.registry_identifiers,
        )
        self.assertCountEqual(
            output.registry_identifiers,
            expected_output.registry_identifiers,
        )

        # Check study type
        self.assertCountEqual(output.study_type, expected_output.study_type)
        self.assertEqual(output.study_type, expected_output.study_type)

        # Check study attributes
        self.assertCountEqual(output.study_attributes, expected_output.study_attributes)
        self.assertEqual(output.study_attributes, expected_output.study_attributes)

        # Check study population
        self.assertCountEqual(output.study_population, expected_output.study_population)
        self.assertEqual(output.study_population, expected_output.study_population)

        # Check study arms
        self.assertCountEqual(output.study_arms, expected_output.study_arms)
        self.assertEqual(output.study_arms, expected_output.study_arms)

        # Check study cohorts
        self.assertCountEqual(output.study_cohorts, expected_output.study_cohorts)
        self.assertEqual(output.study_cohorts, expected_output.study_cohorts)

        # Check study epochs
        self.assertCountEqual(output.study_epochs, expected_output.study_epochs)
        self.assertEqual(output.study_epochs, expected_output.study_epochs)

        # Check study elements
        self.assertCountEqual(output.study_elements, expected_output.study_elements)
        self.assertEqual(output.study_elements, expected_output.study_elements)

        # Check study design matrix
        self.assertCountEqual(
            output.study_design_matrix, expected_output.study_design_matrix
        )
        self.assertEqual(
            output.study_design_matrix, expected_output.study_design_matrix
        )

        # Check study visits
        self.assertCountEqual(output.study_visits, expected_output.study_visits)
        self.assertEqual(output.study_visits, expected_output.study_visits)
