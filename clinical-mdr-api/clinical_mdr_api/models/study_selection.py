import re
from datetime import datetime
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Union

from pydantic import Field, root_validator

from clinical_mdr_api.domain.concepts.simple_concepts.numeric_value_with_unit import (
    NumericValueWithUnitAR,
)
from clinical_mdr_api.domain.study_selection.study_activity_instruction import (
    StudyActivityInstructionVO,
)
from clinical_mdr_api.domain.study_selection.study_activity_schedule import (
    StudyActivityScheduleVO,
)
from clinical_mdr_api.domain.study_selection.study_compound_dosing import (
    StudyCompoundDosingVO,
)
from clinical_mdr_api.domain.study_selection.study_design_cell import StudyDesignCellVO
from clinical_mdr_api.domain.study_selection.study_selection_activity import (
    StudySelectionActivityAR,
)
from clinical_mdr_api.domain.study_selection.study_selection_arm import (
    StudySelectionArmVO,
)
from clinical_mdr_api.domain.study_selection.study_selection_branch_arm import (
    StudySelectionBranchArmVO,
)
from clinical_mdr_api.domain.study_selection.study_selection_cohort import (
    StudySelectionCohortVO,
)
from clinical_mdr_api.domain.study_selection.study_selection_compound import (
    StudySelectionCompoundVO,
)
from clinical_mdr_api.domain.study_selection.study_selection_criteria import (
    StudySelectionCriteriaAR,
)
from clinical_mdr_api.domain.study_selection.study_selection_element import (
    StudySelectionElementVO,
)
from clinical_mdr_api.domain.study_selection.study_selection_endpoint import (
    StudySelectionEndpointsAR,
    StudySelectionEndpointVO,
)
from clinical_mdr_api.domain.study_selection.study_selection_objective import (
    StudySelectionObjectivesAR,
)
from clinical_mdr_api.domain.unit_definition.unit_definition import UnitDefinitionAR
from clinical_mdr_api.domain_repositories.study_selection.study_compound_dosing_repository import (
    SelectionHistory as StudyCompoundDosingSelectionHistory,
)
from clinical_mdr_api.domain_repositories.study_selection.study_selection_activity_repository import (
    SelectionHistory as StudyActivitySelectionHistory,
)
from clinical_mdr_api.domain_repositories.study_selection.study_selection_arm_repository import (
    SelectionHistoryArm,
)
from clinical_mdr_api.domain_repositories.study_selection.study_selection_branch_arm_repository import (
    SelectionHistoryBranchArm,
)
from clinical_mdr_api.domain_repositories.study_selection.study_selection_cohort_repository import (
    SelectionHistoryCohort,
)
from clinical_mdr_api.domain_repositories.study_selection.study_selection_compound_repository import (
    StudyCompoundSelectionHistory,
)
from clinical_mdr_api.domain_repositories.study_selection.study_selection_criteria_repository import (
    SelectionHistory as StudyCriteriaSelectionHistory,
)
from clinical_mdr_api.domain_repositories.study_selection.study_selection_element_repository import (
    SelectionHistoryElement,
)
from clinical_mdr_api.domain_repositories.study_selection.study_selection_endpoint_repository import (
    SelectionHistoryObject as StudyEndpointSelectionHistory,
)
from clinical_mdr_api.domain_repositories.study_selection.study_selection_objective_repository import (
    SelectionHistory as StudyObjectiveSelectionHistory,
)
from clinical_mdr_api.models.activities.activity import Activity
from clinical_mdr_api.models.activity_instruction import ActivityInstructionCreateInput
from clinical_mdr_api.models.compound import Compound
from clinical_mdr_api.models.compound_alias import CompoundAlias
from clinical_mdr_api.models.concept import SimpleNumericValueWithUnit
from clinical_mdr_api.models.criteria import Criteria, CriteriaCreateInput
from clinical_mdr_api.models.criteria_template import CriteriaTemplate
from clinical_mdr_api.models.ct_term import SimpleTermModel
from clinical_mdr_api.models.ct_term_name import CTTermName
from clinical_mdr_api.models.duration import DurationJsonModel
from clinical_mdr_api.models.endpoint import Endpoint, EndpointCreateInput
from clinical_mdr_api.models.error import BatchErrorResponse
from clinical_mdr_api.models.objective import Objective, ObjectiveCreateInput
from clinical_mdr_api.models.timeframe import Timeframe
from clinical_mdr_api.models.utils import BaseModel


class StudySelection(BaseModel):
    study_uid: Optional[str] = Field(
        ...,
        title="study_uid",
        description="The uid of the study",
    )

    order: int = Field(
        ...,
        title="order",
        description="The ordering of the selection",
    )

    project_number: Optional[str] = Field(
        None,
        title="project_number",
        description="Number property of the project that the study belongs to",
    )

    project_name: Optional[str] = Field(
        None,
        title="project_name",
        description="Name property of the project that the study belongs to",
    )

    @classmethod
    def remove_brackets_from_name_property(cls, object_to_clear):
        """
        Method removes brackets that surround template parameter used in the StudySelection object
        :param object_to_clear:
        :return:
        """
        used_template_parameters = []
        for parameter_value in object_to_clear.parameter_values:
            for value in parameter_value.values:
                used_template_parameters.append(value.name)
        for template_parameter in used_template_parameters:
            object_to_clear.name = re.sub(
                rf"\[?{template_parameter}\]?", template_parameter, object_to_clear.name
            )


"""
    Study objectives
"""


class StudySelectionObjectiveCore(StudySelection):
    study_objective_uid: Optional[str] = Field(
        ...,
        title="study_objective_uid",
        description="uid for the study objective",
    )

    objective_level: Optional[CTTermName] = Field(
        None,
        title="objective_level",
        description="level defining the objective",
    )

    objective: Optional[Objective] = Field(
        ...,
        title="objective",
        description="the objective selected for the study",
    )

    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study selection was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )

    user_initials: Optional[str] = Field(
        ..., title="user_initials", description="User initials for the version"
    )

    end_date: Optional[datetime] = Field(
        None, title="end_date", description="Start date for the version"
    )

    status: Optional[str] = Field(None, title="status", description="Change status")

    change_type: Optional[str] = Field(
        None, title="change_type", description="Type of last change for the version"
    )

    @classmethod
    def from_study_selection_history(
        cls,
        study_selection_history: StudyObjectiveSelectionHistory,
        study_uid: str,
        get_ct_term_objective_level: Callable[[str], CTTermName],
        get_objective_by_uid_version_callback: Callable[[str], Objective],
    ) -> "StudySelectionObjectiveCore":

        if study_selection_history.objective_level_uid:
            objective_level = get_ct_term_objective_level(
                study_selection_history.objective_level_uid
            )
        else:
            objective_level = None

        return cls(
            study_objective_uid=study_selection_history.study_selection_uid,
            order=study_selection_history.order,
            study_uid=study_uid,
            objective_level=objective_level,
            start_date=study_selection_history.start_date,
            objective=get_objective_by_uid_version_callback(
                study_selection_history.objective_uid,
                study_selection_history.objective_version,
            ),
            end_date=study_selection_history.end_date,
            status=study_selection_history.status,
            change_type=study_selection_history.change_type,
            user_initials=study_selection_history.user_initials,
        )


class StudySelectionObjective(StudySelectionObjectiveCore):
    endpoint_count: Optional[int] = Field(
        None,
        title="endpoint_count",
        description="Number of study endpoints related to given study objective.",
    )

    latest_objective: Optional[Objective] = Field(
        ...,
        title="latest_objective",
        description="Latest version of objective selected for study.",
    )
    accepted_version: Optional[bool] = Field(
        None,
        title="Accepted Version",
        description="Denotes if user accepted obsolete objective versions",
    )

    @classmethod
    def from_study_selection_objectives_ar_and_order(
        cls,
        study_selection_objectives_ar: StudySelectionObjectivesAR,
        order: int,
        get_objective_by_uid_callback: Callable[[str], Objective],
        get_objective_by_uid_version_callback: Callable[[str], Objective],
        get_ct_term_objective_level: Callable[[str], CTTermName],
        get_study_selection_endpoints_ar_by_study_uid_callback: Callable[
            [str], StudySelectionEndpointsAR
        ],
        find_project_by_study_uid: Callable,
        no_brackets: bool = False,
        accepted_version: bool = False,
    ) -> "StudySelectionObjective":

        study_objective_selection = (
            study_selection_objectives_ar.study_objectives_selection
        )
        study_uid = study_selection_objectives_ar.study_uid
        single_study_selection = study_objective_selection[order - 1]
        study_objective_uid = single_study_selection.study_selection_uid
        objective_uid = single_study_selection.objective_uid
        study_selection_endpoints_ar = (
            get_study_selection_endpoints_ar_by_study_uid_callback(study_uid)
        )
        project = find_project_by_study_uid(study_uid)
        assert project is not None

        endpoint_count = sum(
            _.study_objective_uid == study_objective_uid
            for _ in study_selection_endpoints_ar.study_endpoints_selection
        )

        if single_study_selection.objective_level_uid:
            objective_level = get_ct_term_objective_level(
                single_study_selection.objective_level_uid
            )
        else:
            objective_level = None

        assert objective_uid is not None
        latest_objective = get_objective_by_uid_callback(objective_uid)
        if (
            latest_objective
            and latest_objective.version == single_study_selection.objective_version
        ):
            selected_objective = latest_objective
            latest_objective = None
        else:
            selected_objective = get_objective_by_uid_version_callback(
                objective_uid, single_study_selection.objective_version
            )
        if no_brackets:
            cls.remove_brackets_from_name_property(selected_objective)
            if latest_objective is not None:
                cls.remove_brackets_from_name_property(latest_objective)

        return cls(
            study_objective_uid=study_objective_uid,
            order=order,
            accepted_version=accepted_version,
            study_uid=study_uid,
            objective_level=objective_level,
            start_date=single_study_selection.start_date,
            latest_objective=latest_objective,
            objective=selected_objective,
            endpoint_count=endpoint_count,
            user_initials=single_study_selection.user_initials,
            project_name=project.name,
            project_number=project.project_number,
        )


class StudySelectionObjectiveCreateInput(BaseModel):
    objective_level_uid: Optional[str] = Field(
        None,
        title="objective_level",
        description="level defining the objective",
    )
    objective_data: ObjectiveCreateInput = Field(
        ...,
        title="objective_data",
        description="Objective data to create new objective",
    )


class StudySelectionObjectiveInput(BaseModel):
    objective_uid: str = Field(
        None,
        title="objective_uid",
        description="Uid of the selected objective",
    )

    objective_level_uid: Optional[str] = Field(
        None,
        title="objective_level",
        description="level defining the objective",
    )


class StudySelectionObjectiveNewOrder(BaseModel):
    new_order: int = Field(
        ...,
        title="new_order",
        description="Uid of the selected objective",
    )


"""
    Study endpoints
"""


class EndpointUnits(BaseModel):
    units: Optional[List[str]] = Field(
        ...,
        title="units",
        description="the endpoint units selected for the study endpoint",
    )

    separator: Optional[str] = Field(
        None,
        title="separator",
        description="the endpoint units selected for the study endpoint",
    )


