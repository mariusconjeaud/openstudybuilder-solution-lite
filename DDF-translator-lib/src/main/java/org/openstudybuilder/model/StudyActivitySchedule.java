package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

/**
 * Maps to StudyActivitySchedule
 */
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class StudyActivitySchedule {
    private String studyUid;
    private String studyActivityScheduleUid;
    private String studyActivityUid;
    private String studyActivityName;
    private String studyVisitUid;
    private String studyVisitName;
    private String note;
    private String startDate;
    private String endDate;
    private String userInitials;
}
