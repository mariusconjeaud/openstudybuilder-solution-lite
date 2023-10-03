import Vue from 'vue'
import Vuex from 'vuex'

import app from '@/store/modules/app'
import auth from '@/store/modules/auth'
import form from '@/store/modules/form'

// Library modules
import objectives from '@/store/modules/library/objectives'
import endpoints from '@/store/modules/library/endpoints'
import footnotes from '@/store/modules/library/footnotes'
import timeframes from '@/store/modules/library/timeframes'
import criteria from '@/store/modules/library/criteria'
import activityInstructions from '@/store/modules/library/activityInstructions'
import ctCatalogues from '@/store/modules/library/ctCatalogues'
import tablesLayout from '@/store/modules/library/tablesLayout'
import units from '@/store/modules/library/units'
import compounds from './modules/library/compounds'
import crfs from './modules/library/crfs'

// Studies modules
import studiesGeneral from '@/store/modules/studies/general'
import manageStudies from '@/store/modules/studies/manage'
import studyObjectives from '@/store/modules/studies/objectives'
import studyCompounds from './modules/studies/compounds'
import studyEndpoints from './modules/studies/endpoints'
import studyEpochs from './modules/studies/epochs'
import studyActivities from './modules/studies/activities'
import studyFootnotes from './modules/studies/footnotes'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    app,
    auth,
    objectives,
    timeframes,
    endpoints,
    footnotes,
    criteria,
    activityInstructions,
    compounds,
    ctCatalogues,
    units,
    studiesGeneral,
    manageStudies,
    studyObjectives,
    studyCompounds,
    studyEndpoints,
    studyEpochs,
    studyActivities,
    studyFootnotes,
    tablesLayout,
    form,
    crfs
  }
})
