//package org.openstudybuilder.sdr.acct;
//
//import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
//import lombok.Getter;
//import lombok.Setter;
//import org.CDISC.DDF.model.Code;
//import org.CDISC.DDF.model.Organization;
//
//import java.util.UUID;
//
//@Getter @Setter
//@JsonIgnoreProperties({"organizationIdentifierScheme", "organizationIdentifier", "organizationName", "organizationType"})
//public class AcctStudyIdentOrganisation extends org.CDISC.DDF.model.Organization {
//    private String organisationName;
//    private Code organisationType;
//    private String organisationIdentifier;
//    private String organisationIdentifierScheme;
//
//    public AcctStudyIdentOrganisation(UUID organizationId) {
//        super(organizationId);
//    }
//}
