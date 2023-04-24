from neomodel import (
    BooleanProperty,
    IntegerProperty,
    OneOrMore,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    ZeroOrOne,
)

from clinical_mdr_api.domain_repositories.models.concepts import (
    ConceptRoot,
    UnitDefinitionRoot,
)
from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    CTTermRoot,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    ClinicalMdrRel,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)


class ActivityItem(ConceptRoot):
    has_sdtm_variable = RelationshipTo(
        CTTermRoot, "TABULATED_IN", cardinality=ZeroOrOne
    )
    has_cdash_variable = RelationshipTo(CTTermRoot, "HAS_CDASH", cardinality=ZeroOrOne)


class ActivityDefinition(ActivityItem):
    has_sdtm_domain = RelationshipTo(
        CTTermRoot, "HAS_SDTM_DOMAIN", cardinality=ZeroOrOne
    )
    has_sdtm_cat = RelationshipTo(CTTermRoot, "HAS_SDTM_CAT", cardinality=ZeroOrOne)
    has_sdtm_subcat = RelationshipTo(
        CTTermRoot, "HAS_SDTM_SUBCAT", cardinality=ZeroOrOne
    )

    # Findings specific
    has_findings_test_code = RelationshipTo(
        CTTermRoot, "HAS_TEST_CODE", cardinality=ZeroOrOne
    )
    has_findings_specimen = RelationshipTo(
        CTTermRoot, "HAS_SPECIMEN", cardinality=ZeroOrOne
    )

    # Numeric Finding specific
    has_numeric_finding_unit_dimension = RelationshipTo(
        CTTermRoot, "HAS_UNIT_DIMENSION", cardinality=ZeroOrOne
    )
    has_numeric_finding_unit_definition = RelationshipTo(
        UnitDefinitionRoot, "HAS_UNIT_DEFINITION", cardinality=ZeroOrOne
    )

    # Categoric Finding specific
    has_categoric_response_value = RelationshipTo(
        CTTermRoot, "HAS_CATEGORIC_RESPONSE_VALUE", cardinality=ZeroOrOne
    )
    has_categoric_response_list = RelationshipTo(
        CTTermRoot, "HAS_CATEGORIC_RESPONSE_LIST", cardinality=ZeroOrOne
    )


class ActivityCollection(ActivityItem):
    has_odm_item = RelationshipTo("OdmItemRoot", "HAS_ODM_ITEM", cardinality=ZeroOrOne)


class ActivityInstanceClassValue(VersionValue):
    order = IntegerProperty()
    definition = StringProperty()
    is_domain_specific = BooleanProperty()
    has_latest_value = RelationshipFrom("ActivityInstanceClassRoot", "LATEST")


class ActivityInstanceClassRoot(VersionRoot):
    LIBRARY_REL_LABEL = "CONTAINS_ACTIVITY_INSTANCE_CLASS"

    has_version = RelationshipTo(
        ActivityInstanceClassValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(ActivityInstanceClassValue, "LATEST")
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


class ActivityItemClassValue(VersionValue):
    order = IntegerProperty()
    mandatory = BooleanProperty()
    has_latest_value = RelationshipFrom("ActivityItemClassRoot", "LATEST")


class ActivityItemClassRoot(VersionRoot):
    LIBRARY_REL_LABEL = "CONTAINS_ACTIVITY_ITEM_CLASS"

    has_version = RelationshipTo(
        ActivityItemClassValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(ActivityItemClassValue, "LATEST")
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


class ActivityItemValue(VersionValue):
    has_version = RelationshipFrom(
        "ActivityItemRoot", "HAS_VERSION", model=VersionRelationship
    )
    has_ct_term = RelationshipTo(CTTermRoot, "HAS_CT_TERM")
    has_unit_definition = RelationshipTo(UnitDefinitionRoot, "HAS_UNIT_DEFINITION")


class ActivityItemRoot(VersionRoot):
    LIBRARY_REL_LABEL = "CONTAINS_ACTIVITY_ITEM"

    has_version = RelationshipTo(
        ActivityItemValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(ActivityItemValue, "LATEST")
    latest_draft = RelationshipTo(ActivityItemValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(ActivityItemValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(ActivityItemValue, "LATEST_RETIRED")
    has_activity_item_class = RelationshipFrom(
        ActivityItemClassRoot,
        "HAS_ACTIVITY_ITEM",
        model=ClinicalMdrRel,
    )
