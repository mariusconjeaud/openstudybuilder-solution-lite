import functools
import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from dateutil.parser import isoparse
from neo4j.exceptions import CypherSyntaxError
from neomodel import Q, db
from pydantic import BaseModel, Field, validator
from pydantic.types import T, conlist

from clinical_mdr_api import exceptions
from clinical_mdr_api.models.concept import VersionProperties
from clinical_mdr_api.models.ct_term import SimpleTermModel

# Re-used regex
nested_regex = re.compile(r"\.")

log = logging.getLogger(__name__)


class ComparisonOperator(Enum):
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    CONTAINS = "co"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL_TO = "ge"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL_TO = "le"
    BETWEEN = "bw"
    IN = "in"


comparison_operator_to_neomodel = {
    ComparisonOperator.EQUALS: "",
    ComparisonOperator.NOT_EQUALS: "__ne",
    ComparisonOperator.CONTAINS: "__contains",
    ComparisonOperator.GREATER_THAN: "__gt",
    ComparisonOperator.GREATER_THAN_OR_EQUAL_TO: "__gte",
    ComparisonOperator.LESS_THAN: "__lt",
    ComparisonOperator.LESS_THAN_OR_EQUAL_TO: "__lte",
    ComparisonOperator.IN: "__in",
}


data_type_filters = {
    str: [
        ComparisonOperator.EQUALS,
        ComparisonOperator.NOT_EQUALS,
        ComparisonOperator.CONTAINS,
        ComparisonOperator.IN,
    ],
    int: [
        ComparisonOperator.EQUALS,
        ComparisonOperator.NOT_EQUALS,
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.GREATER_THAN_OR_EQUAL_TO,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.LESS_THAN_OR_EQUAL_TO,
        ComparisonOperator.BETWEEN,
        ComparisonOperator.IN,
    ],
    float: [
        ComparisonOperator.EQUALS,
        ComparisonOperator.NOT_EQUALS,
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.GREATER_THAN_OR_EQUAL_TO,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.LESS_THAN_OR_EQUAL_TO,
        ComparisonOperator.BETWEEN,
        ComparisonOperator.IN,
    ],
    datetime: [
        ComparisonOperator.EQUALS,
        ComparisonOperator.NOT_EQUALS,
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.GREATER_THAN_OR_EQUAL_TO,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.LESS_THAN_OR_EQUAL_TO,
        ComparisonOperator.BETWEEN,
        ComparisonOperator.IN,
    ],
    bool: [ComparisonOperator.EQUALS, ComparisonOperator.IN],
}


def get_wildcard_filter(filter_elem, model: BaseModel):
    """
    Creates the wildcard filter for all string properties also nested one.
    The wildcard filter is a 'contains' case insensitive filter that is combined by OR operator with other properties.
    :param filter_elem:
    :param model:
    :return:
    """
    wildcard_filter = []
    for name, field in model.__fields__.items():
        field_source = get_field_path(prop=name, field=field)
        model_sources = get_version_properties_sources()
        if field_source in model_sources and field.type_ is str:
            get_versioning_q_filter(
                filter_elem=filter_elem, field=field, q_filters=wildcard_filter
            )
            continue
        if issubclass(field.type_, BaseModel):
            q_obj = get_wildcard_filter(filter_elem=filter_elem, model=field.type_)
            wildcard_filter.append(q_obj)
        elif field.type_ is str and name not in ["possible_actions"]:
            q_obj = Q(**{f"{field_source}__icontains": filter_elem.v[0]})
            wildcard_filter.append(q_obj)
    return functools.reduce(lambda filter1, filter2: filter1 | filter2, wildcard_filter)


def get_embedded_field(fields: list, model: BaseModel):
    """
    Return the embedded field to filter by. For instance we can obtain 'flowchart_group.name' filter clause
    from the client which means that we want to filter by the name property in the flowchart_group nested model.
    :param fields:
    :param model:
    :return:
    """
    if len(fields) == 1:
        return model.__fields__.get(fields[0])
    return get_embedded_field(fields[1:], model=model.__fields__.get(fields[0]).type_)


