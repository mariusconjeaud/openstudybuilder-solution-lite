from neomodel import (
    BooleanProperty,
    IntegerProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    ZeroOrMore,
    db,
)

from clinical_mdr_api.domain_repositories.models.activities import (
    ActivityGroupRoot,
    ActivityRoot,
    ActivitySubGroupRoot,
)
from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    CTTermRoot,
)
from clinical_mdr_api.domain_repositories.models.dictionary import DictionaryTermRoot
from clinical_mdr_api.domain_repositories.models.generic import (
    ClinicalMdrRel,
    Conjunction,
    ConjunctionRelation,
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)
from clinical_mdr_api.domain_repositories.models.template_parameter import (
    TemplateParameter,
    TemplateParameterTermRoot,
)


# pylint: disable=abstract-method
class UsesParameterRelation(ClinicalMdrRel):
    position = IntegerProperty()
    allow_multiple = BooleanProperty()
    allow_none = BooleanProperty()


# pylint: disable=abstract-method
class UsesDefaultValueRelation(ClinicalMdrRel):
    position = IntegerProperty()
    index = IntegerProperty()
    set_number = IntegerProperty()


class SyntaxTemplateValue(VersionValue):
    PARAMETERS_LABEL = "USES_DEFAULT_VALUE"

    name = StringProperty()
    name_plain = StringProperty()
    guidance_text = StringProperty()

    # uses_default_value
    has_parameters = RelationshipTo(
        TemplateParameterTermRoot,
        PARAMETERS_LABEL,
        cardinality=ZeroOrMore,
        model=UsesDefaultValueRelation,
    )
    has_conjunction = RelationshipTo(
        Conjunction,
        "HAS_CONJUNCTION",
        cardinality=ZeroOrMore,
        model=ConjunctionRelation,
    )

    def get_study_count(self, template_rel, study_selection_rel, study_rel) -> int:
        cypher_query = f"""
        MATCH (n)<--(:SyntaxTemplateRoot)-[:{template_rel}]->(:SyntaxInstanceRoot)-->(:SyntaxInstanceValue)<-[:{study_selection_rel}]-(:StudySelection)<-[:{study_rel}]-(:StudyValue)<-[:HAS_VERSION|LATEST_DRAFT|LATEST_FINAL|LATEST_RETIRED]-(sr:StudyRoot)
        WHERE id(n)={self.id}
        RETURN count(DISTINCT sr)
        """

        count, _ = db.cypher_query(cypher_query)
        return count[0][0]


