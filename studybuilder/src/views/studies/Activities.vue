<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('ActivitiesView.title') }} ({{ studyId }})
  </div>
  <v-tabs v-model="tab">
    <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">{{ tab.name }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="list">
      <study-activity-table
        />
    </v-tab-item>
    <v-tab-item id="detailed">
      <detailed-flowchart
        :update="updateFlowchart"/>
    </v-tab-item>
    <v-tab-item id="protocol">
      <protocol-flowchart :study-uid="selectedStudy.uid" :update="updateProtocol" />
    </v-tab-item>
    <v-tab-item id="instructions">
      <study-activity-instruction-table :key="instructionsKey" />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import DetailedFlowchart from '@/components/studies/DetailedFlowchart'
import ProtocolFlowchart from '@/components/studies/ProtocolFlowchart'
import StudyActivityInstructionTable from '@/components/studies/StudyActivityInstructionTable'
import StudyActivityTable from '@/components/studies/StudyActivityTable'
import { studySelectedNavigationGuard } from '@/mixins/studies'
import { mapActions } from 'vuex'

export default {
  mixins: [studySelectedNavigationGuard],
  components: {
    DetailedFlowchart,
    ProtocolFlowchart,
    StudyActivityInstructionTable,
    StudyActivityTable
  },
  data () {
    return {
      instructionsKey: 0,
      tab: null,
      updateProtocol: 0,
      updateFlowchart: 0,
      tabs: [
        { tab: '#list', name: this.$t('ActivitiesView.tab1_title') },
        { tab: '#detailed', name: this.$t('ActivitiesView.tab2_title') },
        { tab: '#protocol', name: this.$t('ActivitiesView.tab3_title') },
        { tab: '#instructions', name: this.$t('ActivitiesView.tab4_title') }
      ]
    }
  },
  mounted () {
    this.tab = this.$route.params.tab
    const tabName = this.tab ? this.tabs.find(el => el.tab.substring(1) === this.tab).name : this.tabs[0].name
    setTimeout(() => {
      this.addBreadcrumbsLevel({
        text: tabName,
        to: { name: 'StudyProperties', params: { tab: tabName } },
        index: 3,
        replace: true
      })
    }, 100)
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    }),
    refreshInstructions () {
      this.instructionsKey++
    }
  },
  watch: {
    tab (newValue) {
      const tabName = newValue ? this.tabs.find(el => el.tab.substring(1) === newValue).name : this.tabs[0].name
      this.$router.push({
        name: 'StudyActivities',
        params: { tab: newValue }
      })
      this.addBreadcrumbsLevel({
        text: tabName,
        to: { name: 'StudyProperties', params: { tab: tabName } },
        index: 3,
        replace: true
      })
      if (newValue === 'protocol') this.updateProtocol++
      if (newValue === 'detailed') this.updateFlowchart++
      if (newValue === 'instructions') this.refreshInstructions()
    },
    /*
    ** Non optimal way to allow direct links (ie. a tags with href set to a tab url)
    ** It could create a loop with the above watcher but it works because routes are the same
    ** eventually.
    */
    '$route.params.tab' (newValue) {
      this.tab = newValue
    }
  }
}
</script>
