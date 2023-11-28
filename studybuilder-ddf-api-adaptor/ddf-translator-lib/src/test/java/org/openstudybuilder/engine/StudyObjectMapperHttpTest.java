package org.openstudybuilder.engine;

import org.CDISC.DDF.model.Study;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.openstudybuilder.model.*;

import java.io.IOException;
import java.io.InputStream;

class StudyObjectMapperHttpTest {

    private static OpenStudyObjectFactory objectFactory;
    private final String STUDY_UID = "Study_000002";

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
    void testStudyMapping() throws Exception {
        OpenStudy openStudy = objectFactory.getStudy(STUDY_UID);
        StudyObjectMapper studyObjectMapper = new StudyObjectMapper();
        Study study = studyObjectMapper.map(openStudy, objectFactory);
        Assertions.assertNotNull(openStudy);
        Assertions.assertNotNull(study);
    }
}