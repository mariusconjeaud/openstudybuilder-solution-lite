
# Version 0.2

## Fixes and Enhancements

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


## New Features

- Sourcecode Public Gitlab file updates as below:
   - Added DeveloperSetupGuide markdown file.
   - Added Releasenotes markdown file.
   - Added CHANGELOG markdown file.
- Flowchart fitting for studies with many visits.
- Support creation of special visits without a specific time point reference
- Support multiple ODM.XML styles and extensions.
- Initial implementation to support generation of Clinical Trial Registration information in CDISC CTR.XML format. Note this is in part one only available via the API, a display via the View Spcifications menu item will be added later. Study Objectives & Endpoints HTML table built in the UI.


# Version 0.1

Initial commit to Public Gitlab.