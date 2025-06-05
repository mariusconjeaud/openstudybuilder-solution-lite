@REQ_ID:2383812

Feature: Library - Admin Definitions - Projects

    Background: A Clinical Programme is existed
        Given The user is logged in

    Scenario: User must be able to use column selection option
        Given The '/library/projects' page is opened
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: [Create][Postive case] User must be able to create a new project
        Given The '/library/clinical_programmes' page is opened
        Given A Clinical Programme is created
        Given The '/library/projects' page is opened
        When Click on the + button to create a new project
        When Select an existed clinical programme
        And Input a project name, project number and description
        And 'save' button is clicked on form
        Then The pop up displays 'Project added'
        And Test project is found

    Scenario: [Actions][Edit] User must be able to edit the none study-linked project
        Given The '/library/clinical_programmes' page is opened
        Given A Clinical Programme is created
        Given The '/library/projects' page is opened
        And Click on the + button to create a new project
        And A test project exists and is not linked to any study
        And Test project is found
        When The 'Edit' option is clicked from the three dot menu list
        When Update the project name to a new one
        And 'save' button is clicked on form
        Then The pop up displays 'Project updated'
        And Test project is found

    Scenario: [Actions][Delete] User must be able to delete the none study-linked project
        Given The '/library/clinical_programmes' page is opened
        Given A Clinical Programme is created
        Given The '/library/projects' page is opened
        And Click on the + button to create a new project
        And A test project exists and is not linked to any study
        And Test project is found
        When The 'Delete' option is clicked from the three dot menu list
        When The continue is clicked in confirmation popup
        Then The pop up displays 'Project deleted'
        And Test project is no longer available

    Scenario: [Actions][Edit][Negative case] User must Not be able to edit a study-linked project
        Given The '/library/projects' page is opened
        And Test project with linked study is found
        When The 'Edit' option is clicked from the three dot menu list
        When User tries to update project name
        And 'save' button is clicked on form
        Then The error message displays that this project cannot be updated due to linked studies

    Scenario: [Actions][Delete][Negative case]User must Not be able to delete a study-linked project
        Given The '/library/projects' page is opened
        And Test project with linked study is found
        When The 'Delete' option is clicked from the three dot menu list
        When The continue is clicked in confirmation popup
        Then The error message shows that this project cannot be deleted due to linked studies