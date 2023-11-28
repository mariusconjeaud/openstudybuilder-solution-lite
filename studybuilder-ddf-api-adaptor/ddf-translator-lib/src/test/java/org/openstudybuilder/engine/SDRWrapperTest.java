//package org.openstudybuilder.engine;
//
//import org.junit.jupiter.api.Assertions;
//import org.junit.jupiter.api.BeforeAll;
//import org.junit.jupiter.api.Disabled;
//import org.junit.jupiter.api.Test;
//
//import java.io.IOException;
//
//public class SDRWrapperTest {
//
//    private final String STUDY_UID = "Study_000001";
//
//    @BeforeAll
//    public static void init() {
//        try {
//            InputStream file = SDRWrapperTest.class
//                    .getClassLoader().getResourceAsStream("application.properties");
//            if (file != null) System.getProperties().load(file);
//        } catch (IOException e) {
//            throw new RuntimeException("Error loading application.properties", e);
//        }
//    }
//
//    @Test
//    @Disabled
//    public void shouldGenerateSdrStudy() throws Exception {
//        String token = System.getProperty("builder_api_tmp_auth_token");
//        if (!token.equals("")) {
//            AcctSDRWrapper wrapper = new AcctSDRWrapper(token);
//            String studyResult = wrapper.composeStudy(STUDY_UID);
//            System.out.println(studyResult);
//            Assertions.assertNotNull(studyResult);
//        }
//        else
//            throw new RuntimeException("Auth Token Not found. Check application.properties");
//    }
//}
