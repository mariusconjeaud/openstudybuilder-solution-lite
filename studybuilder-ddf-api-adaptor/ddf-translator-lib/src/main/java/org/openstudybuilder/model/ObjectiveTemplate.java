package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
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
    private List<String> possibleActions;
    private List<ParameterValue> parameters;
    private List<ParameterValue> defaultParameterValues;
    private Library library;
    // TODO - This is refered as "DictionaryTerm"
    private List<Indication> indications;
    private boolean confirmatoryTesting;
    private int studyCount;
    // This is reffered as CTTermNameAndAttributes
    private List<CriteriaType> categories;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getNamePlain() {
        return namePlain;
    }

    public void setNamePlain(String namePlain) {
        this.namePlain = namePlain;
    }

    public String getUid() {
        return uid;
    }

    public void setUid(String uid) {
        this.uid = uid;
    }

    public boolean isEditableInstance() {
        return editableInstance;
    }

    public void setEditableInstance(boolean editableInstance) {
        this.editableInstance = editableInstance;
    }

    public String getStartDate() {
        return startDate;
    }

    public void setStartDate(String startDate) {
        this.startDate = startDate;
    }

    public String getEndDate() {
        return endDate;
    }

    public void setEndDate(String endDate) {
        this.endDate = endDate;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public String getChangeDescription() {
        return changeDescription;
    }

    public void setChangeDescription(String changeDescription) {
        this.changeDescription = changeDescription;
    }

    public String getUserInitials() {
        return userInitials;
    }

    public void setUserInitials(String userInitials) {
        this.userInitials = userInitials;
    }

    public List<String> getPossibleActions() {
        return possibleActions;
    }

    public void setPossibleActions(List<String> possibleActions) {
        this.possibleActions = possibleActions;
    }

    public List<ParameterValue> getParameters() {
        return parameters;
    }

    public void setParameters(List<ParameterValue> parameters) {
        this.parameters = parameters;
    }

    public List<ParameterValue> getDefaultParameterValues() {
        return defaultParameterValues;
    }

    public void setDefaultParameterValues(List<ParameterValue> defaultParameterValues) {
        this.defaultParameterValues = defaultParameterValues;
    }

    public Library getLibrary() {
        return library;
    }

    public void setLibrary(Library library) {
        this.library = library;
    }

    public List<Indication> getIndications() {
        return indications;
    }

    public void setIndications(List<Indication> indications) {
        this.indications = indications;
    }

    public boolean isConfirmatoryTesting() {
        return confirmatoryTesting;
    }

    public void setConfirmatoryTesting(boolean confirmatoryTesting) {
        this.confirmatoryTesting = confirmatoryTesting;
    }

    public int getStudyCount() {
        return studyCount;
    }

    public void setStudyCount(int studyCount) {
        this.studyCount = studyCount;
    }

    public List<CriteriaType> getCategories() {
        return categories;
    }

    public void setCategories(List<CriteriaType> categories) {
        this.categories = categories;
    }
}
