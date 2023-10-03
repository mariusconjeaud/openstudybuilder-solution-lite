import endpoints from '@/api/endpoints'

const state = {
  endpoints: [],
  total: 0
}

const getters = {
  endpoints: state => state.endpoints,
  total: state => state.total
}

const mutations = {
  SET_ENDPOINTS (state, endpoints) {
    state.endpoints = endpoints.items
    state.total = endpoints.total
  }
}

const actions = {
  fetchEndpoints ({ commit }) {
    return endpoints.get().then(resp => {
      commit('SET_ENDPOINTS', resp.data)
    })
  },
  fetchFilteredEndpoints ({ commit }, data) {
    return endpoints.getFiltered(data).then(resp => {
      commit('SET_ENDPOINTS', resp.data)
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
