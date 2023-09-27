package org.CSDISC.DDF.model;

/**
 * A basic building block for time within a clinical study comprising the following characteristics:
 * a description of what happens to the subject during the element; a definition of the start of the element;
 * a rule for ending the element.
 * @author Chris Upkes
 */

public class StudyElement {

    // element only attributes - these purely describe an element
    private final String studyElementId;
    // The literal identifier (i.e., distinctive designation) of the study design element.
    private String studyElementName;
    // The textual representation of the study design element.
    private String studyElementDescription;
    // all elements point to transition rules
    private TransitionRule transitionStartRule;
    private TransitionRule transitionEndRule;


    public StudyElement(String studyElementId) {
        this.studyElementId = studyElementId;
    }

    public String getStudyElementId() {
        return studyElementId;
    }

    public String getStudyElementName() {
        return studyElementName;
    }

    public void setStudyElementName(String studyElementName) {
        this.studyElementName = studyElementName;
    }

    public String getStudyElementDescription() {
        return studyElementDescription;
    }

    public void setStudyElementDescription(String studyElementDescription) {
        this.studyElementDescription = studyElementDescription;
    }

    public TransitionRule getTransitionStartRule() {
        return transitionStartRule;
    }

    public void setTransitionStartRule(TransitionRule transitionStartRule) {
        this.transitionStartRule = transitionStartRule;
    }

    public TransitionRule getTransitionEndRule() {
        return transitionEndRule;
    }

    public void setTransitionEndRule(TransitionRule transitionEndRule) {
        this.transitionEndRule = transitionEndRule;
    }

}
