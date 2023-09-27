package org.openstudybuilder.utils;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.cloud.storage.BlobId;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageException;
import com.google.cloud.storage.StorageOptions;

import java.io.IOException;
import java.io.InputStream;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

public class TranslatorUtils {

    private static final String APP_PROPERTIES_FILE = "/application.properties";
    private static final Logger logger = Logger.getLogger(TranslatorUtils.class.getName());

    public static void loadProperties() {
        try {
            InputStream file = TranslatorUtils.class.getResourceAsStream(APP_PROPERTIES_FILE);
            if (file != null) System.getProperties().load(file);
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Could not load application.properties", e);
            throw new RuntimeException("Error loading application.properties", e);
        }
    }

    public static String getMdrBaseUrl() {
        return System.getProperty("clinical_mdr_base_url");
    }

    public static String getTotCountParamName() {
        return System.getProperty("builder_api_total_count_param");
    }

    public static String getUseTotCountParam() {
        return System.getProperty("builder_api_use_total_count");
    }

    public static String getPageSizeParamName() {
        return System.getProperty("builder_api_page_size_param");
    }

    public static String getDefaultPageSize() {
        return System.getProperty("builder_api_default_page_size");
    }

    public static String getPageNumberParamName() {
        return System.getProperty("builder_api_page_number_param");
    }

    public static String getSortingOptionParamName() {
        return System.getProperty("builder_api_sorting_param");
    }

    public static String attachDefaultSortingParams(String url) {
        String result;
        if (!url.contains("?")) {
            result = url.concat("?");
        }
        else {
            result = url.concat("&");
        }
        result = result.concat(getTotCountParamName() + '=').concat(getUseTotCountParam());
        result = result.concat("&").concat(getPageSizeParamName() + '=').concat(getDefaultPageSize());
        return result;
    }

    public static String attachQueryStringParam(String url, String paramName, Object paramValue)
            throws JsonProcessingException {
        String result;
        if (!url.contains("?")) {
            result = url.concat("?");
        }
        else {
            result = url.concat("&");
        }
        if (paramValue instanceof Map) {
            paramValue = new ObjectMapper().writeValueAsString(paramValue);
        }
        result = result.concat(paramName + '=').concat(paramValue.toString());
        return result;
    }

    /**
     * To use this method, create a service account in gcp with bucket reader role, create account key, download json file
     * and reference it in the test classes via the GOOGLE_APPLICATION_CREDENTIALS env variable (modify run config)
     * @return Bearer token as read from the GCP bucket object (which is defined via app properties)
     */
    public static String getAuthTokenFromGcp() throws StorageException {
        Storage storage = StorageOptions.newBuilder().setProjectId(System.getProperty("gcp_project_id"))
                .build().getService();
        byte[] contents = storage.readAllBytes(BlobId.of(System.getProperty("gcp_bucket_name"),
                        System.getProperty("gcp_object_name")));

        return new String(contents).trim();
    }
}
