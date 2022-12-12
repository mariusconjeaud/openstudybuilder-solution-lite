<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('Sidebar.study.study_interventions') }} ({{ studyId }})
    <help-button :help-text="$t('_help.StudyInterventionsTable.general')" />
  </div>
  <v-tabs v-model="tab">
    <v-tab href="#overview">{{ $t('Sidebar.study.study_intervention_overview') }}</v-tab>
    <v-tab href="#study_compounds">{{ $t('Sidebar.study.compounds') }}</v-tab>
    <v-tab href="#study_compound_dosings">{{ $t('Sidebar.study.compound_dosings') }}</v-tab>
    <v-tab href="#other_interventions">{{ $t('Sidebar.study.other_interventions') }}</v-tab>
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
      tab: null
    }
  },
  mounted () {
    this.tab = this.$route.params.tab
  },
  watch: {
    tab (newValue) {
      this.$router.push({
        name: 'StudyInterventions',
        params: { tab: newValue }
      })
    }
  }
}
</script>
