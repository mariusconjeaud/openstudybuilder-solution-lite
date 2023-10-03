import footnotes from '@/api/footnotes'

const state = {
  footnotes: []
}

const getters = {
  footnotes: state => state.footnotes
}

const mutations = {
  SET_FOOTNOTES (state, footnotes) {
    state.footnotes = footnotes
  }
}

const actions = {
  fetchFootnotes ({ commit }) {
    return footnotes.get().then(resp => {
      commit('SET_FOOTNOTES', resp.data.items)
    })
  },
  fetchFilteredFootnotes ({ commit }, data) {
    return footnotes.getFiltered(data).then(resp => {
      commit('SET_FOOTNOTES', resp.data.items)
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
