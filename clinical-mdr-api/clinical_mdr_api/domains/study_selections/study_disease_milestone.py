import datetime
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from clinical_mdr_api.domains.study_definition_aggregates.study_metadata import (
    StudyStatus,
)


@dataclass
class StudyDiseaseMilestoneAllowedConfig:
    dm_type2: str


Type_name_definition = namedtuple("Type_name_definition", ["named", "definition"])


class StudyDiseaseMilestoneType(Type_name_definition, Enum):
    pass


@dataclass
class StudyDiseaseMilestoneVO:
    study_uid: str
    repetition_indicator: bool
    order: int
    status: StudyStatus
    start_date: datetime.datetime
    author: str
    disease_milestone_type: str
    disease_milestone_type_definition: str
    disease_milestone_type_named: str
    accepted_version: bool = False
    uid: Optional[str] = None

    @property
    def dm_type(self):
        return StudyDiseaseMilestoneType[self.disease_milestone_type]

    def edit_core_properties(
        self,
        disease_milestone_type: str,
        repetition_indicator: bool,
    ):
        self.disease_milestone_type = disease_milestone_type
        self.repetition_indicator = repetition_indicator

    def set_order(self, order):
        self.order = order

    @property
    def possible_actions(self):
        if self.status == StudyStatus.DRAFT:
            return ["edit", "delete", "lock"]
        return None


@dataclass
class StudyDiseaseMilestoneHistoryVO(StudyDiseaseMilestoneVO):
    change_type: Optional[str] = None
    end_date: Optional[datetime.datetime] = None
