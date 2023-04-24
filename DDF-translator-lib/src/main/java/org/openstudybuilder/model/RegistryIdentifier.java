package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class RegistryIdentifier {

    private String ctGovId;
    private Code ctGovIdNullValueCode;
    private String eudractId;
    private Code eudractIdNullValueCode;
    private String universalTrialNumberUTN;
    private Code universalTrialNumberUtnNullValueCode;
    private String japaneseTrialRegistryIdJapic;
    private Code japaneseTrialRegistryIdJapicNullValueCode;
    private String investigationalNewDrugApplicationNumberInd;
    private Code investigationalNewDrugApplicationNumberIndNullValueCode;

    public String getCtGovId() {
        return ctGovId;
    }

    public void setCtGovId(String ctGovId) {
        this.ctGovId = ctGovId;
    }

    public Code getCtGovIdNullValueCode() {
        return ctGovIdNullValueCode;
    }

    public void setCtGovIdNullValueCode(Code ctGovIdNullValueCode) {
        this.ctGovIdNullValueCode = ctGovIdNullValueCode;
    }

    public String getEudractId() {
        return eudractId;
    }

    public void setEudractId(String eudractId) {
        this.eudractId = eudractId;
    }

    public Code getEudractIdNullValueCode() {
        return eudractIdNullValueCode;
    }

    public void setEudractIdNullValueCode(Code eudractIdNullValueCode) {
        this.eudractIdNullValueCode = eudractIdNullValueCode;
    }

    public String getUniversalTrialNumberUTN() {
        return universalTrialNumberUTN;
    }

    public void setUniversalTrialNumberUTN(String universalTrialNumberUTN) {
        this.universalTrialNumberUTN = universalTrialNumberUTN;
    }

    public Code getUniversalTrialNumberUtnNullValueCode() {
        return universalTrialNumberUtnNullValueCode;
    }

    public void setUniversalTrialNumberUtnNullValueCode(Code universalTrialNumberUtnNullValueCode) {
        this.universalTrialNumberUtnNullValueCode = universalTrialNumberUtnNullValueCode;
    }

    public String getJapaneseTrialRegistryIdJapic() {
        return japaneseTrialRegistryIdJapic;
    }

    public void setJapaneseTrialRegistryIdJapic(String japaneseTrialRegistryIdJapic) {
        this.japaneseTrialRegistryIdJapic = japaneseTrialRegistryIdJapic;
    }

    public Code getJapaneseTrialRegistryIdJapicNullValueCode() {
        return japaneseTrialRegistryIdJapicNullValueCode;
    }

    public void setJapaneseTrialRegistryIdJapicNullValueCode(Code japaneseTrialRegistryIdJapicNullValueCode) {
        this.japaneseTrialRegistryIdJapicNullValueCode = japaneseTrialRegistryIdJapicNullValueCode;
    }

    public String getInvestigationalNewDrugApplicationNumberInd() {
        return investigationalNewDrugApplicationNumberInd;
    }

    public void setInvestigationalNewDrugApplicationNumberInd(String investigationalNewDrugApplicationNumberInd) {
        this.investigationalNewDrugApplicationNumberInd = investigationalNewDrugApplicationNumberInd;
    }

    public Code getInvestigationalNewDrugApplicationNumberIndNullValueCode() {
        return investigationalNewDrugApplicationNumberIndNullValueCode;
    }

    public void setInvestigationalNewDrugApplicationNumberIndNullValueCode(Code investigationalNewDrugApplicationNumberIndNullValueCode) {
        this.investigationalNewDrugApplicationNumberIndNullValueCode = investigationalNewDrugApplicationNumberIndNullValueCode;
    }
}
