import repository from './repository'

const resource = 'concepts/activities'

export default {
  get (options, source) {
    const params = {
      ...options
    }
    return repository.get(`${resource}/${source}`, { params })
  },
  getObjectOverview (source, uid, format) {
    const options = {}
    if (format === 'yaml') {
      options.headers = {
        Accept: 'application/x-yaml'
      }
    }
    return repository.get(`${resource}/${source}/${uid}/overview`, options)
  },
  inactivate (uid, source) {
    return repository.delete(`${resource}/${source}/${uid}/activations`)
  },
  reactivate (uid, source) {
    return repository.post(`${resource}/${source}/${uid}/activations`)
  },
  delete (uid, source) {
    return repository.delete(`${resource}/${source}/${uid}`)
  },
  approve (uid, source) {
    return repository.post(`${resource}/${source}/${uid}/approvals`)
  },
  newVersion (uid, source) {
    return repository.post(`${resource}/${source}/${uid}/versions`)
  },
  getCompounds () {
    return repository.get(`${resource}/compounds`)
  },
  getHeaderData (options) {
    const params = {
      ...options
    }
    return repository.get(`${resource}/headers`, { params })
  },
  getGroups (params) {
    return repository.get(`${resource}/activity-groups`, { params })
  },
  getSubGroups (group) {
    const params = {
      activity_group_uid: group,
      page_size: 0,
      sort_by: { name: true }
    }
    return repository.get(`${resource}/activity-sub-groups`, { params })
  },
  getAllGroups (options) {
    const params = {
      ...options
    }
    return repository.get(`${resource}/activity-groups`, { params })
  },
  getAllSubGroups (options) {
    const params = {
      ...options
    }
    return repository.get(`${resource}/activity-sub-groups`, { params })
  },
  getSubGroupActivities (group) {
    const params = {
      activity_subgroup_uid: group,
      page_size: 0,
      sort_by: { name: true }
    }
    return repository.get(`${resource}/activities`, { params })
  },
  create (data, source) {
    const params = {
      ...data
    }
    return repository.post(`${resource}/${source}`, params)
  },
  update (uid, data, source) {
    const params = {
      ...data
    }
    return repository.patch(`${resource}/${source}/${uid}`, params)
  },
  createFromActivityRequest (data) {
    return repository.post(`${resource}/activities/sponsor-activities`, data)
  }
}
