from neomodel import (
    BooleanProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    db,
)

from clinical_mdr_api.domain_repositories.models.generic import (
    ClinicalMdrNode,
    TemplateUsesParameterRelation,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)


class TemplateParameter(ClinicalMdrNode):
    RELATION_LABEL = "HAS_PARAMETER_TERM"
    has_parameter_term = RelationshipTo("TemplateParameterTermRoot", RELATION_LABEL)

    name = StringProperty()


class TemplateParameterTermValue(VersionValue):
    name = StringProperty()
    is_active_template_parameter = BooleanProperty()


class TemplateParameterTermRoot(VersionRoot):
    RELATION_LABEL = "HAS_PARAMETER_TERM"
    PARAMETERS_LABEL = "USES_DEFAULT_VALUE"

    uid = StringProperty()

    has_parameter_term = RelationshipFrom(TemplateParameter, RELATION_LABEL)

    has_version = RelationshipTo(
        TemplateParameterTermValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(TemplateParameterTermValue, "LATEST")
    latest_draft = RelationshipTo(TemplateParameterTermValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(TemplateParameterTermValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(TemplateParameterTermValue, "LATEST_RETIRED")

    @classmethod
    def check_parameter_term_exists(
        cls, parameter_name: str, parameter_term_uid: str
    ) -> bool:
        cypher_query = """
            MATCH (pt:TemplateParameter {name: $name})<-[:HAS_PARENT_PARAMETER*0..]-(pt_parents)-[:HAS_PARAMETER_TERM]->(pr {uid: $uid})
            RETURN
                pt.name AS name, pt_parents.name AS type, pr.uid AS uid
            """
        dataset, _ = db.cypher_query(
            cypher_query, {"uid": parameter_term_uid, "name": parameter_name}
        )
        if len(dataset) == 0:
            return False
        return True


class ParameterTemplateValue(TemplateParameterTermValue):
    template_string = StringProperty()

    def get_all(self):
        cypher_query = """
            MATCH (otv:ParameterTemplateValue)<-[:LATEST_FINAL]-(ot:ParameterTemplateRoot)<-[rel:TPCV_USES_TPV]-(pt)
            where ID(pt) = $id
            RETURN
                pt.name AS name, ot.uid AS uid, rel.position as position, otv.value as value, otv.name as param_value

            """
        dataset, _ = db.cypher_query(cypher_query, {"id": self.id})
        return dataset


class ParameterTemplateRoot(TemplateParameterTermRoot):
    has_version = RelationshipTo(
        ParameterTemplateValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(ParameterTemplateValue, "LATEST")
    latest_draft = RelationshipTo(ParameterTemplateValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(ParameterTemplateValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(ParameterTemplateValue, "LATEST_RETIRED")

    has_parameter_term = RelationshipFrom(TemplateParameter, "HAS_PARAMETER_TERM")
    has_definition = RelationshipFrom(TemplateParameter, "HAS_DEFINITION")


class TemplateParameterComplexValue(TemplateParameterTermValue):
    uses_parameter = RelationshipTo(
        TemplateParameterTermRoot, "TPCV_USES_TPV", model=TemplateUsesParameterRelation
    )

    def get_all(self):
        cypher_query = """
            MATCH (otv:TemplateParameterTermValue)<-[:LATEST_FINAL]-(ot:TemplateParameterTermRoot)<-[rel:TPCV_USES_TPV]-(pt)
            where ID(pt) = $id
            RETURN
                pt.name AS name, ot.uid AS uid, rel.position as position, otv.value as value, otv.name as param_value
                         
            """
        dataset, _ = db.cypher_query(cypher_query, {"id": self.id})
        return dataset


class TemplateParameterComplexRoot(TemplateParameterTermRoot):
    has_version = RelationshipTo(
        TemplateParameterComplexValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(TemplateParameterComplexValue, "LATEST")
    latest_draft = RelationshipTo(TemplateParameterComplexValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(TemplateParameterComplexValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(TemplateParameterComplexValue, "LATEST_RETIRED")

    has_complex_value = RelationshipFrom(ParameterTemplateRoot, "HAS_COMPLEX_VALUE")
