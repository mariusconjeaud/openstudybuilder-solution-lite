from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from clinical_mdr_api.domains.concepts.activities.activity import ActivityAR
from clinical_mdr_api.domains.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domains.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domains.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domains.libraries.object import ParametrizedTemplateVO
from clinical_mdr_api.domains.syntax_pre_instances.pre_instance_ar import PreInstanceAR
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)


@dataclass
class ActivityInstructionPreInstanceAR(PreInstanceAR):
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
        sequence_id: str,
        study_count: int = 0,
        indications: Optional[Sequence[DictionaryTermAR]] = None,
        activities: Optional[Sequence[ActivityAR]] = None,
        activity_groups: Optional[Sequence[ActivityGroupAR]] = None,
        activity_subgroups: Optional[Sequence[ActivitySubGroupAR]] = None,
    ) -> "ActivityInstructionPreInstanceAR":
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
        )

        return ar

    @classmethod
    def from_input_values(
        cls,
        author: str,
        library: LibraryVO,
        template: ParametrizedTemplateVO,
        generate_uid_callback: Callable[[], Optional[str]] = (lambda: None),
        generate_seq_id_callback: Callable[[str, str, str], Optional[str]] = (
            lambda x, y: None
        ),
        indications: Optional[Sequence[DictionaryTermAR]] = None,
        activities: Optional[Sequence[ActivityAR]] = None,
        activity_groups: Optional[Sequence[ActivityGroupAR]] = None,
        activity_subgroups: Optional[Sequence[ActivitySubGroupAR]] = None,
    ) -> "ActivityInstructionPreInstanceAR":
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(author=author)

        generated_uid = generate_uid_callback()

        ar = cls(
            _uid=generated_uid,
            _sequence_id=generate_seq_id_callback(
                generated_uid, template.template_sequence_id, "P"
            ),
            _library=library,
            _template=template,
            _item_metadata=item_metadata,
        )
        ar._indications = indications
        ar._activities = activities
        ar._activity_groups = activity_groups
        ar._activity_subgroups = activity_subgroups

        return ar
