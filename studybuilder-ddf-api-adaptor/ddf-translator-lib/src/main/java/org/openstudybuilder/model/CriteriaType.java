package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class CriteriaType {

    private String termUid;
    private String catalogueName;
    private String changeDescription;
    private String codelistUid;
    private String conceptId;
    private String definition;
    private String endDate;
    private String libraryName;
    private String nameSubmissionValue;
    private String nciPreferredName;
    private List<String> possibleActions;
    private String startDate;
    private String status;
    private String userInitials;
    private String version;
    private String sponsorPreferredName;
    private String sponsorPreferredNameSentenceCase;
    private int order;
    // TODO: check if "attributes" parameter is needed
}
