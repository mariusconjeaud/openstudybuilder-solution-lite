
const state = {
  filteringParams: Object
}

const getters = {
  filteringParams: state => state.filteringParams
}

const mutations = {
  INITIATE_FILTERING_PARAMS () {
    let filtersFromLocalStorage = {}
    if (localStorage.getItem('filteringParams') != null) {
      filtersFromLocalStorage = JSON.parse(localStorage.getItem('filteringParams'))
    }
    state.filteringParams = filtersFromLocalStorage
  },
  SET_FILTERING_PARAMS (state, params) {
    state.filteringParams = params
    localStorage.setItem('filteringParams', JSON.stringify(state.filteringParams))
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations
}
