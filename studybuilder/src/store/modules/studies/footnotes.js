import Vue from 'vue'
import footnotes from '@/api/footnotes'
import study from '@/api/study'
import instances from '@/utils/instances'
import utils from '@/store/utils'

const state = {
  studyFootnotes: [],
  total: 0
}

const getters = {
  studyFootnotes: state => state.studyFootnotes,
  total: state => state.total
}

const mutations = {
  SET_STUDY_FOOTNOTES (state, studyFootnotes) {
    state.studyFootnotes = studyFootnotes.items
    state.total = studyFootnotes.total
  },
  ADD_STUDY_OBJECTIVE (state, studyObjective) {
    state.studyFootnotes.unshift(studyObjective)
  },
  UPDATE_STUDY_OBJECTIVE (state, studyObjective) {
    state.studyFootnotes.filter((item, pos) => {
      if (item.study_objective_uid === studyObjective.study_objective_uid) {
        Vue.set(state.studyFootnotes, pos, studyObjective)
        return true
      }
      return false
    })
  },
  REMOVE_STUDY_FOOTNOTE (state, studyFootnoteUid) {
    state.studyFootnotes = state.studyFootnotes.filter(function (item) {
      return item.study_footnote_uid !== studyFootnoteUid
    })
  }
}

const actions = {
  fetchStudyFootnotes ({ commit }, data) {
    const studyUid = data.studyUid
    delete data.studyUid
    return study.getStudyFootnotes(studyUid, data).then(resp => {
      commit('SET_STUDY_FOOTNOTES', resp.data)
      return resp
    })
  },
  /*
  ** Create a study footnote based on an footnote template. We fist
  ** look if an footnote already exists for the provided name. If so,
  ** we select it, otherwise we create a new footnote in Final state
  ** and select if.
  */
  async addStudyFootnoteFromTemplate ({ commit, dispatch }, { studyUid, form, parameters }) {
    const footnote = {
      footnote_template_uid: form.footnote_template.uid,
      parameter_terms: await instances.formatParameterValues(parameters),
      library_name: form.footnote_template.library.name
    }
    const data = {
      footnote_data: footnote
    }
    return study.createStudyFootnote(studyUid, data, true)
  },
  addStudyFootnote ({ commit, dispatch }, { studyUid, footnoteUid, footnoteLevelUid }) {
    return study.selectStudyFootnote(studyUid, footnoteUid, footnoteLevelUid)
  },
  async updateStudyFootnote ({ commit, dispatch }, { studyUid, studyFootnoteUid, form, template, library }) {
    const data = {}
    let footnoteUid = null

    // Search for an existing footnote by name
    const searchName = await utils.getInternalApiName(template.name, form.parameters)
    const response = await footnotes.getObjectByName(searchName)
    if (response.data.items.length && response.data.items.length > 0) {
      footnoteUid = response.data.items[0].uid
    } else {
      // Create footnote since an footnote with specified name does not exist
      const footnote = {
        footnote_template_uid: template.uid,
        parameter_terms: form.parameters ? await instances.formatParameterValues(form.parameters) : [],
        library_name: library.name
      }
      const resp = await footnotes.create(footnote)
      footnoteUid = resp.data.uid
      await footnotes.approve(footnoteUid)
    }
    data.footnote_uid = footnoteUid
    await study.updateStudyFootnote(studyUid, studyFootnoteUid, data)
  },
  async updateStudyFootnoteLatestVersion ({ commit }, { studyUid, studyFootnoteUid }) {
    const resp = await study.updateStudyFootnoteLatestVersion(
      studyUid, studyFootnoteUid
    )
    commit('UPDATE_STUDY_FOOTNOTE', resp.data)
  },
  async updateStudyFootnoteAcceptVersion ({ commit }, { studyUid, studyFootnoteUid }) {
    const resp = await study.updateStudyFootnoteAcceptVersion(
      studyUid, studyFootnoteUid
    )
    commit('UPDATE_STUDY_FOOTNOTE', resp.data)
  },
  deleteStudyFootnote ({ commit }, { studyUid, studyFootnoteUid }) {
    return study.deleteStudyFootnote(studyUid, studyFootnoteUid).then(resp => {
      commit('REMOVE_STUDY_FOOTNOTE', studyFootnoteUid)
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
