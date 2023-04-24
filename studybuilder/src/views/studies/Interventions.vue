<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('Sidebar.study.study_interventions') }} ({{ studyId }})
    <help-button :help-text="$t('_help.StudyInterventionsTable.general')" />
  </div>
  <v-tabs v-model="tab">
    <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">{{ tab.name }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="overview">
      <intervention-overview />
    </v-tab-item>
    <v-tab-item id="study_compounds">
      <compound-table />
    </v-tab-item>
    <v-tab-item id="study_compound_dosings">
      <compound-dosing-table />
    </v-tab-item>
    <v-tab-item id="other_interventions">
      <UnderConstruction />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import { studySelectedNavigationGuard } from '@/mixins/studies'
import CompoundDosingTable from '@/components/studies/CompoundDosingTable'
import CompoundTable from '@/components/studies/CompoundTable'
import InterventionOverview from '@/components/studies/InterventionOverview'
import UnderConstruction from '@/components/layout/UnderConstruction.vue'
import HelpButton from '@/components/tools/HelpButton'
import { mapActions } from 'vuex'

export default {
  mixins: [studySelectedNavigationGuard],
  components: {
    CompoundDosingTable,
    CompoundTable,
    InterventionOverview,
    UnderConstruction,
    HelpButton
  },
  data () {
    return {
      tab: null,
      tabs: [
        { tab: '#overview', name: this.$t('Sidebar.study.study_intervention_overview') },
        { tab: '#study_compounds', name: this.$t('Sidebar.study.compounds') },
        { tab: '#study_compound_dosings', name: this.$t('Sidebar.study.compound_dosings') },
        { tab: '#other_interventions', name: this.$t('Sidebar.study.other_interventions') }
      ]
    }
  },
  mounted () {
    this.tab = this.$route.params.tab
    const tabName = this.tab ? this.tabs.find(el => el.tab.substring(1) === this.tab).name : this.tabs[0].name
    setTimeout(() => {
      this.addBreadcrumbsLevel({
        text: tabName,
        to: { name: 'StudyInterventions', params: { tab: tabName } },
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
    tab (newValue) {
      const tabName = newValue ? this.tabs.find(el => el.tab.substring(1) === newValue).name : this.tabs[0].name
      this.$router.push({
        name: 'StudyInterventions',
        params: { tab: newValue }
      })
      this.addBreadcrumbsLevel({
        text: tabName,
        to: { name: 'StudyInterventions', params: { tab: tabName } },
        index: 3,
        replace: true
      })
    }
  }
}
</script>
