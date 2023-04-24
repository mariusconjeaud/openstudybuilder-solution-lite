//package org.openstudybuilder.sdr.acct;
//
//import com.fasterxml.jackson.annotation.JsonProperty;
//import lombok.Getter;
//import lombok.Setter;
//import org.CSDISC.DDF.model.Code;
//import org.CSDISC.DDF.model.Encounter;
//
//import java.util.ArrayList;
//import java.util.List;
//
//@Getter @Setter
//public class AcctStudyEpoch extends org.CSDISC.DDF.model.StudyEpoch {
//    @JsonProperty("studyEpochType")
//    private List<Code> extStudyEpochType;
//    private List<Encounter> encounters;
//
//    public AcctStudyEpoch(org.CSDISC.DDF.model.StudyEpoch studyEpoch) {
//        super(studyEpoch.getUuid());
//        this.extStudyEpochType = new ArrayList<>();
//        this.setStudyEpochDesc(studyEpoch.getStudyEpochDesc());
//        this.setStudyEpochName(studyEpoch.getStudyEpochName());
//        this.setSequenceInStudyDesign(studyEpoch.getSequenceInStudyDesign());
//    }
//}
