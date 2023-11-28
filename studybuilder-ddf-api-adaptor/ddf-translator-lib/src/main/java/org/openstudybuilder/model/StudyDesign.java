package org.openstudybuilder.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class StudyDesign {

    private Code studyTypeCode;
    private Code studyTypeNullValueCode;
    private List<Code> trialTypeCodes;
    private Code trialTypeNullValueCode;
    private Code trialPhaseCode;
    private Code trialPhaseNullValueCode;
    @JsonProperty("is_extension_trial")
    private boolean isExtensionTrial;
    private Code isExtensionTrialNullValueCode;
    @JsonProperty("is_adaptive_design")
    private boolean isAdaptiveDesign;
    private Code isAdaptiveDesignNullValueCode;
    private String studyStopRules;
    private Code studyStopRulesNullValueCode;
    private StudyDurationModel confirmedResponseMinimumDuration;
    private Code confirmedResponseMinimumDurationNullValueCode;
    private boolean postAuthIndicator;
    private Code postAuthIndicatorNullValueCode;
}
