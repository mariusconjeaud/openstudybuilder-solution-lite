<template>
<div class="px-4" v-if="selectedStudyVersion === null">
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
        <template v-slot:item.OBJTV="{ item }">
          <div v-html="item.OBJTV"></div>
        </template>
        <template v-slot:item.RACT="{ item }">
          {{ item.RACT|itemList }}
        </template>
        <template v-slot:item.RACTSGRP="{ item }">
          {{ item.RACTSGRP|itemList }}
        </template>
        <template v-slot:item.RACTGRP="{ item }">
          {{ item.RACTGRP|itemList }}
        </template>
        <template v-slot:item.RACTINST="{ item }">
          {{ item.RACTINST|itemList }}
        </template>
      </analysis-metadata-table>
    </v-tab-item>
  </v-tabs-items>
</div>
<div v-else>
  <under-construction :message="$t('UnderConstruction.not_supported')"/>
</div>
</template>

<script>
import AnalysisMetadataTable from '@/components/studies/AnalysisMetadataTable'
import HelpButton from '@/components/tools/HelpButton'
import { mapGetters } from 'vuex'
import UnderConstruction from '@/components/layout/UnderConstruction'

export default {
  components: {
    AnalysisMetadataTable,
    HelpButton,
    UnderConstruction
  },
  computed: {
    ...mapGetters({
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion'
    })
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
        { text: this.$t('AnalysisMetadataTable.visit_type_name'), value: 'VISTPCD' },
        { text: this.$t('AnalysisMetadataTable.visit_num'), value: 'AVISITN' },
        { text: this.$t('AnalysisMetadataTable.visit_name'), value: 'AVISIT' },
        { text: this.$t('AnalysisMetadataTable.visit_short_label'), value: 'VISLABEL' },
        { text: this.$t('AnalysisMetadataTable.day_name'), value: 'AVISIT1' },
        { text: this.$t('AnalysisMetadataTable.day_value'), value: 'AVISIT1N' },
        { text: this.$t('AnalysisMetadataTable.week_name'), value: 'AVISIT2' },
        { text: this.$t('AnalysisMetadataTable.week_value'), value: 'AVISIT2N' }
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
