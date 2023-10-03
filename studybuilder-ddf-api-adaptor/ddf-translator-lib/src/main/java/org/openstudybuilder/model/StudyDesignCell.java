package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
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

    public String getStudyUid() {
        return studyUid;
    }

    public void setStudyUid(String studyUid) {
        this.studyUid = studyUid;
    }

    public String getDesignCellUid() {
        return designCellUid;
    }

    public void setDesignCellUid(String designCellUid) {
        this.designCellUid = designCellUid;
    }

    public String getStudyArmUid() {
        return studyArmUid;
    }

    public void setStudyArmUid(String studyArmUid) {
        this.studyArmUid = studyArmUid;
    }

    public String getStudyArmName() {
        return studyArmName;
    }

    public void setStudyArmName(String studyArmName) {
        this.studyArmName = studyArmName;
    }

    public String getStudyBranchArmName() {
        return studyBranchArmName;
    }

    public void setStudyBranchArmName(String studyBranchArmName) {
        this.studyBranchArmName = studyBranchArmName;
    }

    public String getStudyBranchArmUid() {
        return studyBranchArmUid;
    }

    public void setStudyBranchArmUid(String studyBranchArmUid) {
        this.studyBranchArmUid = studyBranchArmUid;
    }

    public String getStudyEpochName() {
        return studyEpochName;
    }

    public void setStudyEpochName(String studyEpochName) {
        this.studyEpochName = studyEpochName;
    }

    public String getStudyEpochUid() {
        return studyEpochUid;
    }

    public void setStudyEpochUid(String studyEpochUid) {
        this.studyEpochUid = studyEpochUid;
    }

    public String getStudyElementName() {
        return studyElementName;
    }

    public void setStudyElementName(String studyElementName) {
        this.studyElementName = studyElementName;
    }

    public String getStudyElementUid() {
        return studyElementUid;
    }

    public void setStudyElementUid(String studyElementUid) {
        this.studyElementUid = studyElementUid;
    }

    public String getTransitionRule() {
        return transitionRule;
    }

    public void setTransitionRule(String transitionRule) {
        this.transitionRule = transitionRule;
    }

    public String getStartDate() {
        return startDate;
    }

    public void setStartDate(String startDate) {
        this.startDate = startDate;
    }

    public String getUserInitials() {
        return userInitials;
    }

    public void setUserInitials(String userInitials) {
        this.userInitials = userInitials;
    }

    public String getEndDate() {
        return endDate;
    }

    public void setEndDate(String endDate) {
        this.endDate = endDate;
    }

    public int getOrder() {
        return order;
    }

    public void setOrder(int order) {
        this.order = order;
    }
}
