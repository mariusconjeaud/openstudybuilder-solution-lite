import objectives from '@/api/objectives'

const state = {
  objectives: [],
  total: 0
}

const getters = {
  objectives: state => state.objectives,
  total: state => state.total
}

const mutations = {
  SET_OBJECTIVES (state, objectives) {
    state.objectives = objectives.items
    state.total = objectives.total
  }
}

const actions = {
  fetchObjectives ({ commit }) {
    return objectives.get().then(resp => {
      commit('SET_OBJECTIVES', resp.data)
    })
  },
  fetchFilteredObjectives ({ commit }, data) {
    return objectives.getFiltered(data).then(resp => {
      commit('SET_OBJECTIVES', resp.data)
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
