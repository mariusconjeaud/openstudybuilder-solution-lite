from typing import Optional, cast

from clinical_mdr_api.domain.library.library_ar import LibraryAR
from clinical_mdr_api.domain.syntax_pre_instances.endpoint_pre_instance import (
    EndpointPreInstanceAR,
)
from clinical_mdr_api.domain.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.domain_repositories.models.syntax import EndpointPreInstanceRoot
from clinical_mdr_api.domain_repositories.syntax_pre_instances.endpoint_pre_instance_repository import (
    EndpointPreInstanceRepository,
)
from clinical_mdr_api.exceptions import NotFoundException
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
        return EndpointPreInstance.from_endpoint_pre_instance_ar(item_ar)

    def create_ar_from_input_values(
        self,
        template,
        generate_uid_callback=None,
        study_uid: Optional[str] = None,
        template_uid: Optional[str] = None,
        include_study_endpoints: Optional[bool] = False,
    ) -> EndpointPreInstanceAR:
        parameter_terms = self._create_parameter_entries(
            template,
            template_uid=template_uid,
            study_uid=study_uid,
            include_study_endpoints=include_study_endpoints,
        )

        template_uid = template_uid or getattr(template, self.template_uid_property)

        template_vo = self.parametrized_template_vo_class.from_input_values_2(
            template_uid=template_uid,
            parameter_terms=parameter_terms,
            get_final_template_vo_by_template_uid_callback=self._get_template_vo_by_template_uid,
        )

        try:
            library_vo = LibraryVO.from_input_values_2(
                library_name=template.library_name,
                is_library_editable_callback=(
                    lambda name: (
                        cast(
                            LibraryAR, self._repos.library_repository.find_by_name(name)
                        ).is_editable
                        if self._repos.library_repository.find_by_name(name) is not None
                        else None
                    )
                ),
            )
        except ValueError as exc:
            raise NotFoundException(
                f"The library with the name='{template.library_name}' could not be found."
            ) from exc

        indications, categories, sub_categories = self._get_indexings(template)

        item = EndpointPreInstanceAR.from_input_values(
            author=self.user_initials,
            template=template_vo,
            library=library_vo,
            generate_uid_callback=self.repository.generate_uid_callback,
            indications=indications,
            categories=categories,
            sub_categories=sub_categories,
        )
        return item

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
            self._set_indexings(item)
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
