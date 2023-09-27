package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class StudyActivitySection {

    private boolean isAcceptedVersion;
    private Activity activity;
    private FlowChartGroup flowchartGroup;
    private String latestActivity;
    private String note;
    private int order;
    private boolean showActivityGroupInProtocolFlowchart;
    private boolean showActivityInProtocolFlowchart;
    private boolean showActivitySubgroupInProtocolFlowchart;
    private String startDate;
    private String studyActivityUid;
    private String studyUid;
    private String userInitials;
    private String changeType;

    public boolean isAcceptedVersion() {
        return isAcceptedVersion;
    }

    public void setAcceptedVersion(boolean acceptedVersion) {
        isAcceptedVersion = acceptedVersion;
    }

    public Activity getActivity() {
        return activity;
    }

    public void setActivity(Activity activity) {
        this.activity = activity;
    }

    public FlowChartGroup getFlowchartGroup() {
        return flowchartGroup;
    }

    public void setFlowchartGroup(FlowChartGroup flowchartGroup) {
        this.flowchartGroup = flowchartGroup;
    }

    public String getLatestActivity() {
        return latestActivity;
    }

    public void setLatestActivity(String latestActivity) {
        this.latestActivity = latestActivity;
    }

    public String getNote() {
        return note;
    }

    public void setNote(String note) {
        this.note = note;
    }

    public int getOrder() {
        return order;
    }

    public void setOrder(int order) {
        this.order = order;
    }

    public boolean isShowActivityGroupInProtocolFlowchart() {
        return showActivityGroupInProtocolFlowchart;
    }

    public void setShowActivityGroupInProtocolFlowchart(boolean showActivityGroupInProtocolFlowchart) {
        this.showActivityGroupInProtocolFlowchart = showActivityGroupInProtocolFlowchart;
    }

    public boolean isShowActivityInProtocolFlowchart() {
        return showActivityInProtocolFlowchart;
    }

    public void setShowActivityInProtocolFlowchart(boolean showActivityInProtocolFlowchart) {
        this.showActivityInProtocolFlowchart = showActivityInProtocolFlowchart;
    }

    public boolean isShowActivitySubgroupInProtocolFlowchart() {
        return showActivitySubgroupInProtocolFlowchart;
    }

    public void setShowActivitySubgroupInProtocolFlowchart(boolean showActivitySubgroupInProtocolFlowchart) {
        this.showActivitySubgroupInProtocolFlowchart = showActivitySubgroupInProtocolFlowchart;
    }

    public String getStartDate() {
        return startDate;
    }

    public void setStartDate(String startDate) {
        this.startDate = startDate;
    }

    public String getStudyActivityUid() {
        return studyActivityUid;
    }

    public void setStudyActivityUid(String studyActivityUid) {
        this.studyActivityUid = studyActivityUid;
    }

    public String getStudyUid() {
        return studyUid;
    }

    public void setStudyUid(String studyUid) {
        this.studyUid = studyUid;
    }

    public String getUserInitials() {
        return userInitials;
    }

    public void setUserInitials(String userInitials) {
        this.userInitials = userInitials;
    }

    public String getChangeType() {
        return changeType;
    }

    public void setChangeType(String changeType) {
        this.changeType = changeType;
    }
}
