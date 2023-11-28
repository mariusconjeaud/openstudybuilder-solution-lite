package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.Map;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class CurrentMetadata {

    private IdentificationMetadata identificationMetadata;
    private VersionMetadata versionMetadata;
    private StudyDesign highLevelStudyDesign;
    private Intervention studyIntervention;
    private Population studyPopulation;
    private Map<String, String> studyDescription;
}
