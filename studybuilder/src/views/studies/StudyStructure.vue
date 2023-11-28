<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('Sidebar.study.study_structure') }} ({{ studyId }})
    <help-button-with-panels
      :help-text="$t('_help.StudyStructure.general')"
      :items="helpItems"
      />

  </div>
  <v-tabs v-model="tab">
    <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">{{ tab.name }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="overview">
      <study-structure-overview :key="overviewKey" />
    </v-tab-item>
    <v-tab-item id="arms">
      <study-arms-table />
    </v-tab-item>
    <v-tab-item id="branches">
      <study-branches-table />
    </v-tab-item>
    <v-tab-item id="cohorts">
      <study-cohorts-table />
    </v-tab-item>
    <v-tab-item id="epochs">
      <study-epoch-table />
    </v-tab-item>
    <v-tab-item id="elements">
      <study-elements-table />
    </v-tab-item>
    <v-tab-item id="visits">
      <study-visit-table />
    </v-tab-item>
    <v-tab-item id="design_matrix">
      <design-matrix-table :refresh="key"/>
    </v-tab-item>
    <v-tab-item id="disease_milestones">
      <disease-milestone-table />
    </v-tab-item>
  </v-tabs-items>
  <comment-thread-list :topicPath="topicPath" :isTransparent="true"></comment-thread-list>
</div>
</template>

<script>
import DesignMatrixTable from '@/components/studies/DesignMatrixTable'
import DiseaseMilestoneTable from '@/components/studies/DiseaseMilestoneTable'
import HelpButtonWithPanels from '@/components/tools/HelpButtonWithPanels'
import { studySelectedNavigationGuard } from '@/mixins/studies'
import StudyEpochTable from '@/components/studies/StudyEpochTable'
import StudyArmsTable from '@/components/studies/StudyArmsTable'
import StudyBranchesTable from '@/components/studies/StudyBranchesTable'
import StudyVisitTable from '@/components/studies/StudyVisitTable'
import StudyElementsTable from '@/components/studies/StudyElementsTable'
import StudyCohortsTable from '@/components/studies/StudyCohortsTable'
import StudyStructureOverview from '@/components/studies/StudyStructureOverview'
import { mapActions } from 'vuex'
import CommentThreadList from '@/components/tools/CommentThreadList'

export default {
  mixins: [studySelectedNavigationGuard],
  components: {
    DiseaseMilestoneTable,
    HelpButtonWithPanels,
    StudyVisitTable,
    StudyEpochTable,
    StudyArmsTable,
    DesignMatrixTable,
    StudyElementsTable,
    StudyBranchesTable,
    StudyCohortsTable,
    CommentThreadList,
    StudyStructureOverview
  },
  data () {
    return {
      helpItems: [
        'StudyStructure.study_arms',
        'StudyStructure.study_branches',
        'StudyStructure.study_cohorts',
        'StudyStructure.study_epochs',
        'StudyStructure.study_elements',
        'StudyStructure.study_visits',
        'StudyStructure.design_matrix',
        'StudyStructure.edit_visit_tableview'
      ],
      key: 0,
      overviewKey: 0,
      topicPath: '',
      tab: null,
      tabs: [
        { tab: '#overview', name: this.$t('_global.overview') },
        { tab: '#arms', name: this.$t('Sidebar.study.study_arms') },
        { tab: '#branches', name: this.$t('Sidebar.study.study_branches') },
        { tab: '#cohorts', name: this.$t('Sidebar.study.study_cohorts') },
        { tab: '#epochs', name: this.$t('Sidebar.study.study_epochs') },
        { tab: '#elements', name: this.$t('Sidebar.study.study_elements') },
        { tab: '#visits', name: this.$t('Sidebar.study.study_visits') },
        { tab: '#design_matrix', name: this.$t('Sidebar.study.design_matrix') },
        { tab: '#disease_milestones', name: this.$t('Sidebar.study.disease_milestones') }
      ]
    }
  },
  mounted () {
    this.tab = this.$route.params.tab
    const tabName = this.tab ? this.tabs.find(el => el.tab.substring(1) === this.tab).name : this.tabs[0].name
    setTimeout(() => {
      this.addBreadcrumbsLevel({
        text: tabName,
        to: { name: 'StudyStructure', params: { tab: tabName } },
        index: 3,
        replace: true
      })
    }, 100)
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    }),
    refreshMatrix () {
      this.key += 1
    },
    refreshOverview () {
      this.overviewKey += 1
    }
  },
  watch: {
    tab (newValue) {
      if (newValue !== undefined) {
        this.topicPath = '/studies/' + this.selectedStudy.uid + '/study_structure/' + newValue
      }
      if (newValue === 'overview') this.refreshOverview()
      if (newValue === 'design_matrix') this.refreshMatrix()
      const tabName = newValue ? this.tabs.find(el => el.tab.substring(1) === newValue).name : this.tabs[0].name
      this.$router.push({
        name: 'StudyStructure',
        params: { tab: newValue }
      })
      this.addBreadcrumbsLevel({
        text: tabName,
        to: { name: 'StudyProperties', params: { tab: tabName } },
        index: 3,
        replace: true
      })
    },
    '$route.params.tab' (newValue) {
      this.tab = newValue
    }
  }
}
</script>
