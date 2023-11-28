package org.openstudybuilder.engine;

public interface StudyBuilderAdaptor {
    String getEpochs(String studyUid) throws Exception;
    String getVisits(String studyUid) throws Exception;
    String getObjective(String studyObjectiveUid) throws Exception;
    String getStudyObjectiveSections(String studyUid) throws Exception;
    String getPopulation(String studyUid) throws Exception;
    String getIntervention(String studyUid) throws Exception;
    String getInclusions(String studyUid) throws Exception;
    String getHlDesign(String studyUid) throws Exception;
    String getExclusions(String studyUid) throws Exception;
    String getEndpoint(String endpointUid) throws Exception;
    String getStudyEndpointSections(String studyUid) throws Exception;
    String getElements(String studyUid) throws Exception;
    String getDesignMatrix(String studyUid) throws Exception;
    String getArms(String studyUid) throws Exception;
    String getSingleArm(String studyUid, String studyArmUid) throws Exception;
    String getSingleEpoch(String studyUid, String studyEpochUid) throws Exception;
    String getSingleElement(String studyUid, String studyElementUid) throws Exception;
    String getAllStudies() throws Exception;
    String getCriterias(String studyUid) throws Exception;
    String getDesignMatrixCells(String studyUid) throws Exception;
    String getCriteriaType(String studyUid) throws Exception;
    String getSingleStudy(String studyUid) throws Exception;
    String getStudyActivitySections(String studyUid) throws Exception;
    String getStudyActivitySchedules(String studyUid) throws Exception;
    String getStudies() throws Exception;
}
