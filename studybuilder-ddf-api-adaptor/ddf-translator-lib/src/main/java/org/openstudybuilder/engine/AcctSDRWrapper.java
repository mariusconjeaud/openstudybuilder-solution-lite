//package org.openstudybuilder.engine;
//
//import com.fasterxml.jackson.annotation.JsonRootName;
//import com.fasterxml.jackson.databind.DeserializationFeature;
//import com.fasterxml.jackson.databind.ObjectMapper;
//import com.fasterxml.jackson.databind.SerializationFeature;
//import com.google.gson.JsonElement;
//import com.google.gson.JsonObject;
//import lombok.Getter;
//import lombok.NoArgsConstructor;
//import lombok.Setter;
//import org.CSDISC.DDF.model.Code;
//import org.CSDISC.DDF.model.StudyDesign;
//import org.openstudybuilder.model.CurrentMetadata;
//import org.openstudybuilder.model.OpenStudy;
//import org.openstudybuilder.sdr.acct.AcctSdrStudy;
//
//import javax.annotation.Nullable;
//import java.util.List;
//import java.util.Map;
//import java.util.UUID;
//
///**
// * Wrapper for generating standard compliant studies that can be submitted to the Transcelerate SDR
// */
//public class AcctSDRWrapper {
//
//    private OpenStudyObjectFactory openStudyObjectFactory;
//
//    public AcctSDRWrapper(String studyBuilderAuth) {
//        this.openStudyObjectFactory = OpenStudyObjectFactory
//                .withRestApiClient(studyBuilderAuth);
//    }
//
//    /**
//     * Makes the necessary Open Study Builder API Calls to compose a study that can be posted to the SDR
//     * High Level Steps
//     * 1- Pull basic metadata
//     * 2- Incorporate into ACCT Model
//     * 3- Map additional study components
//     * 4- Stub any missing information
//     * 5- Issue response
//     * @param studyUid - This is the Open Study Builder StudyUid
//     * @return JSON String with SDR Acct-compatible study definition
//     */
//    public String composeStudy(String studyUid) throws Exception {
//        OpenStudy study = openStudyObjectFactory.getStudy(studyUid);
//        //StudyObjectMapper studyObjectMapper = new StudyObjectMapper();
//        AcctSdrStudy outputStudy = new AcctSdrStudy(study, openStudyObjectFactory, UUID.randomUUID());
//
//        //outputStudy.setClinicalStudy(studyObjectMapper.map(study, openStudyObjectFactory));
//        ObjectMapper objectMapper = new ObjectMapper();
//        objectMapper.enable(DeserializationFeature.UNWRAP_ROOT_VALUE);
//        objectMapper.enable(SerializationFeature.WRAP_ROOT_VALUE);
//        return objectMapper.writeValueAsString(outputStudy.getStudyDef());
//        //return outputStudy.toString();
//    }
//
////    /**
////     * Ok for things that aren't CDISC
////     */
////    @JsonRootName(value = "clinicalStudy")
////    @Getter @Setter
////    @NoArgsConstructor
////    class AcctSdrStudy {
////        private org.CSDISC.DDF.model.Study clinicalStudy;
////        // get the necessary items, set properties individually if we're stubbing values
////    }
////
////    class AcctProtocolVersion extends org.CSDISC.DDF.model.StudyProtocolVersion {
////        private List<Code> protocolStatus;
////
////        public AcctProtocolVersion(UUID studyProtocolVersionId) {
////            super(studyProtocolVersionId);
////        }
////    }
//
//}