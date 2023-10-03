package org.CSDISC.DDF.model;

import java.util.List;

/**
 * A named time period defined in the protocol, wherein a study activity is specified and unchanging
 * throughout the interval, to support a study-specific purpose.
 * @author Chris Upkes
 */

public class StudyEpoch {

    private final String studyEpochId;
    // The literal identifier (i.e., distinctive designation) of the
    // study epoch, i.e., the named time period defined in the protocol,
    // wherein a study activity is specified and unchanging throughout the interval, to support a study-specific
    // purpose.
    private String studyEpochName;
    // The textual representation of the study epoch.
    private String studyEpochDescription;
    // A characterization or classification of the study epoch, i.e., the named time period defined in the protocol,
    // wherein a study activity is specified and unchanging throughout the interval,
    // to support a study-specific purpose.
    private Code studyEpochType;
    // A system identifier assigned to the epoch that occurs immediately prior to the current epoch.
    private String previousStudyEpochId;
    // A system identifier assigned to the epoch that occurs immediately after the current epoch.
    private String nextStudyEpochId;
    private List<Encounter> encounters;

    public StudyEpoch(String studyEpochId) {
        this.studyEpochId = studyEpochId;
    }

    public String getStudyEpochId() {
        return studyEpochId;
    }

    public String getStudyEpochName() {
        return studyEpochName;
    }

    public void setStudyEpochName(String studyEpochName) {
        this.studyEpochName = studyEpochName;
    }

    public String getStudyEpochDescription() {
        return studyEpochDescription;
    }

    public void setStudyEpochDescription(String studyEpochDescription) {
        this.studyEpochDescription = studyEpochDescription;
    }

    public Code getStudyEpochType() {
        return studyEpochType;
    }

    public void setStudyEpochType(Code studyEpochType) {
        this.studyEpochType = studyEpochType;
    }

    public String getPreviousStudyEpochId() {
        return previousStudyEpochId;
    }

    public void setPreviousStudyEpochId(String previousStudyEpochId) {
        this.previousStudyEpochId = previousStudyEpochId;
    }

    public String getNextStudyEpochId() {
        return nextStudyEpochId;
    }

    public void setNextStudyEpochId(String nextStudyEpochId) {
        this.nextStudyEpochId = nextStudyEpochId;
    }

    public List<Encounter> getEncounters() {
        return encounters;
    }

    public void setEncounters(List<Encounter> encounters) {
        this.encounters = encounters;
    }



}
