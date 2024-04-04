<template>
<div>
  <div class="page-title d-flex align-center">
    {{ $t('DataModels.cdash') }}
    <help-button />
  </div>
  <v-tabs v-model="tab">
    <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">{{ tab.name }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="models">
      <data-exchange-standards-models-view
        :headers="modelsHeaders"
        uid="CDASH"
        @redirectToGuide="redirectToGuide"
        :redirectModel="redirectModel"/>
    </v-tab-item>
    <v-tab-item id="guide">
      <data-exchange-standards-guide-view
        :headers="igHeaders"
        uid="CDASHIG"
        @redirectToModel="redirectToModel"
        :redirectGuide="redirectGuide"/>
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>

import DataExchangeStandardsModelsView from '@/components/library/DataExchangeStandardsModelsView'
import DataExchangeStandardsGuideView from '@/components/library/DataExchangeStandardsGuideView'
import HelpButton from '@/components/tools/HelpButton'

export default {
  components: {
    DataExchangeStandardsModelsView,
    DataExchangeStandardsGuideView,
    HelpButton
  },
  data () {
    return {
      tab: 0,
      tabs: [
        { tab: '#models', name: this.$t('DataModels.cdash_models') },
        { tab: '#guide', name: this.$t('DataModels.cdash_ig') }
      ],
      redirectModel: {},
      redirectGuide: {},
      modelsHeaders: [
        { text: this.$t('DataModels.ordinal'), value: 'dataset_class.ordinal' },
        { text: this.$t('_global.name'), value: 'uid' },
        { text: this.$t('DataModels.label'), value: 'label' },
        { text: this.$t('DataModels.definition'), value: 'description' },
        { text: this.$t('DataModels.question_text'), value: 'question_text' },
        { text: this.$t('DataModels.prompt'), value: 'prompt' },
        { text: this.$t('DataModels.data_type'), value: 'simple_datatype' },
        { text: this.$t('DataModels.impl_notes'), value: 'implementation_notes' },
        { text: this.$t('DataModels.mapping_inst'), value: 'mapping_instructions' },
        { text: this.$t('DataModels.mapping_targets'), value: 'has_mapping_target.uid' },
        { text: this.$t('DataModels.code_list'), value: 'referenced_codelist.uid' }
      ],
      igHeaders: [
        { text: this.$t('DataModels.ordinal'), value: 'dataset.ordinal' },
        { text: this.$t('_global.name'), value: 'uid' },
        { text: this.$t('DataModels.label'), value: 'label' },
        { text: this.$t('DataModels.definition'), value: 'description' },
        { text: this.$t('DataModels.question_text'), value: 'question_text' },
        { text: this.$t('DataModels.prompt'), value: 'prompt' },
        { text: this.$t('DataModels.data_type'), value: 'simple_datatype' },
        { text: this.$t('DataModels.impl_notes'), value: 'implementation_notes' },
        { text: this.$t('DataModels.mapping_inst'), value: 'mapping_instructions' },
        { text: this.$t('DataModels.mapping_targets'), value: 'has_mapping_target.uid' },
        { text: this.$t('DataModels.code_list'), value: 'referenced_codelist.uid' }
      ]
    }
  },
  methods: {
    redirectToGuide (item) {
      this.redirectGuide = item
      this.tab = 'guide'
    },
    redirectToModel (item) {
      this.redirectModel = item
      this.tab = 'models'
    }
  }
}
</script>
