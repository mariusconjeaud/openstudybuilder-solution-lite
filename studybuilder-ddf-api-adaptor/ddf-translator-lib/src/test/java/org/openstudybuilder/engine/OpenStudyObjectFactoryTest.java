package org.openstudybuilder.engine;


import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.openstudybuilder.model.*;

import java.util.List;


class OpenStudyObjectFactoryTest {

    private final OpenStudyObjectFactory staticObjectFactory = OpenStudyObjectFactory.withStaticBuilderAdaptor();
    private final String staticStudyUid = "001";
    private final String staticObjectiveUid = "StudyObjective_000001";

    @Test
    void getStudies() throws Exception {

        List<OpenStudy> openStudies = staticObjectFactory.getStudies();
        Assertions.assertNotNull(openStudies);
        Assertions.assertEquals("CDISC DEV-0",openStudies.get(0).getStudyId());
        CurrentMetadata currentMetadata = openStudies.get(0).getCurrentMetadata();
        IdentificationMetadata identificationMetadata = currentMetadata.getIdentificationMetadata();
        VersionMetadata versionMetadata = currentMetadata.getVersionMetadata();
        Assertions.assertEquals("CDISC DEV", identificationMetadata.getProjectNumber());
        Assertions.assertEquals("2022-10-20T06:13:45.627992", versionMetadata.getVersionTimestamp());

    }


    @Test
    void getVisits() throws Exception {

        List<Visit> visits = staticObjectFactory.getVisits(staticStudyUid);
        Assertions.assertNotNull(visits);
        Assertions.assertEquals("Visit 1", visits.get(0).getVisitSubname());


    }

    @Test
    @Disabled("Missing test data") // TODO: missing population test data for Study_000002
    void getPopulation() throws Exception {

        Population population = staticObjectFactory.getPopulation(staticStudyUid);
        Assertions.assertNotNull(population);
        //Assertions.assertEquals("DictionaryTerm_000013",
       //         population.getTherapeuticAreasCodes().get(0).getTermUid());

    }

    @Test
    @Disabled("Missing data") // TODO: missing objective test data for Study_000002
    void getObjective() throws Exception {
        Objective objective = staticObjectFactory.getObjective(staticObjectiveUid);
        Assertions.assertNotNull(objective);
        Assertions.assertEquals("2022-03-31T15:27:55.819993",objective.getStartDate());

    }

    @Test
    void getStudyObjectiveSections() throws Exception {
       List<StudySelectionObjective> studySelectionObjectives = staticObjectFactory.getStudyObjectiveSections(staticStudyUid);
        Assertions.assertNotNull(studySelectionObjectives);
        Assertions.assertEquals("StudyObjective_000001", studySelectionObjectives.get(0).getStudyObjectiveUid());
    }

    @Test
    @Disabled("Missing test data") // TODO: missing intervention test data
    void getIntervention() throws Exception {

        Intervention intervention = staticObjectFactory.getIntervention(staticStudyUid);
        Assertions.assertNotNull(intervention);
        Assertions.assertEquals("C1909_DRUG",intervention.getInterventionTypeCode().getTermUid());


    }


    @Test
    @Disabled("Missing test data") // TODO: missing high level design test data
    void getHLDesign() throws Exception {

        StudyDesign studyDesign = staticObjectFactory.getHLDesign(staticStudyUid);
        Assertions.assertNotNull(studyDesign);
        Assertions.assertEquals("The study stop rule", studyDesign.getStudyStopRules());

    }

    @Test
    void getEpochs() throws Exception {

        List<Epoch> epochs = staticObjectFactory.getEpochs(staticStudyUid);
        Assertions.assertNotNull(epochs);
        Assertions.assertEquals("C48262_SCREENING",epochs.get(0).getEpoch());
        Assertions.assertEquals("Initial Version", epochs.get(0).getChangeDescription());
        Assertions.assertEquals("C48262_SCREENING", epochs.get(0).getEpochSubtype());
        Assertions.assertEquals("CTTerm_000003", epochs.get(0).getEpochType());
        Assertions.assertEquals(1, epochs.get(0).getOrder());
        Assertions.assertEquals("edit", epochs.get(0).getPossibleActions().get(0));
        Assertions.assertEquals(-14, epochs.get(0).getStartDay());
        Assertions.assertEquals(1, epochs.get(0).getStudyVisitCount());
    }

