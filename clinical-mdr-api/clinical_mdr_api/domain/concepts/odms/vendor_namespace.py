from dataclasses import dataclass
from typing import Callable, List, Optional

from clinical_mdr_api.domain.concepts.concept_base import ConceptVO
from clinical_mdr_api.domain.concepts.odms.odm_ar_base import OdmARBase
from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)
from clinical_mdr_api.exceptions import BusinessLogicException


@dataclass(frozen=True)
class OdmVendorNamespaceVO(ConceptVO):
    name: str
    prefix: str
    url: str
    vendor_element_uids: List[str]
    vendor_attribute_uids: List[str]

    @classmethod
    def from_repository_values(
        cls,
        name: str,
        prefix: str,
        url: str,
        vendor_element_uids: List[str],
        vendor_attribute_uids: List[str],
    ) -> "OdmVendorNamespaceVO":
        return cls(
            name=name,
            prefix=prefix,
            url=url,
            vendor_element_uids=vendor_element_uids,
            vendor_attribute_uids=vendor_attribute_uids,
            name_sentence_case=None,
            definition=None,
            abbreviation=None,
            is_template_parameter=False,
        )

    def validate(
        self,
        concept_exists_by_callback: Callable[[str, str], bool],
        previous_name: Optional[str] = None,
        previous_prefix: Optional[str] = None,
        previous_url: Optional[str] = None,
    ) -> None:
        if concept_exists_by_callback("name", self.name) and previous_name != self.name:
            raise BusinessLogicException(
                f"ODM Vendor Namespace with name ({self.name}) already exists."
            )

        if (
            concept_exists_by_callback("prefix", self.prefix)
            and previous_prefix != self.prefix
        ):
            raise BusinessLogicException(
                f"ODM Vendor Namespace with prefix ({self.prefix}) already exists."
            )

        if concept_exists_by_callback("url", self.url) and previous_url != self.url:
            raise BusinessLogicException(
                f"ODM Vendor Namespace with url ({self.url}) already exists."
            )


@dataclass
class OdmVendorNamespaceAR(OdmARBase):
    _concept_vo: OdmVendorNamespaceVO

    @property
    def name(self) -> str:
        return self._concept_vo.name

    @property
    def concept_vo(self) -> OdmVendorNamespaceVO:
        return self._concept_vo

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        concept_vo: OdmVendorNamespaceVO,
        library: Optional[LibraryVO],
        item_metadata: LibraryItemMetadataVO,
    ) -> "OdmVendorNamespaceAR":
        return cls(
            _uid=uid,
            _concept_vo=concept_vo,
            _library=library,
            _item_metadata=item_metadata,
        )

    @classmethod
    def from_input_values(
        cls,
        author: str,
        concept_vo: OdmVendorNamespaceVO,
        library: LibraryVO,
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
        concept_exists_by_callback: Callable[[str, str], bool] = lambda x, y: True,
    ) -> "OdmVendorNamespaceAR":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        concept_vo.validate(
            concept_exists_by_callback=concept_exists_by_callback,
        )

        return cls(
            _uid=generate_uid_callback(),
            _item_metadata=item_metadata,
            _library=library,
            _concept_vo=concept_vo,
        )

    def edit_draft(
        self,
        author: str,
        change_description: Optional[str],
        concept_vo: OdmVendorNamespaceVO,
        concept_exists_by_name_callback: Callable[[str], bool] = lambda _: True,
        concept_exists_by_callback: Callable[[str, str], bool] = lambda x, y: True,
    ) -> None:
        """
        Creates a new draft version for the object.
        """
        concept_vo.validate(
            concept_exists_by_callback=concept_exists_by_callback,
            previous_name=self.concept_vo.name,
            previous_prefix=self.concept_vo.prefix,
            previous_url=self.concept_vo.url,
        )

        if self._concept_vo != concept_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self._concept_vo = concept_vo
