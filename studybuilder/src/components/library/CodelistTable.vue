<template>
<div>
  <n-n-table
    :headers="headers"
    :items="codelists"
    :server-items-length="total"
    :options.sync="options"
    :page="currentCataloguePage"
    export-object-label="Codelists"
    :export-data-url="columnDataResource"
    :export-data-url-params="exportUrlParams"
    item-key="codelist_uid"
    @update:page="storeCurrentPage"
    dense
    has-api
    @filter="fetchCodelists"
    :column-data-resource="columnDataResource"
    :column-data-parameters="getPackageObject()"
    :library="library"
    >
    <template v-slot:actions="">
      <slot name="extraActions"></slot>
      <v-btn
        data-cy="add-sponsor-codelist"
        v-if="!readOnly"
        fab
        dark
        small
        color="primary"
        @click.stop="showCreationForm = true"
        :title="$t('CodelistCreationForm.title')"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:afterFilter="">
      <v-autocomplete
        v-model="selectedTerms"
        :label="$t('CodelistTable.search_with_terms')"
        :items="terms"
        item-text="name.sponsor_preferred_name"
        item-value="term_uid"
        dense
        class="mt-5 max-width-300"
        clearable
        return-object
        :search-input.sync="search"
        multiple>
        <template v-slot:selection="{index}">
          <div v-if="index === 0">
            <span class="items-font-size">{{ selectedTerms[0].name.sponsor_preferred_name.substring(0, 12) }}</span>
          </div>
          <span
            v-if="index === 1"
            class="grey--text text-caption mr-1"
          >
            (+{{ selectedTerms.length -1 }})
          </span>
        </template>
      </v-autocomplete>
      <v-select
        :items="operators"
        v-model="termsFilterOperator"
        :label="$t('_global.operator')"
        class="mt-5 max-width-100"
        />
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
    <template v-slot:item.name.template_parameter="{ item }">
      {{ item.name.template_parameter|yesno }}
    </template>
    <template v-slot:item.name.status="{ item }">
      <status-chip :status="item.name.status" />
    </template>
    <template v-slot:item.name.start_date="{ item }">
      {{ item.name.start_date | date }}
    </template>
    <template v-slot:item.attributes.extensible="{ item }">
      {{ item.attributes.extensible|yesno }}
    </template>
    <template v-slot:item.attributes.status="{ item }">
      <status-chip :status="item.attributes.status" />
    </template>
    <template v-slot:item.attributes.start_date="{ item }">
      {{ item.attributes.start_date | date }}
    </template>
  </n-n-table>
  <v-dialog
    v-if="!readOnly"
    v-model="showCreationForm"
    persistent
    max-width="1200px"
    >
    <codelist-creation-form
      :catalogue="catalogue"
      @close="showCreationForm = false"
      @created="goToCodelist"
      />
  </v-dialog>
  <v-dialog v-model="showSponsorValuesHistory"
            @keydown.esc="closeHistory"
            persistent
            :max-width="globalHistoryDialogMaxWidth"
            :fullscreen="globalHistoryDialogFullscreen"
  >
    <history-table
      :title="historyTitle"
      @close="closeHistory"
      :headers="historyHeaders"
      :items="historyItems"
      />
  </v-dialog>
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import { bus } from '@/main'
import controlledTerminology from '@/api/controlledTerminology'
import ActionsMenu from '@/components/tools/ActionsMenu'
import CodelistCreationForm from '@/components/library/CodelistCreationForm'
import dataFormating from '@/utils/dataFormating'
import HistoryTable from '@/components/tools/HistoryTable'
import NNTable from '@/components/tools/NNTable'
import StatusChip from '@/components/tools/StatusChip'
import filteringParameters from '@/utils/filteringParameters'

