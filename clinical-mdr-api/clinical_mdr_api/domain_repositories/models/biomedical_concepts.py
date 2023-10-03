from neomodel import (
    BooleanProperty,
    IntegerProperty,
    One,
    OneOrMore,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
)

from clinical_mdr_api.domain_repositories.models.concepts import UnitDefinitionRoot
from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    CTTermRoot,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    ClinicalMdrRel,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)
from clinical_mdr_api.domain_repositories.models.standard_data_model import (
    DatasetClass,
    VariableClass,
)


class ActivityInstanceClassValue(VersionValue):
    order = IntegerProperty()
    definition = StringProperty()
    is_domain_specific = BooleanProperty()
    has_latest_value = RelationshipFrom(
        "ActivityInstanceClassRoot", "LATEST", model=ClinicalMdrRel
    )


class ActivityInstanceClassRoot(VersionRoot):
    LIBRARY_REL_LABEL = "CONTAINS_ACTIVITY_INSTANCE_CLASS"

    has_version = RelationshipTo(
        ActivityInstanceClassValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(
        ActivityInstanceClassValue, "LATEST", model=ClinicalMdrRel
    )
    latest_draft = RelationshipTo(
        ActivityInstanceClassValue, "LATEST_DRAFT", model=VersionRelationship
    )
    latest_final = RelationshipTo(
        ActivityInstanceClassValue, "LATEST_FINAL", model=VersionRelationship
    )
    latest_retired = RelationshipTo(
        ActivityInstanceClassValue, "LATEST_RETIRED", model=VersionRelationship
    )
    parent_class = RelationshipTo(
        "ActivityInstanceClassRoot", "PARENT_CLASS", model=ClinicalMdrRel
    )
    maps_dataset_class = RelationshipTo(
        DatasetClass,
        "MAPS_DATASET_CLASS",
        model=ClinicalMdrRel,
    )


class ActivityItemClassValue(VersionValue):
    order = IntegerProperty()
    mandatory = BooleanProperty()
    has_latest_value = RelationshipFrom(
        "ActivityItemClassRoot", "LATEST", model=ClinicalMdrRel
    )
    has_data_type = RelationshipTo(
        CTTermRoot, "HAS_DATA_TYPE", model=ClinicalMdrRel, cardinality=One
    )
    has_role = RelationshipTo(
        CTTermRoot, "HAS_ROLE", model=ClinicalMdrRel, cardinality=One
    )


class ActivityItemClassRoot(VersionRoot):
    LIBRARY_REL_LABEL = "CONTAINS_ACTIVITY_ITEM_CLASS"

    has_version = RelationshipTo(
        ActivityItemClassValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(
        ActivityItemClassValue, "LATEST", model=ClinicalMdrRel
    )
    latest_draft = RelationshipTo(
        ActivityItemClassValue, "LATEST_DRAFT", model=VersionRelationship
    )
    latest_final = RelationshipTo(
        ActivityItemClassValue, "LATEST_FINAL", model=VersionRelationship
    )
    latest_retired = RelationshipTo(
        ActivityItemClassValue, "LATEST_RETIRED", model=VersionRelationship
    )
    has_activity_instance_class = RelationshipFrom(
        "ActivityInstanceClassRoot",
        "HAS_ITEM_CLASS",
        model=ClinicalMdrRel,
        cardinality=OneOrMore,
    )
    maps_variable_class = RelationshipTo(
        VariableClass,
        "MAPS_VARIABLE_CLASS",
        model=ClinicalMdrRel,
    )


class ActivityItemValue(VersionValue):
    has_version = RelationshipFrom(
        "ActivityItemRoot", "HAS_VERSION", model=VersionRelationship
    )
    has_ct_term = RelationshipTo(CTTermRoot, "HAS_CT_TERM", model=ClinicalMdrRel)
    has_unit_definition = RelationshipTo(
        UnitDefinitionRoot, "HAS_UNIT_DEFINITION", model=ClinicalMdrRel
    )


class ActivityItemRoot(VersionRoot):
    LIBRARY_REL_LABEL = "CONTAINS_ACTIVITY_ITEM"

    has_version = RelationshipTo(
        ActivityItemValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(ActivityItemValue, "LATEST", model=ClinicalMdrRel)
    latest_draft = RelationshipTo(
        ActivityItemValue, "LATEST_DRAFT", model=ClinicalMdrRel
    )
    latest_final = RelationshipTo(
        ActivityItemValue, "LATEST_FINAL", model=ClinicalMdrRel
    )
    latest_retired = RelationshipTo(
        ActivityItemValue, "LATEST_RETIRED", model=ClinicalMdrRel
    )
    has_activity_item_class = RelationshipFrom(
        ActivityItemClassRoot,
        "HAS_ACTIVITY_ITEM",
        model=ClinicalMdrRel,
    )
