import datetime
import math
import re
from collections import defaultdict
from typing import Sequence

import neo4j
from neomodel import AliasProperty, match, match_q, properties, relationship_manager
from neomodel.core import db
from opencensus.trace import execution_context

LATEST_VERSION_ORDER_BY = """
    toInteger(split({rel}.version, '.')[0]) ASC,
    toInteger(split({rel}.version, '.')[1]) ASC,
    {rel}.end_date ASC,
    {rel}.start_date ASC
    """


def convert_to_tz_aware_datetime(value: datetime.datetime):
    # Function created to properly adjust timezone part in Python datetime
    return value.astimezone(tz=datetime.timezone.utc)


def convert_to_datetime(value: neo4j.time.DateTime):
    # Function created to properly represent the DateTime from database as Python datetime
    # Workaround for improper default rounding in to_native method
    dt: datetime.datetime = value.to_native()
    if hasattr(dt, "second"):
        subseconds, _ = math.modf(value.second)
        # Subseconds are between 0.0 and 0.999 999 999
        # thats why to get microseconds it is needed to multiply by 1000000
        microseconds: int = round(subseconds * 1000000)
        return dt.replace(microsecond=microseconds).replace(tzinfo=dt.tzinfo)
    return dt


def format_generic_header_values(values: Sequence):
    if len(values) > 0 and isinstance(values[0], neo4j.time.DateTime):
        return [convert_to_datetime(_val) for _val in values]
    return values


def process_filter_args(cls, kwargs):
    """
    loop through properties in filter parameters check they match class definition
    deflate them and convert into something easy to generate cypher from
    """

    output = {}

    for key, value in kwargs.items():
        current_class = cls
        current_rel_model = None
        leaf_prop = None
        operator = "="
        is_rel_property = "|" in key
        prop = key
        for part in re.split(r"__|\|", key):
            defined_props = current_class.defined_properties(rels=True)
            # update defined props dictionary with relationship properties if
            # we are filtering by property
            if is_rel_property and current_rel_model:
                defined_props.update(current_rel_model.defined_properties(rels=True))
            if part in defined_props:
                if isinstance(
                    defined_props[part], relationship_manager.RelationshipDefinition
                ):
                    defined_props[part]._lookup_node_class()
                    current_class = defined_props[part].definition["node_class"]
                    current_rel_model = defined_props[part].definition["model"]
            elif part in match.OPERATOR_TABLE:
                operator = match.OPERATOR_TABLE[part]
                prop, _ = prop.rsplit("__", 1)
                continue
            else:
                raise ValueError(f"No such property {part} on {cls.__name__}")
            leaf_prop = part
        if is_rel_property and current_rel_model:
            property_obj = getattr(current_rel_model, leaf_prop)
        else:
            property_obj = getattr(current_class, leaf_prop)

        if isinstance(property_obj, properties.AliasProperty):
            prop = property_obj.aliased_to()
            deflated_value = getattr(cls, prop).deflate(value)
        else:
            # handle special operators
            if operator == match._SPECIAL_OPERATOR_IN:
                if not isinstance(value, tuple) and not isinstance(value, list):
                    raise ValueError(
                        f"Value must be a tuple or list for IN operation {key}={value}"
                    )
                deflated_value = [property_obj.deflate(v) for v in value]
            elif operator == match._SPECIAL_OPERATOR_ISNULL:
                if not isinstance(value, bool):
                    raise ValueError(
                        f"Value must be a bool for isnull operation on {key}"
                    )
                operator = "IS NULL" if value else "IS NOT NULL"
                deflated_value = None
            elif operator in match._REGEX_OPERATOR_TABLE.values():
                deflated_value = property_obj.deflate(value)
                if not isinstance(deflated_value, str):
                    raise ValueError(f"Must be a string value for {key}")
                if operator in match._STRING_REGEX_OPERATOR_TABLE.values():
                    deflated_value = re.escape(deflated_value)
                deflated_value = operator.format(deflated_value)
                operator = match._SPECIAL_OPERATOR_REGEX
            else:
                deflated_value = property_obj.deflate(value)

        # FIXME
        # map property to correct property name in the database
        # db_property = cls.defined_properties(rels=False)[prop].db_property or prop
        db_property = prop

        output[db_property] = (operator, deflated_value)
    return output


