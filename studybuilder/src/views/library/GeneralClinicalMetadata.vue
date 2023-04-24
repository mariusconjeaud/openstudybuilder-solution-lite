<template>
<div>
  <div class="page-title d-flex align-center">
    {{ $t('ClinicalMetadataView.title') }}
    <help-button :help-text="$t('_help.GeneralClinicalMetadataTable.general')" />
  </div>
  <v-tabs v-model="currentTab">
    <v-tab v-for="tab in tabs" :key="tab.name" >{{ tab.name }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="currentTab">
    <v-tab-item v-for="tab in tabs"
           :key="tab.name"
           >
      <clinical-metadata-table
        :source="tab.value"/>
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>

import ClinicalMetadataTable from '@/components/library/ClinicalMetadataTable'
import HelpButton from '@/components/tools/HelpButton'
import { mapActions } from 'vuex'

export default {
  components: {
    ClinicalMetadataTable,
    HelpButton
  },
  data () {
    return {
      tabs: [
        { name: this.$t('ClinicalMetadataView.topic_code_def'), value: 'topic-cd-def' },
        { name: this.$t('ClinicalMetadataView.unit_def'), value: '' },
        { name: this.$t('ClinicalMetadataView.cdisc_version'), value: '' },
        { name: this.$t('ClinicalMetadataView.cdisc_package'), value: '' },
        { name: this.$t('ClinicalMetadataView.cdisc_list'), value: '' },
        { name: this.$t('ClinicalMetadataView.cdisc_values'), value: '' }
      ],
      currentTab: null
    }
  },
  mounted () {
    const tabName = this.tabs[0].name
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
    currentTab (newValue) {
      const tabName = this.tabs[newValue].name
      this.addBreadcrumbsLevel({
        text: tabName,
        index: 3,
        replace: true
      })
    }
  }
}
</script>
