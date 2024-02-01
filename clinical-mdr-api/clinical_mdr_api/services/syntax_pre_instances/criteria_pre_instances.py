from neomodel import db

from clinical_mdr_api.domain_repositories.models.syntax import CriteriaPreInstanceRoot
from clinical_mdr_api.domain_repositories.syntax_pre_instances.criteria_pre_instance_repository import (
    CriteriaPreInstanceRepository,
)
from clinical_mdr_api.domains.syntax_pre_instances.criteria_pre_instance import (
    CriteriaPreInstanceAR,
)
from clinical_mdr_api.domains.versioned_object_aggregate import VersioningException
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.syntax_pre_instances.criteria_pre_instance import (
    CriteriaPreInstance,
    CriteriaPreInstanceVersion,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._utils import service_level_generic_filtering
from clinical_mdr_api.services.syntax_instances.criteria import CriteriaService


class CriteriaPreInstanceService(CriteriaService[CriteriaPreInstanceAR]):
    aggregate_class = CriteriaPreInstanceAR
    repository_interface = CriteriaPreInstanceRepository
    version_class = CriteriaPreInstanceVersion
    template_uid_property = "criteria_template_uid"
    template_name_property = "criteria_template"
    root_node_class = CriteriaPreInstanceRoot

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: CriteriaPreInstanceAR
    ) -> CriteriaPreInstance:
        item = CriteriaPreInstance.from_criteria_pre_instance_ar(item_ar)
        self._set_indexings(item, self.root_node_class.nodes.get(uid=item.uid))
        item.template_type_uid = (
            self._repos.criteria_template_repository.get_template_type_uid(
                self._repos.criteria_template_repository.root_class.nodes.get(
                    uid=item.template_uid
                )
            )
        )
        return item

    def create_ar_from_input_values(
        self,
        template,
        generate_uid_callback=None,
        study_uid: str | None = None,
        template_uid: str | None = None,
        include_study_endpoints: bool | None = False,
    ) -> CriteriaPreInstanceAR:
        item_ar = super().create_ar_from_input_values(
            template=template,
            generate_uid_callback=generate_uid_callback,
            next_available_sequence_id_callback=self.repository.next_available_sequence_id,
            study_uid=study_uid,
            template_uid=template_uid,
            include_study_endpoints=include_study_endpoints,
        )

        indications, categories, sub_categories = self._get_indexings(template)

        item_ar._indications = indications
        item_ar._categories = categories
        item_ar._subcategories = sub_categories

        return item_ar

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
    ) -> GenericFilteringReturn[CriteriaPreInstance]:
        pre_instances = self._repos.criteria_pre_instance_repository.find_all(
            status=status, return_study_count=return_study_count
        )
        all_items = [
            self._transform_aggregate_root_to_pydantic_model(pre_instance)
            for pre_instance in pre_instances
        ]

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

    @db.transaction
    def create_new_version(self, uid: str) -> CriteriaPreInstance:
        try:
            item = self._find_by_uid_or_raise_not_found(uid, for_update=True)
            item._create_new_version(author=self.user_initials)
            self.repository.save(item)
            return self._transform_aggregate_root_to_pydantic_model(item)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e

    @db.transaction
    def edit_draft(self, uid, template):
        try:
            item = self._find_by_uid_or_raise_not_found(uid, for_update=True)
            parameter_terms = self._create_parameter_entries(
                template, template_uid=item.template_uid
            )

            template_vo = self.parametrized_template_vo_class.from_input_values_2(
                template_uid=item.template_uid,
                template_sequence_id=item.template_sequence_id,
                parameter_terms=parameter_terms,
                library_name=item.template_library_name,
                get_final_template_vo_by_template_uid_callback=self._get_template_vo_by_template_uid,
            )
            item.edit_draft(
                author=self.user_initials,
                change_description=template.change_description,
                template=template_vo,
            )

            if template.guidance_text is not None:
                setattr(
                    item.repository_closure_data[1],
                    "guidance_text",
                    template.guidance_text,
                )
                item.guidance_text = template.guidance_text

            self.repository.save(item)

            return self._transform_aggregate_root_to_pydantic_model(item)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e
