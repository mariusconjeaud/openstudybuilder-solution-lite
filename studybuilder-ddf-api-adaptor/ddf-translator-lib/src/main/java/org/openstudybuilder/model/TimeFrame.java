package org.openstudybuilder.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class TimeFrame {
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
    @JsonProperty("timeframe_template")
    private TimeFrameTemplate timeFrameTemplate;
    private List<ParameterValue> parameterValues;
    private Library library;

    public String getUid() {
        return uid;
    }

    public void setUid(String uid) {
        this.uid = uid;
    }

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

    public TimeFrameTemplate getTimeFrameTemplate() {
        return timeFrameTemplate;
    }

    public void setTimeFrameTemplate(TimeFrameTemplate timeFrameTemplate) {
        this.timeFrameTemplate = timeFrameTemplate;
    }

    public List<ParameterValue> getParameterValues() {
        return parameterValues;
    }

    public void setParameterValues(List<ParameterValue> parameterValues) {
        this.parameterValues = parameterValues;
    }

    public Library getLibrary() {
        return library;
    }

    public void setLibrary(Library library) {
        this.library = library;
    }
}
