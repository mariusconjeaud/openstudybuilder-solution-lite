from clinical_mdr_api import exceptions
from clinical_mdr_api.domain_repositories.study_definition.study_definition_repository import (
    StudyDefinitionRepository,
)
from clinical_mdr_api.models.listings_study import StudyMetadataListingModel
from clinical_mdr_api.services._meta_repository import MetaRepository


class StudyMetadataListingService:
    _repos = MetaRepository()

    def _close_all_repos(self) -> None:
        self._repos.close()

    def _ct_attr_repos(self):
        return self._repos.ct_term_attributes_repository

    def _dict_term_repos(self):
        return self._repos.dictionary_term_generic_repository

    def get_study_metadata(self, study_number: int) -> StudyMetadataListingModel:
        try:
            uid = StudyDefinitionRepository.find_uid_by_study_number(study_number)
            if uid is None:
                raise exceptions.NotFoundException(
                    f"Study number '{study_number}' not found."
                )
            study_definition = self._repos.study_definition_repository.find_by_uid(uid)
            if study_definition is None:
                raise exceptions.NotFoundException(
                    f"Study definition '{uid}' not found."
                )
            result = StudyMetadataListingModel.from_study_study_metadata_vo_to_listing(
                study_definition.current_metadata,
                find_term_by_uid=self._ct_attr_repos().find_by_uid,
                find_dictionary_term_by_uid=self._dict_term_repos().find_by_uid,
            )
            return result
        finally:
            self._close_all_repos()
