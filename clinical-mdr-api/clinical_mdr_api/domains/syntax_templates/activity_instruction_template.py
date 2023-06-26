from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from clinical_mdr_api.domains.concepts.activities.activity import ActivityAR
from clinical_mdr_api.domains.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domains.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domains.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domains.syntax_templates.template import (
    InstantiationCountsVO,
    TemplateAggregateRootBase,
    TemplateVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)


@dataclass
class ActivityInstructionTemplateAR(TemplateAggregateRootBase):
    """
    A specific Activity Instruction Template AR. It can be used to customize Activity Instruction Template
    behavior. Inherits generic template versioning behaviors
    """

    _indications: Optional[Sequence[DictionaryTermAR]] = None

    _activities: Optional[Sequence[ActivityAR]] = None

    _activity_groups: Optional[Sequence[ActivityGroupAR]] = None

    _activity_subgroups: Optional[Sequence[ActivitySubGroupAR]] = None

    @property
    def indications(self) -> Sequence[DictionaryTermAR]:
        return self._indications

    @property
    def activities(self) -> Sequence[ActivityAR]:
        return self._activities

    @property
    def activity_groups(self) -> Sequence[ActivityGroupAR]:
        return self._activity_groups

    @property
    def activity_subgroups(self) -> Sequence[ActivitySubGroupAR]:
        return self._activity_subgroups

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        sequence_id: str,
        template: TemplateVO,
        library: LibraryVO,
        item_metadata: LibraryItemMetadataVO,
        study_count: int = 0,
        counts: Optional[InstantiationCountsVO] = None,
        indications: Optional[Sequence[DictionaryTermAR]] = None,
        activities: Optional[Sequence[ActivityAR]] = None,
        activity_groups: Optional[Sequence[ActivityGroupAR]] = None,
        activity_subgroups: Optional[Sequence[ActivitySubGroupAR]] = None,
    ) -> "TemplateAggregateRootBase":
        ar = cls(
            _uid=uid,
            _sequence_id=sequence_id,
            _item_metadata=item_metadata,
            _library=library,
            _template=template,
            _indications=indications,
            _activities=activities,
            _activity_groups=activity_groups,
            _activity_subgroups=activity_subgroups,
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
        generate_seq_id_callback: Callable[[str], Optional[str]] = (lambda _: None),
        indications: Optional[Sequence[DictionaryTermAR]] = None,
        activities: Optional[Sequence[ActivityAR]] = None,
        activity_groups: Optional[Sequence[ActivityGroupAR]] = None,
        activity_subgroups: Optional[Sequence[ActivitySubGroupAR]] = None,
    ) -> "ActivityInstructionTemplateAR":
        ar: ActivityInstructionTemplateAR = super().from_input_values(
            author=author,
            template=template,
            library=library,
            template_value_exists_callback=template_value_exists_callback,
            generate_uid_callback=generate_uid_callback,
            generate_seq_id_callback=generate_seq_id_callback,
        )
        ar._indications = indications
        ar._activities = activities
        ar._activity_groups = activity_groups
        ar._activity_subgroups = activity_subgroups

        return ar
