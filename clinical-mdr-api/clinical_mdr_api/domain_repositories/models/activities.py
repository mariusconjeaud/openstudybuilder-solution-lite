from neomodel import One, RelationshipFrom, RelationshipTo, StringProperty, ZeroOrOne

from clinical_mdr_api.domain_repositories.models.biomedical_concepts import (
    ActivityInstanceClassRoot,
    ActivityItemValue,
)
from clinical_mdr_api.domain_repositories.models.concepts import (
    ConceptRoot,
    ConceptValue,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    ClinicalMdrRel,
    VersionRelationship,
)


class ActivityGroupValue(ConceptValue):
    has_latest_value = RelationshipFrom("ActivityGroupRoot", "LATEST")


class ActivityGroupRoot(ConceptRoot):
    has_version = RelationshipTo(
        ActivityGroupValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(ActivityGroupValue, "LATEST")
    latest_draft = RelationshipTo(ActivityGroupValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(ActivityGroupValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(ActivityGroupValue, "LATEST_RETIRED")


class ActivitySubGroupValue(ConceptValue):
    has_latest_value = RelationshipFrom("ActivitySubGroupRoot", "LATEST")
    in_group = RelationshipTo(ActivityGroupValue, "IN_GROUP", model=ClinicalMdrRel)


class ActivitySubGroupRoot(ConceptRoot):
    has_version = RelationshipTo(
        ActivitySubGroupValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(ActivitySubGroupValue, "LATEST")
    latest_draft = RelationshipTo(ActivitySubGroupValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(ActivitySubGroupValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(ActivitySubGroupValue, "LATEST_RETIRED")


class ActivityValue(ConceptValue):
    has_latest_value = RelationshipFrom("ActivityRoot", "LATEST", model=ClinicalMdrRel)
    latest_draft = RelationshipFrom("ActivityRoot", "LATEST_DRAFT")
    latest_final = RelationshipFrom("ActivityRoot", "LATEST_FINAL")
    latest_retired = RelationshipFrom("ActivityRoot", "LATEST_RETIRED")
    in_subgroup = RelationshipTo(
        ActivitySubGroupValue, "IN_SUB_GROUP", model=ClinicalMdrRel
    )
    request_rationale = StringProperty()
    replaced_by_activity = RelationshipTo(
        "ActivityRoot",
        "REPLACED_BY_ACTIVITY",
        model=ClinicalMdrRel,
        cardinality=ZeroOrOne,
    )


class ActivityRoot(ConceptRoot):
    has_version = RelationshipTo(
        ActivityValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(ActivityValue, "LATEST")
    latest_draft = RelationshipTo(ActivityValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(ActivityValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(ActivityValue, "LATEST_RETIRED")


class ActivityInstanceValue(ConceptValue):
    topic_code = StringProperty()
    adam_param_code = StringProperty()
    legacy_description = StringProperty()

    in_hierarchy = RelationshipTo(ActivityValue, "IN_HIERARCHY")
    activity_instance_class = RelationshipTo(
        ActivityInstanceClassRoot, "ACTIVITY_INSTANCE_CLASS", cardinality=One
    )
    contains_activity_item = RelationshipTo(ActivityItemValue, "CONTAINS_ACTIVITY_ITEM")


class ActivityInstanceRoot(ConceptRoot):
    has_version = RelationshipTo(
        ActivityInstanceValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(ActivityInstanceValue, "LATEST")
    latest_draft = RelationshipTo(ActivityInstanceValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(ActivityInstanceValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(ActivityInstanceValue, "LATEST_RETIRED")
