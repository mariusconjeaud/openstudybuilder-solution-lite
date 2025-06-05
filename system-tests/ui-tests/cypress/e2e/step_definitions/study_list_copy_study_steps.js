const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let studyNumber = `${Math.floor(1000 + Math.random() * 9000)}`
let projectNumber

Given('The user selects the {string} option', (option) => {
    cy.contains(option).click()
})

Given('The user populates new study project, number and acronym', () => {
    cy.selectFirstVSelect('project-id')
    cy.get('[data-cy="project-id"] input').invoke('val').then(val => projectNumber = val)
    cy.fillInput('study-number', studyNumber)
    cy.fillInput('study-acronym', 'CopiedViaAutomatedTests')
})


Then('The user is presented study selection dropdown', () => {
    cy.contains('.dialog-title', 'Which study do you want to copy from?').should('exist')
    cy.get('.v-label').should('contain', 'Study ID')
    cy.get('.v-label').should('contain', 'Study acronym')
})

Given('The user is on Select what to copy step in form', () => {
    cy.clickButton('add-study')
    cy.contains('Create a study from an existing study').click()
    cy.selectFirstVSelect('project-id')
    cy.fillInput('study-number', '9876')
    cy.fillInput('study-acronym', 'CopiedViaAutomatedTests')
    cy.clickButton('continue-button')

})

When('The user selects study to use for copy', () => {
    cy.intercept('**structure-statistics').as('study_statistics')
    cy.get('.v-form > .d-flex > :nth-child(1) > .v-input__control > .v-field > .v-field__field > .v-field__input').click()
    cy.contains('.v-list-item__content', '999-3000').click({force: true})
})

Then('The user is presented with visual representation of designated study structure', () => {
    cy.get('.dialog-sub-title').should('contain', 'Preview of study')
    
    cy.get('.arm').eq(0).should('have.attr', 'transform', 'translate(5, 36)').and('contain', 'Test Study Arm 0 short name')
    cy.get('.arm').eq(1).should('have.attr', 'transform', 'translate(5, 71)').and('contain', 'Test Study Arm 1 short name')
    
    cy.get('.epoch').eq(0).should('have.attr', 'transform', 'translate(215, 5)').and('contain', 'Screening')
    cy.get('.epoch').eq(1).should('have.attr', 'transform', 'translate(308, 5)').and('contain', 'Intervention 1')
    cy.get('.epoch').eq(2).should('have.attr', 'transform', 'translate(427, 5)').and('contain', 'Intervention 2')
    cy.get('.epoch').eq(3).should('have.attr', 'transform', 'translate(546, 5)').and('contain', 'Follow-up')

    cy.get('.visit-type').eq(0).should('have.attr', 'transform', 'translate(215, 118)').and('contain', 'Washout')

    cy.get('.visit-timing').eq(0).should('have.attr', 'transform', 'translate(215, 160)').and('contain', '-5 days')
    cy.get('.visit-timing').eq(1).should('have.attr', 'transform', 'translate(308, 160)').and('contain', '0 days')
    cy.get('.visit-timing').eq(2).should('have.attr', 'transform', 'translate(427, 160)').and('contain', '85 days')
    cy.get('.visit-timing').eq(3).should('have.attr', 'transform', 'translate(546, 160)').and('contain', '205 days')

    cy.get('line.timeline-arrow').should('have.length', 1);
    cy.get('line.visit-arrow').should('have.length', 4);
})

When('The user selects {string} category to be copied', (category) => {
    cy.contains('label', category).click()
})

Then('The {string} category with {string} derived from source study is presented for selection', (category, count) => {
    cy.get('@study_statistics').then((request) => {
        let statistic = request.response.body[count]
        cy.contains('label', category).should('have.text', `${category} (${statistic})`)
    })
    
})

Then('The {string} option is visible under {string} category showing appropiate {string} number', (option, category, count) => {
    cy.get('@study_statistics').then((request) => {
        let statistic = request.response.body[count]
        cy.contains('.pa-0', category).within(() => {
            cy.contains(`${option} (${statistic})`).should('exist')
            })
   })
    
})

Then('The Design matrix category is presented for selection', () => {
    cy.contains('label', 'Design matrix').should('exist')
})

When('The user saves the form with selected data to be copied', () => {
    cy.intercept('**clone').as('clone_request')
    cy.clickButton('save-button')
    cy.wait('@clone_request')
})

Then('The new study is created with selected data', () => {
    cy.get('@clone_request').then((req) => {
        expect(req.request.body.copy_study_arm).to.eq(true)
        expect(req.request.body.copy_study_arm).to.eq(true)
        expect(req.request.body.copy_study_branch_arm).to.eq(true)
        expect(req.request.body.copy_study_cohort).to.eq(true)
        expect(req.request.body.copy_study_design_matrix).to.eq(true)
        expect(req.request.body.copy_study_element).to.eq(true)
        expect(req.request.body.copy_study_epoch).to.eq(true)
        expect(req.request.body.copy_study_visit).to.eq(true)
        expect(req.request.body.project_number).to.eq(projectNumber)
        expect(req.request.body.study_acronym).to.eq('CopiedViaAutomatedTests')
        expect(req.request.body.study_number).to.eq(studyNumber)
        expect(req.response.statusCode).to.eq(201)
    })
})

When('The user did not select any category to be copied', () => {
    cy.log('No action step')
})

Given('The user selects study project and uses existing study number', () => {
    cy.sendGetRequest('/studies').as('study_request').then((req) => {
        cy.log(req)
        let existing_number = req.body.items[0].current_metadata.identification_metadata.study_number      
        cy.selectFirstVSelect('project-id')
        cy.fillInput('study-number', existing_number)
        cy.fillInput('study-acronym', 'CopiedViaAutomatedTests')
   
    })
})

Then('The system informs user that already existing number cannot be used', () => {
    cy.get('@study_request').then((req) => {
        let existing_number = req.body.items[0].current_metadata.identification_metadata.study_number
    cy.contains(`Study with Study Number '${existing_number}' already exists.`)
})})
        