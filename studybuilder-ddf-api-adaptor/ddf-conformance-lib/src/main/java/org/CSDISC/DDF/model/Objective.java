package org.CSDISC.DDF.model;

import java.util.List;

/**
 * The reason for performing a study in terms of the scientific questions to be answered by the analysis of
 * data collected during the study.
 * @author Chris Upkes
 */

public class Objective {

    private final String objectiveId;
    // The textual representation of the study objective. (BRIDG)
    private String objectiveDescription;
    // A characterization or classification of the study endpoint
    // that determines its category of importance relative to other study objectives.
    private Code objectiveLevel;
    private List<Endpoint> objectiveEndpoints;

    public Objective(String objectiveId) {
        this.objectiveId = objectiveId;
    }

    public String getObjectiveId() {
        return objectiveId;
    }

    public String getObjectiveDescription() {
        return objectiveDescription;
    }

    public void setObjectiveDescription(String objectiveDescription) {
        this.objectiveDescription = objectiveDescription;
    }

    public Code getObjectiveLevel() {
        return objectiveLevel;
    }

    public void setObjectiveLevel(Code objectiveLevel) {
        this.objectiveLevel = objectiveLevel;
    }

    public List<Endpoint> getObjectiveEndpoints() {
        return objectiveEndpoints;
    }

    public void setObjectiveEndpoints(List<Endpoint> objectiveEndpoints) {
        this.objectiveEndpoints = objectiveEndpoints;
    }

}
