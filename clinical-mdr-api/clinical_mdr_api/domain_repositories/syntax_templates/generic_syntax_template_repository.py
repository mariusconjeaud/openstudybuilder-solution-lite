import abc
from typing import Dict, List, Optional, Sequence, TypeVar

from neomodel import db

from clinical_mdr_api.config import (
    STUDY_DAY_NAME,
    STUDY_DURATION_DAYS_NAME,
    STUDY_DURATION_WEEKS_NAME,
    STUDY_ENDPOINT_TP_NAME,
    STUDY_TIMEPOINT_NAME,
    STUDY_VISIT_NAME,
    STUDY_VISIT_TIMEREF_NAME,
    STUDY_VISIT_TYPE_NAME,
    STUDY_WEEK_NAME,
)
from clinical_mdr_api.domain_repositories.generic_repository import EntityNotFoundError
from clinical_mdr_api.domain_repositories.generic_syntax_repository import (
    GenericSyntaxRepository,
)
from clinical_mdr_api.domain_repositories.models.generic import Conjunction, VersionRoot
from clinical_mdr_api.domain_repositories.models.syntax import SyntaxTemplateValue
from clinical_mdr_api.domain_repositories.models.template_parameter import (
    TemplateParameter,
)
from clinical_mdr_api.domains._utils import strip_html
from clinical_mdr_api.domains.libraries.parameter_term import (
    ComplexParameterTerm,
    ParameterTermEntryVO,
)
from clinical_mdr_api.domains.syntax_templates.template import TemplateVO

_AggregateRootType = TypeVar("_AggregateRootType")


