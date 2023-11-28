package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class VersionMetadata {

    private String studyStatus;
    private int lockedVersionNumber;
    private String versionTimestamp;
    private String lockedVersionAuthor;
    private String lockedVersionInfo;
    private int versionNumber;
    private String versionAuthor;
    private String versionDescription;
}
