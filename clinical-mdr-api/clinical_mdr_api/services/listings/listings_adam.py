from typing import Optional, Sequence, Union

from neomodel import db

from clinical_mdr_api.domains.listings.utils import AdamReport
from clinical_mdr_api.listings.query_service import QueryService
from clinical_mdr_api.models.listings.listings_adam import (
    StudyEndpntAdamListing,
    StudyVisitAdamListing,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services._utils import (
    service_level_generic_filtering,
    service_level_generic_header_filtering,
)


class ADAMListingsService:
    _repos: MetaRepository

    def __init__(self):
        self._query_service = QueryService()

    @db.transaction
    def list_mdvisit(
        self,
        study_uid: str,
    ) -> Sequence[StudyVisitAdamListing]:
        data = self._query_service.get_mdvisit(study_uid=study_uid)
        result = list(map(StudyVisitAdamListing.from_query, data))
        return result

    @db.transaction
    def list_mdendpnt(
        self,
        study_uid: str,
    ) -> Sequence[StudyEndpntAdamListing]:
        data = self._query_service.get_mdendpnt(study_uid=study_uid)
        result = list(map(StudyEndpntAdamListing.from_query, data))
        return result

    def get_report(
        self,
        adam_report: AdamReport,
        study_uid: str,
        sort_by: Optional[dict] = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: Optional[dict] = None,
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
        total_count: bool = False,
    ) -> Union[
        GenericFilteringReturn[StudyVisitAdamListing],
        GenericFilteringReturn[StudyEndpntAdamListing],
    ]:
        if adam_report == AdamReport.MDVISIT:
            result = self.list_mdvisit(study_uid)
        elif adam_report == AdamReport.MDENDPNT:
            result = self.list_mdendpnt(study_uid)

        filtered_items = service_level_generic_filtering(
            items=result,
            filter_by=filter_by,
            filter_operator=filter_operator,
            sort_by=sort_by,
            total_count=total_count,
            page_number=page_number,
            page_size=page_size,
        )
        return filtered_items

    def get_distinct_adam_listing_values_for_headers(
        self,
        field_name: str,
        adam_report: AdamReport,
        study_uid: str,
        search_string: Optional[str] = "",
        filter_by: Optional[dict] = None,
        filter_operator: Optional[FilterOperator] = FilterOperator.AND,
        result_count: int = 10,
    ):
        if adam_report == AdamReport.MDVISIT:
            result = self.list_mdvisit(study_uid)
        elif adam_report == AdamReport.MDENDPNT:
            result = self.list_mdendpnt(study_uid)

        filtered_items = service_level_generic_header_filtering(
            items=result,
            field_name=field_name,
            search_string=search_string,
            filter_by=filter_by,
            filter_operator=filter_operator,
            result_count=result_count,
        )
        return filtered_items
