const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let crfTemplateName, crfTemplateOid, effectiveDate, retiredDate

When('Created CRF Template is found', () => cy.searchAndCheckPresence(crfTemplateName, true))

Then('The CRF Template is no longer available', () => cy.searchAndCheckPresence(crfTemplateName, false))

Given('[API] The CRF Template in draft status exists', () => {
    crfTemplateName = `API_CrfItem${Date.now()}`
    cy.createCrfTemplate(crfTemplateName)
})

When('The CRF Template definition container is filled with data and saved', () => {
    crfTemplateName = `CrfItem${Date.now()}`
    crfTemplateOid = `Oid${Date.now()}`
    fillNameAndOid()
    cy.fixture('crfTemplate.js').then((template) => {
        effectiveDate = template.effective_date
        retiredDate = template.retired_date
        cy.selectDatePicker('crf-template-effective-date', effectiveDate)
        cy.selectDatePicker('crf-template-retired-date', retiredDate)
    })
    saveCrfTemplate('created')
})

When('The CRF Template metadata are updated and saved', () => {
    crfTemplateName += 'Update'
    crfTemplateOid += 'Update'
    effectiveDate += 1
    retiredDate += 1
    fillNameAndOid()
    cy.selectDatePicker('crf-template-effective-date', effectiveDate)
    cy.selectDatePicker('crf-template-retired-date', retiredDate)
    saveCrfTemplate('updated')
})

Then('The CRF Template is visible in the table', () => {
    cy.checkRowByIndex(0, 'Name', crfTemplateName)
    cy.checkRowByIndex(0, 'OID', crfTemplateOid)
    cy.checkRowByIndex(0, 'Effective', effectiveDate)
    cy.checkRowByIndex(0, 'Obsolete', retiredDate)
})

When('The CRF Template definition container is filled without name provided', () => cy.clickButton('save-button'))

Then('The validation appears for the CRF Template Name field', () => cy.get('.v-messages__message').should('be.visible'))

function saveCrfTemplate(action) {
    cy.clickButton('save-button')
    cy.waitForFormSave()
    cy.checkSnackbarMessage(`Template ${action}`)
}

function fillNameAndOid() {
    cy.fillInput('crf-template-oid', crfTemplateOid)
    cy.fillInput('crf-template-name', crfTemplateName)
}