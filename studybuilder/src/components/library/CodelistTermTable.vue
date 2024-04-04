<template>
  <div>
    <codelist-summary :codelist-names="codelistNames" :codelist-attributes="codelistAttributes"/>
    <n-n-table
      :headers="headers"
      :items="terms"
      :server-items-length="total"
      :options.sync="options"
      export-data-url="ct/terms"
      :export-data-url-params="exportUrlParams"
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
          small
          color="primary"
          data-cy="add-term-button"
          @click.stop="showCreationForm = true"
          :title="$t('CodelistTermCreationForm.title')"
          :disabled="!checkPermission($roles.LIBRARY_WRITE)">
          <v-icon dark>
            mdi-plus
          </v-icon>
        </v-btn>
      </template>
      <template v-slot:item.name.status="{ item }">
        <status-chip :status="item.name.status" />
      </template>
      <template v-slot:item.name.start_date="{ item }">
        {{ item.name.start_date | date }}
      </template>
      <template v-slot:item.attributes.status="{ item }">
        <status-chip :status="item.attributes.status" />
      </template>
      <template v-slot:item.attributes.start_date="{ item }">
        {{ item.attributes.start_date | date }}
      </template>
      <template v-slot:item.actions="{ item }">
        <actions-menu :actions="actions" :item="item" />
      </template>
    </n-n-table>
    <v-dialog v-model="showCreationForm" persistent max-width="1024px" content-class="top-dialog">
      <codelist-term-creation-form :catalogueName="codelistNames.catalogue_name"
        :codelistUid="codelistNames.codelist_uid" @close="closeForm" @created="goToTerm" />
    </v-dialog>
    <v-dialog v-model="showHistory" @keydown.esc="closeHistory" persistent :max-width="globalHistoryDialogMaxWidth" :fullscreen="globalHistoryDialogFullscreen">
      <history-table :title="historyTitleLabel" @close="closeHistory" :headers="historyHeaders" :items="historyItems" />
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
import HistoryTable from '@/components/tools/HistoryTable'
import NNTable from '@/components/tools/NNTable'
import StatusChip from '@/components/tools/StatusChip'
import filteringParameters from '@/utils/filteringParameters'
import { accessGuard } from '@/mixins/accessRoleVerifier'

export default {
  mixins: [accessGuard],
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
        ? this.$t('CodelistTermTable.history_label_name', { term: this.selectedTerm.term_uid })
        : this.$t('CodelistTermTable.history_label_attributes', { term: this.selectedTerm.term_uid })
    },
    exportUrlParams () {
      return { codelist_uid: this.codelistUid }
    }
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.editTerm
        },
        {
          label: this.$t('CtCatalogueTable.remove_term'),
          icon: 'mdi-delete-outline',
          iconColor: 'primary',
          click: this.removeTerm,
          accessRole: this.$roles.LIBRARY_WRITE,
          condition: () => this.codelistAttributes.extensible
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
        { text: this.$t('CodelistTermsView.sponsor_name'), value: 'name.sponsor_preferred_name' },
        { text: this.$t('_global.order'), value: '_order' },
        { text: this.$t('CodelistTermsView.name_status'), value: 'name.status' },
        { text: this.$t('CodelistTermsView.name_date'), value: 'name.start_date' },
        { text: this.$t('CtCatalogueTable.concept_id'), value: '_concept_id' },
        { text: this.$t('CodelistTermsView.code_submission_value'), value: 'attributes.code_submission_value' },
        { text: this.$t('CodelistTermsView.name_submission_value'), value: 'attributes.name_submission_value' },
        { text: this.$t('CtCatalogueTable.nci_pref_name'), value: 'attributes.nci_preferred_name' },
        { text: this.$t('_global.definition'), value: 'attributes.definition' },
        { text: this.$t('CodelistTermsView.attr_status'), value: 'attributes.status' },
        { text: this.$t('CodelistTermsView.attr_date'), value: 'attributes.start_date' }
      ],
      historyItems: [],
      historyHeaders: [],
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
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      if (this.packageName !== undefined) {
        params.package = this.packageName
      }
      params.codelist_uid = this.codelistUid
      terms.getAll(params).then(resp => {
        this.terms = resp.data.items
        this.total = resp.data.total
        // Sponsor terms do not have a concept id.
        // Show the term uid for these.
        for (const term of this.terms) {
          if (term.attributes.concept_id === null) {
            term._concept_id = term.term_uid
          } else {
            term._concept_id = term.attributes.concept_id
          }
          term._order = this.getTermOrderInCodelist(term, this.codelistUid)
        }
      })
    },
    removeTerm (term) {
      controlledTerminology.removeTermFromCodelist(this.codelistUid, term.term_uid).then(() => {
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
    async openSponsorValuesHistory (term) {
      this.selectedTerm = term
      this.historyType = 'termName'
      this.historyHeaders = [
        { text: this.$t('CodeListDetail.sponsor_pref_name'), value: 'sponsor_preferred_name' },
        { text: this.$t('CodelistTermDetail.sentence_case_name'), value: 'sponsor_preferred_name_sentence_case' },
        { text: this.$t('CodelistTermDetail.order'), value: 'order' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ]
      const resp = await controlledTerminology.getCodelistTermNamesVersions(this.selectedTerm.term_uid)
      this.historyItems = resp.data.map(item => {
        item.order = this.getTermOrderInCodelist(item, this.codelistUid)
        return item
      })
      this.showHistory = true
    },
    async openCTValuesHistory (term) {
      this.selectedTerm = term
      this.historyType = 'termAttributes'
      this.historyHeaders = [
        { text: this.$t('CodelistTermDetail.concept_id'), value: 'term_uid' },
        { text: this.$t('CodelistTermDetail.name_submission_value'), value: 'name_submission_value' },
        { text: this.$t('CodelistTermDetail.code_submission_value'), value: 'code_submission_value' },
        { text: this.$t('CodeListDetail.nci_pref_name'), value: 'nci_preferred_name' },
        { text: this.$t('_global.definition'), value: 'definition' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ]
      const resp = await controlledTerminology.getCodelistTermAttributesVersions(this.selectedTerm.term_uid)
      this.historyItems = resp.data
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
