package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class StudySelectionObjective {

    private boolean acceptedVersion;
    private int endpointCount;
    private Objective latestObjective;
    private Objective objective;
    private CriteriaType objectiveLevel;
    private int order;
    private String projectName;
    private String projectNumber;
    private String startDate;
    private String endDate;
    private String status;
    private String changeType;
    private String studyObjectiveUid;
    private String studyUid;
    private String userInitials;
}
