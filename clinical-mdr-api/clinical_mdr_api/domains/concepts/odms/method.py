from dataclasses import dataclass
from typing import Callable, List, Optional

from clinical_mdr_api.domains.concepts.concept_base import ConceptVO
from clinical_mdr_api.domains.concepts.odms.description import OdmDescriptionAR
from clinical_mdr_api.domains.concepts.odms.formal_expression import (
    OdmFormalExpressionAR,
)
from clinical_mdr_api.domains.concepts.odms.odm_ar_base import OdmARBase
from clinical_mdr_api.domains.concepts.utils import ENG_LANGUAGE
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)
from clinical_mdr_api.exceptions import BusinessLogicException


@dataclass(frozen=True)
class OdmMethodVO(ConceptVO):
    oid: Optional[str]
    method_type: Optional[str]
    formal_expression_uids: List[str]
    description_uids: List[str]
    alias_uids: List[str]

    @classmethod
    def from_repository_values(
        cls,
        oid: Optional[str],
        name: str,
        method_type: Optional[str],
        formal_expression_uids: List[str],
        description_uids: List[str],
        alias_uids: List[str],
    ) -> "OdmMethodVO":
        return cls(
            oid=oid,
            name=name,
            method_type=method_type,
            formal_expression_uids=formal_expression_uids,
            description_uids=description_uids,
            alias_uids=alias_uids,
            name_sentence_case=None,
            definition=None,
            abbreviation=None,
            is_template_parameter=False,
        )

    def validate(
        self,
        concept_exists_by_callback: Callable[[str, str], bool],
        find_odm_formal_expression_callback: Callable[
            [str], Optional[OdmFormalExpressionAR]
        ],
        find_odm_description_callback: Callable[[str], Optional[OdmDescriptionAR]],
        odm_alias_exists_by_callback: Callable[[str, str, bool], bool],
        previous_name: Optional[str] = None,
        previous_oid: Optional[str] = None,
        previous_formal_expression_uids: Optional[List[str]] = None,
    ) -> None:
        if concept_exists_by_callback("name", self.name) and previous_name != self.name:
            raise BusinessLogicException(
                f"ODM Method with name ({self.name}) already exists."
            )

        if (
            self.oid
            and concept_exists_by_callback("oid", self.oid)
            and previous_oid != self.oid
        ):
            raise BusinessLogicException(
                f"ODM Method with OID ({self.oid}) already exists."
            )

        contexts = set()
        for formal_expression_uid in self.formal_expression_uids:
            formal_expression = find_odm_formal_expression_callback(
                formal_expression_uid
            )
            if not formal_expression:
                raise BusinessLogicException(
                    f"ODM Method tried to connect to non existing ODM Formal Expression identified by uid ({formal_expression_uid})."
                )
            if formal_expression.concept_vo.context in contexts:
                raise BusinessLogicException(
                    f"ODM Method tried to connect to ODM Formal Expressions with same context ({formal_expression.concept_vo.context})."
                )
            contexts.add(formal_expression.concept_vo.context)

            if previous_formal_expression_uids is None:
                continue
            for previous_formal_expression_uid in previous_formal_expression_uids:
                previous_formal_expression = find_odm_formal_expression_callback(
                    previous_formal_expression_uid
                )
                if (
                    formal_expression
                    and previous_formal_expression
                    and formal_expression.concept_vo.context
                    == previous_formal_expression.concept_vo.context
                    and formal_expression.uid != previous_formal_expression.uid
                ):
                    raise BusinessLogicException(
                        f"ODM Method tried to connect to ODM Formal Expressions with same context ({formal_expression.concept_vo.context})."
                    )

        descriptions = []
        for description_uid in self.description_uids:
            desc = find_odm_description_callback(description_uid)
            if not desc:
                raise BusinessLogicException(
                    f"ODM Method tried to connect to non existing ODM Description identified by uid ({description_uid})."
                )
            descriptions.append(desc)

        if not any(
            description.concept_vo.language == ENG_LANGUAGE
            for description in descriptions
        ):
            raise BusinessLogicException("An English ODM Description must be provided.")

        for alias_uid in self.alias_uids:
            if not odm_alias_exists_by_callback("uid", alias_uid, True):
                raise BusinessLogicException(
                    f"ODM Method tried to connect to non existing ODM Alias identified by uid ({alias_uid})."
                )


@dataclass
class OdmMethodAR(OdmARBase):
    _concept_vo: OdmMethodVO

    @property
    def name(self) -> str:
        return self._concept_vo.name

    @property
    def concept_vo(self) -> OdmMethodVO:
        return self._concept_vo

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        concept_vo: OdmMethodVO,
        library: Optional[LibraryVO],
        item_metadata: LibraryItemMetadataVO,
    ) -> "OdmMethodAR":
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
        concept_vo: OdmMethodVO,
        library: LibraryVO,
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
        concept_exists_by_callback: Callable[[str, str], bool] = lambda x, y: True,
        find_odm_formal_expression_callback: Callable[
            [str], Optional[OdmFormalExpressionAR]
        ] = lambda _: None,
        find_odm_description_callback: Callable[
            [str], Optional[OdmDescriptionAR]
        ] = lambda _: None,
        odm_alias_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
    ) -> "OdmMethodAR":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        concept_vo.validate(
            concept_exists_by_callback=concept_exists_by_callback,
            find_odm_formal_expression_callback=find_odm_formal_expression_callback,
            find_odm_description_callback=find_odm_description_callback,
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
        concept_vo: OdmMethodVO,
        concept_exists_by_name_callback: Callable[[str], bool] = lambda _: True,
        concept_exists_by_callback: Callable[[str, str], bool] = lambda x, y: True,
        find_odm_formal_expression_callback: Callable[
            [str], Optional[OdmFormalExpressionAR]
        ] = lambda _: None,
        find_odm_description_callback: Callable[
            [str], Optional[OdmDescriptionAR]
        ] = lambda _: None,
        odm_alias_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
    ) -> None:
        """
        Creates a new draft version for the object.
        """
        concept_vo.validate(
            concept_exists_by_callback=concept_exists_by_callback,
            find_odm_formal_expression_callback=find_odm_formal_expression_callback,
            find_odm_description_callback=find_odm_description_callback,
            odm_alias_exists_by_callback=odm_alias_exists_by_callback,
            previous_name=self.name,
            previous_oid=self._concept_vo.oid,
            previous_formal_expression_uids=self._concept_vo.formal_expression_uids,
        )

        super()._edit_draft(change_description=change_description, author=author)
        self._concept_vo = concept_vo
