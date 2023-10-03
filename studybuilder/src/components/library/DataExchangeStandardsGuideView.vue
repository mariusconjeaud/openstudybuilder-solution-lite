<template>
<div>
  <v-row>
    <v-col cols="1">
      <v-timeline dense>
        <v-timeline-item
          v-for="model of models"
          :key="model.start_date"
          :color="activeGuide === model ? 'primary' : 'grey'"
          small
          right>
          <v-btn
            text
            :color="activeGuide === model ? 'primary' : 'default'"
            @click="chooseGuideVersion(model)"
            >
            {{ model.version_number }}
          </v-btn>
        </v-timeline-item>
      </v-timeline>
    </v-col>
    <v-spacer/>
    <v-col cols="11">
      <v-card
        class="mt-2 mb-2"
        elevation="6"
        max-width="99%">
        <v-card-text>
          <v-row>
            <v-col cols="1">
              <div class="font-weight-bold">{{ $t('DataModels.status') }}</div>
              <p class="font-weight-regular">{{ activeGuide.status }}</p>
            </v-col>
            <v-col cols="3">
              <div class="font-weight-bold">{{ $t('DataModels.effective_date') }}</div>
              <p class="font-weight-regular">{{ activeGuide.start_date ? activeGuide.start_date.substring(0, 10) : '' }}</p>
            </v-col>
            <v-col cols="3">
              <div class="font-weight-bold">{{ $t('DataModels.implements') }}</div>
              <a href="#" @click="redirectToModel(activeGuide.implemented_data_model)" class="font-weight-regular">{{ activeGuide.implemented_data_model ? activeGuide.implemented_data_model.name : '' }}</a>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
      <div class="title font-weight-bold mt-6">{{ $t('DataModels.classes') }}</div>
      <v-tabs v-model="tab" show-arrows>
        <v-tab v-for="tab of datasets" :key="tab[0].uid" :href="tab[0].tab">{{ tab[0].implemented_dataset_class.dataset_class_name ? tab[0].implemented_dataset_class.dataset_class_name.replaceAll('_', ' ') : '0' }}</v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item
          v-for="tab of datasets"
          :key="tab[0].uid">
          <div v-if="tab.length === 1">
            <v-card
              class="mt-2 mb-2 ml-1"
              elevation="6"
              max-width="1440px">
              <v-card-text>
                <v-row>
                  <v-col cols="2">
                    <div class="font-weight-bold">{{ $t('_global.name') }}</div>
                    <p class="font-weight-regular">{{ tab[0].label }}</p>
                  </v-col>
                  <v-col cols="1">
                    <div class="font-weight-bold">{{ $t('DataModels.ordinal') }}</div>
                    <p class="font-weight-regular">{{ tab[0].data_model_ig.ordinal }}</p>
                  </v-col>
                  <v-col cols="9">
                    <div class="font-weight-bold">{{ $t('_global.description') }}</div>
                    <p class="font-weight-regular">{{ tab[0].description }}</p>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
            <v-data-table
              :loading="loading"
              dense
              :headers="headers"
              :items="variables">
                <template v-slot:item.referenced_codelist.uid="{ item }">
                  <a href="#" @click="showCodelistTerms(item.referenced_codelist.uid)">{{ item.referenced_codelist ? item.referenced_codelist.uid : '' }}</a>
                </template>
                <template v-slot:item.implements_variable.uid="{ item }">
                  <a href="#" @click="openImplementedModel(item.implements_variable.uid)">{{ item.implements_variable ? item.implements_variable.uid : '' }}</a>
                </template>
            </v-data-table>
          </div>
          <div v-else>
            <v-tabs v-model="domainTab" show-arrows>
              <v-tab v-for="dTab of tab" :key="dTab.uid" :href="dTab.tab">{{ dTab.uid }}</v-tab>
            </v-tabs>
            <v-tabs-items v-model="domainTab">
              <v-tab-item
                v-for="dTab of tab"
                :key="dTab.uid">
                <v-card
                  class="mt-2 mb-2 ml-1"
                  elevation="6"
                  max-width="1440px">
                  <v-card-text>
                    <v-row>
                      <v-col cols="2">
                        <div class="font-weight-bold">{{ $t('_global.name') }}</div>
                        <p class="font-weight-regular">{{ dTab.label }}</p>
                      </v-col>
                      <v-col cols="1">
                        <div class="font-weight-bold">{{ $t('DataModels.ordinal') }}</div>
                        <p class="font-weight-regular">{{ dTab.data_model_ig.ordinal }}</p>
                      </v-col>
                      <v-col cols="9">
                        <div class="font-weight-bold">{{ $t('_global.description') }}</div>
                        <p class="font-weight-regular">{{ dTab.description }}</p>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
                <v-data-table
                  :loading="loading"
                  dense
                  :headers="headers"
                  :items="variables">
                    <template v-slot:item.referenced_codelist.uid="{ item }">
                      <a href="#" @click="showCodelistTerms(item.referenced_codelist.uid)">{{ item.referenced_codelist ? item.referenced_codelist.uid : '' }}</a>
                    </template>
                    <template v-slot:item.implements_variable.uid="{ item }">
                      <a href="#" @click="openImplementedModel(item.implements_variable.uid)">{{ item.implements_variable ? item.implements_variable.uid : '' }}</a>
                    </template>
                </v-data-table>
              </v-tab-item>
            </v-tabs-items>
          </div>
        </v-tab-item>
      </v-tabs-items>
    </v-col>
  </v-row>
  <v-dialog v-model="showCodelist" persistent>
    <standards-codelist-terms-dialog :codelistUid="codelistUid" @close="closeCodelistTerms"/>
  </v-dialog>
