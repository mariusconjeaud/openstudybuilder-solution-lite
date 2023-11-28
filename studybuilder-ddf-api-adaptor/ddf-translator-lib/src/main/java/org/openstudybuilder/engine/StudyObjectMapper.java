package org.openstudybuilder.engine;


import org.CDISC.DDF.model.Objective;
import org.CDISC.DDF.model.StudyDesign;
import org.CDISC.DDF.model.*;
import org.openstudybuilder.model.Activity;
import org.openstudybuilder.model.Code;
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

    public org.CDISC.DDF.model.StudyDesign map(org.openstudybuilder.model.StudyDesign osbStudyDesign, Intervention osbIntervention) {
        org.CDISC.DDF.model.StudyDesign ddfStudyDesign = new StudyDesign(UUID.randomUUID().toString());

        List<org.CDISC.DDF.model.Code> ddfTrialTypeCodes = new ArrayList<>();
        for(Code osbTrialTypeCode : osbStudyDesign.getTrialTypeCodes()) {
            org.CDISC.DDF.model.Code ddfTrialTypeCode = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
            ddfTrialTypeCode.setCode(osbTrialTypeCode.getTermUid());
            ddfTrialTypeCode.setDecode(osbTrialTypeCode.getName());
            ddfTrialTypeCodes.add(ddfTrialTypeCode);
        }
        ddfStudyDesign.setTrialType(ddfTrialTypeCodes);

        org.CDISC.DDF.model.Code ddfInterventionModelCode = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
        Code osbInterventionModelCode = osbIntervention.getInterventionModelCode();
        if(osbInterventionModelCode != null) {
            ddfInterventionModelCode.setCode(osbInterventionModelCode.getTermUid());
            ddfInterventionModelCode.setDecode(osbInterventionModelCode.getName());
            ddfStudyDesign.setInterventionModel(ddfInterventionModelCode);
        }

        return ddfStudyDesign;
    }

    public org.CDISC.DDF.model.Encounter map(Visit visit) {

        org.CDISC.DDF.model.Encounter encounter = new Encounter(visit.getUid());
        encounter.setEncounterName(visit.getVisitName());
        encounter.setEncounterDescription(visit.getDescription());
        org.CDISC.DDF.model.Code code = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
        code.setDecode(visit.getVisitTypeName());
        code.setCode(visit.getVisitTypeName());
        encounter.setEncounterType(code);
        org.CDISC.DDF.model.TransitionRule startTransitionRule = new TransitionRule(UUID.randomUUID().toString());
        startTransitionRule.setTransitionRuleDescription(visit.getStartRule());
        org.CDISC.DDF.model.TransitionRule endTransitionRule = new TransitionRule(UUID.randomUUID().toString());
        endTransitionRule.setTransitionRuleDescription(visit.getEndRule());
        encounter.setTransitionStartRule(startTransitionRule);
        encounter.setTransitionEndRule(endTransitionRule);
        org.CDISC.DDF.model.Code contactMode = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
        contactMode.setCode(visit.getVisitContactModeUid());
        contactMode.setDecode(visit.getVisitContactModeName());
        List<org.CDISC.DDF.model.Code> contactModes = new ArrayList<>();
        contactModes.add(contactMode);
        encounter.setEncounterContactModes(contactModes);
        encounter.setEncounterEnvironmentalSetting(new org.CDISC.DDF.model.Code(UUID.randomUUID().toString()));
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

    public org.CDISC.DDF.model.InvestigationalIntervention map(Intervention intervention) {

        org.CDISC.DDF.model.InvestigationalIntervention CDISCIntervention = new InvestigationalIntervention(UUID.randomUUID().toString());
        List<org.CDISC.DDF.model.Code> CDISCCodes = new ArrayList<>();

        if (intervention.getInterventionModelCode() != null) {
            CDISCIntervention.setInterventionDescription(intervention.getInterventionModelCode().getName());
            org.CDISC.DDF.model.Code CDISCCode = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
            CDISCCode.setCode(intervention.getInterventionModelCode().getName());
            CDISCCodes.add(CDISCCode);
        }

        if (intervention.getInterventionTypeCode() != null) {

            org.CDISC.DDF.model.Code CDISCCode = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
            CDISCCode.setCode(intervention.getInterventionTypeCode().getName());
            CDISCCodes.add(CDISCCode);


        }

        if (intervention.getControlTypeCode() != null) {

            org.CDISC.DDF.model.Code CDISCCode = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
            CDISCCode.setCode(intervention.getControlTypeCode().getName());
            CDISCCodes.add(CDISCCode);


        }

        if (intervention.getTrialBlindingSchemaCode() != null) {

            org.CDISC.DDF.model.Code CDISCCode = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
            CDISCCode.setCode(intervention.getTrialBlindingSchemaCode().getName());
            CDISCCodes.add(CDISCCode);


        }

        if (intervention.getTrialIntentTypesCodes() != null) {

            for (Code code : intervention.getTrialIntentTypesCodes()) {
                org.CDISC.DDF.model.Code CDISCCode = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
                CDISCCode.setCode(code.getName());
                CDISCCodes.add(CDISCCode);
            }


        }

        CDISCIntervention.setCodes(CDISCCodes);

        return CDISCIntervention;

    }


    public org.CDISC.DDF.model.Objective map(StudySelectionEndpoint studySelectionEndpoint) {

        // overloaded to associate endpoints with the objective, as per the CDISC specification.

        if (studySelectionEndpoint.getStudyObjective() != null  ) {

            org.CDISC.DDF.model.Objective CDISCObjective = new org.CDISC.DDF.model.Objective(UUID.randomUUID().toString());
            List<org.CDISC.DDF.model.Endpoint> CDISCEndpoints = new ArrayList<>();
            org.CDISC.DDF.model.Endpoint CDISCEndpoint = new org.CDISC.DDF.model.Endpoint(UUID.randomUUID().toString());


            CDISCObjective.setObjectiveDescription(studySelectionEndpoint.getStudyObjective().getObjective().getName());
            // TODO change getStudyObjective method signature to getStudyObjectiveSection.
            org.CDISC.DDF.model.Code objectiveLevel = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
            org.CDISC.DDF.model.Code endpointLevel = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
            //objectiveLevel.setCode(objective.getObjectiveLevel().getCatalogueName());
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



    public org.CDISC.DDF.model.StudyElement map(Element element) {

        org.CDISC.DDF.model.StudyElement studyElement = new StudyElement(UUID.randomUUID().toString());
        studyElement.setStudyElementName(element.getName());
        studyElement.setStudyElementDescription(element.getDescription());
        org.CDISC.DDF.model.TransitionRule startTransitionRule = new TransitionRule(UUID.randomUUID().toString());
        org.CDISC.DDF.model.TransitionRule endTransitionRule = new TransitionRule(UUID.randomUUID().toString());
        startTransitionRule.setTransitionRuleDescription(element.getStartRule());
        endTransitionRule.setTransitionRuleDescription(element.getEndRule());
        studyElement.setTransitionStartRule(startTransitionRule);
        studyElement.setTransitionEndRule(endTransitionRule);


        return studyElement;

    }

    public org.CDISC.DDF.model.StudyArm map(Arm arm) {

        org.CDISC.DDF.model.StudyArm studyArm = new StudyArm(UUID.randomUUID().toString());
        studyArm.setStudyArmName(arm.getName());
        studyArm.setStudyArmDescription(arm.getDescription());
        org.CDISC.DDF.model.Code armType = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
        armType.setCode(arm.getArmType().getSponsorPreferredName());
        studyArm.setStudyArmType(armType);
        org.CDISC.DDF.model.Code armDataOriginType = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
        studyArm.setStudyArmDataOriginType(armDataOriginType);
        return studyArm;

    }

    public org.CDISC.DDF.model.StudyEpoch map(Epoch epoch) {

        org.CDISC.DDF.model.StudyEpoch studyEpoch = new StudyEpoch(UUID.randomUUID().toString());
        studyEpoch.setStudyEpochName(epoch.getEpochName());
        studyEpoch.setStudyEpochDescription(epoch.getDescription());
        org.CDISC.DDF.model.Code epochType = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
        epochType.setCode(epoch.getEpochType());
        studyEpoch.setStudyEpochType(epochType);

        return studyEpoch;

    }

    public org.CDISC.DDF.model.Study map(OpenStudy osbStudy, OpenStudyObjectFactory osbObjectFactory) throws
            Exception {

        String osbStudyUid = osbStudy.getUid();

        org.CDISC.DDF.model.Study ddfStudy = new Study(UUID.randomUUID());
        org.CDISC.DDF.model.Code ddfStudyType = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
        org.CDISC.DDF.model.StudyIdentifier ddfStudyIdentifier = new StudyIdentifier(UUID.randomUUID().toString());
        org.CDISC.DDF.model.Organization ddfOrganization = new Organization(UUID.randomUUID().toString());

        CurrentMetadata osbStudyMetadata = osbStudy.getCurrentMetadata();
        org.openstudybuilder.model.StudyDesign osbStudyDesign = osbStudyMetadata.getHighLevelStudyDesign();
        Code osbStudyDesignTypeCode;
        if (osbStudyDesign != null) {
            osbStudyDesignTypeCode = osbStudyDesign.getStudyTypeCode();
            if (osbStudyDesignTypeCode != null) {
                ddfStudyType.setCode(osbStudyDesignTypeCode.getName());
            } else {
                ddfStudyType.setCode(UUID.randomUUID().toString());
            }
        }
        ddfStudy.setStudyType(ddfStudyType);
        if(osbStudyMetadata.getVersionMetadata() != null) {
            ddfStudy.setStudyVersion(String.valueOf(osbStudyMetadata.getVersionMetadata().getVersionNumber()));
        }
        // TODO: create StudyDescription class, avoid hardcoded key name
        ddfStudy.setStudyTitle(osbStudyMetadata.getStudyDescription().get("study_title"));
        // TODO - Must populate correctly organization info in study identifier (single value, In SDR it's an array)
        RegistryIdentifier osbRegistryIdentifier = osbStudyMetadata.getIdentificationMetadata().getRegistryIdentifiers();
        ddfStudyIdentifier.setStudyIdentifier(osbRegistryIdentifier.getEudractId());
        ddfOrganization.setOrganizationIdentifier(osbRegistryIdentifier.getCtGovId());
        ddfStudyIdentifier.setStudyIdentifierScope(ddfOrganization);
        List<org.CDISC.DDF.model.StudyIdentifier> ddfStudyIdentifiers = new ArrayList<>();
        ddfStudyIdentifiers.add(ddfStudyIdentifier);
        ddfStudy.setStudyIdentifiers(ddfStudyIdentifiers);

        // Protocol Versions
        org.CDISC.DDF.model.StudyProtocolVersion ddfProtocolVersion = new StudyProtocolVersion(UUID.randomUUID().toString());
        // TODO: check these hardcoded values
        ddfProtocolVersion.setBriefTitle("Brief Title");
        ddfProtocolVersion.setOfficialTitle("Official Title");
        ddfProtocolVersion.setProtocolAmendment("Amendment");
        ddfProtocolVersion.setProtocolStatus(new org.CDISC.DDF.model.Code(UUID.randomUUID().toString()));
        ddfProtocolVersion.setProtocolVersion("1");
        ddfProtocolVersion.setPublicTitle("Public Title");
        ddfProtocolVersion.setScientificTitle("Scientific Title");
        ddfProtocolVersion.setProtocolEffectiveDate(new Date());
        List<org.CDISC.DDF.model.StudyProtocolVersion> ddfProtocolVersions = new ArrayList<>();
        ddfProtocolVersions.add(ddfProtocolVersion);
        ddfStudy.setStudyProtocolVersions(ddfProtocolVersions);

        // Study Phase
        org.CDISC.DDF.model.AliasCode ddfStudyPhase = new org.CDISC.DDF.model.AliasCode(UUID.randomUUID().toString());
        org.CDISC.DDF.model.Code ddfStudyPhaseCode = new org.CDISC.DDF.model.Code(UUID.randomUUID().toString());
        Code osbStudyDesignTrialPhaseCode;
        if (osbStudyDesign != null) {
            osbStudyDesignTrialPhaseCode = osbStudyDesign.getTrialPhaseCode();
            if (osbStudyDesignTrialPhaseCode != null) {
                ddfStudyPhaseCode.setCode(osbStudyDesignTrialPhaseCode.getName());
            }
        }
        // TODO: check if codes are semantically right
        ddfStudyPhase.setStandardCode(ddfStudyPhaseCode);
        ddfStudy.setStudyPhase(ddfStudyPhase);

        // Study Designs
        org.CDISC.DDF.model.StudyDesign ddfStudyDesign = osbStudyDesign != null ? map(osbStudyDesign, osbStudyMetadata.getStudyIntervention()) : new StudyDesign(UUID.randomUUID().toString());
        // Study Cells is an Array
        org.CDISC.DDF.model.StudyCell ddfStudyCell = new StudyCell(null);
        List<Arm> osbStudyArms = osbObjectFactory.getArms(osbStudyUid);
        org.CDISC.DDF.model.StudyArm ddfStudyArm = !osbStudyArms.isEmpty() ? map(osbStudyArms.get(0)) : null;
        ddfStudyCell.setStudyArm(ddfStudyArm);
        // Build Epoch
        List<Epoch> osbStudyEpochs = osbObjectFactory.getEpochs(osbStudyUid);
        org.CDISC.DDF.model.StudyEpoch studyEpoch = !osbStudyEpochs.isEmpty() ? map(osbStudyEpochs.get(0)) : null;
        ddfStudyCell.setStudyEpoch(studyEpoch);
        // Study Elements
        List<Element> osbStudyElements = osbObjectFactory.getElements(osbStudyUid);
        List<org.CDISC.DDF.model.StudyElement> ddfStudyElements = new ArrayList<>();
        for (Element osbElement: osbStudyElements) {
            ddfStudyElements.add(map(osbElement));
        }
        ddfStudyCell.setStudyElements(ddfStudyElements);
        List<org.CDISC.DDF.model.StudyCell> ddfStudyCells = new ArrayList<>();
        ddfStudyCells.add(ddfStudyCell);
        ddfStudyDesign.setStudyCells(ddfStudyCells);

        // Population
        Population osbStudyPopulation = osbStudyMetadata.getStudyPopulation();
        StudyDesignPopulation ddfPopulation = map(osbStudyPopulation);
        List<StudyDesignPopulation> ddfPopulations = new ArrayList<>();
        ddfPopulations.add(ddfPopulation);
        ddfStudyDesign.setStudyPopulations(ddfPopulations);

        // Objectives
        List<StudySelectionEndpoint> osbStudyEndpoints = osbObjectFactory.getStudyEndpointSections(osbStudyUid);
        List<Objective> ddfObjectives = new ArrayList<>();
        for(StudySelectionEndpoint osbStudyEndpoint : osbStudyEndpoints) {
            ddfObjectives.add(map(osbStudyEndpoint));
        }
        ddfStudyDesign.setStudyObjectives(ddfObjectives);


        // Investigational Intervention
        Intervention osbStudyIntervention = osbStudyMetadata.getStudyIntervention();
        InvestigationalIntervention ddfStudyInvestigationalIntervention = map(osbStudyIntervention);
        List<InvestigationalIntervention> ddfStudyInvestigationalInterventions = new ArrayList<>();
        ddfStudyInvestigationalInterventions.add(ddfStudyInvestigationalIntervention);
        ddfStudyDesign.setStudyInvestigationalInterventions(ddfStudyInvestigationalInterventions);
        // Visits/Encounter
        List<Visit> osbStudyVisits = osbObjectFactory.getVisits(osbStudyUid);
        List<Encounter> ddfEncounters = new ArrayList<>();
        for(Visit osbStudyVisit: osbStudyVisits) {
            ddfEncounters.add(map(osbStudyVisit));
        }
        ddfStudyDesign.setEncounters(ddfEncounters);
        // Activities and Procedures
        List<StudyActivitySection> osbStudyActivitySections = osbObjectFactory.getActivitySections(osbStudyUid);
        List<org.CDISC.DDF.model.Activity> ddfActivities = new ArrayList<>();
        for (StudyActivitySection osbStudyActivitySection : osbStudyActivitySections) {
            org.CDISC.DDF.model.Activity ddfActivity = map(osbStudyActivitySection);
            ddfActivity.setNextActivityId(getNextActivityUid(ddfActivity.getActivityId(), osbStudyActivitySections));
            ddfActivity.setPreviousActivityId(getPreviousActivityUid(ddfActivity.getActivityId(), osbStudyActivitySections));
            ddfActivities.add(ddfActivity);
        }
        ddfStudyDesign.setActivities(ddfActivities);
        // Schedule Timelines
        List<StudyActivitySchedule> studyActivitySchedules = osbObjectFactory.getActivitySchedules(osbStudyUid);
        ScheduleTimeline ddfTimeline = new ScheduleTimeline(UUID.randomUUID().toString());
        ddfTimeline.setScheduleTimelineName("Main Timeline");
        List<ScheduledInstance> ddfTimelineInstances = new ArrayList<>();
        for (StudyActivitySchedule studyActivitySchedule : studyActivitySchedules) {
            ddfTimelineInstances.add(map(studyActivitySchedule));
        }
        ddfTimeline.setScheduleTimelineInstances(ddfTimelineInstances);
        List<ScheduleTimeline> ddfTimelines = new ArrayList<>();
        ddfTimelines.add(ddfTimeline);
        ddfStudyDesign.setStudyScheduleTimelines(ddfTimelines);


        List<StudyDesign> ddfStudyDesigns = new ArrayList<>();
        ddfStudyDesigns.add(ddfStudyDesign);
        ddfStudy.setStudyDesigns(ddfStudyDesigns);


        return ddfStudy;
    }

    private boolean checkForMapKey(Map<String, String> inputMap, String strKey) {
        return inputMap != null && inputMap.containsKey(strKey);
    }

    public org.CDISC.DDF.model.Procedure map(Activity activity) {

        org.CDISC.DDF.model.Procedure ddfProcedure = new org.CDISC.DDF.model.Procedure(activity.getUid());
        ddfProcedure.setProcedureName(activity.getName());

        return ddfProcedure;

    }

    public org.CDISC.DDF.model.Activity map(StudyActivitySection studyActivitySection) {

        org.CDISC.DDF.model.Activity ddfActivity = new org.CDISC.DDF.model.Activity(studyActivitySection.getStudyActivityUid());
//        ddfActivity.setActivityName(studyActivitySection.getActivity().getStudyActivitySubgroup().get("name"));
        String osbActivitySubgroupUid = studyActivitySection.getStudyActivitySubgroup().get("activity_subgroup_uid");
        List<Map<String, String>> osbActivityGroupings = studyActivitySection.getActivity().getActivityGroupings();
        for(Map<String, String> osbActivityGrouping : osbActivityGroupings) {
            if(osbActivityGrouping.get("activity_subgroup_uid").equals(osbActivitySubgroupUid)) {
                ddfActivity.setActivityName(osbActivityGrouping.get("activity_subgroup_name"));
            }
        }

        Activity osbActivity = studyActivitySection.getActivity();
        if (osbActivity != null) {
            Procedure procedure = map(osbActivity);
            List<Procedure> ddfProcedures = new ArrayList<>();
            ddfProcedures.add(procedure);
            ddfActivity.setDefinedProcedures(ddfProcedures);
        }

        return ddfActivity;

    }

    private String getNextActivityUid(String currentActivityUid, List<StudyActivitySection> studyActivitySections) {
        Integer currentStudyActivitySectionOrder = null;
        String nextActivityUid = null;
        for (StudyActivitySection studyActivitySection : studyActivitySections) {
            if (studyActivitySection.getStudyActivityUid().equals(currentActivityUid)) {
                currentStudyActivitySectionOrder = studyActivitySection.getOrder();
            }
        }
        if (currentStudyActivitySectionOrder != null) {
            int nextStudyActivitySectionOrder = currentStudyActivitySectionOrder + 1;
            for (StudyActivitySection studyActivitySection : studyActivitySections) {
                if (studyActivitySection.getOrder() == nextStudyActivitySectionOrder) {
                    nextActivityUid = studyActivitySection.getStudyActivityUid();
                }
            }
        }
        return nextActivityUid;
    }

    private String getPreviousActivityUid(String currentActivityUid, List<StudyActivitySection> studyActivitySections) {
        Integer currentStudyActivitySectionOrder = null;
        String previousActivityUid = null;
        for (StudyActivitySection studyActivitySection : studyActivitySections) {
            if (studyActivitySection.getStudyActivityUid().equals(currentActivityUid)) {
                currentStudyActivitySectionOrder = studyActivitySection.getOrder();
            }
        }
        if (currentStudyActivitySectionOrder != null && currentStudyActivitySectionOrder > 1) {
            int previousStudyActivitySectionOrder = currentStudyActivitySectionOrder - 1;
            for (StudyActivitySection studyActivitySection : studyActivitySections) {
                if (studyActivitySection.getOrder() == previousStudyActivitySectionOrder) {
                    previousActivityUid = studyActivitySection.getStudyActivityUid();
                }
            }
        }
        return previousActivityUid;
    }

    // It uses a ScheduledInstance, which is an abstract class, in OSB we can only map DDF ActivityInstance for now and not Decision-based ones
    public ScheduledActivityInstance map(StudyActivitySchedule studyActivitySchedule) {
        ScheduledActivityInstance scheduledInstance = new ScheduledActivityInstance(studyActivitySchedule.getStudyActivityScheduleUid(), ScheduledInstanceType.ACTIVITY);
        // All the sequence numbers are set to zero in the examples, but setting them all to zero is not semantically correct
        // scheduledInstance.setScheduleSequenceNumber(0);
        scheduledInstance.setScheduledInstanceEncounterId(studyActivitySchedule.getStudyVisitUid());
        List<String> scheduledInstanceActivityUids = new ArrayList<>();
        scheduledInstanceActivityUids.add(studyActivitySchedule.getStudyActivityUid());
        scheduledInstance.setActivityIds(scheduledInstanceActivityUids);

        return scheduledInstance;
    }

}

