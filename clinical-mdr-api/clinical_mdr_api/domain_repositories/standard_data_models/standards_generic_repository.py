from abc import abstractmethod
from typing import Optional, Sequence, Tuple, TypeVar

from clinical_mdr_api.domain_repositories.models._utils import CustomNodeSet
from clinical_mdr_api.repositories._utils import (
    ComparisonOperator,
    FilterOperator,
    decrement_page_number,
    get_field,
    get_field_path,
    get_order_by_clause,
    transform_filters_into_neomodel,
)

_StandardsReturnType = TypeVar("_StandardsReturnType")


class StandardsGenericRepository:

    root_class = type
    return_model = type

    @abstractmethod
    def get_neomodel_extension_query(self) -> CustomNodeSet:
        """
        Method creates a specific neomodel extension query that fetches all required relationships to build an object of type return_model.
        :return CustomNodeSet:
        """

        raise NotImplementedError

    def find_all(
        self,
        sort_by: Optional[dict] = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: Optional[dict] = None,
        # pylint:disable=unused-argument
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
        total_count: bool = False,
    ) -> Tuple[Sequence[_StandardsReturnType], int]:
        neomodel_filter, q_filters = transform_filters_into_neomodel(
            filter_by=filter_by, model=self.return_model
        )
        sort_paths = get_order_by_clause(sort_by=sort_by, model=self.return_model)
        page_number = decrement_page_number(page_number)
        nodes = (
            self.get_neomodel_extension_query()
            .order_by(sort_paths[0] if len(sort_paths) > 0 else "uid")
            .filter(*q_filters, **neomodel_filter)
            .limit_results(page_size)
            .skip_results(page_number * page_size)
            .to_relation_trees()
        )
        all_data_model = [
            self.return_model.from_orm(activity_node) for activity_node in nodes
        ]
        if total_count:
            len_query = self.root_class.nodes.filter(*q_filters, **neomodel_filter)
            all_nodes = len(len_query)
        return all_data_model, all_nodes if total_count else 0

    def find_by_uid(self, uid: str) -> Optional[_StandardsReturnType]:
        node = self.get_neomodel_extension_query().filter(uid=uid).to_relation_trees()
        return node

    def get_distinct_headers(
        self,
        field_name: str,
        search_string: Optional[str] = "",
        filter_by: Optional[dict] = None,
        # pylint: disable=unused-argument
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
        result_count: int = 10,
    ) -> Sequence:
        """
        Method runs a cypher query to fetch possible values for a given field_name, with a limit of result_count.
        It uses generic filtering capability, on top of filtering the field_name with provided search_string.

        :param field_name: Field name for which to return possible values
        :param search_string
        :param filter_by:
        :param filter_operator: Same as for generic filtering
        :param result_count: Max number of values to return. Default 10
        :return Sequence:
        """

        # Add header field name to filter_by, to filter with a CONTAINS pattern
        if search_string != "":
            if filter_by is None:
                filter_by = {}
            filter_by[field_name] = {
                "v": [search_string],
                "op": ComparisonOperator.CONTAINS,
            }
        neomodel_filter, q_filters = transform_filters_into_neomodel(
            filter_by=filter_by, model=self.return_model
        )

        field = get_field(prop=field_name, model=self.return_model)
        field_path = get_field_path(prop=field_name, field=field)
        field_traversal = field_path
        if "__" in field_path:
            field_traversal, prop = field_path.rsplit("__", 1)
            nodes = (
                self.root_class.nodes.fetch_optional_relations_and_collect(
                    field_traversal
                )
                .filter(*q_filters, **neomodel_filter)
                .limit_results(result_count)
                .to_relation_trees()
            )
        else:
            prop = field_path
            nodes = (
                self.root_class.nodes.filter(*q_filters, **neomodel_filter)
                .limit_results(result_count)
                .to_relation_trees()
            )

        result = []
        for n in nodes:
            for part in field_traversal.split("__"):
                if part in n._relations:
                    n = n._relations[part]
                else:
                    n = [n]
            for res in n:
                result.append(getattr(res, prop))

        return result
