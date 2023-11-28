package org.openstudybuilder.engine;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.openstudybuilder.model.*;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.TransformerException;
import java.util.List;

class StudyComponentTranslatorTest {

    private final OpenStudyObjectFactory objectFactory = OpenStudyObjectFactory.withStaticBuilderAdaptor();


    @Test
    void translateEncounter() throws Exception {

        StudyObjectMapper studyObjectMapper = new StudyObjectMapper();
        List<Visit> visits = objectFactory.getVisits("001");
        org.CDISC.DDF.model.Encounter encounter = studyObjectMapper.map(visits.get(0));
        String eventJSON = StudyComponentTranslator.translateStudyObjectToJSON(encounter);
        Assertions.assertNotNull(eventJSON);
        System.out.println(eventJSON);

    }

    @Test
    void translatePopulation() throws Exception {

        StudyObjectMapper studyObjectMapper = new StudyObjectMapper();
        Population population = objectFactory.getPopulation("001");
        org.CDISC.DDF.model.StudyDesignPopulation CDISCPopulation = studyObjectMapper.map(population);
        System.out.println(CDISCPopulation.getPopulationDescription());
        String eventJSON = StudyComponentTranslator.translateStudyObjectToJSON(CDISCPopulation);
        Assertions.assertNotNull(eventJSON);
        System.out.println(eventJSON);

    }

    @Test
    void translateObjective() throws Exception {
        StudyObjectMapper studyObjectMapper = new StudyObjectMapper();
        List<StudySelectionEndpoint> studySelectionEndpoints = objectFactory.getStudyEndpointSections("001");
        org.CDISC.DDF.model.Objective CDISCObjective = studyObjectMapper.map(studySelectionEndpoints.get(0));
        String eventJSON = StudyComponentTranslator.translateStudyObjectToJSON(CDISCObjective);
        Assertions.assertNotNull(eventJSON);
        System.out.println(eventJSON);

    }

    @Test
    void translateInvestigationalIntervention() throws Exception {

        StudyObjectMapper studyObjectMapper = new StudyObjectMapper();
        Intervention intervention = objectFactory.getIntervention("001");
        org.CDISC.DDF.model.InvestigationalIntervention investigationalIntervention = studyObjectMapper.map(intervention);
        String eventJSON = StudyComponentTranslator.translateStudyObjectToJSON(investigationalIntervention);
        Assertions.assertNotNull(eventJSON);
        System.out.println(eventJSON);

    }

    @Test
    void translateStudyArm() throws Exception {

        StudyObjectMapper studyObjectMapper = new StudyObjectMapper();
        List<Arm> arms = objectFactory.getArms("001");
        org.CDISC.DDF.model.StudyArm studyArm = studyObjectMapper.map(arms.get(0));
        String eventJSON = StudyComponentTranslator.translateStudyObjectToJSON(studyArm);
        Assertions.assertNotNull(eventJSON);
        System.out.println(eventJSON);

    }

    @Test
    void translateStudyEpoch() throws Exception {

        StudyObjectMapper studyObjectMapper = new StudyObjectMapper();
        List<Epoch> epochs = objectFactory.getEpochs("001");
        org.CDISC.DDF.model.StudyEpoch studyEpoch = studyObjectMapper.map(epochs.get(0));
        String eventJSON = StudyComponentTranslator.translateStudyObjectToJSON(studyEpoch);
        Assertions.assertNotNull(eventJSON);
        System.out.println(eventJSON);

    }

    @Test
    void translateStudyElement() throws Exception {

        StudyObjectMapper studyObjectMapper = new StudyObjectMapper();
        List<Element> elements = objectFactory.getElements("001");
        org.CDISC.DDF.model.StudyElement studyElement = studyObjectMapper.map(elements.get(0));
        String eventJSON = StudyComponentTranslator.translateStudyObjectToJSON(studyElement);
        Assertions.assertNotNull(eventJSON);
        System.out.println(eventJSON);

    }


}