package org.openstudybuilder.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * Maps to StudyVisit
 * CustomPage_StudyVisit_ is the schema defining an array with "items" of StudyVisit
 */
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class Visit {
    private String studyEpochUid;
    private String visitTypeUid;
    private String timeReferenceUid;
    private int timeValue;
    private String timeUnitUid;
    private String visitSublabelCodelistUid;
    private String visitSublabelReference;
    private String legacyVisitId;
    private String legacyVisitTypeAlias;
    private String legacyName;
    private String legacySubname;
    private String consecutiveVisitGroup;
    private boolean showVisit;
    private int minVisitWindowValue;
    private int maxVisitWindowValue;
    private String visitWindowUnitUid;
    private String description;
    private String startRule;
    private String endRule;
    private String note;
    private String visitContactModeUid;
    private String epochAllocationUid;
    private String visitClass;
    private String visitSubclass;
    @JsonProperty("is_global_anchor_visit")
    private boolean isGlobalAnchorVisit;
    private String uid;
    private String studyUid;
    private String studyEpochName;
    private String epochUid;
    private int order;
    private String visitTypeName;
    private String timeReferenceName;
    private String timeUnitName;
    private String visitContactModeName;
    private String epochAllocationName;
    private int durationTime;
    private String durationTimeUnit;
    private int studyDayNumber;
    private String studyDurationDaysLabel;
    private String studyDayLabel;
    private int studyWeekNumber;
    private String studyDurationWeeksLabel;
    private String studyWeekLabel;
    private int visitNumber;
    private int visitSubnumber;
    private int uniqueVisitNumber;
    private String visitSubname;
    private String visitSublabel;
    private String visitName;
    private String visitShortName;
    private String visitWindowUnitName;
    private String status;
    private String startDate;
    private String userInitials;
    private List<String> possibleActions;
    private int studyActivityCount;
}