class SyntaxTemplateRoot(VersionRoot):
    LIBRARY_REL_LABEL = "CONTAINS_SYNTAX_TEMPLATE"
    PARAMETERS_LABEL = "USES_PARAMETER"

    editable_instance = BooleanProperty()

    has_indication = RelationshipTo(
        DictionaryTermRoot, "HAS_INDICATION", model=ClinicalMdrRel
    )
    has_study_phase = RelationshipTo(
        CTTermRoot, "HAS_STUDY_PHASE", cardinality=ZeroOrMore, model=ClinicalMdrRel
    )
    # uses_parameter
    has_parameters = RelationshipTo(
        TemplateParameter,
        PARAMETERS_LABEL,
        cardinality=ZeroOrMore,
        model=UsesParameterRelation,
    )

    has_library = RelationshipFrom(Library, LIBRARY_REL_LABEL, model=ClinicalMdrRel)
    has_version = RelationshipTo(
        SyntaxTemplateValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(
        SyntaxTemplateValue, "LATEST", model=ClinicalMdrRel
    )
    latest_draft = RelationshipTo(
        SyntaxTemplateValue, "LATEST_DRAFT", model=VersionRelationship
    )
    latest_final = RelationshipTo(
        SyntaxTemplateValue, "LATEST_FINAL", model=VersionRelationship
    )
    latest_retired = RelationshipTo(
        SyntaxTemplateValue, "LATEST_RETIRED", model=VersionRelationship
    )


class SyntaxIndexingTemplateValue(SyntaxTemplateValue):
    ...


class SyntaxIndexingTemplateRoot(SyntaxTemplateRoot):
    has_category = RelationshipTo(CTTermRoot, "HAS_CATEGORY", model=ClinicalMdrRel)
    has_subcategory = RelationshipTo(
        CTTermRoot, "HAS_SUBCATEGORY", model=ClinicalMdrRel
    )


class CriteriaTemplateValue(SyntaxIndexingTemplateValue):
    def get_study_count(self) -> int:
        return super().get_study_count(
            CriteriaTemplateRoot.TEMPLATE_REL_LABEL,
            "HAS_SELECTED_CRITERIA",
            "HAS_STUDY_CRITERIA",
        )


class CriteriaTemplateRoot(SyntaxIndexingTemplateRoot):
    TEMPLATE_REL_LABEL = "HAS_CRITERIA"

    has_template = RelationshipTo(
        ".syntax_instances.CriteriaRoot", TEMPLATE_REL_LABEL, model=ClinicalMdrRel
    )
    has_type = RelationshipTo(CTTermRoot, "HAS_TYPE", model=ClinicalMdrRel)


class EndpointTemplateValue(SyntaxIndexingTemplateValue):
    def get_study_count(self) -> int:
        return super().get_study_count(
            EndpointTemplateRoot.TEMPLATE_REL_LABEL,
            "HAS_SELECTED_ENDPOINT",
            "HAS_STUDY_ENDPOINT",
        )


class EndpointTemplateRoot(SyntaxIndexingTemplateRoot):
    TEMPLATE_REL_LABEL = "HAS_ENDPOINT"

    has_template = RelationshipTo(
        ".syntax_instances.EndpointRoot", TEMPLATE_REL_LABEL, model=ClinicalMdrRel
    )


class ObjectiveTemplateValue(SyntaxIndexingTemplateValue):
    def get_study_count(self) -> int:
        return super().get_study_count(
            ObjectiveTemplateRoot.TEMPLATE_REL_LABEL,
            "HAS_SELECTED_OBJECTIVE",
            "HAS_STUDY_OBJECTIVE",
        )


class ObjectiveTemplateRoot(SyntaxIndexingTemplateRoot):
    TEMPLATE_REL_LABEL = "HAS_OBJECTIVE"

    is_confirmatory_testing = BooleanProperty()

    has_template = RelationshipTo(
        ".syntax_instances.ObjectiveRoot", TEMPLATE_REL_LABEL, model=ClinicalMdrRel
    )


class ActivityInstructionTemplateValue(SyntaxTemplateValue):
    def get_study_count(self) -> int:
        return super().get_study_count(
            ActivityInstructionTemplateRoot.TEMPLATE_REL_LABEL,
            "HAS_SELECTED_ACTIVITY_INSTRUCTION",
            "HAS_STUDY_ACTIVITY_INSTRUCTION",
        )


class ActivityInstructionTemplateRoot(SyntaxTemplateRoot):
    TEMPLATE_REL_LABEL = "HAS_ACTIVITY_INSTRUCTION"

    has_template = RelationshipTo(
        ".syntax_instances.ActivityInstructionRoot",
        TEMPLATE_REL_LABEL,
        model=ClinicalMdrRel,
    )
    has_activity = RelationshipTo(ActivityRoot, "HAS_ACTIVITY", model=ClinicalMdrRel)
    has_activity_group = RelationshipTo(
        ActivityGroupRoot, "HAS_ACTIVITY_GROUP", model=ClinicalMdrRel
    )
    has_activity_subgroup = RelationshipTo(
        ActivitySubGroupRoot, "HAS_ACTIVITY_SUBGROUP", model=ClinicalMdrRel
    )


class TimeframeTemplateValue(SyntaxTemplateValue):
    def get_study_count(self):
        ...


class TimeframeTemplateRoot(SyntaxTemplateRoot):
    TEMPLATE_REL_LABEL = "HAS_TIMEFRAME"

    has_template = RelationshipTo(
        ".syntax_instances.TimeframeRoot", TEMPLATE_REL_LABEL, model=ClinicalMdrRel
    )
