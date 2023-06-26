# OpenStudyBuilder Commits changelog

##  V 0.5

### Fixes and Enhancements
- Improvements to audit trail tracking changes in outbound relationships to related nodes as changes.
- Documentation regarding packaging of python components (e.g. API) is outdated in several places. Corrected API issues reported by schemathesis. Auto-increment of version number enabled in the auto-generated openapi.json API specification.
Upgrade to Python version 3.11.
- Adding missing 'Number of Studies' column for Timeframe instance.
- Some column displays for activity instances has been removed, they will for the moment only be part of detailed displays.
- Improvements to license and SBOM display on About page.
- Various UI, Audit trail and Stability improvements.
- Syntax template functionalities in Library is refactored with improved data model and consistency.

### New Features
- System documentation and Online help on Locking and Versioning of Studies improved.
- Initial implementation for display of Data Exchange Standards for SDTM in Library menu (Part of the foundational data model representation linked to the Activity Concepts model similar to the CDISC Bio-medical Concepts mode).
- Import of core SDTM and SDTMIG data models from CDISC Library is supported going forward.
- New pre-instantiations of syntax templates replacing previous default values.
- Create and Maintain ClinSpark CRF Library using StudyBuilder
- Two sample study Metadata (MD) listings implemented to support ADaM dataset generation.

## V 0.4

### Fixes and Enhancements
- UI/UX improvements.
- Activity Placeholder updates and its corresponded API, UI, Logical and Physical data model updates.
- Sharing OpenStudyBuilder Solution code to Public gitlab (NN SBOM task file updates).
- Activity concepts model improvements, logical & physical data model updates.
- Enabling Study Metadata Listings, properties for generation of SDTM and relevant API endpoint updates.
- Improvements of CRF Management with vendor extension, CRF display in HTML or PDF format and OID & UID refactoring.
- Database Consistency Checks for Versioning Relationships on Library Nodes.
- Additional capabilities on Activity Instance and Item Class Model.
- Improved support for ODM.XML vendor extensions.
- Legacy migration of Activity Instance concepts have been adjusted to match the updated data model. Note the content is not fully curated yet, improvements will therefore come in next release.
- Global Audit Trail report shared as a NeoDash report (intially NeoDash report runs separately).

### New Features
- Locking and Versioning of Study Metadata (incl. API and UI Designs, Logical and Physical Data model updates).
- Import of core SDTM and SDTMIG data models from CDISC Library is supported now (Part of the foundational data model representation linked to the Activity Concepts model similar to the CDISC Bio-medical Concepts mode).
- The Data Model and Data Model IG data structures is extended with a number of attributes to support sponsor needs. Note the UI is not yet made for these part - sample data is loaded into the system database for utilisation by NeoDash reports.
- Initial version of DDF API adaptor enabling Digital Data Flow (DDF) compatible access to StudyBuilder as a DDF Study Definition Repository (SDR) solution.
- The data import repository will also include a DDF sample study. 
- The listing of activity concepts include links to overview pages of bot an Activity Concept and an Activity Instance Concept. This is on two separate tabs, one showing a form based overview and one showing a simplifies YAML based overview. The YAML based overview will in a later release be made fully CDISC COSMoS compliant.
- A NeoDash Report displayed with outbound relationships from the versioned value node.
- A NeoDash based report is included with a more comprehensive display and browsing capabilities of Activity Concepts. This NeoDash report in shared in the neo4j-mdr-db git repository and must be launched manually. 

## V 0.3 (17-FEB-2023)

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