class StudySelectionEndpoint(StudySelection):
    study_endpoint_uid: Optional[str] = Field(
        ...,
        title="study_endpoint_uid",
        description="uid for the study endpoint",
    )

    study_objective: Optional[StudySelectionObjective] = Field(
        None,
        title="study_objective_uid",
        description="uid for the study objective which the study endpoints connects to",
    )

    endpoint_level: Optional[CTTermName] = Field(
        None,
        title="endpoint_level",
        description="level defining the endpoint",
    )

    endpoint_sublevel: Optional[CTTermName] = Field(
        None,
        title="endpoint_sublevel",
        description="sub level defining the endpoint",
    )
    endpoint_units: Optional[EndpointUnits] = Field(
        None,
        title="endpoint_units",
        description="the endpoint units selected for the study endpoint",
    )

    endpoint: Optional[Endpoint] = Field(
        None,
        title="endpoint",
        description="the endpoint selected for the study",
    )

    timeframe: Optional[Timeframe] = Field(
        None,
        title="timeframe",
        description="the timeframe selected for the study",
    )

    latest_endpoint: Optional[Endpoint] = Field(
        None,
        title="latest_endpoint",
        description="Latest version of the endpoint selected for the study (if available else none)",
    )

    latest_timeframe: Optional[Timeframe] = Field(
        None,
        title="latest_timeframe",
        description="Latest version of the timeframe selected for the study (if available else none)",
    )

    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study selection was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )

    user_initials: Optional[str] = Field(
        ..., title="user_initials", description="User initials for the version"
    )

    end_date: Optional[datetime] = Field(
        None, title="end_date", description="Start date for the version"
    )

    status: Optional[str] = Field(None, title="status", description="Change status")

    change_type: Optional[str] = Field(
        None, title="change_type", description="Type of last change for the version"
    )
    accepted_version: Optional[bool] = Field(
        None,
        title="Accepted Version",
        description="Denotes if user accepted obsolete endpoint and timeframe versions",
    )

    @classmethod
    def from_study_selection_endpoint(
        cls,
        study_selection: StudySelectionEndpointVO,
        study_uid: str,
        order: int,
        get_endpoint_by_uid_and_version: Callable[[str], Endpoint],
        get_latest_endpoint_by_uid: Callable[[str], Endpoint],
        get_timeframe_by_uid_and_version: Callable[[str], Timeframe],
        get_latest_timeframe: Callable[[str], Timeframe],
        get_ct_term_objective_level: Callable[[str], CTTermName],
        get_study_objective_by_uid: Callable[[str], StudySelectionObjective],
        find_project_by_study_uid: Callable,
        accepted_version: bool = False,
        no_brackets: bool = False,
    ) -> "StudySelectionEndpoint":

        project = find_project_by_study_uid(study_uid)
        assert project is not None

        if study_selection.endpoint_uid is None:
            end_model = None
            latest_end_model = None
        else:
            end_model = get_endpoint_by_uid_and_version(
                study_selection.endpoint_uid, study_selection.endpoint_version
            )
            latest_end_model = get_latest_endpoint_by_uid(study_selection.endpoint_uid)
            if end_model.version == latest_end_model.version:
                latest_end_model = None
            if no_brackets:
                cls.remove_brackets_from_name_property(object_to_clear=end_model)
                if latest_end_model is not None:
                    cls.remove_brackets_from_name_property(
                        object_to_clear=latest_end_model
                    )
        if study_selection.timeframe_uid is None:
            time_model = None
            latest_time_model = None
        else:
            time_model = get_timeframe_by_uid_and_version(
                study_selection.timeframe_uid, study_selection.timeframe_version
            )
            latest_time_model = get_latest_timeframe(study_selection.timeframe_uid)
            if time_model.version == latest_time_model.version:
                latest_time_model = None
            if no_brackets:
                cls.remove_brackets_from_name_property(object_to_clear=time_model)
                if latest_time_model is not None:
                    cls.remove_brackets_from_name_property(
                        object_to_clear=latest_time_model
                    )
        if study_selection.study_objective_uid is None:
            study_obj_model = None
        else:
            study_obj_model = get_study_objective_by_uid(
                study_uid, study_selection.study_objective_uid, no_brackets=no_brackets
            )
            if no_brackets:
                cls.remove_brackets_from_name_property(
                    object_to_clear=study_obj_model.objective
                )
        if study_selection.endpoint_level_uid:
            endpoint_level = get_ct_term_objective_level(
                study_selection.endpoint_level_uid
            )
        else:
            endpoint_level = None
        if study_selection.endpoint_sublevel_uid:
            endpoint_sublevel = get_ct_term_objective_level(
                study_selection.endpoint_sublevel_uid
            )
        else:
            endpoint_sublevel = None
        return StudySelectionEndpoint(
            study_objective=study_obj_model,
            study_uid=study_uid,
            order=order,
            accepted_version=accepted_version,
            study_endpoint_uid=study_selection.study_selection_uid,
            endpoint_units=EndpointUnits(
                units=study_selection.endpoint_units,
                separator=study_selection.unit_separator,
            ),
            endpoint_level=endpoint_level,
            endpoint_sublevel=endpoint_sublevel,
            start_date=study_selection.start_date,
            endpoint=end_model,
            latest_endpoint=latest_end_model,
            timeframe=time_model,
            latest_timeframe=latest_time_model,
            user_initials=study_selection.user_initials,
            project_name=project.name,
            project_number=project.project_number,
        )

    @classmethod
    def from_study_selection_history(
        cls,
        study_selection_history: StudyEndpointSelectionHistory,
        study_uid: str,
        get_endpoint_by_uid: Callable[[str], Endpoint],
        get_timeframe_by_uid: Callable[[str], Timeframe],
        get_ct_term_objective_level: Callable[[str], CTTermName],
        get_study_objective_by_uid: Callable[[str], StudySelectionObjective],
    ) -> "StudySelectionEndpoint":
        if study_selection_history.endpoint_uid:
            endpoint = get_endpoint_by_uid(
                study_selection_history.endpoint_uid,
                study_selection_history.endpoint_version,
            )
        else:
            endpoint = None
        if study_selection_history.timeframe_uid:
            timeframe = get_timeframe_by_uid(
                study_selection_history.timeframe_uid,
                study_selection_history.timeframe_version,
            )
        else:
            timeframe = None
        if study_selection_history.study_objective_uid:
            study_objective = get_study_objective_by_uid(
                study_uid, study_selection_history.study_objective_uid
            )
        else:
            study_objective = None
        if study_selection_history.endpoint_level:
            endpoint_level = get_ct_term_objective_level(
                study_selection_history.endpoint_level
            )
        else:
            endpoint_level = None
        if study_selection_history.endpoint_sublevel:
            endpoint_sublevel = get_ct_term_objective_level(
                study_selection_history.endpoint_sublevel
            )
        else:
            endpoint_sublevel = None
        return cls(
            study_uid=study_uid,
            study_endpoint_uid=study_selection_history.study_selection_uid,
            study_objective=study_objective,
            endpoint_level=endpoint_level,
            endpoint_sublevel=endpoint_sublevel,
            endpoint_units=EndpointUnits(
                units=study_selection_history.endpoint_units,
                separator=study_selection_history.unit_separator,
            ),
            endpoint=endpoint,
            timeframe=timeframe,
            start_date=study_selection_history.start_date,
            user_initials=study_selection_history.user_initials,
            end_date=study_selection_history.end_date,
            status=study_selection_history.status,
            change_type=study_selection_history.change_type,
            order=study_selection_history.order,
        )


class StudySelectionEndpointCreateInput(BaseModel):
    study_objective_uid: Optional[str] = Field(
        None,
        title="study_objective_uid",
        description="uid for a study objective to connect with",
    )
    endpoint_level_uid: Optional[str] = Field(
        None,
        title="endpoint level",
        description="level defining the endpoint",
    )
    endpoint_sublevel_uid: Optional[str] = Field(
        None,
        title="endpoint sub level",
        description="sub level defining the endpoint",
    )
    endpoint_data: EndpointCreateInput = Field(
        ..., title="endpoint_data", description="endpoint data to create new endpoint"
    )
    endpoint_units: Optional[EndpointUnits] = Field(
        None,
        title="endpoint_units",
        description="hold the units used in the study endpoint",
    )
    timeframe_uid: Optional[str] = Field(
        None,
        title="timeframe_uid",
        description="uid for a timeframe",
    )


class StudySelectionEndpointInput(BaseModel):
    study_objective_uid: Optional[str] = Field(
        None,
        title="study_objective_uid",
        description="uid for a study objective to connect with",
    )

    endpoint_uid: Optional[str] = Field(
        None,
        title="endpoint_uid",
        description="uid for a library endpoint to connect with",
    )

    endpoint_level_uid: Optional[str] = Field(
        None,
        title="endpoint level",
        description="level for the endpoint",
    )
    endpoint_sublevel_uid: Optional[str] = Field(
        None,
        title="endpoint sub level",
        description="sub level for the endpoint",
    )
    timeframe_uid: Optional[str] = Field(
        None,
        title="timeframe_uid",
        description="uid for a timeframe",
    )

    endpoint_units: Optional[EndpointUnits] = Field(
        None,
        title="endpoint_units",
        description="hold the units used in the study endpoint",
    )


class StudySelectionEndpointNewOrder(BaseModel):
    new_order: int = Field(
        ...,
        title="new_order",
        description="Uid of the selected endpoint",
    )


"""
    Study compounds
"""


