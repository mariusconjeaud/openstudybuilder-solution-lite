<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('ActivitiesView.title') }} ({{ studyId }})
    <help-button-with-panels :title="$t('_global.help')" :items="helpItems" />
  </div>
  <v-tabs v-model="tab">
    <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">{{ tab.name }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="list">
      <study-activity-table
        />
    </v-tab-item>
    <v-tab-item id="instances">
      <under-construction />
    </v-tab-item>
    <v-tab-item id="detailed">
      <detailed-flowchart
        :update="updateFlowchart"
        :redirectFootnote="redirectFootnote"/>
    </v-tab-item>
    <v-tab-item id="footnotes">
      <study-footnote-table />
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
import StudyFootnoteTable from '@/components/studies/StudyFootnoteTable'
import { studySelectedNavigationGuard } from '@/mixins/studies'
import UnderConstruction from '@/components/layout/UnderConstruction'
import { mapActions } from 'vuex'
import HelpButtonWithPanels from '@/components/tools/HelpButtonWithPanels'

export default {
  mixins: [studySelectedNavigationGuard],
  components: {
    DetailedFlowchart,
    ProtocolFlowchart,
    StudyActivityInstructionTable,
    StudyActivityTable,
    StudyFootnoteTable,
    UnderConstruction,
    HelpButtonWithPanels
  },
  data () {
    return {
      instructionsKey: 0,
      tab: null,
      updateProtocol: 0,
      updateFlowchart: 0,
      tabs: [
        { tab: '#list', name: this.$t('ActivitiesView.tab1_title') },
        { tab: '#instances', name: this.$t('ActivitiesView.tab2_title') },
        { tab: '#detailed', name: this.$t('ActivitiesView.tab3_title') },
        { tab: '#footnotes', name: this.$t('ActivitiesView.tab4_title') },
        { tab: '#protocol', name: this.$t('ActivitiesView.tab5_title') },
        { tab: '#instructions', name: this.$t('ActivitiesView.tab6_title') }
      ],
      redirectFootnote: {},
      helpItems: [
        'StudyActivity.flowchart_group',
        'StudyActivity.activity_group',
        'StudyActivity.activity_sub_group',
        'StudyActivity.activity',
        'StudyActivity.data_collection',
        'StudyActivity.expand_all',
        'StudyActivity.collapse_all',
        'StudyActivity.hide_activity_selection',
        'StudyActivity.show_activity_selection',
        'StudyActivity.hide_flowchart_groups',
        'StudyActivity.edit_dialog_title',
        'StudyActivity.download_docx',
        'StudyActivity.instructions'
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
      if (newValue === 'detailed') {
        this.updateFlowchart++
        if (this.$route.params.footnote) {
          this.redirectFootnote = this.$route.params.footnote
        }
      }
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
