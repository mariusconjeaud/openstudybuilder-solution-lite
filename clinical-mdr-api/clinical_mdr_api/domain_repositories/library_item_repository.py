import abc
import copy
from datetime import datetime
from typing import Any, Iterable, Mapping, TypeVar

from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from neomodel import (
    OUTGOING,
    NodeClassNotDefined,
    RelationshipDefinition,
    RelationshipManager,
    Traversal,
    db,
)
from neomodel.exceptions import DoesNotExist

from clinical_mdr_api import config
from clinical_mdr_api.domain_repositories._generic_repository_interface import (
    GenericRepository,
)
from clinical_mdr_api.domain_repositories.generic_repository import RepositoryImpl
from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    ControlledTerminology,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)
from clinical_mdr_api.domains._utils import convert_to_plain
from clinical_mdr_api.domains.syntax_templates.template import InstantiationCountsVO
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemAggregateRootBase,
    LibraryItemMetadataVO,
    LibraryItemStatus,
    VersioningException,
)
from clinical_mdr_api.exceptions import BusinessLogicException, NotFoundException
from clinical_mdr_api.repositories._utils import (
    sb_clear_cache,
    validate_max_skip_clause,
)

_AggregateRootType = TypeVar("_AggregateRootType", bound=LibraryItemAggregateRootBase)
RETRIEVED_READ_ONLY_MARK = object()
MATCH_NODE_BY_ID = "MATCH (node) WHERE elementId(node)=$id RETURN node"


