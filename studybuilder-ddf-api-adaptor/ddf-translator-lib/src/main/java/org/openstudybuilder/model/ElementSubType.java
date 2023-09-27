package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
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

    public ElementSubType(){

    }

    public String getTermUid() {
        return termUid;
    }

    public void setTermUid(String termUid) {
        this.termUid = termUid;
    }

    public String getCatalogueName() {
        return catalogueName;
    }

    public void setCatalogueName(String catalogueName) {
        this.catalogueName = catalogueName;
    }

    public String getCodelistUid() {
        return codelistUid;
    }

    public void setCodelistUid(String codelistUid) {
        this.codelistUid = codelistUid;
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

    public int getOrder() {
        return order;
    }

    public void setOrder(int order) {
        this.order = order;
    }

    public String getLibraryName() {
        return libraryName;
    }

    public void setLibraryName(String libraryName) {
        this.libraryName = libraryName;
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



}
