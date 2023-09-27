package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

/**
 * Maps to StudyPopulationJsonModel - Obtained by making a call with the currentMedata.studyPopulation query param
 */
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class Population {
    private List<Code> therapeuticAreaCodes;
    private Code therapeuticAreaNullValueCode;
    private List<Code> diseaseConditionOrIndicationCodes;
    private Code diseaseConditionOrIndicationNullValueCode;
    private List<Code> diagnosisGroupCodes;
    private Code diagnosisGroupNullValueCode;
    private Code sexOfParticipantsCode;
    private Code sexOfParticipantsNullValueCode;
    private boolean rareDiseaseIndicator;
    private Code rareDiseaseIndicatorNullValueCode;
    private boolean healthySubjectIndicator;
    private Code healthySubjectIndicatorNullValueCode;
    private StudyDurationModel plannedMinimumAgeOfSubjects;
    private StudyDurationModel plannedMaximumAgeOfSubjects;
    private Code plannedMinimumAgeOfSubjectsNullValueCode;
    private Code plannedMaximumAgeOfSubjectsNullValueCode;
    private StudyDurationModel stableDiseaseMinimumDuration;
    private Code stableDiseaseMinimumDurationNullValueCode;
    private boolean pediatricStudyIndicator;
    private Code pediatricStudyIndicatorNullValueCode;
    private boolean pediatricPostmarketStudyIndicator;
    private Code pediatricPostmarketStudyIndicatorNullValueCode;
    private boolean pediatricInvestigationPlanIndicator;
    private Code pediatricInvestigationPlanIndicatorNullValueCode;
    private String relapseCriteria;
    private Code relapseCriteriaNullValueCode;
    private int numberOfExpectedSubjects;
    private Code numberOfExpectedSubjectsNullValueCode;

    public List<Code> getTherapeuticAreaCodes() {
        return therapeuticAreaCodes;
    }

    public void setTherapeuticAreaCodes(List<Code> therapeuticAreaCodes) {
        this.therapeuticAreaCodes = therapeuticAreaCodes;
    }

    public Code getTherapeuticAreaNullValueCode() {
        return therapeuticAreaNullValueCode;
    }

    public void setTherapeuticAreaNullValueCode(Code therapeuticAreaNullValueCode) {
        this.therapeuticAreaNullValueCode = therapeuticAreaNullValueCode;
    }

    public List<Code> getDiseaseConditionOrIndicationCodes() {
        return diseaseConditionOrIndicationCodes;
    }

    public void setDiseaseConditionOrIndicationCodes(List<Code> diseaseConditionOrIndicationCodes) {
        this.diseaseConditionOrIndicationCodes = diseaseConditionOrIndicationCodes;
    }

    public Code getDiseaseConditionOrIndicationNullValueCode() {
        return diseaseConditionOrIndicationNullValueCode;
    }

    public void setDiseaseConditionOrIndicationNullValueCode(Code diseaseConditionOrIndicationNullValueCode) {
        this.diseaseConditionOrIndicationNullValueCode = diseaseConditionOrIndicationNullValueCode;
    }

    public List<Code> getDiagnosisGroupCodes() {
        return diagnosisGroupCodes;
    }

    public void setDiagnosisGroupCodes(List<Code> diagnosisGroupCodes) {
        this.diagnosisGroupCodes = diagnosisGroupCodes;
    }

    public Code getDiagnosisGroupNullValueCode() {
        return diagnosisGroupNullValueCode;
    }

    public void setDiagnosisGroupNullValueCode(Code diagnosisGroupNullValueCode) {
        this.diagnosisGroupNullValueCode = diagnosisGroupNullValueCode;
    }

    public Code getSexOfParticipantsCode() {
        return sexOfParticipantsCode;
    }

    public void setSexOfParticipantsCode(Code sexOfParticipantsCode) {
        this.sexOfParticipantsCode = sexOfParticipantsCode;
    }

    public Code getSexOfParticipantsNullValueCode() {
        return sexOfParticipantsNullValueCode;
    }

    public void setSexOfParticipantsNullValueCode(Code sexOfParticipantsNullValueCode) {
        this.sexOfParticipantsNullValueCode = sexOfParticipantsNullValueCode;
    }

    public boolean isRareDiseaseIndicator() {
        return rareDiseaseIndicator;
    }

    public void setRareDiseaseIndicator(boolean rareDiseaseIndicator) {
        this.rareDiseaseIndicator = rareDiseaseIndicator;
    }

    public Code getRareDiseaseIndicatorNullValueCode() {
        return rareDiseaseIndicatorNullValueCode;
    }

    public void setRareDiseaseIndicatorNullValueCode(Code rareDiseaseIndicatorNullValueCode) {
        this.rareDiseaseIndicatorNullValueCode = rareDiseaseIndicatorNullValueCode;
    }

    public boolean isHealthySubjectIndicator() {
        return healthySubjectIndicator;
    }

    public void setHealthySubjectIndicator(boolean healthySubjectIndicator) {
        this.healthySubjectIndicator = healthySubjectIndicator;
    }

    public Code getHealthySubjectIndicatorNullValueCode() {
        return healthySubjectIndicatorNullValueCode;
    }

    public void setHealthySubjectIndicatorNullValueCode(Code healthySubjectIndicatorNullValueCode) {
        this.healthySubjectIndicatorNullValueCode = healthySubjectIndicatorNullValueCode;
    }

    public StudyDurationModel getPlannedMinimumAgeOfSubjects() {
        return plannedMinimumAgeOfSubjects;
    }

    public void setPlannedMinimumAgeOfSubjects(StudyDurationModel plannedMinimumAgeOfSubjects) {
        this.plannedMinimumAgeOfSubjects = plannedMinimumAgeOfSubjects;
    }

    public StudyDurationModel getPlannedMaximumAgeOfSubjects() {
        return plannedMaximumAgeOfSubjects;
    }

    public void setPlannedMaximumAgeOfSubjects(StudyDurationModel plannedMaximumAgeOfSubjects) {
        this.plannedMaximumAgeOfSubjects = plannedMaximumAgeOfSubjects;
    }

    public Code getPlannedMinimumAgeOfSubjectsNullValueCode() {
        return plannedMinimumAgeOfSubjectsNullValueCode;
    }

    public void setPlannedMinimumAgeOfSubjectsNullValueCode(Code plannedMinimumAgeOfSubjectsNullValueCode) {
        this.plannedMinimumAgeOfSubjectsNullValueCode = plannedMinimumAgeOfSubjectsNullValueCode;
    }

    public Code getPlannedMaximumAgeOfSubjectsNullValueCode() {
        return plannedMaximumAgeOfSubjectsNullValueCode;
    }

    public void setPlannedMaximumAgeOfSubjectsNullValueCode(Code plannedMaximumAgeOfSubjectsNullValueCode) {
        this.plannedMaximumAgeOfSubjectsNullValueCode = plannedMaximumAgeOfSubjectsNullValueCode;
    }

    public StudyDurationModel getStableDiseaseMinimumDuration() {
        return stableDiseaseMinimumDuration;
    }

    public void setStableDiseaseMinimumDuration(StudyDurationModel stableDiseaseMinimumDuration) {
        this.stableDiseaseMinimumDuration = stableDiseaseMinimumDuration;
    }

    public Code getStableDiseaseMinimumDurationNullValueCode() {
        return stableDiseaseMinimumDurationNullValueCode;
    }

    public void setStableDiseaseMinimumDurationNullValueCode(Code stableDiseaseMinimumDurationNullValueCode) {
        this.stableDiseaseMinimumDurationNullValueCode = stableDiseaseMinimumDurationNullValueCode;
    }

    public boolean isPediatricStudyIndicator() {
        return pediatricStudyIndicator;
    }

    public void setPediatricStudyIndicator(boolean pediatricStudyIndicator) {
        this.pediatricStudyIndicator = pediatricStudyIndicator;
    }

    public Code getPediatricStudyIndicatorNullValueCode() {
        return pediatricStudyIndicatorNullValueCode;
    }

    public void setPediatricStudyIndicatorNullValueCode(Code pediatricStudyIndicatorNullValueCode) {
        this.pediatricStudyIndicatorNullValueCode = pediatricStudyIndicatorNullValueCode;
    }

    public boolean isPediatricPostmarketStudyIndicator() {
        return pediatricPostmarketStudyIndicator;
    }

    public void setPediatricPostmarketStudyIndicator(boolean pediatricPostmarketStudyIndicator) {
        this.pediatricPostmarketStudyIndicator = pediatricPostmarketStudyIndicator;
    }

    public Code getPediatricPostmarketStudyIndicatorNullValueCode() {
        return pediatricPostmarketStudyIndicatorNullValueCode;
    }

    public void setPediatricPostmarketStudyIndicatorNullValueCode(Code pediatricPostmarketStudyIndicatorNullValueCode) {
        this.pediatricPostmarketStudyIndicatorNullValueCode = pediatricPostmarketStudyIndicatorNullValueCode;
    }

    public boolean isPediatricInvestigationPlanIndicator() {
        return pediatricInvestigationPlanIndicator;
    }

    public void setPediatricInvestigationPlanIndicator(boolean pediatricInvestigationPlanIndicator) {
        this.pediatricInvestigationPlanIndicator = pediatricInvestigationPlanIndicator;
    }

    public Code getPediatricInvestigationPlanIndicatorNullValueCode() {
        return pediatricInvestigationPlanIndicatorNullValueCode;
    }

    public void setPediatricInvestigationPlanIndicatorNullValueCode(Code pediatricInvestigationPlanIndicatorNullValueCode) {
        this.pediatricInvestigationPlanIndicatorNullValueCode = pediatricInvestigationPlanIndicatorNullValueCode;
    }

    public String getRelapseCriteria() {
        return relapseCriteria;
    }

    public void setRelapseCriteria(String relapseCriteria) {
        this.relapseCriteria = relapseCriteria;
    }

    public Code getRelapseCriteriaNullValueCode() {
        return relapseCriteriaNullValueCode;
    }

    public void setRelapseCriteriaNullValueCode(Code relapseCriteriaNullValueCode) {
        this.relapseCriteriaNullValueCode = relapseCriteriaNullValueCode;
    }

    public int getNumberOfExpectedSubjects() {
        return numberOfExpectedSubjects;
    }

    public void setNumberOfExpectedSubjects(int numberOfExpectedSubjects) {
        this.numberOfExpectedSubjects = numberOfExpectedSubjects;
    }

    public Code getNumberOfExpectedSubjectsNullValueCode() {
        return numberOfExpectedSubjectsNullValueCode;
    }

    public void setNumberOfExpectedSubjectsNullValueCode(Code numberOfExpectedSubjectsNullValueCode) {
        this.numberOfExpectedSubjectsNullValueCode = numberOfExpectedSubjectsNullValueCode;
    }
}
