<template>
<div class="px-4">
  <div class="mb-6 d-flex align-center">
    <strong>{{ $t('_global.library') }}</strong> <span class="ml-2 secondary--text">{{ codelistNames.library_name }}</span>
    <v-spacer />
    <strong>{{ $t('CodeListDetail.concept_id') }}</strong> <span class="ml-2 secondary--text">{{ codelistNames.codelist_uid }}</span>
    <v-spacer />
    <v-btn
      fab
      dark
      small
      :title="$t('CodelistTable.show_terms')"
      @click="openCodelistTerms()"
      >
      <v-icon>mdi-dots-horizontal</v-icon>
    </v-btn>
  </div>
  <div class="v-label pa-4">{{ $t('CodeListDetail.sponsor_title') }}</div>
  <div class="v-data-table">
    <div class="v-data-table__wrapper">
      <table class="white" :aria-label="$t('CodeListDetail.sponsor_title')">
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
            <td>{{ codelistNames.name }}</td>
            <td data-cy="names-status" rowspan="2"><status-chip :status="codelistNames.status" /></td>
            <td rowspan="2">{{ codelistNames.start_date|date }}</td>
            <td data-cy="names-version" rowspan="2">{{ codelistNames.version }}</td>
            <td rowspan="2">
              <v-btn
                data-cy="edit-sponsor-values"
                v-if="codelistNames.possible_actions.find(action => action === 'edit')"
                icon
                color="primary"
                :title="$t('CodeListDetail.edit_sponsor_values')"
                @click="editSponsorValues"
                >
                <v-icon>mdi-pencil-outline</v-icon>
              </v-btn>
              <v-btn
                data-cy='approve-sponsor-values'
                v-if="codelistNames.possible_actions.find(action => action === 'approve')"
                color="success"
                icon
                @click="approveSponsorValues"
                :title="$t('CodeListDetail.approve_sponsor_values_version')"
                >
                <v-icon>mdi-check-decagram</v-icon>
              </v-btn>
              <v-btn
                data-cy='create-new-sponsor-values'
                v-if="codelistNames.possible_actions.find(action => action === 'new_version')"
                color="primary"
                icon
                @click="createNewSponsorValuesVersion"
                :title="$t('CodeListDetail.new_version')"
                >
                <v-icon>mdi-plus-circle-outline</v-icon>
              </v-btn>
              <v-btn
                data-cy='sponsor-values-version-history'
                icon
                @click="openNamesHistory"
                :title="$t('CodeListDetail.history')"
                >
                <v-icon>mdi-history</v-icon>
              </v-btn>
            </td>
          </tr>
          <tr>
            <td>{{ $t('CodeListDetail.tpl_parameter') }}</td>
            <td>{{ codelistNames.template_parameter|yesno }}</td>
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
            <th width="45%">{{ $t('CodeListDetail.selected_values') }}</th>
            <th width="5%">{{ $t('_global.status') }}</th>
            <th width="10%">{{ $t('_global.modified') }}</th>
            <th width="5%">{{ $t('_global.version') }}</th>
            <th width="10%">{{ $t('_global.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{{ $t('CodeListDetail.codelist_name') }}</td>
            <td>{{ attributes.name }}</td>
            <td data-cy="attributes-status" rowspan="5"><status-chip :status="attributes.status" /></td>
            <td rowspan="5">{{ attributes.start_date|date }}</td>
            <td data-cy="attributes-version" rowspan="5">{{ attributes.version }}</td>
            <td rowspan="5">
              <v-btn
                v-if="attributes.possible_actions.find(action => action === 'edit')"
                icon
                color="primary"
                :title="$t('CodeListDetail.edit_sponsor_values')"
                @click="editAttributes"
                >
                <v-icon>mdi-pencil-outline</v-icon>
              </v-btn>
              <v-btn
                data-cy="approve-attributes-values"
                v-if="attributes.possible_actions.find(action => action === 'approve')"
                color="success"
                icon
                @click="approveAttributes"
                :title="$t('CodeListDetail.approve_attributes_version')"
                >
                <v-icon>mdi-check-decagram</v-icon>
              </v-btn>
              <v-btn
                v-if="attributes.possible_actions.find(action => action === 'new_version')"
                color="primary"
                icon
                @click="createNewAttributesVersion"
                :title="$t('CodeListDetail.new_attributes_version')"
                >
                <v-icon>mdi-plus-circle-outline</v-icon>
              </v-btn>
              <v-btn
                icon
                @click="openAttributesHistory"
                :title="$t('CodeListDetail.history')"
                >
                <v-icon>mdi-history</v-icon>
              </v-btn>
            </td>
          </tr>
          <tr>
            <td>{{ $t('CodeListDetail.submission_value') }}</td>
            <td>{{ attributes.submission_value }}</td>
          </tr>
          <tr>
            <td>{{ $t('CodeListDetail.nci_pref_name') }}</td>
            <td>{{ attributes.nci_preferred_name }}</td>
          </tr>
          <tr>
            <td>{{ $t('CodeListDetail.extensible') }}</td>
            <td>{{ attributes.extensible|yesno }}</td>
          </tr>
          <tr>
            <td>{{ $t('CodeListDetail.definition') }}</td>
            <td>{{ attributes.definition }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <v-dialog v-model="showSponsorValuesForm"
            @keydown.esc="showSponsorValuesForm = false"
            persistent
            max-width="800px"
            >
    <codelist-sponsor-values-form
      v-model="codelistNames"
      @close="showSponsorValuesForm = false"
      />
  </v-dialog>
  <v-dialog v-model="showAttributesForm"
            @keydown.esc="showAttributesForm = false"
            persistent
            max-width="800px"
            >
    <codelist-attributes-form
      v-model="attributes"
      @close="showAttributesForm = false"
      />
  </v-dialog>
  <v-dialog v-model="showHistory"
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
import { mapActions } from 'vuex'
import { bus } from '@/main'
import controlledTerminology from '@/api/controlledTerminology'
import CodelistAttributesForm from '@/components/library/CodelistAttributesForm'
import CodelistSponsorValuesForm from '@/components/library/CodelistSponsorValuesForm'
import dataFormating from '@/utils/dataFormating'
import HistoryTable from '@/components/tools/HistoryTable'
import StatusChip from '@/components/tools/StatusChip'

export default {
  components: {
    CodelistAttributesForm,
    CodelistSponsorValuesForm,
    HistoryTable,
    StatusChip
  },
  computed: {
    namesHistoryTitle () {
      return this.$t('CodeListDetail.names_history_title', { codelist: this.codelistNames.codelist_uid })
    },
    attributesHistoryTitle () {
      return this.$t('CodeListDetail.attributes_history_title', { codelist: this.attributes.codelist_uid })
    }
  },
  data () {
    return {
      actionsMenu: false,
      attributes: { possible_actions: [] },
      codelistNames: { possible_actions: [] },
      attributesHistoryHeaders: [
        { text: this.$t('CodeListDetail.codelist_name'), value: 'name' },
        { text: this.$t('CodeListDetail.submission_value'), value: 'submission_value' },
        { text: this.$t('CodeListDetail.nci_pref_name'), value: 'nci_preferred_name' },
        { text: this.$t('CodeListDetail.extensible'), value: 'extensible' },
        { text: this.$t('_global.definition'), value: 'definition' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      historyHeaders: [],
      historyItems: [],
      historyTitle: '',
      namesHistoryHeaders: [
        { text: this.$t('CodeListDetail.sponsor_pref_name'), value: 'name' },
        { text: this.$t('CodeListDetail.tpl_parameter'), value: 'template_parameter' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }

      ],
      showAttributesForm: false,
      showHistory: false,
      showSponsorValuesForm: false,
      showSponsorValuesHistory: false
    }
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    }),
    editSponsorValues () {
      this.showSponsorValuesForm = true
    },
    editAttributes () {
      this.showAttributesForm = true
    },
    createNewSponsorValuesVersion () {
      controlledTerminology.newCodelistNamesVersion(this.codelistNames.codelist_uid).then(resp => {
        this.codelistNames = resp.data
        bus.$emit('notification', { msg: this.$t('CodeListDetail.new_version_success') })
      })
    },
    approveSponsorValues () {
      controlledTerminology.approveCodelistNames(this.codelistNames.codelist_uid).then(resp => {
        this.codelistNames = resp.data
        bus.$emit('notification', { msg: this.$t('CodeListDetail.sponsor_values_approve_success') })
      })
    },
    async openNamesHistory () {
      this.historyTitle = this.namesHistoryTitle
      this.historyHeaders = this.namesHistoryHeaders
      const resp = await controlledTerminology.getCodelistNamesVersions(this.codelistNames.codelist_uid)
      this.historyItems = this.transformHistoryItems(resp.data)
      this.showHistory = true
    },
    closeHistory () {
      this.showHistory = false
    },
    createNewAttributesVersion () {
      controlledTerminology.newCodelistAttributesVersion(this.attributes.codelist_uid).then(resp => {
        this.attributes = resp.data
        bus.$emit('notification', { msg: this.$t('CodeListDetail.new_attributes_version_success') })
      })
    },
    approveAttributes () {
      controlledTerminology.approveCodelistAttributes(this.attributes.codelist_uid).then(resp => {
        this.attributes = resp.data
        bus.$emit('notification', { msg: this.$t('CodeListDetail.attributes_approve_success') })
      })
    },
    async openAttributesHistory () {
      this.historyTitle = this.attributesHistoryTitle
      this.historyHeaders = this.attributesHistoryHeaders
      const resp = await controlledTerminology.getCodelistAttributesVersions(this.attributes.codelist_uid)
      this.historyItems = this.transformHistoryItems(resp.data)
      this.showHistory = true
    },
    goToTerm (term) {
      this.$router.push({ name: 'CodelistTermDetail', params: { codelist_id: term.codelist_uid, term_id: term.term_uid } })
      bus.$emit('notification', { msg: this.$t('CodelistTermCreationForm.add_success') })
    },
    openCodelistTerms () {
      this.$router.push({ name: 'CodelistTerms', params: { codelist_id: this.codelistNames.codelist_uid } })
    },
    transformHistoryItems (items) {
      const result = []
      for (const item of items) {
        const newItem = { ...item }
        if (newItem.template_parameter !== undefined) {
          newItem.template_parameter = dataFormating.yesno(newItem.template_parameter)
        }
        if (newItem.extensible !== undefined) {
          newItem.extensible = dataFormating.yesno(newItem.extensible)
        }
        result.push(newItem)
      }
      return result
    }
  },
  mounted () {
    controlledTerminology.getCodelistNames(this.$route.params.codelist_id).then(resp => {
      this.codelistNames = resp.data
      this.addBreadcrumbsLevel({
        text: this.codelistNames.codelist_uid,
        to: { name: 'CodeListDetail', params: this.$route.params },
        index: 4
      })
    })
    controlledTerminology.getCodelistAttributes(this.$route.params.codelist_id).then(resp => {
      this.attributes = resp.data
    })
  }
}
</script>
