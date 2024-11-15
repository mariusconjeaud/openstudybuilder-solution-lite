# pylint: disable=invalid-name
from neomodel import db

from clinical_mdr_api.domain_repositories.feature_flag_repository import (
    FeatureFlagRepository,
)
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.feature_flag import FeatureFlag, FeatureFlagInput


class FeatureFlagService:
    repo: FeatureFlagRepository

    def __init__(self) -> None:
        self.repo = FeatureFlagRepository()

    def get_all_feature_flags(self) -> list[FeatureFlag]:
        return self.repo.retrieve_all_feature_flags()

    def get_feature_flag(self, sn: int) -> FeatureFlag:
        return self.repo.retrieve_feature_flag(sn)

    @db.transaction
    def create_feature_flag(
        self,
        feature_flag_input: FeatureFlagInput,
    ) -> FeatureFlag:
        if self.repo.find_feature_flag_by_name(feature_flag_input.name):
            raise BusinessLogicException(
                f"Feature flag with name ({feature_flag_input.name}) already exists."
            )

        return self.repo.create_feature_flag(
            name=feature_flag_input.name,
            enabled=feature_flag_input.enabled,
            description=feature_flag_input.description,
        )

    @db.transaction
    def update_feature_flag(
        self,
        sn: int,
        feature_flag_input: FeatureFlagInput,
    ) -> FeatureFlag:
        ff = self.repo.find_feature_flag_by_name(feature_flag_input.name)
        if ff and ff.sn != sn:
            raise BusinessLogicException(
                f"Feature flag with name ({feature_flag_input.name}) already exists."
            )

        return self.repo.update_feature_flag(
            sn=sn,
            name=feature_flag_input.name,
            enabled=feature_flag_input.enabled,
            description=feature_flag_input.description,
        )

    @db.transaction
    def delete_feature_flag(self, sn: int) -> None:
        return self.repo.delete_feature_flag(sn)