    @Test
    @Disabled("Missing test data") // TODO: missing endpoint test data
    void getEndpoint() throws Exception {

        Endpoint endpoint = staticObjectFactory.getEndpoint(staticStudyUid);
        Assertions.assertNotNull(endpoint);
        Assertions.assertEquals("Endpoint_000004",endpoint.getUid());

    }

    @Test
    void getStudyEndpointSections() throws Exception {
        List<StudySelectionEndpoint> studySelectionEndpoints = staticObjectFactory.getStudyEndpointSections(staticStudyUid);
        Assertions.assertNotNull(studySelectionEndpoints);
        Assertions.assertEquals("StudyEndpoint_000005", studySelectionEndpoints.get(0).getStudyEndpointUid());

    }

    @Test
    void getElements() throws Exception {
        List<Element> elements = staticObjectFactory.getElements(staticStudyUid);
        Assertions.assertNotNull(elements);
        Assertions.assertEquals("CTTerm_000138", elements.get(0).getCode());
        Assertions.assertEquals("SDTM CT", elements.get(0).getElementSubtype().getCatalogueName());
        Assertions.assertEquals("inactivate", elements.get(0).getElementSubtype().getPossibleActions().get(0));
        Assertions.assertEquals("CTCodelist_000023", elements.get(0).getElementSubtype().getCodelistUid());
        Assertions.assertEquals("StudyElement_000007", elements.get(0).getElementUid());
        Assertions.assertEquals("Study_000002", elements.get(0).getStudyUid());
        Assertions.assertEquals(0, elements.get(0).getStudyCompoundDosingCount());
    }

    @Test
    void getArms() throws Exception {
        List<Arm> arms = staticObjectFactory.getArms(staticStudyUid);
        Assertions.assertNotNull(arms);
        Assertions.assertEquals("Human Insulin",arms.get(0).getName());
        Assertions.assertFalse(arms.get(0).isAcceptedVersion());
        Assertions.assertEquals("#9FA8DAFF", arms.get(0).getArmColour());
        Assertions.assertEquals("SDTM CT", arms.get(0).getArmType().getCatalogueName());
        Assertions.assertEquals("inactivate", arms.get(0).getArmType().getPossibleActions().get(0));
        Assertions.assertEquals(50, arms.get(0).getNumberOfSubjects());
        Assertions.assertEquals(1, arms.get(0).getOrder());
        Assertions.assertEquals("A", arms.get(0).getRandomizationGroup());
    }


    @Test
    void getStudyCriterias() throws Exception {
        List<StudySelectionCriteria> studySelectionCriteria = staticObjectFactory.getCriterias(staticStudyUid);
        Assertions.assertEquals(1,1);
    }

    @Test
    void getDesignMatrixCells() throws Exception {

        List<StudyDesignCell> studyDesignCells = staticObjectFactory.getDesignMatrixCells(staticStudyUid);
        Assertions.assertNotNull(studyDesignCells);
        Assertions.assertEquals("StudyDesignCell_000007", studyDesignCells.get(0).getDesignCellUid());
    }

    @Test
    void getCriteriaType() throws Exception {

        CriteriaType criteriaType = staticObjectFactory.getCriteriaType(staticStudyUid);
        Assertions.assertNotNull(criteriaType);
        Assertions.assertEquals("C25370_EXCLUSION",criteriaType.getTermUid());
    }

