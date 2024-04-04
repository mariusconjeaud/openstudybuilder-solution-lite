import abc
import copy
from datetime import datetime
from typing import TypeVar

from neomodel import NodeClassNotDefined, db

from clinical_mdr_api.domain_repositories.library_item_repository import (
    RETRIEVED_READ_ONLY_MARK,
    LibraryItemRepositoryImplBase,
)
from clinical_mdr_api.domain_repositories.models.activities import (
    ActivityGroupRoot,
    ActivityRoot,
    ActivitySubGroupRoot,
)
from clinical_mdr_api.domain_repositories.models.concepts import (
    NumericValue,
    NumericValueRoot,
)
from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    CTTermRoot,
)
from clinical_mdr_api.domain_repositories.models.dictionary import DictionaryTermRoot
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)
from clinical_mdr_api.domain_repositories.models.syntax import (
    SyntaxInstanceRoot,
    SyntaxPreInstanceRoot,
    SyntaxTemplateRoot,
    SyntaxTemplateValue,
)
from clinical_mdr_api.domain_repositories.models.template_parameter import (
    ParameterTemplateRoot,
    TemplateParameterComplexRoot,
    TemplateParameterComplexValue,
    TemplateParameterTermRoot,
)
from clinical_mdr_api.domains.libraries.parameter_term import (
    ComplexParameterTerm,
    NumericParameterTermVO,
    ParameterTermEntryVO,
    SimpleParameterTermVO,
)
from clinical_mdr_api.domains.syntax_templates.template import (
    InstantiationCountsVO,
    TemplateAggregateRootBase,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemAggregateRootBase,
    LibraryItemStatus,
    VersioningException,
)
from clinical_mdr_api.exceptions import (
    BusinessLogicException,
    NotFoundException,
    ValidationException,
)
from clinical_mdr_api.repositories._utils import (
    ComparisonOperator,
    FilterOperator,
    validate_max_skip_clause,
)

_AggregateRootType = TypeVar("_AggregateRootType", bound=LibraryItemAggregateRootBase)