def get_field(prop, model):
    # if property is a nested property, for instance flowchartGroup.name we have to get underlying
    # 'name' property to filter by.
    if "." in prop:
        field = get_embedded_field(fields=prop.split("."), model=model)
    else:
        field = model.__fields__.get(prop)
    return field


def get_field_path(prop, field):
    source = field.field_info.extra.get("source")
    if source is not None:
        if "." in source:
            field_name = source.replace(".", "__")
        else:
            field_name = source
    else:
        field_name = prop
    return field_name


def get_order_by_clause(sort_by: Optional[dict], model: BaseModel):
    sort_paths = []
    if sort_by:
        for key, value in sort_by.items():
            path = get_field_path(prop=key, field=get_field(prop=key, model=model))
            if value is False:
                path = f"-{path}"
            sort_paths.append(path)
    return sort_paths


def decrement_page_number(page_number: int) -> int:
    page_number -= 1
    return page_number


def unwind_versioning_properties(field_source: str):
    parts = field_source.split("|")
    prop = parts[-1]
    field_names = [
        f"latest_draft|{prop}",
        f"latest_final|{prop}",
        f"latest_retired|{prop}",
    ]
    return field_names


# pylint:disable=unsupported-binary-operation
def get_versioning_q_filter(filter_elem, field, q_filters: list):
    q_filters.append(
        Q(**{f"latest_draft|{field.name}": f"{filter_elem.v[0]}"})
        | Q(**{f"latest_final|{field.name}": f"{filter_elem.v[0]}"})
        | Q(**{f"latest_retired|{field.name}": f"{filter_elem.v[0]}"})
    )


def get_version_properties_sources() -> list:
    return [
        field.field_info.extra.get("source")
        for field in VersionProperties.__fields__.values()
    ]


def transform_filters_into_neomodel(filter_by: Union[dict, None], model: BaseModel):
    neomodel_filters = {}
    q_filters = []
    filters = FilterDict(elements=filter_by)
    for prop, filter_elem in filters.elements.items():
        if prop == "*":
            q_filters.append(get_wildcard_filter(filter_elem=filter_elem, model=model))
        else:
            field = get_field(prop=prop, model=model)
            if field is not None:
                field_name = get_field_path(prop=prop, field=field)
                model_sources = get_version_properties_sources()
                if field_name in model_sources:
                    get_versioning_q_filter(
                        filter_elem=filter_elem, field=field, q_filters=q_filters
                    )
                    continue

                # get the list of possible filters for a given field type
                possible_filters = data_type_filters.get(field.type_)

                # if possible filter list is None it means that data type of the filter field is not listed
                # in the data_type_filters configuration
                if possible_filters is None:
                    raise AttributeError(
                        f"Passed not supported data type {field.type_}"
                    )
                if filter_elem.op not in possible_filters:
                    raise AttributeError(
                        f"The following filtering type {filter_elem.op.name} is not supported "
                        f"for the following data type {field.type_}"
                    )
                if len(filter_elem.v) == 1:
                    neomodel_filter = comparison_operator_to_neomodel.get(
                        filter_elem.op
                    )
                    if neomodel_filter is None:
                        raise AttributeError(
                            f"The following operator {filter_elem.op} is not mapped "
                            f"to the neomodel operators"
                        )
                    filter_name = f"{field_name}{neomodel_filter}"
                    filter_value = filter_elem.v[0]
                    if isinstance(filter_value, str) and is_date(filter_value):
                        filter_value = f"datetime({filter_value})"
                    neomodel_filters[filter_name] = filter_value
                else:
                    if filter_elem.op == ComparisonOperator.BETWEEN:
                        filter_elem.v.sort()
                        filter_values = filter_elem.v
                        min_bound = f"{field_name}__gt"
                        max_bound = f"{field_name}__lt"
                        min_bound_value = filter_values[0]
                        max_bound_value = filter_values[1]
                        if isinstance(min_bound_value, str) and is_date(
                            min_bound_value
                        ):
                            min_bound_value = f"datetime({min_bound_value})"
                        neomodel_filters[min_bound] = min_bound_value
                        if isinstance(max_bound_value, str) and is_date(
                            max_bound_value
                        ):
                            max_bound_value = f"datetime({max_bound_value})"
                        neomodel_filters[max_bound] = max_bound_value
                    elif filter_elem.op == ComparisonOperator.EQUALS:
                        neomodel_filter = comparison_operator_to_neomodel.get(
                            ComparisonOperator.IN
                        )
                        filter_name = f"{field_name}{neomodel_filter}"
                        filter_value = filter_elem.v
                        q_filters.append(Q(**{filter_name: filter_value}))
                        # neomodel_filters[filter_name] = filter_value
                    else:
                        raise AttributeError(
                            f"Not valid operator {filter_elem.op.value} for the following property {prop} of type"
                            f"{type(prop)}"
                        )
            else:
                raise AttributeError("Passed wrong filter field name")
    return neomodel_filters, q_filters


