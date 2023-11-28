from neomodel import db

from clinical_mdr_api import exceptions
from clinical_mdr_api.domain_repositories.models.syntax import FootnoteTemplateRoot
from clinical_mdr_api.domain_repositories.syntax_instances.footnote_repository import (
    FootnoteRepository,
)
from clinical_mdr_api.domain_repositories.syntax_pre_instances.footnote_pre_instance_repository import (
    FootnotePreInstanceRepository,
)
from clinical_mdr_api.domain_repositories.syntax_templates.footnote_template_repository import (
    FootnoteTemplateRepository,
)
from clinical_mdr_api.domains.concepts.activities.activity import ActivityAR
from clinical_mdr_api.domains.concepts.activities.activity_group import ActivityGroupAR
from clinical_mdr_api.domains.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
)
from clinical_mdr_api.domains.controlled_terminologies.ct_term_attributes import (
    CTTermAttributesAR,
)
from clinical_mdr_api.domains.controlled_terminologies.ct_term_name import CTTermNameAR
from clinical_mdr_api.domains.dictionaries.dictionary_term import DictionaryTermAR
from clinical_mdr_api.domains.syntax_templates.footnote_template import (
    FootnoteTemplateAR,
)
from clinical_mdr_api.domains.syntax_templates.template import TemplateVO
from clinical_mdr_api.domains.versioned_object_aggregate import VersioningException
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.concepts.activities.activity import Activity
from clinical_mdr_api.models.concepts.activities.activity_group import ActivityGroup
from clinical_mdr_api.models.concepts.activities.activity_sub_group import (
    ActivitySubGroup,
)
from clinical_mdr_api.models.controlled_terminologies.ct_term import (
    CTTermNameAndAttributes,
)
from clinical_mdr_api.models.dictionaries.dictionary_term import DictionaryTerm
from clinical_mdr_api.models.syntax_templates.footnote_template import (
    FootnoteTemplate,
    FootnoteTemplateCreateInput,
    FootnoteTemplateEditIndexingsInput,
    FootnoteTemplateEditInput,
    FootnoteTemplateVersion,
    FootnoteTemplateWithCount,
)
from clinical_mdr_api.models.utils import BaseModel, GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._utils import (
    raise_404_if_none,
    service_level_generic_filtering,
)
from clinical_mdr_api.services.syntax_templates.generic_syntax_template_service import (
    GenericSyntaxTemplateService,
)


