import activityInstructions from '@/api/activityInstructions'

const state = {
  activityInstructions: [],
  total: 0
}

const getters = {
  activityInstructions: state => state.activityInstructions,
  total: state => state.total
}

const mutations = {
  SET_ACTIVITY_INSTRUCTIONS (state, activityInstructions) {
    state.activityInstructions = activityInstructions.items
    state.total = activityInstructions.total
  }
}

const actions = {
  fetchActivityInstructions ({ commit }) {
    return activityInstructions.get().then(resp => {
      commit('SET_ACTIVITY_INSTRUCTIONS', resp.data)
    })
  },
  fetchFilteredActivityInstructions ({ commit }, data) {
    return activityInstructions.getFiltered(data).then(resp => {
      commit('SET_ACTIVITY_INSTRUCTIONS', resp.data)
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
