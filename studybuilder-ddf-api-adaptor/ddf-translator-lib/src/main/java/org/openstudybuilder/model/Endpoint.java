package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class Endpoint {

    private String uid;
    private String name;
    private String namePlain;
    private String startDate;
    private String endDate;
    private String status;
    private String version;
    private String changeDescription;
    private String userInitials;
    private List<String> possibleActions;
    private EndpointTemplate endpointTemplate;
    private List<ParameterValue> parameterTerms;
    private Library library;
    private int studyCount;
}
