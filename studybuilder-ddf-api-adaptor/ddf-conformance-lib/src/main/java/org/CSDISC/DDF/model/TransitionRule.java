package org.CSDISC.DDF.model;

/**
 * A guide that governs the allocation of subjects to operational options at a discrete decision point or branch
 * (e.g., assignment to a particular arm, discontinuation) within a clinical trial plan.
 * @author Chris Upkes
 */

public class TransitionRule {

    private final String transitionRuleId;
    // The textual representation of the transition rule.
    private String transitionRuleDescription;

    public TransitionRule(String ruleId) {
        this.transitionRuleId = ruleId;
    }

    public String getTransitionRuleId() {
        return transitionRuleId;
    }

    public String getTransitionRuleDescription() {
        return transitionRuleDescription;
    }

    public void setTransitionRuleDescription(String transitionRuleDescription) {
        this.transitionRuleDescription = transitionRuleDescription;
    }
}
