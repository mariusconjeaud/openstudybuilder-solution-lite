import { mapGetters } from 'vuex'
import store from '@/store'

export const studySelectedNavigationGuard = {

  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    studyId () {
      return (this.selectedStudy.study_number !== undefined && this.selectedStudy.study_number !== null)
        ? this.selectedStudy.study_id : this.selectedStudy.study_acronym
    }
  },

  /*
  ** Check if target route requires a selected study or not.
  */
  async beforeRouteEnter (to, from, next) {
    if (to.meta && to.meta.studyRequired && !store.state.studiesGeneral.selectedStudy) {
      next(false)
    } else {
      next()
    }
  }
}