class GenericSyntaxRepository(
    LibraryItemRepositoryImplBase[_AggregateRootType], abc.ABC
):
    def find_by_uid_2(
        self,
        uid: str,
        *,
        version: str | None = None,
        status: LibraryItemStatus | None = None,
        at_specific_date: datetime | None = None,
        for_update: bool = False,
        return_study_count: bool | None = False,
        return_instantiation_counts: bool = False,
    ):
        "Use find_by_uid instead"

    def find_all(
        self,
        *,
        status: LibraryItemStatus | None = None,
        library_name: str | None = None,
        return_study_count: bool | None = False,
    ):
        "Use get_all instead"

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        root: VersionRoot,
        library: Library,
        relationship: VersionRelationship,
        value: VersionValue,
        study_count: int = 0,
        counts: InstantiationCountsVO | None = None,
    ) -> _AggregateRootType:
        "Use _create_ar instead"

    @abc.abstractmethod
    def _create_ar(
        self,
        root: SyntaxTemplateRoot,
        library: Library,
        relationship: VersionRelationship,
        value: SyntaxTemplateValue,
        study_count: int = 0,
        **kwargs,
    ) -> TemplateAggregateRootBase:
        raise NotImplementedError

    def find_by_uid(
        self,
        uid: str,
        for_update=False,
        *,
        library_name: str | None = None,
        status: LibraryItemStatus | None = None,
        version: str | None = None,
        return_study_count: bool | None = False,
        for_audit_trail: bool = False,
    ) -> _AggregateRootType | list[_AggregateRootType]:
        if for_update and (version is not None or status is not None):
            raise NotImplementedError(
                "Retrieval for update supported only for latest version."
            )

        if for_update:
            self._lock_object(uid)

        aggregates: list[_AggregateRootType] = []

        match_stmt, return_stmt = self._find_cypher_query(
            with_status=bool(status),
            with_version=bool(version),
            with_pagination=False,
            return_study_count=return_study_count,
            uid=uid,
            for_audit_trail=for_audit_trail,
        )

        params = {"uid": uid}
        if status:
            params["status"] = status.value
        if version:
            params["version"] = version

        try:
            result, _ = db.cypher_query(
                match_stmt + return_stmt,
                params=params,
                resolve_objects=True,
            )
        except NodeClassNotDefined as exc:
            raise VersioningException(
                "Object labels were changed - likely the object was deleted in a concurrent transaction."
            ) from exc

        if not result:
            raise NotFoundException(
                f"No Syntax Template with UID ({uid}) found in given status and version."
            )

        for (
            library,
            root,
            relationship,
            value,
            study_count,
            indications,
            categories,
            subcategories,
            activities,
            activity_groups,
            activity_subgroups,
            template_type,
            instance_template,
        ) in result:
            if library and library_name is not None and library_name != library.name:
                continue

            ar: _AggregateRootType = self._create_ar(
                library=library,
                root=root,
                relationship=relationship,
                value=value,
                study_count=study_count,
                indications=indications[0] if indications else [],
                template_type=template_type,
                categories=categories[0] if categories else [],
                subcategories=subcategories[0] if subcategories else [],
                activities=activities[0] if activities else [],
                activity_groups=activity_groups[0] if activity_groups else [],
                activity_subgroups=activity_subgroups[0] if activity_subgroups else [],
                instance_template=instance_template,
            )

            if value and relationship:
                if for_update:
                    ar.repository_closure_data = (
                        root,
                        value,
                        library,
                        copy.deepcopy(ar),
                    )
                else:
                    ar.repository_closure_data = RETRIEVED_READ_ONLY_MARK
                aggregates.append(ar)

        if not for_audit_trail:
            return aggregates[0]

        return aggregates

    def get_all(
        self,
        *,
        status: LibraryItemStatus | None = None,
        library_name: str | None = None,
        return_study_count: bool | None = False,
        sort_by: dict | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        total_count: bool = False,
        for_audit_trail: bool = False,
    ) -> tuple[list, int]:
        aggregates = []

        validate_max_skip_clause(page_number=page_number, page_size=page_size)
        where_stmt, params = self._where_stmt(filter_by, filter_operator)

        match_stmt, return_stmt = self._find_cypher_query(
            with_status=bool(status),
            with_pagination=bool(page_size),
            return_study_count=return_study_count,
            where_stmt=where_stmt,
            sort_by=sort_by,
            for_audit_trail=for_audit_trail,
        )

        if status:
            params["status"] = status.value

        if page_size > 0:
            params["page_number"] = page_number - 1
            params["page_size"] = page_size

        result, _ = db.cypher_query(
            match_stmt + return_stmt,
            params=params,
            resolve_objects=True,
        )

        for (
            library,
            root,
            relationship,
            value,
            study_count,
            indications,
            categories,
            subcategories,
            activities,
            activity_groups,
            activity_subgroups,
            template_type,
            instance_template,
        ) in result:
            if library and library_name is not None and library_name != library.name:
                continue

            ar = self._create_ar(
                library=library,
                root=root,
                relationship=relationship,
                value=value,
                study_count=study_count,
                indications=indications[0] if indications else [],
                template_type=template_type,
                categories=categories[0] if categories else [],
                subcategories=subcategories[0] if subcategories else [],
                activities=activities[0] if activities else [],
                activity_groups=activity_groups[0] if activity_groups else [],
                activity_subgroups=activity_subgroups[0] if activity_subgroups else [],
                instance_template=instance_template,
            )

            ar.repository_closure_data = RETRIEVED_READ_ONLY_MARK
            aggregates.append(ar)

        count_result = []
        if total_count:
            count_result, _ = db.cypher_query(
                query=match_stmt + "RETURN count(DISTINCT ver_rel)", params=params
            )
        total_amount = (
            count_result[0][0] if len(count_result) > 0 and total_count else 0
        )
        return aggregates, total_amount

    def get_headers(
        self,
        *,
        field_name: str,
        status: LibraryItemStatus | None = None,
        search_string: str | None = "",
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        result_count: int = 10,
    ):
        if result_count <= 0:
            return []

        if filter_by is None:
            filter_by = {}

        try:
            cypher_field_name = self.basemodel_to_cypher_mapping()[field_name]
        except KeyError as e:
            raise ValidationException(
                f"Unsupported field name parameter: {field_name}. "
                f"Supported parameters are: {list(self.basemodel_to_cypher_mapping())}"
            ) from e

        if search_string:
            filter_by[field_name] = {
                "v": [search_string],
                "op": ComparisonOperator.CONTAINS.value,
            }

        where_stmt, params = self._where_stmt(filter_by, filter_operator, True)

        match_stmt, return_stmt = self._headers_cypher_query(
            cypher_field_name=cypher_field_name,
            with_status=bool(status),
            where_stmt=where_stmt,
        )

        if status:
            params["status"] = status.value

        result, _ = db.cypher_query(
            match_stmt + return_stmt,
            params=params | {"result_count": result_count},
            resolve_objects=True,
        )

        rs = []
        for item in result:
            rs.append(item[0])

        return rs

    def basemodel_to_cypher_mapping(self, header_query: bool = False):
        # Mapping between BaseModel attribute names and their corresponding
        # cypher query (as returned by _find_cypher_query() and _headers_cypher_query()) variables for filtering, sorting and headers
        mapping = {
            "library.name": "library.name",
            "uid": "root.uid",
            "sequence_id": "root.sequence_id",
            "name": "value.name",
            "name_plain": "value.name_plain",
            "status": "ver_rel.status",
            "version": "ver_rel.version",
            "start_date": "ver_rel.start_date",
            "end_date": "ver_rel.end_date",
        }

        if (
            issubclass(self.root_class, SyntaxTemplateRoot | SyntaxInstanceRoot)
            and not header_query
        ):
            mapping |= {"study_count": "study_count"}

        if hasattr(self.root_class, "is_confirmatory_testing"):
            mapping |= {"is_confirmatory_testing": "root.is_confirmatory_testing"}

        # pylint: disable=no-member
        if hasattr(self, "template_class") and hasattr(self.template_class, "has_type"):
            mapping |= {
                "template_uid": "template_root.uid",
                "template_name": "template_value.name",
                "template_type_uid": "type_root.uid",
                "type.term_uid": "type_root.uid",
                "criteria_template.type.term_uid": "type_root.uid",
            }

        if hasattr(self.value_class, "guidance_text"):
            mapping |= {"guidance_text": "value.guidance_text"}

        if hasattr(self.root_class, "has_indication"):
            mapping |= {
                "indications.term_uid": "indication_root.uid",
                "indications.name": "indication_value.name",
            }

        if hasattr(self.root_class, "has_type"):
            mapping |= {
                "template_type_uid": "type_root.uid",
                "type.term_uid": "type_root.uid",
                "type.name.sponsor_preferred_name": "type_ct_term_name_value.name",
                "type.name.sponsor_preferred_name_sentence_case": "type_ct_term_name_value.name_sentence_case",
                "type.attributes.code_submission_value": "type_ct_term_attributes_value.code_submission_value",
                "type.attributes.preferred_term": "type_ct_term_attributes_value.preferred_term",
            }

        if hasattr(self.root_class, "has_category"):
            mapping |= {
                "categories.term_uid": "category_root.uid",
                "categories.name.sponsor_preferred_name": "category_ct_term_name_value.name",
                "categories.name.sponsor_preferred_name_sentence_case": "category_ct_term_name_value.name_sentence_case",
                "categories.attributes.code_submission_value": "category_ct_term_attributes_value.code_submission_value",
                "categories.attributes.preferred_term": "category_ct_term_attributes_value.preferred_term",
            }

        if hasattr(self.root_class, "has_subcategory"):
            mapping |= {
                "sub_categories.term_uid": "subcategory_root.uid",
                "sub_categories.name.sponsor_preferred_name": "subcategory_ct_term_name_value.name",
                "sub_categories.name.sponsor_preferred_name_sentence_case": "subcategory_ct_term_name_value.name_sentence_case",
                "sub_categories.attributes.code_submission_value": "subcategory_ct_term_attributes_value.code_submission_value",
                "sub_categories.attributes.preferred_term": "subcategory_ct_term_attributes_value.preferred_term",
                "subCategories.term_uid": "subcategory_root.uid",
                "subCategories.name.sponsor_preferred_name": "subcategory_ct_term_name_value.name",
                "subCategories.name.sponsor_preferred_name_sentence_case": "subcategory_ct_term_name_value.name_sentence_case",
                "subCategories.attributes.code_submission_value": "subcategory_ct_term_attributes_value.code_submission_value",
                "subCategories.attributes.preferred_term": "subcategory_ct_term_attributes_value.preferred_term",
            }

        if hasattr(self.root_class, "has_activity"):
            mapping |= {
                "activities.uid": "activity_root.uid",
                "activities": "activity_value.name",
                "activities.name": "activity_value.name",
                "activities.name_sentence_case": "activity_value.name_sentence_case",
                "activity.uid": "activity_root.uid",
                "activity": "activity_value.name",
                "activity.name": "activity_value.name",
                "activity.name_sentence_case": "activity_value.name_sentence_case",
            }

        if hasattr(self.root_class, "has_activity_group"):
            mapping |= {
                "activity_groups.uid": "activity_group_root.uid",
                "activity_groups": "activity_group_value.name",
                "activity_groups.name": "activity_group_value.name",
                "activity_groups.name_sentence_case": "activity_group_value.name_sentence_case",
                "activity.activity_group.uid": "activity_group_root.uid",
                "activity.activity_group": "activity_group_value.name",
                "activity.activity_group.name": "activity_group_value.name",
                "activity.activity_group.name_sentence_case": "activity_group_value.name_sentence_case",
            }

        if hasattr(self.root_class, "has_activity_subgroup"):
            mapping |= {
                "activity_subgroups.uid": "activity_subgroup_root.uid",
                "activity_subgroups": "activity_subgroup_value.name",
                "activity_subgroups.name": "activity_subgroup_value.name",
                "activity_subgroups.name_sentence_case": "activity_subgroup_value.name_sentence_case",
                "activity.activity_subgroup.uid": "activity_subgroup_root.uid",
                "activity.activity_subgroup": "activity_subgroup_value.name",
                "activity.activity_subgroup.name": "activity_subgroup_value.name",
                "activity.activity_subgroup.name_sentence_case": "activity_subgroup_value.name_sentence_case",
            }

        return mapping

    def _where_stmt(
        self,
        filter_by: dict | None = None,
        filter_operator: FilterOperator = FilterOperator.AND,
        header_query: bool = False,
    ):
        if not filter_by:
            return "", {}

        mapping = self.basemodel_to_cypher_mapping(header_query)

        fields = []
        params = {}

        if "*" in filter_by:
            filter_operator = FilterOperator.OR
            for _, cypher_name in mapping.items():
                if (
                    "op" in filter_by["*"]
                    and filter_by["*"]["op"] == ComparisonOperator.EQUALS.value
                ):
                    operator = "="
                else:
                    operator = "CONTAINS"

                if any(not isinstance(value, str) for value in filter_by["*"]["v"]):
                    operator = "="

                for idx, value in enumerate(filter_by["*"]["v"]):
                    param_variable = f"{cypher_name}_{idx}".replace(".", "_")
                    params[param_variable] = value
                    fields.append(f"{cypher_name} {operator} ${param_variable}")
        else:
            for filter_name, items in filter_by.items():
                if filter_name not in mapping:
                    raise BusinessLogicException(
                        f"Unsupported filtering parameter: {filter_name}. "
                        f"Supported parameters are: {list(self.basemodel_to_cypher_mapping(header_query))}"
                    )

                if "op" in items and items["op"] == ComparisonOperator.EQUALS.value:
                    operator = "="
                else:
                    operator = "CONTAINS"

                if any(not isinstance(value, str) for value in items["v"]):
                    operator = "="

                for idx, value in enumerate(items["v"]):
                    param_variable = f"{mapping[filter_name]}_{idx}".replace(".", "_")
                    params[param_variable] = value
                    fields.append(
                        f"{mapping[filter_name]} {operator} ${param_variable}"
                    )

        return "WHERE " + f" {filter_operator.value} ".join(fields), params

    def _sort_stmt(self, sort_by: dict | None = None):
        if not sort_by:
            return "ORDER BY root.uid DESC"

        mapping = self.basemodel_to_cypher_mapping()

        fields = []
        for sort_field, direction in sort_by.items():
            if sort_field not in mapping:
                raise BusinessLogicException(
                    f"Unsupported sorting parameter: {sort_field}. "
                    f"Supported parameters are: {list(self.basemodel_to_cypher_mapping())}"
                )

            fields.append(f'{mapping[sort_field]} {"ASC" if direction else "DESC"}')

        return "ORDER BY " + ", ".join(fields)

    def _headers_cypher_query(
        self,
        cypher_field_name: str,
        with_status: bool = False,
        where_stmt: str = "",
    ):
        version_where_stmt = ""
        if with_status:
            version_where_stmt += "WHERE ver_rel.status = $status"

        match_stmt = f"""
            MATCH (library:Library)-[:{self.root_class.LIBRARY_REL_LABEL}]->(root:{self.root_class.__label__})
            -[:LATEST]->(value:{self.value_class.__label__})
            CALL {{
                WITH root, value
                MATCH (root)-[ver_rel:HAS_VERSION]->(value)
                {version_where_stmt}
                RETURN ver_rel
                ORDER BY ver_rel.start_date DESC
                LIMIT 1
            }}
        """

        if issubclass(self.root_class, SyntaxInstanceRoot):
            match_stmt += self._only_instances_with_studies()

        if issubclass(self.root_class, SyntaxInstanceRoot | SyntaxPreInstanceRoot):
            stmt, _ = self._instance_template_match_return_stmt()

            match_stmt += stmt

        if hasattr(self.root_class, "has_indication"):
            stmt, _ = self._indication_match_return_stmt()

            match_stmt += stmt

        # pylint: disable=no-member
        if hasattr(self.root_class, "has_type") or (
            hasattr(self, "template_class") and hasattr(self.template_class, "has_type")
        ):
            stmt, _ = self._template_type_match_return_stmt()

            match_stmt += stmt

        if hasattr(self.root_class, "has_category"):
            stmt, _ = self._category_match_return_stmt()

            match_stmt += stmt

        if hasattr(self.root_class, "has_subcategory"):
            stmt, _ = self._subcategory_match_return_stmt()

            match_stmt += stmt

        if hasattr(self.root_class, "has_activity"):
            stmt, _ = self._activity_match_return_stmt()

            match_stmt += stmt

        if hasattr(self.root_class, "has_activity_group"):
            stmt, _ = self._activity_group_match_return_stmt()

            match_stmt += stmt

        if hasattr(self.root_class, "has_activity_subgroup"):
            stmt, _ = self._activity_subgroup_match_return_stmt()

            match_stmt += stmt

        if where_stmt:
            match_stmt += f"WITH * {where_stmt} "

        return_stmt = f"""
            RETURN DISTINCT {cypher_field_name}
            LIMIT $result_count
        """

        return match_stmt, return_stmt

    def _find_cypher_query(
        self,
        with_status: bool = False,
        with_version: bool = False,
        with_pagination: bool = True,
        return_study_count: bool = False,
        where_stmt: str = "",
        sort_by: dict | None = None,
        uid: str | None = None,
        for_audit_trail: bool = False,
    ):
        version_where_stmt = ""
        if with_status:
            version_where_stmt += "WHERE ver_rel.status = $status"
        if with_version:
            if version_where_stmt:
                version_where_stmt += " AND ver_rel.version = $version"
            else:
                version_where_stmt += "WHERE ver_rel.version = $version"

        if for_audit_trail:
            if not with_status:
                version_rel = "ver_rel:HAS_VERSION"
                version_call = ""
            else:
                version_rel = ":HAS_VERSION"
                version_call = f"""
                    CALL {{
                        WITH root, value
                        MATCH (root)-[ver_rel:HAS_VERSION]->(value)
                        {version_where_stmt}
                        RETURN ver_rel
                        ORDER BY ver_rel.start_date DESC
                        LIMIT 1
                    }}
                """
        else:
            version_rel = ":LATEST" if not with_version and not with_status else ""
            version_call = f"""
                CALL {{
                    WITH root, value
                    MATCH (root)-[ver_rel:HAS_VERSION]->(value)
                    {version_where_stmt}
                    RETURN ver_rel
                    ORDER BY ver_rel.start_date DESC
                    LIMIT 1
                }}
            """

        uid_where_stmt = "WHERE root.uid = $uid" if uid else ""

        match_stmt = f"""
            MATCH (library:Library)-[:{self.root_class.LIBRARY_REL_LABEL}]->(root:{self.root_class.__label__})
            -[{version_rel}]->(value:{self.value_class.__label__})
            {uid_where_stmt}
            {version_call}
        """

        if not uid and issubclass(self.root_class, SyntaxInstanceRoot):
            match_stmt += self._only_instances_with_studies()

        if return_study_count and issubclass(self.root_class, SyntaxTemplateRoot):
            match_stmt += f"""
                OPTIONAL MATCH (root)-[:{self.root_class.TEMPLATE_REL_LABEL}]->(:SyntaxInstanceRoot)-->(:SyntaxInstanceValue)
                <--(:StudySelection)<--(:StudyValue)<-[:HAS_VERSION|LATEST_DRAFT|LATEST_FINAL|LATEST_RETIRED]-(sr:StudyRoot)
            """

        if return_study_count and issubclass(self.root_class, SyntaxInstanceRoot):
            match_stmt += """
                OPTIONAL MATCH (value)<--(:StudySelection)<--(:StudyValue)<-[:HAS_VERSION|LATEST_DRAFT|LATEST_FINAL|LATEST_RETIRED]-(sr:StudyRoot)
            """

        instance_template_return = ", null as instance_template"
        indications_return = ", null as indication"
        template_type_return = ", null as template_type"
        categories_return = ", null as categories"
        subcategories_return = ", null as subcategories"
        activities_return = ", null as activities"
        activity_groups_return = ", null as activity_groups"
        activity_subgroups_return = ", null as activity_subgroups"

        if issubclass(self.root_class, SyntaxInstanceRoot | SyntaxPreInstanceRoot):
            stmt, instance_template_return = self._instance_template_match_return_stmt()

            match_stmt += stmt

        if hasattr(self.root_class, "has_indication"):
            stmt, indications_return = self._indication_match_return_stmt()

            match_stmt += stmt

        # pylint: disable=no-member
        if hasattr(self.root_class, "has_type") or (
            hasattr(self, "template_class") and hasattr(self.template_class, "has_type")
        ):
            stmt, template_type_return = self._template_type_match_return_stmt()

            match_stmt += stmt

        if hasattr(self.root_class, "has_category"):
            stmt, categories_return = self._category_match_return_stmt()

            match_stmt += stmt

        if hasattr(self.root_class, "has_subcategory"):
            stmt, subcategories_return = self._subcategory_match_return_stmt()

            match_stmt += stmt

        if hasattr(self.root_class, "has_activity"):
            stmt, activities_return = self._activity_match_return_stmt()

            match_stmt += stmt

        if hasattr(self.root_class, "has_activity_group"):
            stmt, activity_groups_return = self._activity_group_match_return_stmt()

            match_stmt += stmt

        if hasattr(self.root_class, "has_activity_subgroup"):
            (
                stmt,
                activity_subgroups_return,
            ) = self._activity_subgroup_match_return_stmt()

            match_stmt += stmt

        match_stmt += "WITH *, " + (
            "COUNT(DISTINCT sr) as study_count "
            if return_study_count
            and issubclass(self.root_class, SyntaxTemplateRoot | SyntaxInstanceRoot)
            else "0 as study_count "
        )

        if where_stmt:
            match_stmt += f" {where_stmt} "

        return_stmt = f"""
            RETURN
                library,
                root,
                ver_rel,
                value,
                study_count
                {indications_return}
                {categories_return}
                {subcategories_return}
                {activities_return}
                {activity_groups_return}
                {activity_subgroups_return}
                {template_type_return}
                {instance_template_return}
        """

        if not for_audit_trail:
            if not uid:
                return_stmt += f" {self._sort_stmt(sort_by)} "

                if with_pagination:
                    return_stmt += " SKIP $page_number * $page_size LIMIT $page_size "
        else:
            if not uid:
                return_stmt += " ORDER BY ver_rel.start_date DESC "

                if with_pagination:
                    return_stmt += " SKIP $page_number * $page_size LIMIT $page_size "
            else:
                return_stmt += " ORDER BY ver_rel.start_date DESC "

        return match_stmt, return_stmt

    def _only_instances_with_studies(self):
        return f"""
            MATCH (root)-->(:SyntaxInstanceValue)<-[:{self.value_class.STUDY_SELECTION_REL_LABEL}]-(:StudySelection)<--(:StudyValue)<-[:HAS_VERSION|LATEST_DRAFT|LATEST_FINAL|LATEST_RETIRED]-(isr:StudyRoot)
            WITH *, COUNT(isr) as cnt
            WHERE cnt > 0
        """

    def _activity_subgroup_match_return_stmt(self):
        match_stmt = """
            OPTIONAL MATCH (root)-[:HAS_ACTIVITY_SUBGROUP]->(activity_subgroup_root:ActivitySubGroupRoot)-[:LATEST]->(activity_subgroup_value:ActivitySubGroupValue)
        """

        activity_subgroups_return = """,
            collect(DISTINCT {
                uid: activity_subgroup_root.uid,
                name: activity_subgroup_value.name,
                name_sentence_case: activity_subgroup_value.name_sentence_case
            }) as activity_subgroups
        """

        return match_stmt, activity_subgroups_return

    def _activity_group_match_return_stmt(self):
        match_stmt = """
            OPTIONAL MATCH (root)-[:HAS_ACTIVITY_GROUP]->(activity_group_root:ActivityGroupRoot)-[:LATEST]->(activity_group_value:ActivityGroupValue)
        """

        activity_groups_return = """,
            collect(DISTINCT {
                uid: activity_group_root.uid,
                name: activity_group_value.name,
                name_sentence_case: activity_group_value.name_sentence_case
            }) as activity_groups
        """

        return match_stmt, activity_groups_return

    def _activity_match_return_stmt(self):
        match_stmt = """
            OPTIONAL MATCH (root)-[:HAS_ACTIVITY]->(activity_root:ActivityRoot)-[:LATEST]->(activity_value:ActivityValue)
        """

        activities_return = """,
            collect(DISTINCT {
                uid: activity_root.uid,
                name: activity_value.name,
                name_sentence_case: activity_value.name_sentence_case
            }) as activities
        """

        return match_stmt, activities_return

    def _subcategory_match_return_stmt(self):
        match_stmt = """
            OPTIONAL MATCH (root)-[:HAS_SUBCATEGORY]->(subcategory_root:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]->(subcategory_ct_term_name_value:CTTermNameValue)
            OPTIONAL MATCH (subcategory_root:CTTermRoot)-[:HAS_ATTRIBUTES_ROOT]->(:CTTermAttributesRoot)-[:LATEST]->(subcategory_ct_term_attributes_value:CTTermAttributesValue)
        """

        subcategories_return = """,
            collect(DISTINCT {
                term_uid: subcategory_root.uid,
                name: subcategory_ct_term_name_value.name,
                name_sentence_case: subcategory_ct_term_name_value.name_sentence_case,
                code_submission_value: subcategory_ct_term_attributes_value.code_submission_value,
                preferred_term: subcategory_ct_term_attributes_value.preferred_term
            }) as subcategories
        """

        return match_stmt, subcategories_return

    def _category_match_return_stmt(self):
        match_stmt = """
            OPTIONAL MATCH (root)-[:HAS_CATEGORY]->(category_root:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]->(category_ct_term_name_value:CTTermNameValue)
            OPTIONAL MATCH (category_root:CTTermRoot)-[:HAS_ATTRIBUTES_ROOT]->(:CTTermAttributesRoot)-[:LATEST]->(category_ct_term_attributes_value:CTTermAttributesValue)
        """

        categories_return = """,
            collect(DISTINCT {
                term_uid: category_root.uid,
                name: category_ct_term_name_value.name,
                name_sentence_case: category_ct_term_name_value.name_sentence_case,
                code_submission_value: category_ct_term_attributes_value.code_submission_value,
                preferred_term: category_ct_term_attributes_value.preferred_term
            }) as categories
        """

        return match_stmt, categories_return

    def _instance_template_match_return_stmt(self):
        if hasattr(self, "template_class"):
            rel_type = (
                "-[:CREATED_FROM]->"
                if issubclass(self.root_class, SyntaxPreInstanceRoot)
                else f"<-[:{self.root_class.TEMPLATE_REL_LABEL}]-"
            )
            match_stmt = f"""
                CALL {{
                    WITH root, ver_rel
                    OPTIONAL MATCH (root){rel_type}(template_root)-[template_rel:HAS_VERSION]->(template_value)
                    WHERE template_rel.status = "Final" AND datetime(template_rel.start_date) <= datetime(ver_rel.start_date)
                    OPTIONAL MATCH (template_root)<-[:CONTAINS_SYNTAX_TEMPLATE]-(template_library:Library)
                    RETURN template_root, template_value, template_library
                    ORDER BY template_rel.start_date DESC
                    LIMIT 1
                }}
                OPTIONAL MATCH (template_root)-[:HAS_TYPE]->(type_root:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]->(type_ct_term_name_value:CTTermNameValue)
                OPTIONAL MATCH (type_root)-[:HAS_ATTRIBUTES_ROOT]->(:CTTermAttributesRoot)-[:LATEST]->(type_ct_term_attributes_value:CTTermAttributesValue)
            """

            instance_template_return = """,
                {
                    template_uid: template_root.uid,
                    template_sequence_id: template_root.sequence_id,
                    template_name: template_value.name,
                    template_guidance_text: template_value.guidance_text,
                    template_library_name: template_library.name,
                    term_uid: type_root.uid,
                    name: type_ct_term_name_value.name,
                    name_sentence_case: type_ct_term_name_value.name_sentence_case,
                    code_submission_value: type_ct_term_attributes_value.code_submission_value,
                    preferred_term: type_ct_term_attributes_value.preferred_term
                } as instance_template_return
            """

            return match_stmt, instance_template_return

        return "", ", null as instance_template "

    def _indication_match_return_stmt(self):
        match_stmt = """
            OPTIONAL MATCH (root)-[:HAS_INDICATION]->(indication_root:DictionaryTermRoot)-[:LATEST]-(indication_value:DictionaryTermValue)
        """

        indications_return = """,
            collect(DISTINCT {
                term_uid: indication_root.uid,
                name: indication_value.name
            }) as indications
        """
        return match_stmt, indications_return

    def _template_type_match_return_stmt(self):
        if hasattr(self.root_class, "has_type"):
            match_stmt = """
                OPTIONAL MATCH (root)-[:HAS_TYPE]->(type_root:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]->(type_ct_term_name_value:CTTermNameValue)
                OPTIONAL MATCH (type_root)-[:HAS_ATTRIBUTES_ROOT]->(:CTTermAttributesRoot)-[:LATEST]->(type_ct_term_attributes_value:CTTermAttributesValue)
            """

            template_type_return = """,
                {
                    term_uid: type_root.uid,
                    name: type_ct_term_name_value.name,
                    name_sentence_case: type_ct_term_name_value.name_sentence_case,
                    code_submission_value: type_ct_term_attributes_value.code_submission_value,
                    preferred_term: type_ct_term_attributes_value.preferred_term
                } as template_type
            """
        else:
            match_stmt = """
                OPTIONAL MATCH (root)-[:CREATED_FROM]->(template_root)-[:HAS_TYPE]->(type_root:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]->(type_ct_term_name_value:CTTermNameValue)
                OPTIONAL MATCH (type_root)-[:HAS_ATTRIBUTES_ROOT]->(:CTTermAttributesRoot)-[:LATEST]->(type_ct_term_attributes_value:CTTermAttributesValue)
                OPTIONAL MATCH (template_root)-[:LATEST]->(template_value)
            """

            template_type_return = """,
                {
                    term_uid: type_root.uid,
                    name: type_ct_term_name_value.name,
                    name_sentence_case: type_ct_term_name_value.name_sentence_case,
                    code_submission_value: type_ct_term_attributes_value.code_submission_value,
                    preferred_term: type_ct_term_attributes_value.preferred_term
                } as template_type
            """

        return match_stmt, template_type_return

    def _maintain_complex_parameter(self, parameter_config: ComplexParameterTerm):
        complex_value = TemplateParameterComplexValue.nodes.get_or_none(
            name=parameter_config.value
        )
        if complex_value is None:
            root: TemplateParameterComplexRoot = TemplateParameterComplexRoot(
                is_active_parameter=True
            )
            root.save()
            complex_value = TemplateParameterComplexValue(name=parameter_config.value)
            complex_value.save()
            root.latest_final.connect(complex_value)
            root.has_latest_value.connect(complex_value)
            parameter_root = ParameterTemplateRoot.get(uid=parameter_config.uid)
            root.has_complex_value.connect(parameter_root)
            template_root = ParameterTemplateRoot.nodes.get(uid=parameter_config.uid)
            template_parameter = template_root.has_definition.get()
            root.has_parameter_term.connect(template_parameter)
        else:
            root_uid = complex_value.get_root_uid_by_latest()
            root = TemplateParameterComplexRoot.nodes.get(uid=root_uid)
        for i, param in enumerate(parameter_config.parameters):
            param_uid = param.uid
            if isinstance(param, NumericParameterTermVO):
                numeric_value = NumericValue.nodes.get_or_none(name=param.value)
                if not numeric_value:
                    numeric_value_root = NumericValueRoot(
                        uid="NumericValue_" + str(param.value)
                    )
                    numeric_value_root.save()
                    numeric_value = NumericValue(name=param.value)
                    numeric_value.save()
                    numeric_value_root.latest_final.connect(numeric_value, {})
                    numeric_value_root.has_latest_value.connect(numeric_value)
                    numeric_value_root = numeric_value_root.uid
                else:
                    numeric_value_root = numeric_value.get_root_uid_by_latest()
                param_uid = numeric_value_root
            tptr = TemplateParameterTermRoot.nodes.get(uid=param_uid)
            complex_value.uses_parameter.connect(tptr, {"position": i + 1})
        return root.element_id

    def _parse_parameter_terms(
        self, instance_parameters
    ) -> dict[int, list[ParameterTermEntryVO]]:
        # Note that this method is used both by templates for default values and instances for values
        # Hence the checks we have to make on the existence of the set_number property
        parameter_strings = []
        # First, parse results from the database
        for position_parameters in instance_parameters:
            position, param_name, param_terms, _ = position_parameters
            if len(param_terms) == 0:
                # If we find an empty (NA) parameter term, temporary save a none object that will be replaced later
                parameter_strings.append(
                    {
                        "set_number": 0,
                        "position": position,
                        "index": None,
                        "definition": None,
                        "template": None,
                        "parameter_uid": None,
                        "parameter_term": None,
                        "parameter_name": param_name,
                    }
                )

            for parameter in param_terms:
                parameter_strings.append(
                    {
                        "set_number": (
                            parameter["set_number"] if "set_number" in parameter else 0
                        ),
                        "position": parameter["position"],
                        "index": parameter["index"],
                        "parameter_name": parameter["parameter_name"],
                        "parameter_term": parameter["parameter_term"],
                        "parameter_uid": parameter["parameter_uid"],
                        "definition": parameter["definition"],
                        "template": parameter["template"],
                    }
                )

        # Then, start building the nested dictionary to group parameter terms in a list
        data_dict = {}
        # Create the first two levels, like
        # set_number
        # --> position
        for param in parameter_strings:
            if param["set_number"] not in data_dict:
                data_dict[param["set_number"]] = {}
            data_dict[param["set_number"]][param["position"]] = {
                "parameter_name": param["parameter_name"],
                "definition": param["definition"],
                "template": param["template"],
                "parameter_uids": [],
                "conjunction": next(
                    filter(
                        lambda x, param=param: x[0] == param["position"]
                        and (
                            len(x[2]) == 0
                            or (
                                "set_number" in x[2][0]
                                and x[2][0]["set_number"] == param["set_number"]
                            )
                        ),
                        instance_parameters,
                    )
                )[3],
            }

        # Then, unwind to create the third level, like:
        # set_number
        # --> position
        # -----> [parameter_uids]
        for param in parameter_strings:
            data_dict[param["set_number"]][param["position"]]["parameter_uids"].append(
                {
                    "index": param["index"],
                    "parameter_uid": param["parameter_uid"],
                    "parameter_name": param["parameter_name"],
                    "parameter_term": param["parameter_term"],
                }
            )

        # Finally, convert the nested dictionary to a list of ParameterTermEntryVO objects, grouped by value set
        return_dict = {}
        for set_number, term_set in data_dict.items():
            term_set = [x[1] for x in sorted(term_set.items(), key=lambda x: x[0])]
            parameter_list = []
            for item in term_set:
                term_list = []
                if item.get("definition"):
                    tpcr = TemplateParameterComplexRoot.nodes.get(
                        uid=item["parameter_uids"][0]["parameter_uid"]
                    )
                    defr: ParameterTemplateRoot = tpcr.has_complex_value.get()
                    tpcv: TemplateParameterComplexValue = tpcr.latest_final.get()
                    items = tpcv.get_all()
                    cpx_params = []
                    param_terms = []
                    for itemp in items:
                        param_terms.append(
                            {
                                "position": itemp[2],
                                "value": itemp[3],
                                "vv": itemp[4],
                                "item": itemp[1],
                            }
                        )
                    param_terms.sort(key=lambda x: x["position"])
                    for param in param_terms:
                        if param["value"] is not None:
                            simple_template_parameter_term_vo = NumericParameterTermVO(
                                uid=param["item"], value=param["value"]
                            )
                        else:
                            simple_template_parameter_term_vo = SimpleParameterTermVO(
                                uid=param["item"], value=param["vv"]
                            )
                        cpx_params.append(simple_template_parameter_term_vo)
                    parameter_list.append(
                        ComplexParameterTerm(
                            uid=defr.uid,
                            parameter_template=item["template"],
                            parameters=cpx_params,
                        )
                    )
                else:
                    for value in sorted(
                        item["parameter_uids"],
                        key=lambda x: x["index"] or 0,
                    ):
                        if value["parameter_uid"]:
                            simple_parameter_term_vo = (
                                self._parameter_from_repository_values(value)
                            )
                            term_list.append(simple_parameter_term_vo)
                    pve = ParameterTermEntryVO.from_repository_values(
                        parameters=term_list,
                        parameter_name=item["parameter_name"],
                        conjunction=item.get("conjunction", ""),
                    )
                    parameter_list.append(pve)
            return_dict[set_number] = parameter_list
        return return_dict

    def _parameter_from_repository_values(self, value):
        simple_parameter_term_vo = SimpleParameterTermVO.from_repository_values(
            uid=value["parameter_uid"], value=value["parameter_term"]
        )
        return simple_parameter_term_vo

    def get_template_type_uid(self, syntax_node: SyntaxTemplateRoot) -> str:
        """
        Get the UID of the type associated with a given Syntax Template.

        Args:
            syntax_node (SyntaxTemplateRoot): Syntax Template Root to get the type for.

        Returns:
            str: The UID of the type associated with the given Syntax Template.

        Raises:
            NotFoundException: If a Syntax Template does not exist.
        """

        if not syntax_node:
            raise NotFoundException("The requested Syntax Template does not exist.")

        ct_term = syntax_node.has_type.get_or_none()

        return ct_term.uid if ct_term else None

    def _get_indication(self, uid: str) -> DictionaryTermRoot:
        # Finds indication in database based on root node uid
        return DictionaryTermRoot.nodes.get(uid=uid)

    def _get_category(self, uid: str) -> CTTermRoot:
        # Finds category in database based on root node uid
        return CTTermRoot.nodes.get(uid=uid)

    def _get_activity(self, uid: str) -> ActivityRoot:
        # Finds activity in database based on root node uid
        return ActivityRoot.nodes.get(uid=uid)

    def _get_activity_group(self, uid: str) -> ActivityGroupRoot:
        # Finds activity group in database based on root node uid
        return ActivityGroupRoot.nodes.get(uid=uid)

    def _get_activity_subgroup(self, uid: str) -> ActivitySubGroupRoot:
        # Finds activity sub group in database based on root node uid
        return ActivitySubGroupRoot.nodes.get(uid=uid)

    def _get_template_type(self, uid: str) -> CTTermRoot:
        # Finds template type in database based on root node uid
        return CTTermRoot.nodes.get(uid=uid)

    def patch_indications(self, uid: str, indication_uids: list[str]) -> None:
        root = self.root_class.nodes.get(uid=uid)
        root.has_indication.disconnect_all()
        for indication in indication_uids:
            indication = self._get_indication(indication)
            root.has_indication.connect(indication)

    def patch_categories(self, uid: str, category_uids: list[str]) -> None:
        root = self.root_class.nodes.get(uid=uid)
        root.has_category.disconnect_all()
        for category in category_uids:
            category = self._get_category(category)
            root.has_category.connect(category)

    def patch_subcategories(self, uid: str, sub_category_uids: list[str]) -> None:
        root = self.root_class.nodes.get(uid=uid)
        root.has_subcategory.disconnect_all()
        for sub_category in sub_category_uids:
            sub_category = self._get_category(sub_category)
            root.has_subcategory.connect(sub_category)

    def patch_activities(self, uid: str, activity_uids: list[str]) -> None:
        root = self.root_class.nodes.get(uid=uid)
        root.has_activity.disconnect_all()
        for activity in activity_uids:
            activity = self._get_activity(activity)
            root.has_activity.connect(activity)

    def patch_activity_groups(self, uid: str, activity_group_uids: list[str]) -> None:
        root = self.root_class.nodes.get(uid=uid)
        root.has_activity_group.disconnect_all()
        for group in activity_group_uids:
            group = self._get_activity_group(group)
            root.has_activity_group.connect(group)

    def patch_activity_subgroups(
        self, uid: str, activity_subgroup_uids: list[str]
    ) -> None:
        root = self.root_class.nodes.get(uid=uid)
        root.has_activity_subgroup.disconnect_all()
        for group in activity_subgroup_uids:
            sub_group = self._get_activity_subgroup(group)
            root.has_activity_subgroup.connect(sub_group)

    def patch_is_confirmatory_testing(
        self, uid: str, is_confirmatory_testing: bool | None = None
    ) -> None:
        root = self.root_class.nodes.get(uid=uid)
        if is_confirmatory_testing is None and root.is_confirmatory_testing is not None:
            root.is_confirmatory_testing = None
        elif is_confirmatory_testing is not None:
            root.is_confirmatory_testing = is_confirmatory_testing

        self._db_save_node(root)

    def _create(self, item: _AggregateRootType):
        item = super()._create(item)
        root = None
        if item.uid:
            root = self.root_class.nodes.get(uid=item.uid)
            root.sequence_id = item.sequence_id
            self._db_save_node(root)

        return root, item