class StudySelectionCompound(StudySelection):
    @classmethod
    def from_study_compound_ar(
        cls,
        study_uid: str,
        selection: StudySelectionCompoundVO,
        order: int,
        compound_model: Optional[Compound],
        compound_alias_model: Optional[CompoundAlias],
        find_simple_term_model_name_by_term_uid: Callable,
        find_project_by_study_uid: Callable,
        find_unit_by_uid: Callable[[str], Optional[UnitDefinitionAR]],
        find_numeric_value_by_uid: Callable[[str], Optional[NumericValueWithUnitAR]],
    ):
        project = find_project_by_study_uid(study_uid)
        return cls(
            order=order,
            study_uid=study_uid,
            study_compound_uid=selection.study_selection_uid,
            compound=compound_model,
            compound_alias=compound_alias_model,
            type_of_treatment=find_simple_term_model_name_by_term_uid(
                selection.type_of_treatment_uid
            ),
            route_of_administration=find_simple_term_model_name_by_term_uid(
                selection.route_of_administration_uid
            ),
            strength_value=SimpleNumericValueWithUnit.from_concept_uid(
                uid=selection.strength_value_uid,
                find_unit_by_uid=find_unit_by_uid,
                find_numeric_value_by_uid=find_numeric_value_by_uid,
            ),
            dosage_form=find_simple_term_model_name_by_term_uid(
                selection.dosage_form_uid
            ),
            dispensed_in=find_simple_term_model_name_by_term_uid(
                selection.dispensed_in_uid
            ),
            device=find_simple_term_model_name_by_term_uid(selection.device_uid),
            formulation=find_simple_term_model_name_by_term_uid(
                selection.formulation_uid
            ),
            other_info=selection.other_info,
            reason_for_missing_null_value=find_simple_term_model_name_by_term_uid(
                selection.reason_for_missing_value_uid
            ),
            start_date=selection.start_date,
            user_initials=selection.user_initials,
            project_name=project.name,
            project_number=project.project_number,
            study_compound_dosing_count=selection.study_compound_dosing_count,
        )

    study_compound_uid: Optional[str] = Field(
        ...,
        title="study_compound_uid",
        description="uid for the study compound",
        source="uid",
    )

    compound: Optional[Compound] = Field(
        None, title="compound", description="the connected compound model"
    )

    compound_alias: Optional[CompoundAlias] = Field(
        None,
        title="compound_alias",
        description="the connected compound alias",
    )

    type_of_treatment: Optional[SimpleTermModel] = Field(
        None,
        title="type_of_treatment",
        description="type of treatment uid defined for the selection",
    )

    route_of_administration: Optional[SimpleTermModel] = Field(
        None,
        title="route_of_administration",
        description="route of administration defined for the study selection",
    )

    strength_value: Optional[SimpleNumericValueWithUnit] = Field(
        None,
        title="strength",
        description="compound strength defined for the study selection",
    )

    dosage_form: Optional[SimpleTermModel] = Field(
        None,
        title="dosage_form",
        description="dosage form defined for the study selection",
    )

    dispensed_in: Optional[SimpleTermModel] = Field(
        None,
        title="dispensed_in",
        description="dispense method defined for the study selection",
    )

    device: Optional[SimpleTermModel] = Field(
        None,
        title="device",
        description="device used for the compound in the study selection",
    )

    formulation: Optional[SimpleTermModel] = Field(
        None,
        title="formulation",
        description="formulation defined for the study selection",
    )

    other_info: Optional[str] = Field(
        None,
        title="other_info",
        description="any other information logged regarding the study compound",
    )

    reason_for_missing_null_value: Optional[SimpleTermModel] = Field(
        None,
        title="reason_for_missing_null_value",
        description="Reason why no compound is used in the study selection, e.g. exploratory study",
    )

    study_compound_dosing_count: Optional[int] = Field(
        None, description="Number of compound dosing linked to Study Compound"
    )

    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study selection was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )

    user_initials: Optional[str] = Field(
        ..., title="user_initials", description="User initials for the version"
    )

    end_date: Optional[datetime] = Field(
        None, title="end_date", description="End date for the version"
    )

    status: Optional[str] = Field(None, title="status", description="Change status")

    change_type: Optional[str] = Field(
        None, title="change_type", description="Type of last change for the version"
    )

    @classmethod
    def from_study_selection_history(
        cls,
        study_selection_history: StudyCompoundSelectionHistory,
        study_uid: str,
        get_compound_by_uid: Callable[[str], Compound],
        get_compound_alias_by_uid: Callable[[str], CompoundAlias],
        find_simple_term_model_name_by_term_uid: Callable,
        find_unit_by_uid: Callable[[str], Optional[UnitDefinitionAR]],
        find_numeric_value_by_uid: Callable[[str], Optional[NumericValueWithUnitAR]],
    ) -> "StudySelectionCompound":
        if study_selection_history.compound_uid:
            compound = get_compound_by_uid(study_selection_history.compound_uid)
        else:
            compound = None
        if study_selection_history.compound_alias_uid:
            compound_alias = get_compound_alias_by_uid(
                study_selection_history.compound_alias_uid
            )
        else:
            compound_alias = None
        return cls(
            study_compound_uid=study_selection_history.study_selection_uid,
            order=study_selection_history.order,
            study_uid=study_uid,
            type_of_treatment=find_simple_term_model_name_by_term_uid(
                study_selection_history.type_of_treatment_uid
            ),
            route_of_administration=find_simple_term_model_name_by_term_uid(
                study_selection_history.route_of_administration_uid
            ),
            strength_value=SimpleNumericValueWithUnit.from_concept_uid(
                uid=study_selection_history.strength_value_uid,
                find_unit_by_uid=find_unit_by_uid,
                find_numeric_value_by_uid=find_numeric_value_by_uid,
            ),
            dosage_form=find_simple_term_model_name_by_term_uid(
                study_selection_history.dosage_form_uid
            ),
            dispensed_in=find_simple_term_model_name_by_term_uid(
                study_selection_history.dispensed_in_uid
            ),
            device=find_simple_term_model_name_by_term_uid(
                study_selection_history.device_uid
            ),
            formulation=find_simple_term_model_name_by_term_uid(
                study_selection_history.formulation_uid
            ),
            other_info=study_selection_history.other_info,
            reason_for_missing_null_value=find_simple_term_model_name_by_term_uid(
                study_selection_history.reason_for_missing_value_uid
            ),
            start_date=study_selection_history.start_date,
            compound=compound,
            compound_alias=compound_alias,
            end_date=study_selection_history.end_date,
            status=study_selection_history.status,
            change_type=study_selection_history.change_type,
            user_initials=study_selection_history.user_initials,
        )


class StudySelectionCompoundInput(BaseModel):

    compound_alias_uid: Optional[str] = Field(
        None,
        title="compound_alias_uid",
        description="uid for the library compound alias",
    )

    type_of_treatment_uid: Optional[str] = Field(
        None,
        title="type_of_treatment_uid",
        description="type of treatment defined for the selection",
    )

    route_of_administration_uid: Optional[str] = Field(
        None,
        title="route_of_administration_uid",
        description="route of administration defined for the study selection",
    )

    strength_value_uid: Optional[str] = Field(
        None,
        title="strength_value_uid",
        description="compound strength defined for the study selection",
    )

    dosage_form_uid: Optional[str] = Field(
        None,
        title="dosage_form_uid",
        description="dosage form defined for the study selection",
    )

    dispensed_in_uid: Optional[str] = Field(
        None,
        title="dispensed_in_uid",
        description="dispense method defined for the study selection",
    )

    device_uid: Optional[str] = Field(
        None,
        title="device_uid",
        description="device used for the compound in the study selection",
    )

    formulation_uid: Optional[str] = Field(
        None,
        title="formulation_uid",
        description="formulation defined for the study selection",
    )

    other_info: Optional[str] = Field(
        None,
        title="other_info",
        description="any other information logged regarding the study compound",
    )

    reason_for_missing_null_value_uid: Optional[str] = Field(
        None,
        title="reason_for_missing_null_value_uid",
        description="Reason why no compound is used in the study selection, e.g. exploratory study",
    )


class StudySelectionCompoundNewOrder(BaseModel):
    new_order: int = Field(
        ...,
        title="new_order",
        description="new order selected for the study compound",
    )


"""
    Study criteria
"""


class StudySelectionCriteriaCore(StudySelection):
    study_criteria_uid: Optional[str] = Field(
        ...,
        title="study_criteria_uid",
        description="uid for the study criteria",
    )

    criteria_type: Optional[CTTermName] = Field(
        None,
        title="criteria_type",
        description="Type of criteria",
    )

    criteria: Optional[Criteria] = Field(
        None,
        title="criteria",
        description="the criteria selected for the study",
    )

    criteria_template: Optional[CriteriaTemplate] = Field(
        None,
        title="criteria_template",
        description="the criteria template selected for the study",
    )

    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study selection was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )

    user_initials: Optional[str] = Field(
        ..., title="user_initials", description="User initials for the version"
    )

    end_date: Optional[datetime] = Field(
        None, title="end_date", description="Start date for the version"
    )

    status: Optional[str] = Field(None, title="status", description="Change status")

    change_type: Optional[str] = Field(
        None, title="change_type", description="Type of last change for the version"
    )
    key_criteria: Optional[bool] = Field(False, title="key_criteria", description="")

    @classmethod
    def from_study_selection_template_history(
        cls,
        study_selection_history: StudyCriteriaSelectionHistory,
        study_uid: str,
        get_criteria_template_by_uid_version_callback: Callable[
            [str], CriteriaTemplate
        ],
    ) -> "StudySelectionCriteriaCore":

        return cls(
            study_criteria_uid=study_selection_history.study_selection_uid,
            order=study_selection_history.criteria_type_order,
            study_uid=study_uid,
            start_date=study_selection_history.start_date,
            criteria_template=get_criteria_template_by_uid_version_callback(
                study_selection_history.syntax_object_uid,
                study_selection_history.syntax_object_version,
            ),
            end_date=study_selection_history.end_date,
            status=study_selection_history.status,
            change_type=study_selection_history.change_type,
            user_initials=study_selection_history.user_initials,
            key_criteria=study_selection_history.key_criteria,
        )

    @classmethod
    def from_study_selection_history(
        cls,
        study_selection_history: StudyCriteriaSelectionHistory,
        study_uid: str,
        get_criteria_by_uid_version_callback: Callable[[str], Criteria],
    ) -> "StudySelectionCriteriaCore":

        return cls(
            study_criteria_uid=study_selection_history.study_selection_uid,
            order=study_selection_history.criteria_type_order,
            study_uid=study_uid,
            start_date=study_selection_history.start_date,
            criteria=get_criteria_by_uid_version_callback(
                study_selection_history.syntax_object_uid,
                study_selection_history.syntax_object_version,
            ),
            end_date=study_selection_history.end_date,
            status=study_selection_history.status,
            change_type=study_selection_history.change_type,
            user_initials=study_selection_history.user_initials,
            key_criteria=study_selection_history.key_criteria,
        )


class StudySelectionCriteria(StudySelectionCriteriaCore):
    latest_criteria: Optional[Criteria] = Field(
        None,
        title="latest_criteria",
        description="Latest version of criteria selected for study.",
    )
    latest_template: Optional[CriteriaTemplate] = Field(
        None,
        title="latest_template",
        description="Latest version of criteria template selected for study.",
    )
    accepted_version: Optional[bool] = Field(
        None,
        title="Accepted Version",
        description="Denotes if user accepted obsolete criteria versions",
    )

    @classmethod
    def from_study_selection_criteria_template_ar_and_order(
        cls,
        study_selection_criteria_ar: StudySelectionCriteriaAR,
        criteria_type_uid: str,
        criteria_type_order: int,
        get_criteria_template_by_uid_callback: Callable[[str], CriteriaTemplate],
        get_criteria_template_by_uid_version_callback: Callable[
            [str], CriteriaTemplate
        ],
        get_ct_term_criteria_type: Callable[[str], CTTermName],
        find_project_by_study_uid: Callable,
        accepted_version: bool = False,
    ) -> "StudySelectionCriteria":
        study_uid = study_selection_criteria_ar.study_uid

        project = find_project_by_study_uid(study_uid)
        assert project is not None

        # Filter criteria list on criteria type before selecting with order property
        study_criteria_selection_with_type = [
            x
            for x in study_selection_criteria_ar.study_criteria_selection
            if x.criteria_type_uid == criteria_type_uid
        ]
        single_study_selection = study_criteria_selection_with_type[
            criteria_type_order - 1
        ]
        study_criteria_uid = single_study_selection.study_selection_uid
        criteria_template_uid = single_study_selection.syntax_object_uid

        criteria_type = get_ct_term_criteria_type(criteria_type_uid)

        assert criteria_template_uid is not None
        latest_criteria_template = get_criteria_template_by_uid_callback(
            criteria_template_uid
        )
        if (
            latest_criteria_template
            and latest_criteria_template.version
            == single_study_selection.syntax_object_version
        ):
            selected_criteria_template = latest_criteria_template
            latest_criteria_template = None
        else:
            selected_criteria_template = get_criteria_template_by_uid_version_callback(
                criteria_template_uid, single_study_selection.syntax_object_version
            )

        return cls(
            study_criteria_uid=study_criteria_uid,
            criteria_type=criteria_type,
            order=criteria_type_order,
            accepted_version=accepted_version,
            study_uid=study_uid,
            start_date=single_study_selection.start_date,
            latest_template=latest_criteria_template,
            criteria_template=selected_criteria_template,
            user_initials=single_study_selection.user_initials,
            project_name=project.name,
            project_number=project.project_number,
            key_criteria=single_study_selection.key_criteria,
        )

    @classmethod
    def from_study_selection_criteria_ar_and_order(
        cls,
        study_selection_criteria_ar: StudySelectionCriteriaAR,
        criteria_type_uid: str,
        criteria_type_order: int,
        get_criteria_by_uid_callback: Callable[[str], Criteria],
        get_criteria_by_uid_version_callback: Callable[[str], Criteria],
        get_ct_term_criteria_type: Callable[[str], CTTermName],
        find_project_by_study_uid: Callable,
        no_brackets: bool = False,
        accepted_version: bool = False,
    ) -> "StudySelectionCriteria":

        study_uid = study_selection_criteria_ar.study_uid

        project = find_project_by_study_uid(study_uid)
        assert project is not None

        # Filter criteria list on criteria type before selecting with order property
        study_criteria_selection_with_type = [
            x
            for x in study_selection_criteria_ar.study_criteria_selection
            if x.criteria_type_uid == criteria_type_uid
        ]
        single_study_selection = study_criteria_selection_with_type[
            criteria_type_order - 1
        ]
        study_criteria_uid = single_study_selection.study_selection_uid
        criteria_uid = single_study_selection.syntax_object_uid

        criteria_type = get_ct_term_criteria_type(criteria_type_uid)

        assert criteria_uid is not None
        latest_criteria = get_criteria_by_uid_callback(criteria_uid)
        if (
            latest_criteria
            and latest_criteria.version == single_study_selection.syntax_object_version
        ):
            selected_criteria = latest_criteria
            latest_criteria = None
        else:
            selected_criteria = get_criteria_by_uid_version_callback(
                criteria_uid, single_study_selection.syntax_object_version
            )
        if no_brackets:
            cls.remove_brackets_from_name_property(selected_criteria)
            if latest_criteria is not None:
                cls.remove_brackets_from_name_property(latest_criteria)

        return cls(
            study_criteria_uid=study_criteria_uid,
            criteria_type=criteria_type,
            order=criteria_type_order,
            accepted_version=accepted_version,
            study_uid=study_uid,
            start_date=single_study_selection.start_date,
            latest_criteria=latest_criteria,
            criteria=selected_criteria,
            user_initials=single_study_selection.user_initials,
            project_name=project.name,
            project_number=project.project_number,
            key_criteria=single_study_selection.key_criteria,
        )