    @Test
    void getStudy() throws Exception {

        OpenStudy openStudy = staticObjectFactory.getStudy(staticStudyUid);
        Assertions.assertNotNull(openStudy);
        Assertions.assertEquals("C48660_Not Applicable",
                openStudy.getCurrentMetadata().getHighLevelStudyDesign()
                        .getConfirmedResponseMinimumDurationNullValueCode().getTermUid());
        Assertions.assertFalse(openStudy.getCurrentMetadata().getHighLevelStudyDesign().isAdaptiveDesign());
        Assertions.assertFalse(openStudy.getCurrentMetadata().getHighLevelStudyDesign().isExtensionTrial());
        Assertions.assertEquals("Interventional",
                openStudy.getCurrentMetadata().getHighLevelStudyDesign().getStudyTypeCode().getName());
        Assertions.assertEquals("C15602_PHASE III TRIAL", openStudy.getCurrentMetadata().
                getHighLevelStudyDesign().getTrialPhaseCode().getTermUid());
        Assertions.assertEquals("C49666_EFFICACY", openStudy.getCurrentMetadata().getHighLevelStudyDesign()
                .getTrialTypeCodes().get(0).getTermUid());
        Assertions.assertEquals("CDISC Development programme", openStudy.getCurrentMetadata()
                .getIdentificationMetadata().getClinicalProgrammeName());
        Assertions.assertEquals("NCT12345678", openStudy.getCurrentMetadata().getIdentificationMetadata()
                .getRegistryIdentifiers().getCtGovId());
        Assertions.assertEquals("CDISC DEV-0", openStudy.getCurrentMetadata().getIdentificationMetadata()
                .getStudyId());
        Assertions.assertEquals("A trial comparing cardiovascular safety of human insulin versus metformin in " +
                "subjects with type 2 diabetes at high risk of cardiovascular events", openStudy.getCurrentMetadata()
                .getStudyDescription().get("study_short_title"));
//        Assertions.assertFalse(openStudy.getCurrentMetadata().getStudyIntervention().isAddOnToExistingTreatments());
//        Assertions.assertEquals("C49649_ACTIVE", openStudy.getCurrentMetadata().getStudyIntervention()
//                .getControlTypeCode().getTermUid());
//        Assertions.assertEquals("C82639_PARALLEL", openStudy.getCurrentMetadata().getStudyIntervention()
//                .getInterventionModelCode().getTermUid());
//        Assertions.assertEquals("C1909_DRUG", openStudy.getCurrentMetadata().getStudyIntervention()
//                .getInterventionTypeCode().getTermUid());
//        Assertions.assertTrue(openStudy.getCurrentMetadata().getStudyIntervention().isTrialRandomised());
//        Assertions.assertEquals("C29844_WEEKS", openStudy.getCurrentMetadata().getStudyIntervention()
//                .getPlannedStudyLength().getDurationUnitCode().getTermUid());
//        Assertions.assertEquals(26, openStudy.getCurrentMetadata().getStudyIntervention()
//                .getPlannedStudyLength().getDurationValue());
//        Assertions.assertEquals("C15228_DOUBLE BLIND", openStudy.getCurrentMetadata().getStudyIntervention()
//                .getTrialBlindingSchemaCode().getTermUid());
//        Assertions.assertEquals("C49656_TREATMENT", openStudy.getCurrentMetadata().getStudyIntervention()
//                .getTrialIntentTypesCodes().get(0).getTermUid());
        Assertions.assertEquals("DictionaryTerm_000007", openStudy.getCurrentMetadata().getStudyPopulation()
                .getDiagnosisGroupCodes().get(0).getTermUid());
        Assertions.assertEquals("DictionaryTerm_000007", openStudy.getCurrentMetadata().getStudyPopulation()
                .getDiseaseConditionOrIndicationCodes().get(0).getTermUid());
        Assertions.assertFalse(openStudy.getCurrentMetadata().getStudyPopulation().isHealthySubjectIndicator());
        Assertions.assertFalse(openStudy.getCurrentMetadata().getStudyPopulation().isPediatricInvestigationPlanIndicator());
        Assertions.assertFalse(openStudy.getCurrentMetadata().getStudyPopulation().isPediatricStudyIndicator());
        Assertions.assertFalse(openStudy.getCurrentMetadata().getStudyPopulation().isPediatricPostmarketStudyIndicator());
//        Assertions.assertEquals("CTTerm_000097", openStudy.getCurrentMetadata().getStudyPopulation()
//                .getPlannedMaximumAgeOfSubjectsNullValueCode().getTermUid());
        Assertions.assertNotNull(openStudy.getCurrentMetadata().getStudyPopulation().getPlannedMaximumAgeOfSubjects());
//        Assertions.assertEquals("C29848_YEARS", openStudy.getCurrentMetadata().getStudyPopulation()
//                .getPlannedMinimumAgeOfSubjects().getDurationUnitCode().getTermUid()); // TODO only name and uid in durationunitcode
        Assertions.assertEquals(18, openStudy.getCurrentMetadata().getStudyPopulation()
                .getPlannedMinimumAgeOfSubjects().getDurationValue());
        Assertions.assertFalse(openStudy.getCurrentMetadata().getStudyPopulation().isRareDiseaseIndicator());
        Assertions.assertEquals("C48660_Not Applicable", openStudy.getCurrentMetadata().getStudyPopulation()
                .getRelapseCriteriaNullValueCode().getTermUid());
        Assertions.assertEquals("C49636_BOTH", openStudy.getCurrentMetadata().getStudyPopulation()
                .getSexOfParticipantsCode().getTermUid());
        Assertions.assertEquals("C48660_Not Applicable", openStudy.getCurrentMetadata().getStudyPopulation()
                .getStableDiseaseMinimumDurationNullValueCode().getTermUid());
        Assertions.assertEquals("DictionaryTerm_000013", openStudy.getCurrentMetadata().getStudyPopulation()
                .getTherapeuticAreaCodes().get(0).getTermUid());
        Assertions.assertEquals("Study_000002", openStudy.getUid());
    }

