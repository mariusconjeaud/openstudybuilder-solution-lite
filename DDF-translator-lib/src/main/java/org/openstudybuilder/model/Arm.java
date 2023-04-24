package org.openstudybuilder.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * From the StudySelectionArmWithConnectedBranchArms Model
 */
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class Arm {
    private String studyUid;
    private int order;
    private String projectNumber;
    private String projectName;
    private String armUid;
    private String name;
    private String shortName;
    private String code;
    private String description;
    private String armColour;
    private String randomizationGroup;
    private int numberOfSubjects;
    private CriteriaType armType;
    private String startDate;
    private String endDate;
    private String userInitials;
    private String status;
    private String changeType;
    private boolean acceptedVersion;
    private List<BranchArm> armConnectedBranchArms;
}
