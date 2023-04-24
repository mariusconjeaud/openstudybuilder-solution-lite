package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;
import java.util.Map;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class Activity {

    private String abbreviation;
    private List<Map<String, String>> activityGroups;
    private List<Map<String, String>> activitySubGroups;
    private Map<String, String> activityGroup;
    private Map<String, String> activitySubgroup;
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

    public String getAbbreviation() {
        return abbreviation;
    }

    public void setAbbreviation(String abbreviation) {
        this.abbreviation = abbreviation;
    }

    public List<Map<String, String>> getActivityGroups() {
        return activityGroups;
    }

    public void setActivityGroups(List<Map<String, String>> activityGroups) {
        this.activityGroups = activityGroups;
    }

    public List<Map<String, String>> getActivitySubGroups() {
        return activitySubGroups;
    }

    public void setActivitySubGroups(List<Map<String, String>> activitySubGroups) {
        this.activitySubGroups = activitySubGroups;
    }

    public Map<String, String> getActivityGroup() {
        return activityGroup;
    }

    public void setActivityGroup(Map<String, String> activityGroup) {
        this.activityGroup = activityGroup;
    }

    public Map<String, String> getActivitySubgroup() {
        return activitySubgroup;
    }

    public void setActivitySubgroup(Map<String, String> activitySubgroup) {
        this.activitySubgroup = activitySubgroup;
    }

    public String getChangeDescription() {
        return changeDescription;
    }

    public void setChangeDescription(String changeDescription) {
        this.changeDescription = changeDescription;
    }

    public String getDefinition() {
        return definition;
    }

    public void setDefinition(String definition) {
        this.definition = definition;
    }

    public String getEndDate() {
        return endDate;
    }

    public void setEndDate(String endDate) {
        this.endDate = endDate;
    }

    public String getLibraryName() {
        return libraryName;
    }

    public void setLibraryName(String libraryName) {
        this.libraryName = libraryName;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getNameSentenceCase() {
        return nameSentenceCase;
    }

    public void setNameSentenceCase(String nameSentenceCase) {
        this.nameSentenceCase = nameSentenceCase;
    }

    public List<String> getPossibleActions() {
        return possibleActions;
    }

    public void setPossibleActions(List<String> possibleActions) {
        this.possibleActions = possibleActions;
    }

    public String getStartDate() {
        return startDate;
    }

    public void setStartDate(String startDate) {
        this.startDate = startDate;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getUid() {
        return uid;
    }

    public void setUid(String uid) {
        this.uid = uid;
    }

    public String getUserInitials() {
        return userInitials;
    }

    public void setUserInitials(String userInitials) {
        this.userInitials = userInitials;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public String getRequestRationale() {
        return requestRationale;
    }

    public void setRequestRationale(String requestRationale) {
        this.requestRationale = requestRationale;
    }

    public String getReplacedByActivity() {
        return replacedByActivity;
    }

    public void setReplacedByActivity(String replacedByActivity) {
        this.replacedByActivity = replacedByActivity;
    }
}
