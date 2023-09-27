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
    <v-tab-item id="SDTMIG">
      <data-exchange-standards-guide-view
        :headers="igHeaders"
        uid="SDTMIG"
        @redirectToModel="redirectToModel"
        @redirectToModelWithVariable="redirectToModelWithVariable"
        :redirectGuide="redirectGuide"/>
    </v-tab-item>
    <v-tab-item id="SDTMIG__AP">
      <data-exchange-standards-guide-view
        :headers="igHeaders"
        uid="SDTMIG__AP"
        @redirectToModel="redirectToModel"
        @redirectToModelWithVariable="redirectToModelWithVariable"
        :redirectGuide="redirectGuide"/>
    </v-tab-item>
    <v-tab-item id="SDTMIG__MD">
      <data-exchange-standards-guide-view
        :headers="igHeaders"
        uid="SDTMIG__MD"
        @redirectToModel="redirectToModel"
        @redirectToModelWithVariable="redirectToModelWithVariable"
        :redirectGuide="redirectGuide"/>
    </v-tab-item>
    <v-tab-item id="SENDIG">
      <data-exchange-standards-guide-view
        :headers="igHeaders"
        uid="SENDIG"
        @redirectToModel="redirectToModel"
        @redirectToModelWithVariable="redirectToModelWithVariable"
        :redirectGuide="redirectGuide"/>
    </v-tab-item>
    <v-tab-item id="SENDIG__AR">
      <data-exchange-standards-guide-view
        :headers="igHeaders"
        uid="SENDIG__AR"
        @redirectToModel="redirectToModel"
        @redirectToModelWithVariable="redirectToModelWithVariable"
        :redirectGuide="redirectGuide"/>
    </v-tab-item>
    <v-tab-item id="SENDIG__DART">
      <data-exchange-standards-guide-view
        :headers="igHeaders"
        uid="SENDIG__DART"
        @redirectToModel="redirectToModel"
        @redirectToModelWithVariable="redirectToModelWithVariable"
        :redirectGuide="redirectGuide"/>
    </v-tab-item>
    <v-tab-item id="SENDIG__GENETOX">
      <data-exchange-standards-guide-view
        :headers="igHeaders"
        uid="SENDIG__GENETOX"
        @redirectToModel="redirectToModel"
        @redirectToModelWithVariable="redirectToModelWithVariable"
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
        { tab: '#SDTMIG', name: this.$t('DataModels.sdtm_ig') },
        { tab: '#SDTMIG__AP', name: this.$t('DataModels.sdtmig_ap') },
        { tab: '#SDTMIG__MD', name: this.$t('DataModels.sdtmig_md') },
        { tab: '#SENDIG', name: this.$t('DataModels.sendig') },
        { tab: '#SENDIG__AR', name: this.$t('DataModels.sendig_ar') },
        { tab: '#SENDIG__DART', name: this.$t('DataModels.sendig_dart') },
        { tab: '#SENDIG__GENETOX', name: this.$t('DataModels.sendig_genetox') }
      ],
      redirectModel: {},
      redirectGuide: {},
      modelsHeaders: [
        { text: this.$t('DataModels.ordinal'), value: 'dataset_class.ordinal' },
        { text: this.$t('_global.name'), value: 'uid' },
        { text: this.$t('DataModels.label'), value: 'label' },
        { text: this.$t('DataModels.data_type'), value: 'simple_datatype' },
        { text: this.$t('DataModels.role'), value: 'role' },
        { text: this.$t('DataModels.qualifies_variable'), value: 'qualifies_variable.uid' },
        { text: this.$t('DataModels.described_value_domain'), value: 'described_value_domain' },
        { text: this.$t('DataModels.notes'), value: 'notes' },
        { text: this.$t('DataModels.usage_restrictions'), value: 'usage_restrictions' },
        { text: this.$t('_global.description'), value: 'description' },
        { text: this.$t('DataModels.c_code'), value: 'referenced_codelist.uid' },
        { text: this.$t('DataModels.examples'), value: 'examples' }
      ],
      igHeaders: [
        { text: this.$t('DataModels.ordinal'), value: 'dataset.ordinal' },
        { text: this.$t('_global.name'), value: 'uid' },
        { text: this.$t('DataModels.label'), value: 'label' },
        { text: this.$t('DataModels.data_type'), value: 'simple_datatype' },
        { text: this.$t('DataModels.role'), value: 'role' },
        { text: this.$t('DataModels.core'), value: 'core' },
        { text: this.$t('DataModels.codelist'), value: 'referenced_codelist.uid' },
        { text: this.$t('DataModels.desc_value'), value: 'described_value_domain' },
        { text: this.$t('DataModels.implements'), value: 'implements_variable.uid' },
        { text: this.$t('DataModels.value_list'), value: 'value_list' },
        { text: this.$t('_global.description'), value: 'description' }
      ]
    }
  },
  methods: {
    redirectToGuide (item) {
      this.redirectGuide = item
      this.tab = item.uid
    },
    redirectToModel (item) {
      this.redirectModel = item
      this.tab = 'models'
    },
    redirectToModelWithVariable (data) {
      this.redirectModel = data
      this.tab = 'models'
    }
  }
}
</script>