class StudySelectionCriteriaCreateInput(BaseModel):
    criteria_data: CriteriaCreateInput = Field(
        ..., title="criteria_data", description="Criteria data to create new criteria"
    )


class StudySelectionCriteriaTemplateSelectInput(BaseModel):
    criteria_template_uid: str = Field(
        ...,
        title="criteria_template_uid",
        description="The unique id of the criteria template that is to be selected.",
    )
    library_name: str = Field(
        None,
        title="library_name",
        description="If specified: The name of the library to which the criteria will be linked. The following rules apply: \n"
        "* The library needs to be present, it will not be created with this request. The *[GET] /libraries* criteria can help. And \n"
        "* The library needs to allow the creation: The 'is_editable' property of the library needs to be true. \n\n"
        "If not specified: The library of the criteria template will be used.",
    )


class StudySelectionCriteriaNewOrder(BaseModel):
    new_order: int = Field(
        ...,
        title="new_order",
        description="New value to set for the order property of the selection",
    )


class StudySelectionCriteriaKeyCriteria(BaseModel):
    key_criteria: bool = Field(
        ...,
        title="key_criteria",
        description="New value to set for the key_criteria property of the selection",
    )


#
# Study Activity
#


class CommonStudyActivity(BaseModel):
    show_activity_group_in_protocol_flowchart: Optional[bool] = Field(
        None,
        title="show_activity_group_in_protocol_flowchart",
        description="show activity group in protocol flow chart",
    )

    show_activity_subgroup_in_protocol_flowchart: Optional[bool] = Field(
        None,
        title="show_activity_subgroup_in_protocol_flowchart",
        description="show activity sub group in protocol flow chart",
    )

    show_activity_in_protocol_flowchart: Optional[bool] = Field(
        None,
        title="show_activity_in_protocol_flowchart",
        description="show activity in protocol flow chart",
    )


class StudySelectionActivityCore(CommonStudyActivity, StudySelection):
    study_activity_uid: Optional[str] = Field(
        ...,
        title="study_activity_uid",
        description="uid for the study activity",
        source="uid",
    )

    activity: Optional[Activity] = Field(
        ...,
        title="activity",
        description="the activity selected for the study",
    )

    flowchart_group: Optional[CTTermName] = Field(
        None,
        title="flowchart_group",
        description="flow chart group linked to this study activity",
    )

    note: Optional[str] = Field(
        None, title="note", description="Foot note to display in flowchart"
    )

    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study selection was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
        source="has_after.date",
    )

    user_initials: Optional[str] = Field(
        ...,
        title="user_initials",
        description="User initials for the version",
        source="has_after.user_initials",
    )

    end_date: Optional[datetime] = Field(
        None, title="end_date", description="Start date for the version"
    )

    status: Optional[str] = Field(None, title="status", description="Change status")

    change_type: Optional[str] = Field(
        None, title="change_type", description="Type of last change for the version"
    )

    @classmethod
    def from_study_selection_history(
        cls,
        study_selection_history: StudyActivitySelectionHistory,
        study_uid: str,
        get_ct_term_flowchart_group: Callable[[str], CTTermName],
        get_activity_by_uid_version_callback: Callable[[str], Activity],
    ) -> "StudySelectionActivityCore":

        return cls(
            study_activity_uid=study_selection_history.study_selection_uid,
            order=study_selection_history.activity_order,
            show_activity_group_in_protocol_flowchart=study_selection_history.show_activity_group_in_protocol_flowchart,
            show_activity_subgroup_in_protocol_flowchart=study_selection_history.show_activity_subgroup_in_protocol_flowchart,
            show_activity_in_protocol_flowchart=study_selection_history.show_activity_in_protocol_flowchart,
            note=study_selection_history.note,
            study_uid=study_uid,
            flowchart_group=get_ct_term_flowchart_group(
                study_selection_history.flowchart_group_uid
            ),
            start_date=study_selection_history.start_date,
            activity=get_activity_by_uid_version_callback(
                study_selection_history.activity_uid,
                study_selection_history.activity_version,
            ),
            end_date=study_selection_history.end_date,
            # status=study_selection_history.status,  FIXME
            change_type=study_selection_history.change_type,
            user_initials=study_selection_history.user_initials,
        )


class StudySelectionActivity(StudySelectionActivityCore):
    class Config:
        orm_mode = True

    latest_activity: Optional[Activity] = Field(
        None,
        title="latest_activity",
        description="Latest version of activity selected for study.",
    )
    accepted_version: Optional[bool] = Field(
        None,
        title="Accepted Version",
        description="Denotes if user accepted obsolete activity versions",
    )

    @classmethod
    def from_study_selection_activity_ar_and_order(
        cls,
        study_selection_activity_ar: StudySelectionActivityAR,
        activity_order: int,
        get_activity_by_uid_callback: Callable[[str], Activity],
        get_activity_by_uid_version_callback: Callable[[str], Activity],
        get_ct_term_flowchart_group: Callable[[str], CTTermName],
        accepted_version: bool = False,
    ) -> "StudySelectionActivity":

        study_activity_selection = study_selection_activity_ar.study_objects_selection
        study_uid = study_selection_activity_ar.study_uid
        single_study_selection = study_activity_selection[activity_order - 1]
        study_activity_uid = single_study_selection.study_selection_uid
        activity_uid = single_study_selection.activity_uid

        flowchart_group = get_ct_term_flowchart_group(
            single_study_selection.flowchart_group_uid
        )

        assert activity_uid is not None
        latest_activity = get_activity_by_uid_callback(activity_uid)
        if (
            latest_activity
            and latest_activity.version == single_study_selection.activity_version
        ):
            selected_activity = latest_activity
            latest_activity = None
        else:
            selected_activity = get_activity_by_uid_version_callback(
                activity_uid, single_study_selection.activity_version
            )

        return cls(
            study_activity_uid=study_activity_uid,
            activity=selected_activity,
            latest_activity=latest_activity,
            order=activity_order,
            flowchart_group=flowchart_group,
            show_activity_group_in_protocol_flowchart=single_study_selection.show_activity_group_in_protocol_flowchart,
            show_activity_subgroup_in_protocol_flowchart=single_study_selection.show_activity_subgroup_in_protocol_flowchart,
            show_activity_in_protocol_flowchart=single_study_selection.show_activity_in_protocol_flowchart,
            note=single_study_selection.note,
            accepted_version=accepted_version,
            study_uid=study_uid,
            start_date=single_study_selection.start_date,
            user_initials=single_study_selection.user_initials,
        )


class StudySelectionActivityCreateInput(BaseModel):
    flowchart_group_uid: str = Field(
        title="flowchart_group_uid",
        description="flowchart CT term uid",
    )
    activity_uid: str = Field(title="activity_uid", description="activity uid")
    activity_instance_uid: Optional[str] = Field(
        None, title="activity_instance_uid", description="activity instance uid"
    )


class StudySelectionActivityInput(CommonStudyActivity):
    flowchart_group_uid: Optional[str] = Field(
        title="flowchart_group_uid",
        description="flowchart CT term uid",
    )

    note: Optional[str] = Field(
        None, title="note", description="Foot note to display in flowchart"
    )


class StudySelectionActivityNewOrder(BaseModel):
    new_order: int = Field(
        ...,
        title="new_order",
        description="new order selected for the study activity",
    )


class StudySelectionActivityBatchUpdateInput(BaseModel):
    study_activity_uid: str = Field(
        ...,
        title="study_activity_uid",
        description="UID of the Study Activity to update",
    )
    content: StudySelectionActivityInput


class StudySelectionActivityBatchDeleteInput(BaseModel):
    study_activity_uid: str = Field(
        ...,
        title="study_activity_uid",
        description="UID of the study activity to delete",
    )


class StudySelectionActivityBatchInput(BaseModel):
    method: str = Field(
        ..., title="method", description="HTTP method corresponding to operation type"
    )
    content: Union[
        StudySelectionActivityBatchUpdateInput,
        StudySelectionActivityCreateInput,
        StudySelectionActivityBatchDeleteInput,
    ]


class StudySelectionActivityBatchOutput(BaseModel):
    response_code: int = Field(
        ...,
        title="response_code",
        description="The HTTP response code related to input operation",
    )
    content: Union[StudySelectionActivity, None, BatchErrorResponse]


#
# Study Activity Schedule
#