export default {
  props: {
    catalogue: {
      type: String,
      required: false
    },
    package: {
      type: String,
      required: false
    },
    readOnly: {
      type: Boolean,
      default: false
    },
    columnDataResource: String,
    library: String
  },
  components: {
    ActionsMenu,
    CodelistCreationForm,
    HistoryTable,
    NNTable,
    StatusChip
  },
  computed: {
    ...mapGetters({
      currentCataloguePage: 'ctCatalogues/currentCataloguePage'
    }),
    historyTitle () {
      if (this.selectedCodelist) {
        return this.$t('CodelistTable.history_title', { codelist: this.selectedCodelist.codelist_uid })
      }
      return ''
    },
    exportUrlParams () {
      const params = {}
      if (this.library) {
        params.library = this.library
      }
      if (this.package) {
        params.package = this.package
      }
      if (this.catalogue && this.catalogue !== 'All') {
        params.catalogue_name = this.catalogue
      }
      return params
    }
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil',
          iconColor: 'primary',
          condition: (item) => !this.readOnly,
          click: this.openCodelistDetail
        },
        {
          label: this.$t('CodelistTable.show_terms'),
          icon: 'mdi-dots-horizontal-circle',
          click: this.openCodelistTerms
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openCodelistHistory
        }
      ],
      codelists: [],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('CtCatalogueTable.sponsor_pref_name'), value: 'name.name', width: '15%' },
        { text: this.$t('CtCatalogueTable.template_parameter'), value: 'name.template_parameter' },
        { text: this.$t('CtCatalogueTable.cd_status'), value: 'name.status' },
        { text: this.$t('CtCatalogueTable.modified_name'), value: 'name.start_date' },
        { text: this.$t('CtCatalogueTable.concept_id'), value: 'codelist_uid' },
        { text: this.$t('CtCatalogueTable.submission_value'), value: 'attributes.submission_value' },
        { text: this.$t('CtCatalogueTable.cd_name'), value: 'attributes.name' },
        { text: this.$t('CtCatalogueTable.nci_pref_name'), value: 'attributes.nci_preferred_name' },
        { text: this.$t('CtCatalogueTable.extensible'), value: 'attributes.extensible' },
        { text: this.$t('CtCatalogueTable.attr_status'), value: 'attributes.status' },
        { text: this.$t('CtCatalogueTable.modified_attributes'), value: 'attributes.start_date' }
      ],
      historyHeaders: [
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('CtCatalogueTable.template_parameter'), value: 'template_parameter' },
        { text: this.$t('HistoryTable.change_description'), value: 'change_description' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      historyItems: [],
      options: {},
      showCreationForm: false,
      showSponsorValuesHistory: false,
      selectedCodelist: null,
      total: 0,
      filters: '',
      terms: [],
      selectedTerms: [],
      search: '',
      operators: ['or', 'and'],
      termsFilterOperator: 'or'
    }
  },
  methods: {
    getPackageObject () {
      return { package: this.package }
    },
    fetchCodelists (filters, sort, filtersUpdated) {
      if (!filters && this.filters) {
        filters = this.filters
      }
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      this.filters = filters
      params.library = this.library
      if (this.package) {
        params.package = this.package
      } else if (this.catalogue && this.catalogue !== 'All') {
        params.catalogue_name = this.catalogue
      }
      if (this.selectedTerms.length > 0) {
        params.term_filter = {
          term_uids: this.selectedTerms.map(term => term.term_uid),
          operator: this.termsFilterOperator
        }
      }
      controlledTerminology.getCodelists(params).then(resp => {
        this.codelists = resp.data.items
        this.total = resp.data.total
      })
    },
    fetchTerms  () {
      const params = {
        filters: {
          'name.sponsor_preferred_name':
          { v: [this.search ? this.search : ''], op: 'co' }
        },
        page_size: 20
      }
      controlledTerminology.getCodelistTerms(params).then(resp => {
        this.terms = [...resp.data.items, ...this.selectedTerms]
      })
    },
    goToCodelist (codelist) {
      this.$router.push({ name: 'CodeListDetail', params: { codelist_id: codelist.codelist_uid } })
      bus.$emit('notification', { msg: this.$t('CodelistCreationForm.add_success') })
    },
    openCodelistDetail (codelist) {
      this.$router.push({ name: 'CodeListDetail', params: { catalogue_name: this.catalogue, codelist_id: codelist.codelist_uid } })
    },
    openCodelistTerms (codelist) {
      const params = { codelist }
      if (this.catalogue) {
        params.catalogueName = this.catalogue
      }
      if (this.package) {
        params.packageName = this.package
      }
      this.$emit('openCodelistTerms', params)
    },
    async openCodelistHistory (codelist) {
      this.selectedCodelist = codelist
      const resp = await controlledTerminology.getCodelistNamesVersions(codelist.codelist_uid)
      this.historyItems = resp.data
      for (const item of this.historyItems) {
        if (item.template_parameter !== undefined) {
          item.template_parameter = dataFormating.yesno(item.template_parameter)
        }
      }
      this.showSponsorValuesHistory = true
    },
    storeCurrentPage (page) {
      this.$store.commit('ctCatalogues/SET_CURRENT_CATALOGUE_PAGE', page)
    },
    closeHistory () {
      this.showSponsorValuesHistory = false
    }
  },
  watch: {
    options: {
      handler () {
        this.fetchCodelists()
      },
      deep: true
    },
    search () {
      this.fetchTerms()
    },
    selectedTerms () {
      this.fetchCodelists()
    },
    termsFilterOperator () {
      this.fetchCodelists()
    },
    package (newValue, oldValue) {
      if (newValue !== oldValue) {
        this.codelists = []
        this.fetchCodelists()
      }
    }
  }
}
</script>
<style scoped>
.max-width-100 {
  max-width: 100px;
}
.max-width-300 {
  max-width: 300px;
}
</style>
