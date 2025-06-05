const ctTermsTimeReferenceUrl = '/ct/terms?page_size=100&sort_by={"name.sponsor_preferred_name":true}&codelist_name=Time+Point+Reference'
const studiesInfoUrl = '/studies?include_sections=study_description&sort_by[current_metadata.identification_metadata.study_id]=true&page_size=0'
const studyMetadataUrl = (study_uid) => `studies/${study_uid}/study-visits?page_number=1&page_size=10&total_count=true`
const studyVisitUrl = (study_uid, studyVisit_uid) => `/studies/${study_uid}/study-visits/${studyVisit_uid}`

Cypress.Commands.add('getStudyUid', (study_number) => {
  cy.sendGetRequest(studiesInfoUrl).then((response) => {
            return response.body.items
                .find(study => study.current_metadata.identification_metadata.study_number == study_number)
                .uid
  })
})

Cypress.Commands.add('getGlobalAnchorUid', () => {
  cy.sendGetRequest(ctTermsTimeReferenceUrl).then((response) => {
            return response.body.items
                .find(term => term.name.sponsor_preferred_name == 'Global anchor visit')
                .term_uid
  })
})

Cypress.Commands.add('getStudyVisits', (study_uid) => {
  cy.sendGetRequest(studyMetadataUrl(study_uid)).then((response) => {
    let uid_array = []
    response.body.items.forEach(item => uid_array.push(item.uid))
    return uid_array
  })
})

Cypress.Commands.add('deleteStudyVisitByUid', (study_uid, studyVisit_uid) => {
  cy.sendDeleteRequest(studyVisitUrl(study_uid, studyVisit_uid))
})

Cypress.Commands.add('nullRegistryIdentifiersForStudy', () => {
  cy.request({
    method: 'PATCH',
    url: Cypress.env('API') + '/studies/Study_000001',
    body: {
      current_metadata: {
        identification_metadata: {
          registry_identifiers: {
            ct_gov_id: '',
            ct_gov_id_null_value_code: null,
            eudract_id: '',
            eudract_id_null_value_code: null,
            universal_trial_number_utn: '',
            universal_trial_number_utn_null_value_code: null,
            japanese_trial_registry_id_japic: '',
            japanese_trial_registry_id_japic_null_value_code: null,
            investigational_new_drug_application_number_ind: '',
            investigational_new_drug_application_number_ind_null_value_code: null,
          },
        },
      },
    },
  })
})

Cypress.Commands.add('testCompound', () => {
  cy.get(JSON.parse(window.localStorage.getItem('selectedStudy'))).then((current_study) => {
    cy.request(Cypress.env('API') + '/studies/' + current_study[0].uid + '/study-compounds').then((response) => {
      if (response.body == '') {
        cy.log('Compound - not found - creating')
        cy.request('POST', Cypress.env('API') + '/studies/' + current_study[0].uid + '/study-compounds/select', {
          compound_uid: null,
          device: null,
          dispensedIn: null,
          dosage_form: null,
          formulation: null,
          other_info: null,
          reason_for_missing_null_value_code: { term_uid: 'CTTerm_000143', name: 'Derived' },
          route_of_administration: null,
          type_of_treatment_uid: 'CTTerm_000159',
        }).then((response) => {
          expect(response.status).to.eq(201)
          cy.log('Compound - created - revisiting the page')
          cy.visit('studies/study_structure/epochs')
        })
      } else {
        cy.log('Compound - found')
      }
    })
  })
})

Cypress.Commands.add('createAndOpenCodelist', () => {
  let number = Date.now()
  cy.request('POST', Cypress.env('API') + '/ct/codelists', {
    catalogue_name: 'SEND CT',
    definition: `Definition${number}`,
    extensible: true,
    library_name: 'Sponsor',
    name: `Name${number}`,
    nci_preferred_name: `NCI${number}`,
    sponsor_preferred_name: `SponsorName${number}`,
    submission_value: `Submission${number}`,
    template_parameter: false,
    terms: [],
  }).then((created_response) => {
    cy.log('Codelist - created - visiting')
    cy.visit('/library/ct_catalogues/All/' + created_response.body.codelist_uid)
    cy.wait(3000)
  })
})

Cypress.Commands.add('createAndOpenTerm', () => {
  let number = Date.now()
  cy.request('POST', Cypress.env('API') + '/ct/terms', {
    catalogue_name: 'SEND CT',
    code_submission_value: `SubmissionCode${number}`,
    codelist_uid: 'C100129',
    definition: `Definition${number}`,
    library_name: 'Sponsor',
    name_submission_value: `SubmissionName${number}`,
    nci_preferred_name: `NCI${number}`,
    order: '1',
    sponsor_preferred_name: `SponsorName${number}`,
    sponsor_preferred_name_sentence_case: `SentanceName${number}`,
    synonyms: `Synonyms${number}`,
  }).then((created_response) => {
    cy.log('Term - created - visiting')
    cy.visit('/library/ct_catalogues/All/C100129/terms/' + created_response.body.term_uid)
    cy.wait(3000)
  })
})


Cypress.Commands.add('createCTPackage', (packageName) => {
  cy.request({
    url: `${Cypress.env('API')}/ct/packages/sponsor`,
    method: 'POST',
    body: {
      extends_package: `${packageName}`,
      effective_date: `${new Date().toISOString().split('T')[0]}`
    },
    failOnStatusCode: false
  }).then((response) => {
    expect(response.status).to.be.oneOf([201, 409])
    cy.log(`${packageName} exists`)
  })
})