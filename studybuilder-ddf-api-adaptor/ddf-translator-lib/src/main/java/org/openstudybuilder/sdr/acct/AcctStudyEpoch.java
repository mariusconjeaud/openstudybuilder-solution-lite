//package org.openstudybuilder.sdr.acct;
//
//import com.fasterxml.jackson.annotation.JsonProperty;
//import lombok.Getter;
//import lombok.Setter;
//import org.CDISC.DDF.model.Code;
//import org.CDISC.DDF.model.Encounter;
//
//import java.util.ArrayList;
//import java.util.List;
//
//@Getter @Setter
//public class AcctStudyEpoch extends org.CDISC.DDF.model.StudyEpoch {
//    @JsonProperty("studyEpochType")
//    private List<Code> extStudyEpochType;
//    private List<Encounter> encounters;
//
//    public AcctStudyEpoch(org.CDISC.DDF.model.StudyEpoch studyEpoch) {
//        super(studyEpoch.getUuid());
//        this.extStudyEpochType = new ArrayList<>();
//        this.setStudyEpochDesc(studyEpoch.getStudyEpochDesc());
//        this.setStudyEpochName(studyEpoch.getStudyEpochName());
//        this.setSequenceInStudyDesign(studyEpoch.getSequenceInStudyDesign());
//    }
//}
