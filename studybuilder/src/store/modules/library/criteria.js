import criteria from '@/api/criteria'

const state = {
  criteria: []
}

const getters = {
  criteria: state => state.criteria
}

const mutations = {
  SET_CRITERIA (state, criteria) {
    state.criteria = criteria
  }
}

const actions = {
  fetchFilteredCriteria ({ commit }, data) {
    return criteria.getFiltered(data).then(resp => {
      commit('SET_CRITERIA', resp.data.items)
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
