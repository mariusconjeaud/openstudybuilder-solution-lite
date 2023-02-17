from typing import Dict, List

from clinical_mdr_api.domain.concepts.utils import TargetType
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.ct_codelist_attributes import CTCodelistAttributes
from clinical_mdr_api.models.odm_condition import OdmCondition
from clinical_mdr_api.models.odm_form import OdmForm
from clinical_mdr_api.models.odm_item import OdmItem
from clinical_mdr_api.models.odm_item_group import OdmItemGroup
from clinical_mdr_api.models.unit_definition import UnitDefinitionModel
from clinical_mdr_api.services.ct_codelist_attributes import CTCodelistAttributesService
from clinical_mdr_api.services.ct_term_attributes import CTTermAttributesService
from clinical_mdr_api.services.odm_conditions import OdmConditionService
from clinical_mdr_api.services.odm_forms import OdmFormService
from clinical_mdr_api.services.odm_item_groups import OdmItemGroupService
from clinical_mdr_api.services.odm_items import OdmItemService
from clinical_mdr_api.services.odm_templates import OdmTemplateService
from clinical_mdr_api.services.odm_vendor_attributes import OdmVendorAttributeService
from clinical_mdr_api.services.odm_vendor_elements import OdmVendorElementService
from clinical_mdr_api.services.odm_vendor_namespaces import OdmVendorNamespaceService
from clinical_mdr_api.services.unit_definition import UnitDefinitionService


