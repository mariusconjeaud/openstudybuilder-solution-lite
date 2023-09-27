<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('StudyManageView.title') }}
    <help-button :help-text="$t('_help.SelectOrAddStudyTable.general')" />
  </div>
  <v-tabs v-model="tab">
    <v-tab href="#active">{{ $t('SelectOrAddStudyTable.tab1_title') }}</v-tab>
    <v-tab href="#deleted">{{ $t('SelectOrAddStudyTable.tab2_title') }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="active">
      <study-table
        key="activeStudies"
        :items="activeStudies"
        :server-items-length="totalActiveStudies"
        @filter="fetchActiveStudies"
        :options.sync="activeOptions"
        @refreshStudies="fetchActiveStudies"
        />
    </v-tab-item>
    <v-tab-item id="deleted">
      <study-table
        key="deletedStudies"
        :items="deletedStudies"
        :server-items-length="totalDeletedStudies"
        @filter="fetchDeletedStudies"
        :options.sync="deletedOptions"
        read-only
        />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import api from '@/api/study'
import filteringParameters from '@/utils/filteringParameters'
import StudyTable from '@/components/studies/StudyTable'
import HelpButton from '@/components/tools/HelpButton'

export default {
  components: {
    StudyTable,
    HelpButton
  },
  data () {
    return {
      activeStudies: [],
      activeOptions: {},
      deletedStudies: [],
      deletedOptions: {},
      tab: null,
      totalActiveStudies: 0,
      totalDeletedStudies: 0
    }
  },
  methods: {
    fetchActiveStudies (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.activeOptions, filters, sort, filtersUpdated)
      params.sort_by = { 'current_metadata.identification_metadata.study_id': true }
      api.get(params).then(resp => {
        this.activeStudies = resp.data.items
        this.totalActiveStudies = resp.data.total
      })
    },
    fetchDeletedStudies (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.activeOptions, filters, sort, filtersUpdated)
      params.deleted = true
      api.get(params).then(resp => {
        this.deletedStudies = resp.data.items
        this.totalDeletedStudies = resp.data.total
      })
    },
    initialSortByDate () {
      this.activeOptions.sortBy = ['current_metadata.version_metadata.version_timestamp']
      this.activeOptions.sortDesc = [true]
    }
  },
  mounted () {
    this.tab = this.$route.params.tab
    this.$store.dispatch('manageStudies/fetchProjects')
    this.initialSortByDate()
  },
  watch: {
    tab (newValue) {
      this.$router.push({
        name: 'SelectOrAddStudy',
        params: { tab: newValue }
      })
    },
    activeOptions () {
      this.fetchActiveStudies()
    },
    deletedOptions () {
      this.fetchDeletedStudies()
    }
  }
}
</script>
