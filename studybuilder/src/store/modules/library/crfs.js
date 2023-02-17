import crfs from '@/api/crfs'

const state = {
  templates: [],
  totalTemplates: 0,
  forms: [],
  totalForms: 0,
  itemGroups: [],
  totalItemGroups: 0,
  items: [],
  totalItems: 0
}

const getters = {
  templates: state => state.templates,
  totalTemplates: state => state.totalTemplates,
  forms: state => state.forms,
  totalForms: state => state.totalForms,
  itemGroups: state => state.itemGroups,
  totalItemGroups: state => state.totalItemGroups,
  items: state => state.items,
  totalItems: state => state.totalItems
}

const mutations = {
  SET_TEMPLATES (state, templates) {
    state.templates = templates
  },
  SET_TOTAL_TEMPLATES (state, totalTemplates) {
    state.totalTemplates = totalTemplates
  },
  SET_FORMS (state, forms) {
    state.forms = forms
  },
  SET_TOTAL_FORMS (state, totalForms) {
    state.totalForms = totalForms
  },
  SET_ITEM_GROUPS (state, itemGroups) {
    state.itemGroups = itemGroups
  },
  SET_TOTAL_ITEM_GROUPS (state, totalItemGroups) {
    state.totalItemGroups = totalItemGroups
  },
  SET_ITEMS (state, items) {
    state.items = items
  },
  SET_TOTAL_ITEMS (state, totalItems) {
    state.totalItems = totalItems
  }
}

const actions = {
  fetchTemplates ({ commit }, params) {
    return crfs.get('templates', { params }).then(resp => {
      commit('SET_TEMPLATES', resp.data.items)
      commit('SET_TOTAL_TEMPLATES', resp.data.total)
    })
  },
  setTemplates ({ commit }) {
    commit('SET_TEMPLATES', [])
  },
  fetchForms ({ commit }, params) {
    return crfs.get('forms', { params }).then(resp => {
      commit('SET_FORMS', resp.data.items)
      commit('SET_TOTAL_FORMS', resp.data.total)
    })
  },
  fetchItemGroups ({ commit }, params) {
    return crfs.get('item-groups', { params }).then(resp => {
      commit('SET_ITEM_GROUPS', resp.data.items)
      commit('SET_TOTAL_ITEM_GROUPS', resp.data.total)
    })
  },
  fetchItems ({ commit }, params) {
    return crfs.get('items', { params }).then(resp => {
      commit('SET_ITEMS', resp.data.items)
      commit('SET_TOTAL_ITEMS', resp.data.total)
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
