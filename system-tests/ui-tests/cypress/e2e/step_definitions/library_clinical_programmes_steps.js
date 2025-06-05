const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let programmeName, projectName

When('Clinical programme is found', () => cy.searchAndCheckPresence(programmeName, true))

When('Clinical programme is no longer available', () => cy.searchAndCheckPresence(programmeName, false))

When('Click on the + button to create a new clinical programme', () => cy.clickButton('add-clinical-programme'))

When('Input a clinical programme name', () => fillName())

Given ('A test clinical programme exists and is not linked to any project', () => {
    fillName()
    cy.clickButton('save-button')
})

When('Update the clinical programme name to a new one', () => fillName(true))

When('User tries to update programme name', () => cy.fillInput('clinical-programme-name', 'Update'))

Given ('Create project and link it to the programme', () => {
    projectName = `Test project ${Date.now()}` 
    cy.selectAutoComplete('template-activity-group', programmeName)
    cy.fillInput('project-name', projectName)
    cy.fillInput('project-number', Date.now())
    cy.fillInput('project-description', `Test description ${Date.now()}`)
    cy.clickButton('save-button')
});

Then('The error message displays that this clinical programme can not be updated due to linked project', () => {
    cy.checkSnackbarMessage('Cannot update Clinical Programme')
 })

Then('The error message shows that this clinical programme can not be deleted due to linked project', () => {
    cy.checkSnackbarMessage('Cannot delete Clinical Programme')
 })

function fillName(update = false) {
    programmeName = update ? `Update ${programmeName}}` : `Test Programme ${Date.now()}`
    cy.fillInput('clinical-programme-name', programmeName) 
}