<template>
<div>
  <codelist-summary :codelist-names="codelistNames" :codelist-attributes="codelistAttributes" />
  <n-n-table
    :headers="headers"
    :items="terms"
    :server-items-length="total"
    :options.sync="options"
    export-data-url="ct/terms"
    export-object-label="Terms"
    item-key="term_uid"
    height="40vh"
    class="mt-4"
    has-api
    @filter="fetchTerms"
    column-data-resource="ct/terms"
    :codelist-uid="codelistUid"
    >
    <template v-slot:actions="">
      <v-btn
        v-if="codelistAttributes.extensible"
        fab
        dark
        small
        color="primary"
        data-cy="add-term-button"
        @click.stop="showCreationForm = true"
        :title="$t('CodelistTermCreationForm.title')"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:item.name.status="{ item }">
      <status-chip :status="item.name.status" />
    </template>
    <template v-slot:item.name.start_date="{ item }">
      {{ item.name.start_date|date }}
    </template>
    <template v-slot:item.attributes.status="{ item }">
      <status-chip :status="item.attributes.status" />
    </template>
    <template v-slot:item.attributes.start_date="{ item }">
      {{ item.attributes.start_date|date }}
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
  </n-n-table>
  <v-dialog
    v-model="showCreationForm"
    persistent
    max-width="1024px"
    content-class="top-dialog"
    >
    <codelist-term-creation-form
      :catalogueName="codelistNames.catalogue_name"
      :codelistUid="codelistNames.codelist_uid"
      @close="closeForm"
      @created="goToTerm"
      />
  </v-dialog>
  <v-dialog
    v-model="showHistory"
    persistent
    max-width="1200px"
    >
    <history-table
      @close="closeHistory"
      :type="historyType"
      url-prefix="terms/"
      :url-suffix="historyUrlSuffix"
      :item="selectedTerm"
      :title-label="historyTitleLabel"
      />
  </v-dialog>
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import { bus } from '@/main'
import controlledTerminology from '@/api/controlledTerminology'
import terms from '@/api/controlledTerminology/terms'
import ActionsMenu from '@/components/tools/ActionsMenu'
import CodelistSummary from '@/components/library/CodelistSummary'
import CodelistTermCreationForm from '@/components/library/CodelistTermCreationForm'
import HistoryTable from '@/components/library/HistoryTable'
import NNTable from '@/components/tools/NNTable'
import StatusChip from '@/components/tools/StatusChip'

export default {
  props: ['codelistUid', 'packageName', 'catalogueName'],
  components: {
    ActionsMenu,
    CodelistSummary,
    CodelistTermCreationForm,
    HistoryTable,
    NNTable,
    StatusChip
  },
  computed: {
    ...mapGetters({
      currentCatalogue: 'ctCatalogues/currentCatalogue'
    }),
    historyTitleLabel () {
      return (this.historyType === 'termName')
        ? this.$t('CodelistTermTable.history_label_name')
        : this.$t('CodelistTermTable.history_label_attributes')
    },
    historyUrlSuffix () {
      return (this.historyType === 'termName') ? 'names' : 'attributes'
    }
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil',
          iconColor: 'primary',
          click: this.editTerm
        },
        {
          label: this.$t('CtCatalogueTable.remove_term'),
          icon: 'mdi-delete',
          iconColor: 'primary',
          click: this.removeTerm,
          condition: (item) => this.codelistAttributes.extensible
        },
        {
          label: this.$t('CodelistTermTable.open_sponsor_history'),
          icon: 'mdi-history',
          click: this.openSponsorValuesHistory
        },
        {
          label: this.$t('CodelistTermTable.open_ct_history'),
          icon: 'mdi-history',
          click: this.openCTValuesHistory
        }
      ],
      codelistNames: {},
      codelistAttributes: {},
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('CtCatalogueTable.concept_id'), value: 'term_uid' },
        { text: this.$t('CodelistTermsView.sponsor_name'), value: 'name.sponsor_preferred_name' },
        { text: this.$t('_global.order'), value: 'name.order' },
        { text: this.$t('CodelistTermsView.name_status'), value: 'name.status' },
        { text: this.$t('CodelistTermsView.name_date'), value: 'name.start_date' },
        { text: this.$t('CodelistTermsView.name_submission_value'), value: 'attributes.name_submission_value' },
        { text: this.$t('CodelistTermsView.code_submission_value'), value: 'attributes.code_submission_value' },
        { text: this.$t('CtCatalogueTable.nci_pref_name'), value: 'attributes.nci_preferred_name' },
        { text: this.$t('_global.definition'), value: 'attributes.definition' },
        { text: this.$t('CodelistTermsView.attr_status'), value: 'attributes.status' },
        { text: this.$t('CodelistTermsView.attr_date'), value: 'attributes.start_date' }
      ],
      historyType: '',
      options: {},
      selectedTerm: {},
      showCreationForm: false,
      showHistory: false,
      terms: [],
      total: 0
    }
  },
  mounted () {
    controlledTerminology.getCodelistNames(this.codelistUid).then(resp => {
      this.codelistNames = resp.data
    })
    controlledTerminology.getCodelistAttributes(this.codelistUid).then(resp => {
      this.codelistAttributes = resp.data
    })
  },
  methods: {
    fetchTerms (filters, sort, filtersUpdated) {
      if (filtersUpdated) {
        this.options.page = 1
      }
      const params = {
        page_number: (this.options.page),
        page_size: this.options.itemsPerPage,
        total_count: true
      }
      if (this.packageName !== undefined) {
        params.package = this.packageName
      }
      if (filters !== undefined) {
        params.filters = this.filters
      }
      if (this.options.sortBy.length !== 0 && sort !== undefined) {
        params.sort_by = `{"${this.options.sortBy[0]}":${!sort}}`
      }
      params.codelist_uid = this.codelistUid
      terms.getAll(params).then(resp => {
        this.terms = resp.data.items
        this.total = resp.data.total
      })
    },
    removeTerm (term) {
      controlledTerminology.removeTermFromCodelist(this.codelistUid, term.term_uid).then(resp => {
        this.fetchTerms()
        bus.$emit('notification', { msg: this.$t('CodelistTermCreationForm.remove_success') })
      })
    },
    closeForm () {
      this.showCreationForm = false
      this.fetchTerms()
    },
    goToTerm (term) {
      this.editTerm(term)
      bus.$emit('notification', { msg: this.$t('CodelistTermCreationForm.add_success') })
    },
    editTerm (term) {
      if (this.packageName) {
        this.$router.push({
          name: 'CtPackageTermDetail',
          params: {
            catalogueName: this.catalogueName,
            packageName: this.packageName,
            codelistId: term.codelist_uid,
            termId: term.term_uid
          }
        })
      } else {
        this.$router.push({ name: 'CodelistTermDetail', params: { codelistId: term.codelist_uid, catalogue_name: this.catalogueName, term_id: term.term_uid } })
      }
    },
    openSponsorValuesHistory (term) {
      this.selectedTerm = term
      this.historyType = 'termName'
      this.showHistory = true
    },
    openCTValuesHistory (term) {
      this.selectedTerm = term
      this.historyType = 'termAttributes'
      this.showHistory = true
    },
    closeHistory () {
      this.showHistory = false
      this.historyType = ''
      this.selectedTerm = {}
    }
  },
  watch: {
    options: {
      handler () {
        this.fetchTerms()
      },
      deep: true
    },
    packageName (newValue, oldValue) {
      if (newValue !== oldValue) {
        this.fetchTerms()
      }
    }
  }

}
</script>
