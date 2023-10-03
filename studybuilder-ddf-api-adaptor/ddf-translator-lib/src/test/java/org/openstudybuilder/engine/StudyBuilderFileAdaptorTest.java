package org.openstudybuilder.engine;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class StudyBuilderFileAdaptorTest {

    private final String STUDY_ID = "001";
    private final String STUDY_OBJECTIVE_UID = "StudyObjective_000001";
    private final StudyBuilderAdaptor studyBuilderAdaptor = new OpenStudyBuilderFileAdaptor();

    @Test
    void getEpochs() throws Exception {

        String epochs = studyBuilderAdaptor.getEpochs(STUDY_ID);
        Assertions.assertNotNull(epochs);

    }

    @Test
    void getVisits() throws Exception {

        String visits = studyBuilderAdaptor.getVisits(STUDY_ID);
        Assertions.assertNotNull(visits);
    }

    @Test
    void getObjective() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getObjective(STUDY_OBJECTIVE_UID));

    }

    @Test
    void getStudyObjectiveSections() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getStudyObjectiveSections(STUDY_ID));

    }

    @Test
    void getPopulations() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getPopulation(STUDY_ID));
    }

    @Test
    void getIntervention() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getIntervention(STUDY_ID));
    }

    @Test
    void getInclusions() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getInclusions(STUDY_ID));

    }

    @Test
    void getHlDesign() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getHlDesign(STUDY_ID));
    }

    @Test
    void getExclusions() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getExclusions(STUDY_ID));
    }

    @Test
    void getEndpoints() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getEndpoint(STUDY_ID));
    }

    @Test
    void getStudyEndpointSections() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getStudyEndpointSections(STUDY_ID));
    }


    @Test
    void getElements() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getElements(STUDY_ID));
    }

    @Test
    void getDesignMatrix() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getDesignMatrix(STUDY_ID));
    }

    @Test
    void getArms() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getArms(STUDY_ID));
    }

    @Test
    void getAllStudies() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getAllStudies());
    }

    @Test
    void getCriterias() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getCriterias(STUDY_ID));
    }

    @Test
    void getDesignMatrixCells() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getDesignMatrixCells(STUDY_ID));
    }

    @Test
    void getCriteriaType() throws Exception {

        Assertions.assertNotNull(studyBuilderAdaptor.getCriteriaType(STUDY_ID));
    }

    @Test
    void getStudy() throws Exception {
        Assertions.assertNotNull(studyBuilderAdaptor.getSingleStudy(STUDY_ID));
    }

    @Test
    void getActivitySections() throws Exception {
        Assertions.assertNotNull(studyBuilderAdaptor.getStudyActivitySections(STUDY_ID));
    }
}