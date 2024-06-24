# Release: post-March 2024


## 1. Indexes and Constraints
-------------------------------------
### Change Description
- Re-create all db indexes and constraints according to [db schema definition](https://novonordiskit.visualstudio.com/Clinical-MDR/_git/neo4j-mdr-db?path=/db_schema.py&version=GBmain&_a=contents).


## 2. CT Config Values (Study Fields Configuration)
-------------------------------------  
### Change Description
- Re-create all `CTConfigValue` nodes according to values defined in [this file](https://novonordiskit.visualstudio.com/Clinical-MDR/_git/studybuilder-import?path=/datafiles/configuration/study_fields_configuration.csv).

### Nodes Affected
- CTConfigValue


## 3. Migrate StudyActivityInstances nodes that should be created implicitly when StudyActivity is created
-------------------------------------  
### Change Description
- Removes incorrectly migrated StudyActivityInstances as these are not used in production database
  yet and will be recreated by following steps.
- The StudyActivityInstance nodes should be created when the StudyActivity is being created.
- The created StudyActivityInstance should link to the ActivityInstance node in case if the selected Activity
- for the StudyActivity is linked by some ActivityInstance

### Nodes Affected
  - `StudyActivityInstance`
  - `StudyActivity`
  - `ActivityInstanceValue`


## 4. Rename 'INSERTION_VISIT' visit_class propert into 'MANUALLY_DEFINED_VISIT'
-------------------------------------  
### Change Description
- Update those StudyVisit nodes that have `INSERTION_VISIT` set as visit_class property. The value should be updated
- to `MANUALLY_DEFINED_VISIT`.

### Nodes Affected
  - `StudyVisit`


## 5. Fix StudyDurationDays, StudyDurationWeeks, WeekInStudy properties for StudyVisits with negative timings
-------------------------------------  
### Change Description
- The `StudyDurationDays`, `StudyDurationWeeks` and `WeekInStudy` properties were incorrectly calculated for Studies with negative timings.
- The following migration fixes those values to be equal to StudyDay and StudyWeek values for the negative values.

### Nodes Affected
- `StudyVisit`
- `StudyDurationDays`
- `StudyDurationWeeks`
- `WeekInStudy`


## 6. Fix StudyWeek property for StudyVisits that have timing greater than -7 and less than 0.
-------------------------------------  
### Change Description
- The `StudyWeek` was incorrectly calculcated for the StudyVisits from the -7 < timing < 0 days interval.
- It should be set to -1 for such timing values.

### Nodes Affected
- `StudyWeek`