    @Test
    void getStudyActivitySections() throws Exception {
        List<StudyActivitySection> studyActivitySections = staticObjectFactory.getActivitySections("Study_000036");
        Assertions.assertNotNull(studyActivitySections);
        Assertions.assertFalse(studyActivitySections.get(0).isAcceptedVersion());
        Assertions.assertEquals(1, studyActivitySections.get(0).getOrder());
        Assertions.assertTrue(studyActivitySections.get(0).isShowActivityGroupInProtocolFlowchart());
        Assertions.assertEquals("Study_000002", studyActivitySections.get(0).getStudyUid());
        Assertions.assertEquals("StudyActivity_000007",studyActivitySections.get(0).getStudyActivityUid());
        Assertions.assertEquals("ActivitySubGroup_194", studyActivitySections.get(0)
                .getActivity().getActivityGroupings().get(0).get("activity_subgroup_uid"));
        Assertions.assertEquals("inactivate", studyActivitySections.get(0).getActivity()
                .getPossibleActions().get(0));
        Assertions.assertEquals("CTCodelist_000020", studyActivitySections.get(0).getFlowchartGroup()
                .getCodelistUid());
        Assertions.assertEquals("inactivate", studyActivitySections.get(0).getFlowchartGroup()
                .getPossibleActions().get(0));
        Assertions.assertEquals("CTTerm_000069", studyActivitySections.get(0).getFlowchartGroup().getTermUid());
    }

    @Test
    void getStudyActivitySchedules() throws Exception {
        List<StudyActivitySchedule> activitySchedules = staticObjectFactory.getActivitySchedules(null);
        Assertions.assertNotEquals(0, activitySchedules.size());
        Assertions.assertEquals("Study_000002", activitySchedules.get(2).getStudyUid());
        Assertions.assertEquals("StudyActivitySchedule_000141", activitySchedules.get(2).getStudyActivityScheduleUid());
        Assertions.assertEquals("StudyVisit_000014", activitySchedules.get(2).getStudyVisitUid());
        Assertions.assertEquals("2022-10-20T12:14:39.730138", activitySchedules.get(2).getStartDate());
    }
}
