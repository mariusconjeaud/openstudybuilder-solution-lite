@REQ_ID:1074260
Feature: Maintaining Study Activity Instances in Clinical MDR API

    Background: Test user must be able to call the Clinical MDR API and test data exist
        Given The test user can call the Clinical MDR API
        Given a test study identified by 'uid' is available holding test data


    Rule: As an API user,
        I want the system to support display of the Operational SoA,
        So that I can use this view for overview of the study data specification.

        Scenario: Support display of Operational SoA
        # Gherkin to be made


    Rule: As an API user,
        I want the system to support download of Operational SoA in .csv and Excel file formats,
        So that I can use the files for reviews and downstream integrations.

        Scenario Outline: Download of collections by visits of study activity instances in .csv and Excel file formats
            When the GET API endpoint '/studies/<uid>/operational-soa' is called to download Operational SoA in <file-format>
            Then the API must return the following columns with one row for each collection of an study activity instance by a visit
                # Note in .csv file column header is without underscores in lower case, in Excel as specified.
                | column | header            |
                | 1      | Study number      |
                | 2      | SoA group         |
                | 3      | Activity group    |
                | 4      | Activity subgroup |
                | 5      | Epoch             |
                | 6      | Visit             |
                | 7      | Activity          |
                | 8      | Activity instance |
                | 9      | Topic code        |
                | 10     | Param code        |
            Examples:
                | file-format |
                | .csv        |
                | Exc el      |


    Rule: As an API user,
        I want the system to support download of Operational SoA in DOCX file format,
        So that I can use the matrix representation in DOCX to review the Operational SoA.

        Scenario: Download of collections by visits of study activity instances in DOCX file format
            When the GET API endpoint '/studies/<uid>/operational-soa' is called to download Operational SoA in DOCX format
            Then the API must return the following columns with one row for each study activity instance by a visit
                | column | header                                                                                 |
                | 1      | Study number                                                                           |
                | 2      | Activities (SoA group, Activity group, Activity subgroup, Activity, Activity Instance) |
                | 3      | Topic Code                                                                             |
                | 4      | Param code                                                                             |
                | 3      | Epoch Visit Day/Week Window                                                            |
                | 4+     | <Study Epoch>                                                                          |
                | 4+     | <Study Visit>                                                                          |

