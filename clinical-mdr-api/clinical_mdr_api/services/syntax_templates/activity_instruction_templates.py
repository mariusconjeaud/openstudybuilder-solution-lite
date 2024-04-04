from neomodel import db

from clinical_mdr_api.domain_repositories.syntax_instances.activity_instruction_repository import (
    ActivityInstructionRepository,
)
from clinical_mdr_api.domain_repositories.syntax_pre_instances.activity_instruction_pre_instance_repository import (
    ActivityInstructionPreInstanceRepository,
)
from clinical_mdr_api.domain_repositories.syntax_templates.activity_instruction_template_repository import (
    ActivityInstructionTemplateRepository,
)
from clinical_mdr_api.domains.syntax_templates.activity_instruction_template import (
    ActivityInstructionTemplateAR,
)
from clinical_mdr_api.models.syntax_templates.activity_instruction_template import (
    ActivityInstructionTemplate,
    ActivityInstructionTemplateCreateInput,
    ActivityInstructionTemplateEditIndexingsInput,
    ActivityInstructionTemplateVersion,
    ActivityInstructionTemplateWithCount,
)
from clinical_mdr_api.services.syntax_templates.generic_syntax_template_service import (
    GenericSyntaxTemplateService,
)


class ActivityInstructionTemplateService(
    GenericSyntaxTemplateService[ActivityInstructionTemplateAR]
):
    aggregate_class = ActivityInstructionTemplateAR
    version_class = ActivityInstructionTemplateVersion
    repository_interface = ActivityInstructionTemplateRepository
    instance_repository_interface = ActivityInstructionRepository
    pre_instance_repository_interface = ActivityInstructionPreInstanceRepository

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: ActivityInstructionTemplateAR
    ) -> ActivityInstructionTemplate:
        cls = (
            ActivityInstructionTemplateWithCount
            if item_ar.counts is not None
            else ActivityInstructionTemplate
        )
        return cls.from_activity_instruction_template_ar(item_ar)

    def _create_ar_from_input_values(
        self, template: ActivityInstructionTemplateCreateInput
    ) -> ActivityInstructionTemplateAR:
        template_vo, library_vo = self._create_template_vo(template)

        # Get indexings for templates from database
        (
            indications,
            _,
            _,
            activities,
            activity_groups,
            activity_subgroups,
            _,
        ) = self._get_indexings(template)

        # Process item to save
        item = ActivityInstructionTemplateAR.from_input_values(
            author=self.user_initials,
            template=template_vo,
            library=library_vo,
            generate_uid_callback=self.repository.generate_uid_callback,
            next_available_sequence_id_callback=self.repository.next_available_sequence_id,
            indications=indications,
            activities=activities,
            activity_groups=activity_groups,
            activity_subgroups=activity_subgroups,
        )

        return item

    @db.transaction
    def patch_indexings(
        self, uid: str, indexings: ActivityInstructionTemplateEditIndexingsInput
    ) -> ActivityInstructionTemplate:
        try:
            self._find_by_uid_or_raise_not_found(uid)
            if indexings.indication_uids is not None:
                self.repository.patch_indications(uid, indexings.indication_uids)
            if indexings.activity_uids is not None:
                self.repository.patch_activities(uid, indexings.activity_uids)
            if indexings.activity_group_uids is not None:
                self.repository.patch_activity_groups(
                    uid, indexings.activity_group_uids
                )
            if indexings.activity_subgroup_uids is not None:
                self.repository.patch_activity_subgroups(
                    uid, indexings.activity_subgroup_uids
                )
        finally:
            self.repository.close()

        return self.get_by_uid(uid)
