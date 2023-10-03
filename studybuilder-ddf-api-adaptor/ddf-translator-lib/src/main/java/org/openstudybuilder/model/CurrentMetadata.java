package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.Map;
import java.util.UUID;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class CurrentMetadata {

    private IdentificationMetadata identificationMetadata;
    private VersionMetadata versionMetadata;
    private StudyDesign highLevelStudyDesign;
    // Description is just title/shortTitle string values. Leaving as map for the moment
    private Map<String, String> studyDescription;
    private Intervention studyIntervention;
    private Population studyPopulation;

    public CurrentMetadata(IdentificationMetadata identificationMetadata, VersionMetadata versionMetadata) {
        this.identificationMetadata = identificationMetadata;
        this.versionMetadata = versionMetadata;
    }

    public CurrentMetadata() {

    }

    public IdentificationMetadata getIdentificationMetadata() {
        return identificationMetadata;
    }

    public void setIdentificationMetadata(IdentificationMetadata identificationMetaData) {
        this.identificationMetadata = identificationMetaData;
    }

    public VersionMetadata getVersionMetadata() {
        return versionMetadata;
    }

    public void setVersionMetadata(VersionMetadata versionMetadata) {
        this.versionMetadata = versionMetadata;
    }

    public static class Code {

        private UUID termUid;
        private String name;

        public Code(UUID termUid, String name) {
            this.termUid = termUid;
            this.name = name;
        }

        public void setTermUid(UUID termUid) {
            this.termUid = termUid;
        }

        public void setName(String name) {
            this.name = name;
        }
    }

    public StudyDesign getHighLevelStudyDesign() {
        return highLevelStudyDesign;
    }

    public void setHighLevelStudyDesign(StudyDesign highLevelStudyDesign) {
        this.highLevelStudyDesign = highLevelStudyDesign;
    }

    public Map<String, String> getStudyDescription() {
        return studyDescription;
    }

    public void setStudyDescription(Map<String, String> studyDescription) {
        this.studyDescription = studyDescription;
    }

    public Intervention getStudyIntervention() {
        return studyIntervention;
    }

    public void setStudyIntervention(Intervention studyIntervention) {
        this.studyIntervention = studyIntervention;
    }

    public Population getStudyPopulation() {
        return studyPopulation;
    }

    public void setStudyPopulation(Population studyPopulation) {
        this.studyPopulation = studyPopulation;
    }
}
