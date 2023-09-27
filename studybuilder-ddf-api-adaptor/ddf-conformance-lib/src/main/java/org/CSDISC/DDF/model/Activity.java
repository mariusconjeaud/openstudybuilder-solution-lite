package org.CSDISC.DDF.model;


import java.util.List;

/**
 * An action, undertaking, or event, which is anticipated to be performed or observed, or was performed or observed,
 * according to the study protocol during the execution of the study.
 *
 * @author Chris Upkes
 */

public class Activity {

    private final String activityId;
    // The literal identifier (i.e., distinctive designation) of the clinical study activity.
    private String activityName;
    // The textual representation of the study activity.
    private String activityDescription;
    private List<Procedure> definedProcedures;
    private List<StudyData> studyDataCollection;
    // A system identifier assigned to a study activity that occurs immediately prior to the current study activity.
    private String previousActivityId;
    // A system identifier assigned to a study activity that occurs immediately after the current study activity.
    private String nextActivityId;

    public Activity(String activityId) {
        this.activityId = activityId;
    }

    public String getActivityId() { return  this.activityId; }

    public String getActivityDescription() {
        return activityDescription;
    }

    public void setActivityDescription(String description) {
        this.activityDescription = description;
    }

    public List<Procedure> getDefinedProcedures() {
        return definedProcedures;
    }

    public void setDefinedProcedures(List<Procedure> definedProcedures) {
        this.definedProcedures = definedProcedures;
    }

    public void addDefinedProcedure(Procedure procedure) {
        this.definedProcedures.add(procedure);
    }

    public void removeDefinedProcedure(Procedure procedure){
        this.definedProcedures.remove(procedure);
    }

    public List<StudyData> getStudyDataCollection() {
        return studyDataCollection;
    }

    public void setStudyDataCollection(List<StudyData> studyDataCollection) {
        this.studyDataCollection = studyDataCollection;
    }

    public void addStudyData(StudyData studyData){
        this.studyDataCollection.add(studyData);
    }

    public void removeStudyData(StudyData studyData){
        this.studyDataCollection.remove(studyData);
    }

    public String getActivityName() {
        return activityName;
    }

    public void setActivityName(String activityName) {
        this.activityName = activityName;
    }

    public String getPreviousActivityId() {
        return previousActivityId;
    }

    public void setPreviousActivityId(String previousActivityId) {
        this.previousActivityId = previousActivityId;
    }

    public String getNextActivityId() {
        return nextActivityId;
    }

    public void setNextActivityId(String nextActivityId) {
        this.nextActivityId = nextActivityId;
    }

}