# pylint: disable=unused-argument
def _rel_helper(
    lhs,
    rhs,
    ident=None,
    relation_type=None,
    direction=None,
    relation_properties=None,
    **kwargs,
):
    """
    Generate a relationship matching string, with specified parameters.
    Examples:
    relation_direction = OUTGOING: (lhs)-[relation_ident:relation_type]->(rhs)
    relation_direction = INCOMING: (lhs)<-[relation_ident:relation_type]-(rhs)
    relation_direction = EITHER: (lhs)-[relation_ident:relation_type]-(rhs)
    :param lhs: The left hand statement.
    :type lhs: str
    :param rhs: The right hand statement.
    :type rhs: str
    :param ident: A specific identity to name the relationship, or None.
    :type ident: str
    :param relation_type: None for all direct rels, * for all of any length, or a name of an explicit rel.
    :type relation_type: str
    :param direction: None or EITHER for all OUTGOING,INCOMING,EITHER. Otherwise OUTGOING or INCOMING.
    :param relation_properties: dictionary of relationship properties to match
    :returns: string
    """

    if direction == match.OUTGOING:
        stmt = "-{0}->"
    elif direction == match.INCOMING:
        stmt = "<-{0}-"
    else:
        stmt = "-{0}-"

    rel_props = ""

    if relation_properties:
        key_val_pairs = ", ".join(
            [f"{key}: {value}" for key, value in relation_properties.items()]
        )
        rel_props = f"{{{key_val_pairs}}}"

    # direct, relation_type=None is unspecified, relation_type
    if relation_type is None:
        stmt = stmt.format("")
    # all("*" wildcard) relation_type
    elif relation_type == "*":
        stmt = stmt.format("[*]")
    else:
        # explicit relation_type
        stmt = stmt.format(f"[{ident if ident else ''}:`{relation_type}`{rel_props}]")

    # Make sure not to add parenthesis when they are already present
    # (was not part of the original function)
    if lhs[-1] != ")":
        lhs = f"({lhs})"
    if rhs[-1] != ")":
        rhs = f"({rhs})"
    return f"{lhs}{stmt}{rhs}"


