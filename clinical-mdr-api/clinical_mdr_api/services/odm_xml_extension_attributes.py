from neomodel import db

from clinical_mdr_api import exceptions
from clinical_mdr_api.domain.concepts.odms.xml_extension_attribute import (
    OdmXmlExtensionAttributeAR,
    OdmXmlExtensionAttributeVO,
)
from clinical_mdr_api.domain_repositories.concepts.odms.xml_extension_attribute_repository import (
    XmlExtensionAttributeRepository,
)
from clinical_mdr_api.models.odm_xml_extension_attribute import (
    OdmXmlExtensionAttribute,
    OdmXmlExtensionAttributePatchInput,
    OdmXmlExtensionAttributePostInput,
    OdmXmlExtensionAttributeVersion,
)
from clinical_mdr_api.services.odm_generic_service import OdmGenericService


class OdmXmlExtensionAttributeService(OdmGenericService[OdmXmlExtensionAttributeAR]):
    aggregate_class = OdmXmlExtensionAttributeAR
    version_class = OdmXmlExtensionAttributeVersion
    repository_interface = XmlExtensionAttributeRepository

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: OdmXmlExtensionAttributeAR
    ) -> OdmXmlExtensionAttribute:
        return OdmXmlExtensionAttribute.from_odm_xml_extension_attribute_ar(
            odm_xml_extension_attribute_ar=item_ar,
            find_odm_xml_extension_by_uid=self._repos.odm_xml_extension_repository.find_by_uid_2,
            find_odm_xml_extension_tag_by_uid=self._repos.odm_xml_extension_tag_repository.find_by_uid_2,
        )

    def _create_aggregate_root(
        self, concept_input: OdmXmlExtensionAttributePostInput, library
    ) -> OdmXmlExtensionAttributeAR:
        return OdmXmlExtensionAttributeAR.from_input_values(
            author=self.user_initials,
            concept_vo=OdmXmlExtensionAttributeVO.from_repository_values(
                name=concept_input.name,
                data_type=concept_input.data_type,
                xml_extension_uid=concept_input.xml_extension_uid,
                xml_extension_tag_uid=concept_input.xml_extension_tag_uid,
            ),
            library=library,
            generate_uid_callback=self.repository.generate_uid,
            find_odm_xml_extension_callback=self._repos.odm_xml_extension_repository.find_by_uid_2,
            find_odm_xml_extension_tag_callback=self._repos.odm_xml_extension_tag_repository.find_by_uid_2,
            find_odm_xml_extension_attribute_callback=self._repos.odm_xml_extension_attribute_repository.find_all,
        )

    def _edit_aggregate(
        self,
        item: OdmXmlExtensionAttributeAR,
        concept_edit_input: OdmXmlExtensionAttributePatchInput,
    ) -> OdmXmlExtensionAttributeAR:
        item.edit_draft(
            author=self.user_initials,
            change_description=concept_edit_input.change_description,
            concept_vo=OdmXmlExtensionAttributeVO.from_repository_values(
                name=concept_edit_input.name,
                data_type=concept_edit_input.data_type,
                xml_extension_uid=item.concept_vo.xml_extension_uid,
                xml_extension_tag_uid=item.concept_vo.xml_extension_tag_uid,
            ),
        )
        return item

    @db.transaction
    def get_active_relationships(self, uid: str):
        if not self._repos.odm_xml_extension_attribute_repository.exists_by(
            "uid", uid, True
        ):
            raise exceptions.NotFoundException(
                f"ODM XML Extension Attribute identified by uid ({uid}) does not exist."
            )

        return (
            self._repos.odm_xml_extension_attribute_repository.get_active_relationships(
                uid, ["belongs_to_xml_extension", "belongs_to_xml_extension_tag"]
            )
        )