class LibraryItemRepositoryImplBase(
    RepositoryImpl, GenericRepository[_AggregateRootType], abc.ABC
):
    cache_store_item_by_uid = TTLCache(
        maxsize=config.CACHE_MAX_SIZE, ttl=config.CACHE_TTL
    )
    has_library = True

    @abc.abstractmethod
    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        root: VersionRoot,
        library: Library,
        relationship: VersionRelationship,
        value: VersionValue,
        study_count: int = 0,
        counts: InstantiationCountsVO | None = None,
    ) -> _AggregateRootType:
        raise NotImplementedError

    @abc.abstractmethod
    def _maintain_parameters(
        self,
        versioned_object: _AggregateRootType,
        root: VersionRoot,
        value: VersionValue,
    ) -> None:
        raise NotImplementedError

    value_class: type
    root_class: type

    def exists_by(self, property_name: str, value: str, on_root: bool = False) -> bool:
        """
        Checks whether a node exists in the graph database by a given property name and its value.

        Args:
            property_name (str): The name of the property to match.
            value (str): The value of the property to match.
            on_root (bool, optional): A flag indicating whether to search on the root node. Defaults to False.

        Returns:
            bool: True if a node is found by the given property name and value. False otherwise.
        """
        if not on_root:
            query = f"""
                MATCH (or:{self.root_class.__label__})-[:LATEST_FINAL|LATEST_DRAFT|LATEST_RETIRED|LATEST]->(:{self.value_class.__label__} {{{property_name}: ${property_name}}})
                RETURN or
                """
        else:
            query = f"""
                MATCH (or:{self.root_class.__label__} {{{property_name}: ${property_name}}})-[:LATEST_FINAL|LATEST_DRAFT|LATEST_RETIRED|LATEST]->(:{self.value_class.__label__})
                RETURN or
                """

        result, _ = db.cypher_query(query, {property_name: value})
        return len(result) > 0 and len(result[0]) > 0

    def get_uid_by_property_value(self, property_name: str, value: str) -> str | None:
        query = f"""
            MATCH (or:{self.root_class.__label__})-[:LATEST_FINAL|LATEST_DRAFT|LATEST_RETIRED|LATEST]->(:{self.value_class.__label__} {{{property_name}: ${property_name}}})
            RETURN or
            """
        result, _ = db.cypher_query(query, {property_name: value})
        if len(result) > 0 and len(result[0]) > 0:
            return result[0][0].get("uid")
        return None

    def check_exists_by_name(self, name: str) -> bool:
        return self.exists_by("name", name)

    def find_uid_by_name(self, name: str) -> str | None:
        cypher_query = f"""
            MATCH (or:{self.root_class.__label__})-[:LATEST_FINAL|LATEST_DRAFT|LATEST_RETIRED]->(ov:{self.value_class.__label__} {{name: $name }})
            RETURN or.uid
        """
        items, _ = db.cypher_query(cypher_query, {"name": name})
        if len(items) > 0:
            return items[0][0]
        return None

    def get_property_by_uid(self, uid: str, prop: str) -> str | None:
        cypher_query = f"""
            MATCH (or:{self.root_class.__label__} {{uid: $uid }})-[:LATEST_FINAL|LATEST_DRAFT|LATEST_RETIRED]->(ov:{self.value_class.__label__})
            RETURN ov.{prop}
        """
        items, _ = db.cypher_query(cypher_query, {"uid": uid})
        if len(items) > 0:
            return items[0][0]
        return None

    def _is_repository_related_to_ct(self) -> bool:
        return False

    def _lock_object(self, uid: str) -> None:
        if not self._is_repository_related_to_ct():
            itm = self.root_class.nodes.get_or_none(uid=uid)
        else:
            result, _ = db.cypher_query(
                MATCH_NODE_BY_ID,
                {"id": uid},
                resolve_objects=True,
            )
            itm = result[0][0]
        if itm is not None:
            itm.__WRITE_LOCK__ = None
            itm.save()

    @sb_clear_cache(caches=["cache_store_item_by_uid"])
    def _get_or_create_value(
        self, root: VersionRoot, ar: _AggregateRootType
    ) -> VersionValue:
        (
            has_version_rel,
            _,
            latest_draft_rel,
            latest_final_rel,
            latest_retired_rel,
        ) = self._get_version_relation_keys(root)
        for itm in has_version_rel.filter(name=ar.name):
            return itm

        latest_draft = latest_draft_rel.get_or_none()
        if latest_draft and not self._has_data_changed(ar, latest_draft):
            return latest_draft
        latest_final = latest_final_rel.get_or_none()
        if latest_final and not self._has_data_changed(ar, latest_final):
            return latest_final
        latest_retired = latest_retired_rel.get_or_none()
        if latest_retired and not self._has_data_changed(ar, latest_retired):
            return latest_retired

        additional_props = {}

        if hasattr(ar, "name_plain"):
            additional_props["name_plain"] = convert_to_plain(ar.name)

        new_value = self.value_class(name=ar.name, **additional_props)
        self._db_save_node(new_value)
        return new_value

    def _has_data_changed(self, ar: _AggregateRootType, value: VersionValue) -> bool:
        base_comparison = ar.name != value.name
        return base_comparison

    def _is_new_version_necessary(
        self, ar: _AggregateRootType, value: VersionValue
    ) -> bool:
        return self._has_data_changed(ar, value)

    def _update(self, versioned_object: _AggregateRootType):
        """
        Updates the state of the versioned object in the graph.

        First, the properties on the root/value nodes must be updated
        and new value object created if necessary.

        Then, that the version information has changed, new HAS_VERSION
        relationships must be created.
        Additionally, the pointer relationships
        (LATEST_DRAFT, LATEST_FINAL, LATEST) must be removed and added again.
        """
        (
            root,
            value,
            library,
            previous_versioned_object,
        ) = versioned_object.repository_closure_data
        versioning_data = self._library_item_metadata_vo_to_datadict(
            versioned_object.item_metadata
        )

        # condition added because ControlledTerminology items are versioned slightly different than other library items:
        # we have two root nodes - the 'main' root called for instance CTCodelistRoot that contains uid
        # and also contains relationships to nodes called CTCodelistAttributesRoot or CTCodelistNameRoot
        # these two nodes don't contain uids but serves as a roots for versioned relationships
        # Connection to the Library node is attached to the 'main' root not the root that owns versioned relationships
        # this is why we need the following condition
        if self._is_repository_related_to_ct():
            root = root.has_root.single()

        if (
            self.has_library
            and versioned_object.library.name != root.has_library.get().name
        ):
            self._db_remove_relationship(root.has_library)
            try:
                new_library = self._get_library(versioned_object.library.name)
                if not library.is_editable:
                    raise BusinessLogicException(
                        f"The library with the name='{new_library.name}' does not allow to create objects."
                    )
            except DoesNotExist as exc:
                raise NotFoundException(
                    f"The library with the name='{versioned_object.library.name}' could not be found."
                ) from exc
            self._db_create_relationship(root.has_library, library)

        # going back from different treatment of ControlledTerminology items
        if self._is_repository_related_to_ct():
            root, _, _, _ = versioned_object.repository_closure_data

        (
            _,
            has_latest_value_rel,
            latest_draft_rel,
            latest_final_rel,
            latest_retired_rel,
        ) = self._get_version_relation_keys(root)
        is_data_changed = False
        if self._is_new_version_necessary(versioned_object, value):
            # Creating nev value object if necessary
            new_value = self._get_or_create_value(root, versioned_object)

            # recreating latest_value relationship
            self._db_remove_relationship(has_latest_value_rel)
            self._db_create_relationship(has_latest_value_rel, new_value)
            is_data_changed = True
        else:
            new_value = value

        # we update relationships when the data is changed or the versioning data is changed
        if (
            is_data_changed
            or previous_versioned_object.item_metadata != versioned_object.item_metadata
        ):
            # Updating latest_draft, latest_final or latest_retired relationship if necessary
            if versioned_object.item_metadata.status == LibraryItemStatus.DRAFT:
                self._recreate_relationship(
                    root, latest_draft_rel, new_value, versioning_data
                )

            elif versioned_object.item_metadata.status == LibraryItemStatus.FINAL:
                self._recreate_relationship(
                    root, latest_final_rel, new_value, versioning_data
                )

            elif versioned_object.item_metadata.status == LibraryItemStatus.RETIRED:
                self._recreate_relationship(
                    root, latest_retired_rel, new_value, versioning_data
                )

            # close all previous HAS_VERSIONs
            self._close_previous_versions(root, versioning_data)

        # recreating parameters connections
        self._maintain_parameters(versioned_object, root, new_value)

        return versioned_object

    @sb_clear_cache(caches=["cache_store_item_by_uid"])
    def _recreate_relationship(
        self,
        root: VersionRoot,
        relation: VersionRelationship,
        value: VersionValue,
        parameters: Mapping[str, Any],
    ):
        old_value = relation.get_or_none()
        (
            has_version_rel,
            _,
            _,
            _,
            _,
        ) = self._get_version_relation_keys(root)

        if old_value is not None:
            self._db_remove_relationship(relation)
        all_hvs = has_version_rel.all_relationships(value)
        # Set any missing end_date to the new start_date
        for has_version in all_hvs:
            if has_version.end_date is None:
                has_version.end_date = parameters["start_date"]
                has_version.save()
        has_version_rel.connect(value, parameters)
        self._db_create_relationship(relation, value)

    @sb_clear_cache(caches=["cache_store_item_by_uid"])
    def _close_previous_versions(
        self,
        root: VersionRoot,
        parameters: Mapping[str, Any],
    ):
        (
            has_version_rel,
            _,
            _,
            _,
            _,
        ) = self._get_version_relation_keys(root)
        all_values = has_version_rel.all()
        for value in all_values:
            all_rels = has_version_rel.all_relationships(value)
            # Set any missing end_date to the new start_date, for all except the new version
            for rel in all_rels:
                if rel.version != parameters["version"] and rel.end_date is None:
                    rel.end_date = parameters["start_date"]
                    rel.save()

    def _get_library(self, library_name: str) -> Library:
        # Finds library in database based on library name
        return Library.nodes.get(name=library_name)

    def retrieve_audit_trail(
        self, page_number: int = 1, page_size: int = 0, total_count: bool = False
    ) -> tuple[list[_AggregateRootType], int]:
        """
        Retrieves an audit trail of the given node type from the database.

        This method queries the database for the given node type, ordered by their start date in descending order.
        It retrieves a subset of the entries based on the provided page number and page size parameters.
        Optionally, it can also return the total count of audit trail entries.

        Args:
            page_number (int, optional): The page number of the results to retrieve. Each page contains a subset of the audit trail. Defaults to 1.
            page_size (int, optional): The number of results per page. If set to 0, all results will be retrieved. Defaults to 0.
            total_count (bool, optional): Flag indicating whether to include the total count of audit trail entries. Defaults to False.

        Returns:
            tuple[list[_AggregateRootType], int]: A tuple containing a list of retrieved audit trail entries and the total count of entries.
                The audit trail entries are instances of the _AggregateRootType class.
        """
        validate_max_skip_clause(page_number=page_number, page_size=page_size)

        query = f"""
            MATCH (root:{self.root_class.__name__})-[rel:HAS_VERSION]->(value:{self.value_class.__name__})
            RETURN root, rel, value
            ORDER BY rel.start_date DESC
        """

        if page_size:
            query += "SKIP $page_number * $page_size LIMIT $page_size"

        result = db.cypher_query(
            query,
            params={
                "page_number": page_number - 1,
                "page_size": page_size,
            },
            resolve_objects=True,
        )

        aggregates = []

        for root, relationship, value in result[0]:
            ar = self._create_aggregate_root_instance_from_version_root_relationship_and_value(
                root=root,
                library=root.has_library.get_or_none(),
                relationship=relationship,
                value=value,
            )
            ar.repository_closure_data = RETRIEVED_READ_ONLY_MARK
            aggregates.append(ar)

        if total_count:
            count = db.cypher_query(
                f"MATCH (:{self.root_class.__name__})-[rel:HAS_VERSION]->(:{self.value_class.__name__}) RETURN COUNT(rel) as total_count"
            )[0][0][0]
        else:
            count = 0

        return aggregates, count

    def find_all(
        self,
        *,
        status: LibraryItemStatus | None = None,
        library_name: str | None = None,
        return_study_count: bool | None = False,
    ) -> Iterable[_AggregateRootType]:
        """
        GetAll implementation - gets all objects. Ignores versions.
        """
        aggregates = []
        items = []
        if status is None:
            items = self.root_class.nodes.order_by("-uid")
        elif status == LibraryItemStatus.FINAL:
            items = self.root_class.nodes.has(latest_final=True)
        elif status == LibraryItemStatus.DRAFT:
            items = self.root_class.nodes.has(latest_draft=True)
        elif status == LibraryItemStatus.RETIRED:
            items = self.root_class.nodes.has(latest_retired=True)

        for item in items:
            root: VersionRoot = item
            library: Library = root.has_library.get_or_none()
            (
                _,
                has_latest_value_rel,
                latest_draft_rel,
                latest_final_rel,
                latest_retired_rel,
            ) = self._get_version_relation_keys(root)

            if library and library_name is not None and library_name != library.name:
                continue

            if status is None:
                value: VersionValue = has_latest_value_rel.single()
            elif status == LibraryItemStatus.FINAL:
                value: VersionValue = latest_final_rel.single()
            elif status == LibraryItemStatus.DRAFT:
                value: VersionValue = latest_draft_rel.single()
            elif status == LibraryItemStatus.RETIRED:
                value: VersionValue = latest_retired_rel.single()

            relationship: VersionRelationship = self._get_latest_version(root, value)

            ar = self._create_aggregate_root_instance_based_on_return_counts(
                library=library,
                root=root,
                value=value,
                relationship=relationship,
                return_instantiation_counts=False,
                return_study_count=return_study_count,
            )

            ar.repository_closure_data = RETRIEVED_READ_ONLY_MARK
            aggregates.append(ar)
        return aggregates

    def _get_study_count(self, item: VersionValue) -> int:
        return item.get_study_count()

    def _get_latest_version_for_status(
        self, root: VersionRoot, value: VersionValue, status: LibraryItemStatus
    ) -> VersionRelationship:
        (
            has_version_rel,
            _,
            _,
            _,
            _,
        ) = self._get_version_relation_keys(root)

        all_rels = has_version_rel.all_relationships(value)
        rels = [rel for rel in all_rels if rel.status == status.value]
        if len(rels) == 0:
            raise RuntimeError(f"No HAS_VERSION was found with status {status}")
        if len(rels) == 1:
            return rels[0]
        all_versions = [rel.version for rel in rels]
        highest_version = max(
            all_versions,
            key=lambda v: 1000000 * int(v.split(".")[0]) + int(v.split(".")[1]),
        )
        all_latest = [rel for rel in all_rels if rel.version == highest_version]
        return self._find_latest_version_in(all_latest)

    def _get_latest_version(
        self,
        root: VersionRoot,
        value: VersionValue,
        status: LibraryItemStatus | None = None,
    ) -> VersionRelationship:
        (
            has_version_rel,
            _,
            _,
            _,
            _,
        ) = self._get_version_relation_keys(root)
        if status is None:
            all_rels = has_version_rel.all_relationships(value)
            if len(all_rels) == 0:
                raise RuntimeError("No HAS_VERSION relationship was found")
            highest_version = self._get_max_version(all_rels)
            all_latest = [rel for rel in all_rels if rel.version == highest_version]
            return self._find_latest_version_in(all_latest)
        return self._get_latest_version_for_status(root, value, status)

    def _get_max_version(self, relationships):
        all_versions = [rel.version for rel in relationships]
        highest_version = max(
            all_versions,
            key=lambda v: 1000000 * int(v.split(".")[0]) + int(v.split(".")[1]),
        )
        return highest_version

    def _find_latest_version_in(self, relationships):
        if len(relationships) == 1:
            return relationships[0]
        all_without_end = [rel for rel in relationships if rel.end_date is None]
        if len(all_without_end) == 1:
            return all_without_end[0]
        if len(all_without_end) > 1:
            return max(all_without_end, key=lambda d: d.start_date)
        return max(relationships, key=lambda d: d.end_date)

    def _get_item_versions(
        self,
        root: VersionRoot,
    ) -> tuple[
        list[tuple[Mapping, VersionValue, VersionRelationship]],
        VersionRelationship | None,
        VersionRelationship | None,
    ]:
        """
        Following code recreates full versioning information based on
        HAS_VERSION relation. First finds all VersionValue-s related to
        specific root, then recreates data dictionaries based on
        relationships between particular nodes (there is more then one
        relation HAS_VERSION) possible between
        single root and value objects)
        """
        (
            has_version_rel,
            _,
            latest_draft_rel,
            latest_final_rel,
            _,
        ) = self._get_version_relation_keys(root)
        latest_final = None
        latest_draft = None
        latest_draft_object: VersionValue | None = latest_draft_rel.single()
        if latest_draft_object is not None:
            latest_draft = latest_draft_rel.relationship(latest_draft_object)

        latest_final_object: VersionValue | None = latest_final_rel.single()
        if latest_final_object is not None:
            latest_final = latest_final_rel.relationship(latest_final_object)

        managed: list[VersionValue] = []
        versions: list[tuple[Mapping, VersionValue, VersionRelationship]] = []
        traversal = Traversal(
            root,
            root.__label__,
            {
                "node_class": self.value_class,
                "direction": OUTGOING,
                "model": VersionRelationship,
            },
        )
        itm: VersionValue
        for itm in traversal.all():
            assert isinstance(
                itm, (VersionValue, ControlledTerminology)
            )  # PIWQ: juts to check whether I understand what's going here
            if itm in managed:
                continue

            managed.append(itm)
            rels: Iterable[VersionRelationship] = has_version_rel.all_relationships(itm)

            for rel in rels:
                assert isinstance(
                    rel, VersionRelationship
                )  # PIWQ: again to check whether I understand
                version_data = self._get_version_data_from_db(root, itm, rel)
                versions.append(version_data)

        versions.sort(key=lambda x: x[2].start_date, reverse=True)
        return versions, latest_draft, latest_final

    def get_all_versions_2(
        self, uid: str, return_study_count: bool | None = False
    ) -> Iterable[_AggregateRootType]:
        library: Library | None = None
        # condition added because ControlledTerminology items are versioned slightly different than other library items:
        # we have two root nodes - the 'main' root called for instance CTCodelistRoot that contains uid
        # and also contains relationships to nodes called CTCodelistAttributesRoot or CTCodelistNameRoot
        # these two nodes don't contain uids but serves as a roots for versioned relationships
        # Connection to the Library node is attached to the 'main' root not the root that owns versioned relationships
        # this is why we need the following condition
        if not self._is_repository_related_to_ct():
            root: VersionRoot | None = self.root_class.nodes.get_or_none(uid=uid)
            if root is not None:
                if self.has_library:
                    library: Library = root.has_library.get()
                else:
                    library = None
        else:
            # ControlledTerminology version root items don't contain uid - then we have to get object by it's id
            result, _ = db.cypher_query(
                MATCH_NODE_BY_ID,
                {"id": uid},
                resolve_objects=True,
            )
            root = result[0][0]
            if root is not None:
                if self.has_library:
                    library: Library = root.has_root.single().has_library.get()
                else:
                    library = None

        result: list[_AggregateRootType] = []
        if root is not None:
            if self.has_library:
                assert library is not None
            else:
                assert library is None
            all_version_nodes_and_relationships: list[
                tuple[VersionValue, VersionRelationship]
            ]
            all_version_nodes_and_relationships = [
                (_[1], _[2]) for _ in self._get_item_versions(root)[0]
            ]
            if return_study_count:
                result = [
                    self._create_aggregate_root_instance_from_version_root_relationship_and_value(
                        root=root,
                        value=_[0],
                        relationship=_[1],
                        library=library,
                        study_count=self._get_study_count(_[0]),
                    )
                    for _ in all_version_nodes_and_relationships
                ]
            else:
                result = [
                    self._create_aggregate_root_instance_from_version_root_relationship_and_value(
                        root=root, value=_[0], relationship=_[1], library=library
                    )
                    for _ in all_version_nodes_and_relationships
                ]
            for _ in result:
                _.repository_closure_data = RETRIEVED_READ_ONLY_MARK
        return result

    def hashkey_library_item(
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
        """
        Returns a hash key that will be used for mapping objects stored in cache,
        which ultimately determines whether a method invocation is a hit or miss.

        We need to define this custom hashing function with the same signature as the method we wish to cache (find_by_uid_2),
        since the target method contains optional/default parameters.
        If this custom hashkey function is not defined, most invocations of find_by_uid_2 method will be misses.
        """
        return hashkey(
            str(type(self)),
            uid,
            version,
            status,
            at_specific_date,
            for_update,
            return_study_count,
            return_instantiation_counts,
        )

    def _create_aggregate_root_instance_based_on_return_counts(
        self,
        library: Library,
        root: VersionRoot,
        value: VersionValue,
        relationship: VersionRelationship,
        return_instantiation_counts: bool,
        return_study_count: bool,
    ) -> _AggregateRootType:
        if return_instantiation_counts:
            final, draft, retired = self._get_counts(root)
            counts = InstantiationCountsVO.from_counts(
                final=final, draft=draft, retired=retired
            )
        else:
            counts = None

        if return_study_count:
            study_count = self._get_study_count(value)
        else:
            study_count = 0

        return self._create_aggregate_root_instance_from_version_root_relationship_and_value(
            root=root,
            library=library,
            relationship=relationship,
            value=value,
            counts=counts,
            study_count=study_count,
        )

    def _get_version_active_at_date_time(
        self, has_version_rel: RelationshipDefinition, at_specific_date: datetime
    ) -> tuple[VersionValue | None, VersionRelationship | None]:
        matching_values: list[VersionValue] = has_version_rel.match(
            start_date__lte=at_specific_date
        )
        latest_matching_relationship: VersionRelationship | None = None
        latest_matching_value: VersionValue | None = None
        for matching_value in matching_values:
            relationships: list[
                VersionRelationship
            ] = has_version_rel.all_relationships(matching_value)
            for relationship in relationships:
                if (
                    latest_matching_relationship is None
                    or latest_matching_relationship.start_date < relationship.start_date
                ):
                    latest_matching_relationship = relationship
                    latest_matching_value = matching_value
        return latest_matching_value, latest_matching_relationship

    @cached(cache=cache_store_item_by_uid, key=hashkey_library_item)
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
    ) -> _AggregateRootType | None:
        if for_update and (
            version is not None or status is not None or at_specific_date is not None
        ):
            raise NotImplementedError(
                "Retrieval for update supported only for latest version."
            )

        if for_update:
            self._lock_object(uid)

        root, library = self._get_root_and_library(uid)
        if not root:
            return None

        value: VersionValue | None
        relationship: VersionRelationship | None

        (
            has_version_rel,
            has_latest_value_rel,
            latest_draft_rel,
            latest_final_rel,
            latest_retired_rel,
        ) = self._get_version_relation_keys(root)

        result: _AggregateRootType | None = None

        if version is None:
            if status is None:
                if at_specific_date is None:
                    # Find the latest version (regardless of status)
                    value = has_latest_value_rel.single()
                    relationship = self._get_latest_version(root, value)
                else:
                    # Find the latest version (regardless of status) that exists at the specified date
                    value, relationship = self._get_version_active_at_date_time(
                        has_version_rel, at_specific_date
                    )
            else:
                # Find the latest version with the specified status
                value, relationship = self._get_latest_value_with_status(
                    root,
                    status,
                    has_version_rel,
                    latest_draft_rel,
                    latest_final_rel,
                    latest_retired_rel,
                )
        else:
            # Find the version with the specified version number, and optionally status
            value, relationship = self._get_value_with_version_number(
                root, version, status
            )

        if value and relationship:
            result = self._create_aggregate_root_instance_based_on_return_counts(
                library=library,
                root=root,
                value=value,
                relationship=relationship,
                return_instantiation_counts=return_instantiation_counts,
                return_study_count=return_study_count,
            )
            if for_update:
                result.repository_closure_data = (
                    root,
                    value,
                    library,
                    copy.deepcopy(result),
                )
            else:
                result.repository_closure_data = RETRIEVED_READ_ONLY_MARK
        return result

    def _get_value_with_version_number(
        self, root: VersionRoot, version: str, status: LibraryItemStatus | None = None
    ) -> tuple[VersionValue | None, VersionRelationship | None]:
        matching_value = root.get_value_for_version(version)
        active_relationship: VersionRelationship | None = None
        active_value: VersionValue | None = None
        if matching_value is not None:
            active_relationship = root.get_relation_for_version(version)
            active_value = matching_value

        if active_relationship is None:
            return None, None

        if status is not None and active_relationship.status != status.value:
            return None, None

        return active_value, active_relationship

    def _get_latest_value_with_status(
        self,
        root: VersionRoot,
        status: LibraryItemStatus,
        has_version_rel: RelationshipManager,
        latest_draft_rel: RelationshipManager,
        latest_final_rel: RelationshipManager,
        latest_retired_rel: RelationshipManager,
    ) -> tuple[VersionValue | None, VersionRelationship | None]:
        relationship: VersionRelationship | None = None
        value: VersionValue | None = None

        relationship_manager_to_use: RelationshipManager = latest_retired_rel
        if status == LibraryItemStatus.FINAL:
            relationship_manager_to_use = latest_final_rel
        elif status == LibraryItemStatus.DRAFT:
            relationship_manager_to_use = latest_draft_rel
        value = relationship_manager_to_use.get_or_none()
        if value is None:
            value = has_version_rel.match(status=status.value).all()
            if not value:
                return None, None
            end_dates = {
                has_version_rel.relationship(node).end_date: node for node in value
            }
            last_date = max(end_dates.keys())
            value = end_dates[last_date]

        relationship = self._get_latest_version_for_status(root, value, status)
        return value, relationship

    def _get_root_and_library(
        self, uid: str
    ) -> tuple[VersionRoot | None, Library | None]:
        if not self._is_repository_related_to_ct():
            try:
                root: VersionRoot | None = self.root_class.nodes.get_or_none(uid=uid)
            except NodeClassNotDefined as exc:
                raise VersioningException(
                    "Object labels were changed - likely the object was deleted in a concurrent transaction."
                ) from exc
            if root is None:
                return None, None
            if self.has_library:
                library: Library = root.has_library.get()
            else:
                library = None
        else:
            result, _ = db.cypher_query(
                MATCH_NODE_BY_ID,
                {"id": uid},
                resolve_objects=True,
            )
            root = result[0][0]
            if root is None:
                return None, None
            ct_root = root.has_root.single()
            if self.has_library:
                library: Library = ct_root.has_library.get()
            else:
                library = None
        return root, library

    def _get_counts(self, item: VersionRoot) -> tuple[int, int, int]:
        finals: int
        drafts: int
        retired: int
        finals, drafts, retired = item.get_instantiations_count()
        return (finals, drafts, retired)

    def _get_version_data_from_db(
        self,
        item: VersionRoot | ControlledTerminology,
        value: VersionValue | ControlledTerminology,
        relation: VersionRelationship,
    ) -> tuple[Mapping, VersionValue, VersionRelationship]:
        if not self.has_library:
            library = None
        elif not self._is_repository_related_to_ct():
            library: Library = item.has_library.get()
        else:
            library: Library = item.has_root.single().has_library.get()
        data = value.to_dict()
        rdata = data.copy()
        rdata.update(relation.to_dict())
        if library is not None:
            rdata["library_name"] = library.name
            rdata["library_is_editable"] = library.is_editable

        return rdata, value, relation

    def _library_item_metadata_vo_to_datadict(
        self, item_metadata: LibraryItemMetadataVO
    ) -> Mapping[str, Any]:
        # if the repository knows who is logged in, domain information will be ignored
        user_initials = item_metadata.user_initials
        return {
            "user_initials": user_initials,
            "change_description": item_metadata.change_description,
            "version": item_metadata.version,
            "status": item_metadata.status.value,
            "start_date": item_metadata.start_date,
            "end_date": item_metadata.end_date,
        }

    def _create(self, item: _AggregateRootType) -> _AggregateRootType:
        """
        Creates new VersionedObject AR, checks possibility based on
        library setting, then creates database representation,
        creates TemplateParameters database objects, recreates AR based
        on created database model and returns created AR.
        Saving into database is necessary due to uid creation process that
        require saving object to database.
        """
        relation_data: LibraryItemMetadataVO = item.item_metadata
        root = self.root_class(uid=item.uid)

        self._db_save_node(root)

        value = self._get_or_create_value(root=root, ar=item)

        library = self._get_library(item.library.name)

        (
            root,
            value,
            _,
            _,
            _,
        ) = self._db_create_and_link_nodes(
            root, value, self._library_item_metadata_vo_to_datadict(relation_data)
        )

        # Connect root node to library node
        root.has_library.connect(library)

        self._maintain_parameters(item, root, value)

        return item

    @staticmethod
    def _library_item_metadata_vo_from_relation(
        relationship: VersionRelationship,
    ) -> LibraryItemMetadataVO:
        major, minor = relationship.version.split(".")
        return LibraryItemMetadataVO.from_repository_values(
            change_description=relationship.change_description,
            status=LibraryItemStatus(relationship.status),
            author=relationship.user_initials,
            start_date=relationship.start_date,
            end_date=relationship.end_date,
            major_version=int(major),
            minor_version=int(minor),
        )

    @sb_clear_cache(caches=["cache_store_item_by_uid"])
    def save(self, item: _AggregateRootType) -> None:
        if item.repository_closure_data is RETRIEVED_READ_ONLY_MARK:
            raise NotImplementedError(
                "Only instances which were retrieved for update can be saved by the repository."
            )
        if item.repository_closure_data is not None and not item.is_deleted:
            self._update(item)
        elif item.is_deleted:
            assert item.uid is not None
            self._soft_delete(item.uid)
        else:
            self._create(item)

    def _soft_delete(self, uid: str) -> None:
        label = self.root_class.__label__
        db.cypher_query(
            f"""
            MATCH (otr:{label} {{uid: $uid}})-[latest_draft:LATEST_DRAFT]->(otv)
            WHERE NOT (otr)-[:LATEST_FINAL|HAS_VERSION {{version:'Final'}}]->()
            SET otr:Deleted{label}
            WITH otr
            REMOVE otr:{label}
            WITH otr
            MATCH (otr)-[v:HAS_VERSION]->()
            WHERE v.end_date IS NULL
            SET v.end_date = datetime(apoc.date.toISO8601(datetime().epochSeconds, 's'))
            """,
            {"uid": uid},
        )

    def check_exists_final_version(self, uid: str) -> bool:
        root_node = self.root_class.nodes.get_or_none(uid=uid)
        if root_node is not None:
            return root_node.latest_final.get_or_none() is not None
        return False

    def close(self) -> None:
        # Our repository guidelines state that repos should have a close method
        # But nothing needs to be done in this one
        pass

    def _get_uid_or_none(self, node):
        return node.uid if node is not None else None
