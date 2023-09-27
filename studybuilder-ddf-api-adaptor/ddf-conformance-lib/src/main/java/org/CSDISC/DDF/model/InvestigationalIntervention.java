package org.CSDISC.DDF.model;


import java.util.List;

/**
 * The drug, device, therapy, or process under investigation in a clinical study that is believed to have an effect
 * on outcomes of interest in a study.
 * [After https://grants.nih.gov/grants/policy/faq_clinical_trial_definition.htm#5224] (CDISC-Glossary)
 * @author Chris Upkes
 */

public class InvestigationalIntervention {

    private final String investigationalInterventionId;
    // The textual representation of the study intervention.
    private String interventionDescription;
    // A short sequence of characters that represents the investigational intervention.
    private List<Code> codes;

    public InvestigationalIntervention(String investigationalInterventionId) {
        this.investigationalInterventionId = investigationalInterventionId;
    }

    public String getInvestigationalInterventionId() {
        return investigationalInterventionId;
    }

    public String getInterventionDescription() {
        return interventionDescription;
    }

    public void setInterventionDescription(String interventionDescription) {
        this.interventionDescription = interventionDescription;
    }


    public List<Code> getCodes() {
        return codes;
    }

    public void setCodes(List<Code> codes) {
        this.codes = codes;
    }
}
