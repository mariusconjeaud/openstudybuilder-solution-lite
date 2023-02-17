from dataclasses import dataclass

from clinical_mdr_api.domain.versioned_object_aggregate import (
    TemplateAggregateRootBase,
    VersioningException,
)


@dataclass
class TimeframeTemplateAR(TemplateAggregateRootBase):
    """
    A specific Timeframe Template AR. It can be used to customize Timeframe Template
    behavior. Inherits strictly generic template versioning behaviors
    """

    def _raise_versioning_exception(self):
        raise VersioningException(
            "The template parameters cannot be modified after being a final version, only the plain text can be modified"
        )