class StudyActivitySchedule(BaseModel):
    class Config:
        orm_mode = True

    study_uid: str = Field(
        ...,
        title="study_uid",
        description="The uid of the study",
        source="study_value.study_root.uid",
    )

    study_activity_schedule_uid: Optional[str] = Field(
        ...,
        title="study_activity_schedule_uid",
        description="uid for the study activity schedule",
        source="uid",
    )

    study_activity_uid: str = Field(
        title="study_activity_uid",
        description="The related study activity UID",
        source="study_activity.uid",
    )

    study_activity_name: Optional[str] = Field(
        title="study_activity_name",
        description="The related study activity name",
        source="study_activity.has_selected_activity.name",
    )

    study_visit_uid: str = Field(
        title="study_visit_uid",
        description="The related study visit UID",
        source="study_visit.uid",
    )

    study_visit_name: Optional[str] = Field(
        title="study_visit_name",
        description="The related study visit name",
        source="study_visit.has_visit_name.has_latest_value.name",
    )

    note: Optional[str] = Field(
        None, title="note", description="Foot note to display in flowchart"
    )

    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study selection was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
        source="has_after.date",
    )

    user_initials: Optional[str] = Field(
        ...,
        title="user_initials",
        description="User initials for the version",
        source="has_after.user_initials",
    )

    end_date: Optional[datetime] = Field(
        None, title="end_date", description="Start date for the version"
    )

    @classmethod
    def from_vo(cls, schedule_vo: StudyActivityScheduleVO) -> "StudyActivitySchedule":
        return cls(
            study_activity_schedule_uid=schedule_vo.uid,
            study_uid=schedule_vo.study_uid,
            study_activity_uid=schedule_vo.study_activity_uid,
            study_activity_name=schedule_vo.study_activity_name,
            study_visit_uid=schedule_vo.study_visit_uid,
            study_visit_name=schedule_vo.study_visit_name,
            note=schedule_vo.note,
            start_date=schedule_vo.start_date,
            user_initials=schedule_vo.user_initials,
        )


class StudyActivityScheduleHistory(BaseModel):
    study_uid: str = Field(
        ...,
        title="study_uid",
        description="The uid of the study",
    )

    study_activity_schedule_uid: str = Field(
        ...,
        title="study_activity_schedule_uid",
        description="uid for the study activity schedule",
    )

    study_activity_uid: str = Field(
        ...,
        title="study_activity_uid",
        description="uid for the study activity",
    )

    study_visit_uid: str = Field(
        ...,
        title="study_visit_uid",
        description="uid for the study visit",
    )

    note: Optional[str] = Field(
        None, title="note", description="Foot note to display in flowchart"
    )

    modified: Optional[datetime] = Field(
        None, title="modified", description="Date of last modification"
    )


class StudyActivityScheduleCreateInput(BaseModel):

    study_activity_uid: str = Field(
        ..., title="study_activity_uid", description="The related study activity uid"
    )

    study_visit_uid: str = Field(
        ..., title="study_visit_uid", description="The related study visit uid"
    )

    note: Optional[str] = Field(None, title="note", description="A note")


class StudyActivityScheduleDeleteInput(BaseModel):
    uid: str = Field(
        ..., title="uid", description="UID of the study activity schedule to delete"
    )


class StudyActivityScheduleBatchInput(BaseModel):
    method: str = Field(
        ..., title="method", description="HTTP method corresponding to operation type"
    )
    content: Union[StudyActivityScheduleCreateInput, StudyActivityScheduleDeleteInput]


class StudyActivityScheduleBatchOutput(BaseModel):
    response_code: int = Field(
        ...,
        title="response_code",
        description="The HTTP response code related to input operation",
    )
    content: Union[StudyActivitySchedule, None, BatchErrorResponse]


"""
    Study design cells
"""


class StudyDesignCell(BaseModel):
    class Config:
        orm_mode = True

    study_uid: str = Field(
        ...,
        title="study_uid",
        description="The uid of the study",
        source="study_value.study_root.uid",
    )

    design_cell_uid: Optional[str] = Field(
        ..., title="design_cell_uid", description="uid for the study cell", source="uid"
    )

    study_arm_uid: Optional[str] = Field(
        None,
        title="study_arm_uid",
        description="the uid of the related study arm",
        source="study_arm.uid",
    )

    study_arm_name: Optional[str] = Field(
        None,
        title="study_arm_name",
        description="the name of the related study arm",
        source="study_arm.name",
    )

    study_branch_arm_uid: Optional[str] = Field(
        None,
        title="study_branch_arm_uid",
        description="the uid of the related study branch arm",
        source="study_branch_arm.uid",
    )

    study_branch_arm_name: Optional[str] = Field(
        None,
        title="study_branch_arm_name",
        description="the name of the related study branch arm",
        source="study_branch_arm.name",
    )

    study_epoch_uid: str = Field(
        ...,
        title="study_epoch_uid",
        description="the uid of the related study epoch",
        source="study_epoch.uid",
    )

    study_epoch_name: str = Field(
        ...,
        title="study_epoch_name",
        description="the name of the related study epoch",
        source="study_epoch.has_epoch.has_name_root.has_latest_value.name",
    )

    study_element_uid: str = Field(
        ...,
        title="study_element_uid",
        description="the uid of the related study element",
        source="study_element.uid",
    )

    study_element_name: str = Field(
        ...,
        title="study_element_name",
        description="the name of the related study element",
        source="study_element.name",
    )

    transition_rule: Optional[str] = Field(
        ...,
        title="transition_rule",
        description="transition rule for the cell",
    )

    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study selection was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
        source="has_after.date",
    )

    user_initials: Optional[str] = Field(
        ...,
        title="user_initials",
        description="User initials for the version",
        source="has_after.user_initials",
    )

    end_date: Optional[datetime] = Field(
        None, title="end_date", description="Start date for the version"
    )

    order: Optional[int] = Field(
        None,
        title="order",
        description="The ordering of the selection",
    )

    @classmethod
    def from_vo(cls, design_cell_vo: StudyDesignCellVO) -> "StudyDesignCell":
        return cls(
            design_cell_uid=design_cell_vo.uid,
            study_uid=design_cell_vo.study_uid,
            study_arm_uid=design_cell_vo.study_arm_uid,
            study_arm_name=design_cell_vo.study_arm_name,
            study_branch_arm_uid=design_cell_vo.study_branch_arm_uid,
            study_branch_arm_name=design_cell_vo.study_branch_arm_name,
            study_epoch_uid=design_cell_vo.study_epoch_uid,
            study_epoch_name=design_cell_vo.study_epoch_name,
            study_element_uid=design_cell_vo.study_element_uid,
            study_element_name=design_cell_vo.study_element_name,
            transition_rule=design_cell_vo.transition_rule,
            start_date=design_cell_vo.start_date,
            user_initials=design_cell_vo.user_initials,
            order=design_cell_vo.order,
        )


class StudyDesignCellHistory(BaseModel):
    study_uid: str = Field(..., title="study_uid", description="The uid of the study")

    study_design_cell_uid: str = Field(
        ..., title="study_design_cell_uid", description="uid for the study design cell"
    )

    study_arm_uid: Optional[str] = Field(
        None, title="study_arm_uid", description="the uid of the related study arm"
    )

    study_branch_arm_uid: Optional[str] = Field(
        None,
        title="study_branch_arm_uid",
        description="the uid of the related study branch arm",
    )

    study_epoch_uid: str = Field(
        ..., title="study_epoch_uid", description="the uid of the related study epoch"
    )

    study_element_uid: str = Field(
        None,
        title="study_element_uid",
        description="the uid of the related study element",
    )

    transition_rule: str = Field(
        None, title="transition_rule", description="transition rule for the cell"
    )

    change_type: Optional[str] = Field(
        None, title="change_type", description="Type of last change for the version"
    )

    modified: Optional[datetime] = Field(
        None, title="modified", description="Date of last modification"
    )

    order: Optional[int] = Field(
        None,
        title="order",
        description="The ordering of the selection",
    )


class StudyDesignCellVersion(StudyDesignCellHistory):
    changes: Dict


class StudyDesignCellCreateInput(BaseModel):
    study_arm_uid: Optional[str] = Field(
        None, title="study_arm_uid", description="the uid of the related study arm"
    )

    study_branch_arm_uid: Optional[str] = Field(
        None,
        title="study_branch_arm_uid",
        description="the uid of the related study branch arm",
    )

    study_epoch_uid: str = Field(
        ..., title="study_epoch_uid", description="the uid of the related study epoch"
    )

    study_element_uid: str = Field(
        ...,
        title="study_element_uid",
        description="the uid of the related study element",
    )

    transition_rule: Optional[str] = Field(
        None,
        title="transition_rule",
        description="Optionally, a transition rule for the cell",
    )

    order: Optional[int] = Field(
        None,
        title="order",
        description="The ordering of the selection",
    )


class StudyDesignCellEditInput(BaseModel):
    study_design_cell_uid: str = Field(
        ..., title="study_design_cell_uid", description="uid for the study design cell"
    )
    study_arm_uid: Optional[str] = Field(
        None, title="study_arm_uid", description="the uid of the related study arm"
    )
    study_branch_arm_uid: Optional[str] = Field(
        None,
        title="study_branch_arm_uid",
        description="the uid of the related study branch arm",
    )
    study_element_uid: Optional[str] = Field(
        None,
        title="study_element_uid",
        description="the uid of the related study element",
    )
    order: Optional[int] = Field(
        None,
        title="order",
        description="The ordering of the selection",
    )
    transition_rule: Optional[str] = Field(
        None,
        title="transition_rule",
        description="transition rule for the cell",
    )


class StudyDesignCellDeleteInput(BaseModel):
    uid: str = Field(
        ..., title="uid", description="UID of the study design cell to delete"
    )


class StudyDesignCellBatchInput(BaseModel):
    method: str = Field(
        ..., title="method", description="HTTP method corresponding to operation type"
    )
    content: Union[
        StudyDesignCellCreateInput, StudyDesignCellDeleteInput, StudyDesignCellEditInput
    ]


class StudyDesignCellBatchOutput(BaseModel):
    response_code: int = Field(
        ...,
        title="response_code",
        description="The HTTP response code related to input operation",
    )
    content: Union[StudyDesignCell, None, BatchErrorResponse]


"""
    Study brancharms without ArmRoot
"""


class StudySelectionBranchArmWithoutStudyArm(StudySelection):
    branch_arm_uid: Optional[str] = Field(
        ...,
        title="study_branch_arm_uid",
        description="uid for the study BranchArm",
    )

    name: str = Field(
        ...,
        title="study_branch_arm_name",
        description="name for the study Brancharm",
    )

    short_name: str = Field(
        ...,
        title="study_branch_arm_short_name",
        description="short name for the study Brancharm",
    )

    code: Optional[str] = Field(
        ...,
        title="study_branch_arm_code",
        description="code for the study Brancharm",
    )

    description: Optional[str] = Field(
        ...,
        title="study_branch_arm_description",
        description="description for the study Brancharm",
    )

    colour_code: Optional[str] = Field(
        ...,
        title="study_branch_armcolour_code",
        description="colour_code for the study Brancharm",
    )

    randomization_group: Optional[str] = Field(
        ...,
        title="study_branch_arm_randomization_group",
        description="randomization group for the study Brancharm",
    )

    number_of_subjects: Optional[int] = Field(
        ...,
        title="study_branch_arm_number_of_subjects",
        description="number of subjects for the study Brancharm",
    )

    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study selection was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )

    user_initials: Optional[str] = Field(
        ..., title="user_initials", description="User initials for the version"
    )

    end_date: Optional[datetime] = Field(
        None, title="end_date", description="Start date for the version"
    )

    status: Optional[str] = Field(None, title="status", description="Change status")

    change_type: Optional[str] = Field(
        None, title="change_type", description="Type of last change for the version"
    )

    accepted_version: Optional[bool] = Field(
        None,
        title="Accepted Version",
        description="Denotes if user accepted obsolete endpoint and timeframe versions",
    )

    @classmethod
    def from_study_selection_branch_arm_ar_and_order(
        cls,
        study_uid: str,
        selection: StudySelectionBranchArmVO,
        order: int,
    ):
        return cls(
            study_uid=study_uid,
            branch_arm_uid=selection.study_selection_uid,
            name=selection.name,
            short_name=selection.short_name,
            code=selection.code,
            description=selection.description,
            colour_code=selection.colour_code,
            order=order,
            randomization_group=selection.randomization_group,
            number_of_subjects=selection.number_of_subjects,
            start_date=selection.start_date,
            user_initials=selection.user_initials,
            end_date=selection.end_date,
            status=selection.status,
            change_type=selection.change_type,
            accepted_version=selection.accepted_version,
        )


