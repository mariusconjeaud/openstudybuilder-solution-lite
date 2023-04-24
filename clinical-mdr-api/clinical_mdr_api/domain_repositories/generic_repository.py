from dataclasses import dataclass
from typing import Any, Mapping, Optional, Tuple

from cachetools import TTLCache
from neomodel import RelationshipDefinition, RelationshipManager

from clinical_mdr_api import config
from clinical_mdr_api.domain_repositories.models.generic import (
    ClinicalMdrNode,
    VersionRelationship,
    VersionRoot,
)
from clinical_mdr_api.repositories._utils import sb_clear_cache


class EntityNotFoundError(LookupError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


@dataclass(frozen=True)
class RepositoryClosureData:
    not_for_update: bool
    repository: Any
    additional_closure: Any


class RepositoryImpl:
    """
    A repository is responsible for reading/writing data to/from the database.
    Results from a repository should be used to build aggregate root (AR) objects.
    """

    cache_store_item_by_uid = TTLCache(
        maxsize=config.CACHE_MAX_SIZE, ttl=config.CACHE_TTL
    )

    value_class: type
    root_class: type

    @property
    def user_initials(self) -> Optional[str]:
        return self._user_initials

    def __init__(self, user: str = None):
        self._user_initials = user

    def _get_version_relation_keys(
        self, root_node: VersionRoot
    ) -> Tuple[
        RelationshipDefinition,
        RelationshipDefinition,
        RelationshipDefinition,
        RelationshipDefinition,
        RelationshipDefinition,
    ]:
        """
        Returns the keys used in the neomodel definition for the relationship definition.
        By default, all library objects use "has_version", "has_draft", etc...
        But some objects use an override, like MasterModel with "has_master_model_version"

        Args:
            root_node (VersionRoot): Root node for which to return the relationship manager

        Returns:
            The relationships managers for the various versioning relationships.
        """
        return (
            root_node.has_version,
            root_node.has_latest_value,
            root_node.latest_draft,
            root_node.latest_final,
            root_node.latest_retired,
        )

    @sb_clear_cache(caches=["cache_store_item_by_uid"])
    def _db_create_and_link_nodes(
        self,
        root: ClinicalMdrNode,
        value: ClinicalMdrNode,
        rel_properties: Mapping[str, Any],
        save_root: Optional[bool] = True,
    ):
        """
        Creates versioned root and versioned object nodes.
        # TODO - GEneration of uids should be removed (additional service?)
        """
        if save_root:
            self._db_save_node(root)
        self._db_save_node(value)

        (
            has_version,
            has_latest_value,
            latest_draft,
            latest_final,
            _,
        ) = self._get_version_relation_keys(root)
        latest_value = self._db_create_relationship(has_latest_value, value)
        self._db_create_relationship(has_version, value, rel_properties)

        if rel_properties["status"] != "Final":
            latest_draft = self._db_create_relationship(latest_draft, value)
            latest_final = None
        else:
            # if we create an object that is immediately in a final state, we create a LATEST_FINAL relationship.
            latest_draft = None
            latest_final = self._db_create_relationship(latest_final, value)
        return root, value, latest_value, latest_draft, latest_final

    @sb_clear_cache(caches=["cache_store_item_by_uid"])
    def _db_save_node(self, node: ClinicalMdrNode) -> ClinicalMdrNode:
        """
        Saves a Neomodel node object in the graph.
        TODO: optionalty accept multiple nodes and handle in same DB transaction.
        """
        if node is not None:
            node.save()
        return node

    @sb_clear_cache(caches=["cache_store_item_by_uid"])
    def _db_create_relationship(
        self,
        origin: RelationshipManager,
        destination: ClinicalMdrNode,
        parameters: Optional[Mapping[str, Any]] = None,
    ) -> VersionRelationship:
        """
        Creates a relationship of an origin type (e.g.VersionRoot.has_latest) to a destination (VersionValue).
        Parameters of a VersionRelationship must be included.
        """
        if parameters is None:
            parameters = {}

        if parameters:
            return origin.connect(destination, parameters)
        return origin.connect(destination)

    @sb_clear_cache(caches=["cache_store_item_by_uid"])
    def _db_remove_relationship(
        self, relationship: RelationshipManager, value: Optional[ClinicalMdrNode] = None
    ):
        """
        Removes a relationship.
        Example input: {relationship: compound_root.latest_draft,
                        value: compound_value}
        """
        if value is None:
            relationship.disconnect_all()
        else:
            relationship.disconnect(value)

    def generate_uid_callback(self):
        return self.root_class.get_next_free_uid_and_increment_counter()
