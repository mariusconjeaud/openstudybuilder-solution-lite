from neomodel import db

from clinical_mdr_api.domain_repositories.models.syntax import ObjectivePreInstanceRoot
from clinical_mdr_api.domain_repositories.syntax_pre_instances.objective_pre_instance_repository import (
    ObjectivePreInstanceRepository,
)
from clinical_mdr_api.domains.syntax_pre_instances.objective_pre_instance import (
    ObjectivePreInstanceAR,
)
from clinical_mdr_api.domains.versioned_object_aggregate import VersioningException
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.syntax_pre_instances.objective_pre_instance import (
    ObjectivePreInstance,
    ObjectivePreInstanceVersion,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._utils import service_level_generic_filtering
from clinical_mdr_api.services.syntax_instances.objectives import ObjectiveService


class ObjectivePreInstanceService(ObjectiveService[ObjectivePreInstanceAR]):
    aggregate_class = ObjectivePreInstanceAR
    repository_interface = ObjectivePreInstanceRepository
    version_class = ObjectivePreInstanceVersion
    template_uid_property = "objective_template_uid"
    template_name_property = "objective_template"
    root_node_class = ObjectivePreInstanceRoot

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: ObjectivePreInstanceAR
    ) -> ObjectivePreInstance:
        item = ObjectivePreInstance.from_objective_pre_instance_ar(item_ar)
        self._set_indexings(item)
        return item

    def create_ar_from_input_values(
        self,
        template,
        generate_uid_callback=None,
        study_uid: str | None = None,
        template_uid: str | None = None,
        include_study_endpoints: bool | None = False,
    ) -> ObjectivePreInstanceAR:
        item_ar = super().create_ar_from_input_values(
            template=template,
            generate_uid_callback=generate_uid_callback,
            next_available_sequence_id_callback=self.repository.next_available_sequence_id,
            study_uid=study_uid,
            template_uid=template_uid,
            include_study_endpoints=include_study_endpoints,
        )

        indications, categories, _ = self._get_indexings(template)

        item_ar._indications = indications
        item_ar._categories = categories
        item_ar._is_confirmatory_testing = template.is_confirmatory_testing

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
    ) -> GenericFilteringReturn[ObjectivePreInstance]:
        pre_instances = self._repos.objective_pre_instance_repository.find_all(
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
    def create_new_version(self, uid: str) -> ObjectivePreInstance:
        try:
            item = self._find_by_uid_or_raise_not_found(uid, for_update=True)
            item._create_new_version(author=self.user_initials)
            self.repository.save(item)
            return self._transform_aggregate_root_to_pydantic_model(item)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e
