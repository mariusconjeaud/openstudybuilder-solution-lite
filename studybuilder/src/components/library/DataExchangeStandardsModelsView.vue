<template>
<div>
  <v-row>
    <v-col cols="1">
      <v-timeline dense>
        <v-timeline-item
          v-for="model of models"
          :key="model.start_date"
          :color="activeModel === model ? 'primary' : 'grey'"
          small
          right>
          <v-btn
            text
            @click="chooseModelVersion(model)"
            :color="activeModel === model ? 'primary' : 'default'"
            >
            v{{ model.version_number }}
          </v-btn>
        </v-timeline-item>
      </v-timeline>
    </v-col>
    <v-spacer/>
    <v-col cols="11">
      <v-card
        class="mt-2 mb-2"
        elevation="6"
        max-width="1440px">
        <v-card-text>
          <v-row>
            <v-col cols="1">
              <div class="font-weight-bold">{{ $t('DataModels.status') }}</div>
              <p class="font-weight-regular">{{ activeModel.status }}</p>
            </v-col>
            <v-col cols="3">
              <div class="font-weight-bold">{{ $t('DataModels.effective_date') }}</div>
              <p class="font-weight-regular">{{ activeModel.start_date|date }}</p>
            </v-col>
            <v-col cols="3">
              <div class="font-weight-bold">{{ $t('DataModels.implemented_by') }}</div>
              <a href="#" v-for="guide of activeModel.implementation_guides" :key="guide.name" @click="redirectToGuide(guide)" class="font-weight-regular">{{ guide.name }} </a>
              <!-- <a href="#" v-for="guide of activeModel.implementation_guides" @click="redirectToGuide(activeModel.implementation_guides)" class="font-weight-regular">{{ activeModel.implementation_guides ? activeModel.implementation_guides[0].name : '' }}</a> -->
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
      <div class="title font-weight-bold mt-6">{{ $t('DataModels.classes') }}</div>
      <v-tabs v-model="tab" show-arrows>
        <v-tab v-for="tab of datasetClasses" :key="tab.uid" :href="tab.tab">{{ tab.uid.replaceAll('_', ' ') }}</v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item
          v-for="tab of datasetClasses"
          :key="tab.uid">
          <div>
            <v-card
              class="mt-2 mb-2 ml-1"
              elevation="6"
              max-width="1440px">
              <v-card-text>
                <v-row>
                  <v-col cols="2">
                    <div class="font-weight-bold">{{ $t('_global.name') }}</div>
                    <p class="font-weight-regular">{{ tab.label }}</p>
                  </v-col>
                  <v-col cols="1">
                    <div class="font-weight-bold">{{ $t('DataModels.ordinal') }}</div>
                    <p class="font-weight-regular">{{ tab.data_models[0].ordinal }}</p>
                  </v-col>
                  <v-col cols="9">
                    <div class="font-weight-bold">{{ $t('_global.description') }}</div>
                    <p class="font-weight-regular">{{ tab.description }}</p>
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
                  <a href="#" @click="openCodelistTerms(item.referenced_codelist.uid)">{{ item.referenced_codelist ? item.referenced_codelist.uid : '' }}</a>
                </template>
            </v-data-table>
          </div>
        </v-tab-item>
      </v-tabs-items>
    </v-col>
  </v-row>
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import standards from '@/api/standards'

export default {
  props: {
    uid: String,
    redirectModel: Object,
    headers: Array
  },
  components: {
  },
  computed: {
    ...mapGetters({
    })
  },
  data () {
    return {
      models: [],
      activeModel: {},
      datasetClasses: [],
      activeClass: {},
      tab: null,
      datasetTab: null,
      variables: [],
      loading: false
    }
  },
  mounted () {
    const params = {
      filters: { uid: { v: [this.uid], op: 'eq' } }
    }
    standards.getAllModels(params).then(resp => {
      this.models = resp.data.items
      this.chooseModelVersion(this.models[0])
    })
  },
  methods: {
    openCodelistTerms (codelistUid) {
      this.$router.push({
        name: 'CodelistTerms',
        params: { codelist_id: codelistUid, catalogue_name: 'All' }
      })
    },
    redirectToGuide (item) {
      this.$emit('redirectToGuide', item)
    },
    chooseModelVersion (model) {
      this.activeModel = model
      const params = {
        filters: {
          'data_models.data_model_name': {
            v: [this.activeModel.name], op: 'eq'
          }
        },
        page_size: 0
      }
      standards.getDatasetClasses(params).then(resp => {
        resp.data.items.forEach(element => {
          if (element.data_models.length > 1) {
            element.data_models = element.data_models.filter((element) => {
              return element.data_model_name === this.activeModel.name
            })
          }
        })
        this.datasetClasses = resp.data.items
        this.datasetClasses.sort((a, b) => {
          return a.data_models[0].ordinal - b.data_models[0].ordinal
        })
        this.tab = 0
        this.getVariables(this.datasetClasses[0].label)
      })
    },
    getVariables (className) {
      this.loading = true
      this.variables = []
      const params = {
        filters: {
          'dataset_class.dataset_class_name': {
            v: [className], op: 'eq'
          }
        },
        data_model_name: this.activeModel.uid,
        data_model_version: this.activeModel.version_number,
        page_size: 0
      }
      standards.getClassVariables(params).then(resp => {
        this.variables = resp.data.items
        this.loading = false
      })
    }
  },
  watch: {
    tab (value) {
      this.getVariables(this.datasetClasses[value].label)
    },
    redirectModel (value) {
      if (value) {
        this.chooseModelVersion(this.models.find(model => model.name === value.name))
      }
    }
  }
}
</script>
