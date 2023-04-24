package org.openstudybuilder.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
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

    public Code getStudyTypeCode() {
        return studyTypeCode;
    }

    public void setStudyTypeCode(Code studyTypeCode) {
        this.studyTypeCode = studyTypeCode;
    }

    public Code getStudyTypeNullValueCode() {
        return studyTypeNullValueCode;
    }

    public void setStudyTypeNullValueCode(Code studyTypeNullValueCode) {
        this.studyTypeNullValueCode = studyTypeNullValueCode;
    }

    public List<Code> getTrialTypeCodes() {
        return trialTypeCodes;
    }

    public void setTrialTypeCodes(List<Code> trialTypeCodes) {
        this.trialTypeCodes = trialTypeCodes;
    }

    public Code getTrialTypeNullValueCode() {
        return trialTypeNullValueCode;
    }

    public void setTrialTypeNullValueCode(Code trialTypeNullValueCode) {
        this.trialTypeNullValueCode = trialTypeNullValueCode;
    }

    public Code getTrialPhaseCode() {
        return trialPhaseCode;
    }

    public void setTrialPhaseCode(Code trialPhaseCode) {
        this.trialPhaseCode = trialPhaseCode;
    }

    public Code getTrialPhaseNullValueCode() {
        return trialPhaseNullValueCode;
    }

    public void setTrialPhaseNullValueCode(Code trialPhaseNullValueCode) {
        this.trialPhaseNullValueCode = trialPhaseNullValueCode;
    }

    public boolean isExtensionTrial() {
        return isExtensionTrial;
    }

    public void setExtensionTrial(boolean extensionTrial) {
        isExtensionTrial = extensionTrial;
    }

    public Code getIsExtensionTrialNullValueCode() {
        return isExtensionTrialNullValueCode;
    }

    public void setIsExtensionTrialNullValueCode(Code isExtensionTrialNullValueCode) {
        this.isExtensionTrialNullValueCode = isExtensionTrialNullValueCode;
    }

    public boolean isAdaptiveDesign() {
        return isAdaptiveDesign;
    }

    public void setAdaptiveDesign(boolean adaptiveDesign) {
        isAdaptiveDesign = adaptiveDesign;
    }

    public Code getIsAdaptiveDesignNullValueCode() {
        return isAdaptiveDesignNullValueCode;
    }

    public void setIsAdaptiveDesignNullValueCode(Code isAdaptiveDesignNullValueCode) {
        this.isAdaptiveDesignNullValueCode = isAdaptiveDesignNullValueCode;
    }

    public String getStudyStopRules() {
        return studyStopRules;
    }

    public void setStudyStopRules(String studyStopRules) {
        this.studyStopRules = studyStopRules;
    }

    public Code getStudyStopRulesNullValueCode() {
        return studyStopRulesNullValueCode;
    }

    public void setStudyStopRulesNullValueCode(Code studyStopRulesNullValueCode) {
        this.studyStopRulesNullValueCode = studyStopRulesNullValueCode;
    }

    public StudyDurationModel getConfirmedResponseMinimumDuration() {
        return confirmedResponseMinimumDuration;
    }

    public void setConfirmedResponseMinimumDuration(StudyDurationModel confirmedResponseMinimumDuration) {
        this.confirmedResponseMinimumDuration = confirmedResponseMinimumDuration;
    }

    public Code getConfirmedResponseMinimumDurationNullValueCode() {
        return confirmedResponseMinimumDurationNullValueCode;
    }

    public void setConfirmedResponseMinimumDurationNullValueCode(Code confirmedResponseMinimumDurationNullValueCode) {
        this.confirmedResponseMinimumDurationNullValueCode = confirmedResponseMinimumDurationNullValueCode;
    }

    public boolean isPostAuthIndicator() {
        return postAuthIndicator;
    }

    public void setPostAuthIndicator(boolean postAuthIndicator) {
        this.postAuthIndicator = postAuthIndicator;
    }

    public Code getPostAuthIndicatorNullValueCode() {
        return postAuthIndicatorNullValueCode;
    }

    public void setPostAuthIndicatorNullValueCode(Code postAuthIndicatorNullValueCode) {
        this.postAuthIndicatorNullValueCode = postAuthIndicatorNullValueCode;
    }
}
