<template>
<div>
  <div class="page-title d-flex align-center">
    {{ $t('DataModels.sdtm') }}
    <help-button />
  </div>
  <v-tabs v-model="tab">
    <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">{{ tab.name }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="models">
      <data-exchange-standards-models-view
        :headers="modelsHeaders"
        uid="SDTM"
        @redirectToGuide="redirectToGuide"
        :redirectModel="redirectModel"/>
    </v-tab-item>
    <v-tab-item id="guide">
      <data-exchange-standards-guide-view
        :headers="igHeaders"
        :uid="['SDTMIG', 'SENDIG']"
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
        { tab: '#models', name: this.$t('DataModels.sdtm_models') },
        { tab: '#guide', name: this.$t('DataModels.sdtm_ig') }
      ],
      redirectModel: {},
      redirectGuide: {},
      modelsHeaders: [
        { text: this.$t('DataModels.ordinal'), value: 'dataset_class.ordinal' },
        { text: this.$t('_global.name'), value: 'uid' },
        { text: this.$t('DataModels.label'), value: 'label' },
        { text: this.$t('DataModels.data_type'), value: 'simple_datatype' },
        { text: this.$t('DataModels.role'), value: 'role' },
        { text: this.$t('_global.description'), value: 'description' }
      ],
      igHeaders: [
        { text: this.$t('DataModels.ordinal'), value: 'dataset.ordinal' },
        { text: this.$t('_global.name'), value: 'uid' },
        { text: this.$t('DataModels.label'), value: 'label' },
        { text: this.$t('DataModels.data_type'), value: 'simple_datatype' },
        { text: this.$t('DataModels.role'), value: 'role' },
        { text: this.$t('DataModels.core'), value: 'core' },
        { text: this.$t('DataModels.implements'), value: 'implements_variable.uid' },
        { text: this.$t('_global.description'), value: 'description' }
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
