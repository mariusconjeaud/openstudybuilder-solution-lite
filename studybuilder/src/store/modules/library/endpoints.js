import endpoints from '@/api/endpoints'

const state = {
  endpoints: []
}

const getters = {
  endpoints: state => state.endpoints
}

const mutations = {
  SET_ENDPOINTS (state, endpoints) {
    state.endpoints = endpoints
  }
}

const actions = {
  fetchEndpoints ({ commit }) {
    return endpoints.get().then(resp => {
      commit('SET_ENDPOINTS', resp.data.items)
    })
  },
  fetchFilteredEndpoints ({ commit }, data) {
    return endpoints.getFiltered(data).then(resp => {
      commit('SET_ENDPOINTS', resp.data.items)
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
