from neomodel import (
    IntegerProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    ZeroOrMore,
    db,
)

from clinical_mdr_api.domain_repositories.models.generic import (
    ClinicalMdrRel,
    Conjunction,
    ConjunctionRelation,
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)
from clinical_mdr_api.domain_repositories.models.syntax_templates import (
    ActivityInstructionTemplateRoot,
    CriteriaTemplateRoot,
    EndpointTemplateRoot,
    ObjectiveTemplateRoot,
    TimeframeTemplateRoot,
)
from clinical_mdr_api.domain_repositories.models.template_parameter import (
    TemplateParameterTermRoot,
)


# pylint: disable=abstract-method
class UsesValueRelation(ClinicalMdrRel):
    position = IntegerProperty()
    index = IntegerProperty()
    set_number = IntegerProperty()


class SyntaxInstanceValue(VersionValue):
    PARAMETERS_LABEL = "USES_VALUE"

    name = StringProperty()
    name_plain = StringProperty()

    # uses_value
    has_parameters = RelationshipTo(
        TemplateParameterTermRoot,
        PARAMETERS_LABEL,
        cardinality=ZeroOrMore,
        model=UsesValueRelation,
    )
    has_conjunction = RelationshipTo(
        Conjunction,
        "HAS_CONJUNCTION",
        cardinality=ZeroOrMore,
        model=ConjunctionRelation,
    )


class SyntaxInstanceRoot(VersionRoot):
    LIBRARY_REL_LABEL = "CONTAINS_SYNTAX_INSTANCE"

    has_library = RelationshipFrom(Library, LIBRARY_REL_LABEL, model=ClinicalMdrRel)
    has_version = RelationshipTo(
        SyntaxInstanceValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(
        SyntaxInstanceValue, "LATEST", model=ClinicalMdrRel
    )
    latest_draft = RelationshipTo(
        SyntaxInstanceValue, "LATEST_DRAFT", model=VersionRelationship
    )
    latest_final = RelationshipTo(
        SyntaxInstanceValue, "LATEST_FINAL", model=VersionRelationship
    )
    latest_retired = RelationshipTo(
        SyntaxInstanceValue, "LATEST_RETIRED", model=VersionRelationship
    )


class SyntaxIndexingInstanceValue(SyntaxInstanceValue):
    ...


class SyntaxIndexingInstanceRoot(SyntaxInstanceRoot):
    ...


class CriteriaValue(SyntaxIndexingInstanceValue):
    ROOT_NODE_LABEL = "CriteriaRoot"
    VALUE_NODE_LABEL = "CriteriaValue"
    STUDY_SELECTION_REL_LABEL = "HAS_SELECTED_CRITERIA"
    STUDY_VALUE_REL_LABEL = "HAS_STUDY_CRITERIA"


class CriteriaRoot(SyntaxIndexingInstanceRoot):
    TEMPLATE_REL_LABEL = "HAS_CRITERIA"

    has_template = RelationshipFrom(
        CriteriaTemplateRoot, TEMPLATE_REL_LABEL, model=ClinicalMdrRel
    )


# class CriteriaPreInstanceValue(CriteriaValue, SyntaxIndexingInstanceValue):
#     ...


# class CriteriaPreInstanceRoot(CriteriaRoot, SyntaxIndexingInstanceRoot):
#     ...


class EndpointValue(SyntaxIndexingInstanceValue):
    ROOT_NODE_LABEL = "EndpointRoot"
    VALUE_NODE_LABEL = "EndpointValue"
    STUDY_SELECTION_REL_LABEL = "HAS_SELECTED_ENDPOINT"
    STUDY_VALUE_REL_LABEL = "HAS_STUDY_ENDPOINT"


class EndpointRoot(SyntaxIndexingInstanceRoot):
    TEMPLATE_REL_LABEL = "HAS_ENDPOINT"

    has_template = RelationshipFrom(
        EndpointTemplateRoot, TEMPLATE_REL_LABEL, model=ClinicalMdrRel
    )


class ObjectiveValue(SyntaxIndexingInstanceValue):
    ROOT_NODE_LABEL = "ObjectiveRoot"
    VALUE_NODE_LABEL = "ObjectiveValue"
    STUDY_SELECTION_REL_LABEL = "HAS_SELECTED_OBJECTIVE"
    STUDY_VALUE_REL_LABEL = "HAS_STUDY_OBJECTIVE"


class ObjectiveRoot(SyntaxIndexingInstanceRoot):
    TEMPLATE_REL_LABEL = "HAS_OBJECTIVE"

    has_template = RelationshipFrom(
        ObjectiveTemplateRoot, TEMPLATE_REL_LABEL, model=ClinicalMdrRel
    )


class ActivityInstructionValue(SyntaxInstanceValue):
    ROOT_NODE_LABEL = "ActivityInstructionRoot"
    VALUE_NODE_LABEL = "ActivityInstructionValue"
    STUDY_SELECTION_REL_LABEL = "HAS_SELECTED_ACTIVITY_INSTRUCTION"
    STUDY_VALUE_REL_LABEL = "HAS_STUDY_ACTIVITY_INSTRUCTION"

    activity_instruction_root = RelationshipFrom(
        "ActivityInstructionRoot", "LATEST", model=ClinicalMdrRel
    )


class ActivityInstructionRoot(SyntaxInstanceRoot):
    TEMPLATE_REL_LABEL = "HAS_ACTIVITY_INSTRUCTION"

    has_template = RelationshipFrom(
        ActivityInstructionTemplateRoot, TEMPLATE_REL_LABEL, model=ClinicalMdrRel
    )


class TimeframeValue(SyntaxInstanceValue):
    STUDY_SELECTION_REL_LABEL = "HAS_SELECTED_TIMEFRAME"
    STUDY_VALUE_REL_LABEL = "HAS_SELECTED_TIMEFRAME"

    # Timeframes are not directly used by Study, they are used indirectly by StudyEndpoints that are linked to Study
    # This is why we need to modify the default get study count function
    def get_study_count(self) -> int:
        cypher_query = f"""
        MATCH (n)<-[:{self.STUDY_SELECTION_REL_LABEL}]-(:StudyEndpoint)<-[:{EndpointValue.STUDY_VALUE_REL_LABEL}]-(:StudyValue)<--(sr:StudyRoot)
        WHERE id(n)={self.id}
        RETURN count(DISTINCT sr)
        """

        count, _ = db.cypher_query(cypher_query)
        return count[0][0]


class TimeframeRoot(SyntaxInstanceRoot):
    TEMPLATE_REL_LABEL = "HAS_TIMEFRAME"

    has_template = RelationshipFrom(
        TimeframeTemplateRoot, TEMPLATE_REL_LABEL, model=ClinicalMdrRel
    )
