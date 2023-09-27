package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class OpenStudy {

    private CurrentMetadata currentMetadata;
    private String uid;
    private String studyNumber;
    private String studyId;
    private String studyAcronym;
    @Deprecated
    private String projectNumber;
    private String studyStatus;
    private List<String> possibleActions;

    public CurrentMetadata getCurrentMetadata() {
        return currentMetadata;
    }

    public void setCurrentMetadata(CurrentMetadata currentMetadata) {
        this.currentMetadata = currentMetadata;
    }

    public String getUid() {
        return uid;
    }

    public void setUid(String uid) {
        this.uid = uid;
    }

    public String getStudyNumber() {
        return studyNumber;
    }

    public void setStudyNumber(String studyNumber) {
        this.studyNumber = studyNumber;
    }

    public String getStudyId() {
        return studyId;
    }

    public void setStudyId(String studyId) {
        this.studyId = studyId;
    }

    public String getStudyAcronym() {
        return studyAcronym;
    }

    public void setStudyAcronym(String studyAcronym) {
        this.studyAcronym = studyAcronym;
    }

    public String getProjectNumber() {
        return projectNumber;
    }

    public void setProjectNumber(String projectNumber) {
        this.projectNumber = projectNumber;
    }

    public String getStudyStatus() {
        return studyStatus;
    }

    public void setStudyStatus(String studyStatus) {
        this.studyStatus = studyStatus;
    }

    public List<String> getPossibleActions() {
        return possibleActions;
    }

    public void setPossibleActions(List<String> possibleActions) {
        this.possibleActions = possibleActions;
    }
}
