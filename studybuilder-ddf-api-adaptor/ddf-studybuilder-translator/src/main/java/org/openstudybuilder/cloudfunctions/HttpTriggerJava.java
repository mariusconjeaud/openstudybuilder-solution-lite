package org.openstudybuilder.cloudfunctions;

import java.util.*;
import java.util.logging.Level;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.microsoft.azure.functions.annotation.*;
import com.microsoft.azure.functions.*;
import org.CDISC.DDF.model.Study;
import org.openstudybuilder.cloudfunctions.utils.FunctionUtils;
import org.openstudybuilder.engine.OpenStudyObjectFactory;
import org.openstudybuilder.engine.StudyObjectMapper;
import org.openstudybuilder.model.OpenStudy;

/**
 * Azure Functions with HTTP Trigger.
 */
public class HttpTriggerJava {
    /**
     * Endpoint for getting a study definition compliant with the DDF data model
     * through a GET request that provides the study ID and the authorization token for accessing the study
     * definition from source APIs
     */
    @FunctionName("studyDefinitions")
    public HttpResponseMessage run(
            @HttpTrigger(
                    name = "req",
                    methods = {HttpMethod.GET, HttpMethod.POST},
                    authLevel = AuthorizationLevel.ANONYMOUS)
            HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) throws Exception {
        try {
            context.getLogger().info("Java HTTP trigger processed a request.");
            // Load system properties
            FunctionUtils.loadProperties();
            context.getLogger().log(Level.INFO, String.format("System properties: %s", System.getProperties().toString()));
            // Get auth token
            String API_TOKEN = request.getHeaders().get("authorization");
            // Create object factory
            OpenStudyObjectFactory objectFactory = OpenStudyObjectFactory.withRestApiClient(API_TOKEN);
            // Parse query parameter
            final String studyId = request.getQueryParameters().get("studyId");

            if (studyId == null) {
                return request.createResponseBuilder(HttpStatus.BAD_REQUEST).body("Please pass a studyId on the query string").build();
            } else {
                context.getLogger().log(Level.ALL, objectFactory.toString());
                // Get OSB study
                OpenStudy openStudy = objectFactory.getStudy(studyId);
                context.getLogger().log(Level.ALL, openStudy.getStudyId());
                StudyObjectMapper studyObjectMapper = new StudyObjectMapper();
                Study study = studyObjectMapper.map(openStudy, objectFactory);
                // Create JSON response
                ObjectMapper objectMapper = new ObjectMapper();
                objectMapper.enable(DeserializationFeature.UNWRAP_ROOT_VALUE);
                objectMapper.enable(SerializationFeature.WRAP_ROOT_VALUE);
                String jsonRes = objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(study);

                return request.createResponseBuilder(HttpStatus.OK).body(jsonRes).build();
            }
        } catch (Exception e) {
            context.getLogger().log(Level.ALL, e.toString());
            throw e;
        }
    }
}