class CustomQueryBuilder(match.QueryBuilder):
    def __init__(self, node_set):
        super().__init__(node_set=node_set)
        self._ast["optional match"] = []
        self._ast["relation_selectors"] = {}
        self.node_counter = defaultdict(int)

    def build_ast(self):
        # This is where we deal with required additional relations to
        # fetch, it is not part of the original method.
        self._ast["relation_tree_map"] = {}
        for rel_name in self.node_set._relations_to_fetch:
            self.build_traversal_from_path(rel_name, self.node_set.source)
        for rel_name in self.node_set._optional_relations_to_fetch:
            self.build_traversal_from_path(
                rel_name, self.node_set.source, optional_traversal=True
            )
        for rel_name in self.node_set._optional_relations_to_fetch_and_collect:
            self.build_traversal_from_path(
                rel_name,
                self.node_set.source,
                include_nodes_in_return=False,
                optional_traversal=True,
                collect_variables=True,
            )
        for relation, data in self.node_set._optional_relation_to_fetch_single.items():
            new_name, sort_clause = data
            (
                root_alias,
                target_label,
                reltype,
                direction,
            ) = self.build_relationship_to_select(
                relation, self.node_set.source, data[0]
            )
            self._add_to_select(
                root_alias, new_name, sort_clause, target_label, reltype, direction
            )
        self.build_source(self.node_set)
        self.build_distinct_clause()

        if hasattr(self.node_set, "skip"):
            self._ast["skip"] = self.node_set.skip
        if hasattr(self.node_set, "limit"):
            self._ast["limit"] = self.node_set.limit

        return self

    def build_distinct_clause(self):
        for rel_name in self.node_set._values_to_collect:
            if "__" in rel_name:
                path, prop = rel_name.rsplit("__", 1)
                variable = self.build_traversal_from_path(
                    path,
                    self.node_set.source,
                    optional_traversal=True,
                    include_nodes_in_return=False,
                )
            else:
                variable = self.node_set.source.__label__.lower()
                prop = rel_name
            # clear the return section that is autogenerated by
            if "return" in self._ast:
                del self._ast["return"]
            self._add_to_distinct_set(f" DISTINCT {variable}.{prop} AS {variable}")
            self._add_to_return_set(variable)

    def _add_to_return_set(self, name):
        if "return_set" not in self._ast:
            self._ast["return_set"] = []
        if name not in self._ast["return_set"] and name != self._ast.get("return"):
            self._ast["return_set"].append(name)

    def _add_to_collect_set(self, name):
        if "collect" not in self._ast:
            self._ast["collect"] = []
        if name not in self._ast["collect"] and name != self._ast.get("collect"):
            self._ast["collect"].append(name)

    def _add_to_distinct_set(self, name):
        if "distinct" not in self._ast:
            self._ast["distinct"] = []
        if name not in self._ast["distinct"] and name != self._ast.get("distinct"):
            self._ast["distinct"].append(name)

    def _add_to_select(
        self, root_alias, variable_name, sort_clause, target_label, rel_type, direction
    ):
        data = {
            "root_alias": root_alias,
            "sort_clause": sort_clause,
            "target_label": target_label,
            "type": rel_type,
            "direction": direction,
        }
        self._add_to_return_set(variable_name)
        self._ast["relation_selectors"][variable_name] = data

    def build_relationship_to_select(
        self,
        relationship: str,
        source_class,
        new_variable_name,
    ):
        rel = getattr(source_class, relationship)
        lhs_name = source_class.__label__.lower()
        relation_tree_map = self._ast["relation_tree_map"]
        if new_variable_name not in relation_tree_map:
            relation_tree_map[new_variable_name] = {
                "target": rel.definition["node_class"],
                "children": {},
                "variable_name": new_variable_name,
                "rel_variable_name": new_variable_name,
            }
        direction = (rel.definition["direction"],)
        relation_type = (rel.definition["relation_type"],)
        return (
            lhs_name,
            rel.definition["node_class"].__label__,
            relation_type,
            direction,
        )

    def build_traversal_from_path(
        self,
        path: str,
        source_class,
        include_nodes_in_return=True,
        include_rel_in_return=False,
        optional_traversal=False,
        is_rel_filtering=False,
        collect_variables=False,
    ):
        src_class = source_class
        stmt = ""
        relation_tree_map = self._ast["relation_tree_map"]
        splitted_path = re.split(r"__|\|", path)
        for part in splitted_path:
            relationship = getattr(src_class, part)
            # build source
            if "node_class" not in relationship.definition:
                relationship._lookup_node_class()
            rhs_label = relationship.definition["node_class"].__label__
            rel_reference = f"{relationship.definition['node_class']}_{part}"
            self.node_counter[rel_reference] += 1
            rhs_name = f"{rhs_label.lower()}_{part}_{self.node_counter[rel_reference]}"
            rhs_ident = f"{rhs_name}:{rhs_label}"

            if collect_variables:
                self._add_to_collect_set(rhs_name)
            elif include_nodes_in_return:
                self._add_to_return_set(rhs_name)
            if not stmt:
                lhs_label = src_class.__label__
                lhs_name = lhs_label.lower()
                lhs_ident = f"{lhs_name}:{lhs_label}"
                if include_nodes_in_return:
                    self._add_to_return_set(lhs_name)
                # FIXME: find something cleaner
                # We remove the item generated by build_label() to avoid a useless MATCH statement
                if f"({lhs_ident})" in self._ast["match"]:
                    self._ast["match"].remove(f"({lhs_ident})")
            else:
                lhs_ident = stmt

            rel_ident = self.create_ident()
            if is_rel_filtering:
                rhs_name = rel_ident

            if part not in relation_tree_map:
                relation_tree_map[part] = {
                    "target": relationship.definition["node_class"],
                    "children": {},
                    "variable_name": rhs_name,
                    "rel_variable_name": rel_ident,
                }

            # FIXME: is it useful?
            # self._ast['result_class'] = relationship.definition['node_class']

            # add relationship variable to the return set
            if include_rel_in_return:
                self._add_to_return_set(rel_ident)
            stmt = _rel_helper(
                lhs=lhs_ident,
                rhs=rhs_ident,
                ident=rel_ident,
                direction=relationship.definition["direction"],
                relation_type=relationship.definition["relation_type"],
            )
            src_class = relationship.definition["node_class"]
            relation_tree_map = relation_tree_map[part]["children"]
        if not optional_traversal:
            self._ast["match"].append(stmt)
        else:
            self._ast["optional match"].append(stmt)
        return rhs_name

    def build_query(self):
        query = ""

        if "lookup" in self._ast:
            query += self._ast["lookup"]

        # Instead of using only one MATCH statement for every relation
        # to follow, we use one MATCH per relation (to avoid cartesian
        # product issues...). This part will need some refinement!
        if len(self._ast["match"]) > 0:
            query += " MATCH "
            query += " MATCH ".join(i for i in self._ast["match"])

        if len(self._ast["optional match"]) > 0:
            query += " OPTIONAL MATCH "
            query += " OPTIONAL MATCH ".join(i for i in self._ast["optional match"])

        query += " WITH * "

        if "where" in self._ast and self._ast["where"]:
            query += " WHERE "
            query += " AND ".join(self._ast["where"])

        if "with" in self._ast and self._ast["with"]:
            query += " WITH "
            query += self._ast["with"]
        if "distinct" in self._ast:
            if "with" in self._ast:
                query += ", "
            else:
                query += " WITH "
            query += ", ".join(self._ast["distinct"])

        for varname, data in self._ast["relation_selectors"].items():
            root_alias = data["root_alias"]
            target_label = data["target_label"]
            order_by = data["sort_clause"].format(rel="r")
            direction = data["direction"]
            reltypes = ":".join(data["type"])
            if direction == match.OUTGOING:
                rel_stmt = f"-[r:{reltypes}]->"
            elif direction == match.INCOMING:
                rel_stmt = f"<-[r:{reltypes}]-"
            else:
                rel_stmt = f"-[r:{reltypes}]-"
            proc = """
            CALL {{
                WITH {0}
                MATCH ({0}){1}(:{2})
                WITH r
                ORDER BY {3}
                WITH collect(r) as rs
                RETURN last(rs) as {4}
            }}
            """
            query += proc.format(root_alias, rel_stmt, target_label, order_by, varname)

        query += " RETURN DISTINCT "
        # FIXME: replace all by return_set
        if "return" in self._ast:
            query += self._ast["return"]
        if "return_set" in self._ast:
            if "return" in self._ast:
                query += ", "
            query += ", ".join(self._ast["return_set"])
        if "collect" in self._ast:
            if "return_set" in self._ast or "return" in self._ast:
                query += ", "
            query += ", ".join(f"collect({c}) as {c}" for c in self._ast["collect"])

        if "order_by" in self._ast and self._ast["order_by"]:
            query += " ORDER BY "
            query += ", ".join(self._ast["order_by"])

        if "skip" in self._ast:
            # This code comes from neomodel, we leave it as is
            # pylint: disable-next=consider-using-f-string
            query += " SKIP {0:d}".format(self._ast["skip"])

        if "limit" in self._ast:
            # This code comes from neomodel, we leave it as is
            # pylint: disable-next=consider-using-f-string
            query += " LIMIT {0:d}".format(self._ast["limit"])

        return query

    def build_label(self, ident, cls):
        """
        match nodes by a label
        """
        ident_w_label = ident + ":" + cls.__label__
        if "return_set" not in self._ast or ident not in self._ast["return_set"]:
            self._ast["match"].append(f"({ident_w_label})")
            self._ast["return"] = ident
            self._ast["result_class"] = cls
        return ident

    def _build_filter_statements(self, ident, filters, target, source_class):
        for prop, op_and_val in filters.items():
            if "__" in prop or "|" in prop:
                is_rel_filter = "|" in prop
                ident = self.lookup_query_variable(prop)
                if is_rel_filter:
                    path, prop = prop.rsplit("|", 1)
                else:
                    path, prop = prop.rsplit("__", 1)
                if not ident:
                    optional_traversal = False
                    if is_rel_filter:
                        optional_traversal = True
                    ident = self.build_traversal_from_path(
                        path,
                        source_class,
                        include_nodes_in_return=True,
                        optional_traversal=optional_traversal,
                        is_rel_filtering=is_rel_filter,
                    )
            op, val = op_and_val
            if op in match._UNARY_OPERATORS:
                # unary operators do not have a parameter
                statement = f"{ident}.{prop} {op}"
            else:
                place_holder = self._register_place_holder(ident + "_" + prop)
                statement = f"{ident}.{prop} {op} ${place_holder}"
                self._query_params[place_holder] = val
            target.append(statement)

    def _parse_q_filters(self, ident, q, source_class):
        target = []
        for child in q.children:
            if isinstance(child, match_q.QBase):
                q_childs = self._parse_q_filters(ident, child, source_class)
                if child.connector == match_q.Q.OR:
                    q_childs = "(" + q_childs + ")"
                target.append(q_childs)
            else:
                kwargs = {child[0]: child[1]}

                filters = process_filter_args(source_class, kwargs)
                self._build_filter_statements(ident, filters, target, source_class)
        ret = f" {q.connector} ".join(target)
        if q.negated:
            ret = f"NOT ({ret})"
        return ret

    def _execute(self, lazy=False, dict_output=False):
        """
        Override of the original method.
        Mostly a copy/paste except we change the results format.
        """
        if lazy:
            # inject id() into return or return_set
            if "return" in self._ast:
                self._ast["return"] = f"id({self._ast['return']})"
            else:
                self._ast["return_set"] = [
                    f"id({item})" for item in self._ast["return_set"]
                ]
        query = self.build_query()
        tracer = execution_context.get_opencensus_tracer()
        with tracer.span("neomodel.query") as span:
            span.add_attribute("cypher.query", query)
            span.add_attribute("cypher.params", self._query_params)

            results, prop_names = db.cypher_query(
                query, self._query_params, resolve_objects=True
            )

        if dict_output:
            result_dict = []
            for item in results:
                result_dict.append(dict(zip(prop_names, item)))
            return result_dict
        if results and len(results[0]) == 1:
            return [n[0] for n in results]
        return results

    def _count(self):
        if "return" in self._ast:
            self._ast["return"] = f"count({self._ast['return']})"
        else:
            # We have a set of items to return, we count only the first one.
            self._ast["return"] = f"count({self._ast['return_set'][0]})"
            self._ast.pop("return_set", None)
        # drop order_by, results in an invalid query
        self._ast.pop("order_by", None)
        query = self.build_query()
        results, _ = db.cypher_query(query, self._query_params)
        if len(results) > 0 and len(results[0]) > 0:
            return int(results[0][0])
        return 0

    def build_order_by(self, ident, source):
        if "?" in source._order_by:
            self._ast["with"] = f"{ident}, rand() as r"
            self._ast["order_by"] = "r"
        else:
            order_by = []
            for p in source._order_by:
                is_rel_property = "|" in p
                if "__" not in p and not is_rel_property:
                    order_by.append(f"{ident}.{p}")
                else:
                    prop = (
                        p.split("__")[-1] if not is_rel_property else p.split("|")[-1]
                    )
                    order_by_clause = self.lookup_query_variable(p)
                    order_by.append(f"{order_by_clause}.{prop}")
            self._ast["order_by"] = order_by

    def lookup_query_variable(self, prop):
        relation_tree_map = self._ast["relation_tree_map"]
        if not relation_tree_map:
            return None
        is_rel_property = "|" in prop
        traversals = re.split(r"__|\|", prop)
        if len(traversals) == 0:
            raise ValueError("Can only lookup traversal variables")
        if traversals[0] not in relation_tree_map:
            return None
        relation_tree_map = relation_tree_map[traversals[0]]
        variable_to_return = None
        last_property = traversals[-1]
        for part in traversals[1:]:
            if part in relation_tree_map["children"]:
                relation_tree_map = relation_tree_map["children"][part]
            elif part == last_property:
                # if last part of prop is the last traversal
                # we are safe to lookup the variable from the query
                if is_rel_property:
                    variable_to_return = f"{relation_tree_map['rel_variable_name']}"
                else:
                    variable_to_return = f"{relation_tree_map['variable_name']}"
            else:
                break
        return variable_to_return


