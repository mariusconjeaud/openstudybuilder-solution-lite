const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
import { getCurrStudyUid } from '../../support/helper_functions'

let studyVisits_uid

When('[API] Study vists uids are fetched for study {string}', (study_uid) => cy.getStudyVisits(study_uid).then(uids => studyVisits_uid = uids))

When('[API] Study visits in study {string} are cleaned-up', (study_uid) => {
    const studyVisitsSorted_uid = studyVisits_uid.sort().reverse()
    studyVisitsSorted_uid.forEach(visit_uid => cy.deleteStudyVisitByUid(study_uid, visit_uid))
})

Given('The epoch exists in selected study', () => {
    cy.createTestEpoch(getCurrStudyUid())
})

Given('The study with defined visit is selected', () => {
    cy.selectTestStudy('Study_000001')
})
Given('There are at least 3 visits created for the study', () => {
    cy.log('temporary step')
})

Given('The study with defined anchor visit is selected', () => {
    cy.selectTestStudy('Study_000001')
})

Given('The study without Study Epoch has been selected', () => {
    cy.selectTestStudy('Study_000004')
})

Given('The study with uid {string} is selected', study_uid => cy.selectTestStudy(study_uid))

When('The epoch for visit is not selected in new visit form', () => {
    cy.wait(2500)
    cy.clickButton('add-visit')
    cy.clickButton('SINGLE_VISIT', true)
    cy.clickFormActionButton('continue')
    cy.clickFormActionButton('continue')
})

Then('The validation appears under study period field', () => {
    cy.get('.v-messages__message').should('contain', "This field is required")
})

When('The type, contact mode, time reference and timing is not selected in new visit form', () => {
    cy.wait(2500)
    cy.clickButton('add-visit')
    cy.clickButton('SINGLE_VISIT', true)
    cy.clickFormActionButton('continue')
    cy.selectFirstVSelect('study-period')
    cy.clickFormActionButton('continue')
    cy.clickFormActionButton('save')
})

Then('The validation appears under given study details fields', () => {
    cy.checkIfValidationAppears('visit-type')
    cy.checkIfValidationAppears('contact-mode')
    cy.checkIfValidationAppears('time-reference')
    cy.checkIfValidationAppears('visit-timing')
})

When('The new Anchor Visit is added', () => {
    cy.fixture('studyVisits.js').then((visit_data) => {
        cy.wait(2500)
        cy.clickButton('add-visit')
        cy.clickButton('SINGLE_VISIT', true)
        cy.clickFormActionButton('continue')
        cy.selectVSelect('study-period', visit_data.study_epoch_name)
        cy.clickFormActionButton('continue')
        cy.clickButton(visit_data.visit_class_button, true)
        cy.selectVSelect('visit-type', visit_data.visit_type_name)
        cy.selectVSelect('contact-mode', visit_data.visit_contact_mode_name)
        cy.selectFirstVSelect('time-unit')
        cy.checkbox('anchor-visit-checkbox')
        cy.clickFormActionButton('save')
        cy.waitForTable()
    })
})

When('The new Anchor Visit creation is initiated', () => {
    cy.fixture('studyVisits.js').then((visit_data) => {
        cy.wait(2500)
        cy.clickButton('add-visit')
        cy.clickButton('SINGLE_VISIT', true)
        cy.clickFormActionButton('continue')
        cy.selectVSelect('study-period', visit_data.study_epoch_name)
        cy.clickFormActionButton('continue')
        cy.clickButton(visit_data.visit_class_button, true)
        cy.selectVSelect('visit-type', visit_data.visit_type_name)
        cy.selectVSelect('contact-mode', visit_data.visit_contact_mode_name)
        cy.selectFirstVSelect('time-unit')
        cy.checkbox('anchor-visit-checkbox')
    })
})

Then('It is not possible to edit Time Reference for anchor visit', () => {
    cy.get('[data-cy="time-reference"]').should('have.class', 'v-input--disabled')
})

Then('The new Anchor Visit is visible within the Study Visits table', () => {
    cy.fixture('studyVisits.js').then((visit_data) => {
        cy.tableContains(visit_data.study_epoch_name)
        cy.tableContains(visit_data.visit_type_name)

    })
})

When('The form for new study visit is opened', () => {
    cy.fixture('studyVisits.js').then((visit_data) => {
        cy.wait(2500)
        cy.clickButton('add-visit')
        cy.clickButton('SINGLE_VISIT', true)
        cy.clickFormActionButton('continue')
        cy.selectVSelect('study-period', visit_data.study_epoch_name)
        cy.clickFormActionButton('continue')
    })
})

Then('The Anchor visit checkbox is disabled', () => {
    cy.wait(1500)
    cy.get('[data-cy="anchor-visit-checkbox"]').should('not.exist')
})

When('The study visit is edited', () => {
    cy.waitForTableData()
    cy.clickFormActionButton('continue')
    cy.wait(3000)
    cy.clickFormActionButton('continue')
    cy.fillInput('visit-description', 'Edited visit description')
    cy.clickFormActionButton('save')
})

Then('The study visit data is reflected within the Study Visits table', () => {
    cy.tableContains('Edited visit description')
})

When('The user opens edit form for the study epoch for chosen study visit', () => {
    cy.get('[data-cy="table-item-action-button"]').last().click()
    cy.clickButton('Edit')
    cy.clickButton('continue-button')

})

Then('The study epoch field is enabled for editing', () => {
    cy.get('[data-cy="study-period"]').within(() => {
        cy.get('.v-field--active').should('exist')
    })
})

When('The user tries to update last treatment visit epoch to Screening without updating the timing', () => {
    cy.get('[data-cy="table-item-action-button"]').last().click()
    cy.clickButton('Edit', true)
    cy.clickButton('continue-button')
    cy.selectFirstVSelect('study-period')
    cy.clickButton('continue-button')
    cy.clickButton('save-button')

})
