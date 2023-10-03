<template>
  <div>
    <v-card color="dfltBackground">
      <v-card-title>
        <div class="page-title">
          {{ codelistAttributes.name }} ({{ codelistAttributes.codelist_uid }}) - {{ codelistAttributes.submission_value }} / {{ $t('CodeListDetail.terms_listing') }}
        </div>
      </v-card-title>
      <v-card-text>
        <v-expansion-panels
          flat
          tile
          accordion
          v-model="panel"
          >
          <v-expansion-panel>
            <v-expansion-panel-header class="text-h6 grey--text">{{ $t('CodelistSummary.title') }}</v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-row class="mt-2">
                <v-col cols="2" class="font-weight-bold pb-0">
                  {{ codelistAttributes.codelist_uid }}
                </v-col>
                <v-col cols="1" class="pb-0">
                <v-btn
                  color="secondary"
                  @click="openCodelistTerms"
                  >
                  {{ $t('CodeListDetail.open_ct') }}
                </v-btn>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="2" class="font-weight-bold pb-0">
                  {{ $t('CodeListDetail.extensible') }}:
                </v-col>
                <v-col cols="1" class="pb-0">
                  {{ codelistAttributes.extensible|yesno }}
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="2" class="font-weight-bold pb-0">
                  {{ $t('CodeListDetail.submission_value') }}:
                </v-col>
                <v-col cols="1" class="pb-0">
                  {{ codelistAttributes.submission_value }}
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="2" class="font-weight-bold pb-0">
                  {{ $t('CodeListDetail.definition') }}:
                </v-col>
                <v-col cols="8" class="pb-0">
                  {{ codelistAttributes.definition }}
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="2" class="font-weight-bold">
                  {{ $t('CodeListDetail.nci_pref_name') }}:
                </v-col>
                <v-col cols="8">
                  {{ codelistAttributes.nci_preferred_name }}
                </v-col>
              </v-row>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
        <n-n-table
          :headers="headers"
          :items="terms"
          :server-items-length="total"
          :options.sync="options"
          item-key="term_uid"
          height="40vh"
          class="mt-4"
          has-api
          @filter="fetchTerms"
          column-data-resource="ct/terms"
          :codelist-uid="codelistUid"
        >
          <template v-slot:item.attributes.status="{ item }">
            <status-chip :status="item.attributes.status" />
          </template>
        </n-n-table>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="secondary"
          @click="close"
          >
          {{ $t('_global.close') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import controlledTerminology from '@/api/controlledTerminology'
import terms from '@/api/controlledTerminology/terms'
import NNTable from '@/components/tools/NNTable'
import StatusChip from '@/components/tools/StatusChip'
import filteringParameters from '@/utils/filteringParameters'

export default {
  props: ['codelistUid'],
  components: {
    NNTable,
    StatusChip
  },
  data () {
    return {
      codelistNames: {},
      codelistAttributes: {},
      headers: [
        { text: this.$t('CtCatalogueTable.concept_id'), value: '_concept_id' },
        { text: this.$t('CodelistTermsView.sponsor_name'), value: 'name.sponsor_preferred_name' },
        { text: this.$t('CodelistTermsView.code_submission_value'), value: 'attributes.code_submission_value' },
        { text: 'Version', value: 'attributes.version' },
        { text: this.$t('CodelistTermsView.attr_status'), value: 'attributes.status' }
      ],
      options: {},
      selectedTerm: {},
      terms: [],
      total: 0,
      panel: 0
    }
  },
  mounted () {
    controlledTerminology.getCodelistAttributes(this.codelistUid).then(resp => {
      this.codelistAttributes = resp.data
    })
  },
  methods: {
    close () {
      this.$emit('close')
    },
    openCodelistTerms () {
      this.$router.push({
        name: 'CodelistTerms',
        params: { codelist_id: this.codelistUid, catalogue_name: 'All' }
      })
    },
    fetchTerms (filters, sort, filtersUpdated) {
      if (filtersUpdated) {
        this.options.page = 1
      }
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      params.codelist_uid = this.codelistUid
      terms.getAll(params).then(resp => {
        this.terms = resp.data.items
        this.total = resp.data.total
        for (const term of this.terms) {
          if (term.attributes.concept_id === null) {
            term._concept_id = term.term_uid
          } else {
            term._concept_id = term.attributes.concept_id
          }
        }
      })
    }
  },
  watch: {
    codelistUid (value) {
      if (value) {
        controlledTerminology.getCodelistAttributes(value).then(resp => {
          this.codelistAttributes = resp.data
        })
        this.fetchTerms()
      }
    },
    options: {
      handler () {
        this.fetchTerms()
      },
      deep: true
    }
  }

}
</script>
