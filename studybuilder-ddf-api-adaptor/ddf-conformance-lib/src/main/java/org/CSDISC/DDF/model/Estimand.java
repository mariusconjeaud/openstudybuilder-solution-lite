package org.CSDISC.DDF.model;

import java.util.List;

/** A precise description of the treatment effect reflecting the clinical question posed by a given
 * clinical trial objective. It summarises at a population level what the outcomes would be in the same
 * patients under different treatment conditions being compared. (ICH E9 R1 Addendum)
 * @author Chris Upkes
 */

public class Estimand {

    private final String estimandId;
    // A synopsis of the clinical endpoint of interest within the analysis target study population.
    private String summaryMeasure;
    private AnalysisPopulation analysisPopulation;
    private List<IntercurrentEvent> intercurrentEvents;
    private Endpoint variableOfInterest;
    private InvestigationalIntervention treatment;

    public Estimand(String estimandId) {
        this.estimandId = estimandId;
    }

    public String getEstimandId() {
        return estimandId;
    }

    public String getSummaryMeasure() {
        return summaryMeasure;
    }

    public void setSummaryMeasure(String summaryMeasure) {
        this.summaryMeasure = summaryMeasure;
    }

    public AnalysisPopulation getAnalysisPopulation() {
        return analysisPopulation;
    }

    public void setAnalysisPopulation(AnalysisPopulation analysisPopulation) {
        this.analysisPopulation = analysisPopulation;
    }

    public List<IntercurrentEvent> getIntercurrentEvents() {
        return intercurrentEvents;
    }

    public void setIntercurrentEvents(List<IntercurrentEvent> intercurrentEvents) {
        this.intercurrentEvents = intercurrentEvents;
    }

    public void addIntercurrentEvent(IntercurrentEvent intercurrentEvent) {
        this.intercurrentEvents.add(intercurrentEvent);
    }

    public void removeIntercurrentEvent(IntercurrentEvent intercurrentEvent) {
        this.intercurrentEvents.remove(intercurrentEvent);
    }

    public InvestigationalIntervention getTreatment() {
        return treatment;
    }

    public void setTreatment(InvestigationalIntervention treatment) {
        this.treatment = treatment;
    }

    public Endpoint getVariableOfInterest() {
        return variableOfInterest;
    }

    public void setVariableOfInterest(Endpoint variableOfInterest) {
        this.variableOfInterest = variableOfInterest;
    }
}
