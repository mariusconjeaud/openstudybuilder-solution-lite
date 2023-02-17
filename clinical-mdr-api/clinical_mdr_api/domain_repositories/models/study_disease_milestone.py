from neomodel import (
    BooleanProperty,
    IntegerProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
)

from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    CTTermRoot,
)
from clinical_mdr_api.domain_repositories.models.generic import ConjunctionRelation
from clinical_mdr_api.domain_repositories.models.study import StudyValue
from clinical_mdr_api.domain_repositories.models.study_audit_trail import StudyAction
from clinical_mdr_api.domain_repositories.models.study_selections import StudySelection


class OrderedStudySelectionDiseaseMilestone(StudySelection):
    accepted_version = BooleanProperty()
    order = IntegerProperty()


class StudyDiseaseMilestone(OrderedStudySelectionDiseaseMilestone):
    has_study_disease_milestone = RelationshipFrom(
        StudyValue, "HAS_STUDY_DISEASE_MILESTONE"
    )
    status = StringProperty()
    has_before = RelationshipFrom(StudyAction, "BEFORE", model=ConjunctionRelation)
    has_after = RelationshipFrom(StudyAction, "AFTER", model=ConjunctionRelation)
    has_disease_milestone_type = RelationshipTo(
        CTTermRoot, "HAS_DISEASE_MILESTONE_TYPE"
    )
    repetition_indicator = BooleanProperty()
