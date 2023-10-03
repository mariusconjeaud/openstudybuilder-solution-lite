package org.CSDISC.DDF.model;

import java.util.List;
import java.util.UUID;

/**
 * A clinical study involves research using human volunteers (also called participants) that is intended to
 * add to medical knowledge. There are two main types of clinical studies:
 * clinical trials (also called interventional studies) and observational studies.
 * [[http://ClinicalTrials.gov]](CDISC Glossary)
 * @author Chris Upkes
 */

public class Study {
    private final UUID studyId;
    // The sponsor-defined name of the clinical study.
    private String studyTitle;
    // A plan at a particular point in time for a study.
    private String studyVersion;
    // The nature of the investigation for which study information is being collected. (After clinicaltrials.gov)
    private Code studyType;
    // A step in the clinical research and development of a therapy from initial clinical trials to post-approval
    // studies. NOTE: Clinical trials are generally categorized into four (sometimes five) phases.
    // A therapeutic intervention may be evaluated in two or more phases simultaneously in different trials,
    // and some trials may overlap two different phases. [21 CFR section 312.21; After ICH Topic E8
    // NOTE FOR GUIDANCE ON GENERAL CONSIDERATIONS FOR CLINICAL TRIALS,  CPMP/ICH/291/95 March 1998]
    private Code studyPhase;
    private List<StudyIdentifier> studyIdentifiers;
    private List<StudyProtocolVersion> studyProtocolVersions;
    private List<StudyDesign> studyDesigns;
    // A therapeutic area classification based on the structure and operations of the business unit.
    private List<Code> businessTherapeuticAreas;


    public Study(UUID studyId) {
        this.studyId = studyId;
    }

    public UUID getStudyId() {
        return studyId;
    }

    public String getStudyTitle() {
        return studyTitle;
    }

    public void setStudyTitle(String studyTitle) {
        this.studyTitle = studyTitle;
    }

    public String getStudyVersion() {
        return studyVersion;
    }

    public void setStudyVersion(String studyVersion) {
        this.studyVersion = studyVersion;
    }

    public Code getStudyType() {
        return studyType;
    }

    public void setStudyType(Code studyType) {
        this.studyType = studyType;
    }

    public Code getStudyPhase() {
        return studyPhase;
    }

    public void setStudyPhase(Code studyPhase) {
        this.studyPhase = studyPhase;
    }

    public List<StudyIdentifier> getStudyIdentifiers() {
        return studyIdentifiers;
    }

    public void setStudyIdentifiers(List<StudyIdentifier> studyIdentifiers) {
        this.studyIdentifiers = studyIdentifiers;
    }

    public void addStudyIdentifier(StudyIdentifier studyIdentifier){
        this.studyIdentifiers.add(studyIdentifier);
    }

    public void removeStudyIdentifier(StudyIdentifier studyIdentifier){
        this.studyIdentifiers.remove(studyIdentifier);
    }

    public List<StudyProtocolVersion> getStudyProtocolVersions() {
        return studyProtocolVersions;
    }

    public void setStudyProtocolVersions(List<StudyProtocolVersion> studyProtocolVersions) {
        this.studyProtocolVersions = studyProtocolVersions;
    }

    public void addStudyProtocolVersion(StudyProtocolVersion studyProtocolVersion){
        this.studyProtocolVersions.add(studyProtocolVersion);
    }

    public void removeStudyProtocolVersion(StudyProtocolVersion studyProtocolVersion){
        this.studyProtocolVersions.remove(studyProtocolVersion);
    }

    public List<StudyDesign> getStudyDesigns() {
        return studyDesigns;
    }

    public void setStudyDesigns(List<StudyDesign> studyDesigns) {
        this.studyDesigns = studyDesigns;
    }

    public void addStudyDesign(StudyDesign studyDesign){
        this.studyDesigns.add(studyDesign);
    }

    public void removeStudyDesign(StudyDesign studyDesign){
        this.studyDesigns.remove(studyDesign);
    }

    public List<Code> getBusinessTherapeuticAreas() {
        return businessTherapeuticAreas;
    }

    public void setBusinessTherapeuticAreas(List<Code> businessTherapeuticAreas) {
        this.businessTherapeuticAreas = businessTherapeuticAreas;
    }
}
