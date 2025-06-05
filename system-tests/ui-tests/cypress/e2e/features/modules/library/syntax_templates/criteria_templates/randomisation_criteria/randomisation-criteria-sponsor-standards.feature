@REQ_ID:1070684
Feature: Library - Syntax Templates - Criteria - Randomisation - Parent

  As a user, I want to manage every Randomisation Criteria template under the Syntax template Library
  Background: User must be logged in
    Given The user is logged in

  Scenario: [Navigation] User must be able to navigate to the Randomisation Criteria template under the Syntax template Library
    Given The '/library' page is opened
    When The 'Criteria' submenu is clicked in the 'Syntax Templates' section
    And The 'Randomisation' tab is selected
    Then The current URL is 'library/criteria_templates/Randomisation/parent'

  Scenario: [Table][Columns][Names] User must be able to see the table with correct columns
    Given The 'library/criteria_templates/Randomisation/parent' page is opened
    Then A table is visible with following headers
      | headers         |
      | Sequence number |
      | Parent template |
      | Guidance text   |
      | Modified        |
      | Status          |
      | Version         |

  Scenario: [Table][Columns][Visibility] User must be able to select visibility of columns in the table 
    Given The '/library/criteria_templates/Randomisation/parent' page is opened
    When The first column is selected from Select Columns option for table with actions
    Then The table contain only selected column and actions column

  Scenario: [Create][Positive case] User must be able to create Randomisation Criteria template
    Given The 'library/criteria_templates/Randomisation/parent' page is opened
    When The new criteria is added in the library
    Then The Criteria is visible in the Criteria Templates Table
    And The item has status 'Draft' and version '0.1'

  Scenario: [Create][N/A indexes] User must be able to create Randomisation Criteria template with NA indexes
    Given The 'library/criteria_templates/Randomisation/parent' page is opened
    When The new Criteria is added in the library with not applicable for indexes
    Then The Criteria is visible in the Criteria Templates Table
    And The item has status 'Draft' and version '0.1'

  Scenario: [Actions][Edit][0.1 version] User must be able to edit initial version of the Randomisation Criteria template
    Given The 'library/criteria_templates/Randomisation/parent' page is opened
    And The new criteria is added in the library
    When The 'Edit' option is clicked from the three dot menu list
    And The criteria metadata is updated
    Then The Criteria is visible in the Criteria Templates Table
    And The item has status 'Draft' and version '0.2'

  Scenario: [Create][Mandatory fields] User must not be able to create Randomisation Criteria template without: Template Text
    Given The 'library/criteria_templates/Randomisation/parent' page is opened
    When The new Criteria template is added without template text
    Then The validation appears for Template name
    And The form is not closed

  Scenario: [Create][Mandatory fields] User must not be able to create Randomisation Criteria template without: Indication or Disorder, Criterion Category, Criterion Sub-Category
    Given The 'library/criteria_templates/Randomisation/parent' page is opened
    When The new Criteria template is added without mandatory data
    Then The validation appears for Indication or Disorder, Criterion Category, Criterion Sub-Category
    And The form is not closed

  Scenario: [Create][Syntax validation] User must be able to verify syntax when creating Randomisation Criteria template
    Given The 'library/criteria_templates/Randomisation/parent' page is opened
    When The new template name is prepared with a parameters
    And The syntax is verified
    Then The pop up displays "This syntax is valid"

  Scenario: [Create][Hide parameters] User must be able to hide parameter of the Randomisation Criteria template
    Given The 'library/criteria_templates/Randomisation/parent' page is opened
    When The new template name is prepared with a parameters
    And The user hides the parameter in the next step
    Then The parameter is not visible in the text representation

  Scenario: [Create][Select parameters] User must be able to select parameter of the Randomisation Criteria template
    Given The 'library/criteria_templates/Randomisation/parent' page is opened
    When The new template name is prepared with a parameters
    And The user picks the parameter from the dropdown list
    Then The parameter value is visible in the text representation

  Scenario: [Actions][Delete] User must be able to delete the Draft Randomisation Criteria template in version below 1.0
    Given [API] 'Randomisation' Criteria in status Draft exists
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And Criteria in searched for
    When The 'Delete' option is clicked from the three dot menu list
    Then The pop up displays "Template deleted"
    And The criteria is no longer available

  Scenario: [Actions][Approve] User must be able to approve the Draft Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And Criteria in searched for
    When The 'Approve' option is clicked from the three dot menu list
    Then The pop up displays 'Template is now in Final state'
    And The item has status 'Final' and version '1.0'

  Scenario: [Actions][Edit indexing] User must be able to edit indexing of Final Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And [API] Criteria is approved
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And Criteria in searched for
    When The 'Edit indexing' option is clicked from the three dot menu list
    And The indexing is updated for the Criteria Template
    And The 'Edit indexing' option is clicked from the three dot menu list
    Then The indexes in criteria template are updated

  Scenario: [Actions][Edit][Mandatory fields] User must not be able to save changes to Randomisation Criteria template without: Change description
    Given [API] 'Randomisation' Criteria in status Draft exists
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And Criteria in searched for
    When The 'Edit' option is clicked from the three dot menu list
    And The template is edited witout providing mandatory change description
    Then The validation appears for criteria change description field
    And The form is not closed

  Scenario: [Actions][New version] User must be able to add a new version of the Final Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And [API] Criteria is approved
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And Criteria in searched for
    When The 'New version' option is clicked from the three dot menu list
    Then The pop up displays 'New version created'
    And The item has status 'Draft' and version '1.1'

  Scenario: [Actions][Inactivate] User must be able to inactivate the Final Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And [API] Criteria is approved
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And Criteria in searched for
    When The 'Inactivate' option is clicked from the three dot menu list
    Then The pop up displays 'Template inactivated'
    And The item has status 'Retired' and version '1.0'

  Scenario: [Actions][Reactivate] User must be able to reactivate the Retired Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And [API] Criteria is approved
    And [API] Criteria is inactivated
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And Criteria in searched for
    When The 'Reactivate' option is clicked from the three dot menu list
    Then The pop up displays 'Template is now in Final state'
    And The item has status 'Final' and version '1.0'

  @manual_test
  Scenario: User must be able to view the history for the Randomisation Criteria template with a status as 'Retired'
    Given [API] 'Randomisation' Criteria in status Draft exists
    And [API] Criteria is approved
    And [API] Criteria is inactivated
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And Criteria in searched for
    When The 'Reactivate' option is clicked from the three dot menu list
    Then The 'History for template' window is displayed with the following column list with values
      | Column | Header                 |
      | 1      | Indication or disorder |
      | 2      | Criterion category     |
      | 3      | Criterion sub-category |
      | 4      | Template               |
      | 5      | Guidance text          |
      | 6      | Status                 |
      | 7      | Version                |
      | 8      | Change type            |
      | 9      | User                   |
      | 10     | From                   |
      | 11     | To                     |

  @manual_test
  Scenario: User must be able to read change history of output
    Given The 'library/criteria_templates/Randomisation/parent' page is opened
    When The user opens version history
    Then The user is presented with version history of the output containing timestamp and username

  @manual_test
  Scenario: User must be able to read change history of selected element
    Given The 'library/criteria_templates/Randomisation/parent' page is opened
    And The 'Show history' option is clicked from the three dot menu list
    When The user clicks on History for particular element
    Then The user is presented with history of changes for that element
    And The history contains timestamps and usernames

  Scenario Outline: [Table][Filtering] User must be able to filter the table by text fields
    Given The 'library/criteria_templates/Randomisation/parent' page is opened
    When The user filters field '<name>'
    Then The table is filtered correctly

    Examples:
      | name                   |
      | Indication or disorder |
      | Criterion category     |
      | Criterion sub-category |