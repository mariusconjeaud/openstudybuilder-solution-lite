const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let timeframeName

Then('The History for template window is displayed', () => {
  cy.get(`[data-cy="version-history-window"]`).should('be.visible');
  cy.get('.dialog-title').contains('History for template')
})

When('The template is updated with test data and saved', () => {
  timeframeName = `Edit${Date.now()}`
  cy.get('.ql-editor').clear({ force: true }).type(timeframeName);
  saveAndSearch('updated')
})

When('Timeframe template is saved', () => saveAndSearch('added'))

When('Timeframe template data is filled', () => addTemplateData())

Then('The Timeframe is visible in the Table', () => cy.checkRowByIndex(0, 'Template', timeframeName))

Then('The timeframe template is no longe available', () => cy.searchAndCheckPresence(timeframeName, false))

When('The Add template button is clicked', () => cy.clickButton('add-template'))

When('Change description field is not filled with test data', () => {
  cy.contains('.v-input', 'Change description').clear()
  cy.clickButton('save-button')
})

When('The Add time frame template section selected without test data', () => {
  cy.clickButton('add-template')
  cy.clickButton('save-button')
})

Then("The validation appears for timeframe change description field", () => cy.contains('.v-input', 'Change description').should('contain', 'This field is required'))

Then("The validation appears for timeframe name field", () => cy.get('.v-overlay .v-input').should('contain', 'This field is required'))

Then('[API] Timeframe template in status Draft exists', () => createTimeframeTemplateViaApi())

Then('[API] Timeframe template is approved', () => cy.approveTimeframe())

Then('[API] Timeframe template is inactivated', () => cy.inactivateTimeframe())

Then('[API] Timeframe template gets new version', () => cy.newVersionOfTimeframe(timeframeName))

Then('Timeframe template is searched for', () => {
    cy.intercept('/api/timeframe-templates?page_number=1&*').as('getTemplate')
    cy.wait('@getTemplate', {timeout: 20000})
    cy.searchAndCheckPresence(timeframeName, true)
})

function createTimeframeTemplateViaApi(customName = '') {
  cy.createTimeframe(customName)
  cy.getTimeframeName().then(name => timeframeName = name.replace('<p>', '').replace('</p>', '').trim())
}

function addTemplateData() {
  timeframeName = `${Date.now()} `
  cy.get('[data-cy="input-field"]').type(timeframeName);
  cy.wait(500)
  cy.get('[data-cy="types-dropdown"] .v-list-item').first().click()
  cy.get('[data-cy="input-field"]').invoke('val').then(text => timeframeName += text.trim().replace('[', '').replace(']', ''))
}

function saveAndSearch(action) {
  cy.clickButton('save-button')
  cy.checkSnackbarMessage(`Time frame template ${action}`)
  cy.searchAndCheckPresence(timeframeName, true)
}