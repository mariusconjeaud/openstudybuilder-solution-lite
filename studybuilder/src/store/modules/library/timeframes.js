import timeframes from '@/api/timeframes'

const state = {
  timeframes: []
}

const getters = {
  timeframes: state => state.timeframes
}

const mutations = {
  SET_TIMEFRAMES (state, timeframes) {
    state.timeframes = timeframes
  }
}

const actions = {
  fetchTimeframes ({ commit }) {
    return timeframes.get().then(resp => {
      commit('SET_TIMEFRAMES', resp.data.items)
    })
  },
  fetchFilteredTimeframes ({ commit }, data) {
    return timeframes.getFiltered(data).then(resp => {
      commit('SET_TIMEFRAMES', resp.data.items)
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
