<template>
<div>
  <n-n-table
    :headers="headers"
    :items="items"
    :options.sync="options"
    column-data-resource="studies"
    @filter="fetchItems"
    hide-default-switches
    hide-export-button
    disable-filtering
    :server-items-length="total"
    >
    <template v-slot:actions="">
      <v-btn
        v-if="selectedStudy.current_metadata.version_metadata.study_status === 'DRAFT' && !selectedStudyVersion"
        fab
        small
        color="red"
        @click.stop="lockStudy"
        :title="$t('_global.lock')"
        data-cy="lock-study"
        :disabled="!checkPermission($roles.STUDY_WRITE)"
        >
        <v-icon>mdi-lock-outline</v-icon>
      </v-btn>
      <v-btn
        v-if="selectedStudy.current_metadata.version_metadata.study_status === 'DRAFT' && !selectedStudyVersion"
        fab
        small
        color="info"
        @click.stop="releaseStudy"
        :title="$t('_global.release')"
        data-cy="release-study"
        class="ml-2"
        :disabled="!checkPermission($roles.STUDY_WRITE)"
        >
        <v-icon>mdi-share-variant</v-icon>
      </v-btn>
      <v-btn
        v-if="selectedStudy.current_metadata.version_metadata.study_status === 'LOCKED' && selectedStudyVersion === latestStudyVersion"
        fab
        small
        color="green"
        @click.stop="unlockStudy"
        :title="$t('_global.unlock')"
        data-cy="unlock-study"
        :disabled="!checkPermission($roles.STUDY_WRITE)"
        >
        <v-icon>mdi-lock-open-outline</v-icon>
      </v-btn>
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu
        v-if="checkIfSelectable(item)"
        :actions="actions"
        :item="item"
        />
    </template>
    <template v-slot:item.current_metadata.version_metadata.study_status="{ item }">
      <status-chip
        :status="item.current_metadata.version_metadata.study_status"
        :outlined="false"
        />
    </template>
    <template v-slot:item.current_metadata.version_metadata.version_timestamp="{ item }">
      {{ item.current_metadata.version_metadata.version_timestamp|date }}
    </template>
  </n-n-table>
  <study-status-form
    :action="statusAction"
    :open="showStatusForm"
    @close="closeStatusForm"
    @statusChanged="refreshData"
    />
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import api from '@/api/study'
import { bus } from '@/main'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import filteringParameters from '@/utils/filteringParameters'
import { mapGetters } from 'vuex'
import NNTable from '@/components/tools/NNTable'
import StatusChip from '@/components/tools/StatusChip'
import StudyStatusForm from './StudyStatusForm'
import { accessGuard } from '@/mixins/accessRoleVerifier'
import ActionsMenu from '@/components/tools/ActionsMenu'

export default {
  mixins: [accessGuard],
  components: {
    ConfirmDialog,
    NNTable,
    StatusChip,
    StudyStatusForm,
    ActionsMenu
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion'
    })
  },
  data () {
    return {
      editedStudy: null,
      headers: [
        { text: '', value: 'actions', width: '5' },
        { text: this.$t('Study.status'), value: 'current_metadata.version_metadata.study_status' },
        { text: this.$t('_global.version'), value: 'current_metadata.version_metadata.version_number' },
        { text: this.$t('Study.release_description'), value: 'current_metadata.version_metadata.version_description' },
        { text: this.$t('_global.modified'), value: 'current_metadata.version_metadata.version_timestamp' },
        { text: this.$t('_global.modified_by'), value: 'current_metadata.version_metadata.version_author' }
      ],
      lockedHistory: [],
      options: {},
      showStatusForm: false,
      statusAction: null,
      items: [],
      total: 0,
      actions: [
        {
          label: this.$t('StudyTable.select'),
          icon: 'mdi-check-circle-outline',
          iconColor: 'primary',
          click: this.selectStudyVersion
        }
      ],
      latestStudyVersion: ''
    }
  },
  methods: {
    checkIfSelectable (studyVersion) {
      return studyVersion.current_metadata.version_metadata.version_number !== this.selectedStudyVersion ||
        studyVersion.current_metadata.version_metadata.study_status !== this.selectedStudy.current_metadata.version_metadata.study_status
    },
    selectStudyVersion (studyVersion) {
      this.$store.dispatch('studiesGeneral/selectStudy', { studyObj: studyVersion, forceReload: true })
    },
    closeEditForm () {
      this.showEditForm = false
      this.fetchItems()
    },
    closeStatusForm () {
      this.showStatusForm = false
    },
    fetchItems (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      api.getStudySnapshotHistory(this.selectedStudy.uid, params).then(resp => {
        this.items = resp.data.items
        this.total = resp.data.total
      })
      this.getLatestStudyVersion()
    },
    getLatestStudyVersion () {
      api.getStudy(this.selectedStudy.uid).then(resp => {
        this.latestStudyVersion = resp.data.current_metadata.version_metadata.version_number
      })
    },
    releaseStudy () {
      this.statusAction = 'release'
      this.showStatusForm = true
    },
    lockStudy () {
      this.statusAction = 'lock'
      this.showStatusForm = true
    },
    async refreshData () {
      this.fetchItems()
    },
    async unlockStudy () {
      const resp = await api.unlockStudy(this.selectedStudy.uid)
      this.$store.commit('studiesGeneral/SELECT_STUDY', { studyObj: resp.data })
      bus.$emit('notification', { msg: this.$t('StudyStatusTable.unlock_success'), type: 'success' })
      this.fetchItems()
    }
  },
  watch: {
    options () {
      this.fetchItems()
    }
  }
}
</script>
