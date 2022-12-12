from distutils.util import strtobool
from typing import Sequence

from neomodel import db

from clinical_mdr_api import exceptions
from clinical_mdr_api.domain.concepts.odms.item_group import (
    OdmItemGroupAR,
    OdmItemGroupVO,
)
from clinical_mdr_api.domain.concepts.utils import RelationType
from clinical_mdr_api.domain.versioned_object_aggregate import LibraryItemStatus
from clinical_mdr_api.domain_repositories.concepts.odms.item_group_repository import (
    ItemGroupRepository,
)
from clinical_mdr_api.models.odm_common_models import OdmXmlExtensionRelationPostInput
from clinical_mdr_api.models.odm_description import OdmDescriptionBatchPatchInput
from clinical_mdr_api.models.odm_item_group import (
    OdmItemGroup,
    OdmItemGroupActivitySubGroupPostInput,
    OdmItemGroupItemPostInput,
    OdmItemGroupPatchInput,
    OdmItemGroupPostInput,
    OdmItemGroupVersion,
)
from clinical_mdr_api.services._utils import get_input_or_new_value, normalize_string
from clinical_mdr_api.services.odm_descriptions import OdmDescriptionService
from clinical_mdr_api.services.odm_generic_service import OdmGenericService


class OdmItemGroupService(OdmGenericService[OdmItemGroupAR]):
    aggregate_class = OdmItemGroupAR
    version_class = OdmItemGroupVersion
    repository_interface = ItemGroupRepository

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: OdmItemGroupAR
    ) -> OdmItemGroup:
        return OdmItemGroup.from_odm_item_group_ar(
            odm_item_group_ar=item_ar,
            find_odm_description_by_uid=self._repos.odm_description_repository.find_by_uid_2,
            find_odm_alias_by_uid=self._repos.odm_alias_repository.find_by_uid_2,
            find_term_by_uid=self._repos.ct_term_attributes_repository.find_by_uid,
            find_activity_subgroup_by_uid=self._repos.activity_subgroup_repository.find_by_uid_2,
            find_odm_item_by_uid_with_item_group_relation=self._repos.odm_item_repository.find_by_uid_with_item_group_relation,
            find_odm_xml_extension_tag_by_uid_with_odm_element_relation=(
                self._repos.odm_xml_extension_tag_repository.find_by_uid_with_odm_element_relation
            ),
            find_odm_xml_extension_attribute_by_uid_with_odm_element_relation=(
                self._repos.odm_xml_extension_attribute_repository.find_by_uid_with_odm_element_relation
            ),
        )

    def _create_aggregate_root(
        self, concept_input: OdmItemGroupPostInput, library
    ) -> OdmItemGroupAR:
        return OdmItemGroupAR.from_input_values(
            author=self.user_initials,
            concept_vo=OdmItemGroupVO.from_repository_values(
                oid=get_input_or_new_value(concept_input.oid, "G.", concept_input.name),
                name=concept_input.name,
                repeating=strtobool(concept_input.repeating),
                is_reference_data=strtobool(concept_input.is_reference_data)
                if concept_input.is_reference_data
                else None,
                sas_dataset_name=concept_input.sas_dataset_name,
                origin=concept_input.origin,
                purpose=concept_input.purpose,
                comment=concept_input.comment,
                description_uids=concept_input.descriptions,
                alias_uids=concept_input.alias_uids,
                sdtm_domain_uids=concept_input.sdtm_domain_uids,
                activity_subgroup_uids=[],
                item_uids=[],
                xml_extension_tag_uids=[],
                xml_extension_attribute_uids=[],
                xml_extension_tag_attribute_uids=[],
            ),
            library=library,
            generate_uid_callback=self.repository.generate_uid,
            concept_exists_by_callback=self._repos.odm_item_group_repository.exists_by,
            odm_description_exists_by_callback=self._repos.odm_description_repository.exists_by,
            odm_alias_exists_by_callback=self._repos.odm_alias_repository.exists_by,
            find_term_callback=self._repos.ct_term_attributes_repository.find_by_uid,
        )

    def _edit_aggregate(
        self, item: OdmItemGroupAR, concept_edit_input: OdmItemGroupPatchInput
    ) -> OdmItemGroupAR:
        item.edit_draft(
            author=self.user_initials,
            change_description=concept_edit_input.change_description,
            concept_vo=OdmItemGroupVO.from_repository_values(
                oid=concept_edit_input.oid,
                name=concept_edit_input.name,
                repeating=strtobool(concept_edit_input.repeating),
                is_reference_data=strtobool(concept_edit_input.is_reference_data),
                sas_dataset_name=concept_edit_input.sas_dataset_name,
                origin=concept_edit_input.origin,
                purpose=concept_edit_input.purpose,
                comment=concept_edit_input.comment,
                description_uids=concept_edit_input.descriptions,
                alias_uids=concept_edit_input.alias_uids,
                sdtm_domain_uids=concept_edit_input.sdtm_domain_uids,
                activity_subgroup_uids=[],
                item_uids=[],
                xml_extension_tag_uids=[],
                xml_extension_attribute_uids=[],
                xml_extension_tag_attribute_uids=[],
            ),
            concept_exists_by_callback=self._repos.odm_item_group_repository.exists_by,
            odm_description_exists_by_callback=self._repos.odm_description_repository.exists_by,
            odm_alias_exists_by_callback=self._repos.odm_alias_repository.exists_by,
            find_term_callback=self._repos.ct_term_attributes_repository.find_by_uid,
        )
        return item

    @db.transaction
    def create_with_relations(
        self, concept_input: OdmItemGroupPostInput
    ) -> OdmItemGroup:
        description_uids = [
            description
            if isinstance(description, str)
            else OdmDescriptionService()
            .non_transactional_create(concept_input=description)
            .uid
            for description in concept_input.descriptions
        ]

        item_group = self.non_transactional_create(
            concept_input=OdmItemGroupPostInput(
                library=concept_input.library_name,
                oid=get_input_or_new_value(concept_input.oid, "G.", concept_input.name),
                name=concept_input.name,
                repeating=strtobool(concept_input.repeating),
                is_reference_data=strtobool(concept_input.is_reference_data)
                if concept_input.is_reference_data
                else None,
                sas_dataset_name=concept_input.sas_dataset_name,
                origin=concept_input.origin,
                purpose=concept_input.purpose,
                comment=concept_input.comment,
                descriptions=description_uids,
                alias_uids=concept_input.alias_uids,
                sdtm_domain_uids=concept_input.sdtm_domain_uids,
            )
        )

        return self._transform_aggregate_root_to_pydantic_model(
            self._repos.odm_item_group_repository.find_by_uid_2(item_group.uid)
        )

    @db.transaction
    def update_with_relations(
        self, uid: str, concept_edit_input: OdmItemGroupPatchInput
    ) -> OdmItemGroup:
        description_uids = [
            description
            if isinstance(description, str)
            else OdmDescriptionService()
            .non_transactional_edit(uid=description.uid, concept_edit_input=description)
            .uid
            if isinstance(description, OdmDescriptionBatchPatchInput)
            else OdmDescriptionService()
            .non_transactional_create(concept_input=description)
            .uid
            for description in concept_edit_input.descriptions
        ]

        item_group = self.non_transactional_edit(
            uid=uid,
            concept_edit_input=OdmItemGroupPatchInput(
                change_description=concept_edit_input.change_description,
                name=concept_edit_input.name,
                oid=concept_edit_input.oid,
                repeating=concept_edit_input.repeating,
                is_reference_data=concept_edit_input.is_reference_data,
                sas_dataset_name=concept_edit_input.sas_dataset_name,
                origin=concept_edit_input.origin,
                purpose=concept_edit_input.purpose,
                comment=concept_edit_input.comment,
                descriptions=description_uids,
                alias_uids=concept_edit_input.alias_uids,
                sdtm_domain_uids=concept_edit_input.sdtm_domain_uids,
            ),
        )

        return self._transform_aggregate_root_to_pydantic_model(
            self._repos.odm_item_group_repository.find_by_uid_2(item_group.uid)
        )

    @db.transaction
    def add_activity_subgroups(
        self,
        uid: str,
        odm_item_group_activity_subgroup_post_input: Sequence[
            OdmItemGroupActivitySubGroupPostInput
        ],
        override: bool,
    ) -> OdmItemGroup:
        odm_item_group_ar = self._find_by_uid_or_raise_not_found(normalize_string(uid))

        if odm_item_group_ar.item_metadata.status == LibraryItemStatus.RETIRED:
            raise exceptions.BusinessLogicException(self.OBJECT_IS_INACTIVE)

        if override:
            self._repos.odm_item_group_repository.remove_relation(
                uid=uid,
                relation_uid=None,
                relationship_type=RelationType.ACTIVITY_SUB_GROUP,
                disconnect_all=True,
            )

        try:
            for activity_subgroup in odm_item_group_activity_subgroup_post_input:
                self._repos.odm_item_group_repository.add_relation(
                    uid=uid,
                    relation_uid=activity_subgroup.uid,
                    relationship_type=RelationType.ACTIVITY_SUB_GROUP,
                )
        except ValueError as exception:
            raise exceptions.ValidationException(exception.args[0])

        odm_item_group_ar = self._find_by_uid_or_raise_not_found(normalize_string(uid))

        return self._transform_aggregate_root_to_pydantic_model(odm_item_group_ar)

    @db.transaction
    def add_items(
        self,
        uid: str,
        odm_item_group_item_post_input: Sequence[OdmItemGroupItemPostInput],
        override: bool,
    ) -> OdmItemGroup:
        odm_item_group_ar = self._find_by_uid_or_raise_not_found(normalize_string(uid))

        if odm_item_group_ar.item_metadata.status == LibraryItemStatus.RETIRED:
            raise exceptions.BusinessLogicException(self.OBJECT_IS_INACTIVE)

        if override:
            self._repos.odm_item_group_repository.remove_relation(
                uid=uid,
                relation_uid=None,
                relationship_type=RelationType.ITEM,
                disconnect_all=True,
            )

        try:
            for item in odm_item_group_item_post_input:
                self._repos.odm_item_group_repository.add_relation(
                    uid=uid,
                    relation_uid=item.uid,
                    relationship_type=RelationType.ITEM,
                    parameters={
                        "order_number": item.order_number,
                        "mandatory": strtobool(item.mandatory),
                        "data_entry_required": strtobool(item.data_entry_required),
                        "sdv": strtobool(item.sdv),
                        "locked": strtobool(item.locked),
                        "key_sequence": item.key_sequence,
                        "method_oid": item.method_oid,
                        "imputation_method_oid": item.imputation_method_oid,
                        "role": item.role,
                        "role_codelist_oid": item.role_codelist_oid,
                        "collection_exception_condition_oid": item.collection_exception_condition_oid,
                    },
                )
        except ValueError as exception:
            raise exceptions.ValidationException(exception.args[0])

        odm_item_group_ar = self._find_by_uid_or_raise_not_found(normalize_string(uid))

        return self._transform_aggregate_root_to_pydantic_model(odm_item_group_ar)

    @db.transaction
    def add_xml_extension_tags(
        self,
        uid: str,
        odm_xml_extension_relation_post_input: Sequence[
            OdmXmlExtensionRelationPostInput
        ],
        override: bool,
    ) -> OdmItemGroup:
        odm_item_group_ar = self._find_by_uid_or_raise_not_found(normalize_string(uid))

        if odm_item_group_ar.item_metadata.status == LibraryItemStatus.RETIRED:
            raise exceptions.BusinessLogicException(self.OBJECT_IS_INACTIVE)

        if override:
            self.fail_if_non_present_tags_are_used_by_current_odm_element_attributes(
                odm_item_group_ar._concept_vo.xml_extension_tag_attribute_uids,
                odm_xml_extension_relation_post_input,
            )

            self._repos.odm_item_group_repository.remove_relation(
                uid=uid,
                relation_uid=None,
                relationship_type=RelationType.XML_EXTENSION_TAG,
                disconnect_all=True,
            )

        try:
            for xml_extension_tag in odm_xml_extension_relation_post_input:
                self._repos.odm_item_group_repository.add_relation(
                    uid=uid,
                    relation_uid=xml_extension_tag.uid,
                    relationship_type=RelationType.XML_EXTENSION_TAG,
                    parameters={
                        "value": xml_extension_tag.value,
                    },
                )
        except ValueError as exception:
            raise exceptions.ValidationException(exception.args[0])

        odm_item_group_ar = self._find_by_uid_or_raise_not_found(normalize_string(uid))

        return self._transform_aggregate_root_to_pydantic_model(odm_item_group_ar)

    @db.transaction
    def add_xml_extension_attributes(
        self,
        uid: str,
        odm_xml_extension_relation_post_input: Sequence[
            OdmXmlExtensionRelationPostInput
        ],
        override: bool,
    ) -> OdmItemGroup:
        odm_item_group_ar = self._find_by_uid_or_raise_not_found(normalize_string(uid))

        if odm_item_group_ar.item_metadata.status == LibraryItemStatus.RETIRED:
            raise exceptions.BusinessLogicException(self.OBJECT_IS_INACTIVE)

        self.fail_if_these_attributes_cannot_be_added(
            odm_xml_extension_relation_post_input
        )

        if override:
            self._repos.odm_item_group_repository.remove_relation(
                uid=uid,
                relation_uid=None,
                relationship_type=RelationType.XML_EXTENSION_ATTRIBUTE,
                disconnect_all=True,
            )

        try:
            for xml_extension_attribute in odm_xml_extension_relation_post_input:
                self._repos.odm_item_group_repository.add_relation(
                    uid=uid,
                    relation_uid=xml_extension_attribute.uid,
                    relationship_type=RelationType.XML_EXTENSION_ATTRIBUTE,
                    parameters={
                        "value": xml_extension_attribute.value,
                    },
                )
        except ValueError as exception:
            raise exceptions.ValidationException(exception.args[0])

        odm_item_group_ar = self._find_by_uid_or_raise_not_found(normalize_string(uid))

        return self._transform_aggregate_root_to_pydantic_model(odm_item_group_ar)

    @db.transaction
    def add_xml_extension_tag_attributes(
        self,
        uid: str,
        odm_xml_extension_relation_post_input: Sequence[
            OdmXmlExtensionRelationPostInput
        ],
        override: bool,
    ) -> OdmItemGroup:
        odm_item_group_ar = self._find_by_uid_or_raise_not_found(normalize_string(uid))

        if odm_item_group_ar.item_metadata.status == LibraryItemStatus.RETIRED:
            raise exceptions.BusinessLogicException(self.OBJECT_IS_INACTIVE)

        self.fail_if_these_attributes_cannot_be_added(
            odm_xml_extension_relation_post_input,
            odm_item_group_ar.concept_vo.xml_extension_tag_uids,
        )

        if override:
            self._repos.odm_item_group_repository.remove_relation(
                uid=uid,
                relation_uid=None,
                relationship_type=RelationType.XML_EXTENSION_TAG_ATTRIBUTE,
                disconnect_all=True,
            )

        try:
            for xml_extension_tag_attribute in odm_xml_extension_relation_post_input:
                self._repos.odm_item_group_repository.add_relation(
                    uid=uid,
                    relation_uid=xml_extension_tag_attribute.uid,
                    relationship_type=RelationType.XML_EXTENSION_TAG_ATTRIBUTE,
                    parameters={
                        "value": xml_extension_tag_attribute.value,
                    },
                )
        except ValueError as exception:
            raise exceptions.ValidationException(exception.args[0])

        odm_item_group_ar = self._find_by_uid_or_raise_not_found(normalize_string(uid))

        return self._transform_aggregate_root_to_pydantic_model(odm_item_group_ar)

    @db.transaction
    def get_active_relationships(self, uid: str):
        if not self._repos.odm_item_group_repository.exists_by("uid", uid, True):
            raise exceptions.NotFoundException(
                f"ODM Item Group identified by uid ({uid}) does not exist."
            )

        return self._repos.odm_item_group_repository.get_active_relationships(
            uid, ["item_group_ref"]
        )

    @db.transaction
    def get_item_groups_that_belongs_to_form(self):
        return self._repos.odm_item_group_repository.get_if_has_relationship(
            "item_group_ref"
        )
