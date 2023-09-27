package org.CSDISC.DDF.model;

import java.util.List;

/**
 * The operational aspect of a work procedure: how tasks are structured, who performs them,
 * what their relative order is, how they are synchronized, how information flows to support the tasks
 * and how tasks are being tracked.
 * @author Chris Upkes
 */

public class Workflow {

    private final String workflowId;
    // The textual representation of the workflow.
    private String workflowDescription;
    // The textual representation of the workflow item.
    private List<WorkflowItem> workflowItems;

    public Workflow(String workFlowUUID) {
        this.workflowId = workFlowUUID;
    }

    public String getWorkflowId() {
        return workflowId;
    }

    public String getWorkflowDescription() {
        return workflowDescription;
    }

    public void setWorkflowDescription(String workflowDescription) {
        this.workflowDescription = workflowDescription;
    }

    public List<WorkflowItem> getWorkflowItems() {
        return workflowItems;
    }

    public void setWorkflowItems(List<WorkflowItem> workflowItems) {
        this.workflowItems = workflowItems;
    }
}
