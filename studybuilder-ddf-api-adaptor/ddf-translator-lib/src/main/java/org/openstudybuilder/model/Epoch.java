package org.openstudybuilder.model;


import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class Epoch {

    private String uid;
    private String studyUid;
    private String startRule;
    private String endRule;
    private String epoch;
    private String epochSubtype;
    private String durationUnit;
    private int order;
    private String description;
    private int duration;
    private String colorHash;
    private String epochName;
    private String epochSubtypeName;
    private String epochType;
    private String epochTypeName;
    private int startDay;
    private int endDay;
    private int startWeek;
    private int endWeek;
    private String startDate;
    private String status;
    private String userInitials;
    private List<String> possibleActions;
    private String changeDescription;
    private int studyVisitCount;
}