class GenericSyntaxTemplateRepository(
    GenericSyntaxRepository[_AggregateRootType], abc.ABC
):
    def _get_template(self, value: SyntaxTemplateValue) -> TemplateVO:
        return TemplateVO(
            name=value.name,
            name_plain=value.name_plain,
            guidance_text=value.guidance_text,
        )

    def _get_or_create_value(
        self, root: VersionRoot, ar: _AggregateRootType
    ) -> SyntaxTemplateValue:
        for itm in root.has_version.filter(
            name=ar.name, guidance_text=ar.guidance_text
        ):
            return itm

        latest_draft = root.latest_draft.get_or_none()
        if latest_draft and not self._has_data_changed(ar, latest_draft):
            return latest_draft
        latest_final = root.latest_final.get_or_none()
        if latest_final and not self._has_data_changed(ar, latest_final):
            return latest_final
        latest_retired = root.latest_retired.get_or_none()
        if latest_retired and not self._has_data_changed(ar, latest_retired):
            return latest_retired

        new_value = self.value_class(
            name=ar.name, guidance_text=ar.guidance_text, name_plain=strip_html(ar.name)
        )
        self._db_save_node(new_value)
        return new_value

    def _has_data_changed(
        self, ar: _AggregateRootType, value: SyntaxTemplateValue
    ) -> bool:
        base_comparison = (
            ar.name != value.name or ar.guidance_text != value.guidance_text
        )
        return base_comparison

    def patch_default_parameter_terms(
        self,
        versioned_object: _AggregateRootType,
        parameters: Sequence[ParameterTermEntryVO],
        set_number: Optional[int] = None,
    ):
        (
            _,
            template_value,
            _,
            _,
        ) = versioned_object.repository_closure_data

        # If set_number isn't provided, auto determine the set number
        if set_number is None:
            cypher_query = f"""MATCH (t)-[rel:{template_value.PARAMETERS_LABEL}]->()
            WHERE id(t)=$id
            RETURN coalesce(max(rel.set_number), 0) AS max_set_number
            """
            result, _ = db.cypher_query(cypher_query, {"id": template_value.id})
            set_number = result[0][0] + 1
        else:
            # If the template already has a default term set with this number, first disconnect the parameters
            term_set = template_value.has_parameters.match(set_number=set_number).all()
            for param in term_set:
                self._db_remove_relationship(template_value.has_parameters, param)
        # Then, create the set of parameters
        self._create_default_parameter_term_set(
            value=template_value, parameters=parameters, set_number=set_number
        )

    def _maintain_parameters(
        self,
        versioned_object: _AggregateRootType,
        root: VersionRoot,
        value: SyntaxTemplateValue,
    ) -> None:
        root.has_parameters.disconnect_all()
        for index, parameter_name in enumerate(
            versioned_object.template_value.parameter_names
        ):
            parameter = TemplateParameter.nodes.get_or_none(name=parameter_name)
            if parameter is not None:
                # root.has_parameters.connect(parameter, {"position": index + 1})
                cypher_query = f"""
                    MATCH (tr:{self.root_class.__label__}) WHERE ID(tr)=$id
                    WITH tr
                    MATCH (tp:TemplateParameter {{name: $parameter_name}})
                    WITH tr, tp
                    CREATE (tr)-[uses_parameter:{self.root_class.PARAMETERS_LABEL}]->(tp)
                    SET uses_parameter.position=$position
                    """
                db.cypher_query(
                    cypher_query,
                    {
                        "id": root.id,
                        "parameter_name": parameter_name,
                        "position": index + 1,
                    },
                )
            else:
                raise EntityNotFoundError(
                    f"Cannot find parameter named {parameter_name}"
                )

        if (
            hasattr(versioned_object.template_value, "default_parameter_terms")
            and versioned_object.template_value.default_parameter_terms is not None
        ):
            # Then, create the relationships to the TemplateParameterTermValue nodes, as default values
            value.has_parameters.disconnect_all()
            value.has_conjunction.disconnect_all()

            self._create_default_parameter_term_set(
                value=value,
                parameters=versioned_object.template_value.default_parameter_terms,
            )

    def _create_default_parameter_term_set(
        self,
        value: SyntaxTemplateValue,
        parameters: Sequence[ParameterTermEntryVO],
        set_number: Optional[int] = 0,
    ) -> None:
        for position, parameter_config in enumerate(parameters):
            if isinstance(parameter_config, ComplexParameterTerm):
                root_id = self._maintain_complex_parameter(parameter_config)
                cypher_query = f"""
                    MATCH (tv:SyntaxTemplateValue), (pt:TemplateParameterTermRoot)
                    WHERE ID(tv) = $value_id AND ID(pt) = $root_id
                    CREATE (tv)-[r:{value.PARAMETERS_LABEL} {{set_number: $set_number, position: $position, index: $index}}]->(pt)
                    """
                db.cypher_query(
                    cypher_query,
                    {
                        "root_id": root_id,
                        "set_number": set_number,
                        "position": position,
                        "index": 1,
                        "value_id": value.id,
                    },
                )
            else:
                conjunction_string: str = parameter_config.conjunction
                if len(conjunction_string) != 0:
                    result = Conjunction.nodes.get_or_none(string=conjunction_string)
                    if result is None:
                        conjunction = Conjunction(string=conjunction_string)
                        conjunction.save()
                    else:
                        conjunction = result
                    value.has_conjunction.connect(
                        conjunction,
                        {"set_number": set_number, "position": position + 1},
                    )
                for index, value_config in enumerate(parameter_config.parameters):
                    self._add_value_parameter_relation(
                        value=value,
                        parameter_uid=value_config.uid,
                        set_number=set_number,
                        position=position + 1,
                        index=index + 1,
                    )

    def _add_value_parameter_relation(
        self,
        value: SyntaxTemplateValue,
        parameter_uid: str,
        position: int,
        index: int,
        set_number: Optional[int],
    ):
        set_number_subclause = (
            "set_number: $set_number, " if set_number is not None else ""
        )
        cypher_query = f"""
            MATCH (tv:SyntaxTemplateValue), (pt:TemplateParameterTermRoot {{uid: $parameter_uid}})
            WHERE ID(tv) = $value_id
            CREATE (tv)-[r:{value.PARAMETERS_LABEL} {{{set_number_subclause}position: $position, index: $index}}]->(pt)
            """
        db.cypher_query(
            cypher_query,
            {
                "parameter_uid": parameter_uid,
                "set_number": set_number,
                "position": position,
                "index": index,
                "value_id": value.id,
            },
        )

    def get_parameters_including_terms(
        self,
        template_uid: str,
        study_uid: Optional[str] = None,
        include_study_endpoints: Optional[bool] = False,
    ):
        cypher_query = f"""
            MATCH (otr:{self.root_class.__label__} {{uid: $uid}})-[uses_parameter:{self.root_class.PARAMETERS_LABEL}]->(pt)
            WHERE NOT pt.name=$name
            OPTIONAL MATCH (pt)-[:HAS_DEFINITION]->(tpd:ParameterTemplateRoot)-
                [:LATEST_FINAL]->(tpv:ParameterTemplateValue)
            WITH uses_parameter, pt, tpd, tpv
            ORDER BY
                uses_parameter.position ASC
            CALL {{
                WITH pt
                OPTIONAL MATCH (pt)<-[:HAS_PARENT_PARAMETER*0..]-(pt_parents)-[:HAS_PARAMETER_TERM]->(pr)-[:LATEST_FINAL]->(pv)
                WITH  pr, pv,  pt_parents
                CALL apoc.case(
                 [
                   pv.name_sentence_case IS NOT NULL, 'RETURN pv.name_sentence_case AS name',
                   pv.name_sentence_case IS NULL, 'RETURN pv.name AS name'
                 ],
                 '',
                 {{ pv:pv }})
                 yield value
                WITH pr, pt_parents, value.name as value
                // If a TemplateParameterTermValue is NumericValue type we sort template parameter values
                // by value property not name property
                ORDER BY CASE WHEN "NumericValue" IN labels(pv) THEN pv.value ELSE value END ASC
                RETURN collect({{uid: pr.uid, name: value, type: pt_parents.name}}) AS terms
            }}
            RETURN
                pt.name AS name, tpd.uid as definition, tpv.template_string as template,
                terms
            """
        dataset, _ = db.cypher_query(
            cypher_query, {"uid": template_uid, "name": STUDY_ENDPOINT_TP_NAME}
        )
        data = [
            dict(name=item[0], definition=item[1], template=item[2], terms=item[3])
            for item in dataset
        ]

        if study_uid:
            data = self.subset_parameters_to_specific_study(
                data=data, study_uid=study_uid
            )

        # StudyEndpoint parameters need to be treated separately
        if include_study_endpoints is True:
            cypher_query = f"""
                MATCH (:{self.root_class.__label__} {{uid: $uid}})-[uses_parameter:{self.root_class.PARAMETERS_LABEL}]->(pt)
                WHERE pt.name=$pt_name
                WITH uses_parameter, pt
                ORDER BY
                    uses_parameter.position ASC
                CALL {{
                    WITH pt
                    MATCH (pt)-[:HAS_PARAMETER_TERM]->(pr)<-[:HAS_STUDY_ENDPOINT]-(:StudyValue)<-[:LATEST]-(sr:StudyRoot)
                    WHERE sr.uid=$study_uid
                    MATCH (pr)-[:HAS_SELECTED_ENDPOINT]->(ev:EndpointValue)
                    OPTIONAL MATCH (pr)-[:HAS_SELECTED_TIMEFRAME]->(tv)
                    CALL
                    {{
                        WITH pr
                        OPTIONAL MATCH (pr)-[rel:HAS_UNIT]->(un:UnitDefinitionRoot)-[:LATEST_FINAL]->(udv:UnitDefinitionValue)
                        WITH rel, udv, pr ORDER BY rel.index
                        WITH collect(udv.name_sentence_case) as unit_names, pr
                        OPTIONAL MATCH (pr)-[:HAS_CONJUNCTION]->(co:Conjunction) 
                        WITH unit_names, co
                        RETURN apoc.text.join(unit_names, " " + coalesce(co.string, "") + " ") AS unit
                    }}
                    WITH pr.uid AS puid, ev.name + coalesce(" " + unit, "") + coalesce(" " + tv.name, "") AS pname
                    ORDER BY pname ASC
                    RETURN collect({{uid: puid, name: pname, type: $pt_name}}) AS terms
                }}

                RETURN
                    pt.name AS name, null as definition, null as template,
                    terms
                """
            dataset, _ = db.cypher_query(
                cypher_query,
                {
                    "uid": template_uid,
                    "study_uid": study_uid,
                    "pt_name": STUDY_ENDPOINT_TP_NAME,
                },
            )
            data += [
                dict(name=item[0], definition=item[1], template=item[2], terms=item[3])
                for item in dataset
            ]

        return data

    def get_default_parameter_terms(
        self, template_uid: str
    ) -> Dict[int, Sequence[ParameterTermEntryVO]]:
        cypher_query = f"""
        MATCH  (param:TemplateParameter)<-[u:USES_PARAMETER]-
          (tr:{self.root_class.__label__})-[:LATEST]->(tv)
        WHERE tr.uid=$root_uid
        WITH tv, param.name as parameter, u.position as position
        OPTIONAL MATCH (tv:SyntaxTemplateValue)-[rel:USES_DEFAULT_VALUE]->(tptr:TemplateParameterTermRoot)
        WITH tv,
            head([(tptr)-[:LATEST_FINAL]->(tpv) | tpv]) as tpv,
            head([(tptr)<-[:HAS_PARAMETER_TERM]-(tp) | tp]) as tp,
            rel as rel,
            position,
            parameter,
            tptr as tptr
        OPTIONAL MATCH (tpvv: ParameterTemplateValue)<-[:LATEST_FINAL]-(td: ParameterTemplateRoot)-[:HAS_COMPLEX_VALUE]->(tptr)
        WHERE tpv iS NOT NULL AND tp is NOT NULL
        
        WITH DISTINCT coalesce(rel.set_number, 0) AS set_number, tv, position, parameter, collect(DISTINCT {{set_number: coalesce(rel.set_number, 0), position: rel.position, index: rel.index, parameter_name: tp.name, parameter_term: tpv.name, parameter_uid: tptr.uid,  definition: td.uid, template: tpvv.template_string }}) as data
        OPTIONAL MATCH (tv)-[con_rel:HAS_CONJUNCTION]->(con:Conjunction)
        WHERE con_rel.position=position AND con_rel.set_number=set_number
        WITH position, parameter, data, coalesce(con.string, "") AS conjunction
        RETURN DISTINCT position, parameter, [row in data where row.position = position | row] as parameterterms, conjunction
        """

        results, _ = db.cypher_query(cypher_query, params={"root_uid": template_uid})

        default_parameter_terms = self._parse_parameter_terms(
            instance_parameters=results
        )
        return default_parameter_terms

    def simple_concept_template(self, rel_type: str):
        query_to_subset = f"""
            MATCH (:StudyRoot {{uid:$uid}})-[:LATEST]->(:StudyValue)
            -[:HAS_STUDY_VISIT]->(:StudyVisit)-[:{rel_type}]->(:SimpleConceptRoot)
            -[:LATEST_FINAL]->(simple_concept_value:SimpleConceptValue)
            return simple_concept_value.name
            """
        return query_to_subset

    def ct_term_template(self, rel_type: str):
        query_to_subset = f"""
        MATCH (:StudyRoot {{uid:$uid}})-[:LATEST]->(:StudyValue)
        -[:HAS_STUDY_VISIT]->(:StudyVisit)-[:{rel_type}]->(:CTTermRoot)
        -[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST_FINAL]->(term_name_value:CTTermNameValue)
        return term_name_value.name
        """
        return query_to_subset

    def subset_time_point_reference(self):
        query_to_subset = """
            MATCH (:StudyRoot {uid:$uid})-[:LATEST]->(:StudyValue)
            -[:HAS_STUDY_VISIT]->(:StudyVisit)-[:HAS_TIMEPOINT]->(:SimpleConceptRoot)
            -[:LATEST_FINAL]->(simple_concept_value:SimpleConceptValue)-[:HAS_TIME_REFERENCE]->(:CTTermRoot)
            -[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST_FINAL]->(term_name_value:CTTermNameValue)
            return term_name_value.name
            """
        return query_to_subset

    def subset_parameters_to_specific_study(self, data: List, study_uid: str):
        for parameter in data:
            query_to_subset = None
            param_name = parameter["name"]
            if parameter["name"] == STUDY_VISIT_TYPE_NAME:
                query_to_subset = self.ct_term_template(rel_type="HAS_VISIT_TYPE")
            elif parameter["name"] == STUDY_VISIT_TIMEREF_NAME:
                query_to_subset = self.subset_time_point_reference()
            elif parameter["name"] == STUDY_VISIT_NAME:
                query_to_subset = self.simple_concept_template(
                    rel_type="HAS_VISIT_NAME"
                )
            elif parameter["name"] == STUDY_DAY_NAME:
                query_to_subset = self.simple_concept_template(rel_type="HAS_STUDY_DAY")
            elif parameter["name"] == STUDY_DURATION_DAYS_NAME:
                query_to_subset = self.simple_concept_template(
                    rel_type="HAS_STUDY_DURATION_DAYS"
                )
            elif parameter["name"] == STUDY_WEEK_NAME:
                query_to_subset = self.simple_concept_template(
                    rel_type="HAS_STUDY_WEEK"
                )
            elif parameter["name"] == STUDY_DURATION_WEEKS_NAME:
                query_to_subset = self.simple_concept_template(
                    rel_type="HAS_STUDY_DURATION_WEEKS"
                )
            elif parameter["name"] == STUDY_TIMEPOINT_NAME:
                query_to_subset = self.simple_concept_template(rel_type="HAS_TIMEPOINT")
            if query_to_subset:
                template_parameters_subset, _ = db.cypher_query(
                    query_to_subset, {"uid": study_uid}
                )
                flat_template_parameters = self.flatten_neomodel_output(
                    output=template_parameters_subset
                )
                self.subset_value_list_for_given_tp(
                    data=data,
                    param_name=param_name,
                    subset_list=flat_template_parameters,
                )
        return data

    def flatten_neomodel_output(self, output: List):
        flatted_output = []
        if len(output) > 0:
            for value in output:
                flatted_output.append(value[0].lower())
        return flatted_output

    def subset_value_list_for_given_tp(
        self, data: List, param_name: str, subset_list: List
    ):
        for template_param_value in data:
            if template_param_value["name"] == param_name:
                template_param_value["terms"] = [
                    item
                    for item in template_param_value["terms"]
                    if item["name"].lower() in subset_list
                ]

    @abc.abstractmethod
    def check_exists_by_name_in_study(self, name: str, study_uid: str) -> bool:
        raise NotImplementedError()

    def check_usage_count(self, uid: str) -> int:
        itm: VersionRoot = self.root_class.nodes.get(uid=uid)
        return len(itm.has_template.all())

    def check_exists_by_name_in_library(self, name: str, library: str) -> bool:
        query = f"""
            MATCH (:Library {{name: $library}})-[:{self.root_class.LIBRARY_REL_LABEL}]->(tr:{self.root_class.__label__})-[:LATEST_FINAL|LATEST_DRAFT|LATEST_RETIRED|LATEST]->(:{self.value_class.__label__} {{name: $name}})
            RETURN tr
            """
        result, _ = db.cypher_query(query, {"name": name, "library": library})
        return len(result) > 0 and len(result[0]) > 0
