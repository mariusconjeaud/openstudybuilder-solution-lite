@REQ_ID:xxx
Feature: Library - Code Lists - Terms

    Background: User must be logged in
        Given The user is logged in

@pending_development
    Scenario: [Navigation] User must be able to navigate to the Terms page
        Given The '/library' page is opened
        When The 'Terms' submenu is clicked in the 'Code Lists' section
        Then The current URL is 'library/terms'

@pending_development
    Scenario: [Table][Columns][Names] User must be able to see the columns list of Terms 
        Given The '/library/terms' page is opened
        Then A table is visible with following options
            | options                                                         |
            | Columns                                                         |
            | Export                                                          |
            | Add select boxes to table to allow selection of rows for export | * to be checked

        And A table is visible with following headers (to be added)
            | headers                |
            | Library                |
            | Sponsor preferred name |
            | Template parameter     |
            | Code list status       |
            | Name modified          |
            | Concept ID             |

@pending_development
    Scenario: [Table][Pagination] User must be able to use table pagination
        Given The '/library/terms' page is opened
        When The user switches pages of the table
        Then The table page presents correct data

@pending_development
    Scenario: User must be able to add none-code list to the terms table
        Given The '/library/terms' page is opened
        When The user filter the none-code list from the table
        And The user clicks on the 'Edit' button from the three dot menu list
        Then The 'Edit' page is opened
        When The user clicks on the 'Add' button
        And The user fills in all the neccesary fields
        And The user clicks on the 'Save' button
        Then The 'Edit' page is closed
        And The table contains the added none-code list

@pending_development
     Scenario: User must be able to add new term to the terms table
        Given The '/library/terms' page is opened
        When The user clicks on the 'Edit' button from the three dot menu list
        Then The 'Edit' page is opened
        When The user clicks on the 'Add' button
        And The user fills in all the neccesary fields
        And The user clicks on the 'Save' button
        Then The 'Edit' page is closed
        And The table contains the added 

@pending_development     
    Scenario: User must be able to verify the history page of the term
        Given The '/library/terms' page is opened
        When The user clicks on the 'view history' button from the three dot menu list
        Then The 'History' page is opened
        And The history page contains the following data (to be checked)
            | name               | value                                                                                                                                |
            | Library            | CDISC                                                                                                                               |
            | Sponsor preferred  | AUC All Normalized by Body Mass Index                                                                                               |
            | Template parameter  | AUC All Norm by BMI                                                                                                                 |
            | Code list status    | AUCALLB                                                                                                                             |
            | Name modified      | The area under the curve (AUC) from the time of dosing to th                                                                        |

    

    