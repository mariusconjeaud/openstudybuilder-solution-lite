import datetime
from dataclasses import dataclass
from functools import reduce
from operator import add
from typing import AbstractSet, Callable, Optional, Sequence

from clinical_mdr_api.domains._utils import (
    convert_to_plain,
    extract_parameters,
    strip_html,
)
from clinical_mdr_api.domains.libraries.parameter_term import ParameterTermEntryVO
from clinical_mdr_api.domains.syntax_templates.template import TemplateVO
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemAggregateRootBase,
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
    ObjectAction,
)


@dataclass(frozen=True)
class ParametrizedTemplateVO:
    """
    Object representing template with proper parameter setting.
    Allows for creation of proper object name
    """

    template_name: str
    template_uid: str
    template_sequence_id: Optional[str]
    parameter_terms: Sequence[ParameterTermEntryVO]

    @classmethod
    def from_repository_values(
        cls,
        *,
        template_name: str,
        template_uid: str,
        template_sequence_id: str,
        parameter_terms: Sequence[ParameterTermEntryVO],
    ) -> "ParametrizedTemplateVO":
        """
        Creates object based on repository values
        """
        return cls(
            template_uid=template_uid,
            template_sequence_id=template_sequence_id,
            template_name=template_name,
            parameter_terms=tuple(parameter_terms),
        )

    @classmethod
    def from_input_values_2(
        cls,
        *,
        template_uid: str,
        template_sequence_id: str,
        parameter_terms: Sequence[ParameterTermEntryVO],
        get_final_template_vo_by_template_uid_callback: Callable[
            [str], Optional[TemplateVO]
        ],
    ) -> "ParametrizedTemplateVO":
        """
        Creates object based on external input
        """
        template = get_final_template_vo_by_template_uid_callback(template_uid)

        if template is None:
            raise ValueError(
                f"The template with uid '{template_uid}' was not found. Make sure that there is a latest 'Final' version."
            )

        return cls(
            template_name=template.name,
            template_uid=template_uid,
            template_sequence_id=template_sequence_id,
            parameter_terms=tuple(parameter_terms),
        )

    @classmethod
    def from_name_and_parameter_terms(
        cls,
        name: str,
        template_uid: str,
        parameter_terms: Sequence[ParameterTermEntryVO],
        template_sequence_id: Optional[str] = None,
    ) -> "ParametrizedTemplateVO":
        return cls(
            template_name=name,
            template_uid=template_uid,
            template_sequence_id=template_sequence_id,
            parameter_terms=parameter_terms,
        )

    @staticmethod
    def _create_name_from_template(
        template_name: str, parameter_terms: Sequence[ParameterTermEntryVO]
    ) -> str:
        """
        Calculates current name based on template name and current list of parameters
        """
        name = template_name
        template_parameters = extract_parameters(template_name)
        if parameter_terms is not None:
            for i, param in enumerate(parameter_terms):
                values = param.parameters
                conjunction = param.conjunction
                if len(values) == 0:
                    # If no values are selected, the template will be filled in without a name.
                    combined_name = ""
                elif len(values) == 1:
                    # if only one value is present (c.q. no conjunctions) we just use this value.
                    combined_name = values[0].value
                else:
                    # Use a Python reduce function to combine the values array and the conjunctions array into a string.
                    # We use comma's for the first few items, and the specified conjuction word between the last two.
                    combined_name = reduce(
                        add,
                        [
                            str(values[x].value)
                            + ParametrizedTemplateVO.generate_template_value_seperator(
                                template_name,
                                parameter_terms,
                                template_parameters[i],
                                i,
                                values,
                                x,
                                conjunction,
                            )
                            for x in range(len(values) - 1)
                        ],
                    ) + str(values[len(values) - 1].value)
                name = name.replace(
                    "[" + template_parameters[i] + "]", "[" + combined_name + "]", 1
                )

            # Clean up extra spacing, unneeded brackets, etc.
            name = ParametrizedTemplateVO.clean_instantiation_name(name)
        return name

    @staticmethod
    def clean_instantiation_name(name):
        # Filter out unneeded brackets, double spaces, and extra spacing around the string.
        replacement_rules = {
            "([])": "[]",
            "[NA]": "[]",
            ",,": ",",
            "  ": " ",
            "[] []": "[][]",
            "[] ([": "[]([",
            "[) []": "])[]",
            "] and []": "][]",
            "[] and [": "[][",
            "], []": "][]",
            "[], [": "[][",
            "] or []": "][]",
            "[] or [": "[][",
            "] []": "][]",
            "[] [": "[][",
            "()": "",
            "(,)": "",
        }
        for original, replacement in replacement_rules.items():
            while original in name:
                name = name.replace(original, replacement)
        name = name.strip()
        return name

    @staticmethod
    def generate_template_value_seperator(
        template,
        parameter_terms,
        parameter_name,
        template_index,
        values,
        index,
        conjunction,
    ) -> str:
        # We check if there's a 'joined' parameter term following the current one.
        # This, for example, ensure that we generate:
        # "To investigate [A,B,C] and [D]"
        # instead of:
        # "To investigate [A,B and C] and [D]".
        text_after_parameter = template.split("[" + parameter_name + "]")[1]
        next_parameter_has_term = (
            template_index < len(parameter_terms) - 1
            and len(parameter_terms[template_index + 1].parameters) > 0
        )
        has_joined_parameter_term = (
            next_parameter_has_term
            and text_after_parameter.strip().startswith(conjunction)
        )

        if index < (len(values) - 2) or has_joined_parameter_term:
            return ", "
        return " " + conjunction + " "

    @property
    def template_name_plain(self) -> str:
        return strip_html(self.template_name)

    @property
    def expanded_template_value(self) -> str:
        return self._create_name_from_template(
            template_name=self.template_name, parameter_terms=self.parameter_terms
        )

    @property
    def expanded_plain_template_value(self) -> str:
        name = self._create_name_from_template(
            template_name=self.template_name,
            parameter_terms=self.parameter_terms,
        )
        return convert_to_plain(name)


