package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class CriteriaTemplate {

    private String name;
    private String namePlain;
    private String guidanceText;
    private String uid;
    private String sequenceId;
    private String startDate;
    private String endDate;
    private String status;
    private String version;
    private String changeDescription;
    private String userInitials;
    private List<String> possibleActions;
    // TODO: check parameters model
    private List<ParameterValue> parameters;
    private List<ParameterValue> defaultParameterValues;
    private Library library;
    // This corresponds to CTTermNameAndAttributes
    private CriteriaType type;
    private List<Indication> indications;
    // Corresponds to CTTermNameAndAttributes
    private List<CriteriaType> categories;
    // Corresponds to CTTermNameAndAttributes
    private List<CriteriaType> subCategories;
    private int studyCount;
}
