package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class OpenStudy {

    private CurrentMetadata currentMetadata;
    private String uid;
    private String studyNumber;
    private String studyId;
    private String studyAcronym;
    @Deprecated
    private String projectNumber;
    private String studyStatus;
    private List<String> possibleActions;}
