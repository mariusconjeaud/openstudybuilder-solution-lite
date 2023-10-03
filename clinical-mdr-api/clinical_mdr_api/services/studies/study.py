from datetime import datetime
from typing import Callable, Collection, Iterable, Sequence

from neomodel import db  # type: ignore

from clinical_mdr_api import exceptions
from clinical_mdr_api.config import DAY_UNIT_NAME
from clinical_mdr_api.domain_repositories.models._utils import CustomNodeSet
from clinical_mdr_api.domains.clinical_programmes.clinical_programme import (
    ClinicalProgrammeAR,
)
from clinical_mdr_api.domains.concepts.unit_definitions.unit_definition import (
    UnitDefinitionAR,
)
from clinical_mdr_api.domains.controlled_terminologies.ct_term_name import CTTermNameAR
from clinical_mdr_api.domains.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domains.projects.project import ProjectAR
from clinical_mdr_api.domains.study_definition_aggregates.registry_identifiers import (
    RegistryIdentifiersVO,
)
from clinical_mdr_api.domains.study_definition_aggregates.root import StudyDefinitionAR
from clinical_mdr_api.domains.study_definition_aggregates.study_metadata import (
    HighLevelStudyDesignVO,
    StudyComponentEnum,
    StudyDescriptionVO,
    StudyFieldAuditTrailEntryAR,
    StudyIdentificationMetadataVO,
    StudyInterventionVO,
    StudyPopulationVO,
    StudyStatus,
)
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.study_selections.study import (
    CompactStudy,
    HighLevelStudyDesignJsonModel,
    Study,
    StudyCreateInput,
    StudyDescriptionJsonModel,
    StudyFieldAuditTrailEntry,
    StudyIdentificationMetadataJsonModel,
    StudyInterventionJsonModel,
    StudyPatchRequestJsonModel,
    StudyPopulationJsonModel,
    StudyPreferredTimeUnit,
    StudyProtocolTitle,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._meta_repository import MetaRepository  # type: ignore
from clinical_mdr_api.services._utils import (  # type: ignore
    FieldsDirective,
    create_duration_object_from_api_input,
    fill_missing_values_in_base_model_from_reference_base_model,
    filter_base_model_using_fields_directive,
    get_term_uid_or_none,
    get_unit_def_uid_or_none,
    service_level_generic_filtering,
    service_level_generic_header_filtering,
)


class StudyService:
    _repos: MetaRepository

    def __init__(self, user=None):
        self.user = user
        if user is None:
            self.user = "TODO Initials"
        self._repos = MetaRepository(self.user)

    # and convenience method to close all repos
    def _close_all_repos(self) -> None:
        self._repos.close()

    @staticmethod
    def filter_result_by_requested_fields(result, fields: str | None = None):
        # here goes filtering according to value of fields query param
        default_fields = (
            "current_metadata.identification_metadata,"
            "current_metadata.version_metadata,"
            "uid,possible_actions,project_number,study_number,study_acronym,"
            "eudract_id,ct_gov_id,study_id,study_status"
        )
        mandatory_fields = "uid,study_status"
        # provide some default
        if fields is None or len(fields) == 0:
            fields = default_fields
        fields = "".join(fields.split())  # easy way to remove all white space
        # if starts with + or - we assume client specifies a difference so we prepend our default
        if fields[0] == "+" or fields[0] == "-":
            fields = default_fields + "," + fields
        else:
            fields = mandatory_fields + "," + fields
        result = filter_base_model_using_fields_directive(
            result, FieldsDirective.from_fields_query_parameter(fields)
        )
        return result

    @staticmethod
    def _models_study_from_study_definition_ar(
        study_definition_ar: StudyDefinitionAR,
        find_project_by_project_number: Callable[[str], ProjectAR],
        find_clinical_programme_by_uid: Callable[[str], ClinicalProgrammeAR],
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
        find_term_by_uid: Callable[[str], CTTermNameAR | None] = lambda _: None,
        find_dictionary_term_by_uid: Callable[
            [str], DictionaryTermAR | None
        ] = lambda _: None,
        fields: str | None = None,
        at_specified_date_time: datetime | None = None,
        status: StudyStatus | None = None,
        version: str | None = None,
        history_endpoint: bool = False,
    ) -> Study:
        result = Study.from_study_definition_ar(
            study_definition_ar=study_definition_ar,
            find_project_by_project_number=find_project_by_project_number,
            find_clinical_programme_by_uid=find_clinical_programme_by_uid,
            find_all_study_time_units=find_all_study_time_units,
            find_term_by_uid=find_term_by_uid,
            find_dictionary_term_by_uid=find_dictionary_term_by_uid,
            at_specified_date_time=at_specified_date_time,
            status=status,
            version=version,
            history_endpoint=history_endpoint,
        )
        return (
            StudyService.filter_result_by_requested_fields(result, fields)
            if result is not None
            else None
        )

    @staticmethod
    def _models_compact_study_from_study_definition_ar(
        study_definition_ar: StudyDefinitionAR,
        find_project_by_project_number: Callable[[str], ProjectAR],
        find_clinical_programme_by_uid: Callable[[str], ClinicalProgrammeAR],
        fields: str | None = None,
    ) -> CompactStudy:
        result = CompactStudy.from_study_definition_ar(
            study_definition_ar=study_definition_ar,
            find_project_by_project_number=find_project_by_project_number,
            find_clinical_programme_by_uid=find_clinical_programme_by_uid,
        )
        return (
            StudyService.filter_result_by_requested_fields(result, fields)
            if result is not None
            else None
        )

    def _models_study_protocol_title_from_study_definition_ar(
        self, study_definition_ar: StudyDefinitionAR
    ) -> StudyProtocolTitle:
        return StudyProtocolTitle.from_study_definition_ar(
            study_definition_ar,
            find_term_by_uid=self._repos.ct_term_name_repository.find_by_uid,
        )

    @staticmethod
    def determine_filtering_sections_set(
        default_sections, sections_selected
    ) -> Collection[str]:
        filtered_sections = default_sections
        for section in sections_selected:
            section = section.strip()
            if section.startswith("+"):
                if section[1:] in default_sections:
                    raise exceptions.ValidationException(
                        "The specified section "
                        + section[1:]
                        + " is a default section, and "
                        "is included by default. "
                        "Please remove this argument."
                    )
                filtered_sections.append(section[1:])
            elif section.startswith("-"):
                if section[1:] not in default_sections:
                    raise exceptions.ValidationException(
                        "The specified section "
                        + section[1:]
                        + " is not a default section, and "
                        "cannot be filtered out."
                    )
                filtered_sections.remove(section[1:])
            else:
                raise exceptions.ValidationException(
                    "Specify a list of sections to filter the audit trail by. "
                    "Each section name must be preceded by a '+' or a '-', "
                    "valid values are: 'identification_metadata, registry_identifiers, version_metadata, "
                    "high_level_study_design, study_population, study_intervention, study_description'. "
                    "Example valid input: '-identification_metadata,+study_population'."
                )
        return filtered_sections

    @db.transaction
    def get_by_uid(
        self,
        uid: str,
        at_specified_date_time: datetime | None = None,
        status: StudyStatus | None = None,
        version: str | None = None,
        fields: str | None = None,
    ) -> Study:
        try:
            # call relevant finder (we use helper property to get to the repository)
            study_definition = self._repos.study_definition_repository.find_by_uid(
                uid=uid,
            )
            if study_definition is None:
                raise exceptions.NotFoundException(
                    f"StudyDefinition '{uid}' not found."
                )
            return self._models_study_from_study_definition_ar(
                study_definition_ar=study_definition,
                find_project_by_project_number=self._repos.project_repository.find_by_project_number,
                find_clinical_programme_by_uid=self._repos.clinical_programme_repository.find_by_uid,
                find_all_study_time_units=self._repos.unit_definition_repository.find_all,
                find_term_by_uid=self._repos.ct_term_name_repository.find_by_uid,
                find_dictionary_term_by_uid=self._repos.dictionary_term_generic_repository.find_by_uid,
                fields=fields,
                at_specified_date_time=at_specified_date_time,
                status=status,
                version=version,
            )
        finally:
            self._close_all_repos()

    @db.transaction
    def lock(self, uid: str, change_description: str) -> Study:
        try:
            study_definition = self._repos.study_definition_repository.find_by_uid(
                uid, for_update=True
            )
            if study_definition is None:
                raise exceptions.NotFoundException(
                    f"StudyDefinition '{uid}' not found."
                )
            study_definition.lock(
                version_description=change_description,
                version_author=self.user,
            )
            self._repos.study_definition_repository.save(study_definition)
            return self._models_study_from_study_definition_ar(
                study_definition_ar=study_definition,
                find_project_by_project_number=self._repos.project_repository.find_by_project_number,
                find_clinical_programme_by_uid=self._repos.clinical_programme_repository.find_by_uid,
                find_all_study_time_units=self._repos.unit_definition_repository.find_all,
                find_term_by_uid=self._repos.ct_term_name_repository.find_by_uid,
                find_dictionary_term_by_uid=self._repos.dictionary_term_generic_repository.find_by_uid,
            )
        finally:
            self._close_all_repos()

    @db.transaction
    def unlock(self, uid: str) -> Study:
        try:
            study_definition = self._repos.study_definition_repository.find_by_uid(
                uid, for_update=True
            )
            if study_definition is None:
                raise exceptions.NotFoundException(
                    f"StudyDefinition '{uid}' not found."
                )
            study_definition.unlock()
            self._repos.study_definition_repository.save(study_definition)
            return self._models_study_from_study_definition_ar(
                study_definition_ar=study_definition,
                find_project_by_project_number=self._repos.project_repository.find_by_project_number,
                find_clinical_programme_by_uid=self._repos.clinical_programme_repository.find_by_uid,
                find_all_study_time_units=self._repos.unit_definition_repository.find_all,
                find_term_by_uid=self._repos.ct_term_name_repository.find_by_uid,
                find_dictionary_term_by_uid=self._repos.dictionary_term_generic_repository.find_by_uid,
            )
        finally:
            self._close_all_repos()

    @db.transaction
    def release(self, uid: str, change_description: str | None) -> Study:
        try:
            study_definition = self._repos.study_definition_repository.find_by_uid(
                uid, for_update=True
            )
            if study_definition is None:
                raise exceptions.NotFoundException(
                    f"StudyDefinition '{uid}' not found."
                )
            study_definition.release(change_description=change_description)
            self._repos.study_definition_repository.save(study_definition)
            return self._models_study_from_study_definition_ar(
                study_definition_ar=study_definition,
                find_project_by_project_number=self._repos.project_repository.find_by_project_number,
                find_clinical_programme_by_uid=self._repos.clinical_programme_repository.find_by_uid,
                find_all_study_time_units=self._repos.unit_definition_repository.find_all,
                find_term_by_uid=self._repos.ct_term_name_repository.find_by_uid,
                find_dictionary_term_by_uid=self._repos.dictionary_term_generic_repository.find_by_uid,
            )
        finally:
            self._close_all_repos()

    @db.transaction
    def soft_delete(self, uid: str) -> None:
        try:
            study_definition = self._repos.study_definition_repository.find_by_uid(
                uid, for_update=True
            )
            if study_definition is None:
                raise exceptions.NotFoundException(
                    f"StudyDefinition '{uid}' not found."
                )
            study_definition.mark_deleted()
            self._repos.study_definition_repository.save(study_definition)
        finally:
            self._close_all_repos()

    @staticmethod
    def _models_study_field_audit_trail_from_audit_trail_vo(
        study_audit_trail_vo_sequence: Iterable[StudyFieldAuditTrailEntryAR],
        find_term_by_uid: Callable[[str], CTTermNameAR | None],
        sections: str | None = None,
    ) -> Sequence[StudyFieldAuditTrailEntry]:
        # Create entries from the audit trail value objects and filter by section.
        all_sections = [
            "identification_metadata",
            "registry_identifiers",
            "version_metadata",
            "high_level_study_design",
            "study_population",
            "study_intervention",
            "study_description",
            "Unknown",
        ]
        default_sections = ["identification_metadata", "version_metadata"]
        # If no filter is specified, return all default sections of the audit trail.
        # Else, use filtering.
        sections_selected = (
            StudyService.determine_filtering_sections_set(
                default_sections, sections.strip().split(",")
            )
            if sections is not None and sections.strip() != ""
            else all_sections
        )

        result = [
            StudyFieldAuditTrailEntry.from_study_field_audit_trail_vo(
                study_audit_trail_vo, sections_selected, find_term_by_uid
            )
            for study_audit_trail_vo in study_audit_trail_vo_sequence
        ]

        # Only return entries that have at least one audit trail action in them.
        result = [entry for entry in result if len(entry.actions) > 0]

        return result

    @db.transaction
    def get_fields_audit_trail_by_uid(
        self, uid: str, sections: str | None = None
    ) -> Sequence[StudyFieldAuditTrailEntry] | None:
        try:
            # call relevant finder (we use helper property to get to the repository)
            study_fields_audit_trail_vo_sequence = (
                self._repos.study_definition_repository.get_audit_trail_by_uid(uid)
            )

            if study_fields_audit_trail_vo_sequence is None:
                raise exceptions.NotFoundException(f"The study '{uid}' was not found.")

            # Filter to see only the relevant sections.
            result = self._models_study_field_audit_trail_from_audit_trail_vo(
                study_audit_trail_vo_sequence=study_fields_audit_trail_vo_sequence,
                sections=sections,
                find_term_by_uid=self._repos.ct_term_name_repository.find_by_uid,
            )
            return result
        finally:
            self._close_all_repos()

    def get_all(
        self,
        has_study_objective: bool | None = None,
        has_study_endpoint: bool | None = None,
        has_study_criteria: bool | None = None,
        has_study_activity: bool | None = None,
        has_study_activity_instruction: bool | None = None,
        sort_by: dict | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        total_count: bool = False,
        deleted: bool = False,
    ) -> GenericFilteringReturn[CompactStudy]:
        try:
            # Note that for this endpoint, we have to override the generic filtering
            # Some transformation logic is happening from an aggregated object to the pydantic return model
            # This logic prevents us from doing the filtering, sorting, and pagination on the Cypher side
            # Consequently, this has to be done here in the service layer
            all_items = self._repos.study_definition_repository.find_all(
                has_study_objective=has_study_objective,
                has_study_endpoint=has_study_endpoint,
                has_study_criteria=has_study_criteria,
                has_study_activity=has_study_activity,
                has_study_activity_instruction=has_study_activity_instruction,
                sort_by={},
                total_count=False,
                filter_by={},
                deleted=deleted,
            )

            if not sort_by:
                sort_by = {"uid": True}

            # then prepare and return response of our service
            parsed_items = [
                self._models_compact_study_from_study_definition_ar(
                    study_definition_ar=item,
                    find_project_by_project_number=self._repos.project_repository.find_by_project_number,
                    find_clinical_programme_by_uid=self._repos.clinical_programme_repository.find_by_uid,
                    fields=None,
                )
                for item in all_items.items
            ]

            # Do filtering, sorting, pagination and count
            filtered_items = service_level_generic_filtering(
                items=parsed_items,
                filter_by=filter_by,
                filter_operator=filter_operator,
                sort_by=sort_by,
                total_count=total_count,
                page_number=page_number,
                page_size=page_size,
            )

            return filtered_items

        finally:
            self._close_all_repos()

    def get_study_snapshot_history(
        self,
        study_uid: str,
        sort_by: dict | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        total_count: bool = False,
    ) -> GenericFilteringReturn[CompactStudy]:
        try:
            if not sort_by:
                sort_by = {}

            all_items = (
                self._repos.study_definition_repository.find_study_snapshot_history(
                    study_uid=study_uid,
                    sort_by=sort_by,
                    page_number=page_number,
                    page_size=page_size,
                    filter_by=filter_by,
                    filter_operator=filter_operator,
                    total_count=total_count,
                )
            )

            parsed_items = [
                CompactStudy.from_study_definition_ar(
                    study_definition_ar=item,
                    find_project_by_project_number=self._repos.project_repository.find_by_project_number,
                    find_clinical_programme_by_uid=self._repos.clinical_programme_repository.find_by_uid,
                )
                for item in all_items.items
            ]
            all_items.items = parsed_items
            return all_items
        finally:
            self._close_all_repos()

    def get_distinct_values_for_header(
        self,
        field_name: str,
        search_string: str | None = "",
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        result_count: int = 10,
    ):
        # Note that for this endpoint, we have to override the generic filtering
        # Some transformation logic is happening from an aggregated object to the pydantic return model
        # This logic prevents us from doing the filtering, sorting, and pagination on the Cypher side
        # Consequently, this has to be done here in the service layer
        all_items = self._repos.study_definition_repository.find_all(
            sort_by={}, total_count=False, filter_by={}
        )

        parsed_items = [
            self._models_study_from_study_definition_ar(
                study_definition_ar=item,
                find_project_by_project_number=self._repos.project_repository.find_by_project_number,
                find_clinical_programme_by_uid=self._repos.clinical_programme_repository.find_by_uid,
                find_all_study_time_units=self._repos.unit_definition_repository.find_all,
            )
            for item in all_items.items
        ]

        # Do filtering, sorting, pagination and count
        header_values = service_level_generic_header_filtering(
            items=parsed_items,
            field_name=field_name,
            search_string=search_string,
            filter_by=filter_by,
            filter_operator=filter_operator,
            result_count=result_count,
        )
        # Return values for field_name
        return header_values

    def get_protocol_title(self, uid: str) -> StudyProtocolTitle:
        try:
            study_definition = self._repos.study_definition_repository.find_by_uid(uid)
            if study_definition is None:
                raise exceptions.NotFoundException(
                    f"StudyDefinition '{uid}' not found."
                )
            result = self._models_study_protocol_title_from_study_definition_ar(
                study_definition
            )
            compound_selection_ar = self._repos.study_compound_repository.find_by_study(
                uid, type_of_treatment="Investigational Product"
            )
            names = []
            for study_compound in compound_selection_ar.study_compounds_selection:
                compound = self._repos.compound_repository.find_by_uid_2(
                    study_compound.compound_uid
                )
                names.append(compound.name)
            if names:
                result.substance_name = ", ".join(names)
            return result
        finally:
            self._close_all_repos()

    @db.transaction
    def create(self, study_create_input: StudyCreateInput) -> Study:
        try:
            # now we invoke our domain layer
            study_definition = StudyDefinitionAR.from_initial_values(
                generate_uid_callback=self._repos.study_definition_repository.generate_uid,
                project_exists_callback=self._repos.project_repository.project_number_exists,
                study_title_exists_callback=self._repos.study_title_repository.study_title_exists,
                study_short_title_exists_callback=self._repos.study_title_repository.study_short_title_exists,
                study_number_exists_callback=self._repos.study_definition_repository.study_number_exists,
                initial_id_metadata=StudyIdentificationMetadataVO.from_input_values(
                    project_number=study_create_input.project_number,
                    study_number=study_create_input.study_number,
                    study_acronym=study_create_input.study_acronym,
                    # Not added on study create
                    registry_identifiers=RegistryIdentifiersVO(
                        ct_gov_id=None,
                        ct_gov_id_null_value_code=None,
                        eudract_id=None,
                        eudract_id_null_value_code=None,
                        universal_trial_number_utn=None,
                        universal_trial_number_utn_null_value_code=None,
                        japanese_trial_registry_id_japic=None,
                        japanese_trial_registry_id_japic_null_value_code=None,
                        investigational_new_drug_application_number_ind=None,
                        investigational_new_drug_application_number_ind_null_value_code=None,
                    ),
                ),
            )

            # save the aggregate instance we have just created
            self._repos.study_definition_repository.save(study_definition)

            # create default time unit pointing to 'Day' Unit Definition
            self.post_study_preferred_time_unit(
                study_uid=study_definition.uid,
                unit_definition_uid=self._repos.unit_definition_repository.find_uid_by_name(
                    DAY_UNIT_NAME
                ),
            )

            # then prepare and return our response
            return_item = self._models_study_from_study_definition_ar(
                study_definition,
                find_project_by_project_number=self._repos.project_repository.find_by_project_number,
                find_clinical_programme_by_uid=self._repos.clinical_programme_repository.find_by_uid,
                find_all_study_time_units=self._repos.unit_definition_repository.find_all,
            )
            return return_item
        finally:
            self._close_all_repos()

    @staticmethod
    def _patch_prepare_new_study_intervention(
        current_study_intervention: StudyInterventionVO,
        request_study_intervention: StudyInterventionJsonModel,
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
        find_unit_definition_by_uid: Callable[[str], UnitDefinitionAR | None],
    ) -> StudyInterventionVO:
        fill_missing_values_in_base_model_from_reference_base_model(
            base_model_with_missing_values=request_study_intervention,
            reference_base_model=StudyInterventionJsonModel.from_study_intervention_vo(
                study_intervention_vo=current_study_intervention,
                find_all_study_time_units=find_all_study_time_units,
                find_term_by_uid=lambda _: None,
            ),
        )

        # we start a try block to catch any ValueError and report as Forbidden (otherwise it would be
        # reported as Internal)
        new_study_intervention = StudyInterventionVO.from_input_values(
            intervention_type_code=get_term_uid_or_none(
                request_study_intervention.intervention_type_code
            ),
            intervention_type_null_value_code=get_term_uid_or_none(
                request_study_intervention.intervention_type_null_value_code
            ),
            add_on_to_existing_treatments=request_study_intervention.add_on_to_existing_treatments,
            add_on_to_existing_treatments_null_value_code=get_term_uid_or_none(
                request_study_intervention.add_on_to_existing_treatments_null_value_code
            ),
            control_type_code=get_term_uid_or_none(
                request_study_intervention.control_type_code
            ),
            control_type_null_value_code=get_term_uid_or_none(
                request_study_intervention.control_type_null_value_code
            ),
            intervention_model_code=get_term_uid_or_none(
                request_study_intervention.intervention_model_code
            ),
            intervention_model_null_value_code=get_term_uid_or_none(
                request_study_intervention.intervention_model_null_value_code
            ),
            is_trial_randomised=request_study_intervention.is_trial_randomised,
            is_trial_randomised_null_value_code=get_term_uid_or_none(
                request_study_intervention.is_trial_randomised_null_value_code
            ),
            stratification_factor=request_study_intervention.stratification_factor,
            stratification_factor_null_value_code=get_term_uid_or_none(
                request_study_intervention.stratification_factor_null_value_code
            ),
            trial_blinding_schema_code=get_term_uid_or_none(
                request_study_intervention.trial_blinding_schema_code
            ),
            trial_blinding_schema_null_value_code=get_term_uid_or_none(
                request_study_intervention.trial_blinding_schema_null_value_code
            ),
            trial_intent_types_codes=[
                get_term_uid_or_none(trial_intent_type_code)
                for trial_intent_type_code in request_study_intervention.trial_intent_types_codes
            ]
            if request_study_intervention.trial_intent_types_codes
            else [],
            trial_intent_type_null_value_code=get_term_uid_or_none(
                request_study_intervention.trial_intent_types_null_value_code
            ),
            planned_study_length=(
                create_duration_object_from_api_input(
                    value=request_study_intervention.planned_study_length.duration_value,
                    unit=get_unit_def_uid_or_none(
                        request_study_intervention.planned_study_length.duration_unit_code
                    ),
                    find_duration_name_by_code=find_unit_definition_by_uid,
                )
                if request_study_intervention.planned_study_length is not None
                else None
            ),
            planned_study_length_null_value_code=get_term_uid_or_none(
                request_study_intervention.planned_study_length_null_value_code
            ),
        )

        return new_study_intervention

    @staticmethod
    def _patch_prepare_new_study_population(
        current_study_population: StudyPopulationVO,
        request_study_population: StudyPopulationJsonModel,
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
        find_unit_definition_by_uid: Callable[[str], UnitDefinitionAR | None],
    ) -> StudyPopulationVO:
        fill_missing_values_in_base_model_from_reference_base_model(
            base_model_with_missing_values=request_study_population,
            reference_base_model=StudyPopulationJsonModel.from_study_population_vo(
                study_population_vo=current_study_population,
                find_all_study_time_units=find_all_study_time_units,
                find_term_by_uid=lambda _: None,
                find_dictionary_term_by_uid=lambda _: None,
            ),
        )

        def _helper(array: Sequence | None) -> Sequence:
            return array if array is not None else []

        new_study_population = StudyPopulationVO.from_input_values(
            therapeutic_area_codes=[
                get_term_uid_or_none(therapeutic_area)
                for therapeutic_area in _helper(
                    request_study_population.therapeutic_area_codes
                )
            ],
            therapeutic_area_null_value_code=get_term_uid_or_none(
                request_study_population.therapeutic_area_null_value_code
            ),
            disease_condition_or_indication_codes=[
                get_term_uid_or_none(disease_condition)
                for disease_condition in _helper(
                    request_study_population.disease_condition_or_indication_codes
                )
            ],
            disease_condition_or_indication_null_value_code=get_term_uid_or_none(
                request_study_population.disease_condition_or_indication_null_value_code
            ),
            diagnosis_group_codes=[
                get_term_uid_or_none(diagnosis_group)
                for diagnosis_group in _helper(
                    request_study_population.diagnosis_group_codes
                )
            ],
            diagnosis_group_null_value_code=get_term_uid_or_none(
                request_study_population.diagnosis_group_null_value_code
            ),
            sex_of_participants_code=get_term_uid_or_none(
                request_study_population.sex_of_participants_code
            ),
            sex_of_participants_null_value_code=get_term_uid_or_none(
                request_study_population.sex_of_participants_null_value_code
            ),
            rare_disease_indicator=request_study_population.rare_disease_indicator,
            rare_disease_indicator_null_value_code=get_term_uid_or_none(
                request_study_population.rare_disease_indicator_null_value_code
            ),
            healthy_subject_indicator=request_study_population.healthy_subject_indicator,
            healthy_subject_indicator_null_value_code=get_term_uid_or_none(
                request_study_population.healthy_subject_indicator_null_value_code
            ),
            planned_minimum_age_of_subjects_null_value_code=get_term_uid_or_none(
                request_study_population.planned_minimum_age_of_subjects_null_value_code
            ),
            planned_maximum_age_of_subjects_null_value_code=get_term_uid_or_none(
                request_study_population.planned_maximum_age_of_subjects_null_value_code
            ),
            stable_disease_minimum_duration_null_value_code=get_term_uid_or_none(
                request_study_population.stable_disease_minimum_duration_null_value_code
            ),
            planned_minimum_age_of_subjects=(
                create_duration_object_from_api_input(
                    value=request_study_population.planned_minimum_age_of_subjects.duration_value,
                    unit=get_unit_def_uid_or_none(
                        request_study_population.planned_minimum_age_of_subjects.duration_unit_code
                    ),
                    find_duration_name_by_code=find_unit_definition_by_uid,
                )
                if request_study_population.planned_minimum_age_of_subjects
                else None
            ),
            planned_maximum_age_of_subjects=(
                create_duration_object_from_api_input(
                    value=request_study_population.planned_maximum_age_of_subjects.duration_value,
                    unit=get_unit_def_uid_or_none(
                        request_study_population.planned_maximum_age_of_subjects.duration_unit_code
                    ),
                    find_duration_name_by_code=find_unit_definition_by_uid,
                )
                if request_study_population.planned_maximum_age_of_subjects is not None
                else None
            ),
            stable_disease_minimum_duration=(
                create_duration_object_from_api_input(
                    value=request_study_population.stable_disease_minimum_duration.duration_value,
                    unit=get_unit_def_uid_or_none(
                        request_study_population.stable_disease_minimum_duration.duration_unit_code
                    ),
                    find_duration_name_by_code=find_unit_definition_by_uid,
                )
                if request_study_population.stable_disease_minimum_duration is not None
                else None
            ),
            pediatric_study_indicator=request_study_population.pediatric_study_indicator,
            pediatric_study_indicator_null_value_code=get_term_uid_or_none(
                request_study_population.pediatric_study_indicator_null_value_code
            ),
            pediatric_postmarket_study_indicator=request_study_population.pediatric_postmarket_study_indicator,
            pediatric_postmarket_study_indicator_null_value_code=get_term_uid_or_none(
                request_study_population.pediatric_postmarket_study_indicator_null_value_code
            ),
            pediatric_investigation_plan_indicator=request_study_population.pediatric_investigation_plan_indicator,
            pediatric_investigation_plan_indicator_null_value_code=get_term_uid_or_none(
                request_study_population.pediatric_investigation_plan_indicator_null_value_code
            ),
            relapse_criteria=request_study_population.relapse_criteria,
            relapse_criteria_null_value_code=get_term_uid_or_none(
                request_study_population.relapse_criteria_null_value_code
            ),
            number_of_expected_subjects=request_study_population.number_of_expected_subjects,
            number_of_expected_subjects_null_value_code=get_term_uid_or_none(
                request_study_population.number_of_expected_subjects_null_value_code
            ),
        )

        return new_study_population

    @staticmethod
    def _patch_prepare_new_high_level_study_design(
        current_high_level_study_design: HighLevelStudyDesignVO,
        request_high_level_study_design: HighLevelStudyDesignJsonModel,
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
        find_unit_definition_by_uid: Callable[[str], UnitDefinitionAR | None],
    ) -> HighLevelStudyDesignVO:
        # now we go through fields of request and for those which were not set in the request
        # we substitute values from current metadata
        fill_missing_values_in_base_model_from_reference_base_model(
            base_model_with_missing_values=request_high_level_study_design,
            reference_base_model=(
                HighLevelStudyDesignJsonModel.from_high_level_study_design_vo(
                    high_level_study_design_vo=current_high_level_study_design,
                    find_term_by_uid=lambda _: None,
                    find_all_study_time_units=find_all_study_time_units,
                )
            ),
        )

        # we start a try block to catch any ValueError and report as Forbidden (otherwise it would be
        # reported as Internal)
        def _helper(array: Sequence | None) -> Sequence:
            return array if array is not None else []

        new_high_level_study_design = HighLevelStudyDesignVO.from_input_values(
            study_type_code=get_term_uid_or_none(
                request_high_level_study_design.study_type_code
            ),
            study_stop_rules=request_high_level_study_design.study_stop_rules,
            study_stop_rules_null_value_code=get_term_uid_or_none(
                request_high_level_study_design.study_stop_rules_null_value_code
            ),
            study_type_null_value_code=get_term_uid_or_none(
                request_high_level_study_design.study_type_null_value_code
            ),
            trial_type_codes=[
                get_term_uid_or_none(trial_type_code)
                for trial_type_code in _helper(
                    request_high_level_study_design.trial_type_codes
                )
            ],
            trial_type_null_value_code=get_term_uid_or_none(
                request_high_level_study_design.trial_type_null_value_code
            ),
            trial_phase_code=get_term_uid_or_none(
                request_high_level_study_design.trial_phase_code
            ),
            trial_phase_null_value_code=get_term_uid_or_none(
                request_high_level_study_design.trial_phase_null_value_code
            ),
            is_extension_trial=request_high_level_study_design.is_extension_trial,
            is_extension_trial_null_value_code=get_term_uid_or_none(
                request_high_level_study_design.is_extension_trial_null_value_code
            ),
            is_adaptive_design=request_high_level_study_design.is_adaptive_design,
            is_adaptive_design_null_value_code=get_term_uid_or_none(
                request_high_level_study_design.is_adaptive_design_null_value_code
            ),
            confirmed_response_minimum_duration=(
                create_duration_object_from_api_input(
                    value=request_high_level_study_design.confirmed_response_minimum_duration.duration_value,
                    unit=get_unit_def_uid_or_none(
                        request_high_level_study_design.confirmed_response_minimum_duration.duration_unit_code
                    ),
                    find_duration_name_by_code=find_unit_definition_by_uid,
                )
                if request_high_level_study_design.confirmed_response_minimum_duration
                is not None
                else None
            ),
            confirmed_response_minimum_duration_null_value_code=get_term_uid_or_none(
                request_high_level_study_design.confirmed_response_minimum_duration_null_value_code
            ),
            post_auth_indicator=request_high_level_study_design.post_auth_indicator,
            post_auth_indicator_null_value_code=get_term_uid_or_none(
                request_high_level_study_design.post_auth_indicator_null_value_code
            ),
        )

        return new_high_level_study_design

    @staticmethod
    def _patch_prepare_new_id_metadata(
        current_id_metadata: StudyIdentificationMetadataVO,
        request_id_metadata: StudyIdentificationMetadataJsonModel,
        find_project_by_project_number: Callable[[str], ProjectAR],
        find_clinical_programme_by_uid: Callable[[str], ClinicalProgrammeAR],
    ) -> StudyIdentificationMetadataVO:
        fill_missing_values_in_base_model_from_reference_base_model(
            base_model_with_missing_values=request_id_metadata,
            reference_base_model=StudyIdentificationMetadataJsonModel.from_study_identification_vo(
                study_identification_o=current_id_metadata,
                find_project_by_project_number=find_project_by_project_number,
                find_clinical_programme_by_uid=find_clinical_programme_by_uid,
                find_term_by_uid=lambda _: None,
            ),
        )

        assert request_id_metadata.registry_identifiers is not None
        new_id_metadata = StudyIdentificationMetadataVO.from_input_values(
            project_number=request_id_metadata.project_number,
            study_number=request_id_metadata.study_number,
            study_acronym=request_id_metadata.study_acronym,
            registry_identifiers=RegistryIdentifiersVO.from_input_values(
                ct_gov_id=request_id_metadata.registry_identifiers.ct_gov_id,
                ct_gov_id_null_value_code=get_term_uid_or_none(
                    request_id_metadata.registry_identifiers.ct_gov_id_null_value_code
                ),
                eudract_id=request_id_metadata.registry_identifiers.eudract_id,
                eudract_id_null_value_code=get_term_uid_or_none(
                    request_id_metadata.registry_identifiers.eudract_id_null_value_code
                ),
                universal_trial_number_utn=request_id_metadata.registry_identifiers.universal_trial_number_utn,
                universal_trial_number_utn_null_value_code=get_term_uid_or_none(
                    request_id_metadata.registry_identifiers.universal_trial_number_utn_null_value_code
                ),
                japanese_trial_registry_id_japic=request_id_metadata.registry_identifiers.japanese_trial_registry_id_japic,
                japanese_trial_registry_id_japic_null_value_code=get_term_uid_or_none(
                    request_id_metadata.registry_identifiers.japanese_trial_registry_id_japic_null_value_code
                ),
                investigational_new_drug_application_number_ind=(
                    request_id_metadata.registry_identifiers.investigational_new_drug_application_number_ind
                ),
                investigational_new_drug_application_number_ind_null_value_code=get_term_uid_or_none(
                    request_id_metadata.registry_identifiers.investigational_new_drug_application_number_ind_null_value_code
                ),
            ),
        )

        return new_id_metadata

    @staticmethod
    def _patch_prepare_new_study_description_metadata(
        current_study_description_metadata: StudyDescriptionVO,
        request_study_description_metadata: StudyDescriptionJsonModel,
    ) -> StudyDescriptionVO:
        fill_missing_values_in_base_model_from_reference_base_model(
            base_model_with_missing_values=request_study_description_metadata,
            reference_base_model=StudyDescriptionJsonModel.from_study_description_vo(
                study_description_vo=current_study_description_metadata
            ),
        )

        new_id_metadata = StudyDescriptionVO.from_input_values(
            study_title=request_study_description_metadata.study_title,
            study_short_title=request_study_description_metadata.study_short_title,
        )

        return new_id_metadata

    @db.transaction
    def patch(
        self,
        uid: str,
        dry: bool,
        study_patch_request: StudyPatchRequestJsonModel,
        fields: str | None = None,
    ) -> Study:
        try:
            study_definition_ar = self._repos.study_definition_repository.find_by_uid(
                uid, for_update=not dry
            )

            if study_definition_ar is None:  # there's no such study
                raise exceptions.NotFoundException(
                    f"The study with UID '{uid}' cannot be found."
                )

            new_id_metadata: StudyIdentificationMetadataVO | None = None
            new_high_level_study_design: HighLevelStudyDesignVO | None = None
            new_study_population: StudyPopulationVO | None = None
            new_study_intervention: StudyInterventionVO | None = None
            new_study_description: StudyDescriptionVO | None = None

            if (
                study_patch_request.current_metadata is not None
                and study_patch_request.current_metadata.identification_metadata
                is not None
            ):
                new_id_metadata = self._patch_prepare_new_id_metadata(
                    current_id_metadata=study_definition_ar.current_metadata.id_metadata,
                    request_id_metadata=study_patch_request.current_metadata.identification_metadata,
                    find_project_by_project_number=self._repos.project_repository.find_by_project_number,
                    find_clinical_programme_by_uid=self._repos.clinical_programme_repository.find_by_uid,
                )

            if (
                study_patch_request.current_metadata is not None
                and study_patch_request.current_metadata.high_level_study_design
                is not None
            ):
                new_high_level_study_design = self._patch_prepare_new_high_level_study_design(
                    current_high_level_study_design=study_definition_ar.current_metadata.high_level_study_design,
                    request_high_level_study_design=study_patch_request.current_metadata.high_level_study_design,
                    find_all_study_time_units=self._repos.unit_definition_repository.find_all,
                    find_unit_definition_by_uid=self._repos.unit_definition_repository.find_by_uid_2,
                )

            if (
                study_patch_request.current_metadata is not None
                and study_patch_request.current_metadata.study_population is not None
            ):
                new_study_population = self._patch_prepare_new_study_population(
                    current_study_population=study_definition_ar.current_metadata.study_population,
                    request_study_population=study_patch_request.current_metadata.study_population,
                    find_all_study_time_units=self._repos.unit_definition_repository.find_all,
                    find_unit_definition_by_uid=self._repos.unit_definition_repository.find_by_uid_2,
                )

            if (
                study_patch_request.current_metadata is not None
                and study_patch_request.current_metadata.study_intervention is not None
            ):
                new_study_intervention = self._patch_prepare_new_study_intervention(
                    current_study_intervention=study_definition_ar.current_metadata.study_intervention,
                    request_study_intervention=study_patch_request.current_metadata.study_intervention,
                    find_all_study_time_units=self._repos.unit_definition_repository.find_all,
                    find_unit_definition_by_uid=self._repos.unit_definition_repository.find_by_uid_2,
                )

            if (
                study_patch_request.current_metadata is not None
                and study_patch_request.current_metadata.study_description is not None
            ):
                new_study_description = self._patch_prepare_new_study_description_metadata(
                    current_study_description_metadata=study_definition_ar.current_metadata.study_description,
                    request_study_description_metadata=study_patch_request.current_metadata.study_description,
                )

            study_definition_ar.edit_metadata(
                new_id_metadata=new_id_metadata,
                project_exists_callback=self._repos.project_repository.project_number_exists,
                new_high_level_study_design=new_high_level_study_design,
                study_type_exists_callback=self._repos.ct_term_name_repository.term_exists,
                trial_type_exists_callback=self._repos.ct_term_name_repository.term_exists,
                trial_intent_type_exists_callback=self._repos.ct_term_name_repository.term_exists,
                trial_phase_exists_callback=self._repos.ct_term_name_repository.term_exists,
                null_value_exists_callback=self._repos.ct_term_name_repository.term_exists,
                new_study_population=new_study_population,
                therapeutic_area_exists_callback=self._repos.dictionary_term_generic_repository.term_exists,
                disease_condition_or_indication_exists_callback=self._repos.dictionary_term_generic_repository.term_exists,
                diagnosis_group_exists_callback=self._repos.dictionary_term_generic_repository.term_exists,
                sex_of_participants_exists_callback=self._repos.ct_term_name_repository.term_exists,
                new_study_intervention=new_study_intervention,
                new_study_description=new_study_description,
                study_title_exists_callback=self._repos.study_title_repository.study_title_exists,
                study_short_title_exists_callback=self._repos.study_title_repository.study_short_title_exists,
                # add here valid callbacks
                intervention_type_exists_callback=self._repos.ct_term_name_repository.term_exists,
                control_type_exists_callback=self._repos.ct_term_name_repository.term_exists,
                intervention_model_exists_callback=self._repos.ct_term_name_repository.term_exists,
                trial_blinding_schema_exists_callback=self._repos.ct_term_name_repository.term_exists,
            )

            # now if we are not running in dry mode we can save the instance
            if not dry:
                self._repos.study_definition_repository.save(study_definition_ar)

            return self._models_study_from_study_definition_ar(
                study_definition_ar,
                find_project_by_project_number=self._repos.project_repository.find_by_project_number,
                find_clinical_programme_by_uid=self._repos.clinical_programme_repository.find_by_uid,
                find_all_study_time_units=self._repos.unit_definition_repository.find_all,
                fields=fields,
            )
        finally:
            self._close_all_repos()

    def copy_component_from_another_study(
        self,
        uid: str,
        reference_study_uid: str,
        component_to_copy: StudyComponentEnum,
        overwrite: bool,
    ):
        fields = f"+current_metadata.{component_to_copy.value}"
        study = self.get_by_uid(uid=uid, fields=fields)
        reference_study = self.get_by_uid(uid=reference_study_uid, fields=fields)

        base_study_component = getattr(study.current_metadata, component_to_copy.value)
        reference_study_component = getattr(
            reference_study.current_metadata, component_to_copy.value
        )
        if overwrite:
            setattr(
                study.current_metadata,
                component_to_copy.value,
                reference_study_component,
            )
        else:
            for name, _ in base_study_component.__fields__.items():
                if not getattr(base_study_component, name):
                    setattr(
                        base_study_component,
                        name,
                        getattr(reference_study_component, name),
                    )
        return study

    def check_if_study_is_locked(self, study_uid: str):
        return self._repos.study_definition_repository.check_if_study_is_locked(
            study_uid=study_uid
        )

    def check_if_study_exists(self, study_uid: str):
        if not self._repos.study_definition_repository.study_exists_by_uid(
            study_uid=study_uid
        ):
            raise exceptions.NotFoundException(
                f"Study with specified uid '{study_uid}' was not found."
            )

    def _check_if_unit_definition_exists(self, unit_definition_uid: str):
        if not self._repos.unit_definition_repository.final_concept_exists(
            uid=unit_definition_uid
        ):
            raise exceptions.NotFoundException(
                f"Unit definition with specified uid '{unit_definition_uid}' was not found."
            )

    def _check_repository_output(self, nodes: CustomNodeSet, study_uid: str):
        if len(nodes) > 1:
            raise BusinessLogicException(
                f"Found more than one preferred study time StudyTimeField node for the following study_uid='{study_uid}'."
            )
        if len(nodes) == 0:
            raise BusinessLogicException(
                f"The preferred study time StudyTimeField node for the following study_uid='{study_uid}' could not be found."
            )
        return nodes[0]

    @db.transaction
    def get_study_preferred_time_unit(self, study_uid: str) -> StudyPreferredTimeUnit:
        self.check_if_study_exists(study_uid=study_uid)
        nodes = self._repos.study_definition_repository.get_preferred_time_unit(
            study_uid=study_uid
        )
        return_node = self._check_repository_output(nodes=nodes, study_uid=study_uid)
        return StudyPreferredTimeUnit.from_orm(return_node)

    def post_study_preferred_time_unit(self, study_uid: str, unit_definition_uid: str):
        self.check_if_study_exists(study_uid=study_uid)
        self._check_if_unit_definition_exists(unit_definition_uid=unit_definition_uid)
        nodes = self._repos.study_definition_repository.post_preferred_time_unit(
            study_uid=study_uid, unit_definition_uid=unit_definition_uid
        )
        return_node = self._check_repository_output(nodes=nodes, study_uid=study_uid)
        return StudyPreferredTimeUnit.from_orm(return_node)

    @db.transaction
    def patch_study_preferred_time_unit(
        self, study_uid: str, unit_definition_uid: str
    ) -> StudyPreferredTimeUnit:
        self.check_if_study_exists(study_uid=study_uid)
        self._check_if_unit_definition_exists(unit_definition_uid=unit_definition_uid)
        nodes = self._repos.study_definition_repository.edit_preferred_time_unit(
            study_uid=study_uid, unit_definition_uid=unit_definition_uid
        )
        return_node = self._check_repository_output(nodes=nodes, study_uid=study_uid)
        return StudyPreferredTimeUnit.from_orm(return_node)