class CustomNodeSet(match.NodeSet):
    query_cls = CustomQueryBuilder

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._relations_to_fetch = []
        self._optional_relations_to_fetch = []
        self._optional_relations_to_fetch_and_collect = []
        self._values_to_collect = []
        self._order_by = []
        self._optional_relation_to_fetch_single = {}

    def all(self, lazy=False, dict_output=False):
        """
        Return all nodes belonging to the set
        :param lazy: False by default, specify True to get nodes with id only without the parameters.
        :param dict_output: False by default, specify True to get nodes with the corresponding query variable names
        :return: list of nodes
        :rtype: list
        """
        return self.query_cls(self).build_ast()._execute(lazy, dict_output=dict_output)

    def fetch_relations(self, *relation_names):
        """Custom method to specify a set of extra relations to return."""
        self._relations_to_fetch = relation_names
        return self

    def fetch_optional_relations(self, *relation_names):
        """Custom method to specify a set of extra optional relations to return."""
        self._optional_relations_to_fetch = relation_names
        return self

    def fetch_optional_relations_and_collect(self, *relation_names):
        """Custom method to specify a set of extra optional relations to return in collection."""
        self._optional_relations_to_fetch_and_collect = relation_names
        return self

    def collect_values(self, *relations_names):
        """Custom method to specify a set of extra optional relations to return in collection.
        The collection will be the only variable returned"""
        self._values_to_collect = relations_names
        return self

    def fetch_optional_single_relation_of_type(self, relation_data):
        """Custom method to specify an optional relation to return.
        Use this to fetch a single relationship when several may exist for the type.
        The input parameter is a dict:
        {
            $relationship$: ($output_variable_name$, $sort_statement$),
        }
        The method will get all relationships of the given type, sort them according to the sort statement,
        and return the last one in the sorted result as output_variable_name.
        The sort statement is a string with a placeholder, {rel}, where the relationship alias will be inserted.
        For example, the statement "{rel}.amount" will get expanded to "SORT BY r5.amount",
        where the alias "r5" is autogenerated.
        Full example:
        {
            "knows": ("oldest_friendship", "{rel}.since DESC"),
            "hnows": ("newest_friendship", "{rel}.since ASC"),
        }
        Here nodes represent persons, that are connected by KNOWS relationships.
        The KNOWS relationship has a property "since".
        We select the oldest and newest friendships by sorting on "since" in descending and ascending order.
        """
        self._optional_relation_to_fetch_single.update(relation_data)
        return self

    def order_by(self, *props):
        """
        Order by properties. Prepend with minus to do descending. Pass None to
        remove ordering.
        """
        should_remove = len(props) == 1 and props[0] is None
        if not hasattr(self, "_order_by") or should_remove:
            self._order_by = []
            if should_remove:
                return self
        if "?" in props:
            self._order_by.append("?")
        else:
            for prop in props:
                prop = prop.strip()
                if prop.startswith("-"):
                    prop = prop[1:]
                    desc = True
                else:
                    desc = False

                if prop in self.source_class.defined_properties(rels=False):
                    property_obj = getattr(self.source_class, prop)
                    if isinstance(property_obj, AliasProperty):
                        prop = property_obj.aliased_to()

                self._order_by.append(prop + (" DESC" if desc else ""))
        return self


