package org.CSDISC.DDF.model;

import java.net.URI;

/** Data collected in the course of a clinical study.
 * @author Chris Upkes
 */

public class StudyData {

    private final String studyDataId;
    // The literal identifier (i.e., distinctive designation) for the study data.
    private String studyDataName;
    // The textual representation of the study data.
    private String studyDataDescription;
    // The uniform resource locator used to access the digital case report form.
    private URI ecrfLink;

    public StudyData(String studyDataId) {
        this.studyDataId = studyDataId;
    }

    public String getStudyDataId() {
        return studyDataId;
    }

    public String getStudyDataName() {
        return studyDataName;
    }

    public void setStudyDataName(String studyDataName) {
        this.studyDataName = studyDataName;
    }

    public String getStudyDataDescription() {
        return studyDataDescription;
    }

    public void setStudyDataDescription(String studyDataDescription) {
        this.studyDataDescription = studyDataDescription;
    }

    public URI getEcrfLink() {
        return ecrfLink;
    }

    public void setEcrfLink(URI ecrfLink) {
        this.ecrfLink = ecrfLink;
    }

}
