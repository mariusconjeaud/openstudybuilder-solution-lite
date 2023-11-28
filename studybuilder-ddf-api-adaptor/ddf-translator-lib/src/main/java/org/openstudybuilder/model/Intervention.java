package org.openstudybuilder.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
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
}
