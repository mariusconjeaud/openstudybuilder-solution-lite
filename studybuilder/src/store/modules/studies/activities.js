import study from '@/api/study'
import Vue from 'vue'

const state = {
  studyActivities: []
}

const getters = {
  studyActivities: state => state.studyActivities,
  sortedStudyActivities: state => {
    const result = {}
    for (const studyActivity of state.studyActivities) {
      const fgroup = studyActivity.study_soa_group.soa_group_name
      if (!result[fgroup]) {
        Vue.set(result, fgroup, {})
      }
      const group = studyActivity.study_activity_group && studyActivity.study_activity_group.activity_group_name ? studyActivity.study_activity_group.activity_group_name : '(not selected)'
      const subgroup = studyActivity.study_activity_subgroup && studyActivity.study_activity_subgroup.activity_subgroup_name ? studyActivity.study_activity_subgroup.activity_subgroup_name : '(not selected)'
      if (!result[fgroup][group]) {
        Vue.set(result[fgroup], group, {})
      }
      if (!result[fgroup][group][subgroup]) {
        Vue.set(result[fgroup][group], subgroup, [])
      }
      result[fgroup][group][subgroup].push(studyActivity)
    }
    return result
  }
}

const mutations = {
  SET_STUDY_ACTIVITIES (state, studyActivities) {
    state.studyActivities = studyActivities
  },
  UPDATE_STUDY_ACTIVITY (state, studyActivity) {
    state.studyActivities.filter((item, pos) => {
      if (item.study_activity_uid === studyActivity.study_activity_uid) {
        Vue.set(state.studyActivities, pos, studyActivity)
      }
    })
  }
}

const actions = {
  async fetchStudyActivities ({ commit }, params) {
    const studyUid = params.studyUid
    delete params.studyUid
    if (!Object.prototype.hasOwnProperty.call(params, 'page_size')) {
      params.page_size = 0
    }
    if (!Object.prototype.hasOwnProperty.call(params, 'page_number')) {
      params.page_number = 1
    }
    const resp = await study.getStudyActivities(studyUid, params)
    commit('SET_STUDY_ACTIVITIES', resp.data.items)
    return resp
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
