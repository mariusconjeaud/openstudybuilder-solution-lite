package org.CSDISC.DDF.model;

import java.util.Date;

/**
 * A plan at a particular point in time for a formal investigation to assess the utility, impact, pharmacological,
 * physiological, and/or psychological effects of a particular treatment, procedure, drug, device, biologic,
 * food product, cosmetic, care plan, or subject characteristic. (BRIDG)
 * @author Chris Upkes
 */

public class StudyProtocolVersion {

    private final String studyProtocolVersionId;
    // The short descriptive name for the protocol.
    private String briefTitle;
    // The formal descriptive name for the protocol.
    private String officialTitle;
    // The descriptive name of the protocol that is intended for the lay public, written in easily understood language.
    private String publicTitle;
    // A more extensive descriptive name of the protocol that is intended for medical professionals,
    // written using medical and scientific language.
    private String scientificTitle;
    // A plan at a particular point in time for a formal investigation to assess the utility, impact,
    // pharmacological, physiological, and/or psychological effects of a particular treatment, procedure,
    // drug, device, biologic, food product, cosmetic, care plan, or subject characteristic. (BRIDG)
    private String protocolVersion;
    // A written description of a change(s) to, or formal clarification of, a protocol. (ICH E6)
    private String protocolAmendment;
    // The date and time specifying when the protocol amendment takes effect or becomes operative.
    private Date protocolEffectiveDate;
    // A condition of the protocol at a point in time with respect to its state of readiness for implementation.
    private Code protocolStatus;

    public StudyProtocolVersion(String studyProtocolVersionId) {
        this.studyProtocolVersionId = studyProtocolVersionId;
    }

    public String getStudyProtocolVersionId(){
        return studyProtocolVersionId;
    }

    public String getBriefTitle() {
        return briefTitle;
    }

    public void setBriefTitle(String briefTitle) {
        this.briefTitle = briefTitle;
    }

    public String getOfficialTitle() {
        return officialTitle;
    }

    public void setOfficialTitle(String officialTitle) {
        this.officialTitle = officialTitle;
    }

    public String getPublicTitle() {
        return publicTitle;
    }

    public void setPublicTitle(String publicTitle) {
        this.publicTitle = publicTitle;
    }

    public String getScientificTitle() {
        return scientificTitle;
    }

    public void setScientificTitle(String scientificTitle) {
        this.scientificTitle = scientificTitle;
    }

    public String getProtocolVersion() {
        return protocolVersion;
    }

    public void setProtocolVersion(String protocolVersion) {
        this.protocolVersion = protocolVersion;
    }

    public String getProtocolAmendment() {
        return protocolAmendment;
    }

    public void setProtocolAmendment(String protocolAmendment) {
        this.protocolAmendment = protocolAmendment;
    }

    public Date getProtocolEffectiveDate() {
        return protocolEffectiveDate;
    }

    public void setProtocolEffectiveDate(Date protocolEffectiveDate) {
        this.protocolEffectiveDate = protocolEffectiveDate;
    }

    public Code getProtocolStatus() {
        return protocolStatus;
    }

    public void setProtocolStatus(Code protocolStatus) {
        this.protocolStatus = protocolStatus;
    }
}
