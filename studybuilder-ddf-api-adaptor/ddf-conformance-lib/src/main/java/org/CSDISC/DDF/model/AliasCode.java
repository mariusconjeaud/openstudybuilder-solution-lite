package org.CSDISC.DDF.model;

import java.util.List;

/** An alternative symbol or combination of symbols which is assigned to the members of a collection.
 * @author Chris Upkes
 */

public class AliasCode {

    private final String aliasCodeId;
    private Code standardCode;
    private List<Code> standardCodeAliases;

    public AliasCode(String aliasCodeId) {
        this.aliasCodeId = aliasCodeId;
    }

    public Code getStandardCode() {
        return standardCode;
    }

    public void setStandardCode(Code standardCode) {
        this.standardCode = standardCode;
    }

    public List<Code> getStandardCodeAliases() {
        return standardCodeAliases;
    }

    public void setStandardCodeAliases(List<Code> standardCodeAliases) {
        this.standardCodeAliases = standardCodeAliases;
    }
    

}
