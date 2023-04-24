package org.openstudybuilder.engine;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.openstudybuilder.model.*;

import java.util.List;
import java.util.Map;

public class OpenStudyObjectFactory {

    private final StudyBuilderAdaptor studyBuilderAdaptor;

    OpenStudyObjectFactory(StudyBuilderAdaptor studyBuilderAdaptor) {
        this.studyBuilderAdaptor = studyBuilderAdaptor;
    }

    public static OpenStudyObjectFactory withStaticBuilderAdaptor() {
        return new OpenStudyObjectFactory(new OpenStudyBuilderFileAdaptor());
    }

    public static OpenStudyObjectFactory withRestApiClient() {
        return new OpenStudyObjectFactory(new OpenStudyBuilderSwaggerAdaptor());
    }
    public static OpenStudyObjectFactory withRestApiClient(String bearerToken) {
        return new OpenStudyObjectFactory(new OpenStudyBuilderSwaggerAdaptor(bearerToken));
    }

    public List<Visit> getVisits(String studyId) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();
        String visitJSON = studyBuilderAdaptor.getVisits(studyId);
        // the visits json file is not an array at the root, instead
        // the visits array is referenced by 'items' at the root.
        // So, let's grab the array node under 'items'.
        JsonNode jsonNode = objectMapper.readTree(visitJSON);
        JsonNode visitsNode = jsonNode.get("items");
        // visitsNode is an array that contains visit objects



