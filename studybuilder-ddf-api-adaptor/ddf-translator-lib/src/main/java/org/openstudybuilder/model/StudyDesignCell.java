package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class StudyDesignCell {
    private String studyUid;
    private String designCellUid;
    private String studyArmUid;
    private String studyArmName;
    private String studyBranchArmName;
    private String studyBranchArmUid;
    private String studyEpochName;
    private String studyEpochUid;
    private String studyElementName;
    private String studyElementUid;
    private String transitionRule;
    private String startDate;
    private String userInitials;
    private String endDate;
    private int order;
}