def is_date(string):
    try:
        # changing into isoparse instead of parse as
        # parse was interpreting for instance '1.0' as date
        # and '1.0' is commonly used value in version filtering
        isoparse(string)
        return True
    except ValueError:
        return False


class GenericFilteringReturn:
    def __init__(self, items: Sequence[Any], total_count: int):
        self.items = items
        self.total_count = total_count


class FilterOperator(Enum):
    AND = "and"
    OR = "or"

    @staticmethod
    def from_str(label):
        if label in ("or", "OR"):
            return FilterOperator.OR
        if label in ("and", "AND"):
            return FilterOperator.AND
        raise exceptions.NotFoundException(
            "Filter operator only accepts values of 'and' and 'or'."
        )


class FilterDictElement(BaseModel):
    v: conlist(item_type=T) = Field(
        ...,
        title="search values",
        description="list of values to use as search values. Can be of any type.",
    )
    op: Optional[ComparisonOperator] = Field(
        ComparisonOperator.EQUALS,
        title="comparison operator to apply",
        description="comparison operator from enum, for operations like =, >=, or <",
    )

    @validator("op", pre=True)
    # pylint:disable=no-self-argument
    def _is_op_supported(cls, val):
        try:
            return ComparisonOperator(val)
        except Exception as exc:
            raise exceptions.ValidationException(
                f"Unsupported comparison operator: '{val}'"
            ) from exc


class FilterDict(BaseModel):
    elements: Dict[str, FilterDictElement] = Field(
        ...,
        title="filters description",
        description="""filters description, with key being the alias to filter
        against, and value is a description object with search values and comparison operator""",
    )

    @validator("elements", pre=True)
    # pylint:disable=no-self-argument
    def _none_as_empty_dict(cls, val):
        if val is None:
            return {}
        return val


