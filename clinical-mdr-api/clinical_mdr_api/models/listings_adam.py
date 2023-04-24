from typing import Optional, Sequence

from pydantic import Field

from clinical_mdr_api.models.utils import BaseModel


class StudyEndpntAdamListing(BaseModel):
    STUDYID: str = Field(
        ..., title="Study Identifier", description="Unique identifier for a study."
    )
    OBJTVLVL: Optional[str] = Field(
        None,
        title="Objective Level",
        description="Objective Level",
    )
    OBJTV: str = Field(
        ...,
        title="Objective",
        description="Objective",
    )
    OBJTVPT: str = Field(
        None,
        title="Objective Plain Text",
        description="""Objective Plain Text""",
    )
    ENDPNTLVL: Optional[str] = Field(
        None,
        title="Endpoint Level",
        description="Endpoint Level",
    )
    ENDPNTSL: Optional[str] = Field(
        None,
        title="Endpoint Sub-level",
        description="Endpoint Sub-level",
    )
    ENDPNT: Optional[str] = Field(
        None,
        title="Endpoint Plain",
        description="Endpoint Plain",
    )
    ENDPNTPT: Optional[str] = Field(
        None,
        title="Endpoint Plain Text",
        description="Endpoint Plain Text",
    )
    UNITDEF: Optional[str] = Field(
        None,
        title="Unit Definition",
        description="Unit Definition",
    )
    UNIT: Optional[str] = Field(
        None,
        title="Unit",
        description="Unit",
    )
    TMFRM: Optional[str] = Field(
        None,
        title="Time Frame",
        description="Time Frame",
    )
    TMFRMPT: Optional[str] = Field(
        None,
        title="Time Frame Plain Text",
        description="Time Frame Plain Text",
    )
    RACT: Optional[Sequence[str]] = Field(
        None,
        title="Related Activities",
        description="Array list for all related Activity Group as Template Parameter in either Objective or Endpoint",
    )
    RACTSGRP: Optional[Sequence[str]] = Field(
        None,
        title="Related Activity Subroups",
        description="Array list for all related Activity Subgroup as Template Parameter in either Objective or Endpoint",
    )
    RACTGRP: Optional[Sequence[str]] = Field(
        None,
        title="Related Activity Groups",
        description="Array list for all related Activity Group as Template Parameter in either Objective or Endpoint",
    )
    RACTINST: Optional[Sequence[str]] = Field(
        None,
        title="Related Activity Instances",
        description="Array list for all related Activity Instamces as Template Parameter in either Objective or Endpoint",
    )

    @classmethod
    def from_query(cls, query_result: dict) -> "StudyVisitAdamListing":
        return cls(
            STUDYID=query_result["STUDYID"],
            OBJTVLVL=query_result["OBJTVLVL"],
            OBJTV=query_result["OBJTV"],
            OBJTVPT=query_result["OBJTVPT"],
            ENDPNTLVL=query_result["ENDPNTLVL"],
            ENDPNTSL=query_result["ENDPNTSL"],
            ENDPNT=query_result["ENDPNT"],
            ENDPNTPT=query_result["ENDPNTPT"],
            UNITDEF=query_result["UNITDEF"],
            UNIT=query_result["UNIT"],
            TMFRM=query_result["TMFRM"],
            TMFRMPT=query_result["TMFRMPT"],
            RACT=query_result["RACT"],
            RACTSGRP=query_result["RACTSGRP"],
            RACTGRP=query_result["RACTGRP"],
            RACTINST=query_result["RACTINST"],
        )


class StudyVisitAdamListing(BaseModel):
    STUDYID: str = Field(
        title="Study Identifier", description="Unique identifier for a study."
    )
    VISIT_TYPE_NAME: str = Field(
        title="Visit Type Code",
        description="Visit Type Code",
    )
    VISIT_NUM: int = Field(
        title="Visit Number",
        description="1. Clinical encounter number 2. Numeric version of VISIT, used for sorting.",
    )
    VISIT_NAME: str = Field(
        None,
        title="Visit Name",
        description="""1. Protocol-defined description of clinical encounter. 2. May
        be used in addition to VISITNUM and/or VISITDY as a text description of the clinical encounter.""",
    )
    DAY_VALUE: int = Field(
        None,
        title="Planned Study Day of Visit",
        description="1. Planned study day of VISIT. 2. Due to its sequential nature, used for sorting.",
    )
    VISIT_SHORT_LABEL: str = Field(
        None,
        title="Visit Label",
        description="Visit Label",
    )
    DAY_NAME: str = Field(
        None,
        title="Planned day",
        description="Planned day",
    )
    WEEK_NAME: str = Field(
        None,
        title="Planned Week Text",
        description="Planned Week Text",
    )
    WEEK_VALUE: str = Field(
        None,
        title="Planned Week Number",
        description="Planned Week Number",
    )

    @classmethod
    def from_query(cls, query_result: dict) -> "StudyVisitAdamListing":
        return cls(
            STUDYID=query_result["STUDYID"],
            VISIT_TYPE_NAME=query_result["VISIT_TYPE_NAME"],
            VISIT_NUM=query_result["VISIT_NUM"],
            VISIT_NAME=query_result["VISIT_NAME"],
            DAY_VALUE=query_result["DAY_VALUE"],
            VISIT_SHORT_LABEL=query_result["VISIT_SHORT_LABEL"],
            DAY_NAME=query_result["DAY_NAME"],
            WEEK_NAME=query_result["WEEK_NAME"],
            WEEK_VALUE=query_result["WEEK_VALUE"],
        )
