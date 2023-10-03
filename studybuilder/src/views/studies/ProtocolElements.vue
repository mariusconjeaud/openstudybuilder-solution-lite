<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('StudyProtocolElementsView.title') }} ({{ studyId }})
    <help-button :help-text="$t('_help.ProtocolElementsTable.general')" />
  </div>
  <v-tabs v-model="tab">
    <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">{{ tab.name }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="tab-0">
      <protocol-title-page />
    </v-tab-item>
    <v-tab-item id="tab-1">
      <protocol-flowchart :study-uid="selectedStudy.uid"  :update="updateFlowchart" />
    </v-tab-item>
    <v-tab-item id="tab-2">
      <protocol-elements-objective-table :study-uid="selectedStudy.uid" :update="updateObjectives"/>
    </v-tab-item>
     <v-tab-item id="tab-3">
       <protocol-elements-study-design :study-uid="selectedStudy.uid" :update="updateDesign"/>
    </v-tab-item>
     <v-tab-item id="tab-4">
       <protocol-elements-study-population-summary />
    </v-tab-item>
     <v-tab-item id="tab-5">
       <protocol-elements-study-interventions :study-uid="selectedStudy.uid" :update="updateInterventions"/>
    </v-tab-item>
     <v-tab-item id="tab-6">
       <protocol-elements-procedures-and-activities />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import { studySelectedNavigationGuard } from '@/mixins/studies'
import ProtocolElementsObjectiveTable from '@/components/studies/ProtocolElementsObjectiveTable'
import ProtocolElementsStudyPopulationSummary from '@/components/studies/ProtocolElementsStudyPopulationSummary'
import ProtocolElementsStudyDesign from '@/components/studies/ProtocolElementsStudyDesign'
import ProtocolElementsStudyInterventions from '@/components/studies/ProtocolElementsStudyIntervention'
import ProtocolElementsProceduresAndActivities from '@/components/studies/ProtocolElementsProceduresAndActivities'
import ProtocolFlowchart from '@/components/studies/ProtocolFlowchart'
import ProtocolTitlePage from '@/components/studies/ProtocolTitlePage'
import HelpButton from '@/components/tools/HelpButton'
import { mapActions } from 'vuex'

export default {
  mixins: [studySelectedNavigationGuard],
  components: {
    ProtocolElementsObjectiveTable,
    ProtocolFlowchart,
    HelpButton,
    ProtocolTitlePage,
    ProtocolElementsStudyPopulationSummary,
    ProtocolElementsStudyDesign,
    ProtocolElementsStudyInterventions,
    ProtocolElementsProceduresAndActivities
  },
  data () {
    return {
      tab: null,
      updateFlowchart: 0,
      updateObjectives: 0,
      updateDesign: 0,
      updateInterventions: 0,
      tabs: [
        { tab: '#tab-0', name: this.$t('Sidebar.study.protocol_title') },
        { tab: '#tab-1', name: this.$t('StudyProtocolElementsView.protocol_soa') },
        { tab: '#tab-2', name: this.$t('Sidebar.study.objective_endpoints_estimands') },
        { tab: '#tab-3', name: this.$t('Sidebar.study.study_design') },
        { tab: '#tab-4', name: this.$t('Sidebar.study.study_population') },
        { tab: '#tab-5', name: this.$t('Sidebar.study.study_interventions_and_therapy') },
        { tab: '#tab-6', name: this.$t('Sidebar.study.study_activities') }
      ]
    }
  },
  mounted () {
    this.tab = localStorage.getItem('templatesTab') || 'tab-0'
    const tabName = this.tab ? this.tabs.find(el => el.tab.substring(1) === this.tab).name : this.tabs[0].name
    setTimeout(() => {
      this.addBreadcrumbsLevel({
        text: tabName,
        index: 3,
        replace: true
      })
    }, 100)
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    })
  },
  watch: {
    tab (value) {
      const tabName = value ? this.tabs.find(el => el.tab.substring(1) === value).name : this.tabs[0].name
      this.addBreadcrumbsLevel({
        text: tabName,
        index: 3,
        replace: true
      })
      localStorage.setItem('templatesTab', value)
      switch (value) {
        case 'tab-1':
          this.updateFlowchart++
          break
        case 'tab-2':
          this.updateObjectives++
          break
        case 'tab-3':
          this.updateDesign++
          break
        case 'tab-5':
          this.updateInterventions++
          break
      }
    }
  }
}
</script>
