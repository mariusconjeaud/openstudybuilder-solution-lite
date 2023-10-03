//package org.openstudybuilder.sdr.acct;
//
//import com.fasterxml.jackson.annotation.JsonProperty;
//import lombok.Getter;
//import lombok.Setter;
//import org.CSDISC.DDF.model.Code;
//
//import java.util.List;
//import java.util.UUID;
//
//@Getter @Setter
//public class AcctStudyEncounter extends org.CSDISC.DDF.model.Encounter {
//    @JsonProperty("encounterType")
//    private List<Code> extEncounterType;
//    @JsonProperty("encounterContactMode")
//    private List<Code> extEncounterContactMode;
//    @JsonProperty("encounterEnvironmentalSetting")
//    private List<Code> extEncounterEnvironmentalSetting;
//
//    public AcctStudyEncounter(org.CSDISC.DDF.model.Encounter encounter) {
//        super(encounter.getUuid());
//        this.setExtEncounterType(List.of(encounter.getEncounterType()));
//        this.setExtEncounterContactMode(List.of(encounter.getEncounterContactMode()));
//        this.setEncounterName(encounter.getEncounterName());
//        this.setEncounterDesc(encounter.getEncounterDesc());
//        this.setExtEncounterEnvironmentalSetting(List.of(encounter.getEncounterEnvironmentalSetting()));
//        this.setSequenceInStudyDesign(encounter.getSequenceInStudyDesign());
//        this.setStartRule(encounter.getStartRule());
//        this.setEndRule(encounter.getEndRule());
//    }
//}
