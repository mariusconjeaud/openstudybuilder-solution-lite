package org.CSDISC.DDF.model;

/**
 * The population within the general population to which the study results can be generalized.
 */
public class StudyDesignPopulation {

    private final String studyDesignPopulationId;
    // The textual representation of the study population.
    private String populationDescription;


    public StudyDesignPopulation(String uuid) {
        this.studyDesignPopulationId = uuid;
    }

    public String getStudyDesignPopulationId() {
        return studyDesignPopulationId;
    }

    public String getPopulationDescription() {
        return populationDescription;
    }

    public void setPopulationDescription(String populationDescription) {
        this.populationDescription = populationDescription;
    }
}
