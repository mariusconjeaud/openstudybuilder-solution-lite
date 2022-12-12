from neomodel import db

from clinical_mdr_api import exceptions
from clinical_mdr_api.domain.concepts.odms.xml_extension_tag import (
    OdmXmlExtensionTagAR,
    OdmXmlExtensionTagVO,
)
from clinical_mdr_api.domain_repositories.concepts.odms.xml_extension_tag_repository import (
    XmlExtensionTagRepository,
)
from clinical_mdr_api.models.odm_xml_extension_tag import (
    OdmXmlExtensionTag,
    OdmXmlExtensionTagPatchInput,
    OdmXmlExtensionTagPostInput,
    OdmXmlExtensionTagVersion,
)
from clinical_mdr_api.services.odm_generic_service import OdmGenericService


class OdmXmlExtensionTagService(OdmGenericService[OdmXmlExtensionTagAR]):
    aggregate_class = OdmXmlExtensionTagAR
    version_class = OdmXmlExtensionTagVersion
    repository_interface = XmlExtensionTagRepository

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: OdmXmlExtensionTagAR
    ) -> OdmXmlExtensionTag:
        return OdmXmlExtensionTag.from_odm_xml_extension_tag_ar(
            odm_xml_extension_tag_ar=item_ar,
            find_odm_xml_extension_by_uid=self._repos.odm_xml_extension_repository.find_by_uid_2,
            find_odm_xml_extension_attribute_by_uid=self._repos.odm_xml_extension_attribute_repository.find_by_uid_2,
        )

    def _create_aggregate_root(
        self, concept_input: OdmXmlExtensionTagPostInput, library
    ) -> OdmXmlExtensionTagAR:
        return OdmXmlExtensionTagAR.from_input_values(
            author=self.user_initials,
            concept_vo=OdmXmlExtensionTagVO.from_repository_values(
                name=concept_input.name,
                xml_extension_uid=concept_input.xml_extension_uid,
                xml_extension_attribute_uids=[],
            ),
            library=library,
            generate_uid_callback=self.repository.generate_uid,
            odm_xml_extension_exists_by_callback=self._repos.odm_xml_extension_repository.exists_by,
            find_odm_xml_extension_tag_callback=self._repos.odm_xml_extension_tag_repository.find_all,
        )

    def _edit_aggregate(
        self,
        item: OdmXmlExtensionTagAR,
        concept_edit_input: OdmXmlExtensionTagPatchInput,
    ) -> OdmXmlExtensionTagAR:
        item.edit_draft(
            author=self.user_initials,
            change_description=concept_edit_input.change_description,
            concept_vo=OdmXmlExtensionTagVO.from_repository_values(
                name=concept_edit_input.name,
                xml_extension_uid=item.concept_vo.xml_extension_uid,
                xml_extension_attribute_uids=[],
            ),
        )
        return item

    @db.transaction
    def get_active_relationships(self, uid: str):
        if not self._repos.odm_xml_extension_tag_repository.exists_by("uid", uid, True):
            raise exceptions.NotFoundException(
                f"ODM XML Extension Tag identified by uid ({uid}) does not exist."
            )

        return self._repos.odm_xml_extension_tag_repository.get_active_relationships(
            uid, ["belongs_to_xml_extension"]
        )

    def soft_delete(self, uid: str) -> None:
        if not self._repos.odm_xml_extension_tag_repository.exists_by("uid", uid, True):
            raise exceptions.NotFoundException(
                f"ODM XML Extension Tag identified by uid ({uid}) does not exist."
            )

        if self._repos.odm_xml_extension_tag_repository.has_active_relationships(
            uid, ["belongs_to_form", "belongs_to_item_group", "belongs_to_item"]
        ):
            raise exceptions.BusinessLogicException(
                "This ODM XML Extension Tag is in use."
            )

        return super().soft_delete(uid)
