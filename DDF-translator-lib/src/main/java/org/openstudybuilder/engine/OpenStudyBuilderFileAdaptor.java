package org.openstudybuilder.engine;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.logging.Level;
import java.util.logging.Logger;

public class OpenStudyBuilderFileAdaptor implements StudyBuilderAdaptor {

    private static final Logger logger = Logger.getLogger(OpenStudyBuilderFileAdaptor.class.getName());

    private static final String EPOCHS_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.study-epochs.json";
    private static final String VISITS_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.study-visits.json";
    private static final String POPULATIONS_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.study-population.json";
    private static final String OBJECTIVES_FILE = "./data/study_00001/objective.json";
    // TODO - Verify. No dedicated file but we've serialized Intervention from Current Metadata
    private static final String INTERVENTIONS_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.study-intervention.json";
    // TODO - Not included in latest files - Probably replaced by Design Matrix?
    private static final String HL_DESIGN_FILE = "./data/study_00001/studydesign.json";
    // TODO - Inclusion/Exclusion have prob been replaced by single Criteria Model. To be reviewed
    private static final String EXCLUSIONS_FILE = "./data/study_00001/exclusion.json";
    private static final String INCLUSIONS_FILE = "./data/study_00001/inclusion.json";
    // TODO - Verify if we're replacing this with STUDY ENDPOINT SECTIONS
    private static final String ENDPOINTS_FILE = "./data/study_00001/endpoint.json";
    private static final String ELEMENTS_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.study-elements.json";
    private static final String DESIGN_MATRIX_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.study-design-cells.json";
    private static final String ARMS_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.study-arms.json";
    private static final String STUDIES_FILE = "./data/study_000002_SNAKE_CASE/studies.json";
    // TODO Is it really ok to model Criteria based on criteria-templates.json? Looks like a different entity altogether?
    private static final String CRITERIAS_FILE = "./data/study_000002_SNAKE_CASE/criteria-templates.json";
    // TODO - Has been replaced with DESIGN_MATRIX_FILE - Should probably remove if not in use anymore
    private static final String DMCELL_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.study-design-cells.json";
    // TODO - Verify. No dedicated file but we've serialized CriteriaType from Criteria
    private static final String CRIT_TYPE_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.study-criteria-type.json";
    private static final String STUDY_OBJ_SEC_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.study-objectives.json";
    private static final String STUDY_EP_SEC_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.study-endpoints.json";
    private static final String STUDY_SEC_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.json";
    // TODO - Adopting "Study Section" kind of model for activities. Must review
    private static final String STUDY_ACTIVITIES_SEC_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.study-activities.json";
    private static final String STUDY_ACTIVITIES_SCHEDULES_FILE = "./data/study_000002_SNAKE_CASE/studies.Study_000002.study-activity-schedules.json";
    // this is a stub class that mocks what would really come from API calls.

     /* STUDY CELL
    JSON HERE:
     */

    // My idea is to provide methods that return JSON.  I didn't know what to put into
    // an interface as I don't really understand your api.

    // so, for now, just mock your api get endpoints.

    // TODO: implement the first mock method

    /*
    example:
    public JSON getStudyCells(UUID studyID) {
        put some comments in here describing the actual endpoint and the nature of the JSON object
        it might even help to include a commented "entire study".

     return '{someJSON:here}'
     }
     */

    // YOu can take a look at my IStudyComponentBroker interface to understand what types
    // of granular calls I am using to build a Study.

    // once we've filled this out, we'll create an interface and then we'll implement
    // an adapter that actually calls the OpenStudyBuilder API.

    // If I can build a study from the OpenStudyBuilder API, then we should know how
    // OpenStudyBuilder can post a study to the SDR via adaptor logic.

    private static String readFile(String path) throws IOException {
        try {
            return new String(Files.readAllBytes((Paths.get(path))));
        }
        catch (IOException ioException) {
            logger.log(Level.SEVERE,"Could not read json stub file", ioException);
            throw ioException;
        }
    }

    public String getEpochs(String studyUid) throws Exception {
        // Fetch epochs for a study
        // GET /study/Study_000001/study-epochs
        return readFile(EPOCHS_FILE);
    }