</div>
</template>

<script>
import standards from '@/api/standards'
import _isEmpty from 'lodash/isEmpty'
import StandardsCodelistTermsDialog from '@/components/library/StandardsCodelistTermsDialog'

export default {
  props: {
    uid: String,
    headers: Array,
    redirectGuide: Object
  },
  components: {
    StandardsCodelistTermsDialog
  },
  data () {
    return {
      models: [],
      activeGuide: {},
      datasets: [],
      activeClass: {},
      tab: null,
      variables: [],
      loading: false,
      domainTab: null,
      showCodelist: false,
      codelistUid: ''
    }
  },
  mounted () {
    const params = {
      filters: { uid: { v: [this.uid], op: 'eq' } },
      page_size: 0
    }
    standards.getAllGuides(params).then(resp => {
      this.models = resp.data.items
      this.chooseGuideVersion(!_isEmpty(this.redirectGuide) ? this.models.find(model => model.name === this.redirectGuide.name) : this.models[0])
    })
  },
  methods: {
    openImplementedModel (variable) {
      const params = {
        data_model_name: this.activeGuide.implemented_data_model.uid,
        data_model_version: this.activeGuide.implemented_data_model.name.substring(6),
        dataset_class_name: this.datasets[this.tab][0].implemented_dataset_class.dataset_class_name,
        filters: { uid: { v: [variable], op: 'eq' } }
      }
      standards.getClassVariables(params).then(resp => {
        this.$emit('redirectToModelWithVariable', { data: resp.data.items, implementation: this.activeGuide.implemented_data_model })
      })
    },
    showCodelistTerms (codelistUid) {
      this.codelistUid = codelistUid
      this.showCodelist = true
    },
    closeCodelistTerms () {
      this.codelistUid = ''
      this.showCodelist = false
    },
    redirectToModel (item) {
      this.$emit('redirectToModel', item)
    },
    chooseGuideVersion (guide) {
      if (guide) {
        this.datasets = []
        this.activeGuide = guide
        const params = {
          data_model_ig_name: this.activeGuide.uid,
          data_model_ig_version: this.activeGuide.version_number,
          page_size: 0
        }
        standards.getDatasets(params).then(resp => {
          this.datasets = resp.data.items
          const sortedDatasets = Object.values(this.datasets.reduce((acc, curr) => {
            acc[curr.implemented_dataset_class.dataset_class_name] = acc[curr.implemented_dataset_class.dataset_class_name] || []
            acc[curr.implemented_dataset_class.dataset_class_name].push(curr)
            return acc
          }, {})).sort((a, b) => a[0].implemented_dataset_class.dataset_class_name.localeCompare(b[0].implemented_dataset_class.dataset_class_name))
          this.datasets = sortedDatasets
          this.tab = 0
          this.getVariables(this.datasets[0][0].label)
        })
      }
    },
    getVariables (domain) {
      this.loading = true
      this.variables = []
      const params = {
        filters: {
          'dataset.name': {
            v: [domain], op: 'eq'
          }
        },
        data_model_ig_name: this.activeGuide.uid,
        data_model_ig_version: this.activeGuide.version_number,
        page_size: 0
      }
      standards.getDatasetVariables(params).then(resp => {
        this.variables = resp.data.items
        this.loading = false
      })
    }
  },
  watch: {
    tab (value) {
      this.domainTab = 0
      if (this.datasets[value]) {
        this.getVariables(this.datasets[value][0].label)
      }
    },
    redirectGuide (value) {
      this.chooseGuideVersion(this.models.find(model => model.name === value.name))
    },
    domainTab (value) {
      this.getVariables(this.datasets[this.tab][value].label)
    }
  }
}
</script>
