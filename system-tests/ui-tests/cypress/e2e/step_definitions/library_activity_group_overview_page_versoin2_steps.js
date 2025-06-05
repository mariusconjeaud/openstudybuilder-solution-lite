import { apiActivityName, apiGroupName, apiSubgroupName, apiInstanceName } from "./api_library_steps";
const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

const clickOnLinkInTable = (name) => cy.get('table tbody tr td').contains(name).click()
const verifyThatValuesPresent = (values) => values.forEach(value => cy.get('.v-table__wrapper').contains(value))

When('I click on the test activity group name in the activity group page', () => {

cy.searchAndCheckPresence(apiGroupName, true)
cy.get('table tbody tr td').contains(apiGroupName).click()

})
 
Then('The Activity subgroups table will be displayed with correct column', () => {
     // Check if the table is present
     cy.get('.group-overview-container').should('contain.text', 'Activity subgroups');

     // Assert that the table exists using the subgroups-table class
     cy.get('.subgroups-table').first().get('[data-cy="data-table"]').first().within(() => {
           cy.get('.v-data-table__thead .v-data-table__td').then(($headers) => {
               // Extract the text of each header
               const headerTexts = $headers.map((index, header) => Cypress.$(header).text().trim()).get();
               // Check that the header texts match the expected values
               expect(headerTexts).to.deep.equal(['Name', 'Definition', 'Version', 'Status']);
           });
       });
})

Then('The linked subgroup should be displayed in the Activity subgroups table', () => {
    cy.get('.group-overview-container').should('contain.text', 'Activity subgroups');
    // Assert that the table exists using the subgroups-table class
    cy.get('.subgroups-table').first().get('[data-cy="data-table"] tbody tr').first().within(() => {      
        cy.get('.v-data-table__td').then(($headers) => {
              // Extract the text of each header
              const headerTexts = $headers.map((index, header) => Cypress.$(header).text().trim()).get();
                cy.wrap($headers[0]).should('contain.text', apiSubgroupName); // First Column Check 
                cy.wrap($headers[2]).should('contain.text', '1.0'); // Version Check
                cy.wrap($headers[3]).should('contain.text', 'Final'); // Status Check
          });
      });
    });

Then('The free text search field should be displayed in the Activity subgroups table', () => {
        cy.get('[data-cy="search-field"]').first().should('be.visible'); // Check if the search field for Activity groupings table is present
    })
 
Then('The Activity subgroups table should be empty', () => {
    cy.get('.group-overview-container').should('contain.text', 'Activity subgroups');
    // Assert that the table exists using the subgroups-table class
    cy.get('.subgroups-table').first()
    .should('exist') // Confirm the table is present
    .within(() => {
        // Check for the "No subgroups available." message
        cy.get('tbody .v-data-table-rows-no-data')
          .should('exist') // Ensure the no-data row is present
          .find('span') // Locate the span containing the message
          .should('have.text', 'No subgroups available.'); // Check the text content
        });
    });

function verifyOverviewPage(pageName){
    cy.get('.d-flex.page-title').invoke('text').should('match', new RegExp(pageName));
    cy.get('button[role="tab"][value="html"]').contains('Overview');
}

function goToPageSearchAndClickLink(endpoint, searchFor, clickOn) {
    cy.visit(`/library/activities/${endpoint}`)
    cy.searchAndCheckPresence(searchFor, true)
    cy.get('table tbody tr td').contains(clickOn).click()
}

function openLinkedItemAndGoBack(itemName) {
    cy.get('.v-table__wrapper').contains('a', itemName).click();
    verifyOverviewPage(itemName) 
    cy.go(-1); // Go back to the previous page
    cy.wait(1000)
}