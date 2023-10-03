//package org.openstudybuilder.sdr.acct;
//
//import com.fasterxml.jackson.annotation.JsonProperty;
//import lombok.Getter;
//import lombok.Setter;
//import org.CSDISC.DDF.model.Code;
//import org.CSDISC.DDF.model.Endpoint;
//
//import java.util.List;
//
//@Getter @Setter
//public class AcctStudyObjectiveEndpoint extends org.CSDISC.DDF.model.Endpoint {
//    @JsonProperty("endpointLevel")
//    private List<Code> extEndpointLevel;
//    // This is a field not available in CDISC endpoint
//    private String endpointPurposeDesc;
//
//    public AcctStudyObjectiveEndpoint(Endpoint endpoint) {
//        super(endpoint.getUuid());
//        this.setExtEndpointLevel(List.of(endpoint.getEndpointLevel()));
//        this.setEndpointDesc(endpoint.getEndpointDesc());
//        this.setEndpointPurpose(endpoint.getEndpointPurpose());
//    }
//}
