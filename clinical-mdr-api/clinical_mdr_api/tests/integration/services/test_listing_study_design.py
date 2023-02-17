import unittest

from clinical_mdr_api.models.listings_study import (
    RegistryIdentifiersListingModel,
    StudyMetadataListingModel,
    StudyPopulationListingModel,
    StudyTypeListingModel,
)
from clinical_mdr_api.services.listings_study import StudyMetadataListingService
from clinical_mdr_api.services.study import StudyService
from clinical_mdr_api.tests.integration.utils.api import inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import inject_base_data
from clinical_mdr_api.tests.integration.utils.method_library import (
    generate_description_metadata,
    generate_high_level_study_design,
    generate_ri_data,
    generate_study_population,
    input_metadata_in_study,
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
        cls.study_number = studies.items[0].study_number
        input_metadata_in_study(cls.study_uid)

    def test_study_metadata_listing(self):
        self.maxDiff = None
        study_listing_service = StudyMetadataListingService()
        output = study_listing_service.get_study_metadata(self.study_number)
        expected_output = StudyMetadataListingModel(
            study_title=generate_description_metadata(),
            registry_identifiers=RegistryIdentifiersListingModel.from_registry_identifiers_json_model(
                generate_ri_data(),
                find_term_by_uid=study_listing_service._ct_attr_repos().find_by_uid,
            ),
            study_type=StudyTypeListingModel.from_high_level_study_design_json_model(
                generate_high_level_study_design(),
                find_term_by_uid=study_listing_service._ct_attr_repos().find_by_uid,
            ),
            study_population=StudyPopulationListingModel.from_study_population_json_model(
                generate_study_population(),
                find_term_by_uid=study_listing_service._ct_attr_repos().find_by_uid,
                find_dictionary_term_by_uid=study_listing_service._dict_term_repos().find_by_uid,
            ),
        )
        print("output: ", output)
        print("expect: ", expected_output)
        self.assertEqual(output.study_title, expected_output.study_title)
        self.assertEqual(
            output.registry_identifiers,
            expected_output.registry_identifiers,
        )
        self.assertCountEqual(output.study_type, expected_output.study_type)
        self.assertCountEqual(output.study_population, expected_output.study_population)
        self.assertEqual(output.study_population, expected_output.study_population)
