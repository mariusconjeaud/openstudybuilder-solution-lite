from neomodel import (
    BooleanProperty,
    IntegerProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    ZeroOrMore,
)

from clinical_mdr_api.domain_repositories.models.concepts import UnitDefinitionRoot
from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    CTTermRoot,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    ClinicalMdrRel,
    ConjunctionRelation,
)
from clinical_mdr_api.domain_repositories.models.study import StudyValue
from clinical_mdr_api.domain_repositories.models.study_audit_trail import StudyAction
from clinical_mdr_api.domain_repositories.models.study_selections import (
    StudyDesignCell,
    StudySelection,
)


class OrderedStudySelection(StudySelection):
    accepted_version = BooleanProperty()
    order = IntegerProperty()


class StudyEpoch(OrderedStudySelection):
    study_value = RelationshipFrom(StudyValue, "HAS_STUDY_EPOCH", model=ClinicalMdrRel)
    has_epoch = RelationshipTo(CTTermRoot, "HAS_EPOCH", model=ClinicalMdrRel)
    has_epoch_subtype = RelationshipTo(
        CTTermRoot, "HAS_EPOCH_SUB_TYPE", model=ClinicalMdrRel
    )
    has_epoch_type = RelationshipTo(CTTermRoot, "HAS_EPOCH_TYPE", model=ClinicalMdrRel)
    has_duration_unit = RelationshipTo(
        UnitDefinitionRoot, "HAS_DURATION_UNIT", model=ClinicalMdrRel
    )
    name = StringProperty()
    short_name = StringProperty()
    description = StringProperty()
    start_rule = StringProperty()
    end_rule = StringProperty()
    order = IntegerProperty()
    color_hash = StringProperty()
    status = StringProperty()
    has_design_cell = RelationshipTo(
        StudyDesignCell,
        "STUDY_EPOCH_HAS_DESIGN_CELL",
        model=ClinicalMdrRel,
        cardinality=ZeroOrMore,
    )
    has_study_visit = RelationshipTo(
        ".study_visit.StudyVisit", "STUDY_EPOCH_HAS_STUDY_VISIT", model=ClinicalMdrRel
    )
    has_before = RelationshipFrom(StudyAction, "BEFORE", model=ConjunctionRelation)
    has_after = RelationshipFrom(StudyAction, "AFTER", model=ConjunctionRelation)
