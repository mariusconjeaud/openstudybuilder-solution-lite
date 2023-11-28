package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class ObjectiveTemplate {

    private String name;
    private String namePlain;
    private String uid;
    private boolean editableInstance;
    private String startDate;
    private String endDate;
    private String status;
    private String version;
    private String changeDescription;
    private String userInitials;
    private String sequenceId;
    private String guidanceText;
    private List<String> possibleActions;
    private List<ParameterValue> parameters;
    private List<ParameterValue> defaultParameterValues;
    private Library library;
    private String libraryName;
    // TODO - This is refered as "DictionaryTerm"
    private List<Indication> indications;
    private boolean confirmatoryTesting;
    private int studyCount;
    // This is reffered as CTTermNameAndAttributes
    private List<CriteriaType> categories;
}
