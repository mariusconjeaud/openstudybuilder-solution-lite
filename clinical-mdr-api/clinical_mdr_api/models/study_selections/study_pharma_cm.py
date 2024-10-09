from typing import Callable, Self

from pydantic import Field

from clinical_mdr_api.domains.concepts.unit_definitions.unit_definition import (
    UnitDefinitionAR,
)
from clinical_mdr_api.domains.controlled_terminologies.ct_term_name import CTTermNameAR
from clinical_mdr_api.domains.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domains.study_definition_aggregates.root import StudyDefinitionAR
from clinical_mdr_api.domains.study_selections.study_selection_arm import (
    StudySelectionArmAR,
)
from clinical_mdr_api.models.study_selections.study_selection import (
    StudySelectionCriteria,
    StudySelectionEndpoint,
)
from clinical_mdr_api.models.utils import (
    BaseModel,
    from_duration_object_to_value_and_unit,
)
from clinical_mdr_api.services._utils import get_name_or_none


class CompactStudyArm(BaseModel):
    arm_type: str | None = Field(
        None,
    )
    arm_title: str = Field(
        ...,
    )
    arm_description: str | None = Field(
        None,
    )


class CompactOutcomeMeasure(BaseModel):
    title: str | None = Field(
        None,
    )
    timeframe: str | None = Field(
        None,
    )
    description: str | None = Field(
        None,
    )


class CompactRegistryIdentifier(BaseModel):
    secondary_id: str | None = Field(
        None,
    )
    id_type: str | None = Field(
        None,
    )
    description: str | None = Field(None)