        return objectMapper.readValue(
                visitsNode.toString(),
                new TypeReference<List<Visit>>(){});
    }

    public Population getPopulation(String studyId) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();

        return objectMapper.readValue(
                studyBuilderAdaptor.getPopulation(studyId),
                new TypeReference<Population>(){});
    }

    public Objective getObjective(String studyObjectiveUid) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();

        return objectMapper.readValue(
                studyBuilderAdaptor.getObjective(studyObjectiveUid),
                new TypeReference<Objective>(){});
    }

    public List<StudySelectionObjective> getStudyObjectiveSections(String studyId) throws Exception {
        ObjectMapper objectMapper = new ObjectMapper();
        String objectivesJson = studyBuilderAdaptor.getStudyObjectiveSections(studyId);

        JsonNode jsonNode = objectMapper.readTree(objectivesJson);
        JsonNode objectivesNode = jsonNode.get("items");

        return objectMapper.readValue(
                objectivesNode.toString(),
                new TypeReference<List<StudySelectionObjective>>(){});
    }


    public Intervention getIntervention(String studyId) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();

        return objectMapper.readValue(
                studyBuilderAdaptor.getIntervention(studyId),
                new TypeReference<Intervention>(){});
    }


    public StudyDesign getHLDesign(String studyId) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();

        return objectMapper.readValue(
                studyBuilderAdaptor.getHlDesign(studyId),
                new TypeReference<StudyDesign>(){});
    }

    public List<Epoch> getEpochs(String studyId) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();
        String epochJson = studyBuilderAdaptor.getEpochs(studyId);

        JsonNode jsonNode = objectMapper.readTree(epochJson);
        JsonNode epochsNode = jsonNode.get("items");

        return objectMapper.readValue(
                epochsNode.toString(),
                new TypeReference<List<Epoch>>(){});
    }

    public List<Epoch> getEpochs(String studyId, Map<String, Boolean> sortingOptions, int pageNumber) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();
        // TODO - Using a static method here doesn't seem right. But what other option to overload this method?
        String epochJson = OpenStudyBuilderSwaggerAdaptor.getEpochsWithPageAndSorting(studyId, sortingOptions, pageNumber);

        JsonNode jsonNode = objectMapper.readTree(epochJson);
        JsonNode epochsNode = jsonNode.get("items");

        return objectMapper.readValue(
                epochsNode.toString(),
                new TypeReference<List<Epoch>>(){});
    }

    public Endpoint getEndpoint(String studyId) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();

        return objectMapper.readValue(
                studyBuilderAdaptor.getEndpoint(studyId),
                new TypeReference<Endpoint>(){});
    }

    public List<StudySelectionEndpoint> getStudyEndpointSections(String studyId) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();

        String endpointsJson = studyBuilderAdaptor.getStudyEndpointSections(studyId);
        JsonNode jsonNode = objectMapper.readTree(endpointsJson);
        JsonNode endpointsNode = jsonNode.get("items");

        return objectMapper.readValue(
                endpointsNode.toString(),
                new TypeReference<List<StudySelectionEndpoint>>(){});
    }

    public List<Element> getElements(String studyId) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();
        String elementJSon = studyBuilderAdaptor.getElements(studyId);

        JsonNode jsonNode = objectMapper.readTree(elementJSon);
        JsonNode elementsNode = jsonNode.get("items");

        return objectMapper.readValue(
                elementsNode.toString(),
                new TypeReference<List<Element>>(){});
    }

    public List<StudyDesignCell> getDesignMatrix(String studyId) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();

        return objectMapper.readValue(
                studyBuilderAdaptor.getDesignMatrix(studyId),
                new TypeReference<List<StudyDesignCell>>(){});
    }

    public List<Arm> getArms(String studyId) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();
        String armJson = studyBuilderAdaptor.getArms(studyId);

        JsonNode jsonNode = objectMapper.readTree(armJson);
        JsonNode armsNode = jsonNode.get("items");

        return objectMapper.readValue(
                armsNode.toString(),
                new TypeReference<List<Arm>>(){});
    }

    public Arm getSingleArm(String studyId, String armId) throws Exception {
        ObjectMapper objectMapper = new ObjectMapper();
        String armJson = studyBuilderAdaptor.getSingleArm(studyId, armId);
        return objectMapper.readValue(armJson, new TypeReference<Arm>() {});
    }

    public Epoch getSingleEpoch(String studyId, String epochId) throws Exception {
        ObjectMapper objectMapper = new ObjectMapper();
        String epochJson = studyBuilderAdaptor.getSingleEpoch(studyId, epochId);
        return objectMapper.readValue(epochJson, new TypeReference<Epoch>() {});
    }

    public Element getSingleElement(String studyId, String elementId) throws Exception {
        ObjectMapper objectMapper = new ObjectMapper();
        String elementJson = studyBuilderAdaptor.getSingleElement(studyId, elementId);
        return objectMapper.readValue(elementJson, new TypeReference<Element>() {});
    }

    public List<OpenStudy> getStudies() throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();
        String allStudiesJson = studyBuilderAdaptor.getAllStudies();

        JsonNode jsonNode = objectMapper.readTree(allStudiesJson);
        JsonNode studiesNode = jsonNode.get("items");

        return objectMapper.readValue(
                studiesNode.toString(),
                new TypeReference<List<OpenStudy>>(){});
    }

    public List<StudySelectionCriteria> getCriterias(String studyId) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();
        String criteriaJson = studyBuilderAdaptor.getCriterias(studyId);

        JsonNode jsonNode = objectMapper.readTree(criteriaJson);
        JsonNode criteriasNode = jsonNode.get("items");

        return objectMapper.readValue(
                criteriasNode.toString(),
                new TypeReference<List<StudySelectionCriteria>>(){});
    }

    public List<StudyDesignCell> getDesignMatrixCells(String studyId) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();

        return objectMapper.readValue(
                studyBuilderAdaptor.getDesignMatrixCells(studyId),
                new TypeReference<List<StudyDesignCell>>(){});
    }

    public CriteriaType getCriteriaType(String studyId) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();

        return objectMapper.readValue(
                studyBuilderAdaptor.getCriteriaType(studyId),
                new TypeReference<CriteriaType>(){});
    }

    public OpenStudy getStudy(String studyId) throws Exception {
        ObjectMapper objectMapper = new ObjectMapper();
        return objectMapper.readValue(studyBuilderAdaptor.getSingleStudy(studyId),
                new TypeReference<OpenStudy>(){});
    }

    public List<StudyActivitySection> getActivitySections(String studyId) throws Exception {
        ObjectMapper objectMapper = new ObjectMapper();
        String activityJson = studyBuilderAdaptor.getStudyActivitySections(studyId);

        JsonNode jsonNode = objectMapper.readTree(activityJson);
        JsonNode activitiesNode = jsonNode.get("items");
        if (activitiesNode == null) {
            activitiesNode = jsonNode;
        }

        return objectMapper.readValue(
                activitiesNode.toString(),
                new TypeReference<List<StudyActivitySection>>(){});
    }

    public List<StudyActivitySchedule> getActivitySchedules(String studyId) throws Exception {
        ObjectMapper objectMapper = new ObjectMapper();
        String activityJson = studyBuilderAdaptor.getStudyActivitySchedules(studyId);

        JsonNode jsonNode = objectMapper.readTree(activityJson);
        JsonNode activitiesNode = jsonNode.get("items");
        if (activitiesNode == null) {
            activitiesNode = jsonNode;
        }

        return objectMapper.readValue(
                activitiesNode.toString(),
                new TypeReference<List<StudyActivitySchedule>>(){});
    }


}
