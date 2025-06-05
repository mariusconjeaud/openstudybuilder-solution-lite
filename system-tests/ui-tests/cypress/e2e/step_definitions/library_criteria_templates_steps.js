const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let defaultCriteriaName, indicationSelected, criterionCatSelected, criterionSubCatSelected, parameterSelected

When('The new criteria is added in the library', () => createCriteria(false))

When('The new Criteria is added in the library with not applicable for indexes', () => createCriteria(true))

Then('The Criteria is visible in the Criteria Templates Table', () => cy.checkRowByIndex(0, 'Parent template', defaultCriteriaName))

When('The new Criteria template is added without template text', () => {
    cy.clickButton('add-template')
    cy.clickFormActionButton('continue')
})

When('The new Criteria template is added without mandatory data', () => {
    cy.clickButton('add-template')
    fillNameAndContinue(Date.now())
    cy.clickFormActionButton('save')
})

Then('The validation appears for Indication or Disorder, Criterion Category, Criterion Sub-Category', () => {
    cy.checkIfValidationAppears('template-indication-dropdown')
    cy.checkIfValidationAppears('template-criterion-category')
    cy.checkIfValidationAppears('template-criterion-sub-category')
})

When('The new template name is prepared with a parameters', () => {
    cy.clickButton('add-template')
    cy.fillTextArea('template-text-field', 'Test [Activity] and [Event] template')
})

When('The syntax is verified', () => cy.clickButton('verify-syntax-button'))

When('The user hides the parameter in the next step', () => {
    cy.clickFormActionButton('continue')
    cy.get('[title^="Show/hide parameter"] .v-btn__content').first().click()
})

When('The user picks the parameter from the dropdown list', () => {
    cy.clickFormActionButton('continue')
    cy.selectLastVSelect("Activity")
    cy.get('[data-cy="Activity"] span').invoke("text").then(text => parameterSelected = text)
})

Then('The parameter is not visible in the text representation', () => checkParameterValue(false, 'Activity'))

Then('The parameter value is visible in the text representation', () => checkParameterValue(true, parameterSelected.split('...')[0]))

Then('The validation appears for criteria change description field', () => cy.checkIfValidationAppears('template-change-description'))

Then('The criteria is no longer available', () => cy.searchAndCheckPresence(defaultCriteriaName, false))

When('The indexing is updated for the Criteria Template', () => {
    fillIndexingData(true)
    cy.clickFormActionButton('save')
})

When('The criteria metadata is updated', () => {
    defaultCriteriaName = `${Date.now()} Updated`
    fillNameAndContinue(defaultCriteriaName)
    fillIndexingData(true)
    cy.clickFormActionButton('continue')
    cy.fillInput('template-change-description', 'updated for test')
    cy.clickFormActionButton('save')
    cy.searchAndCheckPresence(defaultCriteriaName, true)
})

Then('The indexes in criteria template are updated', () => {
    cy.wait(2000)
    cy.get('[data-cy="form-body"]').should('contain', indicationSelected)
    cy.get('[data-cy="form-body"]').should('contain', criterionCatSelected)
    cy.get('[data-cy="form-body"]').should('contain', criterionSubCatSelected)
})

Then('[API] {string} Criteria in status Draft exists', (type) => createCriteriaViaApi(type))

Then('[API] Criteria is approved', () => cy.approveCriteria())

Then('[API] Criteria is inactivated', () => cy.inactivateCriteria())

Then('Criteria in searched for', () => {
    cy.intercept('/api/criteria-templates?page_number=1&*').as('getCriteria')
    cy.wait('@getCriteria', {timeout: 20000})
    cy.searchAndCheckPresence(defaultCriteriaName, true)
})

function createCriteria(notApplicableIndexes) {
    defaultCriteriaName = `Criteria${Date.now()}`
    cy.clickButton('add-template')
    fillNameAndContinue(defaultCriteriaName)
    notApplicableIndexes ? cy.checkAllCheckboxes() : fillIndexingData(false)
    cy.intercept('/api/criteria-templates?page_number=1&*').as('getCriteria')
    cy.clickFormActionButton('save')
    cy.wait('@getCriteria', {timeout: 20000})
    cy.waitForTable()
    cy.searchAndCheckPresence(defaultCriteriaName, true)
}

function fillNameAndContinue(name) {
    cy.fillTextArea('template-text-field', name)
    cy.clickFormActionButton('continue')
    cy.clickFormActionButton('continue')
}

function fillIndexingData(update) {
    let select = update ? (locator) => cy.selectLastMultipleSelect(locator) : (locator) => cy.selectFirstMultipleSelect(locator)
    cy.clearField('template-indication-dropdown')
    cy.clearField('template-criterion-category')
    cy.clearField('template-criterion-sub-category')
    select('template-indication-dropdown')
    select('template-criterion-category')
    select('template-criterion-sub-category')
    cy.get('[data-cy="template-indication-dropdown"] input').invoke('text').then(text => indicationSelected = text)
    cy.get('[data-cy="template-criterion-category"] input').invoke('text').then(text => criterionCatSelected = text)
    cy.get('[data-cy="template-criterion-sub-category"] input').invoke('text').then(text => criterionSubCatSelected = text)
}

function checkParameterValue(shouldContain, value) {
    let condition = shouldContain ? 'contain' : 'not.contain'
    cy.get('[edit-mode="false"] .template-readonly').should(condition, value)
    cy.get('[edit-mode="false"] .pa-4').should(condition, value)
}

function createCriteriaViaApi(type, customName = '') {
    if (type == 'Inclusion') cy.getInclusionCriteriaUid()
        else if (type == 'Exclusion') cy.getExclusionCriteriaUid()
            else if (type == 'Dosing') cy.getDosingCriteriaUid()
                else if (type == 'Withdrawal') cy.getWithdrawalCriteriaUid()
                    else if (type == 'Run-in') cy.getRunInCriteriaUid()
                        else if (type == 'Randomisation') cy.getRandomizationCriteriaUid()
    cy.getInidicationUid()
    cy.getCriteriaCategoryUid()
    cy.getCriteriaSubCategoryUid()
    cy.createCriteria(customName)
    cy.getCriteriaName().then(name => defaultCriteriaName = name.replace('<p>', '').replace('</p>', '').trim())
}