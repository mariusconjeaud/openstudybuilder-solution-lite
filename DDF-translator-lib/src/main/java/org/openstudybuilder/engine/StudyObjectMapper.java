package org.openstudybuilder.engine;


import org.CSDISC.DDF.model.*;
import org.CSDISC.DDF.model.StudyDesign;
import org.openstudybuilder.model.Code;
import org.openstudybuilder.model.Population;
import org.openstudybuilder.model.*;
import org.w3c.dom.Document;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.StringWriter;
import java.util.*;


public class StudyObjectMapper {

    public org.CSDISC.DDF.model.Encounter map(Visit visit) {

        org.CSDISC.DDF.model.Encounter encounter = new Encounter(UUID.randomUUID().toString());
        encounter.setEncounterName(visit.getVisitName());
        encounter.setEncounterDescription(visit.getDescription());
        org.CSDISC.DDF.model.Code code = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
        code.setDecode(visit.getVisitTypeName());
        code.setCode(visit.getVisitTypeName());
        encounter.setEncounterType(code);
        org.CSDISC.DDF.model.TransitionRule startTransitionRule = new TransitionRule(UUID.randomUUID().toString());
        startTransitionRule.setTransitionRuleDescription(visit.getStartRule());
        org.CSDISC.DDF.model.TransitionRule endTransitionRule = new TransitionRule(UUID.randomUUID().toString());
        endTransitionRule.setTransitionRuleDescription(visit.getEndRule());
        encounter.setTransitionStartRule(startTransitionRule);
        encounter.setTransitionEndRule(endTransitionRule);
        org.CSDISC.DDF.model.Code contactMode = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
        contactMode.setCode(visit.getVisitContactModeUid());
        contactMode.setDecode(visit.getVisitContactModeName());
        encounter.setEncounterContactModes(List.of(contactMode));
        encounter.setEncounterEnvironmentalSetting(new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString()));
        return encounter;

    }

    public StudyDesignPopulation map(Population population) throws ParserConfigurationException, TransformerException {

        StudyDesignPopulation CDISCPopulation = new StudyDesignPopulation(UUID.randomUUID().toString());
        // replace with parseable xml object (DOM).

        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        DocumentBuilder db = dbf.newDocumentBuilder();
        Document document = db.newDocument();
        org.w3c.dom.Element rootElement = document.createElement("OpenStudyBuilderPopulation");
        document.appendChild(rootElement);
        org.w3c.dom.Element diagGroupCodesElement = document.createElement("DiagnosisGroupsCodes");
        for (Code code : population.getDiagnosisGroupCodes()) {

            org.w3c.dom.Element element = document.createElement("code");
            element.setTextContent(
                    code.getName() == null ? "null"
                            : code.getName()
            );
            diagGroupCodesElement.appendChild(element);


        }
        rootElement.appendChild(diagGroupCodesElement);

        org.w3c.dom.Element relapseCriteriaElement = document.createElement("relapseCriteria");
        relapseCriteriaElement.setTextContent(population.getRelapseCriteria() == null ? "null" :  population.getRelapseCriteria());
        rootElement.appendChild(relapseCriteriaElement);

        org.w3c.dom.Element diagGroupsNullValueCodeElement = document.createElement("DiagnosisGroupsNullValueCode");
        diagGroupsNullValueCodeElement.setTextContent(
                population.getDiagnosisGroupNullValueCode() == null ? "null"
                        :  population.getDiagnosisGroupNullValueCode().getName());

        rootElement.appendChild(diagGroupsNullValueCodeElement);

        org.w3c.dom.Element stableDiseaseMinDurationElement = document.createElement("StableDiseaseMinimumDuration");
        stableDiseaseMinDurationElement.setTextContent(
                population.getStableDiseaseMinimumDuration() == null ? "null"
                        : String.valueOf(population.getStableDiseaseMinimumDuration().getDurationValue()));
        rootElement.appendChild(stableDiseaseMinDurationElement);


        org.w3c.dom.Element diseaseConditionsOrIndicationsCodesElement =
                document.createElement("DiseaseConditionsOrIndicationsCodes");
        if (population.getDiseaseConditionOrIndicationCodes() != null)
        {
            for (Code code : population.getDiseaseConditionOrIndicationCodes()) {

                org.w3c.dom.Element element = document.createElement("code");
                element.setTextContent(
                        code.getName() == null ? "null"
                                : code.getName()
                );
                diagGroupCodesElement.appendChild(element);


            }

        }

        TransformerFactory tf = TransformerFactory.newInstance();
        Transformer trans = tf.newTransformer();
        StringWriter sw = new StringWriter();
        trans.transform(new DOMSource(document), new StreamResult(sw));

        CDISCPopulation.setPopulationDescription(sw.toString());
        return CDISCPopulation;

    }

    public org.CSDISC.DDF.model.InvestigationalIntervention map(Intervention intervention) {

        org.CSDISC.DDF.model.InvestigationalIntervention CDISCIntervention = new InvestigationalIntervention(UUID.randomUUID().toString());
        List<org.CSDISC.DDF.model.Code> CDISCCodes = new ArrayList<>();

        if (intervention.getInterventionModelCode() != null) {
            CDISCIntervention.setInterventionDescription(intervention.getInterventionModelCode().getName());
            org.CSDISC.DDF.model.Code CDISCCode = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
            CDISCCode.setCode(intervention.getInterventionModelCode().getName());
            CDISCCodes.add(CDISCCode);
        }

        if (intervention.getInterventionTypeCode() != null) {

            org.CSDISC.DDF.model.Code CDISCCode = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
            CDISCCode.setCode(intervention.getInterventionTypeCode().getName());
            CDISCCodes.add(CDISCCode);


        }

        if (intervention.getControlTypeCode() != null) {

            org.CSDISC.DDF.model.Code CDISCCode = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
            CDISCCode.setCode(intervention.getControlTypeCode().getName());
            CDISCCodes.add(CDISCCode);


        }

        if (intervention.getTrialBlindingSchemaCode() != null) {

            org.CSDISC.DDF.model.Code CDISCCode = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
            CDISCCode.setCode(intervention.getTrialBlindingSchemaCode().getName());
            CDISCCodes.add(CDISCCode);


        }

        if (intervention.getTrialIntentTypesCodes() != null) {

            for (Code code : intervention.getTrialIntentTypesCodes()) {
                org.CSDISC.DDF.model.Code CDISCCode = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
                CDISCCode.setCode(code.getName());
                CDISCCodes.add(CDISCCode);
            }


        }

        CDISCIntervention.setCodes(CDISCCodes);

        return CDISCIntervention;

    }

    public org.CSDISC.DDF.model.Objective map(StudySelectionObjective objective) {

        org.CSDISC.DDF.model.Objective CDISCObjective = new org.CSDISC.DDF.model.Objective(UUID.randomUUID().toString());
        CDISCObjective.setObjectiveDescription(objective.getObjective().getName());
        org.CSDISC.DDF.model.Code objectiveLevel = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
        objectiveLevel.setCode(objective.getObjectiveLevel().getCatalogueName());
        CDISCObjective.setObjectiveLevel(objectiveLevel);



        return CDISCObjective;
    }




    public org.CSDISC.DDF.model.Objective map(StudySelectionEndpoint studySelectionEndpoint) {

        // overloaded to associate endpoints with the objective, as per the CDISC specification.

        if (studySelectionEndpoint.getStudyObjective() != null  ) {

            org.CSDISC.DDF.model.Objective CDISCObjective = new org.CSDISC.DDF.model.Objective(UUID.randomUUID().toString());
            List<org.CSDISC.DDF.model.Endpoint> CDISCEndpoints = new ArrayList<>();
            org.CSDISC.DDF.model.Endpoint CDISCEndpoint = new org.CSDISC.DDF.model.Endpoint(UUID.randomUUID().toString());


            CDISCObjective.setObjectiveDescription(studySelectionEndpoint.getStudyObjective().getObjective().getName());
            // TODO change getStudyObjective method signature to getStudyObjectiveSection.
            org.CSDISC.DDF.model.Code objectiveLevel = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
            org.CSDISC.DDF.model.Code endpointLevel = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());

            objectiveLevel.setCode(studySelectionEndpoint.getStudyObjective().getObjectiveLevel().getSponsorPreferredName());
            CDISCObjective.setObjectiveLevel(objectiveLevel);

            CDISCEndpoint.setEndpointDescription(studySelectionEndpoint.getEndpoint().getName());
            CDISCEndpoint.setEndpointPurposeDescription(studySelectionEndpoint.getProjectName());
            endpointLevel.setCode(studySelectionEndpoint.getEndpointLevel().getSponsorPreferredName());
            CDISCEndpoint.setEndpointLevel(endpointLevel);
            CDISCEndpoints.add(CDISCEndpoint);
            CDISCObjective.setObjectiveEndpoints(CDISCEndpoints);
            return CDISCObjective;
        }
        return null;

    }



    public org.CSDISC.DDF.model.StudyElement map(Element element) {

        org.CSDISC.DDF.model.StudyElement studyElement = new StudyElement(UUID.randomUUID().toString());
        studyElement.setStudyElementName(element.getName());
        studyElement.setStudyElementDescription(element.getDescription());
        org.CSDISC.DDF.model.TransitionRule startTransitionRule = new TransitionRule(UUID.randomUUID().toString());
        org.CSDISC.DDF.model.TransitionRule endTransitionRule = new TransitionRule(UUID.randomUUID().toString());
        startTransitionRule.setTransitionRuleDescription(element.getStartRule());
        endTransitionRule.setTransitionRuleDescription(element.getEndRule());
        studyElement.setTransitionStartRule(startTransitionRule);
        studyElement.setTransitionEndRule(endTransitionRule);


        return studyElement;

    }

    public org.CSDISC.DDF.model.StudyArm map(Arm arm) {

        org.CSDISC.DDF.model.StudyArm studyArm = new StudyArm(UUID.randomUUID().toString());
        studyArm.setStudyArmName(arm.getName());
        studyArm.setStudyArmDescription(arm.getDescription());
        org.CSDISC.DDF.model.Code armType = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
        armType.setCode(arm.getArmType().getSponsorPreferredName());
        studyArm.setStudyArmType(armType);
        org.CSDISC.DDF.model.Code armDataOriginType = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
        studyArm.setStudyArmDataOriginType(armDataOriginType);
        return studyArm;

    }

    public org.CSDISC.DDF.model.StudyEpoch map(Epoch epoch) {

        org.CSDISC.DDF.model.StudyEpoch studyEpoch = new StudyEpoch(UUID.randomUUID().toString());
        studyEpoch.setStudyEpochName(epoch.getEpochName());
        studyEpoch.setStudyEpochDescription(epoch.getDescription());
        org.CSDISC.DDF.model.Code epochType = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
        epochType.setCode(epoch.getEpochType());
        studyEpoch.setStudyEpochType(epochType);

        return studyEpoch;

    }

    public org.CSDISC.DDF.model.Study map(OpenStudy openStudy, OpenStudyObjectFactory openStudyObjectFactory) throws
            Exception {

        String openStudyUid = openStudy.getUid();

        org.CSDISC.DDF.model.Study study = new Study(UUID.randomUUID());
        org.CSDISC.DDF.model.Code studyType = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
        org.CSDISC.DDF.model.StudyIdentifier studyIdentifier = new StudyIdentifier(UUID.randomUUID().toString());
        org.CSDISC.DDF.model.Organization organization = new Organization(UUID.randomUUID().toString());

        CurrentMetadata studyMd = openStudy.getCurrentMetadata();
        org.openstudybuilder.model.StudyDesign openStudyDesign = studyMd.getHighLevelStudyDesign();
        Code studyDesignTypeCode;
        if (openStudyDesign != null) {
            studyDesignTypeCode = openStudyDesign.getStudyTypeCode();
            if (studyDesignTypeCode != null) {
                studyType.setCode(studyDesignTypeCode.getName());
            }
        }
        study.setStudyType(studyType);
        // TODO: create StudyDescription class, avoid hardcoded key name
        study.setStudyTitle(studyMd.getStudyDescription().get("study_title"));
        // TODO - Must populate correctly organization info in study identifier (single value, In SDR it's an array)
        RegistryIdentifier registryIdentifier = studyMd.getIdentificationMetadata().getRegistryIdentifiers();
        studyIdentifier.setStudyIdentifier(registryIdentifier.getEudractId());
        organization.setOrganizationIdentifier(registryIdentifier.getCtGovId());
        studyIdentifier.setStudyIdentifierScope(organization);
        study.setStudyIdentifiers(List.of(studyIdentifier));

        // Protocol Versions
        org.CSDISC.DDF.model.StudyProtocolVersion protocolVersion = new StudyProtocolVersion(UUID.randomUUID().toString());
        // TODO: check these hardcoded values
        protocolVersion.setBriefTitle("Brief Title");
        protocolVersion.setOfficialTitle("Official Title");
        protocolVersion.setProtocolAmendment("Amendment");
        protocolVersion.setProtocolStatus(new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString()));
        protocolVersion.setProtocolVersion("1");
        protocolVersion.setPublicTitle("Public Title");
        protocolVersion.setScientificTitle("Scientific Title");
        protocolVersion.setProtocolEffectiveDate(new Date());
        study.setStudyProtocolVersions(List.of(protocolVersion));

        // Study Phase
        org.CSDISC.DDF.model.AliasCode studyPhase = new org.CSDISC.DDF.model.AliasCode(UUID.randomUUID().toString());
        org.CSDISC.DDF.model.Code studyPhaseCode = new org.CSDISC.DDF.model.Code(UUID.randomUUID().toString());
        Code studyDesignTrialPhaseCode;
        if (openStudyDesign != null) {
            studyDesignTrialPhaseCode = openStudyDesign.getTrialPhaseCode();
            if (studyDesignTrialPhaseCode != null) {
                studyPhaseCode.setCode(studyDesignTrialPhaseCode.getName());
            }
        }
        // TODO: check if codes are semantically right
        studyPhase.setStandardCode(studyPhaseCode);
        study.setStudyPhase(studyPhase);

        // Study Designs
        org.CSDISC.DDF.model.StudyDesign studyDesign = new StudyDesign(null);
        // Study Cells is an Array
        org.CSDISC.DDF.model.StudyCell studyCell = new StudyCell(null);
        List<Arm> openStudyArms = openStudyObjectFactory.getArms(openStudyUid);
        org.CSDISC.DDF.model.StudyArm studyArm = openStudyArms.size() > 0 ? map(openStudyArms.get(0)) : null;
        studyCell.setStudyArm(studyArm);
        // Build Epoch
        List<Epoch> openStudyEpochs = openStudyObjectFactory.getEpochs(openStudyUid);
        org.CSDISC.DDF.model.StudyEpoch studyEpoch = openStudyEpochs.size() > 0 ? map(openStudyEpochs.get(0)) : null;
        studyCell.setStudyEpoch(studyEpoch);
        // Study Elements
        List<Element> openStudyElements = openStudyObjectFactory.getElements(openStudyUid);
        List<org.CSDISC.DDF.model.StudyElement> studyElements = new ArrayList<>();
        for (Element element: openStudyElements) {
            studyElements.add(map(element));
        }
        // Investigational Intervention
        Intervention openStudyIntervention = studyMd.getStudyIntervention();
        InvestigationalIntervention intervention = map(openStudyIntervention);
        studyDesign.setStudyInvestigationalInterventions(List.of(intervention));
        // Visits/Encounter
        List<Visit> openStudyVisits = openStudyObjectFactory.getVisits(openStudyUid);
        List<Encounter> encounters = new ArrayList<>();
        for(Visit visit: openStudyVisits) {
            encounters.add(map(visit));
        }
        studyDesign.setEncounters(encounters);
        studyCell.setStudyElements(studyElements);
        studyDesign.setStudyCells(List.of(studyCell));
        study.setStudyDesigns(List.of(studyDesign));



        return study;
    }

    private boolean checkForMapKey(Map<String, String> inputMap, String strKey) {
        return inputMap != null && inputMap.containsKey(strKey);
    }

}

