package org.CSDISC.DDF.model;

import java.util.List;

/**
 * A partitioning of a study arm into individual pieces, which are associated with an epoch and any
 * number of sequential elements within that epoch.
 * @author Chris Upkes
 */

public class StudyCell {

    private final String studyCellId;
    private StudyArm studyArm;
    private StudyEpoch studyEpoch;
    private List<StudyElement> studyElements;

    public StudyCell(String studyCellId) {
        this.studyCellId = studyCellId;
    }

    public String getStudyCellId() {
        return studyCellId;
    }

    public StudyArm getStudyArm() {
        return studyArm;
    }

    public void setStudyArm(StudyArm studyArm) {
        this.studyArm = studyArm;
    }

    public StudyEpoch getStudyEpoch() {
        return studyEpoch;
    }

    public void setStudyEpoch(StudyEpoch studyEpoch) {
        this.studyEpoch = studyEpoch;
    }

    public List<StudyElement> getStudyElements() {
        return studyElements;
    }

    public void setStudyElements(List<StudyElement> studyElements) {
        this.studyElements = studyElements;
    }

    public void addStudyElement(StudyElement studyElement){
        this.studyElements.add(studyElement);
    }

    public void removeStudyElement(StudyElement studyElement){
        this.studyElements.remove(studyElement);
    }
}
