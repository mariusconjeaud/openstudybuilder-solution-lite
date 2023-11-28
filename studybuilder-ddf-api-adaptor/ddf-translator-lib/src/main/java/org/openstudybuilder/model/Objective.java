package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * Maps to Objective. In use by StudySelectionObjective, which is the main entity used to map the getObjectives call
 */
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class Objective {

    private String uid;
    private String name;
    private String startDate;
    private String endDate;
    private String status;
    private String version;
    private String changeDescription;
    private String userInitials;
    private List<String> possibleActions;
    private ObjectiveTemplate objectiveTemplate;
    private List<ParameterValue> parameterTerms;
    private Library library;
    private int studyCount;
    private String namePlain;
}
