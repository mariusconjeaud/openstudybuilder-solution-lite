import criteria from '@/api/criteria'

const state = {
  criteria: [],
  total: 0
}

const getters = {
  criteria: state => state.criteria,
  total: state => state.total
}

const mutations = {
  SET_CRITERIA (state, criteria) {
    state.criteria = criteria.items
    state.total = criteria.total
  }
}

const actions = {
  fetchFilteredCriteria ({ commit }, data) {
    return criteria.getFiltered(data).then(resp => {
      commit('SET_CRITERIA', resp.data)
    })
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
