<template>
<div>
  <n-n-table
    :headers="headers"
    :items="items"
    column-data-resource="studies"
    @filter="fetchStudySubparts"
    :server-items-length="total"
    item-key="uid"
    has-api
    :no-data-text="Boolean(selectedStudy.study_parent_part) ? $t('StudySubparts.nested_subparts_warning', {subpartStudyId: selectedStudy.current_metadata.identification_metadata.study_id, parentStudyId: selectedStudy.study_parent_part.study_id}): $t('NNTable.no_data')"
    :loading-watcher="loading"
    >
    <template v-slot:afterSwitches>
      <div :title="$t('NNTableTooltips.reorder_content')">
        <v-switch
          v-model="sortMode"
          :label="$t('NNTable.reorder_content')"
          hide-details
          class="mr-6"
          />
      </div>
    </template>
    <template v-slot:actions="">
      <v-btn
        fab
        small
        color="primary"
        @click.stop="openForm()"
        :title="$t('StudySubparts.add_subpart')"
        :disabled="!checkPermission($roles.STUDY_WRITE) || Boolean(selectedStudy.study_parent_part)"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
    <template v-slot:item.current_metadata.version_metadata.version_timestamp="{ item }">
      {{ item.current_metadata.version_metadata.version_timestamp | date }}
    </template>
    <template v-slot:body="props" v-if="sortMode">
      <draggable
        :list="props.items"
        tag="tbody"
        @change="onOrderChange($event)"
        >
        <tr
          v-for="(item, index) in props.items"
          :key="index"
          >
          <td>
            <actions-menu :actions="actions" :item="item" />
          </td>
          <td>
            {{ item.study_parent_part.study_id }}
          </td>
          <td>
            {{ item.study_parent_part.study_acronym }}
          </td>
          <td>
            {{ item.current_metadata.identification_metadata.study_number }}
          </td>
          <td>
            {{ item.current_metadata.identification_metadata.study_acronym }}
          </td>
          <td>
            {{ item.current_metadata.identification_metadata.description }}
          </td>
          <td>
            {{ item.current_metadata.version_metadata.version_timestamp | date }}
          </td>
          <td>
            {{ item.current_metadata.version_metadata.version_author }}
          </td>
        </tr>
      </draggable>
    </template>
  </n-n-table>
  <v-dialog
      v-model="form"
      persistent
      fullscreen
      content-class="fullscreen-dialog"
    >
    <study-subpart-form
      :edited-subpart="selectedSubpart"
      @close="closeForm()"/>
  </v-dialog>
  <v-dialog v-model="showHistory"
            @keydown.esc="closeHistory"
            persistent
            :max-width="globalHistoryDialogMaxWidth"
            :fullscreen="globalHistoryDialogFullscreen">
    <history-table
      title="History for Study Subpart xyz"
      @close="closeHistory"
      :headers="historyHeaders"
      :items="subpartHistoryItems"
      />
  </v-dialog>
</div>
</template>

<script>
import studies from '@/api/study'
import { bus } from '@/main'
import filteringParameters from '@/utils/filteringParameters'
import { mapGetters } from 'vuex'
import NNTable from '@/components/tools/NNTable'
import { accessGuard } from '@/mixins/accessRoleVerifier'
import StudySubpartForm from '@/components/studies/StudySubpartForm'
import ActionsMenu from '@/components/tools/ActionsMenu'
import HistoryTable from '@/components/tools/HistoryTable'
import draggable from 'vuedraggable'

export default {
  mixins: [accessGuard],
  components: {
    NNTable,
    StudySubpartForm,
    ActionsMenu,
    HistoryTable,
    draggable
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion'
    })
  },
  data () {
    return {
      items: [],
      options: {},
      total: 0,
      headers: [
        { text: '', value: 'actions', width: '5' },
        { text: this.$t('StudySubparts.study_id'), value: 'study_parent_part.study_id' },
        { text: this.$t('StudySubparts.study_acronym'), value: 'study_parent_part.study_acronym' },
        { text: this.$t('StudySubparts.subpart_id'), value: 'current_metadata.identification_metadata.study_number' },
        { text: this.$t('StudySubparts.subpart_acronym'), value: 'current_metadata.identification_metadata.study_acronym' },
        { text: this.$t('_global.description'), value: 'current_metadata.identification_metadata.description' },
        { text: this.$t('_global.modified'), value: 'current_metadata.version_metadata.version_timestamp' },
        { text: this.$t('_global.modified_by'), value: 'current_metadata.version_metadata.version_author' }
      ],
      historyHeaders: [
        { text: this.$t('HistoryTable.field'), value: 'field' },
        { text: this.$t('HistoryTable.value_before'), value: 'before_value.term_uid' },
        { text: this.$t('HistoryTable.value_after'), value: 'after_value.term_uid' },
        { text: this.$t('_global.user'), value: 'user_initials' }
      ],
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.editSubpart
        },
        {
          label: this.$t('_global.remove'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          accessRole: this.$roles.STUDY_WRITE,
          click: this.removeSubpart
        }
      ],
      form: false,
      selectedSubpart: {},
      subpartHistoryItems: [],
      showHistory: false,
      sortMode: false,
      loading: false
    }
  },
  mounted () {
    this.fetchStudySubparts()
  },
  methods: {
    fetchStudySubparts (filters, sort, filtersUpdated) {
      if (filters) {
        const filtersObj = JSON.parse(filters)
        filtersObj['study_parent_part.uid'] = { v: [this.selectedStudy.uid] }
        filters = JSON.stringify(filtersObj)
      } else {
        filters = { 'study_parent_part.uid': { v: [this.selectedStudy.uid] } }
      }
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      params.sort_by = { 'current_metadata.identification_metadata.study_number': true }
      studies.get(params).then(resp => {
        this.items = resp.data.items
        this.total = resp.data.total
        this.loading = false
      })
    },
    openForm () {
      this.form = true
    },
    closeForm () {
      this.selectedSubpart = {}
      this.form = false
      this.fetchStudySubparts()
    },
    editSubpart (subpart) {
      this.selectedSubpart = subpart
      this.form = true
    },
    removeSubpart (subpart) {
      delete subpart.current_metadata.study_description
      subpart.study_parent_part_uid = null
      studies.updateStudy(subpart.uid, subpart).then(resp => {
        this.fetchStudySubparts()
        bus.$emit('notification', { msg: this.$t('StudySubparts.substudy_removed') })
      })
    },
    async openHistory (subpart) {
      this.selectedSubpart = subpart
      const resp = await studies.getStudyFieldsAuditTrail(subpart.uid, 'identification_metadata')
      this.subpartHistoryItems = resp.data[0].actions
      this.showHistory = true
    },
    async closeHistory () {
      this.showHistory = false
    },
    async refreshData () {
      this.fetchStudySubparts()
    },
    onOrderChange (event) {
      this.loading = true
      const data = {
        uid: event.moved.element.uid,
        study_number: String.fromCharCode(event.moved.newIndex + 'A'.charCodeAt(0)).toLowerCase()
      }
      studies.reorderStudySubpart(this.selectedStudy.uid, data).then(() => {
        this.fetchStudySubparts()
      })
    }
  },
  watch: {
    options () {
      this.fetchStudySubparts()
    }
  }
}
</script>