"""
    Study arms
"""


class StudySelectionArm(StudySelection):
    arm_uid: Optional[str] = Field(
        ...,
        title="study_arm_uid",
        description="uid for the study arm",
    )

    name: str = Field(
        ...,
        title="study_arm_name",
        description="name for the study arm",
    )

    short_name: str = Field(
        ...,
        title="study_arm_short_name",
        description="short name for the study arm",
    )

    code: Optional[str] = Field(
        ...,
        title="study_arm_code",
        description="code for the study arm",
    )

    description: Optional[str] = Field(
        ...,
        title="study_arm_description",
        description="description for the study arm",
    )

    arm_colour: Optional[str] = Field(
        ...,
        title="study_arm_colour",
        description="colour for the study arm",
    )

    randomization_group: Optional[str] = Field(
        ...,
        title="study_arm_randomization_group",
        description="randomization group for the study arm",
    )

    number_of_subjects: Optional[int] = Field(
        ...,
        title="study_arm_number_of_subjects",
        description="number of subjects for the study arm",
    )

    arm_type: Optional[CTTermName] = Field(
        ..., title="study_arm_type", description="type for the study arm"
    )

    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study selection was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )

    user_initials: Optional[str] = Field(
        ..., title="user_initials", description="User initials for the version"
    )

    end_date: Optional[datetime] = Field(
        None, title="end_date", description="Start date for the version"
    )

    status: Optional[str] = Field(None, title="status", description="Change status")

    change_type: Optional[str] = Field(
        None, title="change_type", description="Type of last change for the version"
    )

    accepted_version: Optional[bool] = Field(
        None,
        title="Accepted Version",
        description="Denotes if user accepted obsolete endpoint and timeframe versions",
    )

    @classmethod
    def from_study_selection_arm_ar_and_order(
        cls,
        study_uid: str,
        selection: StudySelectionArmVO,
        order: int,
        find_simple_term_arm_type_by_term_uid: Callable,
    ):
        if selection.arm_type_uid:
            arm_type_call_back = find_simple_term_arm_type_by_term_uid(
                selection.arm_type_uid
            )
        else:
            arm_type_call_back = None

        return cls(
            study_uid=study_uid,
            arm_uid=selection.study_selection_uid,
            name=selection.name,
            short_name=selection.short_name,
            code=selection.code,
            description=selection.description,
            arm_colour=selection.arm_colour,
            order=order,
            randomization_group=selection.randomization_group,
            number_of_subjects=selection.number_of_subjects,
            arm_type=arm_type_call_back,
            start_date=selection.start_date,
            user_initials=selection.user_initials,
            end_date=selection.end_date,
            status=selection.status,
            change_type=selection.change_type,
            accepted_version=selection.accepted_version,
        )

    @classmethod
    def from_study_selection_history(
        cls,
        study_selection_history: SelectionHistoryArm,
        study_uid: str,
        get_ct_term_arm_type: Callable[[str], CTTermName],
    ) -> "StudySelectionArm":

        if study_selection_history.arm_type:
            arm_type_call_back = get_ct_term_arm_type(study_selection_history.arm_type)
        else:
            arm_type_call_back = None

        return cls(
            study_uid=study_uid,
            order=study_selection_history.order,
            arm_uid=study_selection_history.study_selection_uid,
            name=study_selection_history.arm_name,
            short_name=study_selection_history.arm_short_name,
            code=study_selection_history.arm_code,
            description=study_selection_history.arm_description,
            arm_colour=study_selection_history.arm_colour,
            randomization_group=study_selection_history.arm_randomization_group,
            number_of_subjects=study_selection_history.arm_number_of_subjects,
            arm_type=arm_type_call_back,
            start_date=study_selection_history.start_date,
            user_initials=study_selection_history.user_initials,
            end_date=study_selection_history.end_date,
            status=study_selection_history.status,
            change_type=study_selection_history.change_type,
            accepted_version=study_selection_history.accepted_version,
        )


class StudySelectionArmWithConnectedBranchArms(StudySelectionArm):

    arm_connected_branch_arms: Optional[
        Sequence[StudySelectionBranchArmWithoutStudyArm]
    ] = Field(
        None,
        title="study_branch_arms",
        description="lsit of study branch arms connected to arm",
    )

    @classmethod
    def from_study_selection_arm_ar__order__connected_branch_arms(
        cls,
        study_uid: str,
        selection: StudySelectionArmVO,
        order: int,
        find_simple_term_arm_type_by_term_uid: Callable,
        find_multiple_connected_branch_arm: Callable,
    ):
        if selection.arm_type_uid:
            arm_type_call_back = find_simple_term_arm_type_by_term_uid(
                selection.arm_type_uid
            )
        else:
            arm_type_call_back = None

        return cls(
            study_uid=study_uid,
            arm_uid=selection.study_selection_uid,
            name=selection.name,
            short_name=selection.short_name,
            code=selection.code,
            description=selection.description,
            arm_colour=selection.arm_colour,
            order=order,
            randomization_group=selection.randomization_group,
            number_of_subjects=selection.number_of_subjects,
            arm_type=arm_type_call_back,
            arm_connected_branch_arms=find_multiple_connected_branch_arm(
                study_uid=study_uid,
                study_arm_uid=selection.study_selection_uid,
                user_initials=selection.user_initials,
            ),
            start_date=selection.start_date,
            user_initials=selection.user_initials,
            end_date=selection.end_date,
            status=selection.status,
            change_type=selection.change_type,
            accepted_version=selection.accepted_version,
        )


class StudySelectionArmCreateInput(BaseModel):

    name: str = Field(
        None,
        title="study_arm_name",
        description="name for the study arm",
    )

    short_name: str = Field(
        None,
        title="study_arm_short_name",
        description="short name for the study arm",
    )

    code: Optional[str] = Field(
        None,
        title="study_arm_code",
        description="code for the study arm",
    )

    description: Optional[str] = Field(
        None,
        title="study_description",
        description="description for the study arm",
    )

    arm_colour: Optional[str] = Field(
        None,
        title="study_arm_colour",
        description="colour for the study arm",
    )

    randomization_group: Optional[str] = Field(
        None,
        title="study_arm_randomization_group",
        description="randomization group for the study arm",
    )

    number_of_subjects: Optional[int] = Field(
        None,
        title="study_arm_number_of_subjects",
        description="number of subjects for the study arm",
    )

    arm_type_uid: Optional[str] = Field(
        None,
        title="study_arm_type_uid",
        description="uid for the study arm",
    )


class StudySelectionArmInput(StudySelectionArmCreateInput):

    arm_uid: str = Field(
        None,
        title="study_arm_uid",
        description="uid for the study arm",
    )


class StudySelectionArmNewOrder(BaseModel):

    new_order: int = Field(
        ...,
        title="new_order",
        description="new order of the selected arm",
    )


class StudySelectionArmVersion(StudySelectionArm):
    changes: Dict


# Study Activity Instructions


class StudyActivityInstruction(BaseModel):
    class Config:
        orm_mode = True

    study_activity_instruction_uid: Optional[str] = Field(
        ...,
        title="study_activity_instruction_uid",
        description="uid for the study activity instruction",
        source="uid",
    )

    study_uid: str = Field(
        ...,
        title="study_uid",
        description="The uid of the study",
        source="study_value.study_root.uid",
    )

    study_activity_uid: Optional[str] = Field(
        ...,
        title="study_activity_uid",
        description="uid for the study activity",
        source="study_activity.uid",
    )

    activity_instruction_uid: str = Field(
        title="activity_instruction_uid",
        description="The related activity instruction UID",
        source="activity_instruction_value.activity_instruction_root.uid",
    )

    activity_instruction_name: str = Field(
        title="activity_instruction_name",
        description="The related activity instruction name",
        source="activity_instruction_value.name",
    )

    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study selection was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
        source="has_after.date",
    )

    user_initials: Optional[str] = Field(
        ...,
        title="user_initials",
        description="User initials for the version",
        source="has_after.user_initials",
    )

    end_date: Optional[datetime] = Field(
        None, title="end_date", description="Start date for the version"
    )

    @classmethod
    def from_vo(
        cls, instruction_vo: StudyActivityInstructionVO
    ) -> "StudyActivityInstruction":
        return cls(
            study_activity_instruction_uid=instruction_vo.uid,
            study_uid=instruction_vo.study_uid,
            study_activity_uid=instruction_vo.study_activity_uid,
            activity_instruction_name=instruction_vo.activity_instruction_name,
            activity_instruction_uid=instruction_vo.activity_instruction_uid,
            start_date=instruction_vo.start_date,
            user_initials=instruction_vo.user_initials,
        )


class StudyActivityInstructionCreateInput(BaseModel):
    activity_instruction_data: Optional[ActivityInstructionCreateInput] = Field(
        None,
        title="activity_instruction_data",
        description="Data to create new activity instruction",
    )

    activity_instruction_uid: Optional[str] = Field(
        None,
        title="activity_instruction_uid",
        description="The uid of an existing activity instruction",
    )

    study_activity_uid: str = Field(
        ..., title="study_activity_uid", description="uid for the study activity"
    )

    @root_validator(pre=False)
    @classmethod
    def check_required_fields(cls, values):
        data, uid = values.get("activity_instruction_data"), values.get(
            "activity_instruction_uid"
        )
        if not data and not uid:
            raise ValueError(
                "You must provide activity_instruction_data or activity_instruction_uid"
            )
        return values


class StudyActivityInstructionDeleteInput(BaseModel):
    study_activity_instruction_uid: Optional[str] = Field(
        ...,
        title="study_activity_instruction_uid",
        description="uid for the study activity instruction",
        source="uid",
    )


class StudyActivityInstructionBatchInput(BaseModel):
    method: str = Field(
        ..., title="method", description="HTTP method corresponding to operation type"
    )
    content: Union[
        StudyActivityInstructionCreateInput, StudyActivityInstructionDeleteInput
    ]


class StudyActivityInstructionBatchOutput(BaseModel):
    response_code: int = Field(
        ...,
        title="response_code",
        description="The HTTP response code related to input operation",
    )
    content: Union[StudyActivityInstruction, None, BatchErrorResponse]


"""
    Study elements
"""


