@REQ_ID:1070684
Feature: Library - Syntax Templates - Time Frames - Parent
  As a user, I want to manage every Timeframe template under the Syntax template Library
  
  Background: User must be logged in
    Given The user is logged in

  Scenario: [Navigation] User must be able to navigate to the Timeframe template under the Syntax template Library
    Given The '/library' page is opened
    When The 'Time Frames' submenu is clicked in the 'Syntax Templates' section
    And The 'Parent' tab is selected
    Then The current URL is '/library/timeframe_templates/parent'

  Scenario: [Table][Columns][Names] User must be able to see the table with correct columns
    Given The '/library/timeframe_templates/parent' page is opened
    Then A table is visible with following headers
      | headers         |
      | Sequence number |
      | Template        |
      | Modified        |
      | Status          |
      | Version         |

  Scenario: [Table][Columns][Visibility] User must be able to select visibility of columns in the table 
    Given The '/library/timeframe_templates/parent' page is opened
    When The first column is selected from Select Columns option for table with actions
    Then The table contain only selected column and actions column

  Scenario: [Create][Positive case] User must be able to create Timeframe template
    Given The '/library/timeframe_templates/parent' page is opened
    When The Add template button is clicked
    And Timeframe template data is filled
    And Timeframe template is saved
    Then The Timeframe is visible in the Table

  Scenario: [Create][Mandatory fields] User must not be able to create Timeframe template without: Template Text
    Given The '/library/timeframe_templates/parent' page is opened
    When The Add time frame template section selected without test data
    Then The validation appears for timeframe name field

  Scenario: [Create][Mandatory fields] User must be able to verify syntax when creating Timeframe template
    Given The '/library/timeframe_templates/parent' page is opened
    When The Add template button is clicked
    And Timeframe template data is filled
    And The 'verify-syntax-button' button is clicked
    Then The pop up displays 'This syntax is valid'

  Scenario: [Actions][Edit][0.1 version] User must be able to edit initial version of the Timeframe template
    Given [API] Timeframe template in status Draft exists
    And The '/library/timeframe_templates/parent' page is opened
    And Timeframe template is searched for
    When The 'Edit' option is clicked from the three dot menu list
    And The template is updated with test data and saved
    And The Timeframe is visible in the Table
    And The item has status 'Draft' and version '0.2'

  Scenario: [Actions][Edit][Mandatory fields] User must not be able to save changes to Timeframe template without: Change description
    Given [API] Timeframe template in status Draft exists
    And The '/library/timeframe_templates/parent' page is opened
    And Timeframe template is searched for
    When The 'Edit' option is clicked from the three dot menu list
    And Change description field is not filled with test data
    Then The validation appears for timeframe change description field

  Scenario: [Actions][Approve] User must be able to approve the Draft Timeframe template
    Given [API] Timeframe template in status Draft exists
    And The '/library/timeframe_templates/parent' page is opened
    And Timeframe template is searched for
    When The 'Approve' option is clicked from the three dot menu list
    Then The pop up displays 'Template is now in Final state'
    And The item has status 'Final' and version '1.0'

  Scenario: [Actions][Delete] User must be able to delete the Draft Timeframe template in version below 1.0
    Given [API] Timeframe template in status Draft exists
    And The '/library/timeframe_templates/parent' page is opened
    And Timeframe template is searched for
    When The 'Delete' option is clicked from the three dot menu list
    Then The pop up displays 'Timeframe template has been deleted'
    And The timeframe template is no longe available

  Scenario: [Actions][Availability][Final item] User must not be able to have access to Delete action for Timeframe template in version above 1.0
    Given [API] Timeframe template in status Draft exists
    And [API] Timeframe template is approved
    And [API] Timeframe template gets new version
    And The '/library/timeframe_templates/parent' page is opened
    And Timeframe template is searched for
    When The item actions button is clicked
    Then 'Delete' action is not available
    Then 'Edit' action is available

  Scenario: [Actions][View history][Draft item] User must be able to view the history for the Draft Timeframe template
    Given [API] Timeframe template in status Draft exists
    And The '/library/timeframe_templates/parent' page is opened
    And Timeframe template is searched for
    When The 'History' option is clicked from the three dot menu list
    Then The History for template window is displayed
    And The following column list with values will exist
      | header          |
      | Sequence number |
      | Template        |
      | Status          |
      | Version         |
      | Change type     |
      | User            |
      | From            |
      | To              |

  Scenario: [Actions][New version] User must be able to add a new version of the Final Timeframe template
    Given [API] Timeframe template in status Draft exists
    And [API] Timeframe template is approved
    And The '/library/timeframe_templates/parent' page is opened
    And Timeframe template is searched for
    When The 'New version' option is clicked from the three dot menu list
    Then The pop up displays 'New version created'
    And The item has status 'Draft' and version '1.1'

  Scenario: [Actions][Inactivate] User must be able to inactivate the Final Timeframe template
    Given [API] Timeframe template in status Draft exists
    And [API] Timeframe template is approved
    And The '/library/timeframe_templates/parent' page is opened
    And Timeframe template is searched for
    When The 'Inactivate' option is clicked from the three dot menu list
    Then The pop up displays 'Template inactivated'
    And The item has status 'Retired' and version '1.0'

  Scenario: [Actions][View history][Final item] User must be able to view the history for the Draft Timeframe template
    Given [API] Timeframe template in status Draft exists
    And [API] Timeframe template is approved
    And The '/library/timeframe_templates/parent' page is opened
    And Timeframe template is searched for
    When The 'History' option is clicked from the three dot menu list
    Then The History for template window is displayed
    And The following column list with values will exist
      | header          |
      | Sequence number |
      | Template        |
      | Status          |
      | Version         |
      | Change type     |
      | User            |
      | From            |
      | To              |

  Scenario: [Actions][Reactivate] User must be able to reactivate the Retired Timeframe template
    Given [API] Timeframe template in status Draft exists
    And [API] Timeframe template is approved
    And [API] Timeframe template is inactivated
    And The '/library/timeframe_templates/parent' page is opened
    And Timeframe template is searched for
    When The 'Reactivate' option is clicked from the three dot menu list
    Then The pop up displays 'Template is now in Final state'
    And The item has status 'Final' and version '1.0'

  Scenario: [Actions][View history][Retired item] User must be able to view the history for the Retired Timeframe template
    Given [API] Timeframe template in status Draft exists
    And [API] Timeframe template is approved
    And [API] Timeframe template is inactivated
    And The '/library/timeframe_templates/parent' page is opened
    And Timeframe template is searched for
    When The 'History' option is clicked from the three dot menu list
    Then The History for template window is displayed
    And The following column list with values will exist
      | header          |
      | Sequence number |
      | Template        |
      | Status          |
      | Version         |
      | Change type     |
      | User            |
      | From            |
      | To              |

  @manual_test
  Scenario: User must be able to read change history of output
    Given The '/library/timeframe_templates/parent' page is opened
    When The user opens version history
    Then The user is presented with version history of the output containing timestamp and username

  @manual_test
  Scenario: User must be able to read change history of selected element
    Given The '/library/timeframe_templates/parent' page is opened
    And The 'Show history' option is clicked from the three dot menu list
    When The user clicks on History for particular element
    Then The user is presented with history of changes for that element
    And The history contains timestamps and usernames

  Scenario Outline: [Table][Filtering] User must be able to filter the table by text fields
    Given The 'library/timeframe_templates/parent' page is opened
    When The user filters field '<name>'
    Then The table is filtered correctly

    Examples:
      | name            |
      | Sequence number |
      | Template        |
      | Status          |
      | Version         |

  Scenario: [Table][Pagination] User must be able to use table pagination        
      Given The '/library/timeframe_templates/parent' page is opened
      When The user switches pages of the table
      Then The table page presents correct data