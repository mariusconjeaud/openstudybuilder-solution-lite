const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let defaultActivityName, indicationSelected

Then('The Activity Instruction template is visible in the table', () => cy.checkRowByIndex(0, 'Parent template', defaultActivityName))

When("The new activity is added in the library", () => addTemplate(true, false))

When("The new Activity is added in the library with not applicable for indexes", () => addTemplate(true, false))

When("The second activity is added with the same template text", () => {
  addTemplate(false, false)
  cy.clickFormActionButton('save')
})

When("The new Activity template is added without template text", () => {
  cy.clickButton('add-template')
  cy.clickFormActionButton('continue')
})

When("The new Activity template is added without Indication or Disorder", () => addTemplateWithoutMandatoryData(false, false, false))

When("The new Activity template is added without Activity Group", () => addTemplateWithoutMandatoryData(true, false, false))

When("The new Activity template is added without Activity Subgroup", () => addTemplateWithoutMandatoryData(true, true, false))

When("The new Activity template is added without Activity field", () => addTemplateWithoutMandatoryData(true, true, true))

Then("The validation appears for Indication or Disorder field", () => cy.checkIfValidationAppears('template-indication-dropdown'))

Then("The validation appears for Activity Group field", () => cy.checkIfValidationAppears('template-activity-group'))

Then("The validation appears for Activity Subgroup field", () => cy.checkIfValidationAppears('template-activity-sub-group'))

Then("The validation appears for Activity field", () => cy.checkIfValidationAppears('template-activity-activity'))

Then("The validation appears for activity change description field", () => cy.checkIfValidationAppears('template-change-description'))

When("The created activity template is edited without change description provided", () => {
  fillTemplateNameAndCountinue("testDescriptionUpdate")
  cy.clickFormActionButton('continue')
  cy.get('[data-cy="template-change-description"] [value]').clear()
  cy.clickFormActionButton('save')
})

When("The activity metadata is updated", () => {
  defaultActivityName = `${Date.now()}Updated`
  fillTemplateNameAndCountinue(defaultActivityName)
  cy.clickFormActionButton('continue')
  cy.fillInput("template-change-description", "updated for test")
  saveActivityInstructionAndSearch()
})

When("The indexing is updated for the Activity Template", () => {
  cy.selectLastVSelect("template-indication-dropdown")
  cy.get('[data-cy="template-indication-dropdown"] .v-field__input').invoke("text").then(text => indicationSelected = text)
  cy.clickButton("save-button")
  cy.checkSnackbarMessage('Indexing properties updated')
  cy.searchAndCheckPresence(defaultActivityName, true)
})

Then("The indexes in activity template are updated", () => {
  cy.get('[data-cy="template-indication-dropdown"] .v-field__input').should('contain', indicationSelected.split(',')[0])
  cy.get('[data-cy="template-indication-dropdown"] .v-field__input').should('contain', indicationSelected.split(',')[1])
})
Then("The parent activity is no longer available", () => cy.searchAndCheckPresence(defaultActivityName, false))

Then('[API] Activity Instruction in status Draft exists', () => createActivityInstructionViaApi())

Then('[API] Activity Instruction is approved', () => cy.approveActivityInstruction())

Then('[API] Activity Instruction is inactivated', () => cy.inactivateActivityInstruction())

Then('Activity Instruction is searched for', () => {
    cy.intercept('/api/activity-instruction-templates?page_number=1&*').as('getTemplate')
    cy.wait('@getTemplate', {timeout: 20000})
    cy.searchAndCheckPresence(defaultActivityName, true)
})

function fillTemplateNameAndCountinue(name) {
  cy.wait(1500)
  cy.fillTextArea("template-text-field", name)
  cy.clickFormActionButton('continue')
  cy.clickFormActionButton('continue')
}

function addTemplate(uniqueName, notApplicableIndexes) {
  defaultActivityName = uniqueName ? `ActivityInstruction${Date.now()}` : defaultActivityName 
  cy.clickButton('add-template');
  fillTemplateNameAndCountinue(defaultActivityName)
  if (notApplicableIndexes) cy.checkAllCheckboxes()
    else {
      cy.selectFirstVSelect('template-activity-group')
      cy.selectFirstVSelect('template-activity-sub-group')
  }
  cy.selectFirstVSelect('template-indication-dropdown')
  cy.selectFirstVSelect('template-activity-activity')
  if (uniqueName) saveActivityInstructionAndSearch()
}

function addTemplateWithoutMandatoryData(selectIndication, selectActivityGroup, selectSubGroup) {
  cy.clickButton('add-template')
  fillTemplateNameAndCountinue(`${Date.now()}`)
  if (selectIndication) cy.selectFirstVSelect('template-indication-dropdown')
  if (selectActivityGroup) cy.selectFirstVSelect('template-activity-group')
  if (selectSubGroup) cy.selectFirstVSelect('template-activity-sub-group')
  cy.clickFormActionButton('save')
}

function createActivityInstructionViaApi(customName = '') {
  cy.getInidicationUid()
  cy.createActivityInstruction(customName)
  cy.getActivityInstructionName().then(name => defaultActivityName = name.replace('<p>', '').replace('</p>', '').trim())
}

function saveActivityInstructionAndSearch() {
  cy.intercept('/api/activity-instruction-templates?page_number=1&*').as('getTemplate')
  cy.clickFormActionButton('save')
  cy.wait('@getTemplate', {timeout: 20000})
  cy.waitForTable()
  cy.searchAndCheckPresence(defaultActivityName, true)
}