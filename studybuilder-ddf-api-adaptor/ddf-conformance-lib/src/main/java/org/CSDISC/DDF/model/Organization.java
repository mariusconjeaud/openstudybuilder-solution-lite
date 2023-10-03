package org.CSDISC.DDF.model;

/**
 * A formalized group of persons or other organizations collected together for a common purpose (such as administrative,
 * legal, political) and the infrastructure to carry out that purpose. (BRIDG)
 * @author Chris Upkes
 */

public class Organization {

    private final String organizationId;
    // The name of the organization that provides the identifier for the entity.
    private String organizationIdentifierScheme;
    // A unique symbol that establishes identity of the organization. (BRIDG)
    private String organizationIdentifier;
    // A non-unique textual identifier for the organization. (BRIDG)
    private String organizationName;
    // A characterization or classification of the formalized group of persons or other organizations collected
    // together for a common purpose (such as administrative, legal, political) and the infrastructure to carry
    // out that purpose.
    private Code organizationType;

    public Organization(String organizationId) {
        this.organizationId = organizationId;
    }

    public String getOrganizationId() {
        return organizationId;
    }

    public String getOrganizationIdentifierScheme() {
        return organizationIdentifierScheme;
    }

    public void setOrganizationIdentifierScheme(String organizationIdentifierScheme) {
        this.organizationIdentifierScheme = organizationIdentifierScheme;
    }

    public String getOrganizationIdentifier() {
        return organizationIdentifier;
    }

    public void setOrganizationIdentifier(String organizationIdentifier) {
        this.organizationIdentifier = organizationIdentifier;
    }

    public String getOrganizationName() {
        return organizationName;
    }

    public void setOrganizationName(String organizationName) {
        this.organizationName = organizationName;
    }

    public Code getOrganizationType() {
        return organizationType;
    }

    public void setOrganizationType(Code organizationType) {
        this.organizationType = organizationType;
    }
}
