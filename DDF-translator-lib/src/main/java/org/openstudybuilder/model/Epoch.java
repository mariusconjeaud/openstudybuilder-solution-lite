package org.openstudybuilder.model;


import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class Epoch {

    private String uid;
    private String studyUid;
    private String startRule;
    private String endRule;
    private String epoch;
    private String epochSubtype;
    private String durationUnit;
    private int order;
    private String description;
    private int duration;
    private String colorHash;
    private String epochName;
    private String epochSubtypeName;
    private String epochType;
    private int startDay;
    private int endDay;
    private int startWeek;
    private int endWeek;
    private String startDate;
    private String status;
    private String userInitials;
    private List<String> possibleActions;
    private String changeDescription;
    private int studyVisitCount;

    public Epoch(){

    }


    public Epoch(String uid) {
        this.uid = uid;
    }

    public String getUid() {
        return uid;
    }

    public void setUid(String uid){
        this.uid = uid;
    }

    public String getStudyUid() {
        return studyUid;
    }

    public void setStudyUid(String studyUid) {
        this.studyUid = studyUid;
    }

    public String getStartRule() {
        return startRule;
    }

    public void setStartRule(String startRule) {
        this.startRule = startRule;
    }

    public String getEndRule() {
        return endRule;
    }

    public void setEndRule(String endRule) {
        this.endRule = endRule;
    }

    public String getEpoch() {
        return epoch;
    }

    public void setEpoch(String epoch) {
        this.epoch = epoch;
    }

    public String getEpochSubtype() {
        return epochSubtype;
    }

    public void setEpochSubtype(String epochSubtype) {
        this.epochSubtype = epochSubtype;
    }

    public String getDurationUnit() {
        return durationUnit;
    }

    public void setDurationUnit(String durationUnit) {
        this.durationUnit = durationUnit;
    }

    public int getDuration() {
        return duration;
    }

    public void setDuration(int duration) {
        this.duration = duration;
    }

    public String getColorHash() {
        return colorHash;
    }

    public void setColorHash(String colorHash) {
        this.colorHash = colorHash;
    }

    public String getEpochName() {
        return epochName;
    }

    public void setEpochName(String epochName) {
        this.epochName = epochName;
    }

    public String getEpochSubtypeName() {
        return epochSubtypeName;
    }

    public void setEpochSubtypeName(String epochSubTyeName) {
        this.epochSubtypeName = epochSubTyeName;
    }

    public String getEpochType() {
        return epochType;
    }

    public void setEpochType(String epochType) {
        this.epochType = epochType;
    }

    public int getStartDay() {
        return startDay;
    }

    public void setStartDay(int startDay) {
        this.startDay = startDay;
    }

    public int getStartWeek() {
        return startWeek;
    }

    public void setStartWeek(int startWeek) {
        this.startWeek = startWeek;
    }

    public int getEndWeek() {
        return endWeek;
    }

    public void setEndWeek(int endWeek) {
        this.endWeek = endWeek;
    }

    public int getEndDay() {
        return endDay;
    }

    public void setEndDay(int endDay) {
        this.endDay = endDay;
    }

    public String getStartDate() {
        return startDate;
    }

    public void setStartDate(String startDate) {
        this.startDate = startDate;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getUserInitials() {
        return userInitials;
    }

    public void setUserInitials(String userInitials) {
        this.userInitials = userInitials;
    }

    public List<String> getPossibleActions() {
        return possibleActions;
    }

    public void setPossibleActions(List<String> possibleActions) {
        this.possibleActions = possibleActions;
    }

    public String getChangeDescription() {
        return changeDescription;
    }

    public void setChangeDescription(String changeDescription) {
        this.changeDescription = changeDescription;
    }

    public int getStudyVisitCount() {
        return studyVisitCount;
    }

    public void setStudyVisitCount(int studyVisitCount) {
        this.studyVisitCount = studyVisitCount;
    }

    public int getOrder() {
        return order;
    }

    public void setOrder(int order) {
        this.order = order;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
}