    public String getVisits(String studyUid) throws  IOException {

        // According to the OpenStudyBuilder team, the study-visits.json file structure
        // is somewhat stable, so we now reference the 000002 study data.

        return readFile(VISITS_FILE);
    }

    public String getObjective(String studyObjectiveUid) throws  IOException {

        return readFile(OBJECTIVES_FILE);
    }

    public String getStudyObjectiveSections(String studyUid) throws IOException {

        return readFile(STUDY_OBJ_SEC_FILE);
    }

    public String getPopulation(String studyUid) throws  IOException {

        return readFile(POPULATIONS_FILE);
    }

    public String getIntervention(String studyUid) throws  IOException {

        return readFile(INTERVENTIONS_FILE);
    }

    public String getInclusions(String studyUid) throws  IOException {

        return readFile(INCLUSIONS_FILE);
    }

    public String getHlDesign(String studyUid) throws  IOException {

        return readFile(HL_DESIGN_FILE);
    }

    public String getExclusions(String studyUid) throws  IOException {

        return readFile(EXCLUSIONS_FILE);
    }

    public String getEndpoint(String studyUid) throws  IOException {

        return readFile(ENDPOINTS_FILE);
    }

    public String getStudyEndpointSections(String studyUid) throws IOException {

        return readFile(STUDY_EP_SEC_FILE);
    }

    public String getElements(String studyUid) throws  IOException {

        return readFile(ELEMENTS_FILE);
    }

    public String getDesignMatrix(String studyUid) throws  IOException {

        return readFile(DESIGN_MATRIX_FILE);
    }

    public String getArms(String studyUid) throws  IOException {

        return readFile(ARMS_FILE);
    }

    @Override
    public String getSingleArm(String studyUid, String studyArmUid) throws Exception {
        return null;
    }

    @Override
    public String getSingleEpoch(String studyUid, String studyEpochUid) throws Exception {
        return null;
    }

    @Override
    public String getSingleElement(String studyUid, String studyElementUid) throws Exception {
        return null;
    }

    public String getAllStudies() throws  IOException {

        return readFile(STUDIES_FILE);
    }

    public String getCriterias(String studyUid) throws  IOException {

        return readFile(CRITERIAS_FILE);
    }

    public String getDesignMatrixCells(String studyUid) throws  IOException {

        return readFile(DMCELL_FILE);
    }

    public String getCriteriaType(String studyUid) throws  IOException {

        return readFile(CRIT_TYPE_FILE);
    }

    public String getSingleStudy(String studyUid) throws IOException {
        return readFile(STUDY_SEC_FILE);
    }

    public String getStudyActivitySections(String studyUid) throws IOException {
        return readFile(STUDY_ACTIVITIES_SEC_FILE);
    }

    @Override
    public String getStudyActivitySchedules(String studyUid) throws Exception {
        return readFile(STUDY_ACTIVITIES_SCHEDULES_FILE);
    }


    public String getStudies() {
        // This fetches all studies, our test DB has only one study "Study_000001".
        // GET http://localhost:8000/studies/?sortBy=%7B%7D&pageNumber=1&pageSize=0&operator=and&totalCount=false

        // We are unsure of how to enter multiline strings full off "difficult"
        // symbols, so this may not be valid.
        return "{\"items\":[{\"uid\":\"Study_000001\",\"studyNumber\":\"0\",\"studyId\":\"CDISC DEV-0\",\"studyAcronym\":null,\"projectNumber\":\"CDISC DEV\",\"studyStatus\":\"DRAFT\",\"currentMetadata\":{\"identificationMetadata\":{\"studyNumber\":\"0\",\"studyAcronym\":null,\"projectNumber\":\"CDISC DEV\",\"projectName\":\"CDISC Dev\",\"brandName\":null,\"clinicalProgrammeName\":\"CDISC Development programme\",\"studyId\":\"CDISC DEV-0\",\"registryIdentifiers\":{\"ctGovId\":null,\"ctGovIdNullValueCode\":null,\"eudractId\":null,\"eudractIdNullValueCode\":null,\"universalTrialNumberUTN\":null,\"universalTrialNumberUTNNullValueCode\":null,\"japaneseTrialRegistryIdJAPIC\":null,\"japaneseTrialRegistryIdJAPICNullValueCode\":null,\"investigationalNewDrugApplicationNumberIND\":null,\"investigationalNewDrugApplicationNumberINDNullValueCode\":null}},\"versionMetadata\":{\"studyStatus\":\"DRAFT\",\"lockedVersionNumber\":null,\"versionTimestamp\":\"2022-03-15T07:33:49.011304\",\"lockedVersionAuthor\":null,\"lockedVersionInfo\":null}}}],\"total\":0,\"page\":1,\"size\":0}";
     }

