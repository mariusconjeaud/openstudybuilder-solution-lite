<template>
<div>
  <div class="mt-4 mb-6 d-flex align-center">
    <v-spacer />
    <v-speed-dial
      v-model="actionsMenu"
      direction="left"
      transition="transition-slide-x-reverse"
      >
      <template v-slot:activator>
        <v-btn
          v-model="actionsMenu"
          color="primary"
          fab
          >
          <v-icon>
            mdi-menu
          </v-icon>
        </v-btn>
      </template>
      <data-table-export-button type="endpoint" dataUrl="" />
      <v-btn
        v-if="codelistAttributes.extensible"
        class="mx-2"
        fab
        dark
        small
        color="primary"
        @click.stop="showCreationForm = true"
        :title="$t('CodelistTermDetail.add_term')"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </v-speed-dial>
  </div>
  <codelist-summary :codelist-names="codelistNames" :codelist-attributes="codelistAttributes" />
  <div class="pa-4 v-label">{{ $t('CodelistTermDetail.sponsor_title') }}</div>
  <div class="v-data-table">
    <div class="v-data-table__wrapper">
      <table class="white" :aria-label="$t('CodelistTermDetail.sponsor_title')">
        <thead>
          <tr class="greyBackground">
            <th width="25%">{{ $t('CodeListDetail.ct_identifiers') }}</th>
            <th width="50%">{{ $t('CodeListDetail.selected_values') }}</th>
            <th width="5%">{{ $t('_global.status') }}</th>
            <th width="10%">{{ $t('_global.modified') }}</th>
            <th width="5%">{{ $t('_global.version') }}</th>
            <th width="5%">{{ $t('_global.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{{ $t('CodeListDetail.sponsor_pref_name') }}</td>
            <td>{{ termNames.sponsor_preferred_name }}</td>
            <td data-cy="names-status" rowspan="2"><status-chip :status="termNames.status" /></td>
            <td rowspan="2">{{ termNames.start_date|date }}</td>
            <td data-cy="names-version" rowspan="2">{{ termNames.version }}</td>
            <td rowspan="2">
              <v-btn
                data-cy="edit-sponsor-values"
                v-if="termNames.possible_actions.find(action => action === 'edit')"
                icon
                color="primary"
                :title="$t('CodelistTermDetail.edit_names')"
                @click="showNamesForm = true"
                >
                <v-icon>mdi-pencil-outline</v-icon>
              </v-btn>
              <v-btn
                data-cy="approve-term-sponsor-values"
                v-if="termNames.possible_actions.find(action => action === 'approve')"
                color="success"
                icon
                @click="approveTermNames"
                :title="$t('CodelistTermDetail.approve_names')"
                >
                <v-icon>mdi-check-decagram</v-icon>
              </v-btn>
              <v-btn
                data-cy='create-new-sponsor-values'
                v-if="termNames.possible_actions.find(action => action === 'new_version')"
                color="primary"
                icon
                @click="newTermNamesVersion"
                :title="$t('CodelistTermDetail.new_names_version')"
                >
                <v-icon>mdi-plus-circle-outline</v-icon>
              </v-btn>
              <v-btn
                color="warning"
                v-if="termNames.possible_actions.find(action => action === 'inactivate')"
                icon
                :title="$t('CodelistTermDetail.inactivate_names')"
                @click="inactivateTermNames"
                >
                <v-icon>mdi-close-octagon-outline</v-icon>
              </v-btn>
              <v-btn
                color="primary"
                v-if="termNames.possible_actions.find(action => action === 'reactivate')"
                icon
                :title="$t('CodelistTermDetail.reactivate_names')"
                @click="reactivateTermNames"
                >
                <v-icon>mdi-undo-variant</v-icon>
              </v-btn>
              <v-btn
                v-if="termNames.possible_actions.find(action => action === 'delete')"
                icon
                color="error"
                @click="deleteTermNames()"
                :title="$t('CodelistTermDetail.delete_names')"
                >
                <v-icon>mdi-delete-outline</v-icon>
              </v-btn>
              <v-btn
                data-cy="term-sponsor-version-history"
                icon
                @click="openSponsorValuesHistory"
                :title="$t('CodeListDetail.history')"
                >
                <v-icon>mdi-history</v-icon>
              </v-btn>
            </td>
          </tr>
          <tr>
            <td>{{ $t('CodelistTermDetail.sentence_case_name') }}</td>
            <td>{{ termNames.sponsor_preferred_name_sentence_case }}</td>
          </tr>
          <tr>
            <td>{{ $t('CodelistTermDetail.order') }}</td>
            <td>{{ termNames.order }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="v-label pa-4 mt-6">{{ $t('CodeListDetail.attributes_title') }}</div>
  <div class="v-data-table">
    <div class="v-data-table__wrapper">
      <table class="white" :aria-label="$t('CodeListDetail.attributes_title')">
        <thead>
          <tr class="greyBackground">
            <th width="25%">{{ $t('CodeListDetail.ct_identifiers') }}</th>
            <th width="50%">{{ $t('CodeListDetail.selected_values') }}</th>
            <th width="5%">{{ $t('_global.status') }}</th>
            <th width="10%">{{ $t('_global.modified') }}</th>
            <th width="5%">{{ $t('_global.version') }}</th>
            <th width="5%">{{ $t('_global.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{{ $t('CodelistTermDetail.concept_id') }}</td>
            <td>{{ termAttributes.term_uid }}</td>
                        <td data-cy="attributes-status" rowspan="5"><status-chip :status="termAttributes.status" /></td>
            <td rowspan="5">{{ termAttributes.start_date|date }}</td>
            <td data-cy="attributes-version" rowspan="5">{{ termAttributes.version }}</td>
            <td rowspan="5">
              <v-btn
                v-if="termAttributes.possible_actions.find(action => action === 'edit')"
                icon
                color="primary"
                :title="$t('CodelistTermDetail.edit_attributes')"
                @click="showAttributesForm = true"
                >
                <v-icon>mdi-pencil-outline</v-icon>
              </v-btn>
              <v-btn
                data-cy="approve-term-attributes-values"
                v-if="termAttributes.possible_actions.find(action => action === 'approve')"
                color="success"
                icon
                @click="approveTermAttributes"
                :title="$t('CodelistTermDetail.approve_attributes')"
                >
                <v-icon>mdi-check-decagram</v-icon>
              </v-btn>
              <v-btn
                v-if="termAttributes.possible_actions.find(action => action === 'new_version')"
                color="primary"
                icon
                @click="newTermAttributesVersion"
                :title="$t('CodelistTermDetail.new_attributes_version')"
                >
                <v-icon>mdi-plus-circle-outline</v-icon>
              </v-btn>
              <v-btn
                color="warning"
                v-if="termAttributes.possible_actions.find(action => action === 'inactivate')"
                icon
                :title="$t('CodelistTermDetail.inactivate_attributes')"
                @click="inactivateTermAttributes"
                >
                <v-icon>mdi-close-octagon-outline</v-icon>
              </v-btn>
              <v-btn
                color="primary"
                v-if="termAttributes.possible_actions.find(action => action === 'reactivate')"
                icon
                :title="$t('CodelistTermDetail.reactivate_attributes')"
                @click="reactivateTermAttributes"
                >
                <v-icon>mdi-undo-variant</v-icon>
              </v-btn>
              <v-btn
                v-if="termAttributes.possible_actions.find(action => action === 'delete')"
                icon
                color="error"
                @click="deleteTermAttributes()"
                :title="$t('CodelistTermDetail.delete_attributes')"
                >
                <v-icon>mdi-delete-outline</v-icon>
              </v-btn>
              <v-btn
                icon
                @click="openCTValuesHistory"
                :title="$t('CodeListDetail.history')"
                >
                <v-icon>mdi-history</v-icon>
              </v-btn>
            </td>
          </tr>
          <tr>
            <td>{{ $t('CodelistTermDetail.term_name') }}</td>
            <td>{{ termAttributes.name_submission_value }}</td>
          </tr>
          <tr>
            <td>{{ $t('CodelistTermDetail.submission_value') }}</td>
            <td>{{ termAttributes.code_submission_value }}</td>
          </tr>
          <tr>
            <td>{{ $t('CodelistTermDetail.nci_pref_name') }}</td>
            <td>{{ termAttributes.nci_preferred_name }}</td>
          </tr>
          <tr>
            <td>{{ $t('_global.definition') }}</td>
            <td>{{ termAttributes.definition }}</td>
          </tr>
          <tr>
            <td>{{ $t('CodelistTermDetail.synonyms') }}</td>
            <td>{{ termAttributes.synonyms }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <v-dialog
    v-model="showNamesForm"
    @keydown.esc="showNamesForm = false"
    persistent
    max-width="1024px"
    >
    <codelist-term-names-form
      v-model="termNames"
      @close="showNamesForm = false"
      />
  </v-dialog>
  <v-dialog
    v-model="showAttributesForm"
    @keydown.esc="showAttributesForm = false"
    persistent
    max-width="1024px"
    >
    <codelist-term-attributes-form
      v-model="termAttributes"
      @close="showAttributesForm = false"
      />
  </v-dialog>
  <v-dialog
    v-if="codelistAttributes.extensible"
    v-model="showCreationForm"
    persistent
    max-width="1024px"
    content-class="top-dialog"
    >
    <codelist-term-creation-form
      :catalogueName="codelistNames.catalogue_name"
      :codelistUid="codelistNames.codelist_uid"
      @close="showCreationForm = false"
      @created="goToTerm"
      />
  </v-dialog>
  <v-dialog
    v-model="showHistory"
    @keydown.esc="closeHistory"
    persistent
    :max-width="globalHistoryDialogMaxWidth"
    :fullscreen="globalHistoryDialogFullscreen"
    >
    <history-table
      :title="historyTitleLabel"
      @close="closeHistory"
      :headers="historyHeaders"
      :items="historyItems"
      />
  </v-dialog>
</div>
</template>

<script>
import { bus } from '@/main'
import controlledTerminology from '@/api/controlledTerminology'
import CodelistSummary from '@/components/library/CodelistSummary'
import CodelistTermAttributesForm from '@/components/library/CodelistTermAttributesForm'
import CodelistTermCreationForm from '@/components/library/CodelistTermCreationForm'
import CodelistTermNamesForm from '@/components/library/CodelistTermNamesForm'
import DataTableExportButton from '@/components/tools/DataTableExportButton'
import HistoryTable from '@/components/tools/HistoryTable'
import StatusChip from '@/components/tools/StatusChip'

export default {
  components: {
    CodelistSummary,
    CodelistTermAttributesForm,
    CodelistTermCreationForm,
    CodelistTermNamesForm,
    DataTableExportButton,
    HistoryTable,
    StatusChip
  },
  props: ['codelistUid', 'termUid'],
  computed: {
    historyTitleLabel () {
      return (this.historyType === 'termName')
        ? this.$t('CodelistTermTable.history_label_name', { term: this.termUid })
        : this.$t('CodelistTermTable.history_label_attributes', { term: this.termUid })
    }
  },
  data () {
    return {
      actionsMenu: false,
      codelistAttributes: {},
      codelistNames: {},
      historyType: '',
      historyItems: [],
      historyHeaders: [],
      showAttributesForm: false,
      showCreationForm: false,
      showHistory: false,
      showNamesForm: false,
      term: { term_uid: this.termUid },
      termNames: { possible_actions: [] },
      termAttributes: { possible_actions: [] }
    }
  },
  methods: {
    fetchTermNames () {
      controlledTerminology.getCodelistTermNames(this.termUid).then(resp => {
        this.termNames = resp.data
      })
    },
    newTermNamesVersion () {
      controlledTerminology.newCodelistTermNamesVersion(this.termNames.term_uid).then(resp => {
        this.termNames = resp.data
        bus.$emit('notification', { msg: this.$t('CodelistTermDetail.new_names_version_success') })
      })
    },
    approveTermNames () {
      controlledTerminology.approveCodelistTermNames(this.termNames.term_uid).then(resp => {
        this.termNames = resp.data
        bus.$emit('notification', { msg: this.$t('CodelistTermDetail.approve_names_success') })
      })
    },
    inactivateTermNames () {
      controlledTerminology.inactivateCodelistTermNames(this.termNames.term_uid).then(resp => {
        this.termNames = resp.data
        bus.$emit('notification', { msg: this.$t('CodelistTermDetail.inactivate_names_success') })
      })
    },
    reactivateTermNames () {
      controlledTerminology.reactivateCodelistTermNames(this.termNames.term_uid).then(resp => {
        this.termNames = resp.data
        bus.$emit('notification', { msg: this.$t('CodelistTermDetail.reactivate_names_success') })
      })
    },
    deleteTermNames () {
      controlledTerminology.deleteCodelistTermNames(this.termNames.term_uid).then(resp => {
        this.fetchTermNames()
        bus.$emit('notification', { msg: this.$t('CodelistTermDetail.delete_names_success') })
      })
    },
    fetchTermAttributes () {
      controlledTerminology.getCodelistTermAttributes(this.termUid).then(resp => {
        this.termAttributes = resp.data
      })
    },
    newTermAttributesVersion () {
      controlledTerminology.newCodelistTermAttributesVersion(this.termAttributes.term_uid).then(resp => {
        this.termAttributes = resp.data
        bus.$emit('notification', { msg: this.$t('CodelistTermDetail.new_attributes_version_success') })
      })
    },
    approveTermAttributes () {
      controlledTerminology.approveCodelistTermAttributes(this.termAttributes.term_uid).then(resp => {
        this.termAttributes = resp.data
        bus.$emit('notification', { msg: this.$t('CodelistTermDetail.approve_attributes_success') })
      })
    },
    inactivateTermAttributes () {
      controlledTerminology.inactivateCodelistTermAttributes(this.termAttributes.term_uid).then(resp => {
        this.termAttributes = resp.data
        bus.$emit('notification', { msg: this.$t('CodelistTermDetail.inactivate_attributes_success') })
      })
    },
    reactivateTermAttributes () {
      controlledTerminology.reactivateCodelistTermAttributes(this.termAttributes.term_uid).then(resp => {
        this.termAttributes = resp.data
        bus.$emit('notification', { msg: this.$t('CodelistTermDetail.reactivate_attributes_success') })
      })
    },
    deleteTermAttributes () {
      controlledTerminology.deleteCodelistTermAttributes(this.termNames.term_uid).then(resp => {
        this.fetchTermAttributes()
        bus.$emit('notification', { msg: this.$t('CodelistTermDetail.delete_attributes_success') })
      })
    },
    goToTerm (term) {
      this.$router.push({ name: 'CodelistTermDetail', params: { codelist_id: term.codelist_uid, term_id: term.term_uid } })
      bus.$emit('notification', { msg: this.$t('CodelistTermCreationForm.add_success') })
    },
    async openSponsorValuesHistory () {
      this.historyType = 'termName'
      this.historyHeaders = [
        { text: this.$t('CodeListDetail.sponsor_pref_name'), value: 'sponsor_preferred_name' },
        { text: this.$t('CodelistTermDetail.sentence_case_name'), value: 'sponsor_preferred_name_sentence_case' },
        { text: this.$t('CodelistTermDetail.order'), value: 'order' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ]
      const resp = await controlledTerminology.getCodelistTermNamesVersions(this.termUid)
      this.historyItems = resp.data
      this.showHistory = true
    },
    async openCTValuesHistory () {
      this.historyType = 'termAttributes'
      this.historyHeaders = [
        { text: this.$t('CodelistTermDetail.concept_id'), value: 'concept_id' },
        { text: this.$t('CodelistTermDetail.term_name'), value: 'name_submission_value' },
        { text: this.$t('CodelistTermDetail.submission_value'), value: 'code_submission_value' },
        { text: this.$t('CodeListDetail.nci_pref_name'), value: 'nci_preferred_name' },
        { text: this.$t('_global.definition'), value: 'definition' },
        { text: this.$t('CodelistTermDetail.synonyms'), value: 'synonyms' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ]
      const resp = await controlledTerminology.getCodelistTermAttributesVersions(this.termUid)
      this.historyItems = resp.data
      this.showHistory = true
    },
    closeHistory () {
      this.showHistory = false
      this.historyType = ''
    }
  },
  mounted () {
    controlledTerminology.getCodelistNames(this.codelistUid).then(resp => {
      this.codelistNames = resp.data
    })
    controlledTerminology.getCodelistAttributes(this.codelistUid).then(resp => {
      this.codelistAttributes = resp.data
    })
    this.fetchTermNames()
    this.fetchTermAttributes()
  }
}
</script>
