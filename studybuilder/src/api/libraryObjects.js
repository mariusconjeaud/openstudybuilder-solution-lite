import repository from './repository'

export default (basePath) => {
  return {
    get (status) {
      const params = {
        page_size: 0
      }
      if (status) {
        params.status = status
      }
      return repository.get(`${basePath}`, { params })
    },
    getFiltered (params) {
      return repository.get(`${basePath}`, { params })
    },
    getObject (uid) {
      return repository.get(`${basePath}/${uid}`)
    },
    getObjectByName (name) {
      const params = {
        page_size: 0,
        filters: {
          name: {
            v: [name],
            op: 'eq'
          }
        }
      }
      return repository.get(`${basePath}`, { params })
    },
    getObjectParameters (uid, params) {
      return repository.get(`${basePath}/${uid}/parameters`, { params })
    },
    getVersions (uid) {
      return repository.get(`${basePath}/${uid}/versions`)
    },
    create (data) {
      return repository.post(`${basePath}`, data)
    },
    update (uid, data) {
      return repository.patch(`${basePath}/${uid}`, data)
    },
    deleteObject (uid) {
      return repository.delete(`${basePath}/${uid}`)
    },
    approve (uid) {
      return repository.post(`${basePath}/${uid}/approve`)
    },
    inactivate (uid) {
      return repository.post(`${basePath}/${uid}/inactivate`)
    },
    reactivate (uid) {
      return repository.post(`${basePath}/${uid}/reactivate`)
    },
    newVersion (uid) {
      return repository.post(`${basePath}/${uid}/versions`)
    }
  }
}
