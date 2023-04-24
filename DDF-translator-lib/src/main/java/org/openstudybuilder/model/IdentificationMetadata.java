package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public  class IdentificationMetadata  {

    private String studyNumber;
    private String studyAcronym;
    private String projectNumber;
    private String projectName;
    private String clinicalProgrammeName;
    private String studyId;
    private RegistryIdentifier registryIdentifiers;

    public String getStudyNumber() {
        return studyNumber;
    }

    public void setStudyNumber(String studyNumber) {
        this.studyNumber = studyNumber;
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

    public String getProjectName() {
        return projectName;
    }

    public void setProjectName(String projectName) {
        this.projectName = projectName;
    }

    public String getClinicalProgrammeName() {
        return clinicalProgrammeName;
    }

    public void setClinicalProgrammeName(String clinicalProgrammeName) {
        this.clinicalProgrammeName = clinicalProgrammeName;
    }

    public String getStudyId() {
        return studyId;
    }

    public void setStudyId(String studyId) {
        this.studyId = studyId;
    }

    public RegistryIdentifier getRegistryIdentifiers() {
        return registryIdentifiers;
    }

    public void setRegistryIdentifiers(RegistryIdentifier registryIdentifiers) {
        this.registryIdentifiers = registryIdentifiers;
    }
}