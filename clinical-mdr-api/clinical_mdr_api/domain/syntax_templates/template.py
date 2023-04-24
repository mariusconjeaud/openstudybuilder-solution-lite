from dataclasses import dataclass
from typing import AbstractSet, Callable, Optional, Sequence

from deprecated.classic import deprecated

from clinical_mdr_api.domain._utils import (
    extract_parameters,
    is_syntax_of_template_name_correct,
    strip_html,
)
from clinical_mdr_api.domain.library.parameter_term import ParameterTermEntryVO
from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryItemAggregateRootBase,
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
    ObjectAction,
    VersioningException,
)


@dataclass(frozen=True)
class TemplateVO:
    """
    Value Object class representing template values
    """

    # template name value
    name: str
    name_plain: Optional[str] = None
    # Optional, default parameter terms
    default_parameter_terms: Optional[Sequence[ParameterTermEntryVO]] = None

    # template guidance text
    guidance_text: Optional[str] = None

    @staticmethod
    def _extract_parameter_names_from_template_string(
        template_string: str,
    ) -> Sequence[str]:
        return extract_parameters(template_string)

    @property
    def parameter_names(self) -> Sequence[str]:
        return self._extract_parameter_names_from_template_string(self.name)

    @classmethod
    def from_input_values_2(
        cls,
        template_name: str,
        parameter_name_exists_callback: Callable[[str], bool],
        default_parameter_terms: Optional[Sequence[ParameterTermEntryVO]] = None,
        template_guidance_text: Optional[str] = None,
    ) -> "TemplateVO":
        if not is_syntax_of_template_name_correct(template_name):
            raise ValueError(f"Template string syntax incorrect: {template_name}")
        result = cls(
            name=template_name,
            name_plain=strip_html(template_name),
            guidance_text=template_guidance_text,
            default_parameter_terms=tuple(default_parameter_terms)
            if default_parameter_terms
            else None,
        )
        for parameter_name in result.parameter_names:
            if not parameter_name_exists_callback(parameter_name):
                raise ValueError(
                    f"Unknown parameter name in template string: {parameter_name}"
                )
        return result

    @classmethod
    def from_repository_values(
        cls,
        template_name: str,
        template_name_plain: str,
        template_guidance_text: Optional[str] = None,
    ) -> "TemplateVO":
        return cls(
            name=template_name,
            name_plain=template_name_plain,
            guidance_text=template_guidance_text,
        )


@dataclass
class InstantiationCountsVO:
    _count_draft: int = 0
    _count_final: int = 0
    _count_retired: int = 0

    @property
    def count_draft(self):
        return self._count_draft

    @property
    def count_final(self):
        return self._count_final

    @property
    def count_retired(self):
        return self._count_retired

    @property
    def count_total(self):
        return self._count_draft + self._count_final + self._count_retired

    @classmethod
    def from_counts(cls, final: int, draft: int, retired: int):
        return cls(_count_draft=draft, _count_final=final, _count_retired=retired)


@dataclass
class TemplateAggregateRootBase(LibraryItemAggregateRootBase):
    """
    A generic class implementing versioning of templates. It will be
    inherited from by other Template AR classes.
    """

    _template: Optional[TemplateVO] = None

    _counts: Optional[InstantiationCountsVO] = None

    _study_count: Optional[int] = None

    @property
    def study_count(self) -> int:
        return self._study_count

    @property
    def name(self) -> str:
        assert self._template is not None
        return self._template.name

    @property
    def name_plain(self) -> str:
        assert self._template is not None
        return self._template.name_plain

    @property
    def guidance_text(self) -> Optional[str]:
        assert self._template is not None
        return self._template.guidance_text

    @property
    def counts(self):
        return self._counts

    @classmethod
    @deprecated
    def from_neomodel(
        cls,
        uid: str,
        template: TemplateVO,
        library: LibraryVO,
        item_metadata: LibraryItemMetadataVO,
    ) -> "TemplateAggregateRootBase":
        return cls.from_repository_values(
            uid=uid,
            template=template,
            library=library,
            item_metadata=item_metadata,
        )

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        template: TemplateVO,
        library: LibraryVO,
        item_metadata: LibraryItemMetadataVO,
        study_count: Optional[int] = None,
        counts: Optional[InstantiationCountsVO] = None,
    ) -> "TemplateAggregateRootBase":
        ar = cls(
            _uid=uid,
            _item_metadata=item_metadata,
            _library=library,
            _template=template,
            _study_count=study_count,
            _counts=counts,
        )
        return ar

    @classmethod
    def from_input_values(
        cls,
        *,
        author: str,
        template: TemplateVO,
        library: LibraryVO,
        template_value_exists_callback: Callable[
            [TemplateVO], bool
        ],  # = (lambda _: False),
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
    ) -> "TemplateAggregateRootBase":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)
        if not library.is_editable:
            raise ValueError(
                f"The library with the name='{library.name}' does not allow to create objects."
            )
        if template_value_exists_callback(template):
            raise ValueError(
                f"Duplicate templates not allowed - template exists: {template.name}"
            )
        ar = cls(
            _uid=generate_uid_callback(),
            _item_metadata=item_metadata,
            _library=library,
            _template=template,
        )

        return ar

    @property
    def template_value(self) -> TemplateVO:
        assert self._template is not None
        return self._template

    def edit_draft(
        self, author: str, change_description: str, template: TemplateVO
    ) -> None:
        """
        Creates a new draft version for the object.
        """
        if self.item_metadata.version >= "1.0" and extract_parameters(
            self.name
        ) != extract_parameters(template.name):
            self._raise_versioning_exception()
        if self._template != template:
            super()._edit_draft(change_description=change_description, author=author)
            self._template = template

    def _raise_versioning_exception(self):
        raise VersioningException(
            "You cannot change number or order of template parameters for a previously approved template."
        )

    def create_new_version(
        self, author: str, change_description: str, template: TemplateVO
    ) -> None:
        """
        Puts object into DRAFT status with relevant changes to version numbers.
        """
        super()._create_new_version(
            change_description=change_description, author=author
        )
        self._template = template

    def get_possible_actions(self) -> AbstractSet[ObjectAction]:
        """
        Returns list of possible actions
        """
        if (
            self._item_metadata.status == LibraryItemStatus.DRAFT
            and self._item_metadata.major_version == 0
        ):
            return {ObjectAction.APPROVE, ObjectAction.EDIT, ObjectAction.DELETE}
        if self._item_metadata.status == LibraryItemStatus.DRAFT:
            return {ObjectAction.APPROVE, ObjectAction.EDIT}
        if self._item_metadata.status == LibraryItemStatus.FINAL:
            return {ObjectAction.NEWVERSION, ObjectAction.INACTIVATE}
        if self._item_metadata.status == LibraryItemStatus.RETIRED:
            return {ObjectAction.REACTIVATE}
        return frozenset()
