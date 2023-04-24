package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class FlowChartGroup {

    private String catalogueName;
    private String changeDescription;
    private String codelistUid;
    private String endDate;
    private String libraryName;
    private String order;
    private List<String> possibleActions;
    private String sponsorPreferredName;
    private String sponsorPreferredNameSentenceCase;
    private String startDate;
    private String status;
    private String termUid;
    private String userInitials;
    private String version;

    public String getCatalogueName() {
        return catalogueName;
    }

    public void setCatalogueName(String catalogueName) {
        this.catalogueName = catalogueName;
    }

    public String getChangeDescription() {
        return changeDescription;
    }

    public void setChangeDescription(String changeDescription) {
        this.changeDescription = changeDescription;
    }

    public String getCodelistUid() {
        return codelistUid;
    }

    public void setCodelistUid(String codelistUid) {
        this.codelistUid = codelistUid;
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

    public String getOrder() {
        return order;
    }

    public void setOrder(String order) {
        this.order = order;
    }

    public List<String> getPossibleActions() {
        return possibleActions;
    }

    public void setPossibleActions(List<String> possibleActions) {
        this.possibleActions = possibleActions;
    }

    public String getSponsorPreferredName() {
        return sponsorPreferredName;
    }

    public void setSponsorPreferredName(String sponsorPreferredName) {
        this.sponsorPreferredName = sponsorPreferredName;
    }

    public String getSponsorPreferredNameSentenceCase() {
        return sponsorPreferredNameSentenceCase;
    }

    public void setSponsorPreferredNameSentenceCase(String sponsorPreferredNameSentenceCase) {
        this.sponsorPreferredNameSentenceCase = sponsorPreferredNameSentenceCase;
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

    public String getTermUid() {
        return termUid;
    }

    public void setTermUid(String termUid) {
        this.termUid = termUid;
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
}
