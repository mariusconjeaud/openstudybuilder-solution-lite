from clinical_mdr_api.domain_repositories.syntax_instances.footnote_repository import (
    FootnoteRepository,
)
from clinical_mdr_api.domain_repositories.syntax_templates.footnote_template_repository import (
    FootnoteTemplateRepository,
)
from clinical_mdr_api.domains.syntax_instances.footnote import FootnoteAR
from clinical_mdr_api.models.syntax_instances.footnote import (
    Footnote,
    FootnoteVersion,
    FootnoteWithType,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._utils import service_level_generic_filtering
from clinical_mdr_api.services.syntax_instances.generic_syntax_instance_service import (
    GenericSyntaxInstanceService,
    _AggregateRootType,
)


class FootnoteService(GenericSyntaxInstanceService[FootnoteAR | _AggregateRootType]):
    aggregate_class = FootnoteAR
    repository_interface = FootnoteRepository
    template_repository_interface = FootnoteTemplateRepository
    version_class = FootnoteVersion
    template_uid_property = "footnote_template_uid"
    template_name_property = "footnote_template"

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: FootnoteAR
    ) -> Footnote:
        return FootnoteWithType.from_footnote_ar(
            item_ar,
            syntax_template_node=self._repos.footnote_template_repository.root_class.nodes.get_or_none(
                uid=item_ar.template_uid
            ),
            get_footnote_type_name=self._repos.ct_term_name_repository.get_syntax_template_type,
            get_footnote_type_attributes=self._repos.ct_term_attributes_repository.get_syntax_template_type,
        )

    def get_all(
        self,
        # pylint: disable=unused-argument
        status: str | None = None,
        return_study_count: bool = True,
        sort_by: dict | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict | None = None,
        filter_operator: FilterOperator | None = FilterOperator.AND,
        total_count: bool = False,
    ) -> GenericFilteringReturn[Footnote]:
        all_items = super().get_releases_referenced_by_any_study()

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