class StudyPharmaCM(BaseModel):
    unique_protocol_identification_number: str = Field(...)
    brief_title: str | None = Field(
        None,
    )
    official_title: str | None = Field(
        None,
    )
    acronym: str | None = Field(
        None,
    )
    study_type: str | None = Field(
        None,
    )
    secondary_ids: list[CompactRegistryIdentifier] = Field([])

    responsible_party: str = Field(
        "Sponsor",
    )
    primary_disease_or_condition_being_studied: list[str] = Field(
        [],
    )
    primary_purpose: list[str] = Field(
        [],
    )
    study_phase: str | None = Field(
        None,
    )
    interventional_study_model: str | None = Field(
        None,
    )
    number_of_arms: int | None = Field(
        None,
    )
    allocation: str | None = Field(
        None,
    )
    number_of_subjects: int | None = Field(
        None,
    )
    study_arms: list[CompactStudyArm] = Field([])
    intervention_type: str | None = Field(
        [],
    )
    outcome_measures: list[CompactOutcomeMeasure] = Field([])
    minimum_age: str | None = Field(None)
    maximum_age: str | None = Field(None)
    accepts_healthy_volunteers: bool | None = Field(None)
    inclusion_criteria: list[str] = Field([])
    exclusion_criteria: list[str] = Field([])

    @classmethod
    def from_various_data(
        cls,
        study: StudyDefinitionAR,
        study_arms: list[StudySelectionArmAR],
        study_endpoints: list[StudySelectionEndpoint],
        inclusion_criterias: list[StudySelectionCriteria],
        exclusion_criterias: list[StudySelectionCriteria],
        find_term_by_uid: Callable[[str], CTTermNameAR | None],
        find_dictionary_term_by_uid: Callable[[str], DictionaryTermAR | None],
        find_all_units: Callable[[], UnitDefinitionAR],
    ) -> Self:
        study_type = get_name_or_none(
            find_term_by_uid(
                term_uid=study.current_metadata.high_level_study_design.study_type_code
            )
        )
        is_trial_randomized = (
            study.current_metadata.study_intervention.is_trial_randomised
        )
        allocation_text = "randomized" if is_trial_randomized else "not randomized"
        planned_minimum_age = (
            study.current_metadata.study_population.planned_minimum_age_of_subjects
        )
        minimum_age, minimum_age_unit = (
            from_duration_object_to_value_and_unit(
                duration=planned_minimum_age,
                find_all_study_time_units=find_all_units,
            )
            if planned_minimum_age
            else (None, None)
        )
        minimum_age_str = (
            f"{minimum_age} {minimum_age_unit.name}" if minimum_age_unit else None
        )
        planned_maximum_age = (
            study.current_metadata.study_population.planned_maximum_age_of_subjects
        )
        maximum_age, maximum_age_unit = (
            from_duration_object_to_value_and_unit(
                duration=planned_maximum_age,
                find_all_study_time_units=find_all_units,
            )
            if planned_maximum_age
            else (None, None)
        )
        maximum_age_str = (
            f"{maximum_age} {maximum_age_unit.name}" if maximum_age_unit else None
        )
        number_of_arms = len(study_arms.study_arms_selection)
        secondary_ids = []
        registry_identifier = "Registry Identifier"
        other_identifier = "Other Identifier"
        eudract_number_identifier = "EudraCT Number"
        if study.current_metadata.id_metadata.registry_identifiers.eudract_id:
            secondary_ids.append(
                CompactRegistryIdentifier(
                    secondary_id=study.current_metadata.id_metadata.registry_identifiers.eudract_id,
                    id_type=eudract_number_identifier,
                    description="EUDRACT ID",
                )
            )
        if study.current_metadata.id_metadata.registry_identifiers.ct_gov_id:
            secondary_ids.append(
                CompactRegistryIdentifier(
                    secondary_id=study.current_metadata.id_metadata.registry_identifiers.ct_gov_id,
                    id_type=registry_identifier,
                    description="ClinicalTrials.gov ID",
                )
            )
        if (
            study.current_metadata.id_metadata.registry_identifiers.universal_trial_number_utn
        ):
            secondary_ids.append(
                CompactRegistryIdentifier(
                    secondary_id=study.current_metadata.id_metadata.registry_identifiers.universal_trial_number_utn,
                    id_type=other_identifier,
                    description="Universal Trial Number (UTN)",
                )
            )
        if (
            study.current_metadata.id_metadata.registry_identifiers.japanese_trial_registry_id_japic
        ):
            secondary_ids.append(
                CompactRegistryIdentifier(
                    secondary_id=study.current_metadata.id_metadata.registry_identifiers.japanese_trial_registry_id_japic,
                    id_type=registry_identifier,
                    description="Japanese Trial Registry ID (JAPIC)",
                )
            )
        if (
            study.current_metadata.id_metadata.registry_identifiers.investigational_new_drug_application_number_ind
        ):
            secondary_ids.append(
                CompactRegistryIdentifier(
                    secondary_id=study.current_metadata.id_metadata.registry_identifiers.investigational_new_drug_application_number_ind,
                    id_type=registry_identifier,
                    description="Investigational New Drug Application (IND) Number",
                )
            )
        if (
            study.current_metadata.id_metadata.registry_identifiers.national_clinical_trial_number
        ):
            secondary_ids.append(
                CompactRegistryIdentifier(
                    secondary_id=study.current_metadata.id_metadata.registry_identifiers.national_clinical_trial_number,
                    id_type=other_identifier,
                    description="National Clinical Trial Number",
                )
            )
        if (
            study.current_metadata.id_metadata.registry_identifiers.japanese_trial_registry_number_jrct
        ):
            secondary_ids.append(
                CompactRegistryIdentifier(
                    secondary_id=study.current_metadata.id_metadata.registry_identifiers.japanese_trial_registry_number_jrct,
                    id_type=registry_identifier,
                    description="Japanese Trial Registry Number",
                )
            )
        if (
            study.current_metadata.id_metadata.registry_identifiers.national_medical_products_administration_nmpa_number
        ):
            secondary_ids.append(
                CompactRegistryIdentifier(
                    secondary_id=study.current_metadata.id_metadata.registry_identifiers.national_medical_products_administration_nmpa_number,
                    id_type=other_identifier,
                    description="NMPA Number",
                )
            )
        if study.current_metadata.id_metadata.registry_identifiers.eudamed_srn_number:
            secondary_ids.append(
                CompactRegistryIdentifier(
                    secondary_id=study.current_metadata.id_metadata.registry_identifiers.eudamed_srn_number,
                    id_type=other_identifier,
                    description="EUDAMED number",
                )
            )
        if (
            study.current_metadata.id_metadata.registry_identifiers.investigational_device_exemption_ide_number
        ):
            secondary_ids.append(
                CompactRegistryIdentifier(
                    secondary_id=study.current_metadata.id_metadata.registry_identifiers.investigational_device_exemption_ide_number,
                    id_type=registry_identifier,
                )
            )
        return cls(
            unique_protocol_identification_number=f"{study.current_metadata.id_metadata.study_id_prefix}-{study.current_metadata.id_metadata.study_number}",
            brief_title=study.current_metadata.study_description.study_short_title,
            official_title=study.current_metadata.study_description.study_title,
            acronym=study.current_metadata.id_metadata.study_acronym,
            study_type=study_type,
            secondary_ids=secondary_ids,
            primary_disease_or_condition_being_studied=[
                find_dictionary_term_by_uid(term_uid=code).name
                for code in study.current_metadata.study_population.disease_condition_or_indication_codes
            ],
            primary_purpose=[
                find_term_by_uid(term_uid=code).name
                for code in study.current_metadata.study_intervention.trial_intent_types_codes
            ],
            study_phase=get_name_or_none(
                find_term_by_uid(
                    term_uid=study.current_metadata.high_level_study_design.trial_phase_code
                )
            ),
            interventional_study_model=get_name_or_none(
                find_term_by_uid(
                    term_uid=study.current_metadata.study_intervention.intervention_model_code
                )
            ),
            number_of_arms=number_of_arms,
            allocation="N/A" if study_type != "Interventional" else allocation_text,
            number_of_subjects=sum(
                study_arm.number_of_subjects
                for study_arm in study_arms.study_arms_selection
                if study_arm.number_of_subjects
            ),
            study_arms=[
                CompactStudyArm(
                    arm_type=get_name_or_none(
                        find_term_by_uid(term_uid=study_arm.arm_type_uid)
                    ),
                    arm_title=study_arm.name,
                    arm_description=study_arm.description,
                )
                for study_arm in study_arms.study_arms_selection
            ],
            intervention_type=get_name_or_none(
                find_term_by_uid(
                    term_uid=study.current_metadata.study_intervention.intervention_type_code
                )
            ),
            outcome_measures=[
                CompactOutcomeMeasure(
                    title=study_endpoint.study_objective.objective.name_plain
                    if study_endpoint.study_objective
                    else None,
                    timeframe=study_endpoint.timeframe.name_plain
                    if study_endpoint.timeframe
                    else None,
                    description=f" {study_endpoint.endpoint_units.separator} ".join(
                        [unit.name for unit in study_endpoint.endpoint_units.units]
                    )
                    if len(study_endpoint.endpoint_units.units) > 1
                    else "".join(
                        [unit.name for unit in study_endpoint.endpoint_units.units]
                    ),
                )
                for study_endpoint in study_endpoints
            ],
            minimum_age=minimum_age_str,
            maximum_age=maximum_age_str,
            accepts_healthy_volunteers=study.current_metadata.study_population.healthy_subject_indicator,
            inclusion_criteria=[
                inclusion_criteria.criteria.name_plain
                for inclusion_criteria in inclusion_criterias
            ],
            exclusion_criteria=[
                exclusion_criteria.criteria.name_plain
                for exclusion_criteria in exclusion_criterias
            ],
        )
