package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class Element {
    private String elementUid;
    private String studyUid;
    private int order;
    private String name;
    private String shortName;
    private String code;
    private String description;
    private ElementSubType elementType;
    private ElementSubType elementSubtype;
    private String startDate;
    private String endDate;
    private String userInitials;
    private String status;
    private String changeType;
    private boolean acceptedVersion;
    private String elementColour;
    private String endRule;
    private Duration plannedDuration;
    private String startRule;
    private int studyCompoundDosingCount;

}
