Cypress.Commands.add('createCriteriaTemplate', () => {
        cy.request({
            method: 'POST',
            url: Cypress.env('API') + '/criteria-templates',
            body: JSON.stringify(inclusion),
        }).then((response) => {
            cy.request({
                    method: 'POST',
                    url: Cypress.env('API') + '/criteria-templates/' + response.body.uid + '/approvals',
                })
        })
    cy.reload()
})


const inclusion = "{ name: '<p>Test inclusion criteria testTemplate</p>', library_name: 'User Defined', type_uid: 'C25532_INCLUSION', study_uid: 'Study_000001' }"
const exclusion = '{ name: "<p>Test exclusion criteria testTemplate</p>", library_name: "User Defined", type_uid: "C25370_EXCLUSION", study_uid: "Study_000001" }'
const runIn = '{ name: "<p>Test runIn criteria testTemplate</p>", library_name: "User Defined", type_uid: "CTTerm_000025", study_uid: "Study_000001" }'
const randomisation = '{ name: "<p>Test randomisation criteria testTemplate</p>", library_name: "User Defined", type_uid: "CTTerm_000026", study_uid: "Study_000001" }'
const dosing = '{ name: "<p>Test dosing criteria testTemplate</p>", library_name: "User Defined", type_uid: "CTTerm_000027", study_uid: "Study_000001" }'
const withdrawal = '{ name: "<p>Test withdrawal criteria testTemplate</p>", library_name: "User Defined", type_uid: "CTTerm_000028", study_uid: "Study_000001" }'