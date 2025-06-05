const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let formNameDefault, formOidDefault

When('Created CRF form is found', () => cy.searchAndCheckPresence(formNameDefault, true))

When('The Form definition container is filled with data and saved', () => {
    formNameDefault = `CrfForm${Date.now()}`
    formOidDefault = `Oid${Date.now()}`
    cy.fillInput('form-oid', formOidDefault)
    cy.fillInput('form-oid-name', formNameDefault)
    cy.clickFormActionButton('continue')
    cy.clickFormActionButton('continue')
    cy.clickFormActionButton('save')
    cy.waitForTable()
})

When('The Form metadata are updated and saved', () => {
    formOidDefault = `Update ${formOidDefault}`
    formNameDefault = `Update ${formNameDefault}`
    cy.fillInput('form-oid', formOidDefault)
    cy.fillInput('form-oid-name', formNameDefault)
    cy.clickFormActionButton('continue')
    cy.clickFormActionButton('continue')
    cy.clickFormActionButton('continue')
    cy.fillInput('form-change-description', 'Change description for edit scenario')
    cy.clickFormActionButton('save')
    cy.checkSnackbarMessage('Form updated')
})

Then('The CRF Form is no longer available', () => cy.searchAndCheckPresence(formOidDefault, false))