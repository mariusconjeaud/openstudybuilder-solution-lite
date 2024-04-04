import Vue from 'vue'
import objectives from '@/api/objectives'
import study from '@/api/study'
import instances from '@/utils/instances'
import utils from '@/store/utils'

const state = {
  studyObjectives: [],
  total: 0
}

const getters = {
  studyObjectives: state => state.studyObjectives,
  total: state => state.total
}

const mutations = {
  SET_STUDY_OBJECTIVES (state, studyObjectives) {
    state.studyObjectives = studyObjectives.items
    state.total = studyObjectives.total
  },
  ADD_STUDY_OBJECTIVE (state, studyObjective) {
    state.studyObjectives.unshift(studyObjective)
  },
  UPDATE_STUDY_OBJECTIVE (state, studyObjective) {
    state.studyObjectives.filter((item, pos) => {
      if (item.study_objective_uid === studyObjective.study_objective_uid) {
        Vue.set(state.studyObjectives, pos, studyObjective)
        return true
      }
      return false
    })
  },
  REMOVE_STUDY_OBJECTIVE (state, studyObjectiveUid) {
    state.studyObjectives = state.studyObjectives.filter(function (item) {
      return item.study_objective_uid !== studyObjectiveUid
    })
  }
}

const actions = {
  fetchStudyObjectives ({ commit }, data) {
    const studyUid = data.studyUid
    delete data.studyUid
    return study.getStudyObjectives(studyUid, data).then(resp => {
      commit('SET_STUDY_OBJECTIVES', resp.data)
      return resp
    })
  },
  /*
  ** Create a study objective based on an objective template. We fist
  ** look if an objective already exists for the provided name. If so,
  ** we select it, otherwise we create a new objective in Final state
  ** and select if.
  */
  async addStudyObjectiveFromTemplate ({ commit, dispatch }, { studyUid, form, parameters }) {
    const objective = {
      objective_template_uid: form.objective_template.uid,
      parameter_terms: await instances.formatParameterValues(parameters),
      library_name: form.objective_template.library.name
    }
    const objectiveLevelUid = (form.objective_level) ? form.objective_level.term_uid : undefined
    const data = {
      objective_level_uid: objectiveLevelUid,
      objective_data: objective
    }
    return study.createStudyObjective(studyUid, data)
  },
  addStudyObjective ({ commit, dispatch }, { studyUid, objectiveUid, objectiveLevelUid }) {
    return study.selectStudyObjective(studyUid, objectiveUid, objectiveLevelUid)
  },
  async updateStudyObjective ({ commit, dispatch }, { studyUid, studyObjectiveUid, form, template, library }) {
    const data = {}
    if (form.objective_level !== undefined) {
      if (form.objective_level === null) {
        data.objective_level_uid = null
      } else {
        data.objective_level_uid = form.objective_level.term_uid
      }
    }
    if (form.parameters !== undefined) {
      let objectiveUid = null

      // Search for an existing objective by name
      const searchName = utils.getInternalApiName(template.name, form.parameters)
      const response = await objectives.getObjectByName(searchName)
      if (response.data.items.length) {
        objectiveUid = response.data.items[0].uid
      } else {
        // Create objective since an objective with specified name does not exist
        const objective = {
          objective_template_uid: template.uid,
          parameter_terms: await instances.formatParameterValues(form.parameters),
          library_name: library.name
        }
        const resp = await objectives.create(objective)
        objectiveUid = resp.data.uid
        await objectives.approve(objectiveUid)
      }
      data.objective_uid = objectiveUid
    }
    await study.updateStudyObjective(studyUid, studyObjectiveUid, data)
  },
  async updateStudyObjectiveLatestVersion ({ commit }, { studyUid, studyObjectiveUid }) {
    const resp = await study.updateStudyObjectiveLatestVersion(
      studyUid, studyObjectiveUid
    )
    commit('UPDATE_STUDY_OBJECTIVE', resp.data)
  },
  async updateStudyObjectiveAcceptVersion ({ commit }, { studyUid, studyObjectiveUid }) {
    const resp = await study.updateStudyObjectiveAcceptVersion(
      studyUid, studyObjectiveUid
    )
    commit('UPDATE_STUDY_OBJECTIVE', resp.data)
  },
  deleteStudyObjective ({ commit }, { studyUid, studyObjectiveUid }) {
    return study.deleteStudyObjective(studyUid, studyObjectiveUid).then(resp => {
      commit('REMOVE_STUDY_OBJECTIVE', studyObjectiveUid)
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
