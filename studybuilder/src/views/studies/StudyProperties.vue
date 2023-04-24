<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('Sidebar.study.study_properties') }} ({{ studyId }})
    <help-button-with-panels
      :help-text="$t('_help.StudyProperties.general')"
      :items="helpItems"
      />
  </div>
  <v-tabs v-model="tab">
    <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">{{ tab.name }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="type">
      <study-type-summary />
    </v-tab-item>
    <v-tab-item id="attributes">
      <intervention-type-summary />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import HelpButtonWithPanels from '@/components/tools/HelpButtonWithPanels'
import InterventionTypeSummary from '@/components/studies/InterventionTypeSummary'
import { studySelectedNavigationGuard } from '@/mixins/studies'
import StudyTypeSummary from '@/components/studies/StudyTypeSummary'
import { mapActions } from 'vuex'

export default {
  mixins: [studySelectedNavigationGuard],
  components: {
    InterventionTypeSummary,
    HelpButtonWithPanels,
    StudyTypeSummary
  },
  data () {
    return {
      helpItems: [
        'StudyProperties.study_type'
      ],
      tab: null,
      tabs: [
        { tab: '#type', name: this.$t('Sidebar.study.study_type') },
        { tab: '#attributes', name: this.$t('Sidebar.study.study_attributes') }
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
    })
  },
  watch: {
    tab (newValue) {
      this.$router.push({
        name: 'StudyProperties',
        params: { tab: newValue }
      })
      const tabName = newValue ? this.tabs.find(el => el.tab.substring(1) === newValue).name : this.tabs[0].name
      this.addBreadcrumbsLevel({
        text: tabName,
        to: { name: 'StudyProperties', params: { tab: tabName } },
        index: 3,
        replace: true
      })
    }
  }
}
</script>
