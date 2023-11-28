//package org.openstudybuilder.sdr.acct;
//
//import com.fasterxml.jackson.annotation.JsonRootName;
//import lombok.Getter;
//import org.CDISC.DDF.model.*;
//import org.CDISC.DDF.model.Code;
//import org.CDISC.DDF.model.Endpoint;
//import org.CDISC.DDF.model.Objective;
//import org.openstudybuilder.engine.OpenStudyObjectFactory;
//import org.openstudybuilder.engine.StudyObjectMapper;
//import org.openstudybuilder.model.*;
//import org.openstudybuilder.model.Population;
//
//import java.text.SimpleDateFormat;
//import java.util.ArrayList;
//import java.util.Date;
//import java.util.List;
//import java.util.UUID;
//
///**
// * The purpose of this class is to wrap the definition of a Clincal Study per Accenture's SDR Schema
// */
//public class AcctSdrStudy {
//
//    private OpenStudy openStudy;
//    private OpenStudyObjectFactory openStudyObjectFactory;
//    private Study studyDef;
//
//    // TODO - Validate usage and value of these constants
//    private static final String CODE_SYSTEM_VERSION = "1";
//    private static final String CODE_SYSTEM = "http:www.cdisc.org";
//
//    @Getter
//    @JsonRootName(value = "clinicalStudy")
//    class Study {
//        private UUID uuid;
//        private String studyTitle;
//        private String studyVersion;
//        private org.CDISC.DDF.model.Code studyType;
//        private org.CDISC.DDF.model.Code studyPhase;
//        private List<org.CDISC.DDF.model.StudyIdentifier> studyIdentifiers;
//        private List<AcctStudyProtocolVersion> studyProtocolVersions;
//        private List<org.CDISC.DDF.model.StudyDesign> studyDesigns;
//    }
//
//
//
//    public AcctSdrStudy(OpenStudy openStudy, OpenStudyObjectFactory openStudyObjectFactory,
//                        UUID uuid) throws Exception {
//        this.openStudy = openStudy;
//        this.openStudyObjectFactory = openStudyObjectFactory;
//        this.studyDef = new Study();
//        studyDef.uuid = null;
//        buildStudy();
//    }
//
//    public void buildStudy() throws Exception {
//        StudyObjectMapper studyObjectMapper = new StudyObjectMapper();
//
//        String openStudyUid = openStudy.getUid();
//        studyDef.studyVersion = "1";
//
//        org.CDISC.DDF.model.StudyIdentifier studyIdentifier = new StudyIdentifier(UUID.randomUUID());
//        CurrentMetadata studyMd = openStudy.getCurrentMetadata();
//
//        studyDef.studyType = new org.CDISC.DDF.model.Code(UUID.randomUUID());
//        // Study Phase
//        studyDef.studyPhase = new org.CDISC.DDF.model.Code(UUID.randomUUID());
//
//        if (studyMd.getHighLevelStudyDesign() != null) {
//            studyDef.studyType.setCode(studyMd.getHighLevelStudyDesign().getStudyTypeCode().getName());
//            studyDef.studyType.setDecode(studyMd.getHighLevelStudyDesign().getStudyTypeCode().getName());
//            studyDef.studyType.setCodeSystem(studyMd.getHighLevelStudyDesign().getStudyTypeCode().getTermUid());
//            studyDef.studyType.setCodeSystemVersion(CODE_SYSTEM_VERSION);
//
//            studyDef.studyPhase.setCode(studyMd.getHighLevelStudyDesign().getTrialPhaseCode().getName());
//            studyDef.studyPhase.setDecode(studyMd.getHighLevelStudyDesign().getTrialPhaseCode().getName());
//            studyDef.studyPhase.setCodeSystem(studyMd.getHighLevelStudyDesign().getTrialPhaseCode().getTermUid());
//            studyDef.studyPhase.setCodeSystemVersion(CODE_SYSTEM_VERSION);
//        }
//
//        studyDef.studyTitle = studyMd.getStudyDescription().get("studyTitle");
//        // TODO - Organization is partly being stubbed. Non-stubbed fields should be validated too
//        RegistryIdentifier registryIdentifier = studyMd.getIdentificationMetadata().getRegistryIdentifiers();
//        studyIdentifier.setStudyIdentifier(registryIdentifier.getEudractId());
//        studyIdentifier.setStudyIdentifierScope(generateOrganization(registryIdentifier));
//        studyDef.studyIdentifiers = List.of(studyIdentifier);
//
//        // Protocol Versions
//        studyDef.studyProtocolVersions = generateProtocolVersion();
//
//        // First we're going to get a list of all visits for the study, we'll need this as we build study cells
//        // With the lack of an api to get visits under a particular epoch, we search for this list.
//        List<Visit> openStudyVisits = openStudyObjectFactory.getVisits(openStudyUid);
//
//        // Study Designs (Submitting just 1 as Open Study Builder has only 1 Study Design per study
//        AcctStudyDesign currentStudyDesign = new AcctStudyDesign(studyMd);
//        // Study Design Cells
//        List<StudyCell> currentStudyCells = new ArrayList<>();
//        List<StudyDesignCell> openStudyDesignCells = openStudyObjectFactory.getDesignMatrixCells(openStudyUid);
//        for (StudyDesignCell openStudyDesignCell: openStudyDesignCells) {
//            org.CDISC.DDF.model.StudyCell studyCell = new StudyCell(null);
//            // Cell Arm Info
//            // TODO - This armID is being stubbed due to api always returning null. To be fixed
//            String currentArmId = openStudyDesignCell.getStudyArmUid() == null ? "StudyArm_000001" :
//                    openStudyDesignCell.getStudyArmUid();
//            Arm openStudyCellArm = openStudyObjectFactory.getSingleArm(openStudyUid, currentArmId);
//            AcctStudyArm studyArmExt = new AcctStudyArm(studyObjectMapper.map(openStudyCellArm));
//            studyArmExt.setStudyArmDataOriginDesc("Captured subject data");
//            generateArmDataOriginType(studyArmExt.getExtStudyArmDataOriginType());
//            generateArmType(studyArmExt.getExtArmType());
//            studyCell.setStudyArm(studyArmExt);
//            // Epoch Info
//            String currentEpochId = openStudyDesignCell.getStudyEpochUid();
//            Epoch openStudyCellEpoch = openStudyObjectFactory.getSingleEpoch(openStudyUid, currentEpochId);
//            AcctStudyEpoch studyEpochExt = new AcctStudyEpoch(studyObjectMapper.map(openStudyCellEpoch));
//            studyEpochExt.setExtStudyEpochType(List.of(generateEpochType()));
//            // Epoch Encounters
//            List<Encounter> encounters = pullEncountersFromAllVisits(openStudyVisits, currentEpochId);
//            studyEpochExt.setEncounters(encounters);
//            studyCell.setStudyEpoch(studyEpochExt);
//
//            // Study Elements (Ok to process as a single-element list)
//            String currentElementId = openStudyDesignCell.getStudyElementUid();
//            Element openStudyElement = openStudyObjectFactory.getSingleElement(openStudyUid, currentElementId);
//            studyCell.setStudyElements(List.of(studyObjectMapper.map(openStudyElement)));
//            currentStudyCells.add(studyCell);
//        }
//        currentStudyDesign.setStudyCells(currentStudyCells);
//
//        // Investigational Intervention
//        Intervention openStudyIntervention = studyMd.getStudyIntervention();
//        InvestigationalIntervention intervention = studyObjectMapper.map(openStudyIntervention);
//        for (Code interventionCode: intervention.getCodes()) {
//            interventionCode.setCodeSystemVersion(CODE_SYSTEM_VERSION);
//            interventionCode.setCodeSystem(CODE_SYSTEM);
//            interventionCode.setDecode(interventionCode.getCode());
//        }
//        currentStudyDesign.setStudyInvestigationalInterventions(List.of(intervention));
//
//        // TODO - Workflow items
//
//        // Study Design Population - 1 item list
//        Population openStudyPopulation = openStudy.getCurrentMetadata().getStudyPopulation();
//        org.CDISC.DDF.model.Population population = studyObjectMapper.map(openStudyPopulation);
//        currentStudyDesign.setStudyPopulations(List.of(population));
//
//        // Objectives & Endpoints
//        List<StudySelectionEndpoint> openStudyEndpoints =
//                openStudyObjectFactory.getStudyEndpointSections(openStudyUid);
//        List<Objective> currentStudyObjectives = new ArrayList<>();
//        for (StudySelectionEndpoint objective: openStudyEndpoints) {
//            if (objective != null) {
//                Objective cdiscObjective = studyObjectMapper.map(objective);
//                if (cdiscObjective != null) {
//                    AcctStudyObjective currentObjective = new AcctStudyObjective(cdiscObjective);
//                    generateObjectiveLevel(currentObjective.getExtObjectiveLevel());
//                    currentStudyObjectives.add(currentObjective);
//                    // Endpoints
//                    List<Endpoint> currentEndpoints = new ArrayList<>(currentObjective.getObjectiveEndpoints());
//                    currentObjective.getObjectiveEndpoints().clear();
//                    for (Endpoint currentEndpoint : currentEndpoints) {
//                        AcctStudyObjectiveEndpoint newEndpoint = new AcctStudyObjectiveEndpoint(currentEndpoint);
//                        generateEndpointLevel(newEndpoint);
//                        currentObjective.getObjectiveEndpoints().add(newEndpoint);
//                    }
//                }
//            }
//        }
//        currentStudyDesign.setStudyObjectives(currentStudyObjectives);
//
//        studyDef.studyDesigns = List.of(currentStudyDesign);
//    }
//
//    public Study getStudyDef() {
//        return studyDef;
//    }
//
//    // ---- STUBBING SECTION -------
//    // Below are some methods that populate some values that are not being directly mapped due to missing info in Open Study Builder
//
//    private List<AcctStudyProtocolVersion> generateProtocolVersion() {
//        AcctStudyProtocolVersion currentProtocolVersion = new AcctStudyProtocolVersion(UUID.randomUUID());
//        currentProtocolVersion.setBriefTitle("Short");
//        currentProtocolVersion.setOfficialTitle("Very Official");
//        currentProtocolVersion.setProtocolAmendment("Ammendment");
//        Code protocolStatus = new Code(UUID.randomUUID());
//        protocolStatus.setCode("C1113x");
//        protocolStatus.setDecode("FINAL 1");
//        protocolStatus.setCodeSystem(CODE_SYSTEM);
//        protocolStatus.setCodeSystemVersion(CODE_SYSTEM_VERSION);
//        currentProtocolVersion.setExtProtocolStatus(List.of(protocolStatus));
//        currentProtocolVersion.setProtocolVersion("1");
//        currentProtocolVersion.setPublicTitle("Public Voice");
//        currentProtocolVersion.setScientificTitle("Incomprehensible");
//        SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd");
//        currentProtocolVersion.setExtProtocolEffectiveDate(formatter.format(new Date()));
//        return List.of(currentProtocolVersion);
//    }
//
//    private void generateEndpointLevel(AcctStudyObjectiveEndpoint endpoint) {
//        endpoint.setEndpointPurposeDesc("level description");
//        List<Code> endpointLevels = endpoint.getExtEndpointLevel();
//        for (Code endpointLevel: endpointLevels) {
//            endpointLevel.setCode("C9844x");
//            endpointLevel.setDecode("PURPOSE");
//            endpointLevel.setCodeSystem(CODE_SYSTEM);
//            endpointLevel.setCodeSystemVersion(CODE_SYSTEM_VERSION);
//        }
//    }
//
//    private void generateObjectiveLevel(List<Code> objectiveLevels) {
//        for (Code objectiveLevel: objectiveLevels) {
//            objectiveLevel.setCode("C6574y");
//            objectiveLevel.setDecode("OBJ LEVEL");
//            objectiveLevel.setCodeSystem(CODE_SYSTEM);
//            objectiveLevel.setCodeSystemVersion(CODE_SYSTEM_VERSION);
//        }
//    }
//
//    private void generateArmDataOriginType(List<Code> armDataOriginTypes) {
//        for (Code armDataOriginType: armDataOriginTypes) {
//            armDataOriginType.setCode("C6574y");
//            armDataOriginType.setDecode("SUBJECT DATA");
//            armDataOriginType.setCodeSystem(CODE_SYSTEM);
//            armDataOriginType.setCodeSystemVersion(CODE_SYSTEM_VERSION);
//        }
//    }
//
//    private void generateArmType(List<Code> armTypes) {
//        for (Code armType: armTypes) {
//            armType.setDecode("Placebo Control Arm");
//            armType.setCodeSystem(CODE_SYSTEM);
//            armType.setCodeSystemVersion(CODE_SYSTEM_VERSION);
//        }
//    }
//
//    private Code generateEpochType() {
//        Code epochType = new Code(UUID.randomUUID());
//        epochType.setCodeSystemVersion(CODE_SYSTEM_VERSION);
//        epochType.setCode("C98779");
//        epochType.setDecode("Run-in Period");
//        epochType.setCodeSystem(CODE_SYSTEM);
//        return epochType;
//    }
//
//    private AcctStudyIdentOrganisation generateOrganization(RegistryIdentifier openStudyRegistryIdentifier) {
//        AcctStudyIdentOrganisation organization = new AcctStudyIdentOrganisation(null);
//
//        organization.setOrganisationIdentifier(openStudyRegistryIdentifier.getCtGovId());
//        organization.setOrganisationIdentifierScheme("FDA");
//        organization.setOrganisationName("ClinicalTrials.gov");
//        Code orgTypeCode = new Code(UUID.randomUUID());
//        orgTypeCode.setCode("C2365x");
//        orgTypeCode.setCodeSystem(CODE_SYSTEM);
//        orgTypeCode.setDecode("Clinical Study Sponsor");
//        orgTypeCode.setCodeSystemVersion(CODE_SYSTEM_VERSION);
//        organization.setOrganisationType(orgTypeCode);
//
//        return organization;
//    }
//
//    /**
//     * This method not only generates stubs for Encounter Environmental Setting, Type and Contact Mode,
//     * but also obtains Encounters from a list of all the visits in the Open Study. Each visit is evaluated to match
//     * the Epoch UID from the Open Study Cell Item. If a match is found, then we perform the mapping.
//     * @param openStudyVisits - A list of all the visits in the current study obtained from Open Study Builder
//     * @param epochId - The Epoch UID we're looking for that is associated with one visit in the list
//     * @return CSDISC-compatible list of Encounters
//     */
//    private List<Encounter> pullEncountersFromAllVisits(List<Visit> openStudyVisits, String epochId) {
//        List<Encounter> returnVal = new ArrayList<>();
//        StudyObjectMapper studyObjectMapper = new StudyObjectMapper();
//
//        for (Visit visit: openStudyVisits) {
//            if (visit.getStudyEpochUid().equals(epochId)) {
//                Encounter encounter = studyObjectMapper.map(visit);
//                encounter.getEncounterEnvironmentalSetting().setCode("C51282");
//                encounter.getEncounterEnvironmentalSetting().setDecode("Clinic");
//                encounter.getEncounterEnvironmentalSetting().setCodeSystemVersion(CODE_SYSTEM_VERSION);
//                encounter.getEncounterEnvironmentalSetting().setCodeSystem(CODE_SYSTEM);
//                encounter.getEncounterType().setCode("C7652x");
//                encounter.getEncounterType().setDecode("SITE VISIT");
//                encounter.getEncounterType().setCodeSystemVersion(CODE_SYSTEM_VERSION);
//                encounter.getEncounterType().setCodeSystem(CODE_SYSTEM);
//                encounter.getEncounterContactMode().setCode("C1755745");
//                encounter.getEncounterContactMode().setDecode("In Person");
//                encounter.getEncounterContactMode().setCodeSystemVersion(CODE_SYSTEM_VERSION);
//                encounter.getEncounterContactMode().setCodeSystem(CODE_SYSTEM);
//                returnVal.add(new AcctStudyEncounter(encounter));
//            }
//        }
//        return returnVal;
//    }
//}
