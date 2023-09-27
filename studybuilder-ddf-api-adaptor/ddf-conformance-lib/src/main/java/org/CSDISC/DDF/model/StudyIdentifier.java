package org.CSDISC.DDF.model;

/**
 * A sequence of characters used to identify, name, or characterize the study.
 * @author Chris Upkes
 */

public class StudyIdentifier {

    private final String studyIdentifierId;
    // A sequence of characters used to identify, name, or characterize the study.
    private String studyIdentifier;
    private Organization studyIdentifierScope;


    public StudyIdentifier(String studyIdentifierId) {
        this.studyIdentifierId = studyIdentifierId;
    }

    public String getStudyIdentifierId() {
        return studyIdentifierId;
    }

    public String getStudyIdentifier() {
        return studyIdentifier;
    }

    public void setStudyIdentifier(String studyIdentifier) {
        this.studyIdentifier = studyIdentifier;
    }

    public Organization getStudyIdentifierScope() {
        return studyIdentifierScope;
    }

    public void setStudyIdentifierScope(Organization studyIdentifierScope) {
        this.studyIdentifierScope = studyIdentifierScope;
    }

}