class CypherQueryBuilder:
    """
    This class builds two queries : items and total_count with filtering and pagination capabilities.
    Important note : To provide the filtering and sorting capabilities, this class
    relies on the use of Cypher aliases. Please read the 'Mandatory inputs' section carefully.

    Mandatory inputs :
        match_clause : Basically everything a Cypher query needs to do before a
        RETURN statement : MATCH a pattern, CALL a procedure/subquery, do a WITH processing...
            Note, though, filtering, sorting and pagination will be added
            automatically by the class methods.
        alias_clause : Cypher aliases definition clause ; Similar to what you would
        write in your RETURN statement, but without the RETURN keyword.
            This is processed to set variables on which to apply filtering and sorting.

    Optional inputs :
        sort_by: dictionary of Cypher aliases on which to apply sorting as keys, and
        boolean to define sort direction (true=ascending) as values
        page_number : int, number of the page to return. 1-based (will be converted
        to 0-based for Cypher by class methods)
        page_size : int, number of results per page
        filter_by : dict, keys are field names for filter_variable and values are
        objects describing the filtering to execute
            * v = list of values to filter against
            * op = filter operator. Expected values : eq, co (contains), ge, gt, le, lt
            Example : { "name" : { "v": ["Jimbo"], "op": "co" }}
        return_model (class) / wildcard_properties_list (list of strings): when a
        wildcard filtering is requested, we need to extract the list of
            known properties on which to apply filter. This can be done automatically
            from the return model definition ; in some more complex cases
            (e.g. aggregated object with many nested objects), the list cannot be
            extracted directly from the model definition, and has to be provided to this method
        format_filter_sort_keys: Callable. In some cases, the returned model property
        keys differ from the property keys defined in the database.
            To cover these cases, a conversion function can be provided.

    Output properties :
        full_query : Complete cypher query with all clauses. See build_full_query
        method definition for more details.
        count_query : Cypher query with match, filter clauses, and results count. Se
        build_count_query method definition for more details.
        parameters : Parameters object to pass along with the cypher query

    Internal properties :
        filter_clause : str - Generated on class init ; adds filtering on aliases as
        defined in the filter_by dictionary
        sort_clause : str - Generated on class init ; adds sorting on aliases as
        defined in the sort_by dictionary
        pagination_clause : str - Generated on class init ; adds pagination
    """

    def __init__(
        self,
        match_clause: str,
        alias_clause: str,
        page_number: int = 1,
        page_size: int = 0,
        sort_by: Optional[dict] = None,
        filter_by: Optional[FilterDict] = None,
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
        total_count: bool = False,
        return_model: Optional[type] = None,
        wildcard_properties_list: Optional[Sequence[str]] = None,
        format_filter_sort_keys: Optional[Callable] = None,
    ):
        if wildcard_properties_list is None:
            wildcard_properties_list = []

        self.match_clause = match_clause
        self.alias_clause = alias_clause
        self.sort_by = sort_by if sort_by is not None else {}
        self.page_number = page_number
        self.page_size = page_size
        self.filter_by = filter_by
        self.filter_operator = filter_operator
        self.total_count = total_count
        self.return_model = return_model
        self.wildcard_properties_list = wildcard_properties_list
        self.format_filter_sort_keys = format_filter_sort_keys
        self.filter_clause = ""
        self.sort_clause = ""
        self.pagination_clause = ""
        self.parameters = {}

        # Auto-generate internal clauses
        if filter_by and len(self.filter_by.elements) > 0:
            self.build_filter_clause()
        if self.page_size > 0:
            self.build_pagination_clause()
        if self.sort_by:
            if not isinstance(self.sort_by, dict):
                raise exceptions.ValidationException("sort_by must be a dict")
            self.build_sort_clause()

        # Auto-generate final queries
        self.build_full_query()
        self.build_count_query()

    def build_filter_clause(self) -> None:
        _filter_clause = "WHERE "
        filter_predicates = []

        for key in self.filter_by.elements:
            _alias = key
            _values = self.filter_by.elements[key].v
            _operator = self.filter_by.elements[key].op
            _predicates = []
            _parsed_operator = "="

            if _alias == "*":
                # Parse operator to use in filter for wildcard
                _parsed_operator = " CONTAINS "
                # Only accept requests with default operator (set to equal by FilterDict class) or specified contains operator
                if (
                    ComparisonOperator(_operator) != ComparisonOperator.EQUALS
                    and ComparisonOperator(_operator) != ComparisonOperator.CONTAINS
                ):
                    raise exceptions.NotFoundException(
                        "Only the default 'contains' operator is supported for wildcard filtering."
                    )
            else:
                # Parse operator to use in filter for the current label
                if ComparisonOperator(_operator) == ComparisonOperator.CONTAINS:
                    _parsed_operator = " CONTAINS "
                elif ComparisonOperator(_operator) == ComparisonOperator.GREATER_THAN:
                    _parsed_operator = ">"
                elif (
                    ComparisonOperator(_operator)
                    == ComparisonOperator.GREATER_THAN_OR_EQUAL_TO
                ):
                    _parsed_operator = ">="
                elif ComparisonOperator(_operator) == ComparisonOperator.LESS_THAN:
                    _parsed_operator = "<"
                elif (
                    ComparisonOperator(_operator)
                    == ComparisonOperator.LESS_THAN_OR_EQUAL_TO
                ):
                    _parsed_operator = "<="

            # Parse filter clauses for the current label
            # 'Between' operator works differently from the others
            if ComparisonOperator(_operator) == ComparisonOperator.BETWEEN:
                if len(_values) == 2:
                    if _alias != "*":
                        # If necessary, replace key using return-model-to-cypher fieldname mapping
                        if self.format_filter_sort_keys:
                            _alias = self.format_filter_sort_keys(_alias)
                        _values.sort()
                        _query_param_prefix = f"{self.escape_alias(_alias)}"
                        _predicate = f"${_query_param_prefix}_0<={_alias}<=${_query_param_prefix}_1"
                        # If the provided value can be parsed as a date, also add a predicate with a datetime casting on the Neo4j side
                        if is_date(_values[0]) and is_date(_values[1]):
                            _date_predicate = f"datetime(${_query_param_prefix}_0)<={_alias}<=datetime(${_query_param_prefix}_1)"
                            _predicate += f" OR {_date_predicate}"
                        filter_predicates.append(_predicate)
                        self.parameters[f"{_query_param_prefix}_0"] = _values[0]
                        self.parameters[f"{_query_param_prefix}_1"] = _values[1]
                    else:
                        exceptions.NotFoundException(
                            "Between operator not supported with wildcard filtering"
                        )
                else:
                    exceptions.NotFoundException(
                        "For between operator to work, exactly 2 values must be provided"
                    )
            else:
                # If necessary, replace key using return-model-to-cypher fieldname mapping
                if self.format_filter_sort_keys and _alias != "*":
                    _alias = self.format_filter_sort_keys(_alias)
                # An empty _values list means that the returned item's property value should be null
                if len(_values) == 0:
                    if _alias == "*":
                        raise exceptions.ValidationException(
                            "Wildcard filtering not supported with null values"
                        )
                    _predicates.append(f"{_alias} IS NULL")
                else:
                    for index, el in enumerate(_values):
                        # If filter is a wildcard
                        if _alias == "*":
                            # Wildcard filtering only accepts a search value of type string
                            if isinstance(el, str):
                                # If a list of wildcard properties is provided, use it
                                if len(self.wildcard_properties_list) > 0:
                                    for db_property in self.wildcard_properties_list:
                                        _predicates.append(
                                            f"toLower({db_property}){_parsed_operator}$wildcard_{index}"
                                        )
                                # If not, then extract list of properties from return model
                                elif self.return_model:
                                    for (
                                        attribute,
                                        attr_desc,
                                    ) in self.return_model.__fields__.items():
                                        # Wildcard filtering only searches in properties of type string
                                        if (
                                            attr_desc.type_ is str
                                            and attribute not in ["possible_actions"]
                                        ):
                                            # name=$name_0 with name_0 defined in parameter objects
                                            if self.format_filter_sort_keys:
                                                attribute = (
                                                    self.format_filter_sort_keys(
                                                        attribute
                                                    )
                                                )
                                            _predicates.append(
                                                f"toLower({attribute}){_parsed_operator}$wildcard_{index}"
                                            )
                                        # Wildcard filtering for SimpleTermModel
                                        elif attr_desc.type_ is SimpleTermModel:
                                            # name=$name_0 with name_0 defined in parameter objects
                                            if self.format_filter_sort_keys:
                                                attribute = (
                                                    self.format_filter_sort_keys(
                                                        attribute
                                                    )
                                                )
                                            if attr_desc.sub_fields is None:
                                                # if field is just SimpleTermModel compare wildcard filter
                                                # with name property of SimpleTermModel
                                                _predicates.append(
                                                    f"toLower({attribute}.name){_parsed_operator}$wildcard_{index}"
                                                )
                                            else:
                                                # if field is an array of SimpleTermModels
                                                _predicates.append(
                                                    f"$wildcard_{index} IN [attr in {attribute} | toLower(attr.name)]"
                                                )
                                # If none are provided, raise an exception
                                else:
                                    raise exceptions.ValidationException(
                                        "Wildcard filtering not properly covered for this object"
                                    )
                                self.parameters[f"wildcard_{index}"] = el.lower()
                            else:
                                raise exceptions.NotFoundException(
                                    "Wildcard filtering only supports a search value of type string"
                                )
                        else:
                            # name=$name_0 with name_0 defined in parameter objects
                            # . for nested properties will be replaced by _
                            _query_param_name = f"{self.escape_alias(_alias)}_{index}"
                            if (
                                self.return_model
                                and issubclass(self.return_model, BaseModel)
                                and self.return_model.__fields__.get(_alias)
                                and self.return_model.__fields__.get(_alias).type_
                                is SimpleTermModel
                            ):
                                attr_desc = self.return_model.__fields__.get(_alias)
                                # name=$name_0 with name_0 defined in parameter objects
                                if attr_desc.sub_fields is None:
                                    # if field is just SimpleTermModel compare wildcard filter
                                    # with name property of SimpleTermModel
                                    _predicates.append(
                                        f"toLower({_alias}.name){_parsed_operator}${_query_param_name}"
                                    )
                                else:
                                    # if field is an array of SimpleTermModels
                                    _predicates.append(
                                        f"any(attr in {_alias} WHERE toLower(attr.name) CONTAINS ${_query_param_name})"
                                    )
                                self.parameters[f"{_query_param_name}"] = el.lower()
                            elif (
                                isinstance(el, str)
                                and ComparisonOperator(_operator)
                                == ComparisonOperator.CONTAINS
                            ):
                                _predicates.append(
                                    f"toLower(toString({_alias})){_parsed_operator}${_query_param_name}"
                                )
                                self.parameters[f"{_query_param_name}"] = el.lower()
                            else:
                                _predicates.append(
                                    f"{_alias}{_parsed_operator}${_query_param_name}"
                                )
                                # If the provided value is a string that can be parsed as a date,
                                # also add a predicate with a datetime casting on the Neo4j side
                                # It is necessary to check if it is a string because the value could also be a boolean here
                                if isinstance(el, str) and is_date(el):
                                    _predicates.append(
                                        f"{_alias}{_parsed_operator}datetime(${_query_param_name})"
                                    )
                                self.parameters[_query_param_name] = el

                # If multiple values, will create a clause with OR, between ()
                _predicate = " OR ".join(_predicates)
                if len(_values) > 1 or _alias == "*":
                    _predicate = f"({_predicate})"

                # Add to list of predicates
                filter_predicates.append(_predicate)

        # Set clause
        self.filter_clause = (
            _filter_clause
            + f" {self.filter_operator.value.upper()} ".join(list(filter_predicates))
        )

    def build_pagination_clause(self) -> None:
        # Set clause
        self.pagination_clause = "SKIP $page_number * $page_size LIMIT $page_size"

        # Add corresponding parameters
        self.parameters["page_number"] = self.page_number - 1
        self.parameters["page_size"] = self.page_size

    def build_sort_clause(self) -> None:
        _sort_clause = "ORDER BY "
        # Add list of order by statements parsed from dict
        # If necessary, replace key using return-model-to-cypher fieldname mapping
        sort_by_statements = map(
            lambda key: f"{self.format_filter_sort_keys(key) if self.format_filter_sort_keys else key} "
            + ("ASC" if self.sort_by[key] else "DESC"),
            self.sort_by.keys(),
        )

        # Set clause
        self.sort_clause = _sort_clause + ",".join(list(sort_by_statements))

    def build_full_query(self) -> None:
        """
        The generated query will have the following pattern :
            MATCH caller-provided (and WITH, CALL, ... any custom pattern matching necessary)
            > WITH alias_clause caller-provided
            > WHERE filter_clause using aliases
            > RETURN * to return results as is
            > ORDER BY to sort results using aliases
            > SKIP * LIMIT * to paginate results
        """
        _with_alias_clause = f"WITH {self.alias_clause}"
        _return_clause = "RETURN *"

        # Set clause
        self.full_query = " ".join(
            [
                self.match_clause,
                _with_alias_clause,
                self.filter_clause,
                _return_clause,
                self.sort_clause,
                self.pagination_clause,
            ]
        )

    def build_count_query(self) -> None:
        """
        The generated query will have the following pattern :
            MATCH caller-provided (and WITH, CALL, ... any custom pattern matching necessary)
            > WITH alias_clause caller-provided
            > WHERE filter_clause using aliases
            > RETURN results count
        """
        _with_alias_clause = f"WITH {self.alias_clause}"
        _return_count_clause = "RETURN count(*) AS total_count"

        # Set clause
        self.count_query = " ".join(
            [
                self.match_clause,
                _with_alias_clause,
                self.filter_clause,
                _return_count_clause,
            ]
        )

    def build_header_query(self, header_alias: str, result_count: int) -> str:
        """
        Mandatory inputs :
            * header_alias - Alias of the header for which to get possible values, as defined in the alias clause
            * result_count - Number of results to return
        The generated query will have the following pattern :
            MATCH caller-provided (and WITH, CALL, ... any custom pattern matching necessary)
            > WITH alias_clause caller-provided
            > WHERE filter_clause using aliases
            > RETURN list of possible headers for given alias, ordered, with a limit
        """
        _with_alias_clause = f"WITH {self.alias_clause}"
        # Escape header_alias to plan for nested properties as a . character would make Cypher fail
        _escaped_header_alias = self.escape_alias(header_alias)
        _return_header_clause = f"""WITH DISTINCT {header_alias} AS
        {_escaped_header_alias} ORDER BY {_escaped_header_alias} LIMIT {result_count} RETURN collect(DISTINCT {_escaped_header_alias}) AS values"""

        return " ".join(
            [
                self.match_clause,
                _with_alias_clause,
                self.filter_clause,
                _return_header_clause,
            ]
        )

    def escape_alias(self, alias: str) -> str:
        """
        Escapes alias to prevent Cypher failures.
            * Replaces . for nested properties by _
        """
        return re.sub(nested_regex, "_", alias)

    def execute(self) -> Tuple[any, any]:
        try:
            result_array, attributes_names = db.cypher_query(
                query=self.full_query, params=self.parameters
            )
        except CypherSyntaxError as _ex:
            raise exceptions.ValidationException(
                "Unsupported filtering or sort parameters specified"
            )
        return result_array, attributes_names


def sb_clear_cache(caches: List[str] = None):
    """
    Decorator that will clear the specified caches after the wrapped function execution.
    """
    if caches is None:
        caches = []

    def decorator(function):
        @functools.wraps(function)
        def wrapper(self, *args, **kwargs):
            try:
                result = function(self, *args, **kwargs)
                return result
            finally:
                for cache_name in caches:
                    cache = getattr(self, cache_name, None)
                    if cache:
                        log.info(
                            "Clear cache '%s.%s' of size: %s",
                            self.__class__.__name__,
                            cache_name,
                            cache.currsize,
                        )
                        cache.clear()

        return wrapper

    return decorator
