from dataclasses import dataclass
from typing import Callable, List, Optional

from clinical_mdr_api.domain.concepts.concept_base import ConceptVO
from clinical_mdr_api.domain.concepts.odms.odm_ar_base import OdmARBase
from clinical_mdr_api.domain.controlled_terminology.ct_term_attributes import (
    CTTermAttributesAR,
)
from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.utils import booltostr


@dataclass(frozen=True)
class OdmItemGroupVO(ConceptVO):
    oid: Optional[str]
    repeating: Optional[str]
    is_reference_data: Optional[str]
    sas_dataset_name: Optional[str]
    origin: Optional[str]
    purpose: Optional[str]
    comment: Optional[str]
    description_uids: List[str]
    alias_uids: List[str]
    sdtm_domain_uids: List[str]
    activity_subgroup_uids: List[str]
    item_uids: List[str]
    vendor_attribute_uids: List[str]
    vendor_element_uids: List[str]
    vendor_element_attribute_uids: List[str]

    @classmethod
    def from_repository_values(
        cls,
        oid: Optional[str],
        name: str,
        repeating: Optional[str],
        is_reference_data: Optional[str],
        sas_dataset_name: Optional[str],
        origin: Optional[str],
        purpose: Optional[str],
        comment: Optional[str],
        description_uids: List[str],
        alias_uids: List[str],
        sdtm_domain_uids: List[str],
        activity_subgroup_uids: List[str],
        item_uids: List[str],
        vendor_element_uids: List[str],
        vendor_attribute_uids: List[str],
        vendor_element_attribute_uids: List[str],
    ) -> "OdmItemGroupVO":
        return cls(
            oid=oid,
            name=name,
            repeating=repeating,
            is_reference_data=is_reference_data,
            sas_dataset_name=sas_dataset_name,
            origin=origin,
            purpose=purpose,
            comment=comment,
            description_uids=description_uids,
            alias_uids=alias_uids,
            sdtm_domain_uids=sdtm_domain_uids,
            activity_subgroup_uids=activity_subgroup_uids,
            item_uids=item_uids,
            vendor_element_uids=vendor_element_uids,
            vendor_attribute_uids=vendor_attribute_uids,
            vendor_element_attribute_uids=vendor_element_attribute_uids,
            name_sentence_case=None,
            definition=None,
            abbreviation=None,
            is_template_parameter=False,
        )

    def validate(
        self,
        concept_exists_by_callback: Callable[[str, str], bool],
        odm_description_exists_by_callback: Callable[[str, str, bool], bool],
        odm_alias_exists_by_callback: Callable[[str, str, bool], bool],
        find_term_callback: Callable[[str], Optional[CTTermAttributesAR]],
        previous_name: Optional[str] = None,
        previous_oid: Optional[str] = None,
    ) -> None:
        if concept_exists_by_callback("name", self.name) and previous_name != self.name:
            raise BusinessLogicException(
                f"ODM Item Group with name ({self.name}) already exists."
            )

        if (
            self.oid
            and concept_exists_by_callback("oid", self.oid)
            and previous_oid != self.oid
        ):
            raise BusinessLogicException(
                f"ODM Item Group with OID ({self.oid}) already exists."
            )

        for description_uid in self.description_uids:
            if not odm_description_exists_by_callback("uid", description_uid, True):
                raise BusinessLogicException(
                    f"ODM Item Group tried to connect to non existing ODM Description identified by uid ({description_uid})."
                )

        for alias_uid in self.alias_uids:
            if not odm_alias_exists_by_callback("uid", alias_uid, True):
                raise BusinessLogicException(
                    f"ODM Item Group tried to connect to non existing ODM Alias identified by uid ({alias_uid})."
                )

        for sdtm_domain_uid in self.sdtm_domain_uids:
            if not find_term_callback(sdtm_domain_uid):
                raise BusinessLogicException(
                    f"ODM Item Group tried to connect to non existing SDTM Domain identified by uid ({sdtm_domain_uid})."
                )


@dataclass
class OdmItemGroupAR(OdmARBase):
    _concept_vo: OdmItemGroupVO

    @property
    def name(self) -> str:
        return self._concept_vo.name

    @property
    def concept_vo(self) -> OdmItemGroupVO:
        return self._concept_vo

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        concept_vo: OdmItemGroupVO,
        library: Optional[LibraryVO],
        item_metadata: LibraryItemMetadataVO,
    ) -> "OdmItemGroupAR":
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
        concept_vo: OdmItemGroupVO,
        library: LibraryVO,
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
        concept_exists_by_callback: Callable[[str, str], bool] = lambda x, y: True,
        odm_description_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        odm_alias_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        find_term_callback: Callable[
            [str], Optional[CTTermAttributesAR]
        ] = lambda _: None,
    ) -> "OdmItemGroupAR":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        concept_vo.validate(
            concept_exists_by_callback=concept_exists_by_callback,
            odm_description_exists_by_callback=odm_description_exists_by_callback,
            odm_alias_exists_by_callback=odm_alias_exists_by_callback,
            find_term_callback=find_term_callback,
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
        concept_vo: OdmItemGroupVO,
        concept_exists_by_name_callback: Callable[[str], bool] = lambda _: True,
        concept_exists_by_callback: Callable[[str, str], bool] = lambda x, y: True,
        odm_description_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        odm_alias_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        find_term_callback: Callable[
            [str], Optional[CTTermAttributesAR]
        ] = lambda _: None,
    ) -> None:
        """
        Creates a new draft version for the object.
        """
        concept_vo.validate(
            concept_exists_by_callback=concept_exists_by_callback,
            odm_description_exists_by_callback=odm_description_exists_by_callback,
            odm_alias_exists_by_callback=odm_alias_exists_by_callback,
            find_term_callback=find_term_callback,
            previous_name=self.name,
            previous_oid=self._concept_vo.oid,
        )

        if self._concept_vo != concept_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self._concept_vo = concept_vo


@dataclass(frozen=True)
class OdmItemGroupRefVO:
    uid: str
    oid: str
    name: str
    form_uid: str
    order_number: int
    mandatory: str
    collection_exception_condition_oid: Optional[str]
    vendor: dict

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        oid: str,
        name: str,
        form_uid: str,
        order_number: int,
        mandatory: bool,
        vendor: dict,
        collection_exception_condition_oid: Optional[str] = None,
    ) -> "OdmItemGroupRefVO":
        return cls(
            uid=uid,
            oid=oid,
            name=name,
            form_uid=form_uid,
            order_number=order_number,
            mandatory=booltostr(mandatory),
            collection_exception_condition_oid=collection_exception_condition_oid,
            vendor=vendor,
        )
