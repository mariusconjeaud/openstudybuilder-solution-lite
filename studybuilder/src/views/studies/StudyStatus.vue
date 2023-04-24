<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('StudyStatusView.title') }} ({{ studyId }})
    <help-button width="800px">
      <div class="text-h6">{{ $t('_help.StudyStatus.core_attributes') }}</div>
      <div class="my-2" v-html="$t('_help.StudyStatus.core_attributes_body')"></div>
      <div class="text-h6">{{ $t('_help.StudyStatus.study_status') }}</div>
      <div class="my-2">
        {{ $t('_help.StudyStatus.content_line_1') }}
        <ul>
          <li v-html="$t('_help.StudyStatus.content_line_2')"></li>
          <li v-html="$t('_help.StudyStatus.content_line_3')"></li>
          <li v-html="$t('_help.StudyStatus.content_line_4')"></li>
        </ul>
        <p class='mt-2'>{{ $t('_help.StudyStatus.content_line_5') }} </p>
        <p>{{ $t('_help.StudyStatus.content_line_6') }} </p>
      </div>
      <ul>
        <li><span v-html="$t('_help.StudyStatus.content_line_7')"></span>
          <ul>
            <li v-html="$t('_help.StudyStatus.content_line_8')"></li>
          </ul>
        </li>
        <li>
          <span v-html="$t('_help.StudyStatus.content_line_9')"></span>
          <ul>
            <li v-html="$t('_help.StudyStatus.content_line_10')"></li>
          </ul>
        </li>
        <li>
          <span v-html="$t('_help.StudyStatus.content_line_11')"></span>
          <ul>
            <li v-html="$t('_help.StudyStatus.content_line_12')"></li>
          </ul>
        </li>
      </ul>

      <div class="text-h6 mt-2">{{ $t('_help.StudyStatus.study_sub_parts') }}</div>
      <div class="my-2">
        {{ $t('_help.StudyStatus.study_sub_parts_body') }}
      </div>
      <div class="text-h6">{{ $t('_help.StudyStatus.protocol_version') }}</div>
      <div class="my-2">
        {{ $t('_help.StudyStatus.protocol_version_body') }}
      </div>
    </help-button>
  </div>
  <v-tabs v-model="tab">
    <v-tab href="#core_attributes">{{ $t('StudyStatusView.tab1_title') }}</v-tab>
    <v-tab href="#study_status">{{ $t('StudyStatusView.tab2_title') }}</v-tab>
    <v-tab href="#subparts">{{ $t('StudyStatusView.tab3_title') }}</v-tab>
    <v-tab href="#protocolversions">{{ $t('StudyStatusView.tab4_title') }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="core_attributes">
      <study-identification-summary />
    </v-tab-item>
    <v-tab-item id="study_status">
      <study-status-table />
    </v-tab-item>
    <v-tab-item id="subparts">
      <under-construction />
    </v-tab-item>
    <v-tab-item id="protocolversions">
      <under-construction />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import HelpButton from '@/components/tools/HelpButton'
import StudyIdentificationSummary from '@/components/studies/StudyIdentificationSummary'
import { studySelectedNavigationGuard } from '@/mixins/studies'
import StudyStatusTable from '@/components/studies/StudyStatusTable'
import UnderConstruction from '@/components/layout/UnderConstruction'

export default {
  mixins: [studySelectedNavigationGuard],
  components: {
    HelpButton,
    StudyIdentificationSummary,
    StudyStatusTable,
    UnderConstruction
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
        name: 'StudyStatus',
        params: { tab: newValue }
      })
    }
  }
}
</script>
