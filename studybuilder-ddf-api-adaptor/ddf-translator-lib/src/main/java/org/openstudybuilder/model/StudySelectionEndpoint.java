package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class StudySelectionEndpoint {

    private boolean acceptedVersion;
    private Endpoint endpoint;
    private CriteriaType endpointLevel;
    private CriteriaType endpointSublevel;
    private EndpointUnits endpointUnits;
    private Endpoint latestEndpoint;
    private TimeFrame latestTimeframe;
    private int order;
    private String projectName;
    private String projectNumber;
    private String startDate;
    private String endDate;
    private String studyEndpointUid;
    private String status;
    private String changeType;
    private StudySelectionObjective studyObjective;
    private String studyUid;
    private TimeFrame timeframe;
    private String userInitials;
}
