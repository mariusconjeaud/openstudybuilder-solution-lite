let arm_type_uid
const ctTermArmTypeUrl_Refactor = '/ct/codelists/terms?page_size=100&codelist_submission_value=ARMTTP'
const ctTermArmTypeUrl = '/ct/terms?page_size=100&sort_by={"name.sponsor_preferred_name":true}&codelist_name=Arm+Type'

Cypress.Commands.add('createTestArm', (study_uid) => {
    cy.request('GET', Cypress.env('API') + '/studies/' + study_uid + '/study-arms?page_number=1&page_size=10&total_count=true&study_uid=' + study_uid).then((response) => {
        if (response.body.total == 0) {
            cy.request('POST', Cypress.env('API') + '/studies/' + study_uid + '/study-arms', {
                arm_type_uid: arm_type_uid,
                code: `Code${Date.now()}`,
                description: 'TestDescForArm',
                name: `Arm${Date.now()}`,
                short_name: `Arm${Date.now()}`,
                number_of_subjects: '100',
                randomization_group: `Random${Date.now()}`,
            }).then((created_response) => {
                cy.log('Test arm created with status code' + created_response.status)
            })
        }
    })
})

Cypress.Commands.add('deleteStudyArm', () => {
    cy.request('DELETE', Cypress.env('API') + `studies/${Cypress.env('TEST_STUDY_UID')}/study-arms/StudyArm_000155`).then((response) => cy.log('Test arm deleted' + response.status))
})

Cypress.Commands.add('getArmTypeUid', (armType_name) => {
    cy.sendGetRequest(ctTermArmTypeUrl).then((response) => {
      arm_type_uid = response.body.items.find(item => item.name.sponsor_preferred_name == armType_name).term_uid
  })
})

Cypress.Commands.add('getArmTypeUidRefactored', (armType_name) => {
    cy.sendGetRequest(ctTermArmTypeUrl_Refactor).then((response) => {
      arm_type_uid = response.body.items.find(item => item.sponsor_preferred_name == armType_name).term_uid
  })
})