import re
from abc import ABC
from typing import Dict, List, Optional, Union

from clinical_mdr_api.domain_repositories.concepts.odms.form_repository import (
    FormRepository,
)
from clinical_mdr_api.domain_repositories.concepts.odms.item_group_repository import (
    ItemGroupRepository,
)
from clinical_mdr_api.domain_repositories.concepts.odms.item_repository import (
    ItemRepository,
)
from clinical_mdr_api.domains.concepts.odms.form import OdmFormAR
from clinical_mdr_api.domains.concepts.odms.item import OdmItemAR
from clinical_mdr_api.domains.concepts.odms.item_group import OdmItemGroupAR
from clinical_mdr_api.domains.concepts.odms.vendor_attribute import OdmVendorAttributeAR
from clinical_mdr_api.domains.concepts.utils import RelationType, VendorCompatibleType
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.concepts.odms.odm_common_models import (
    OdmVendorRelationPostInput,
    OdmVendorsPostInput,
)
from clinical_mdr_api.services.concepts.concept_generic_service import (
    ConceptGenericService,
    _AggregateRootType,
)


class OdmGenericService(ConceptGenericService[_AggregateRootType], ABC):
    OBJECT_IS_INACTIVE = "The object is inactive"

    def fail_if_non_present_vendor_elements_are_used_by_current_odm_element_attributes(
        self,
        attribute_uids: List[str],
        input_elements: List[OdmVendorRelationPostInput],
    ):
        (
            odm_vendor_attribute_ars,
            _,
        ) = self._repos.odm_vendor_attribute_repository.find_all(
            filter_by={"uid": {"v": attribute_uids, "op": "eq"}}
        )

        odm_vendor_attribute_element_uids = {
            odm_vendor_attribute_ar.concept_vo.vendor_element_uid
            for odm_vendor_attribute_ar in odm_vendor_attribute_ars
        }

        if not odm_vendor_attribute_element_uids.issubset(
            {input_element.uid for input_element in input_elements}
        ):
            raise BusinessLogicException(
                "Cannot remove an ODM Vendor Element whose attributes are connected to this ODM element."
            )

    def fail_if_these_attributes_cannot_be_added(
        self,
        input_attributes: List[OdmVendorRelationPostInput],
        element_uids: Optional[List[str]] = None,
        compatible_type: Optional[VendorCompatibleType] = None,
    ):
        odm_vendor_attribute_ars = self._get_odm_vendor_attributes(input_attributes)
        vendor_attribute_patterns = {
            odm_vendor_attribute_ar.uid: odm_vendor_attribute_ar.concept_vo.value_regex
            for odm_vendor_attribute_ar in odm_vendor_attribute_ars
        }

        self.attribute_values_matches_their_regex(
            input_attributes, vendor_attribute_patterns
        )

        for odm_vendor_attribute_ar in odm_vendor_attribute_ars:
            if odm_vendor_attribute_ar:
                if (
                    element_uids
                    and odm_vendor_attribute_ar.concept_vo.vendor_element_uid
                    not in element_uids
                ):
                    raise BusinessLogicException(
                        f"ODM Vendor Attribute identified by ({odm_vendor_attribute_ar.uid}) cannot not be added as an Vendor Element Attribute."
                    )

                if (
                    not element_uids
                    and not odm_vendor_attribute_ar.concept_vo.vendor_namespace_uid
                ):
                    raise BusinessLogicException(
                        f"ODM Vendor Attribute identified by ({odm_vendor_attribute_ar.uid}) cannot not be added as an Vendor Attribute."
                    )

        self.is_vendor_compatible(odm_vendor_attribute_ars, compatible_type)

    def can_connect_vendor_attributes(
        self, attributes: List[OdmVendorRelationPostInput]
    ):
        errors = []
        for attribute in attributes:
            attr = self._repos.odm_vendor_attribute_repository.find_by_uid_2(
                attribute.uid
            )

            if not attr or not attr.concept_vo.vendor_namespace_uid:
                errors.append(attribute.uid)

        if errors:
            raise BusinessLogicException(
                f"ODM Vendor Attributes with the following UIDs don't exist or aren't connected to an ODM Vendor Namespace. UIDs: {errors}"
            )

        return True

    def attribute_values_matches_their_regex(
        self,
        input_attributes: List[OdmVendorRelationPostInput],
        attribute_patterns: dict,
    ):
        errors = {}
        for input_attribute in input_attributes:
            if (
                input_attribute.value
                and attribute_patterns.get(input_attribute.uid)
                and not bool(
                    re.match(
                        attribute_patterns[input_attribute.uid], input_attribute.value
                    )
                )
            ):
                errors[input_attribute.uid] = attribute_patterns[input_attribute.uid]
        if errors:
            raise BusinessLogicException(
                f"Provided values for following attributes don't match their regex pattern:\n\n{errors}"
            )

        return True

    def get_regex_patterns_of_attributes(
        self, attribute_uids: List[str]
    ) -> Dict[str, Optional[str]]:
        attributes, _ = self._repos.odm_vendor_attribute_repository.find_all(
            filter_by={"uid": {"v": attribute_uids, "op": "eq"}}
        )

        attribute_patterns = {
            attribute.uid: attribute.concept_vo.value_regex for attribute in attributes
        }

        return attribute_patterns

    def is_vendor_compatible(
        self,
        odm_vendor_attributes: Union[
            List[OdmVendorRelationPostInput], List[OdmVendorAttributeAR]
        ],
        compatible_type: Optional[VendorCompatibleType] = None,
    ):
        errors = {}

        if all(
            isinstance(odm_vendor_attribute, OdmVendorRelationPostInput)
            for odm_vendor_attribute in odm_vendor_attributes
        ):
            odm_vendor_attributes = self._get_odm_vendor_attributes(
                odm_vendor_attributes
            )

        for odm_vendor_attribute in odm_vendor_attributes:
            if (
                compatible_type
                and compatible_type.value
                not in odm_vendor_attribute.concept_vo.compatible_types
            ):
                errors[
                    odm_vendor_attribute.uid
                ] = odm_vendor_attribute.concept_vo.compatible_types
        if errors:
            raise BusinessLogicException(
                f"Trying to add non-compatible ODM Vendor:\n\n{errors}"
            )

        return True

    def _get_odm_vendor_attributes(
        self, input_attributes: List[OdmVendorRelationPostInput]
    ):
        return self._repos.odm_vendor_attribute_repository.find_all(
            filter_by={
                "uid": {
                    "v": [input_attribute.uid for input_attribute in input_attributes],
                    "op": "eq",
                }
            }
        )[0]

    def pre_management(
        self,
        uid,
        odm_vendors_post_input: OdmVendorsPostInput,
        odm_ar: Union[OdmFormAR, OdmItemGroupAR, OdmItemAR],
        repo: Union[FormRepository, ItemGroupRepository, ItemRepository],
    ):
        removed_vendor_attribute_uids = set(
            odm_ar.concept_vo.vendor_element_attribute_uids
        ) - {
            element_attribute.uid
            for element_attribute in odm_vendors_post_input.element_attributes
        }
        for removed_vendor_attribute_uid in removed_vendor_attribute_uids:
            repo.remove_relation(
                uid=uid,
                relation_uid=removed_vendor_attribute_uid,
                relationship_type=RelationType.VENDOR_ELEMENT_ATTRIBUTE,
            )

        new_vendor_element_uids = {
            element.uid for element in odm_vendors_post_input.elements
        } - set(odm_ar.concept_vo.vendor_element_uids)
        for element in odm_vendors_post_input.elements:
            if element.uid in new_vendor_element_uids:
                repo.add_relation(
                    uid=uid,
                    relation_uid=element.uid,
                    relationship_type=RelationType.VENDOR_ELEMENT,
                    parameters={
                        "value": element.value,
                    },
                )
