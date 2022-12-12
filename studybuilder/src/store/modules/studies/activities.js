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
      const fgroup = studyActivity.flowchart_group.sponsor_preferred_name
      if (!result[fgroup]) {
        Vue.set(result, fgroup, {})
      }
      const group = (studyActivity.activity.activity_group)
        ? studyActivity.activity.activity_group.name : ''
      const subgroup = (studyActivity.activity.activity_subgroup)
        ? studyActivity.activity.activity_subgroup.name : ''
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
  fetchStudyActivities ({ commit }, params) {
    const studyUid = params.studyUid
    delete params.studyUid
    if (!Object.prototype.hasOwnProperty.call(params, 'page_size')) {
      params.page_size = 0
    }
    if (!Object.prototype.hasOwnProperty.call(params, 'page_number')) {
      params.page_number = 1
    }
    return study.getStudyActivities(studyUid, params).then(resp => {
      commit('SET_STUDY_ACTIVITIES', resp.data.items)
      return resp
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
