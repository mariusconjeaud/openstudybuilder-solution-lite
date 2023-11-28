package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * Maps to StudyPopulationJsonModel - Obtained by making a call with the currentMedata.studyPopulation query param
 */
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
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
}
