package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public  class IdentificationMetadata  {

    private String studyNumber;
    private String studyAcronym;
    private String projectNumber;
    private String projectName;
    private String clinicalProgrammeName;
    private String studyId;
    private RegistryIdentifier registryIdentifiers;
}