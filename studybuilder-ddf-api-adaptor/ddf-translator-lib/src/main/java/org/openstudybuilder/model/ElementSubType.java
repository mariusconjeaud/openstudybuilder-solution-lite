package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class ElementSubType {

    private String termUid;
    private String catalogueName;
    private String codelistUid;
    private String sponsorPreferredName;
    private String sponsorPreferredNameSentenceCase;
    private int order;
    private String libraryName;
    private String startDate;
    private String endDate;
    private String status;
    private String version;
    private String changeDescription;
    private String userInitials;
    private List<String> possibleActions;
}
