const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let itemGroupNameDefault, itemGroupOidDefault

When('Created CRF Item Group is found', () => cy.searchAndCheckPresence(itemGroupNameDefault, true))

Then('The CRF Item Group is no longer available', () => cy.searchAndCheckPresence(itemGroupNameDefault, false))

When('The CRF Item Group definition container is filled with data and saved', () => {
    itemGroupNameDefault = `CrfItemGroup${Date.now()}`
    itemGroupOidDefault = `Oid${Date.now()}`
    cy.fillInput('item-group-oid', itemGroupOidDefault)
    cy.fillInput('item-group-name', itemGroupNameDefault)
    cy.clickFormActionButton('continue')
    cy.clickFormActionButton('continue')
    cy.clickFormActionButton('save')
    cy.waitForTable()
})

When('The CRF Item Group metadata are updated and saved', () => {
    itemGroupNameDefault = `Update ${itemGroupNameDefault}`
    itemGroupOidDefault = `Update ${itemGroupNameDefault}`
    cy.fillInput('item-group-oid', itemGroupOidDefault)
    cy.fillInput('item-group-name', itemGroupNameDefault)
    cy.clickFormActionButton('continue')
    cy.clickFormActionButton('continue')
    cy.clickFormActionButton('continue')
    cy.fillInput('item-group-change-description', 'Test description')
    cy.clickFormActionButton('save')
    cy.waitForTable()
})
