package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class StudySelectionCriteria {

    private String studyCriteriaUid;
    private String studyUid;
    private int order;
    private Criteria criteria;
    private CriteriaTemplate criteriaTemplate;
    private Criteria latestCriteria;
    private CriteriaTemplate latestCriteriaTemplate;
    private boolean keyCriteria;
    private String startDate;
    private String endDate;
    private String status;
    private String changeType;
    private String userInitials;
    private String projectNumber;
    private String projectName;
    // At this level this fields corresponds to CTTermName
    private CriteriaType criteriaType;
    private boolean acceptedVersion;

    public String getStudyCriteriaUid() {
        return studyCriteriaUid;
    }

    public void setStudyCriteriaUid(String studyCriteriaUid) {
        this.studyCriteriaUid = studyCriteriaUid;
    }

    public String getStudyUid() {
        return studyUid;
    }

    public void setStudyUid(String studyUid) {
        this.studyUid = studyUid;
    }

    public int getOrder() {
        return order;
    }

    public void setOrder(int order) {
        this.order = order;
    }

    public Criteria getCriteria() {
        return criteria;
    }

    public void setCriteria(Criteria criteria) {
        this.criteria = criteria;
    }

    public CriteriaTemplate getCriteriaTemplate() {
        return criteriaTemplate;
    }

    public void setCriteriaTemplate(CriteriaTemplate criteriaTemplate) {
        this.criteriaTemplate = criteriaTemplate;
    }

    public Criteria getLatestCriteria() {
        return latestCriteria;
    }

    public void setLatestCriteria(Criteria latestCriteria) {
        this.latestCriteria = latestCriteria;
    }

    public CriteriaTemplate getLatestCriteriaTemplate() {
        return latestCriteriaTemplate;
    }

    public void setLatestCriteriaTemplate(CriteriaTemplate latestCriteriaTemplate) {
        this.latestCriteriaTemplate = latestCriteriaTemplate;
    }

    public boolean getKeyCriteria() {
        return keyCriteria;
    }

    public void setKeyCriteria(boolean keyCriteria) {
        this.keyCriteria = keyCriteria;
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

    public String getUserInitials() {
        return userInitials;
    }

    public void setUserInitials(String userInitials) {
        this.userInitials = userInitials;
    }

    public String getProjectNumber() {
        return projectNumber;
    }

    public void setProjectNumber(String projectNumber) {
        this.projectNumber = projectNumber;
    }

    public String getProjectName() {
        return projectName;
    }

    public void setProjectName(String projectName) {
        this.projectName = projectName;
    }

    public CriteriaType getCriteriaType() {
        return criteriaType;
    }

    public void setCriteriaType(CriteriaType criteriaType) {
        this.criteriaType = criteriaType;
    }

    public boolean isAcceptedVersion() {
        return acceptedVersion;
    }

    public void setAcceptedVersion(boolean acceptedVersion) {
        this.acceptedVersion = acceptedVersion;
    }
}
