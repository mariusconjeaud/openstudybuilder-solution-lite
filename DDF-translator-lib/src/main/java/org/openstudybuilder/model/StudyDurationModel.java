package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class StudyDurationModel {

    private int durationValue;
    private Code durationUnitCode;

    public int getDurationValue() {
        return durationValue;
    }

    public void setDurationValue(int durationValue) {
        this.durationValue = durationValue;
    }

    public Code getDurationUnitCode() {
        return durationUnitCode;
    }

    public void setDurationUnitCode(Code durationUnitCode) {
        this.durationUnitCode = durationUnitCode;
    }
}
