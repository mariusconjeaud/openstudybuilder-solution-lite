package org.CSDISC.DDF.model;

import java.util.List;

/**
 * Contact between subject/patient and healthcare practitioner/researcher, during which an assessment
 * or activity is performed. Contact may be physical or virtual.
 * @author Chris Upkes
 */

public class Encounter {

    private final String encounterId;
    // The literal identifier (i.e., distinctive designation) for a protocol-defined clinical encounter.
    private String encounterName;
    // The textual representation of the protocol-defined clinical encounter.
    private String encounterDescription;
    // A characterization or classification of contact between subject/patient and healthcare
    // practitioner/researcher, during which an assessment or activity is performed.
    private Code encounterType;
    // The environment/setting where the event, intervention, or finding occurred.
    private Code encounterEnvironmentalSetting;
    // The means by which an interaction occurs between the subject/participant and person or entity (e.g., a device).
    private Code encounterContactMode;
    private TransitionRule transitionStartRule;
    private TransitionRule transitionEndRule;
    // A system identifier assigned to a clinical encounter that occurs immediately prior to the
    // current clinical encounter.
    private String previousEncounterId;
    // A system identifier assigned to a clinical encounter that occurs immediately after the
    // current clinical encounter.
    private String nextEncounterId;


    public Encounter(String encounterId) {
        this.encounterId = encounterId;
    }

    public String getEncounterId() {
        return encounterId;
    }

    public String getEncounterName() {
        return encounterName;
    }

    public void setEncounterName(String encounterName) {
        this.encounterName = encounterName;
    }

    public String getEncounterDescription() {
        return encounterDescription;
    }

    public void setEncounterDescription(String encounterDescription) {
        this.encounterDescription = encounterDescription;
    }

    public Code getEncounterType() {
        return encounterType;
    }

    public void setEncounterType(Code encounterType) {
        this.encounterType = encounterType;
    }

    public Code getEncounterEnvironmentalSetting() {
        return encounterEnvironmentalSetting;
    }

    public void setEncounterEnvironmentalSetting(Code encounterEnvironmentalSetting) {
        this.encounterEnvironmentalSetting = encounterEnvironmentalSetting;
    }

    public Code getEncounterContactMode() {
        return encounterContactMode;
    }

    public void setEncounterContactMode(Code encounterContactMode) {
        this.encounterContactMode = encounterContactMode;
    }

    public TransitionRule getStartRule() {
        return transitionStartRule;
    }

    public TransitionRule getTransitionStartRule() {
        return transitionStartRule;
    }

    public void setTransitionStartRule(TransitionRule transitionStartRule) {
        this.transitionStartRule = transitionStartRule;
    }

    public TransitionRule getTransitionEndRule() {
        return transitionEndRule;
    }

    public void setTransitionEndRule(TransitionRule transitionEndRule) {
        this.transitionEndRule = transitionEndRule;
    }

    public String getPreviousEncounterId() {
        return previousEncounterId;
    }

    public void setPreviousEncounterId(String previousEncounterId) {
        this.previousEncounterId = previousEncounterId;
    }

    public String getNextEncounterId() {
        return nextEncounterId;
    }

    public void setNextEncounterId(String nextEncounterId) {
        this.nextEncounterId = nextEncounterId;
    }


}