    public JsonNode getStudiesJSON() throws IOException {
        // This fetches all studies, our test DB has only one study "Study_000001".
        // GET http://localhost:8000/studies/?sortBy=%7B%7D&pageNumber=1&pageSize=0&operator=and&totalCount=false

        // We are unsure of how to enter multiline strings full off "difficult"
        // symbols, so this may not be valid.
        String study =  "{\"items\":[{\"uid\":\"Study_000001\",\"studyNumber\":\"0\",\"studyId\":\"CDISC DEV-0\",\"studyAcronym\":null,\"projectNumber\":\"CDISC DEV\",\"studyStatus\":\"DRAFT\",\"currentMetadata\":{\"identificationMetadata\":{\"studyNumber\":\"0\",\"studyAcronym\":null,\"projectNumber\":\"CDISC DEV\",\"projectName\":\"CDISC Dev\",\"brandName\":null,\"clinicalProgrammeName\":\"CDISC Development programme\",\"studyId\":\"CDISC DEV-0\",\"registryIdentifiers\":{\"ctGovId\":null,\"ctGovIdNullValueCode\":null,\"eudractId\":null,\"eudractIdNullValueCode\":null,\"universalTrialNumberUTN\":null,\"universalTrialNumberUTNNullValueCode\":null,\"japaneseTrialRegistryIdJAPIC\":null,\"japaneseTrialRegistryIdJAPICNullValueCode\":null,\"investigationalNewDrugApplicationNumberIND\":null,\"investigationalNewDrugApplicationNumberINDNullValueCode\":null}},\"versionMetadata\":{\"studyStatus\":\"DRAFT\",\"lockedVersionNumber\":null,\"versionTimestamp\":\"2022-03-15T07:33:49.011304\",\"lockedVersionAuthor\":null,\"lockedVersionInfo\":null}}}],\"total\":0,\"page\":1,\"size\":0}";
         ObjectMapper objectMapper = new ObjectMapper();
         return objectMapper.readTree(study);

    }

    public String getStudyArray() {
        // This fetches all studies, our test DB has only one study "Study_000001".
        // GET http://localhost:8000/studies/?sortBy=%7B%7D&pageNumber=1&pageSize=0&operator=and&totalCount=false

        // We are unsure of how to enter multiline strings full off "difficult"
        // symbols, so this may not be valid.

        return "[{\"uid\":\"Study_000001\",\"studyNumber\":\"0\",\"studyId\":\"CDISC DEV-0\",\"studyAcronym\":null,\"projectNumber\":\"CDISC DEV\",\"studyStatus\":\"DRAFT\",\"currentMetadata\":{\"identificationMetadata\":{\"studyNumber\":\"0\",\"studyAcronym\":null,\"projectNumber\":\"CDISC DEV\",\"projectName\":\"CDISC Dev\",\"brandName\":null,\"clinicalProgrammeName\":\"CDISC Development programme\",\"studyId\":\"CDISC DEV-0\",\"registryIdentifiers\":{\"ctGovId\":null,\"ctGovIdNullValueCode\":null,\"eudractId\":null,\"eudractIdNullValueCode\":null,\"universalTrialNumberUTN\":null,\"universalTrialNumberUTNNullValueCode\":null,\"japaneseTrialRegistryIdJAPIC\":null,\"japaneseTrialRegistryIdJAPICNullValueCode\":null,\"investigationalNewDrugApplicationNumberIND\":null,\"investigationalNewDrugApplicationNumberINDNullValueCode\":null}},\"versionMetadata\":{\"studyStatus\":\"DRAFT\",\"lockedVersionNumber\":null,\"versionTimestamp\":\"2022-03-15T07:33:49.011304\",\"lockedVersionAuthor\":null,\"lockedVersionInfo\":null}}}]";

    }


}
