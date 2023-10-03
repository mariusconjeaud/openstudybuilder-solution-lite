from dataclasses import dataclass
from typing import Callable, Self

from clinical_mdr_api import exceptions
from clinical_mdr_api.domains._utils import normalize_string


@dataclass(frozen=True)
class RegistryIdentifiersVO:
    ct_gov_id: str | None
    ct_gov_id_null_value_code: str | None
    eudract_id: str | None
    eudract_id_null_value_code: str | None
    universal_trial_number_utn: str | None
    universal_trial_number_utn_null_value_code: str | None
    japanese_trial_registry_id_japic: str | None
    japanese_trial_registry_id_japic_null_value_code: str | None
    investigational_new_drug_application_number_ind: str | None
    investigational_new_drug_application_number_ind_null_value_code: str | None

    @classmethod
    def from_input_values(
        cls,
        ct_gov_id: str | None,
        ct_gov_id_null_value_code: str | None,
        eudract_id: str | None,
        eudract_id_null_value_code: str | None,
        universal_trial_number_utn: str | None,
        universal_trial_number_utn_null_value_code: str | None,
        japanese_trial_registry_id_japic: str | None,
        japanese_trial_registry_id_japic_null_value_code: str | None,
        investigational_new_drug_application_number_ind: str | None,
        investigational_new_drug_application_number_ind_null_value_code: str | None,
    ) -> Self:
        def norm_str(s: str | None) -> str | None:
            return normalize_string(s)

        return cls(
            ct_gov_id=norm_str(ct_gov_id),
            ct_gov_id_null_value_code=norm_str(ct_gov_id_null_value_code),
            eudract_id=norm_str(eudract_id),
            eudract_id_null_value_code=norm_str(eudract_id_null_value_code),
            universal_trial_number_utn=norm_str(universal_trial_number_utn),
            universal_trial_number_utn_null_value_code=norm_str(
                universal_trial_number_utn_null_value_code
            ),
            japanese_trial_registry_id_japic=norm_str(japanese_trial_registry_id_japic),
            japanese_trial_registry_id_japic_null_value_code=norm_str(
                japanese_trial_registry_id_japic_null_value_code
            ),
            investigational_new_drug_application_number_ind=norm_str(
                investigational_new_drug_application_number_ind
            ),
            investigational_new_drug_application_number_ind_null_value_code=norm_str(
                investigational_new_drug_application_number_ind_null_value_code
            ),
        )

    def validate(
        self, null_value_exists_callback: Callable[[str], bool] = (lambda _: True)
    ) -> None:
        """Raises ValueError if values do not comply with relevant business rules."""
        if (
            self.ct_gov_id_null_value_code is not None
            and not null_value_exists_callback(self.ct_gov_id_null_value_code)
        ):
            raise exceptions.ValidationException(
                "Unknown null value code provided for Reason For Missing in ClinicalTrials.gov ID"
            )

        if (
            self.eudract_id_null_value_code is not None
            and not null_value_exists_callback(self.eudract_id_null_value_code)
        ):
            raise exceptions.ValidationException(
                "Unknown null value code provided for Reason For Missing in EUDRACT ID"
            )

        if (
            self.universal_trial_number_utn_null_value_code is not None
            and not null_value_exists_callback(
                self.universal_trial_number_utn_null_value_code
            )
        ):
            raise exceptions.ValidationException(
                "Unknown null value code provided for Reason For Missing in Universal Trial Number (UTN)"
            )

        if (
            self.japanese_trial_registry_id_japic_null_value_code is not None
            and not null_value_exists_callback(
                self.japanese_trial_registry_id_japic_null_value_code
            )
        ):
            raise exceptions.ValidationException(
                "Unknown null value code provided for Reason For Missing in Japanese Trial Registry ID (JAPIC)"
            )

        if (
            self.investigational_new_drug_application_number_ind_null_value_code
            is not None
            and not null_value_exists_callback(
                self.investigational_new_drug_application_number_ind_null_value_code
            )
        ):
            raise exceptions.ValidationException(
                "Unknown null value code provided for Reason For Missing in Investigational New Drug Application (IND) Number"
            )

        if self.ct_gov_id_null_value_code is not None and self.ct_gov_id is not None:
            raise exceptions.ValidationException(
                "If reason_for_missing_null_value_uid has a value, then field ct_gov_id must be None or empty string"
            )

        if self.eudract_id_null_value_code is not None and self.eudract_id is not None:
            raise exceptions.ValidationException(
                "If reason_for_missing_null_value_uid has a value, then field eudract_id must be None or empty string"
            )

        if (
            self.universal_trial_number_utn_null_value_code is not None
            and self.universal_trial_number_utn is not None
        ):
            raise exceptions.ValidationException(
                "If reason_for_missing_null_value_uid has a value, then field universal_trial_number_utn must be None or empty string"
            )

        if (
            self.japanese_trial_registry_id_japic_null_value_code is not None
            and self.japanese_trial_registry_id_japic is not None
        ):
            raise exceptions.ValidationException(
                "If reason_for_missing_null_value_uid has a value, then field japanese_trial_registry_id_japic must be None or empty string"
            )

        if (
            self.investigational_new_drug_application_number_ind_null_value_code
            is not None
            and self.investigational_new_drug_application_number_ind is not None
        ):
            raise exceptions.ValidationException(
                (
                    "If reason_for_missing_null_value_uid has a value, "
                    "then field investigational_new_drug_application_number_ind must be None or empty string"
                )
            )