class StudySelectionElement(StudySelection):
    element_uid: Optional[str] = Field(
        ...,
        title="study_element_uid",
        description="uid for the study element",
    )

    name: Optional[str] = Field(
        ...,
        title="study_element_name",
        description="name for the study element",
    )

    short_name: Optional[str] = Field(
        ...,
        title="study_element_short_name",
        description="short name for the study element",
    )

    code: Optional[str] = Field(
        ...,
        title="study_element_code",
        description="code for the study element",
    )

    description: Optional[str] = Field(
        ...,
        title="study_element_description",
        description="description for the study element",
    )

    planned_duration: Optional[DurationJsonModel] = Field(
        ...,
        title="study_element_planned_duration",
        description="planned_duration for the study element",
    )

    start_rule: Optional[str] = Field(
        ...,
        title="study_element_start_rule",
        description="start_rule for the study element",
    )

    end_rule: Optional[str] = Field(
        ...,
        title="study_element_end_rule",
        description="end_rule for the study element",
    )

    element_colour: Optional[str] = Field(
        ...,
        title="study_elementelement_colour",
        description="element_colour for the study element",
    )

    element_subtype: Optional[CTTermName] = Field(
        ..., title="study_element_subtype", description="subtype for the study element"
    )

    study_compound_dosing_count: Optional[int] = Field(
        None, description="Number of compound dosing linked to Study Element"
    )

    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study selection was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )

    user_initials: Optional[str] = Field(
        ..., title="user_initials", description="User initials for the version"
    )

    end_date: Optional[datetime] = Field(
        None, title="end_date", description="Start date for the version"
    )

    status: Optional[str] = Field(None, title="status", description="Change status")

    change_type: Optional[str] = Field(
        None, title="change_type", description="Type of last change for the version"
    )

    accepted_version: Optional[bool] = Field(
        None,
        title="Accepted Version",
        description="Denotes if user accepted obsolete endpoint and timeframe versions",
    )

    @classmethod
    def from_study_selection_element_ar_and_order(
        cls,
        study_uid: str,
        selection: StudySelectionElementVO,
        order: int,
        find_simple_term_element_subtype_by_term_uid: Callable,
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
    ) -> "StudySelectionElement":
        return cls(
            study_uid=study_uid,
            element_uid=selection.study_selection_uid,
            name=selection.name,
            short_name=selection.short_name,
            code=selection.code,
            description=selection.description,
            planned_duration=(
                DurationJsonModel.from_duration_object(
                    duration=selection.planned_duration,
                    find_all_study_time_units=find_all_study_time_units,
                )
                if selection.planned_duration is not None
                else None
            ),
            start_rule=selection.start_rule,
            end_rule=selection.end_rule,
            element_colour=selection.element_colour,
            order=order,
            element_subtype=find_simple_term_element_subtype_by_term_uid(
                selection.element_subtype_uid
            ),
            study_compound_dosing_count=selection.study_compound_dosing_count,
            start_date=selection.start_date,
            user_initials=selection.user_initials,
            end_date=selection.end_date,
            status=selection.status,
            change_type=selection.change_type,
            accepted_version=selection.accepted_version,
        )

    @classmethod
    def from_study_selection_history(
        cls,
        study_selection_history: SelectionHistoryElement,
        study_uid: str,
        get_ct_term_element_subtype: Callable[[str], CTTermName],
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
    ) -> "StudySelectionElement":
        return cls(
            study_uid=study_uid,
            order=study_selection_history.order,
            element_uid=study_selection_history.study_selection_uid,
            name=study_selection_history.element_name,
            short_name=study_selection_history.element_short_name,
            code=study_selection_history.element_code,
            description=study_selection_history.element_description,
            planned_duration=(
                DurationJsonModel.from_duration_object(
                    duration=study_selection_history.element_planned_duration,
                    find_all_study_time_units=find_all_study_time_units,
                )
                if study_selection_history.element_planned_duration is not None
                else None
            ),
            start_rule=study_selection_history.element_start_rule,
            end_rule=study_selection_history.element_end_rule,
            element_colour=study_selection_history.element_colour,
            element_subtype=get_ct_term_element_subtype(
                study_selection_history.element_subtype
            ),
            start_date=study_selection_history.start_date,
            user_initials=study_selection_history.user_initials,
            end_date=study_selection_history.end_date,
            status=study_selection_history.status,
            change_type=study_selection_history.change_type,
            accepted_version=study_selection_history.accepted_version,
        )


class StudySelectionElementCreateInput(BaseModel):

    name: str = Field(
        None,
        title="study_element_name",
        description="name for the study element",
    )

    short_name: str = Field(
        None,
        title="study_element_short_name",
        description="short name for the study element",
    )

    code: Optional[str] = Field(
        None,
        title="study_element_code",
        description="code for the study element",
    )

    description: Optional[str] = Field(
        None,
        title="study_description",
        description="description for the study element",
    )

    planned_duration: Optional[DurationJsonModel] = Field(
        None,
        title="study_element_planned_duration",
        description="planned_duration for the study element",
    )

    start_rule: Optional[str] = Field(
        None,
        title="study_element_start_rule",
        description="start_rule for the study element",
    )

    end_rule: Optional[str] = Field(
        None,
        title="study_element_end_rule",
        description="end_rule for the study element",
    )

    element_colour: Optional[str] = Field(
        None,
        title="studyelement_colour",
        description="element_colour for the study element",
    )

    element_subtype_uid: str = Field(
        None,
        title="study_element_subtype_uid",
        description="uid for the study element",
    )


class StudySelectionElementInput(StudySelectionElementCreateInput):

    element_uid: str = Field(
        None,
        title="study_element_uid",
        description="uid for the study element",
    )

    @classmethod
    def from_study_selection_element(
        cls,
        selection: StudySelectionElementVO,
        find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
    ) -> "StudySelectionElementInput":
        return cls(
            element_uid=selection.study_selection_uid,
            name=selection.name,
            short_name=selection.short_name,
            code=selection.code,
            description=selection.description,
            planned_duration=(
                DurationJsonModel.from_duration_object(
                    duration=selection.planned_duration,
                    find_all_study_time_units=find_all_study_time_units,
                )
                if selection.planned_duration is not None
                else None
            ),
            start_rule=selection.start_rule,
            end_rule=selection.end_rule,
            element_colour=selection.element_colour,
            element_subtype_uid=selection.element_subtype_uid,
        )


class StudyElementTypes(BaseModel):
    type: str = Field(..., title="Type uid", description="Element type uid")
    type_name: str = Field(..., title="Type name", description="Element type name")
    subtype: str = Field(..., title="Subtype", description="Element subtype uid")
    subtype_name: str = Field(
        ..., title="Subtype name", description="Element subtype name"
    )


class StudySelectionElementNewOrder(BaseModel):

    new_order: int = Field(
        ...,
        title="new_order",
        description="new order of the selected element",
    )


class StudySelectionElementVersion(StudySelectionElement):
    changes: Dict


"""
    Study brancharms adding Arm Root parameter
"""


class StudySelectionBranchArm(StudySelectionBranchArmWithoutStudyArm):

    arm_root: StudySelectionArm = Field(
        ..., title="study_arm_root", description="Root for the study branch arm"
    )

    @classmethod
    def from_study_selection_branch_arm_ar_and_order(
        cls,
        study_uid: str,
        selection: StudySelectionBranchArmVO,
        order: int,
        find_simple_term_branch_arm_root_by_term_uid: Callable,
    ):
        return cls(
            study_uid=study_uid,
            branch_arm_uid=selection.study_selection_uid,
            name=selection.name,
            short_name=selection.short_name,
            code=selection.code,
            description=selection.description,
            colour_code=selection.colour_code,
            order=order,
            randomization_group=selection.randomization_group,
            number_of_subjects=selection.number_of_subjects,
            arm_root=find_simple_term_branch_arm_root_by_term_uid(
                study_uid, selection.arm_root_uid
            ),
            start_date=selection.start_date,
            user_initials=selection.user_initials,
            end_date=selection.end_date,
            status=selection.status,
            change_type=selection.change_type,
            accepted_version=selection.accepted_version,
        )

    @classmethod
    def from_study_selection_history(
        cls,
        study_selection_history: SelectionHistoryBranchArm,
        study_uid: str,
        find_simple_term_branch_arm_root_by_term_uid: Callable[[str], CTTermName],
    ) -> "StudySelectionBranchArm":
        return cls(
            study_uid=study_uid,
            order=study_selection_history.order,
            branch_arm_uid=study_selection_history.study_selection_uid,
            name=study_selection_history.branch_arm_name,
            short_name=study_selection_history.branch_arm_short_name,
            code=study_selection_history.branch_arm_code,
            description=study_selection_history.branch_arm_description,
            colour_code=study_selection_history.branch_arm_colour_code,
            randomization_group=study_selection_history.branch_arm_randomization_group,
            number_of_subjects=study_selection_history.branch_arm_number_of_subjects,
            arm_root=find_simple_term_branch_arm_root_by_term_uid(
                study_uid, study_selection_history.arm_root
            ),
            start_date=study_selection_history.start_date,
            user_initials=study_selection_history.user_initials,
            end_date=study_selection_history.end_date,
            status=study_selection_history.status,
            change_type=study_selection_history.change_type,
            accepted_version=study_selection_history.accepted_version,
        )


class StudySelectionBranchArmHistory(StudySelectionBranchArmWithoutStudyArm):
    """
    Class created to describe Study BranchArm History, it specifies the ArmRootUid instead of ArmRoot to handle non longer existent Arms
    """

    arm_root_uid: str = Field(
        ..., title="study_arm_root_uid", description="Uid Root for the study branch arm"
    )

    @classmethod
    def from_study_selection_history(
        cls,
        study_selection_history: SelectionHistoryBranchArm,
        study_uid: str,
    ) -> "StudySelectionBranchArmHistory":
        return cls(
            study_uid=study_uid,
            order=study_selection_history.order,
            branch_arm_uid=study_selection_history.study_selection_uid,
            name=study_selection_history.branch_arm_name,
            short_name=study_selection_history.branch_arm_short_name,
            code=study_selection_history.branch_arm_code,
            description=study_selection_history.branch_arm_description,
            colour_code=study_selection_history.branch_arm_colour_code,
            randomization_group=study_selection_history.branch_arm_randomization_group,
            number_of_subjects=study_selection_history.branch_arm_number_of_subjects,
            arm_root_uid=study_selection_history.arm_root,
            start_date=study_selection_history.start_date,
            user_initials=study_selection_history.user_initials,
            end_date=study_selection_history.end_date,
            status=study_selection_history.status,
            change_type=study_selection_history.change_type,
            accepted_version=study_selection_history.accepted_version,
        )


class StudySelectionBranchArmCreateInput(BaseModel):

    name: str = Field(
        None,
        title="study_branch_arm_name",
        description="name for the study Brancharm",
    )

    short_name: str = Field(
        None,
        title="study_branch_arm_short_name",
        description="short name for the study Brancharm",
    )

    code: Optional[str] = Field(
        None,
        title="study_branch_arm_code",
        description="code for the study Brancharm",
    )

    description: Optional[str] = Field(
        None,
        title="study_description",
        description="description for the study Brancharm",
    )

    colour_code: Optional[str] = Field(
        None,
        title="studycolour_code",
        description="colour_code for the study Brancharm",
    )

    randomization_group: Optional[str] = Field(
        None,
        title="study_branch_arm_randomization_group",
        description="randomization group for the study Brancharm",
    )

    number_of_subjects: Optional[int] = Field(
        None,
        title="study_branch_arm_number_of_subjects",
        description="number of subjects for the study Brancharm",
    )

    arm_uid: str = Field(
        None,
        title="study_armt_uid",
        description="uid for the study arm",
    )


class StudySelectionBranchArmEditInput(StudySelectionBranchArmCreateInput):

    branch_arm_uid: str = Field(
        None,
        title="study_branch_arm_uid",
        description="uid for the study branch arm",
    )


