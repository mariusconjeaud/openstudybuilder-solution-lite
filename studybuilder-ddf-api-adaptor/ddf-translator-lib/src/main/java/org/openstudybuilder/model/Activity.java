package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;
import java.util.Map;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class Activity {

    private String abbreviation;
    private List<Map<String, String>> activityGroupings;
    private String changeDescription;
    private String definition;
    private String endDate;
    private String libraryName;
    private String name;
    private String nameSentenceCase;
    private List<String> possibleActions;
    private String startDate;
    private String status;
    private String uid;
    private String userInitials;
    private String version;
    private String requestRationale;
    private String replacedByActivity;
}
