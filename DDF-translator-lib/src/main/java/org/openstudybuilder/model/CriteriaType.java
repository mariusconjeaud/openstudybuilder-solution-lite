package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class CriteriaType {
    private String termUid;
    private String catalogueName;
    private String changeDescription;
    private String codeSubmissionValue;
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

    public String getChangeDescription() {
        return changeDescription;
    }

    public void setChangeDescription(String changeDescription) {
        this.changeDescription = changeDescription;
    }

    public String getCodeSubmissionValue() {
        return codeSubmissionValue;
    }

    public void setCodeSubmissionValue(String codeSubmissionValue) {
        this.codeSubmissionValue = codeSubmissionValue;
    }

    public String getCodelistUid() {
        return codelistUid;
    }

    public void setCodelistUid(String codelistUid) {
        this.codelistUid = codelistUid;
    }

    public String getConceptId() {
        return conceptId;
    }

    public void setConceptId(String conceptId) {
        this.conceptId = conceptId;
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

    public String getNameSubmissionValue() {
        return nameSubmissionValue;
    }

    public void setNameSubmissionValue(String nameSubmissionValue) {
        this.nameSubmissionValue = nameSubmissionValue;
    }

    public String getNciPreferredName() {
        return nciPreferredName;
    }

    public void setNciPreferredName(String nciPreferredName) {
        this.nciPreferredName = nciPreferredName;
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
}
