package org.CSDISC.DDF.model;

/**
 * A defined variable intended to reflect an outcome of interest that is statistically analyzed to address a particular
 * research question. NOTE: A precise definition of an endpoint typically specifies the type of assessments made,
 * the timing of those assessments, the assessment tools used, and possibly other details, as applicable,
 * such as how multiple assessments within an individual are to be combined. [After BEST Resource]
 * @author Chris Upkes
 */

public class Endpoint {

    private final String endpointId;
    // The textual representation of the study endpoint.
    private String endpointDescription;
    // The textual representation of the study endpoint purpose.
    private String endpointPurposeDescription;
    // A characterization or classification of the study endpoint that determines its category of
    // importance relative to other study endpoints.
    private Code endpointLevel;

    public Endpoint(String endpointId) {
        this.endpointId = endpointId;
    }

    public String getEndpointId() {
        return endpointId;
    }

    public String getEndpointDescription() {
        return endpointDescription;
    }

    public void setEndpointDescription(String endpointDescription) {
        this.endpointDescription = endpointDescription;
    }

    public String getEndpointPurposeDescription() {
        return endpointPurposeDescription;
    }

    public void setEndpointPurposeDescription(String endpointPurposeDescription) {
        this.endpointPurposeDescription = endpointPurposeDescription;
    }

    public Code getEndpointLevel() {
        return endpointLevel;
    }

    public void setEndpointLevel(Code endpointLevel) {
        this.endpointLevel = endpointLevel;
    }


}