class FootnoteTemplateService(GenericSyntaxTemplateService[FootnoteTemplateAR]):
    aggregate_class = FootnoteTemplateAR
    version_class = FootnoteTemplateVersion
    repository_interface = FootnoteTemplateRepository
    instance_repository_interface = FootnoteRepository
    pre_instance_repository_interface = FootnotePreInstanceRepository
    root_node_class = FootnoteTemplateRoot

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: FootnoteTemplateAR
    ) -> FootnoteTemplate:
        item_ar = self._set_default_parameter_terms(item_ar)
        cls = (
            FootnoteTemplateWithCount if item_ar.study_count != 0 else FootnoteTemplate
        )
        item = cls.from_footnote_template_ar(
            item_ar,
            find_activity_subgroup_by_uid=self._repos.activity_subgroup_repository.find_by_uid_2,
            find_activity_group_by_uid=self._repos.activity_group_repository.find_by_uid_2,
        )
        self._set_indexings(item)
        return item

    def get_all(
        self,
        status: str | None = None,
        return_study_count: bool = True,
        sort_by: dict | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        total_count: bool = False,
    ) -> GenericFilteringReturn[FootnoteTemplate]:
        all_items = super().get_all(status, return_study_count)

        # The get_all method is only using neomodel, without Cypher query
        # Therefore, the filtering will be done in this service layer
        filtered_items = service_level_generic_filtering(
            items=all_items,
            filter_by=filter_by,
            filter_operator=filter_operator,
            sort_by=sort_by,
            total_count=total_count,
            page_number=page_number,
            page_size=page_size,
        )

        return filtered_items

    def _create_ar_from_input_values(
        self, template: FootnoteTemplateCreateInput
    ) -> FootnoteTemplateAR:
        default_parameter_terms = self._create_default_parameter_entries(
            template_name=template.name,
            default_parameter_terms=template.default_parameter_terms,
        )

        template_vo, library_vo = self._create_template_vo(
            template, default_parameter_terms
        )

        # Get indexings for templates from database
        (
            footnote_type,
            indications,
            activities,
            activity_groups,
            activity_subgroups,
        ) = self._get_indexings(template)

        # Process item to save
        item = FootnoteTemplateAR.from_input_values(
            author=self.user_initials,
            template=template_vo,
            library=library_vo,
            generate_uid_callback=self.repository.generate_uid_callback,
            next_available_sequence_id_callback=self.repository.next_available_sequence_id,
            indications=indications,
            activities=activities,
            activity_groups=activity_groups,
            activity_subgroups=activity_subgroups,
            footnote_type=footnote_type,
        )

        return item

    @db.transaction
    def edit_draft(
        self, uid: str, template: FootnoteTemplateEditInput
    ) -> FootnoteTemplate:
        try:
            item = self._find_by_uid_or_raise_not_found(uid, for_update=True)

            if (
                self.repository.check_exists_by_name_in_library(
                    name=template.name,
                    library=item.library.name,
                    type_uid=self.repository.get_template_type_uid(uid),
                )
                and template.name != item.name
            ):
                raise exceptions.ValidationException(
                    f"Duplicate templates not allowed - template exists: {template.name}"
                )

            template_vo = TemplateVO.from_input_values_2(
                template_name=template.name,
                parameter_name_exists_callback=self._parameter_name_exists,
            )

            item.edit_draft(
                author=self.user_initials,
                change_description=template.change_description,
                template=template_vo,
            )

            # Save item
            self.repository.save(item)
            return self._transform_aggregate_root_to_pydantic_model(item)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e

    @db.transaction
    def patch_indexings(
        self, uid: str, indexings: FootnoteTemplateEditIndexingsInput
    ) -> FootnoteTemplate:
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

    def _set_default_parameter_terms(
        self, item: FootnoteTemplateAR
    ) -> FootnoteTemplateAR:
        """This method fetches and sets the default parameter terms for the template

        Args:
            item (FootnoteTemplateAR): The template for which to fetch default parameter terms
        """
        # Get default parameter terms
        default_parameter_terms = self.repository.get_default_parameter_terms(item.uid)

        return FootnoteTemplateAR(
            _uid=item.uid,
            _sequence_id=item.sequence_id,
            _library=item.library,
            _item_metadata=item.item_metadata,
            _counts=item.counts,
            _study_count=item.study_count,
            _indications=item.indications,
            _activities=item.activities,
            _activity_groups=item.activity_groups,
            _activity_subgroups=item.activity_subgroups,
            _type=item.type,
            _template=TemplateVO(
                name=item.template_value.name,
                name_plain=item.template_value.name_plain,
                default_parameter_terms=default_parameter_terms,
            ),
        )

    def _set_indexings(self, item: FootnoteTemplate) -> None:
        """
        This method fetches and sets the indexing properties to a template.
        """
        if not hasattr(item, "uid"):
            return

        # Get type
        footnote_type_name = (
            self._repos.ct_term_name_repository.get_syntax_template_type(
                self.root_node_class, item.uid
            )
        )
        footnote_type_attributes = (
            self._repos.ct_term_attributes_repository.get_syntax_template_type(
                self.root_node_class, item.uid
            )
        )
        if footnote_type_name is not None and footnote_type_attributes is not None:
            item.type = CTTermNameAndAttributes.from_ct_term_ars(
                ct_term_name_ar=footnote_type_name,
                ct_term_attributes_ar=footnote_type_attributes,
            )

        # Get indications
        indications = (
            self._repos.dictionary_term_generic_repository.get_syntax_indications(
                self.root_node_class, item.uid
            )
        )
        if indications:
            item.indications = sorted(
                [
                    DictionaryTerm.from_dictionary_term_ar(indication)
                    for indication in indications
                ],
                key=lambda x: x.term_uid,
            )
        # Get activities
        activities = self._repos.activity_repository.get_syntax_activities(
            self.root_node_class, item.uid
        )
        if activities:
            item.activities = sorted(
                [
                    Activity.from_activity_ar(
                        activity,
                        self._repos.activity_subgroup_repository.find_by_uid_2,
                        self._repos.activity_group_repository.find_by_uid_2,
                    )
                    for activity in activities
                ],
                key=lambda x: x.uid,
            )
        # Get activity groups
        activity_groups = (
            self._repos.activity_group_repository.get_syntax_activity_groups(
                self.root_node_class, item.uid
            )
        )
        if activity_groups:
            item.activity_groups = sorted(
                [
                    ActivityGroup.from_activity_ar(activity)
                    for activity in activity_groups
                ],
                key=lambda x: x.uid,
            )
        # Get activity sub_groups
        activity_subgroups = (
            self._repos.activity_subgroup_repository.get_syntax_activity_subgroups(
                self.root_node_class, item.uid
            )
        )
        if activity_subgroups:
            item.activity_subgroups = sorted(
                [
                    ActivitySubGroup.from_activity_ar(
                        activity, self._repos.activity_group_repository.find_by_uid_2
                    )
                    for activity in activity_subgroups
                ],
                key=lambda x: x.uid,
            )

    def _get_indexings(
        self, template: BaseModel, template_uid: str | None = None
    ) -> tuple[
        tuple[CTTermNameAR, CTTermAttributesAR] | None,
        list[DictionaryTermAR],
        list[ActivityAR],
        list[ActivityGroupAR],
        list[ActivitySubGroupAR],
    ]:
        footnote_type: tuple[CTTermNameAR, CTTermAttributesAR] | None = None
        indications: list[DictionaryTermAR] = []
        activities: list[ActivityAR] = []
        activity_groups: list[ActivityGroupAR] = []
        activity_subgroups: list[ActivitySubGroupAR] = []

        footnote_type_term_uid = getattr(
            template, "type_uid", None
        ) or self._repos.footnote_template_repository.get_template_type_uid(
            template_uid
        )

        if footnote_type_term_uid is not None:
            footnote_type_name = self._repos.ct_term_name_repository.find_by_uid(
                term_uid=footnote_type_term_uid
            )
            raise_404_if_none(
                footnote_type_name,
                f"Footnote type with uid '{footnote_type_term_uid}' does not exist.",
            )
            footnote_type_attributes = (
                self._repos.ct_term_attributes_repository.find_by_uid(
                    term_uid=footnote_type_term_uid
                )
            )
            raise_404_if_none(
                footnote_type_attributes,
                f"Footnote type with uid '{footnote_type_term_uid}' does not exist.",
            )
            footnote_type = (footnote_type_name, footnote_type_attributes)

        for uid in template.indication_uids or []:
            indication = self._repos.dictionary_term_generic_repository.find_by_uid(
                term_uid=uid
            )
            raise_404_if_none(
                indication,
                f"Indication with uid '{uid}' does not exist.",
            )
            indications.append(indication)

        for uid in template.activity_uids or []:
            activity = self._repos.activity_repository.find_by_uid_2(uid=uid)
            raise_404_if_none(
                activity,
                f"Activity with uid '{uid}' does not exist.",
            )
            activities.append(activity)

        for uid in template.activity_group_uids or []:
            activity_group = self._repos.activity_group_repository.find_by_uid_2(
                uid=uid
            )
            raise_404_if_none(
                activity_group,
                f"Activity group with uid '{uid}' does not exist.",
            )
            activity_groups.append(activity_group)

        for uid in template.activity_subgroup_uids or []:
            activity_subgroup = self._repos.activity_subgroup_repository.find_by_uid_2(
                uid=uid
            )
            raise_404_if_none(
                activity_subgroup,
                f"Activity subgroup with uid '{uid}' does not exist.",
            )
            activity_subgroups.append(activity_subgroup)

        return (
            footnote_type,
            indications,
            activities,
            activity_groups,
            activity_subgroups,
        )
