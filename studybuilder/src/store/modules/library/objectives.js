import objectives from '@/api/objectives'

const state = {
  objectives: []
}

const getters = {
  objectives: state => state.objectives
}

const mutations = {
  SET_OBJECTIVES (state, objectives) {
    state.objectives = objectives
  }
}

const actions = {
  fetchObjectives ({ commit }) {
    return objectives.get().then(resp => {
      commit('SET_OBJECTIVES', resp.data.items)
    })
  },
  fetchFilteredObjectives ({ commit }, data) {
    return objectives.getFiltered(data).then(resp => {
      commit('SET_OBJECTIVES', resp.data.items)
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
