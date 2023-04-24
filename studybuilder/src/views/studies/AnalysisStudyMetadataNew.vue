<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('Sidebar.study.analysis_study_metadata_new') }}
    <help-button :help-text="$t('_help.SdtmSpecificationTable.general')" />
  </div>
  <v-tabs v-model="tab">
    <v-tab href="#mdvisit">{{ $t('AnalysisStudyMetadata.mdvisit') }}</v-tab>
    <v-tab href="#mdendpnt">{{ $t('AnalysisStudyMetadata.mdendpnt') }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="mdvisit">
      <analysis-metadata-table
        key="mdvisit"
        type="mdvisit"
        :headers="mdVisitHeaders"
        />
    </v-tab-item>
    <v-tab-item id="mdendpnt">
      <analysis-metadata-table
        key="mdendpnt"
        type="mdendpnt"
        :headers="mdEndpntHeaders"
        >

      </analysis-metadata-table>
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import AnalysisMetadataTable from '@/components/studies/AnalysisMetadataTable'
import HelpButton from '@/components/tools/HelpButton'

export default {
  components: {
    AnalysisMetadataTable,
    HelpButton
  },
  data () {
    return {
      mdEndpntHeaders: [
        { text: this.$t('AnalysisMetadataTable.study_id'), value: 'STUDYID' },
        { text: this.$t('AnalysisMetadataTable.objective_level'), value: 'OBJTVLVL' },
        { text: this.$t('AnalysisMetadataTable.objective'), value: 'OBJTV' },
        { text: this.$t('AnalysisMetadataTable.objective_plain_text'), value: 'OBJTVPT' },
        { text: this.$t('AnalysisMetadataTable.endpoint_level'), value: 'ENDPNTLVL' },
        { text: this.$t('AnalysisMetadataTable.endpoint_sub_level'), value: 'ENDPNTSL' },
        { text: this.$t('AnalysisMetadataTable.endpoint_plain'), value: 'ENDPNT' },
        { text: this.$t('AnalysisMetadataTable.endpoint_plain_text'), value: 'ENDPNTPT' },
        { text: this.$t('AnalysisMetadataTable.unit_definition'), value: 'UNITDEF' },
        { text: this.$t('AnalysisMetadataTable.unit'), value: 'UNIT' },
        { text: this.$t('AnalysisMetadataTable.time_frame'), value: 'TMFRM' },
        { text: this.$t('AnalysisMetadataTable.time_frame_plain_text'), value: 'TMFRMPT' },
        { text: this.$t('AnalysisMetadataTable.related_activity_groups'), value: 'RACTGRP' },
        { text: this.$t('AnalysisMetadataTable.related_activity_subgroups'), value: 'RACTSGRP' },
        { text: this.$t('AnalysisMetadataTable.related_activities'), value: 'RACT' },
        { text: this.$t('AnalysisMetadataTable.related_activity_instances'), value: 'RACTINST' }
      ],
      mdVisitHeaders: [
        { text: this.$t('AnalysisMetadataTable.study_id'), value: 'STUDYID' },
        { text: this.$t('AnalysisMetadataTable.visit_type_name'), value: 'VISIT_TYPE_NAME' },
        { text: this.$t('AnalysisMetadataTable.visit_num'), value: 'VISIT_NUM' },
        { text: this.$t('AnalysisMetadataTable.visit_name'), value: 'VISIT_NAME' },
        { text: this.$t('AnalysisMetadataTable.visit_short_label'), value: 'VISIT_SHORT_LABEL' },
        { text: this.$t('AnalysisMetadataTable.day_name'), value: 'DAY_NAME' },
        { text: this.$t('AnalysisMetadataTable.day_value'), value: 'DAY_VALUE' },
        { text: this.$t('AnalysisMetadataTable.week_name'), value: 'WEEK_NAME' },
        { text: this.$t('AnalysisMetadataTable.week_value'), value: 'WEEK_VALUE' }
      ],
      tab: null
    }
  },
  mounted () {
    this.tab = this.$route.params.tab
  },
  watch: {
    tab (newValue) {
      this.$router.push({
        name: 'AnalysisStudyMetadataNew',
        params: { tab: newValue }
      })
    }
  }
}
</script>
