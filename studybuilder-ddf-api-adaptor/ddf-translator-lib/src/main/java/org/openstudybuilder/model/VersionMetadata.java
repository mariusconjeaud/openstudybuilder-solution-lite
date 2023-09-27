package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class VersionMetadata{

    private String studyStatus;
    private int lockedVersionNumber;
    private String versionTimestamp;
    private String lockedVersionAuthor;
    private String lockedVersionInfo;
    private int versionNumber;
    private String versionAuthor;
    private String versionDescription;

    public VersionMetadata(String studyStatus, int lockedVersionNumber, String versionTimestamp, String lockedVersionAuthor, String lockedVersionInfo) {
        this.studyStatus = studyStatus;
        this.lockedVersionNumber = lockedVersionNumber;
        this.versionTimestamp = versionTimestamp;
        this.lockedVersionAuthor = lockedVersionAuthor;
        this.lockedVersionInfo = lockedVersionInfo;
    }

    public VersionMetadata() {

    }

    public String getStudyStatus() {
        return studyStatus;
    }

    public void setStudyStatus(String studyStatus) {
        this.studyStatus = studyStatus;
    }

    public int getLockedVersionNumber() {
        return lockedVersionNumber;
    }

    public void setLockedVersionNumber(int lockedVersionNumber) {
        this.lockedVersionNumber = lockedVersionNumber;
    }

    public String getVersionTimestamp() {
        return versionTimestamp;
    }

    public void setVersionTimestamp(String versionTimestamp) {
        this.versionTimestamp = versionTimestamp;
    }

    public String getLockedVersionAuthor() {
        return lockedVersionAuthor;
    }

    public void setLockedVersionAuthor(String lockedVersionAuthor) {
        this.lockedVersionAuthor = lockedVersionAuthor;
    }

    public String getLockedVersionInfo() {
        return lockedVersionInfo;
    }

    public void setLockedVersionInfo(String lockedVersionInfo) {
        this.lockedVersionInfo = lockedVersionInfo;
    }

    public int getVersionNumber() {
        return versionNumber;
    }

    public void setVersionNumber(int versionNumber) {
        this.versionNumber = versionNumber;
    }

    public String getVersionAuthor() {
        return versionAuthor;
    }

    public void setVersionAuthor(String versionAuthor) {
        this.versionAuthor = versionAuthor;
    }

    public String getVersionDescription() {
        return versionDescription;
    }

    public void setVersionDescription(String versionDescription) {
        this.versionDescription = versionDescription;
    }
}
