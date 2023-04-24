package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
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

    public boolean isAcceptedVersion() {
        return acceptedVersion;
    }

    public void setAcceptedVersion(boolean acceptedVersion) {
        this.acceptedVersion = acceptedVersion;
    }

    public Endpoint getEndpoint() {
        return endpoint;
    }

    public void setEndpoint(Endpoint endpoint) {
        this.endpoint = endpoint;
    }

    public CriteriaType getEndpointLevel() {
        return endpointLevel;
    }

    public void setEndpointLevel(CriteriaType endpointLevel) {
        this.endpointLevel = endpointLevel;
    }

    public EndpointUnits getEndpointUnits() {
        return endpointUnits;
    }

    public void setEndpointUnits(EndpointUnits endpointUnits) {
        this.endpointUnits = endpointUnits;
    }

    public Endpoint getLatestEndpoint() {
        return latestEndpoint;
    }

    public void setLatestEndpoint(Endpoint latestEndpoint) {
        this.latestEndpoint = latestEndpoint;
    }

    public TimeFrame getLatestTimeframe() {
        return latestTimeframe;
    }

    public void setLatestTimeframe(TimeFrame latestTimeframe) {
        this.latestTimeframe = latestTimeframe;
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

    public String getStudyEndpointUid() {
        return studyEndpointUid;
    }

    public void setStudyEndpointUid(String studyEndpointUid) {
        this.studyEndpointUid = studyEndpointUid;
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

    public StudySelectionObjective getStudyObjective() {
        return studyObjective;
    }

    public void setStudyObjective(StudySelectionObjective studyObjective) {
        this.studyObjective = studyObjective;
    }

    public String getStudyUid() {
        return studyUid;
    }

    public void setStudyUid(String studyUid) {
        this.studyUid = studyUid;
    }

    public TimeFrame getTimeframe() {
        return timeframe;
    }

    public void setTimeframe(TimeFrame timeframe) {
        this.timeframe = timeframe;
    }

    public String getUserInitials() {
        return userInitials;
    }

    public void setUserInitials(String userInitials) {
        this.userInitials = userInitials;
    }

    public CriteriaType getEndpointSublevel() {
        return endpointSublevel;
    }

    public void setEndpointSublevel(CriteriaType endpointSublevel) {
        this.endpointSublevel = endpointSublevel;
    }
}
