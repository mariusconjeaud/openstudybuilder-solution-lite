package org.CSDISC.DDF.model;

/**
 * Any activity performed by manual and/or instrumental means for the purpose of diagnosis, assessment, therapy,
 * prevention, or palliative care.
 * @author Chris Upkes
 */

public class Procedure {

    private final String procedureId;
    // A characterization or classification of the study procedure.
    private String procedureType;
    // A symbol or combination of symbols which is assigned to medical procedure.
    private Code procedureCode;

    public Procedure(String procedureId) {
        this.procedureId = procedureId;
    }

    public String getProcedureId() {
        return procedureId;
    }

    public String getProcedureType() {
        return procedureType;
    }

    public void setProcedureType(String procedureType) {
        this.procedureType = procedureType;
    }

    public Code getProcedureCode() {
        return procedureCode;
    }

    public void setProcedureCode(Code procedureCode) {
        this.procedureCode = procedureCode;
    }

}
