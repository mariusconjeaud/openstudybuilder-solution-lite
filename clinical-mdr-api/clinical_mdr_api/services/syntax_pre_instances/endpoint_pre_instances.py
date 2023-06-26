from typing import Optional

from neomodel import db

from clinical_mdr_api.domain_repositories.models.syntax import EndpointPreInstanceRoot
from clinical_mdr_api.domain_repositories.syntax_pre_instances.endpoint_pre_instance_repository import (
    EndpointPreInstanceRepository,
)
from clinical_mdr_api.domains._utils import generate_seq_id
from clinical_mdr_api.domains.syntax_pre_instances.endpoint_pre_instance import (
    EndpointPreInstanceAR,
)
from clinical_mdr_api.domains.versioned_object_aggregate import VersioningException
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models.syntax_pre_instances.endpoint_pre_instance import (
    EndpointPreInstance,
    EndpointPreInstanceVersion,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._utils import service_level_generic_filtering
from clinical_mdr_api.services.syntax_instances.endpoints import EndpointService


class EndpointPreInstanceService(EndpointService[EndpointPreInstanceAR]):
    aggregate_class = EndpointPreInstanceAR
    repository_interface = EndpointPreInstanceRepository
    version_class = EndpointPreInstanceVersion
    template_uid_property = "endpoint_template_uid"
    template_name_property = "endpoint_template"
    root_node_class = EndpointPreInstanceRoot

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: EndpointPreInstanceAR
    ) -> EndpointPreInstance:
        item = EndpointPreInstance.from_endpoint_pre_instance_ar(item_ar)
        self._set_indexings(item)
        return item

    def create_ar_from_input_values(
        self,
        template,
        generate_uid_callback=None,
        study_uid: Optional[str] = None,
        template_uid: Optional[str] = None,
        include_study_endpoints: Optional[bool] = False,
    ) -> EndpointPreInstanceAR:
        item_ar = super().create_ar_from_input_values(
            template=template,
            generate_uid_callback=generate_uid_callback,
            generate_seq_id_callback=generate_seq_id,
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
        status: Optional[str] = None,
        return_study_count: bool = True,
        sort_by: Optional[dict] = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: Optional[dict] = None,
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
        total_count: bool = False,
    ) -> GenericFilteringReturn[EndpointPreInstance]:
        pre_instances = self._repos.endpoint_pre_instance_repository.find_all()
        all_items = []
        for pre_instance in pre_instances:
            item = self._transform_aggregate_root_to_pydantic_model(pre_instance)
            all_items.append(item)

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
    def create_new_version(self, uid: str) -> EndpointPreInstance:
        try:
            item = self._find_by_uid_or_raise_not_found(uid, for_update=True)
            item._create_new_version(author=self.user_initials)
            self.repository.save(item)
            return self._transform_aggregate_root_to_pydantic_model(item)
        except VersioningException as e:
            raise BusinessLogicException(e.msg) from e
