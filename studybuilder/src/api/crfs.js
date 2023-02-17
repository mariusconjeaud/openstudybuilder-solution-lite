import repository from './repository'

const resource = 'concepts/odms'

export default {
  get (source, params) {
    if (!source) {
      return repository.get(`${resource}`, params)
    }
    return repository.get(`${resource}/${source}`, params)
  },
  reactivate (source, uid) {
    return repository.post(`${resource}/${source}/${uid}/activations`)
  },
  inactivate (source, uid) {
    return repository.delete(`${resource}/${source}/${uid}/activations`)
  },
  newVersion (source, uid) {
    return repository.post(`${resource}/${source}/${uid}/versions`)
  },
  approve (source, uid) {
    return repository.post(`${resource}/${source}/${uid}/approvals`)
  },
  delete (source, uid) {
    return repository.delete(`${resource}/${source}/${uid}`)
  },
  createForm (data) {
    return repository.post(`${resource}/forms`, data)
  },
  updateForm (data, uid) {
    return repository.patch(`${resource}/forms/${uid}`, data)
  },
  batchCreateDescription (data) {
    return repository.post(`${resource}/descriptions/batch`, data)
  },
  createAlias (data) {
    return repository.post(`${resource}/aliases`, data)
  },
  getAliases () {
    return repository.get(`${resource}/aliases`)
  },
  getForm (uid) {
    return repository.get(`${resource}/forms/${uid}`)
  },
  createItemGroup (data) {
    return repository.post(`${resource}/item-groups`, data)
  },
  updateItemGroup (data, uid) {
    return repository.patch(`${resource}/item-groups/${uid}`, data)
  },
  getItemGroup (uid) {
    return repository.get(`${resource}/item-groups/${uid}`)
  },
  getTemplateAuditTrail (uid) {
    return repository.get(`${resource}/templates/${uid}/versions`)
  },
  getFormAuditTrail (uid) {
    return repository.get(`${resource}/forms/${uid}/versions`)
  },
  getGroupAuditTrail (uid) {
    return repository.get(`${resource}/item-groups/${uid}/versions`)
  },
  createItem (data) {
    return repository.post(`${resource}/items`, data)
  },
  updateItem (data, uid) {
    return repository.patch(`${resource}/items/${uid}`, data)
  },
  getItem (uid) {
    return repository.get(`${resource}/items/${uid}`)
  },
  getItemAuditTrail (uid) {
    return repository.get(`${resource}/items/${uid}/versions`)
  },
  getTemplate (uid) {
    return repository.get(`${resource}/templates/${uid}`)
  },
  createTemplate (data) {
    return repository.post(`${resource}/templates`, data)
  },
  updateTemplate (data, uid) {
    return repository.patch(`${resource}/templates/${uid}`, data)
  },
  addFormsToTemplate (data, uid, sync) {
    return repository.post(`${resource}/templates/${uid}/forms?override=${sync}`, data)
  },
  addItemGroupsToForm (data, uid, sync) {
    return repository.post(`${resource}/forms/${uid}/item-groups?override=${sync}`, data)
  },
  addItemsToItemGroup (data, uid, sync) {
    return repository.post(`${resource}/item-groups/${uid}/items?override=${sync}`, data)
  },
  overwriteFormsInTemplate (data, uid) {
    return repository.post(`${resource}/templates/${uid}/forms`, data)
  },
  overwriteItemGroupsInForm (data, uid) {
    return repository.post(`${resource}/forms/${uid}/item-groups`, data)
  },
  overwriteItemsInItemGroup (data, uid) {
    return repository.post(`${resource}/item-groups/${uid}/items`, data)
  },
  addActivityGroupsToForm (data, uid) {
    return repository.post(`${resource}/forms/${uid}/activity-groups?override=true`, data)
  },
  addActivitySubGroupsToItemGroup (data, uid) {
    return repository.post(`${resource}/item-groups/${uid}/activity-sub-groups?override=true`, data)
  },
  addActivitiesToItem (data, uid) {
    return repository.post(`${resource}/items/${uid}/activities?override=true`, data)
  },
  getXml (params) {
    return repository.post(`${resource}/metadata/xmls/export?target_uid=${params.target_uid}&target_type=${params.target_type}&export_to=${params.export_to}&stylesheet=${params.stylesheet}&status=${params.status}`)
  },
  getXsl (type) {
    return repository.get(`${resource}/metadata/xmls/stylesheets/${type}`)
  },
  getAllAliases (params) {
    return repository.get(`${resource}/aliases`, { params })
  },
  deleteAlias (uid) {
    return repository.delete(`${resource}/aliases/${uid}`)
  },
  addAlias (data) {
    return repository.post(`${resource}/aliases`, data)
  },
  editAlias (uid, data) {
    return repository.patch(`${resource}/aliases/${uid}`, data)
  },
  getDescriptions () {
    return repository.get(`${resource}/descriptions`)
  },
  getExpressions () {
    return repository.get(`${resource}/formal-expressions`)
  },
  createExpression (data) {
    return repository.post(`${resource}/formal-expressions`, data)
  },
  editExpression (uid, data) {
    return repository.patch(`${resource}/formal-expressions/${uid}`, data)
  },
  deleteExpression (uid) {
    return repository.delete(`${resource}/formal-expressions/${uid}`)
  },
  getConditionByOid (params) {
    return repository.get(`${resource}/conditions`, { params })
  },
  createCondition (data) {
    return repository.post(`${resource}/conditions`, data)
  },
  editCondition (uid, data) {
    return repository.patch(`${resource}/conditions/${uid}`, data)
  },
  deleteCondition (uid) {
    return repository.delete(`${resource}/conditions/${uid}`)
  },
  getFormRelationship (uid) {
    return repository.get(`${resource}/forms/${uid}/relationships`)
  },
  getGroupRelationship (uid) {
    return repository.get(`${resource}/item-groups/${uid}/relationships`)
  },
  getItemRelationship (uid) {
    return repository.get(`${resource}/items/${uid}/relationships`)
  },
  getCrfForms () {
    return repository.get(`${resource}/forms/templates`)
  },
  getCrfGroups () {
    return repository.get(`${resource}/item-groups/forms`)
  },
  getAllNamespaces (params) {
    return repository.get(`${resource}/vendor-namespaces`, { params })
  },
  getNamespace (uid) {
    return repository.get(`${resource}/vendor-namespaces/${uid}`)
  },
  createNamespace (data) {
    return repository.post(`${resource}/vendor-namespaces`, data)
  },
  deleteNamespace (uid) {
    return repository.delete(`${resource}/vendor-namespaces/${uid}`)
  },
  editNamespace (uid, data) {
    return repository.patch(`${resource}/vendor-namespaces/${uid}`, data)
  },
  getAllAttributes (params) {
    return repository.get(`${resource}/vendor-attributes`, { params })
  },
  createAttribute (data) {
    return repository.post(`${resource}/vendor-attributes`, data)
  },
  editAttribute (uid, data) {
    return repository.patch(`${resource}/vendor-attributes/${uid}`, data)
  },
  getAllElements (params) {
    return repository.get(`${resource}/vendor-elements`, { params })
  },
  createElement (data) {
    return repository.post(`${resource}/vendor-elements`, data)
  },
  setElements (source, uid, data) {
    return repository.post(`${resource}/${source}/${uid}/vendor-elements`, data)
  },
  setAttributes (source, uid, data) {
    return repository.post(`${resource}/${source}/${uid}/vendor-attributes`, data)
  },
  setElementAttributes (source, uid, data) {
    return repository.post(`${resource}/${source}/${uid}/vendor-element-attributes`, data)
  }
}
