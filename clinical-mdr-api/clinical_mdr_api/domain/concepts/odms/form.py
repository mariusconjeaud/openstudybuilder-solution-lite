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
class OdmFormVO(ConceptVO):
    oid: Optional[str]
    repeating: Optional[str]
    sdtm_version: Optional[str]
    scope_uid: Optional[str]
    description_uids: List[str]
    alias_uids: List[str]
    activity_group_uids: List[str]
    item_group_uids: List[str]
    vendor_attribute_uids: List[str]
    vendor_element_uids: List[str]
    vendor_element_attribute_uids: List[str]

    @classmethod
    def from_repository_values(
        cls,
        oid: Optional[str],
        name: str,
        sdtm_version: Optional[str],
        repeating: Optional[str],
        scope_uid: Optional[str],
        description_uids: List[str],
        alias_uids: List[str],
        activity_group_uids: List[str],
        item_group_uids: List[str],
        vendor_element_uids: List[str],
        vendor_attribute_uids: List[str],
        vendor_element_attribute_uids: List[str],
    ) -> "OdmFormVO":
        return cls(
            oid=oid,
            name=name,
            sdtm_version=sdtm_version,
            repeating=repeating,
            scope_uid=scope_uid,
            description_uids=description_uids,
            alias_uids=alias_uids,
            activity_group_uids=activity_group_uids,
            item_group_uids=item_group_uids,
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
        find_term_callback: Callable[[str], Optional[CTTermAttributesAR]],
        odm_description_exists_by_callback: Callable[[str, str, bool], bool],
        odm_alias_exists_by_callback: Callable[[str, str, bool], bool],
        previous_name: Optional[str] = None,
        previous_oid: Optional[str] = None,
    ) -> None:

        if concept_exists_by_callback("name", self.name) and previous_name != self.name:
            raise BusinessLogicException(
                f"ODM Form with name ({self.name}) already exists."
            )

        if (
            self.oid
            and concept_exists_by_callback("oid", self.oid)
            and previous_oid != self.oid
        ):
            raise BusinessLogicException(
                f"ODM Form with OID ({self.oid}) already exists."
            )

        if self.scope_uid is not None and not find_term_callback(self.scope_uid):
            raise BusinessLogicException(
                f"ODM Form tried to connect to non existing Scope identified by uid ({self.scope_uid})."
            )

        for description_uid in self.description_uids:
            if not odm_description_exists_by_callback("uid", description_uid, True):
                raise BusinessLogicException(
                    f"ODM Form tried to connect to non existing ODM Description identified by uid ({description_uid})."
                )

        for alias_uid in self.alias_uids:
            if not odm_alias_exists_by_callback("uid", alias_uid, True):
                raise BusinessLogicException(
                    f"ODM Form tried to connect to non existing ODM Alias identified by uid ({alias_uid})."
                )


@dataclass
class OdmFormAR(OdmARBase):
    _concept_vo: OdmFormVO

    @property
    def name(self) -> str:
        return self._concept_vo.name

    @property
    def concept_vo(self) -> OdmFormVO:
        return self._concept_vo

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        concept_vo: OdmFormVO,
        library: Optional[LibraryVO],
        item_metadata: LibraryItemMetadataVO,
    ) -> "OdmFormAR":
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
        concept_vo: OdmFormVO,
        library: LibraryVO,
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
        concept_exists_by_callback: Callable[[str, str], bool] = lambda x, y: True,
        find_term_callback: Callable[
            [str], Optional[CTTermAttributesAR]
        ] = lambda _: None,
        odm_description_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        odm_alias_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
    ) -> "OdmFormAR":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        concept_vo.validate(
            concept_exists_by_callback=concept_exists_by_callback,
            find_term_callback=find_term_callback,
            odm_description_exists_by_callback=odm_description_exists_by_callback,
            odm_alias_exists_by_callback=odm_alias_exists_by_callback,
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
        concept_vo: OdmFormVO,
        concept_exists_by_name_callback: Callable[[str], bool] = lambda _: True,
        concept_exists_by_callback: Callable[[str, str], bool] = lambda x, y: True,
        find_term_callback: Callable[
            [str], Optional[CTTermAttributesAR]
        ] = lambda _: None,
        odm_description_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        odm_alias_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
    ) -> None:
        """
        Creates a new draft version for the object.
        """
        concept_vo.validate(
            concept_exists_by_callback=concept_exists_by_callback,
            find_term_callback=find_term_callback,
            odm_description_exists_by_callback=odm_description_exists_by_callback,
            odm_alias_exists_by_callback=odm_alias_exists_by_callback,
            previous_name=self.name,
            previous_oid=self._concept_vo.oid,
        )

        if self._concept_vo != concept_vo:
            super()._edit_draft(change_description=change_description, author=author)
            self._concept_vo = concept_vo


@dataclass(frozen=True)
class OdmFormRefVO:
    uid: str
    name: str
    template_uid: str
    order_number: int
    mandatory: str
    locked: str
    collection_exception_condition_oid: str

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        name: str,
        template_uid: str,
        order_number: int,
        mandatory: bool,
        locked: bool,
        collection_exception_condition_oid: str,
    ) -> "OdmFormRefVO":
        return cls(
            uid=uid,
            name=name,
            template_uid=template_uid,
            order_number=order_number,
            mandatory=booltostr(mandatory),
            locked=booltostr(locked),
            collection_exception_condition_oid=collection_exception_condition_oid,
        )
