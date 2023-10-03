package org.CSDISC.DDF.model;

/**
 * A planned pathway assigned to the subject as they progress through the study,
 * usually referred to by a name that reflects one or more treatments, exposures, and/or controls included in the path.
 * @author Chris Upkes
 */

public class StudyArm {

    private final String studyArmId;
    // The literal identifier (i.e., distinctive designation) of the study arm.
    private String studyArmName;
    // The textual representation of the study arm.
    private String studyArmDescription;
    // The literal identifier (i.e., distinctive designation) of the study arm type.
    private Code studyArmType;
    // The textual representation of the study arm data origin.
    private String studyArmDataOriginDescription;
    // A characterization or classification of the study arm with respect to where the study arm data originates.
    private Code studyArmDataOriginType;

    public StudyArm(String studyArmId) {
        this.studyArmId = studyArmId;
    }

    public String getStudyArmId() {
        return studyArmId;
    }

    public String getStudyArmName() {
        return studyArmName;
    }

    public void setStudyArmName(String studyArmName) {
        this.studyArmName = studyArmName;
    }

    public String getStudyArmDescription() {
        return studyArmDescription;
    }

    public void setStudyArmDescription(String studyArmDescription) {
        this.studyArmDescription = studyArmDescription;
    }

    public Code getStudyArmType() {
        return studyArmType;
    }

    public void setStudyArmType(Code studyArmType) {
        this.studyArmType = studyArmType;
    }

    public String getStudyArmDataOriginDescription() {
        return studyArmDataOriginDescription;
    }

    public void setStudyArmDataOriginDescription(String studyArmDataOriginDescription) {
        this.studyArmDataOriginDescription = studyArmDataOriginDescription;
    }

    public Code getStudyArmDataOriginType() {
        return studyArmDataOriginType;
    }

    public void setStudyArmDataOriginType(Code studyArmDataOriginType) {
        this.studyArmDataOriginType = studyArmDataOriginType;
    }
}
