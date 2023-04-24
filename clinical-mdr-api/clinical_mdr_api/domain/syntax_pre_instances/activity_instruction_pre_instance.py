from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from clinical_mdr_api.domain.concepts.activities.activity import ActivityAR
from clinical_mdr_api.domain.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domain.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domain.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domain.library.object import (
    ParametrizedTemplateARBase,
    ParametrizedTemplateVO,
)
from clinical_mdr_api.domain.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)


@dataclass
class ActivityInstructionPreInstanceAR(ParametrizedTemplateARBase):
    """
    Implementation of ActivityInstructionPreInstanceAR. Solely based on Parametrized Template.
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
        template: ParametrizedTemplateVO,
        library: LibraryVO,
        item_metadata: LibraryItemMetadataVO,
        study_count: Optional[int] = None,
        indications: Optional[Sequence[DictionaryTermAR]] = None,
        activities: Optional[Sequence[ActivityAR]] = None,
        activity_groups: Optional[Sequence[ActivityGroupAR]] = None,
        activity_subgroups: Optional[Sequence[ActivitySubGroupAR]] = None,
    ) -> "ActivityInstructionPreInstanceAR":
        ar = cls(
            _uid=uid,
            _item_metadata=item_metadata,
            _library=library,
            _template=template,
            _indications=indications,
            _activities=activities,
            _activity_groups=activity_groups,
            _activity_subgroups=activity_subgroups,
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
        indications: Optional[Sequence[DictionaryTermAR]] = None,
        activities: Optional[Sequence[ActivityAR]] = None,
        activity_groups: Optional[Sequence[ActivityGroupAR]] = None,
        activity_subgroups: Optional[Sequence[ActivitySubGroupAR]] = None,
    ) -> "ActivityInstructionPreInstanceAR":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        ar = cls(
            _uid=generate_uid_callback(),
            _library=library,
            _template=template,
            _item_metadata=item_metadata,
        )
        ar._indications = indications
        ar._activities = activities
        ar._activity_groups = activity_groups
        ar._activity_subgroups = activity_subgroups

        return ar
