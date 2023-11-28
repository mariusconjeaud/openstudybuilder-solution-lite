import { mapGetters } from 'vuex'
import store from '@/store'

export const studySelectedNavigationGuard = {

  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion'
    }),
    studyId () {
      const studyNumber = this.selectedStudy.current_metadata.identification_metadata.study_number
      return (studyNumber !== undefined && studyNumber !== null)
        ? this.selectedStudy.current_metadata.identification_metadata.study_id : this.selectedStudy.current_metadata.identification_metadata.study_acronym
    }
  },

  /*
  ** Check if target route requires a selected study or not.
  */
  async beforeRouteEnter (to, from, next) {
    if (to.meta && to.meta.studyRequired && !store.state.studiesGeneral.selectedStudy) {
      if (from.name === 'AuthCallback') {
        // Special case for after-login process
        next({ name: 'SelectOrAddStudy' })
      } else {
        next(false)
      }
    } else {
      next()
    }
  }
}