class OdmDataExtractor:
    target_uid: str
    target_name: str
    status: List[str]

    odm_vendor_namespaces: Dict[str, dict]
    odm_vendor_elements: Dict[str, dict]
    odm_forms: List[OdmForm]
    odm_item_groups: List[OdmItemGroup]
    odm_items: List[OdmItem]
    odm_conditions: List[OdmCondition]
    codelists: List[CTCodelistAttributes]
    ct_terms: List[Dict[str, str]]
    unit_definitions: List[UnitDefinitionModel]

    vendor_namespace_service: OdmVendorNamespaceService
    vendor_element_service: OdmVendorElementService
    vendor_attribute_service: OdmVendorAttributeService
    template_service: OdmTemplateService
    form_service: OdmFormService
    item_group_service: OdmItemGroupService
    item_service: OdmItemService
    condition_service: OdmConditionService
    ct_codelist_attributes_service: CTCodelistAttributesService
    ct_term_attributes_service: CTTermAttributesService
    unit_definition_service: UnitDefinitionService

    def __init__(
        self,
        target_uid: str,
        target_type: TargetType,
        status: List[str],
        unit_definition_service,
    ):
        self.unit_definition_service = unit_definition_service
        self.vendor_namespace_service = OdmVendorNamespaceService()
        self.vendor_element_service = OdmVendorElementService()
        self.vendor_attribute_service = OdmVendorAttributeService()
        self.template_service = OdmTemplateService()
        self.form_service = OdmFormService()
        self.item_group_service = OdmItemGroupService()
        self.item_service = OdmItemService()
        self.condition_service = OdmConditionService()
        self.ct_codelist_attributes_service = CTCodelistAttributesService()
        self.ct_term_attributes_service = CTTermAttributesService()

        self.odm_vendor_namespaces = {}
        self.odm_vendor_elements = {}
        self.ref_odm_vendor_attributes = {}
        self.odm_forms = []
        self.odm_item_groups = []
        self.odm_items = []
        self.odm_conditions = []
        self.codelists = []
        self.ct_terms = []
        self.unit_definitions = []

        self.status = status

        if target_type == TargetType.TEMPLATE:
            template = self.template_service.get_by_uid(target_uid)
            self.target_name = template.name
            self.set_forms_of_target(template)
        elif target_type == TargetType.FORM:
            self.odm_forms.append(self.form_service.get_by_uid(target_uid))
            self.target_name = self.odm_forms[0].name
            self.set_item_groups_of_forms(self.odm_forms)
        elif target_type == TargetType.ITEM_GROUP:
            self.odm_item_groups.append(self.item_group_service.get_by_uid(target_uid))
            self.target_name = self.odm_item_groups[0].name
            self.set_items_of_item_groups(self.odm_item_groups)
        elif target_type == TargetType.ITEM:
            self.odm_items.append(self.item_service.get_by_uid(target_uid))
            self.target_name = self.odm_items[0].name
            self.set_unit_definitions_of_items(self.odm_items)
            self.set_codelists_of_items(self.odm_items)
        else:
            raise BusinessLogicException("Requested target type not supported.")

        self.target_uid = target_uid

        self.set_conditions(self.odm_forms, self.odm_item_groups)
        self.set_vendor_namespaces()
        self.set_vendor_elements()
        self.set_ref_vendor_attributes()

    def set_ref_vendor_attributes(self):
        vendor_attributes = self.vendor_attribute_service.get_all_concepts(
            filter_by={
                "uid": {
                    "v": (
                        {
                            attribute.uid
                            for form in self.odm_forms
                            for item_group in form.item_groups
                            if item_group.vendor
                            for attribute in item_group.vendor.attributes
                        }
                        | {
                            attribute.uid
                            for item_group in self.odm_item_groups
                            for item in item_group.items
                            if item.vendor
                            for attribute in item.vendor.attributes
                        }
                    ),
                    "op": "eq",
                }
            },
            only_specific_status=self.status,
        ).items

        self.ref_odm_vendor_attributes = {
            vendor_attribute.uid: {
                "name": vendor_attribute.name,
                "vendor_namespace": vars(vendor_attribute.vendor_namespace),
            }
            for vendor_attribute in vendor_attributes
            if vendor_attribute.vendor_namespace
        }

    def set_vendor_elements(self):
        vendor_elements = self.vendor_element_service.get_all_concepts(
            filter_by={
                "uid": {
                    "v": (
                        {
                            element.uid
                            for form in self.odm_forms
                            for element in form.vendor_elements
                        }
                        | {
                            element.uid
                            for item_group in self.odm_item_groups
                            for element in item_group.vendor_elements
                        }
                    ),
                    "op": "eq",
                }
            },
            only_specific_status=self.status,
        ).items

        self.odm_vendor_elements = {
            vendor_element.uid: {
                "name": vendor_element.name,
                "vendor_namespace": vars(vendor_element.vendor_namespace),
            }
            for vendor_element in vendor_elements
        }

    def set_vendor_namespaces(self):
        vendor_namespaces = self.vendor_namespace_service.get_all_concepts(
            only_specific_status=self.status
        ).items

        self.odm_vendor_namespaces = {
            vendor_namespace.uid: {
                "name": vendor_namespace.name,
                "prefix": vendor_namespace.prefix,
                "url": vendor_namespace.url,
            }
            for vendor_namespace in vendor_namespaces
        }

    def set_forms_of_target(self, target):
        self.odm_forms = sorted(
            self.form_service.get_all_concepts(
                filter_by={
                    "uid": {
                        "v": [form.uid for form in target.forms],
                        "op": "eq",
                    }
                },
                only_specific_status=self.status,
            ).items,
            key=lambda elm: elm.name,
        )

        self.set_item_groups_of_forms(self.odm_forms)

    def set_item_groups_of_forms(self, forms: List[OdmForm]):
        self.odm_item_groups = sorted(
            self.item_group_service.get_all_concepts(
                filter_by={
                    "uid": {
                        "v": [
                            item_group.uid
                            for form in forms
                            for item_group in form.item_groups
                        ],
                        "op": "eq",
                    }
                },
                only_specific_status=self.status,
            ).items,
            key=lambda elm: elm.name,
        )

        self.set_items_of_item_groups(self.odm_item_groups)

    def set_items_of_item_groups(self, item_groups: List[OdmItemGroup]):
        self.odm_items = sorted(
            self.item_service.get_all_concepts(
                filter_by={
                    "uid": {
                        "v": [
                            item.uid
                            for item_group in item_groups
                            for item in item_group.items
                        ],
                        "op": "eq",
                    }
                },
                only_specific_status=self.status,
            ).items,
            key=lambda elm: elm.name,
        )

        self.set_unit_definitions_of_items(self.odm_items)
        self.set_codelists_of_items(self.odm_items)
        self.set_conditions(self.odm_forms, self.odm_item_groups)

    def set_conditions(self, forms, item_groups):
        oids = [
            item_group.collection_exception_condition_oid
            for form in forms
            for item_group in form.item_groups
        ] + [
            item.collection_exception_condition_oid
            for item_group in item_groups
            for item in item_group.items
        ]

        if oids:
            self.odm_conditions = sorted(
                self.condition_service.get_all_concepts(
                    filter_by={"oid": {"v": oids, "op": "eq"}},
                    only_specific_status=self.status,
                ).items,
                key=lambda elm: elm.name,
            )

    def set_unit_definitions_of_items(self, items: List[OdmItem]):
        self.unit_definitions = sorted(
            self.unit_definition_service.get_all(
                library_name=None,
                filter_by={
                    "uid": {
                        "v": [
                            unit_definition.uid
                            for item in items
                            for unit_definition in item.unit_definitions
                        ],
                        "op": "eq",
                    }
                },
            ).items,
            key=lambda elm: elm.name,
        )

    def set_codelists_of_items(self, items: List[OdmItem]):
        self.codelists = sorted(
            self.ct_codelist_attributes_service.get_all_ct_codelists(
                catalogue_name=None,
                library=None,
                package=None,
                filter_by={
                    "codelist_uid": {
                        "v": [item.codelist.uid for item in items if item.codelist],
                        "op": "eq",
                    }
                },
            ).items,
            key=lambda elm: elm.name,
        )

        self.set_terms_of_codelists(self.codelists)

    def set_terms_of_codelists(self, codelists: List[CTCodelistAttributes]):
        self.ct_terms = sorted(
            self.ct_term_attributes_service.get_term_name_and_attributes_by_codelist_uids(
                [codelist.codelist_uid for codelist in codelists]
            ),
            key=lambda elm: elm["nci_preferred_name"],
        )

    def get_items_by_codelist_uid(self, codelist_uid: str):
        return sorted(
            [
                item
                for item in self.odm_items
                if item.codelist and item.codelist.uid == codelist_uid
            ],
            key=lambda elm: elm.name,
        )
