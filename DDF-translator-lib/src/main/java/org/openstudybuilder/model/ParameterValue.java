package org.openstudybuilder.model;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.HashMap;
import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class ParameterValue {

    private int position;
    private String conjunction;
    private List<HashMap<String, String>> values;

    public ParameterValue() {

    }


    public ParameterValue(int position, String conjunction, List<HashMap<String, String>> values) {
        this.position = position;
        this.conjunction = conjunction;
        this.values = values;
    }

    public int getPosition() {
        return position;
    }

    public String getConjunction() {
        return conjunction;
    }

    public List<HashMap<String, String>> getValues() {
        return values;
    }

    public void setPosition(int position) {
        this.position = position;
    }

    public void setConjunction(String conjunction) {
        this.conjunction = conjunction;
    }

    public void setValues(List<HashMap<String, String>> values) {
        this.values = values;
    }
}
