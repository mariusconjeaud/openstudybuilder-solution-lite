
const state = {
  columns: Object
}

const getters = {
  columns: state => state.columns
}

const mutations = {
  INITIATE_COLUMNS () {
    let columnsFromLocalStorage = {}
    if (localStorage.getItem('columns') != null) {
      columnsFromLocalStorage = JSON.parse(localStorage.getItem('columns'))
    }
    state.columns = columnsFromLocalStorage
  },
  SET_COLUMNS (state, columns) {
    for (const [key, value] of columns) {
      state.columns[key] = value
    }
    localStorage.setItem('columns', JSON.stringify(state.columns))
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations
}
