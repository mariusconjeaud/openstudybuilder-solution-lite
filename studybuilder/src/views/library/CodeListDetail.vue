<template>
<div class="px-4">
  <div class="mb-6 d-flex align-center">
    <strong>{{ $t('_global.library') }}</strong> <span class="ml-2 secondary--text">{{ codelistNames.library_name }}</span>
    <v-spacer />
    <strong>{{ $t('CodeListDetail.concept_id') }}</strong> <span class="ml-2 secondary--text">{{ codelistNames.codelist_uid }}</span>
    <v-spacer />
    <v-speed-dial
      v-model="actionsMenu"
      direction="left"
      transition="transition-slide-x-reverse"
      >
      <template v-slot:activator>
        <v-btn
          data-cy="table-actions-button"
          v-model="actionsMenu"
          color="primary"
          fab
          >
          <v-icon>
            mdi-menu
          </v-icon>
        </v-btn>
      </template>
      <v-btn
        fab
        dark
        small
        :title="$t('CodelistTable.show_terms')"
        @click="openCodelistTerms()"
        >
        <v-icon>mdi-dots-horizontal</v-icon>
      </v-btn>
      <v-btn
        class="mx-2"
        color="secondary"
        fab
        small
        >
        <v-icon>mdi-history</v-icon>
      </v-btn>
      <data-table-export-button type="endpoint" dataUrl="" />
      <v-btn
        data-cy="add-new-term"
        v-if="attributes.extensible"
        class="mx-2"
        fab
        dark
        small
        color="primary"
        @click.stop="showCreationForm = true"
        :title="$t('CodelistTermsView.add_term')"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </v-speed-dial>
  </div>
  <div class="v-label pa-4">{{ $t('CodeListDetail.sponsor_title') }}</div>
  <div class="v-data-table">
    <div class="v-data-table__wrapper">
      <table class="white">
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
                <v-icon>mdi-pencil</v-icon>
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
                @click="openHistory"
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
      <table class="white">
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
                <v-icon>mdi-pencil</v-icon>
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
            persistent
            max-width="800px"
            >
    <codelist-sponsor-values-form
      v-model="codelistNames"
      @close="showSponsorValuesForm = false"
      />
  </v-dialog>
  <v-dialog v-model="showAttributesForm"
            persistent
            max-width="800px"
            >
    <codelist-attributes-form
      v-model="attributes"
      @close="showAttributesForm = false"
      />
  </v-dialog>
  <v-dialog v-model="showSponsorValuesHistory"
            persistent
            max-width="1200px">
    <history-table
      @close="closeHistory()"
      type="codelistSponsorValues"
      url-prefix=""
      :item="historyData"
      :title-label="$t('CodelistTable.history_title')"
      :headers="historyHeaders"
      />
  </v-dialog>
  <v-dialog v-model="showAttributesHistory"
            persistent
            max-width="1200px">
    <history-table
      @close="closeHistory()"
      type="codelistAttributes"
      url-prefix=""
      :item="historyData"
      :title-label="$t('CodelistTable.history_title')"
      :headers="historyHeaders"
      />
  </v-dialog>
  <v-dialog
    v-if="attributes.extensible"
    v-model="showCreationForm"
    persistent
    max-width="1024px"
    content-class="top-dialog"
    >
    <codelist-term-creation-form
      :catalogueName="codelistNames.catalogue_name"
      :codelistUid="codelistNames.codelist_uid"
      :libraryName="codelistNames.library_name"
      @close="showCreationForm = false"
      @created="goToTerm"
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
import CodelistTermCreationForm from '@/components/library/CodelistTermCreationForm'
import DataTableExportButton from '@/components/tools/DataTableExportButton'
import HistoryTable from '@/components/library/HistoryTable'
import StatusChip from '@/components/tools/StatusChip'

export default {
  components: {
    CodelistAttributesForm,
    CodelistSponsorValuesForm,
    CodelistTermCreationForm,
    DataTableExportButton,
    HistoryTable,
    StatusChip
  },
  data () {
    return {
      actionsMenu: false,
      attributes: { possible_actions: [] },
      codelistNames: { possible_actions: [] },
      historyHeaders: [
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('HistoryTable.change_description'), value: 'change_description' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' },
        { text: this.$t('_global.user'), value: 'user_initials' },
        { text: this.$t('HistoryTable.start_date'), value: 'start_date' },
        { text: this.$t('HistoryTable.end_date'), value: 'endDate' }
      ],
      showAttributesForm: false,
      showAttributesHistory: false,
      showCreationForm: false,
      showSponsorValuesForm: false,
      showSponsorValuesHistory: false,
      historyData: {}
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
    openHistory () {
      this.historyData = this.codelistNames
      this.showSponsorValuesHistory = true
    },
    closeHistory () {
      this.historyData = {}
      this.showSponsorValuesHistory = false
      this.showAttributesHistory = false
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
    openAttributesHistory () {
      this.historyData = this.attributes
      this.showAttributesHistory = true
    },
    goToTerm (term) {
      this.$router.push({ name: 'CodelistTermDetail', params: { codelist_id: term.codelist_uid, term_id: term.term_uid } })
      bus.$emit('notification', { msg: this.$t('CodelistTermCreationForm.add_success') })
    },
    openCodelistTerms () {
      this.$router.push({ name: 'CodelistTerms', params: { codelist_id: this.codelistNames.codelist_uid } })
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
