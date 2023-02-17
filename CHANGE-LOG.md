# OpenStudyBuilder Commits changelog

## V 0.3

### Fixes and Enhancements
- Fixes on CRF library
  - Issues on the Reference Extension on the Front-end fixed.
- Improvements on Study structure and Study Interventions.
- Fix applied on visual indication of required/mandatory (*) fields in UI so unnecessary error messages can be avoided.

### New Features
- Further additions to CRF library module.
- API refactoring done, majorly use of snake case and aligning SB API with Zalando Rest API guidelines.
- Implemented API to support Activity Placeholders and User Requested Activity Concept Requests.
- Audit trail history studies.
- Implemented Disease Milestones under Study Structure.
- OS packages has been added for generating PDF. OS software licenses are included in git repositories, including the third party licenses. 


## V 0.2 (12-DEC-2022)

### Fixes and Enhancements
- Locked version of documentation portal. 
- neo4j database version updated in dockerfile. 
- Updated README to correct default password error.
- Added README section about platform architectures and docker.
- Added separate README to allow for starting up the OpenStudyBuilder only using Docker for neo4j and the respective technologies for the rest of the components, such as python and yarn. This can be found in DeveloperSetupGuide.md.
- General source code quality improvements, below mentioned:
  - Aligned SB API with Zalando REST API Guidelines, e.g. naming of endpoints, query and path parameters, proper usage of HTTP methods etc.
  - A number of API refactorings to be more consistent in design and use of snake case including: Aligned StudyBuilder API with Zalando REST API Guidelines, e.g. naming of endpoints, query and path parameters, proper usage of HTTP methods etc.
  - Fixed major warnings reported by Pylint/SonarLint static code analyzers.
  - Removed unused endpoints and code.
- Filtering corrected for Activities in a number of places.
-  A number of fixes and improvements to CRF module:
  - Edit references from CRF tree.
  - Improvements in UI for CRF Instructions.
  - Support for exporting attributes as ODM.XML alias.
  - A number of corrections and improvements to the CRF Library pages and ODM.XML import and export capabilities
  - Improvements for ODM-XML Import.
  - API: Added a new field 'dispaly_text' on the relation between OdmItemRoot and CTTermRoot.
  - Data Model: Added 'display_text' between ODM Item and CT Term.
  - Mapper for ODM XML export added.
  - Added Import library for ClinSpark.
- A number of bug fixes including: 
   - All Study Field Selections related to CT must have relationships in the database to selected CT Term.
   - StudyBuilder is hanging when duplicating a StudyVisit is fixed.
   - All timings are available for syntax templates
- Improvements to sample data, data import and readme descriptions
- Improvements to SDTM Study Design dataset listings.
- Improvements on ease-of-use, clean and simplify sample data
- Page level Version History on Study Activities, Study Endpoints, Study Intervention, Registry identifier pages.
- Fix applied for Page level version history on Study Properties and on row level studies/criterias.

### New Features
- Flowchart fitting for studies with many visits.
- Improvements to Word add-in
- Support creation of special visits without a specific time point reference
- Support multiple ODM.XML styles and extensions.
- Initial implementation to support generation of Clinical Trial Registration information in CDISC CTR.XML format. Note this is in part one only available via the API, a display via the View Spcifications menu item will be added later. Study Objectives & Endpoints HTML table built in the UI.


## V 0.1 (24-OCT-2022)

Initial commit to Public Gitlab.