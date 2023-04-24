//package org.openstudybuilder.sdr.acct;
//
//import com.fasterxml.jackson.annotation.JsonProperty;
//import lombok.Getter;
//import lombok.Setter;
//import org.CSDISC.DDF.model.Code;
//import org.CSDISC.DDF.model.Objective;
//
//import java.util.List;
//
//@Getter @Setter
//public class AcctStudyObjective extends org.CSDISC.DDF.model.Objective {
//    @JsonProperty("objectiveLevel")
//    private List<Code> extObjectiveLevel;
//    public AcctStudyObjective(Objective objective) {
//        super(objective.getUuid());
//        this.setObjectiveDesc(objective.getObjectiveDesc());
//        this.setExtObjectiveLevel(List.of(objective.getObjectiveLevel()));
//        this.setObjectiveEndpoints(objective.getObjectiveEndpoints());
//    }
//}
