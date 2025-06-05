const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let projectName, programmeName

When('Test project is found', () => cy.searchAndCheckPresence(projectName, true))

When('Test project with linked study is found', () => cy.searchAndCheckPresence('CDISC Dev', true))

When('Test project is no longer available', () => cy.searchAndCheckPresence(projectName, false))

Given ('A Clinical Programme is created', () => {
    programmeName = `Test programme ${Date.now()}`
    cy.clickButton('add-clinical-programme')
    cy.fillInput('clinical-programme-name', programmeName) 
    cy.clickButton('save-button')
})

Given ('A test project exists and is not linked to any study', () => {
    cy.get('[data-cy="form-body"]').should('be.visible');
    cy.selectAutoComplete('template-activity-group', programmeName)
    fillProjectData()
    cy.clickButton('save-button')
});

When('Click on the + button to create a new project', () => cy.clickButton('add-project'))

When('Select an existed clinical programme', () => cy.selectAutoComplete('template-activity-group', programmeName))

When('Input a project name, project number and description', () => fillProjectData())

When('Update the project name to a new one', () => {
    projectName += 'Update'
    cy.wait(1000)
    cy.fillInput('project-name', projectName)
})

Then('User tries to update project name', () => cy.fillInput('project-name', 'Update'))

Then('The error message displays that this project cannot be updated due to linked studies', () => {
    cy.checkSnackbarMessage('Cannot update Project')
});

Then('The error message shows that this project cannot be deleted due to linked studies', () => {
    cy.checkSnackbarMessage('Cannot delete Project')
});

function fillProjectData() {
    projectName = `Test project ${Date.now()}` 
    cy.fillInput('project-name', projectName)
    cy.fillInput('project-number', Date.now())
    cy.fillInput('project-description', `Test description ${Date.now()}`)
}