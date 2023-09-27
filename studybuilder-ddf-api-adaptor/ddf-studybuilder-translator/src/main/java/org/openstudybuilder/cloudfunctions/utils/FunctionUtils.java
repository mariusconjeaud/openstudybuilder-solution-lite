package org.openstudybuilder.cloudfunctions.utils;

import java.io.IOException;
import java.io.InputStream;
import java.util.logging.Level;
import java.util.logging.Logger;

public class FunctionUtils {

    private static final Logger logger = Logger.getLogger(FunctionUtils.class.getName());
    private static final String APP_PROPERTIES_FILE = "/application.properties";

    public static void loadProperties() {
        try {
            InputStream file = FunctionUtils.class.getResourceAsStream(APP_PROPERTIES_FILE);
            if (file!=null) System.getProperties().load(file);
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Could not load application.properties", e);
            throw new RuntimeException("Error loading application.properties", e);
        }
    }

    public static String getMdrBaseUrl() {
        return System.getProperty("clinical_mdr_base_url");
    }
}
