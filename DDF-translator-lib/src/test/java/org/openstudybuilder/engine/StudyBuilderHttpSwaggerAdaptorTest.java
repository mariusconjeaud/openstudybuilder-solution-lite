package org.openstudybuilder.engine;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

import java.io.IOException;

public class StudyBuilderHttpSwaggerAdaptorTest {

    private final String STUDY_ID = "Study_000001";
    private final String STUDY_OBJECTIVE_UID = "StudyObjective_000001";
    private static StudyBuilderAdaptor studyBuilderAdaptor;

    /**
     * Load application.properties so the test knows where to pull auth token from and
     * which Study Builder api url to send requests to.
     * @throws IOException
     */
    @BeforeAll
    public static void init() throws IOException {
        try {
            var file = StudyBuilderHttpSwaggerAdaptorTest.class
                    .getClassLoader().getResourceAsStream("application.properties");
            if (file != null) System.getProperties().load(file);
        } catch (IOException e) {
            throw new RuntimeException("Error loading application.properties", e);
        }
        studyBuilderAdaptor = new OpenStudyBuilderSwaggerAdaptor(System.getProperty("builder_api_tmp_auth_token"));
    }

    @Test
    void getEpochs() throws Exception {
        Assertions.assertNotNull(studyBuilderAdaptor.getEpochs(STUDY_ID));
    }

    @Test
    void getVisits() throws Exception {
        Assertions.assertNotNull(studyBuilderAdaptor.getVisits(STUDY_ID));
    }

    @Test
    @Disabled
    void getObjective() throws Exception {
        Assertions.assertNotNull(studyBuilderAdaptor.getObjective(STUDY_OBJECTIVE_UID));
    }

    @Test
    @Disabled
    // TODO - This is disabled until we can define how we get to single endpoint
    void getEndpoint() throws Exception {
        Assertions.assertNotNull(studyBuilderAdaptor.getEndpoint(STUDY_ID));
    }

    @Test
    void getElements() throws Exception {
        Assertions.assertNotNull(studyBuilderAdaptor.getElements(STUDY_ID));
    }

    @Test
    void getArms() throws Exception {
        Assertions.assertNotNull(studyBuilderAdaptor.getArms(STUDY_ID));
    }

    @Test
    void getStudies() throws Exception {
        Assertions.assertNotNull(studyBuilderAdaptor.getStudies());
    }

    @Test
    void getStudyCriterias() throws Exception {
        Assertions.assertNotNull(studyBuilderAdaptor.getCriterias(STUDY_ID));
    }

    @Test
    void getSingleStudy() throws Exception {
        Assertions.assertNotNull(studyBuilderAdaptor.getSingleStudy(STUDY_ID));
    }
}
