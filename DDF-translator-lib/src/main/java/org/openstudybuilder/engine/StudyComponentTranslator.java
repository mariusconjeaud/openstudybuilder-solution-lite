package org.openstudybuilder.engine;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;


/**
 * org.CDISC.DDF.composer.util.StudyComponentTranslator class is used to translate study objects into JSON or XML.
 *
 * @author Chris Upkes
 */

public class StudyComponentTranslator {

    // TODO implement method to translate a component to JSON
    // method could be overloaded to accept different objects.

    public static String translateStudyObjectToJSON(Object studyObject) throws JsonProcessingException {

        ObjectMapper mapper = new ObjectMapper();
        return mapper.writeValueAsString(studyObject);


    }






}
