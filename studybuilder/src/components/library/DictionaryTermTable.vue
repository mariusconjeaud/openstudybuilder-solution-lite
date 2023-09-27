<template>
<div>
  <n-n-table
    :headers="actualHeaders"
    :export-object-label="dictionaryName"
    :export-data-url="columnDataResource"
    :export-data-url-params="exportUrlParams"
    item-key="term_uid"
    :server-items-length="total"
    :options.sync="options"
    has-api
    :items="items"
    @filter="fetchTerms"
    :column-data-resource="columnDataResource"
    :codelistUid="codelistUid"
    >
    <template v-slot:actions="">
      <v-btn
        fab
        small
        color="primary"
        @click="createTerm()"
        :title="$t('DictionaryTermTable.add_title')"
        :disabled="!checkPermission($roles.LIBRARY_WRITE)"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:item.status="{ item }">
      <status-chip :status="item.status" />
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date | date }}
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item"/>
    </template>
  </n-n-table>
  <slot name="termForm" :closeForm="closeForm" :open="showTermForm">
    <dictionary-term-form
      :open="showTermForm"
      @close="closeForm"
      :dictionaryName="dictionaryName"
      :editedTerm="formToEdit"
      :editedTermCategory="codelistUid"
      @save="fetchTerms"
      />
  </slot>
</div>
</template>

<script>
import dictionaries from '@/api/dictionaries'
import ActionsMenu from '@/components/tools/ActionsMenu'
import DictionaryTermForm from '@/components/library/DictionaryTermForm'
import NNTable from '@/components/tools/NNTable'
import StatusChip from '@/components/tools/StatusChip'
import filteringParameters from '@/utils/filteringParameters'
import { accessGuard } from '@/mixins/accessRoleVerifier'

export default {
  mixins: [accessGuard],
  components: {
    ActionsMenu,
    DictionaryTermForm,
    NNTable,
    StatusChip
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: (item) => item.possible_actions.find(action => action === 'approve'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.approveTerm
        },
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'edit'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.editTerm
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'new_version'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.newTermVersion
        },
        {
          label: this.$t('_global.inactivate'),
          icon: 'mdi-close-octagon-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'inactivate'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.inactivateTerm
        },
        {
          label: this.$t('_global.reactivate'),
          icon: 'mdi-undo-variant',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'reactivate'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.reactivateTerm
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          condition: (item) => item.possible_actions.find(action => action === 'delete'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.deleteTerm
        }
      ],
      defaultHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.dictionaryName, value: 'dictionary_id' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('DictionaryTermTable.lower_case_name'), value: 'name_sentence_case' },
        { text: this.$t('DictionaryTermTable.abbreviation'), value: 'abbreviation' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' },
        { text: this.$t('_global.modified'), value: 'start_date' }
      ],
      total: 0,
      options: {},
      items: [],
      showTermForm: false,
      formToEdit: {}
    }
  },
  props: {
    codelistUid: String,
    columnDataResource: String,
    dictionaryName: String,
    headers: {
      type: Array,
      required: false
    }
  },
  computed: {
    actualHeaders () {
      return (this.headers) ? this.headers : this.defaultHeaders
    },
    exportUrlParams () {
      return { codelist_uid: this.codelistUid }
    }
  },
  methods: {
    fetchTerms (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      params.codelist_uid = this.codelistUid
      if (params.codelist_uid !== null) {
        dictionaries.getTerms(params).then(resp => {
          this.items = resp.data.items
          this.total = resp.data.total
        })
      }
    },
    inactivateTerm (item) {
      dictionaries.inactivate(item.term_uid).then(resp => {
        this.fetchTerms()
      })
    },
    reactivateTerm (item) {
      dictionaries.reactivate(item.term_uid).then(resp => {
        this.fetchTerms()
      })
    },
    deleteTerm (item) {
      dictionaries.delete(item.term_uid).then(resp => {
        this.fetchTerms()
      })
    },
    approveTerm (item) {
      dictionaries.approve(item.term_uid).then(resp => {
        this.fetchTerms()
      })
    },
    newTermVersion (item) {
      dictionaries.newVersion(item.term_uid).then(resp => {
        this.fetchTerms()
      })
    },
    editTerm (item) {
      this.formToEdit = item
      this.showTermForm = true
    },
    createTerm () {
      this.formToEdit = null
      this.showTermForm = true
    },
    closeForm () {
      this.formToEdit = null
      this.showTermForm = false
    }
  },
  watch: {
    options: {
      handler () {
        this.fetchTerms()
      },
      deep: true
    },
    codelistUid () {
      this.fetchTerms()
    }
  }
}
</script>
