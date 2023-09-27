package org.CSDISC.DDF.model;

import java.util.List;

/**
 * A plan detailing how a study will be performed in order to represent the phenomenon under examination,
 * to answer the research questions that have been asked, and informing the statistical approach.
 * @author Chris Upkes
 */

public class StudyDesign {


    private final String studyDesignId;
    // The literal identifier (i.e., distinctive designation) of the study design.
    private String studyDesignName;
    // The textual representation of the study design.
    private String studyDesignDescription;
    // The planned purpose of the therapy, device, or agent under study in the clinical trial.
    private List<Code> trialIntentType;
    // The nature of the interventional study for which information is being collected.
    private List<Code> trialType;
    // The general design of the strategy for assigning interventions to participants in a clinical study.
    // (clinicaltrials.gov)
    private Code interventionModel;
    private List<StudyCell> studyCells;
    private List<Indication> studyIndications;
    private List<InvestigationalIntervention> studyInvestigationalInterventions;
    private List<StudyDesignPopulation> studyPopulations;
    private List<Objective> studyObjectives;
    private List<Workflow> studyWorkflows;
    // A categorization of a disease, disorder, or other condition based on common characteristics and often
    // associated with a medical specialty focusing on research and development of specific therapeutic
    // interventions for the purpose of treatment and prevention.
    private List<Code> therapeuticAreas;
    private List<Estimand> studyEstimands;
    private List<Encounter> encounters;
    private List<Activity> activities;


    public StudyDesign(String studyDesignId) {
        this.studyDesignId = studyDesignId;
    }

    public String getStudyDesignId() {
        return studyDesignId;
    }

    public String getStudyDesignName() {
        return studyDesignName;
    }

    public void setStudyDesignName(String studyDesignName) {
        this.studyDesignName = studyDesignName;
    }

    public String getStudyDesignDescription() {
        return studyDesignDescription;
    }

    public void setStudyDesignDescription(String studyDesignDescription) {
        this.studyDesignDescription = studyDesignDescription;
    }

    public List<Code> getTrialIntentType() {
        return trialIntentType;
    }

    public void setTrialIntentType(List<Code> trialIntentType) {
        this.trialIntentType = trialIntentType;
    }

    public List<Code> getTrialType() {
        return trialType;
    }

    public void setTrialType(List<Code> trialType) {
        this.trialType = trialType;
    }

    public List<StudyCell> getStudyCells() {
        return studyCells;
    }

    public void setStudyCells(List<StudyCell> studyCells) {
        this.studyCells = studyCells;
    }

    public List<Indication> getStudyIndications() {
        return studyIndications;
    }

    public void setStudyIndications(List<Indication> studyIndications) {
        this.studyIndications = studyIndications;
    }

    public void addStudyIndication(Indication indication){
        this.studyIndications.add(indication);
    }

    public void removeStudyIndication(Indication indication){
        this.studyIndications.remove(indication);
    }

    public List<InvestigationalIntervention> getStudyInvestigationalInterventions() {
        return studyInvestigationalInterventions;
    }

    public void setStudyInvestigationalInterventions(List<InvestigationalIntervention> studyInvestigationalInterventions) {
        this.studyInvestigationalInterventions = studyInvestigationalInterventions;
    }

    public void addStudyInvestigationalIntervention(InvestigationalIntervention investigationalIntervention){
        this.studyInvestigationalInterventions.add(investigationalIntervention);
    }

    public void removeStudyInvestigationalIntervention(InvestigationalIntervention investigationalIntervention){
        this.studyInvestigationalInterventions.remove(investigationalIntervention);
    }

    public List<Objective> getStudyObjectives() {
        return studyObjectives;
    }

    public void setStudyObjectives(List<Objective> studyObjectives) {
        this.studyObjectives = studyObjectives;
    }

    public void addStudyObjective(Objective objective){
        this.studyObjectives.add(objective);
    }

    public void removeStudyObjective(Objective objective){
        this.studyObjectives.remove(objective);
    }

    public List<Workflow> getStudyWorkflows() {
        return studyWorkflows;
    }

    public void setStudyWorkflows(List<Workflow> studyWorkflows) {
        this.studyWorkflows = studyWorkflows;
    }

    public void addStudyWorkflow(Workflow workflow){
        this.studyWorkflows.add(workflow);
    }

    public void removeStudyWorkflow(Workflow workflow){
        this.studyWorkflows.remove(workflow);
    }

    public List<StudyDesignPopulation> getStudyPopulations() {
        return studyPopulations;
    }

    public void setStudyPopulations(List<StudyDesignPopulation> studyStudyDesignPopulations) {
        this.studyPopulations = studyStudyDesignPopulations;
    }

    public Code getInterventionModel() {
        return interventionModel;
    }

    public void setInterventionModel(Code interventionModel) {
        this.interventionModel = interventionModel;
    }

    public List<Estimand> getStudyEstimands() {
        return studyEstimands;
    }

    public void setStudyEstimands(List<Estimand> studyEstimands) {
        this.studyEstimands = studyEstimands;
    }

    public List<Code> getTherapeuticAreas() {
        return this.therapeuticAreas;
    }

    public void setTherapeuticAreas(List<Code> therapeuticAreas) {
        this.therapeuticAreas = therapeuticAreas;
    }

    public List<Encounter> getEncounters() {
        return encounters;
    }

    public void setEncounters(List<Encounter> encounters) {
        this.encounters = encounters;
    }

    public List<Activity> getActivities() {
        return activities;
    }

    public void setActivities(List<Activity> activities) {
        this.activities = activities;
    }



}