@dataclass
class ParametrizedTemplateARBase(LibraryItemAggregateRootBase):
    """
    Aggregate root supporting template derived object with proper parametrization

    """

    CASCADING_UPDATE_LABEL = "Cascading update triggered by template update uid: '{}'"  # TODO: put reference with uid
    # inheritance from class with default values

    _template: ParametrizedTemplateVO

    _sequence_id: Optional[str] = None

    _study_count: int = 0

    @property
    def sequence_id(self) -> str:
        return self._sequence_id

    @sequence_id.setter
    def sequence_id(self, sequence_id: Optional[str]) -> None:
        self.__set_sequence_id(sequence_id)

    # Setter for supporting sequence_id creation
    def __set_sequence_id(self, sequence_id: Optional[str]) -> None:
        self.__raise_error_if_deleted()
        if self._sequence_id is None:
            self._sequence_id = sequence_id
        else:
            raise TypeError("Cannot modify existing sequence_id.")

    @property
    def study_count(self) -> int:
        return self._study_count

    @classmethod
    def _from_repository_values(
        cls,
        *,
        library: LibraryVO,
        uid: str,
        item_metadata: LibraryItemMetadataVO,
        sequence_id: Optional[str] = None,
        study_count: int = 0,
        **kwargs,
    ) -> "ParametrizedTemplateARBase":
        # noinspection PyArgumentList
        # pylint:disable=no-value-for-parameter
        return cls(
            _uid=uid,
            _sequence_id=sequence_id,
            _library=library,
            _item_metadata=item_metadata,
            _study_count=study_count,
            **kwargs,
        )

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        template: ParametrizedTemplateVO,
        library: LibraryVO,
        item_metadata: LibraryItemMetadataVO,
        sequence_id: Optional[str] = None,
        study_count: int = 0,
    ) -> "ParametrizedTemplateARBase":
        ar = cls(
            _uid=uid,
            _sequence_id=sequence_id,
            _item_metadata=item_metadata,
            _library=library,
            _template=template,
            _study_count=study_count,
        )

        return ar

    @classmethod
    def from_input_values(
        cls,
        author: str,
        library: LibraryVO,
        template: ParametrizedTemplateVO,
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
        generate_seq_id_callback: Callable[[str, str], Optional[str]] = (
            lambda x, y: None
        ),
    ) -> "ParametrizedTemplateARBase":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        generated_uid = generate_uid_callback()

        ar = cls(
            _uid=generated_uid,
            _sequence_id=generate_seq_id_callback(
                generated_uid, template.template_sequence_id
            ),
            _library=library,
            _template=template,
            _item_metadata=item_metadata,
        )
        return ar

    def edit_draft(
        self, author: str, change_description: str, template: ParametrizedTemplateVO
    ):
        """
        Creates a new draft version for the object.
        """
        if self._template != template:
            super()._edit_draft(change_description=change_description, author=author)
            self._template = template

    def cascade_update(
        self,
        author: str,
        date: datetime.datetime,
        new_template_name: str,
        change_description: str = CASCADING_UPDATE_LABEL,
    ):
        change_description = change_description.format(self.template_uid)
        self._template = ParametrizedTemplateVO.from_name_and_parameter_terms(
            name=new_template_name,
            template_uid=self.template_uid,
            parameter_terms=self._template.parameter_terms,
        )
        self._item_metadata = self._item_metadata.new_version_start_date(
            author=author, change_description=change_description, date=date
        )

    @property
    def template_uid(self) -> str:
        return self._template.template_uid

    @property
    def template_sequence_id(self) -> str:
        return self._template.template_sequence_id

    @property
    def template_name(self) -> str:
        return self._template.template_name

    @property
    def template_name_plain(self) -> str:
        return self._template.template_name_plain

    @property
    def name(self) -> str:
        return self._template.expanded_template_value

    @property
    def name_plain(self) -> str:
        return self._template.expanded_plain_template_value

    def get_parameters(self) -> Sequence[ParameterTermEntryVO]:
        return self._template.parameter_terms

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
            return {ObjectAction.INACTIVATE}
        if self._item_metadata.status == LibraryItemStatus.RETIRED:
            return {ObjectAction.REACTIVATE}
        return frozenset()
