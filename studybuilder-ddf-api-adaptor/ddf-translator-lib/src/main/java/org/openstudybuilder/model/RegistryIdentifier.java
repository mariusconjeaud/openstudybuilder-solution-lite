package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
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
}
