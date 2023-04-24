package org.openstudybuilder.utils;

import com.google.api.client.http.*;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.JsonFactory;
import com.google.api.client.json.JsonObjectParser;
import com.google.api.client.json.jackson2.JacksonFactory;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.logging.Logger;

public class HttpRestClient {

    private static final String CLINICAL_MDR_BASE_URL = TranslatorUtils.getMdrBaseUrl();
    private final String BEARER_TOKEN;
    private static final HttpTransport HTTP_TRANSPORT = new NetHttpTransport();
    private static final JsonFactory JSON_FACTORY = new JacksonFactory();
    private HttpRequestFactory httpRequestFactory;

    private static final Logger logger = Logger.getLogger(HttpRestClient.class.getName());

    public HttpRestClient(String bearerToken) {
        this.BEARER_TOKEN =
                bearerToken.startsWith("Bearer") ? bearerToken : "Bearer ".concat(bearerToken);
        this.httpRequestFactory = HTTP_TRANSPORT.createRequestFactory(
                new HttpRequestInitializer() {
                    @Override
                    public void initialize(HttpRequest request) {
                        request.setParser(new JsonObjectParser(JSON_FACTORY));
                    }
                });
    }

    private static class OpenStudyApiUrl extends GenericUrl {
        public OpenStudyApiUrl(String encodedUrl) {
            super(encodedUrl);
        }
    }

    public HttpResponse sendGetRequest(String path) throws IOException {
        try {
            OpenStudyApiUrl openStudyApiUrl = new OpenStudyApiUrl(CLINICAL_MDR_BASE_URL.concat(path));
            HttpRequest httpRequest = httpRequestFactory.buildGetRequest(openStudyApiUrl);
            HttpHeaders headers = new HttpHeaders();
            headers.setAccept("application/json");
            if (BEARER_TOKEN != null) {
                headers.setAuthorization(BEARER_TOKEN);
            }
            else {
                logger.warning("Issuing GET request without Authorization Header");
            }
            httpRequest.setHeaders(headers);
            HttpResponse response = httpRequest.execute();
            logger.fine(String.format("Received response from Api Server: %1$s", response));
            return response;
        }
        catch (HttpResponseException httpResponseException) {
            if (httpResponseException.getStatusCode() == HttpStatusCodes.STATUS_CODE_NOT_FOUND) {
                logger.warning("Endpoint returned 404 for request. Check /api endpoint configuration");
            }
            else {
                logger.severe("Study Builder Api Request Failed.");
            }
            throw httpResponseException;
        }
    }

    //TODO This is prob not needed since we won't issue POST requests to Study Builder
    public HttpResponse sendPostRequest(String path, String body) throws IOException {
        try {
            OpenStudyApiUrl openStudyApiUrl = new OpenStudyApiUrl(CLINICAL_MDR_BASE_URL.concat(path));
            HttpRequest httpRequest = httpRequestFactory.buildPostRequest(openStudyApiUrl,
                    new ByteArrayContent(null, body.getBytes(StandardCharsets.UTF_8)));
            httpRequest.setRequestMethod(HttpMethods.POST);
            HttpHeaders headers = new HttpHeaders();
            headers.setAuthorization(BEARER_TOKEN);
            httpRequest.setHeaders(headers);
            HttpResponse response = httpRequest.execute();
            logger.fine(String.format("Received response from Api Server: %1$s", response));
            return response;
        }
        catch (HttpResponseException httpResponseException) {
            if (httpResponseException.getStatusCode() == HttpStatusCodes.STATUS_CODE_NOT_FOUND) {
                logger.warning("Endpoint returned 404 for request. Check /api endpoint configuration");
            }
            else {
                logger.severe("Study Builder Api Request Failed.");
            }
            throw httpResponseException;
        }
    }
}
