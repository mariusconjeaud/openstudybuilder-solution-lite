package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class ActivityGroup {

    private String abbreviation;
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
}
