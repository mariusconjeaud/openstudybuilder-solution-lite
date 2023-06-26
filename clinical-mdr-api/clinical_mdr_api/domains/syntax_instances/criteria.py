from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from clinical_mdr_api.domains.libraries.object import (
    ParametrizedTemplateARBase,
    ParametrizedTemplateVO,
)
from clinical_mdr_api.domains.libraries.parameter_term import ParameterTermEntryVO
from clinical_mdr_api.domains.syntax_templates.template import TemplateVO


@dataclass(frozen=True)
class CriteriaTemplateVO(ParametrizedTemplateVO):
    guidance_text: str

    @classmethod
    def from_repository_values(
        cls,
        *,
        template_name: str,
        template_uid: str,
        template_sequence_id: str,
        guidance_text: str,
        parameter_terms: Sequence[ParameterTermEntryVO],
    ) -> "CriteriaTemplateVO":
        """
        Create object based on repository values.

        Overriden version to include guidance text.
        """
        return cls(
            template_uid=template_uid,
            template_sequence_id=template_sequence_id,
            template_name=template_name,
            guidance_text=guidance_text,
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
    ) -> "CriteriaTemplateVO":
        """
        Creates object based on external input.

        Overriden version to include guidance text.
        """
        template = get_final_template_vo_by_template_uid_callback(template_uid)

        if template is None:
            raise ValueError(
                "The template with uid '{template_uid}' was not found. Make sure that there is a latest 'Final' version."
            )

        return cls(
            template_name=template.name,
            template_uid=template_uid,
            template_sequence_id=template_sequence_id,
            parameter_terms=tuple(parameter_terms),
            guidance_text=template.guidance_text,
        )


@dataclass
class CriteriaAR(ParametrizedTemplateARBase):
    """
    Implementation of Criteria AR. Solely based on Parametrized Template.
    If there will be a need to customize behavior of Criteria comparing to
    other template derived objects - this code should go here.
    """

    _template: CriteriaTemplateVO

    @property
    def template_guidance_text(self) -> str:
        """Shortcut to access template's guidance text."""
        return self._template.guidance_text
