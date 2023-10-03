package org.CSDISC.DDF.model;

/**
 * A target study population on which an analysis is performed. These may be represented by the entire
 * study population, a subgroup defined by a particular characteristic measured at baseline, or a principal
 * stratum defined by the occurrence (or non-occurrence, depending on context) of a specific intercurrent
 * event. (ICH E9 R1 Addendum)
 */
public class AnalysisPopulation {

    private final String analysisPopulationId;
    // The textual representation of the study population for analysis.
    private String populationDescription;

    public AnalysisPopulation(String analysisPopulationId) {
        this.analysisPopulationId = analysisPopulationId;
    }

    public String getAnalysisPopulationId() {
        return analysisPopulationId;
    }

    public String getPopulationDescription() {
        return populationDescription;
    }

    public void setPopulationDescription(String populationDescription) {
        this.populationDescription = populationDescription;
    }
}
