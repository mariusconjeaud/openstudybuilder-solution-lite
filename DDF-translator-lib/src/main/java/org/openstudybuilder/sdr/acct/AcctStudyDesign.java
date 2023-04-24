//package org.openstudybuilder.sdr.acct;
//
//import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
//import com.fasterxml.jackson.annotation.JsonProperty;
//import lombok.Getter;
//import lombok.Setter;
//import org.CSDISC.DDF.model.Code;
//import org.openstudybuilder.model.CurrentMetadata;
//import org.openstudybuilder.model.StudyDesign;
//
//import java.util.ArrayList;
//import java.util.List;
//import java.util.UUID;
//
//
//@Getter @Setter
//@JsonIgnoreProperties({"trialIntentTypes", "interventionalModel"})
//public class AcctStudyDesign extends org.CSDISC.DDF.model.StudyDesign {
//
//    @JsonProperty("trialType")
//    private List<Code> extTrialTypes;
//    @JsonProperty("trialIntentType")
//    private List<Code> extTrialIntentTypes;
//    @JsonProperty("interventionModel")
//    private List<Code> interventionModel;
//
//    public AcctStudyDesign(CurrentMetadata studyMetadata) {
//        super(UUID.randomUUID());
//
//        extTrialTypes = new ArrayList<>();
//        extTrialIntentTypes = new ArrayList<>();
//        StudyDesign hlStudyDesign = studyMetadata.getHighLevelStudyDesign();
//
//        List<org.openstudybuilder.model.Code> trialTypes = hlStudyDesign.getTrialTypesCodes();
//        for (org.openstudybuilder.model.Code trialType: trialTypes) {
//            Code newTrialType = new Code(UUID.randomUUID());
//            newTrialType.setCode(trialType.getName());
//            newTrialType.setDecode(trialType.getName());
//            newTrialType.setCodeSystem(trialType.getTermUid());
//            // TODO - Check hardcoded system version
//            newTrialType.setCodeSystemVersion("1");
//            extTrialTypes.add(newTrialType);
//        }
//
//        List<org.openstudybuilder.model.Code> trialIntentTypes = studyMetadata.getStudyIntervention().getTrialIntentTypesCodes();
//        for (org.openstudybuilder.model.Code trialIntentTypeCode: trialIntentTypes) {
//            Code newTrialType = new Code(UUID.randomUUID());
//            newTrialType.setCode(trialIntentTypeCode.getName());
//            newTrialType.setDecode(trialIntentTypeCode.getName());
//            newTrialType.setCodeSystem(trialIntentTypeCode.getTermUid());
//            // TODO - Check hardcoded system version
//            newTrialType.setCodeSystemVersion("1");
//            extTrialIntentTypes.add(newTrialType);
//        }
//
//        org.openstudybuilder.model.Code interventionCode = studyMetadata.getStudyIntervention().getInterventionModelCode();
//        if (interventionCode != null) {
//            Code extInterventionCode = new Code(UUID.randomUUID());
//            extInterventionCode.setCode(interventionCode.getName());
//            extInterventionCode.setDecode(interventionCode.getName());
//            extInterventionCode.setCodeSystem(interventionCode.getTermUid());
//            extInterventionCode.setCodeSystemVersion("1");
//            interventionModel = List.of(extInterventionCode);
//        }
//
//    }
//}
