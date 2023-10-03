package org.CSDISC.DDF.model;

/**
 * @author Chris Upkes
 */

public class WorkflowItem {

    private final String workflowItemId;
    // The textual representation of the workflow item.
    private String workflowItemDescription;
    // A system identifier assigned to a workflow item that occurs immediately prior to the current workflow item.
    private String previousWorkflowItemId;
    // A system identifier assigned to a workflow item that occurs immediately prior to the current workflow item.
    private String nextWorkflowItemId;
    private Encounter workflowItemEncounter;
    private Activity workflowItemActivity;

    public WorkflowItem(String workflowItemId) {
        this.workflowItemId = workflowItemId;
    }

    public String getWorkflowItemId() {
        return workflowItemId;
    }

    public String getWorkflowItemDescription() {
        return workflowItemDescription;
    }

    public void setWorkflowItemDescription(String workflowItemDescription) {
        this.workflowItemDescription = workflowItemDescription;
    }

    public String getPreviousWorkflowItemId() {
        return previousWorkflowItemId;
    }

    public void setPreviousWorkflowItemId(String previousWorkflowItemId) {
        this.previousWorkflowItemId = previousWorkflowItemId;
    }

    public Encounter getWorkflowItemEncounter() {
        return workflowItemEncounter;
    }

    public void setWorkflowItemEncounter(Encounter workflowItemEncounter) {
        this.workflowItemEncounter = workflowItemEncounter;
    }

    public Activity getWorkflowItemActivity() {
        return workflowItemActivity;
    }

    public void setWorkflowItemActivity(Activity workflowItemActivity) {
        this.workflowItemActivity = workflowItemActivity;
    }

    public String getNextWorkflowItemId() {
        return nextWorkflowItemId;
    }

    public void setNextWorkflowItemId(String nextWorkflowItemId) {
        this.nextWorkflowItemId = nextWorkflowItemId;
    }
}
