package org.openstudybuilder.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class Intervention {

    private Code interventionTypeCode;
    private Code interventionTypeNullValueCode;
    private boolean addOnToExistingTreatments;
    private Code addOnToExistingTreatmentsNullValueCode;
    private Code controlTypeCode;
    private Code controlTypeNullValueCode;
    private Code interventionModelCode;
    private Code interventionModelNullValueCode;
    @JsonProperty("is_trial_randomised")
    private boolean isTrialRandomised;
    private Code isTrialRandomisedNullValueCode;
    private String stratificationFactor;
    private Code stratificationFactorNullValueCode;
    private Code trialBlindingSchemaCode;
    private Code trialBlindingSchemaNullValueCode;
    private StudyDurationModel plannedStudyLength;
    private Code plannedStudyLengthNullValueCode;
    private boolean drugStudyIndication;
    private Code drugStudyIndicationNullValueCode;
    private String deviceStudyIndication;
    private Code deviceStudyIndicationNullValueCode;
    private List<Code> trialIntentTypesCodes;
    private Code trialIntentTypesNullValueCode;

    public Code getInterventionTypeCode() {
        return interventionTypeCode;
    }

    public void setInterventionTypeCode(Code interventionTypeCode) {
        this.interventionTypeCode = interventionTypeCode;
    }

    public Code getInterventionTypeNullValueCode() {
        return interventionTypeNullValueCode;
    }

    public void setInterventionTypeNullValueCode(Code interventionTypeNullValueCode) {
        this.interventionTypeNullValueCode = interventionTypeNullValueCode;
    }

    public boolean isAddOnToExistingTreatments() {
        return addOnToExistingTreatments;
    }

    public void setAddOnToExistingTreatments(boolean addOnToExistingTreatments) {
        this.addOnToExistingTreatments = addOnToExistingTreatments;
    }

    public Code getAddOnToExistingTreatmentsNullValueCode() {
        return addOnToExistingTreatmentsNullValueCode;
    }

    public void setAddOnToExistingTreatmentsNullValueCode(Code addOnToExistingTreatmentsNullValueCode) {
        this.addOnToExistingTreatmentsNullValueCode = addOnToExistingTreatmentsNullValueCode;
    }

    public Code getControlTypeCode() {
        return controlTypeCode;
    }

    public void setControlTypeCode(Code controlTypeCode) {
        this.controlTypeCode = controlTypeCode;
    }

    public Code getControlTypeNullValueCode() {
        return controlTypeNullValueCode;
    }

    public void setControlTypeNullValueCode(Code controlTypeNullValueCode) {
        this.controlTypeNullValueCode = controlTypeNullValueCode;
    }

    public Code getInterventionModelCode() {
        return interventionModelCode;
    }

    public void setInterventionModelCode(Code interventionModelCode) {
        this.interventionModelCode = interventionModelCode;
    }

    public Code getInterventionModelNullValueCode() {
        return interventionModelNullValueCode;
    }

    public void setInterventionModelNullValueCode(Code interventionModelNullValueCode) {
        this.interventionModelNullValueCode = interventionModelNullValueCode;
    }

    public boolean isTrialRandomised() {
        return isTrialRandomised;
    }

    public void setTrialRandomised(boolean trialRandomised) {
        isTrialRandomised = trialRandomised;
    }

    public Code getIsTrialRandomisedNullValueCode() {
        return isTrialRandomisedNullValueCode;
    }

    public void setIsTrialRandomisedNullValueCode(Code isTrialRandomisedNullValueCode) {
        this.isTrialRandomisedNullValueCode = isTrialRandomisedNullValueCode;
    }

    public String getStratificationFactor() {
        return stratificationFactor;
    }

    public void setStratificationFactor(String stratificationFactor) {
        this.stratificationFactor = stratificationFactor;
    }

    public Code getStratificationFactorNullValueCode() {
        return stratificationFactorNullValueCode;
    }

    public void setStratificationFactorNullValueCode(Code stratificationFactorNullValueCode) {
        this.stratificationFactorNullValueCode = stratificationFactorNullValueCode;
    }

    public Code getTrialBlindingSchemaCode() {
        return trialBlindingSchemaCode;
    }

    public void setTrialBlindingSchemaCode(Code trialBlindingSchemaCode) {
        this.trialBlindingSchemaCode = trialBlindingSchemaCode;
    }

    public Code getTrialBlindingSchemaNullValueCode() {
        return trialBlindingSchemaNullValueCode;
    }

    public void setTrialBlindingSchemaNullValueCode(Code trialBlindingSchemaNullValueCode) {
        this.trialBlindingSchemaNullValueCode = trialBlindingSchemaNullValueCode;
    }

    public StudyDurationModel getPlannedStudyLength() {
        return plannedStudyLength;
    }

    public void setPlannedStudyLength(StudyDurationModel plannedStudyLength) {
        this.plannedStudyLength = plannedStudyLength;
    }

    public Code getPlannedStudyLengthNullValueCode() {
        return plannedStudyLengthNullValueCode;
    }

    public void setPlannedStudyLengthNullValueCode(Code plannedStudyLengthNullValueCode) {
        this.plannedStudyLengthNullValueCode = plannedStudyLengthNullValueCode;
    }

    public boolean isDrugStudyIndication() {
        return drugStudyIndication;
    }

    public void setDrugStudyIndication(boolean drugStudyIndication) {
        this.drugStudyIndication = drugStudyIndication;
    }

    public Code getDrugStudyIndicationNullValueCode() {
        return drugStudyIndicationNullValueCode;
    }

    public void setDrugStudyIndicationNullValueCode(Code drugStudyIndicationNullValueCode) {
        this.drugStudyIndicationNullValueCode = drugStudyIndicationNullValueCode;
    }

    public String getDeviceStudyIndication() {
        return deviceStudyIndication;
    }

    public void setDeviceStudyIndication(String deviceStudyIndication) {
        this.deviceStudyIndication = deviceStudyIndication;
    }

    public Code getDeviceStudyIndicationNullValueCode() {
        return deviceStudyIndicationNullValueCode;
    }

    public void setDeviceStudyIndicationNullValueCode(Code deviceStudyIndicationNullValueCode) {
        this.deviceStudyIndicationNullValueCode = deviceStudyIndicationNullValueCode;
    }

    public List<Code> getTrialIntentTypesCodes() {
        return trialIntentTypesCodes;
    }

    public void setTrialIntentTypesCodes(List<Code> trialIntentTypesCodes) {
        this.trialIntentTypesCodes = trialIntentTypesCodes;
    }

    public Code getTrialIntentTypesNullValueCode() {
        return trialIntentTypesNullValueCode;
    }

    public void setTrialIntentTypesNullValueCode(Code trialIntentTypesNullValueCode) {
        this.trialIntentTypesNullValueCode = trialIntentTypesNullValueCode;
    }
}
