package org.openstudybuilder.engine;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.openstudybuilder.utils.HttpRestClient;
import org.openstudybuilder.utils.TranslatorUtils;

import java.util.Map;
import java.util.logging.Logger;

public class OpenStudyBuilderSwaggerAdaptor implements StudyBuilderAdaptor {

    private static final Logger logger = Logger.getLogger(OpenStudyBuilderSwaggerAdaptor.class.getName());
    private static HttpRestClient httpRestClient;

    // Parameter names that we attach to query string whenever we paginate results
    private static final String TOTAL_COUNT_PARAM_NAME = TranslatorUtils.getTotCountParamName();
    private static final String PAGE_SIZE_PARAM_NAME = TranslatorUtils.getPageSizeParamName();
    private static final String PAGE_NUMBER_PARAM_NAME = TranslatorUtils.getPageNumberParamName();
    private static final String SORTING_OPTIONS_PARAM_NAME = TranslatorUtils.getSortingOptionParamName();
    // Default parameter values for pagination
    private static final String USE_TOTAL_COUNT = TranslatorUtils.getUseTotCountParam();
    private static final String DEFAULT_PAGE_SIZE = TranslatorUtils.getDefaultPageSize();

    public OpenStudyBuilderSwaggerAdaptor(String bearerToken) {
        httpRestClient = new HttpRestClient(bearerToken);
    }

    /**
     * No args constructor is for api environments with no authentication enabled
     * This is marked as deprecated as it was for testing purposes only
     */
    @Deprecated
    public OpenStudyBuilderSwaggerAdaptor() {
        httpRestClient = new HttpRestClient(null);
    }

    @Override
    public String getEpochs(String studyUid) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-epochs", studyUid);
        logger.info(String.format("GET Epochs: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    public static String getEpochsWithPageAndSorting(String studyUid, Map<String, Boolean> sortingOptions,
                                              int pageNumber) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-epochs", studyUid);
        requestUrl = TranslatorUtils.attachDefaultSortingParams(requestUrl);
        requestUrl = TranslatorUtils.attachQueryStringParam(requestUrl, PAGE_NUMBER_PARAM_NAME, String.valueOf(pageNumber));
        if (sortingOptions != null) {
            requestUrl = TranslatorUtils.attachQueryStringParam(requestUrl, SORTING_OPTIONS_PARAM_NAME, sortingOptions);
        }
        logger.info(String.format("GET Epochs with Sorting Options: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getVisits(String studyUid) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-visits", studyUid);
        logger.info(String.format("GET Visits: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    public String getVisitsWithPageAndSorting(String studyUid, Map<String, Boolean> sortingOptions,
                                              int pageNumber) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-visits?", studyUid);
        requestUrl = requestUrl.concat(TOTAL_COUNT_PARAM_NAME + '=').concat(USE_TOTAL_COUNT);
        requestUrl = requestUrl.concat(PAGE_SIZE_PARAM_NAME + '=').concat(DEFAULT_PAGE_SIZE);
        requestUrl = requestUrl.concat(PAGE_NUMBER_PARAM_NAME + '=').concat(String.valueOf(pageNumber));
        if (sortingOptions != null) {
            String jsonSorting = new ObjectMapper().writeValueAsString(sortingOptions);
            requestUrl = requestUrl.concat(SORTING_OPTIONS_PARAM_NAME + '=').concat(jsonSorting);
        }
        logger.info(String.format("GET Visits with Sorting Options: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }


    @Override
    public String getObjective(String studyObjectiveUid) throws Exception {
        String requestUrl = String.format("/objectives/%1$s", studyObjectiveUid);
        logger.info(String.format("GET Specific Objective by UID: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getStudyObjectiveSections(String studyUid) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-objectives", studyUid);
        logger.info(String.format("GET Study Objectives: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getPopulation(String studyNumber) throws Exception {
        // TODO - Must recheck how we're going to use this endpoint in our workflows
        String requestUrl = String.format("/listings/studies/listing/%1$s/study-population", studyNumber);
        logger.info(String.format("GET Population with study NUMBER: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getIntervention(String studyUid) throws Exception {
        // TODO - Could not find any intervention endpoint
        return null;
    }

    @Override
    public String getInclusions(String studyUid) throws Exception {
        // TODO - Could not find this in swagger.json
        return null;
    }

    @Override
    public String getHlDesign(String studyUid) throws Exception {
        // TODO - Could not find this in swagger.json
        return null;
    }

    @Override
    public String getExclusions(String studyUid) throws Exception {
        // TODO - Could not find this in swagger.json
        return null;
    }

    @Override
    // TODO - Check if we really need this one
    public String getEndpoint(String endpointUid) throws Exception {
        String requestUrl = String.format("/endpoints/%1$s", endpointUid);
        logger.info(String.format("GET Single Endpoint Data: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getStudyEndpointSections(String studyUid) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-endpoints", studyUid);
        logger.info(String.format("GET Endpoints: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getElements(String studyUid) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-elements", studyUid);
        logger.info(String.format("GET Elements: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getDesignMatrix(String studyUid) throws Exception {
        // TODO - Could not find this in swagger.json Prob replaced by design cells
        return null;
    }

    @Override
    public String getArms(String studyUid) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-arms", studyUid);
        logger.info(String.format("GET Arms: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getSingleArm(String studyUid, String studyArmUid) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-arms/%2$s", studyUid, studyArmUid);
        logger.info(String.format("GET Individual Arm: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getSingleEpoch(String studyUid, String studyEpochUid) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-epochs/%2$s", studyUid, studyEpochUid);
        logger.info(String.format("GET Individual Epoch: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getSingleElement(String studyUid, String studyElementUid) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-elements/%2$s", studyUid, studyElementUid);
        logger.info(String.format("GET Individual Element: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }


    @Override
    public String getAllStudies() throws Exception {
        // TODO - What was the intended difference between getAllStudies and getStudies?
        String requestUrl = "/studies";
        logger.info(String.format("GET All Studies: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getCriterias(String studyUid) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-criteria", studyUid);
        logger.info(String.format("GET Criterias: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getDesignMatrixCells(String studyUid) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-design-cells", studyUid);
        logger.info(String.format("GET Design Cells: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getCriteriaType(String studyUid) throws Exception {
        // TODO - Could not find this in swagger.json.
        return null;
    }

    @Override
    public String getSingleStudy(String studyUid) throws Exception {
        String addtlParams = "?fields=%2Bcurrent_metadata.study_description,current_metadata.study_intervention," +
                "current_metadata.high_level_study_design,current_metadata.study_population," +
                "current_metadata.identification_metadata";
        String requestUrl = String.format("/studies/%1$s", studyUid).concat(addtlParams);
        logger.info(String.format("GET Study: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getStudyActivitySections(String studyUid) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-activities", studyUid);
        logger.info(String.format("GET Study Activities: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getStudyActivitySchedules(String studyUid) throws Exception {
        String requestUrl = String.format("/studies/%1$s/study-activity-schedules", studyUid);
        logger.info(String.format("GET Study Activity Schedules: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }

    @Override
    public String getStudies() throws Exception {
        String requestUrl = "/studies";
        logger.info(String.format("GET All Studies Again: %1$s", requestUrl));
        return httpRestClient.sendGetRequest(requestUrl).parseAsString();
    }
}
