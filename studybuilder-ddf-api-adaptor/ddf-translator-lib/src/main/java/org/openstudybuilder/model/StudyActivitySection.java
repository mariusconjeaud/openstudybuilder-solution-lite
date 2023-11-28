package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

import java.util.Map;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class StudyActivitySection {

    private boolean isAcceptedVersion;
    private Map<String, String> studyActivityGroup;
    private Map<String, String> studyActivitySubgroup;
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
}
