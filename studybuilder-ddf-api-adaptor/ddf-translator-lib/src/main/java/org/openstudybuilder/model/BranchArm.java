package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class BranchArm {
    private String studyUid;
    private int order;
    private String projectNumber;
    private String projectName;
    private String branchArmUid;
    private String name;
    private String shortName;
    private String code;
    private String description;
    private String colourCode;
    private String randomizationGroup;
    private int numberOfSubjects;
    private String startDate;
    private String endDate;
    private String userInitials;
    private String status;
    private String changeType;
    private boolean acceptedVersion;
}
