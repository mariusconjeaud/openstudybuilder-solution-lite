package org.CSDISC.DDF.model;

/**
 *
 * A symbol or combination of symbols which is assigned to the members of a collection.
 * @author Chris Upkes
 */

public class Code {

    private final String codeId;
    // The literal value of a code.
    private String code;
    // The literal identifier (i.e., distinctive designation) of the system used to assign and/or manage codes.
    private String codeSystem;
    // The version of the code system.
    private String codeSystemVersion;
    // Standardized or dictionary-derived human readable text associated with a code.
    private String decode;

    public Code(String codeId) {
        this.codeId = codeId;
    }

    public String getCodeId() {
        return codeId;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getCodeSystem() {
        return codeSystem;
    }

    public void setCodeSystem(String codeSystem) {
        this.codeSystem = codeSystem;
    }

    public String getCodeSystemVersion() {
        return codeSystemVersion;
    }

    public void setCodeSystemVersion(String codeSystemVersion) {
        this.codeSystemVersion = codeSystemVersion;
    }

    public String getDecode() {
        return decode;
    }

    public void setDecode(String decode) {
        this.decode = decode;
    }




}
