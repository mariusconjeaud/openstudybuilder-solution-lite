package org.CSDISC.DDF.model;

import java.util.List;

/**
 * The condition, disease or disorder that the clinical trial is intended to investigate or address.
 * @author Chris Upkes
 */

public class Indication {

    private final String indicationId;
    // The condition, disease or disorder that the clinical trial is intended to investigate or address.
    private String indicationDescription;
    // A short sequence of characters that represents the disease indication.
    private List<Code> codes;

    public Indication(String indicationId) {
        this.indicationId = indicationId;
    }

    public String getIndicationId() {
        return indicationId;
    }

    public String getIndicationDescription() {
        return indicationDescription;
    }

    public void setIndicationDescription(String indicationDescription) {
        this.indicationDescription = indicationDescription;
    }

    public List<Code> getCodes() {
        return codes;
    }

    public void setCodes(List<Code> codes) {
        this.codes = codes;
    }
}
