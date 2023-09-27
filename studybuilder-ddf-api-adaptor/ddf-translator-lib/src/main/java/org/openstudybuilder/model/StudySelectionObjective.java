package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
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

    public boolean isAcceptedVersion() {
        return acceptedVersion;
    }

    public void setAcceptedVersion(boolean acceptedVersion) {
        this.acceptedVersion = acceptedVersion;
    }

    public int getEndpointCount() {
        return endpointCount;
    }

    public void setEndpointCount(int endpointCount) {
        this.endpointCount = endpointCount;
    }

    public Objective getLatestObjective() {
        return latestObjective;
    }

    public void setLatestObjective(Objective latestObjective) {
        this.latestObjective = latestObjective;
    }

    public Objective getObjective() {
        return objective;
    }

    public void setObjective(Objective objective) {
        this.objective = objective;
    }

    public CriteriaType getObjectiveLevel() {
        return objectiveLevel;
    }

    public void setObjectiveLevel(CriteriaType objectiveLevel) {
        this.objectiveLevel = objectiveLevel;
    }

    public int getOrder() {
        return order;
    }

    public void setOrder(int order) {
        this.order = order;
    }

    public String getProjectName() {
        return projectName;
    }

    public void setProjectName(String projectName) {
        this.projectName = projectName;
    }

    public String getProjectNumber() {
        return projectNumber;
    }

    public void setProjectNumber(String projectNumber) {
        this.projectNumber = projectNumber;
    }

    public String getStartDate() {
        return startDate;
    }

    public void setStartDate(String startDate) {
        this.startDate = startDate;
    }

    public String getEndDate() {
        return endDate;
    }

    public void setEndDate(String endDate) {
        this.endDate = endDate;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getChangeType() {
        return changeType;
    }

    public void setChangeType(String changeType) {
        this.changeType = changeType;
    }

    public String getStudyObjectiveUid() {
        return studyObjectiveUid;
    }

    public void setStudyObjectiveUid(String studyObjectiveUid) {
        this.studyObjectiveUid = studyObjectiveUid;
    }

    public String getStudyUid() {
        return studyUid;
    }

    public void setStudyUid(String studyUid) {
        this.studyUid = studyUid;
    }

    public String getUserInitials() {
        return userInitials;
    }

    public void setUserInitials(String userInitials) {
        this.userInitials = userInitials;
    }
}
