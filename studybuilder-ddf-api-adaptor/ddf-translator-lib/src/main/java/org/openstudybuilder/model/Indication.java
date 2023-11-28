package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class Indication {

    private String abbreviation;
    private String changeDescription;
    private String definition;
    private String dictionaryId;
    private String endDate;
    private String libraryName;
    private String name;
    private String nameSentenceCase;
    private List<String> possibleActions;
    private String startDate;
    private String status;
    private String termUid;
    private String userInitials;
    private String version;
}
