import timeframes from '@/api/timeframes'

const state = {
  timeframes: [],
  total: 0
}

const getters = {
  timeframes: state => state.timeframes,
  total: state => state.total
}

const mutations = {
  SET_TIMEFRAMES (state, timeframes) {
    state.timeframes = timeframes.items
    state.total = timeframes.total
  }
}

const actions = {
  fetchTimeframes ({ commit }) {
    return timeframes.get().then(resp => {
      commit('SET_TIMEFRAMES', resp.data)
    })
  },
  fetchFilteredTimeframes ({ commit }, data) {
    return timeframes.getFiltered(data).then(resp => {
      commit('SET_TIMEFRAMES', resp.data)
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
