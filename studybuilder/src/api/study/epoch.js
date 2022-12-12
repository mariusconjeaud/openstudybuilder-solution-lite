import repository from '../repository'

const resource = 'studies'

export default {
  getAll (studyUid) {
    return repository.get(`${resource}/${studyUid}/study-epochs`, { params: {page_size: 0}})
  },
  create (studyUid, data) {
    return repository.post(`${resource}/${studyUid}/study-epochs`, data)
  }
}
