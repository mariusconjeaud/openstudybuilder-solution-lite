package org.openstudybuilder.engine;

import org.junit.jupiter.api.*;
import org.openstudybuilder.model.*;

import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class OpenStudyHttpObjectFactoryTest {

    private static OpenStudyObjectFactory objectFactory;
    // Notice the STUDY_UID used by the Rest Apis is different from the "studyId" displayed by the Open Study Builder UI
    private final String STUDY_UID = "Study_000001";
    private final String STUDY_NUMBER = "0";
    private final String ENDPOINT_UID = "Endpoint_000004";
    private final String STUDY_OBJECTIVE_UID = "Objective_000001";

    @BeforeAll
    public static void init() {
        try {
            InputStream file = OpenStudyHttpObjectFactoryTest.class
                    .getClassLoader().getResourceAsStream("application.properties");
            if (file != null) System.getProperties().load(file);
        } catch (IOException e) {
            throw new RuntimeException("Error loading application.properties", e);
        }
        objectFactory = OpenStudyObjectFactory.withRestApiClient(System.getProperty("builder_api_tmp_auth_token"));
    }

    @Test
    void getStudies() throws Exception {
        // Leaving First Study in the list checking against CDISC DEV-0
        List<OpenStudy> openStudies = objectFactory.getStudies();
        Assertions.assertNotEquals(0, openStudies.size());
        CurrentMetadata currentMetadata = openStudies.get(0).getCurrentMetadata();
        IdentificationMetadata identificationMetadata = currentMetadata.getIdentificationMetadata();
        VersionMetadata versionMetadata = currentMetadata.getVersionMetadata();
        Assertions.assertEquals("CDISC DEV-0", identificationMetadata.getStudyId());
        Assertions.assertEquals("CDISC DEV", identificationMetadata.getProjectNumber());
        Assertions.assertEquals("DRAFT", currentMetadata.getVersionMetadata().getStudyStatus());
    }

    @Test
    void getSingleStudy() throws Exception {
        // Leaving First Study in the list checking against CDISC DEV-0
        OpenStudy openStudy = objectFactory.getStudy(STUDY_UID);
        Assertions.assertNotNull(openStudy);
    }

    @Test
    void getEpochsForStudy() throws Exception {
        List<Epoch> epochs = objectFactory.getEpochs(STUDY_UID);
        Assertions.assertNotEquals(0, epochs.size());
        Assertions.assertEquals("C48262_SCREENING",epochs.get(0).getEpoch());
        Assertions.assertEquals("Initial Version", epochs.get(0).getChangeDescription());
        Assertions.assertEquals("C48262_SCREENING", epochs.get(0).getEpochSubtype());
        Assertions.assertEquals("CTTerm_000003", epochs.get(0).getEpochType());
        Assertions.assertEquals(1, epochs.get(0).getOrder());
        Assertions.assertEquals("edit", epochs.get(0).getPossibleActions().get(0));
        Assertions.assertEquals(-14, epochs.get(0).getStartDay());
        Assertions.assertEquals(1, epochs.get(0).getStudyVisitCount());
    }

    @Test
    void getEpochsSortedWithPage() throws Exception {
        Map<String, Boolean> sortingOptions = new HashMap<>();
        sortingOptions.put("uid", false);
        // Retrieve only one page of results sorted by epoch uid descending
        List<Epoch> epochs = objectFactory.getEpochs(STUDY_UID, sortingOptions, 1 );
        Assertions.assertNotEquals(0, epochs.size());
        Assertions.assertEquals("StudyEpoch_000001", epochs.get(0).getUid());
        Assertions.assertEquals("StudyEpoch_000002", epochs.get(1).getUid());
        Assertions.assertEquals("StudyEpoch_000003", epochs.get(2).getUid());
    }

    @Test
    void getStudyEndpointSections() throws Exception {
        List<StudySelectionEndpoint> studySelectionEndpoints =
                objectFactory.getStudyEndpointSections(STUDY_UID);
        Assertions.assertNotEquals(0, studySelectionEndpoints.size());
        StudySelectionEndpoint firstEndpointItem = studySelectionEndpoints.get(0);
        Assertions.assertEquals("StudyEndpoint_000001", firstEndpointItem.getStudyEndpointUid());
        // Sample study no longer has an endpoint level
        //Assertions.assertEquals("C98772_OUTMSPRI", firstEndpointItem.getEndpointLevel().getTermUid());
    }

    @Test
    void getObjectiveByUid() throws Exception {
        Objective studyObjective = objectFactory.getObjective(STUDY_OBJECTIVE_UID);
        Assertions.assertNotNull(studyObjective);
        Assertions.assertEquals("Final", studyObjective.getStatus());
    }

    @Test
    void getStudyObjectiveSections() throws Exception {
        List<StudySelectionObjective> studySelectionObjectives =
                objectFactory.getStudyObjectiveSections(STUDY_UID);
        Assertions.assertNotEquals(0, studySelectionObjectives.size());
        StudySelectionObjective firstObjectiveItem = studySelectionObjectives.get(0);
        Assertions.assertEquals("StudyObjective_000001", firstObjectiveItem.getStudyObjectiveUid());
        Assertions.assertEquals("SDTM CT", firstObjectiveItem.getObjectiveLevel().getCatalogueName());
        Assertions.assertEquals("Objective_000006", firstObjectiveItem.getObjective().getUid());
    }

    @Test
    @Disabled("Missing data") // TODO
    void getStudyCriterias() throws Exception {
        List<StudySelectionCriteria> studyCriteria =
                objectFactory.getCriterias(STUDY_UID);
        Assertions.assertNotEquals(0, studyCriteria.size());
        StudySelectionCriteria firstCriteriaItem = studyCriteria.get(0);
        Assertions.assertEquals("StudyCriteria_000001", firstCriteriaItem.getStudyCriteriaUid());
        Assertions.assertEquals("Exclusion Criteria", firstCriteriaItem.getCriteriaType()
                .getSponsorPreferredName());
        Assertions.assertEquals("Criteria_000001", firstCriteriaItem.getCriteria().getUid());
    }

    @Test
    void getStudyActivitySections() throws Exception {
        List<StudyActivitySection> studyActivitySections = objectFactory.getActivitySections(STUDY_UID);
        Assertions.assertNotEquals(0, studyActivitySections.size());
        StudyActivitySection firstActivityItem = studyActivitySections.get(0);
        Assertions.assertEquals("StudyActivity_000001", firstActivityItem.getStudyActivityUid());
        Assertions.assertEquals("Randomized", firstActivityItem.getActivity().getName());
    }

    @Test
    @Disabled
    void getStudyPopulationListing() throws Exception {
        // TODO: get population api is based on study number not uid
        Population studyPopulationListing = objectFactory.getPopulation("0");
        Assertions.assertNotNull(studyPopulationListing);
    }

    @Test
    void getDesignMatrixCells() throws Exception {
        List<StudyDesignCell> studyDesignCells = objectFactory.getDesignMatrixCells(STUDY_UID);
        Assertions.assertNotEquals(0, studyDesignCells.size());
        Assertions.assertEquals("StudyDesignCell_000001", studyDesignCells.get(0).getDesignCellUid());
    }

    @Test
    void getSingleEndpoint() throws Exception {
        Endpoint endpoint = objectFactory.getEndpoint(ENDPOINT_UID);
        Assertions.assertNotNull(endpoint);
        Assertions.assertEquals("<p>Disease control rate of [azd6738] + [durvalumab] cohort</p>",
                endpoint.getName());
        Assertions.assertEquals("EndpointTemplate_000006", endpoint.getEndpointTemplate().getUid());
    }

    @Test
    void getStudyArms() throws Exception {
        List<Arm> arms = objectFactory.getArms(STUDY_UID);
        Assertions.assertNotEquals(0, arms.size());
    }

    @Test
    void getStudyVisits() throws Exception {
        List<Visit> visits = objectFactory.getVisits(STUDY_UID);
        Assertions.assertNotEquals(0, visits.size());
    }

}