def _to_relation_tree(nodeset, root_node, other_nodes, relation_tree_map):
    """Recursive method to build root_node's relation tree from relation_tree_map."""
    root_node._relations = {}
    for name, relation_def in relation_tree_map.items():
        for var_name, node in other_nodes.items():
            if (
                var_name
                in [
                    relation_def["variable_name"],
                    relation_def["rel_variable_name"],
                ]
                and node is not None
            ):
                if isinstance(node, list):
                    root_node._relations[name] = []
                    for n in node:
                        root_node._relations[name].append(
                            _to_relation_tree(
                                nodeset, n, other_nodes, relation_def["children"]
                            )
                        )
                else:
                    root_node._relations[name] = _to_relation_tree(
                        nodeset, node, other_nodes, relation_def["children"]
                    )
    return root_node


def to_relation_trees(nodeset):
    """
    Convert every result contained in this node set to a relation tree.

    By default, we receive results from neomodel as a list of
    nodes without the hierarchy. This method tries to rebuild this
    hierarchy without overidding anything in the node, that's why
    we use a dedicated property to store node's relations.

    NOTE: there is still an issue with this method, it won't work
    properly if two nodes of the same type are returned because it
    will mix them. This is mostly because we don't have a simple
    way to identify which node corresponds to which relation...

    """
    results = []
    qbuilder = nodeset.query_cls(nodeset).build_ast()
    all_nodes = qbuilder._execute(dict_output=True)
    other_nodes = {}
    root_node = None
    relation_tree_map = qbuilder._ast["relation_tree_map"]
    for result_dict in all_nodes:
        for name, node in result_dict.items():
            if node.__class__ is nodeset.source and "_" not in name:
                root_node = node
            else:
                if isinstance(node, list) and isinstance(node[0], list):
                    other_nodes[name] = node[0]
                else:
                    other_nodes[name] = node
        results.append(
            _to_relation_tree(nodeset, root_node, other_nodes, relation_tree_map)
        )
    return results


def classproperty(f) -> CustomNodeSet:
    class cpf:
        def __init__(self, getter):
            self.getter = getter

        def __get__(self, obj, class_type):
            return self.getter(class_type)

    return cpf(f)
