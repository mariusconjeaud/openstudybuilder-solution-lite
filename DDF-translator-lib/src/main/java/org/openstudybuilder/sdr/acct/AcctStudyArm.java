//package org.openstudybuilder.sdr.acct;
//
//import com.fasterxml.jackson.annotation.JsonProperty;
//import lombok.Getter;
//import lombok.Setter;
//import org.CSDISC.DDF.model.Code;
//
//import java.util.ArrayList;
//import java.util.List;
//
//@Getter @Setter
//public class AcctStudyArm extends org.CSDISC.DDF.model.StudyArm {
//    @JsonProperty("studyArmType")
//    private List<Code> extArmType;
//    @JsonProperty("studyArmDataOriginType")
//    private List<Code> extStudyArmDataOriginType;
//
//    public AcctStudyArm(org.CSDISC.DDF.model.StudyArm studyArm) {
//        super(studyArm.getUuid());
//        this.extArmType = List.of(studyArm.getStudyArmType());
//        this.extStudyArmDataOriginType = List.of(studyArm.getStudyArmDataOriginType());
//        this.setStudyArmDataOriginDesc(studyArm.getStudyArmDataOriginDesc());
//        this.setStudyArmDesc(studyArm.getStudyArmDesc());
//        this.setStudyArmName(studyArm.getStudyArmName());
//    }
//}