class StudySelectionBranchArmNewOrder(BaseModel):

    new_order: int = Field(
        ...,
        title="new_order",
        description="new order of the selected branch arm",
    )


class StudySelectionBranchArmVersion(StudySelectionBranchArmHistory):
    changes: Dict


"""
    Study cohorts
"""


class StudySelectionCohortWithoutArmBranArmRoots(StudySelection):
    cohort_uid: Optional[str] = Field(
        ...,
        title="study_cohort_uid",
        description="uid for the study Cohort",
    )

    name: str = Field(
        ...,
        title="study_cohort_name",
        description="name for the study Cohort",
    )

    short_name: str = Field(
        ...,
        title="study_cohort_short_name",
        description="short name for the study Cohort",
    )

    code: Optional[str] = Field(
        None,
        title="study_cohort_code",
        description="code for the study Cohort",
    )

    description: Optional[str] = Field(
        ...,
        title="study_cohort_description",
        description="description for the study Cohort",
    )

    colour_code: Optional[str] = Field(
        ...,
        title="study_cohort_colour_code",
        description="colour code for the study Cohort",
    )

    number_of_subjects: Optional[int] = Field(
        ...,
        title="study_cohort_number_of_subjects",
        description="number of subjects for the study Cohort",
    )

    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study selection was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )

    user_initials: Optional[str] = Field(
        ..., title="user_initials", description="User initials for the version"
    )

    end_date: Optional[datetime] = Field(
        None, title="end_date", description="Start date for the version"
    )

    status: Optional[str] = Field(None, title="status", description="Change status")

    change_type: Optional[str] = Field(
        None, title="change_type", description="Type of last change for the version"
    )

    accepted_version: Optional[bool] = Field(
        None,
        title="Accepted Version",
        description="Denotes if user accepted obsolete endpoint and timeframe versions",
    )


class StudySelectionCohort(StudySelectionCohortWithoutArmBranArmRoots):

    branch_arm_roots: Optional[Sequence[StudySelectionBranchArm]] = Field(
        None,
        title="study_branch_arm_roots",
        description="Branch Arm Roots for the study Cohort",
    )

    arm_roots: Optional[Sequence[StudySelectionArm]] = Field(
        None, title="study_arm_roots", description="ArmRoots for the study Cohort"
    )

    @classmethod
    def from_study_selection_cohort_ar_and_order(
        cls,
        study_uid: str,
        selection: StudySelectionCohortVO,
        order: int,
        find_arm_root_by_uid: Callable = None,
        find_branch_arm_root_cohort_by_uid: Union[Callable, None] = None,
    ):

        """
        Factory method
        :param study_uid
        :param selection
        :param order
        :param find_project_by_study_uid
        :param find_arm_root_by_uid
        :param find_branch_arm_root_cohort_by_uid
        :return:
        """
        if selection.branch_arm_root_uids:
            branch_arm_roots = [
                find_branch_arm_root_cohort_by_uid(study_uid, branch_arm_root_uid)
                for branch_arm_root_uid in selection.branch_arm_root_uids
            ]
        else:
            branch_arm_roots = None

        if selection.arm_root_uids:
            arm_roots = [
                find_arm_root_by_uid(study_uid, arm_root_uid)
                for arm_root_uid in selection.arm_root_uids
            ]
        else:
            arm_roots = None

        return cls(
            study_uid=study_uid,
            cohort_uid=selection.study_selection_uid,
            name=selection.name,
            short_name=selection.short_name,
            code=selection.code,
            description=selection.description,
            order=order,
            colour_code=selection.colour_code,
            number_of_subjects=selection.number_of_subjects,
            branch_arm_roots=branch_arm_roots,
            arm_roots=arm_roots,
            start_date=selection.start_date,
            user_initials=selection.user_initials,
            end_date=selection.end_date,
            status=selection.status,
            change_type=selection.change_type,
            accepted_version=selection.accepted_version,
        )


class StudySelectionCohortHistory(StudySelectionCohortWithoutArmBranArmRoots):

    branch_arm_roots_uids: Optional[Sequence[str]] = Field(
        None,
        title="study_branch_arm_roots_uids",
        description="Branch Arm Roots Uids for the study Cohort",
    )

    arm_roots_uids: Optional[Sequence[str]] = Field(
        None,
        title="study_arm_roots_uids",
        description="ArmRoots Uids for the study Cohort",
    )

    @classmethod
    def from_study_selection_history(
        cls,
        study_selection_history: SelectionHistoryCohort,
        study_uid: str,
    ) -> "StudySelectionCohortHistory":

        if study_selection_history.branch_arm_roots:
            branch_arm_roots_uids = study_selection_history.branch_arm_roots
        else:
            branch_arm_roots_uids = None

        if study_selection_history.arm_roots:
            arm_roots_uids = study_selection_history.arm_roots
        else:
            arm_roots_uids = None

        return cls(
            study_uid=study_uid,
            order=study_selection_history.order,
            cohort_uid=study_selection_history.study_selection_uid,
            name=study_selection_history.cohort_name,
            short_name=study_selection_history.cohort_short_name,
            code=study_selection_history.cohort_code,
            description=study_selection_history.cohort_description,
            colour_code=study_selection_history.cohort_colour_code,
            number_of_subjects=study_selection_history.cohort_number_of_subjects,
            branch_arm_roots_uids=branch_arm_roots_uids,
            arm_roots_uids=arm_roots_uids,
            start_date=study_selection_history.start_date,
            user_initials=study_selection_history.user_initials,
            end_date=study_selection_history.end_date,
            status=study_selection_history.status,
            change_type=study_selection_history.change_type,
            accepted_version=study_selection_history.accepted_version,
        )


class StudySelectionCohortCreateInput(BaseModel):

    name: str = Field(
        None,
        title="study_cohort_name",
        description="name for the study Cohort",
    )

    short_name: str = Field(
        None,
        title="study_cohort_short_name",
        description="short name for the study Cohort",
    )

    code: Optional[str] = Field(
        None,
        title="study_cohort_code",
        description="code for the study Cohort",
    )

    description: Optional[str] = Field(
        None,
        title="study_description",
        description="description for the study Cohort",
    )

    colour_code: Optional[str] = Field(
        None,
        title="study_cohort_colour_code",
        description="colour code for the study Cohort",
    )

    number_of_subjects: Optional[int] = Field(
        None,
        title="study_cohort_number_of_subjects",
        description="number of subjects for the study Cohort",
    )

    branch_arm_uids: Optional[Sequence[str]] = Field(
        None,
        title="studybranch_arm_uid",
        description="uid for the study branch arm",
    )

    arm_uids: Optional[Sequence[str]] = Field(
        None,
        title="study_armt_uid",
        description="uid for the study arm",
    )


class StudySelectionCohortEditInput(StudySelectionCohortCreateInput):

    cohort_uid: str = Field(
        None,
        title="study_cohort_uid",
        description="uid for the study Cohort",
    )


class StudySelectionCohortNewOrder(BaseModel):

    new_order: int = Field(
        ...,
        title="new_order",
        description="new order of the selected Cohort",
    )


class StudySelectionCohortVersion(StudySelectionCohortHistory):
    changes: Dict


#
# Study compound dosing
#


class StudyCompoundDosing(StudySelection):

    study_compound_dosing_uid: Optional[str] = Field(
        ...,
        title="study_compound_dosing_uid",
        description="uid for the study compound dosing",
    )

    study_compound: StudySelectionCompound = Field(
        ..., title="study_compound", description="The related study compound"
    )

    study_element: StudySelectionElement = Field(
        ..., title="study_element", description="The related study element"
    )

    dose_value: Optional[SimpleNumericValueWithUnit] = Field(
        None,
        title="dose",
        description="compound dose defined for the study selection",
    )

    dose_frequency: Optional[SimpleTermModel] = Field(
        None,
        title="dose_frequency",
        description="dose frequency defined for the study selection",
    )

    start_date: Optional[datetime] = Field(
        ...,
        title="start_date",
        description="The most recent point in time when the study selection was edited."
        "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
    )

    user_initials: Optional[str] = Field(
        ..., title="user_initials", description="User initials for the version"
    )

    end_date: Optional[datetime] = Field(
        None, title="end_date", description="Start date for the version"
    )
    change_type: Optional[str] = Field(
        None, title="change_type", description="Type of last change for the version"
    )

    @classmethod
    def from_vo(
        cls,
        compound_dosing_vo: StudyCompoundDosingVO,
        order: int,
        study_compound_model: StudySelectionCompound,
        study_element_model: StudySelectionElement,
        find_simple_term_model_name_by_term_uid: Callable,
        find_unit_by_uid: Callable[[str], Optional[UnitDefinitionAR]],
        find_numeric_value_by_uid: Callable[[str], Optional[NumericValueWithUnitAR]],
    ) -> "StudyCompoundDosing":
        return cls(
            order=order,
            study_compound_dosing_uid=compound_dosing_vo.study_selection_uid,
            study_uid=compound_dosing_vo.study_uid,
            study_compound=study_compound_model,
            study_element=study_element_model,
            dose_value=SimpleNumericValueWithUnit.from_concept_uid(
                uid=compound_dosing_vo.dose_value_uid,
                find_unit_by_uid=find_unit_by_uid,
                find_numeric_value_by_uid=find_numeric_value_by_uid,
            ),
            dose_frequency=find_simple_term_model_name_by_term_uid(
                compound_dosing_vo.dose_frequency_uid
            ),
            start_date=compound_dosing_vo.start_date,
            user_initials=compound_dosing_vo.user_initials,
        )

    @classmethod
    def from_study_selection_history(
        cls,
        study_selection_history: StudyCompoundDosingSelectionHistory,
        study_uid: str,
        order: int,
        study_compound_model: StudySelectionCompound,
        study_element_model: StudySelectionElement,
        find_simple_term_model_name_by_term_uid: Callable,
        find_unit_by_uid: Callable[[str], Optional[UnitDefinitionAR]],
        find_numeric_value_by_uid: Callable[[str], Optional[NumericValueWithUnitAR]],
    ) -> "StudyCompoundDosing":
        return cls(
            study_compound_dosing_uid=study_selection_history.study_selection_uid,
            study_uid=study_uid,
            order=order,
            study_compound=study_compound_model,
            study_element=study_element_model,
            dose_value=SimpleNumericValueWithUnit.from_concept_uid(
                uid=study_selection_history.dose_value_uid,
                find_unit_by_uid=find_unit_by_uid,
                find_numeric_value_by_uid=find_numeric_value_by_uid,
            ),
            dose_frequency=find_simple_term_model_name_by_term_uid(
                study_selection_history.dose_frequency_uid
            ),
            start_date=study_selection_history.start_date,
            end_date=study_selection_history.end_date,
            change_type=study_selection_history.change_type,
            user_initials=study_selection_history.user_initials,
        )


class StudyCompoundDosingInput(BaseModel):

    study_compound_uid: str = Field(
        ..., title="study_compound_uid", description="The related study compound uid"
    )

    study_element_uid: str = Field(
        ..., title="study_element_uid", description="The related study element uid"
    )

    dose_value_uid: Optional[str] = Field(
        None,
        title="dose_value_uid",
        description="compound dose defined for the study selection",
    )

    dose_frequency_uid: Optional[str] = Field(
        None,
        title="dose_frequency_uid",
        description="dose frequency defined for the study selection",
    )
