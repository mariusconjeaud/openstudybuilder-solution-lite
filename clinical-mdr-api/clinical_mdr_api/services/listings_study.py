from clinical_mdr_api import exceptions
from clinical_mdr_api.domain.study_selection.study_epoch import TimelineAR
from clinical_mdr_api.domain_repositories.study_definition.study_definition_repository import (
    StudyDefinitionRepository,
)
from clinical_mdr_api.models.listings_study import StudyMetadataListingModel
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services.study_epoch import StudyEpochService


class StudyMetadataListingService:
    _repos = MetaRepository()

    def _close_all_repos(self) -> None:
        self._repos.close()

    @property
    def ct_attr_repo(self):
        return self._repos.ct_term_attributes_repository

    @property
    def dict_term_repo(self):
        return self._repos.dictionary_term_generic_repository

    @property
    def arm_repo(self):
        return self._repos.study_arm_repository

    @property
    def branch_arm_repo(self):
        return self._repos.study_branch_arm_repository

    @property
    def cohort_repo(self):
        return self._repos.study_cohort_repository

    @property
    def element_repo(self):
        return self._repos.study_element_repository

    @property
    def design_cell_repo(self):
        return self._repos.study_design_cell_repository

    @property
    def visit_repo(self):
        return self._repos.study_visit_repository

    def get_all_visits(self, study_uid: str):
        study_visits = self.visit_repo.find_all_visits_by_study_uid(study_uid=study_uid)
        timeline = TimelineAR(study_uid=study_uid, _visits=study_visits)
        assert study_visits is not None
        return timeline.ordered_study_visits

    def get_study_metadata(self, study_number: int) -> StudyMetadataListingModel:
        try:
            study_uid = StudyDefinitionRepository.find_uid_by_study_number(study_number)
            if study_uid is None:
                raise exceptions.NotFoundException(
                    f"Study number '{study_number}' not found."
                )
            study_definition = self._repos.study_definition_repository.find_by_uid(
                study_uid
            )
            if study_definition is None:
                raise exceptions.NotFoundException(
                    f"Study definition '{study_uid}' not found."
                )
            result = StudyMetadataListingModel.from_study_metadata_vo(
                study_uid=study_uid,
                study_metadata_vo=study_definition.current_metadata,
                study_selection_arm_ar=self.arm_repo.find_by_study(
                    study_uid,
                ),
                study_selection_cohort_ar=self.cohort_repo.find_by_study(
                    study_uid,
                ),
                study_epochs=StudyEpochService()
                .get_all_epochs(
                    study_uid,
                )
                .items,
                study_element_ar=self.element_repo.find_by_study(
                    study_uid,
                ),
                study_design_cells=self.design_cell_repo.find_all_design_cells_by_study(
                    study_uid,
                ),
                study_visits=self.get_all_visits(
                    study_uid,
                ),
                find_term_by_uid=self.ct_attr_repo.find_by_uid,
                find_dictionary_term_by_uid=self.dict_term_repo.find_by_uid,
                find_multiple_connected_branch_arm=self.branch_arm_repo.find_by_arm,
                find_arm_by_uid=self.arm_repo.find_by_study(
                    study_uid,
                ).get_specific_arm_selection,
                find_branch_arm_by_uid=self.branch_arm_repo.find_by_study(
                    study_uid,
                ).get_specific_branch_arm_selection,
            )
            return result
        finally:
            self._close_all_repos()
