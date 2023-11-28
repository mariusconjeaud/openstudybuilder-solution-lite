package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.Setter;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@Getter @Setter
public class StudySelectionCriteria {

    private String studyCriteriaUid;
    private String studyUid;
    private int order;
    private Criteria criteria;
    private CriteriaTemplate criteriaTemplate;
    private Criteria latestCriteria;
    private CriteriaTemplate latestCriteriaTemplate;
    private boolean keyCriteria;
    private String startDate;
    private String endDate;
    private String status;
    private String changeType;
    private String userInitials;
    private String projectNumber;
    private String projectName;
    // At this level this fields corresponds to CTTermName
    private CriteriaType criteriaType;
    private boolean acceptedVersion;
}
