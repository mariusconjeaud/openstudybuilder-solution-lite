<template>
<div>
  <n-n-table
    key="studyActivityTable"
    ref="table"
    :headers="headers"
    :items="studyActivities"
    :server-items-length="total"
    item-key="study_activity_uid"
    export-object-label="StudyActivities"
    :export-data-url="exportDataUrl"
    :options.sync="options"
    @filter="getStudyActivities"
    has-api
    :column-data-resource="`studies/${selectedStudy.uid}/study-activities`"
    :history-data-fetcher="fetchActivitiesHistory"
    :history-title="$t('StudyActivityTable.global_history_title')"
    :extra-item-class="getItemRowClass"
    :filters-modify-function="modifyFilters"
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
    <template v-slot:actions="slot">
      <v-btn
        v-if="slot.showSelectBoxes"
        fab
        small
        color="primary"
        @click="openBatchEditForm(slot.selected)"
        :title="$t('StudyActivityTable.edit_activity_selection')"
        :disabled="!checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
        >
        <v-icon>
          mdi-pencil-box-multiple-outline
        </v-icon>
      </v-btn>
      <v-btn
        fab
        small
        class="ml-2"
        color="primary"
        data-cy="add-study-activity"
        @click.stop="showActivityForm = true"
        :title="$t('StudyActivityForm.add_title')"
        :disabled="!checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
        >
        <v-icon>
          mdi-plus
        </v-icon>
      </v-btn>
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
          :class="item.activity.library_name === libConstants.LIBRARY_REQUESTED ? 'warning' : ''"
          >
          <td v-if="props.showSelectBoxes">
            <v-checkbox
              :value="item.study_activity_uid"
              hide-details
              @change="props.select(!props.isSelected(item))"
              />
          </td>
          <td>
            <actions-menu
              :actions="actions"
              :item="item"
              />
          </td>
          <td>
            <v-icon
              small
              class="page__grab-icon"
              >
              mdi-sort
            </v-icon>
            {{ item.order }}
          </td>
          <td>{{ item.activity.library_name }}</td>
          <td>{{ item.study_soa_group.soa_group_name }}</td>
          <td>{{ item.study_activity_group.activity_group_name }}</td>
          <td>{{ item.study_activity_subgroup.activity_subgroup_name }}</td>
          <td>{{ item.activity.name }}</td>
          <td>{{ item.activity.is_data_collected|yesno }}</td>
          <td>{{ item.start_date|date }}</td>
          <td>{{ item.user_initials }}</td>
        </tr>
      </draggable>
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu
        :actions="getActionsForItem(item)"
        :item="item"
        :badge="actionsMenuBadge(item)"
        />
    </template>
    <template v-slot:item.activity.name="{ item }">
      <router-link :to="{ name: 'StudyActivityOverview', params: { study_id: selectedStudy.uid, id: item.study_activity_uid } }">
        {{ item.activity.name }}
      </router-link>
    </template>
    <template v-slot:item.activity.is_data_collected="{ item }">
      {{ item.activity.is_data_collected | yesno }}
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date | date }}
    </template>
  </n-n-table>
  <v-dialog
    v-model="showActivityForm"
    persistent
    fullscreen
    content-class="fullscreen-dialog"
    >
    <study-activity-form
      @close="closeForm"
      @added="onStudyActivitiesUpdated"
      class="fullscreen-dialog"
      />
  </v-dialog>
  <v-dialog
    v-model="showActivityEditForm"
    max-width="1000px"
    >
    <study-activity-edit-form
      @close="closeEditForm"
      :study-activity="selectedStudyActivity"
      @updated="onStudyActivitiesUpdated"
      class="fullscreen-dialog"
      />
  </v-dialog>
  <v-dialog v-model="showHistory"
            @keydown.esc="closeHistory"
            persistent
            :max-width="globalHistoryDialogMaxWidth"
            :fullscreen="globalHistoryDialogFullscreen">
    <history-table
      :title="activityHistoryTitle"
      @close="closeHistory"
      :headers="headers"
      :items="activityHistoryItems"
      />
  </v-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
  <study-activity-batch-edit-form
    :open="showBatchEditForm"
    :selection="currentSelection"
    @updated="onStudyActivitiesUpdated"
    @close="closeBatchEditForm"
    @remove="unselectItem"
    />
</div>
</template>

<script>
import { bus } from '@/main'
import draggable from 'vuedraggable'
import { mapGetters } from 'vuex'
import study from '@/api/study'
import ActionsMenu from '@/components/tools/ActionsMenu'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import filteringParameters from '@/utils/filteringParameters'
import HistoryTable from '@/components/tools/HistoryTable'
import NNTable from '@/components/tools/NNTable'
import StudyActivityBatchEditForm from './StudyActivityBatchEditForm'
import StudyActivityEditForm from './StudyActivityEditForm'
import StudyActivityForm from './StudyActivityForm'
import libConstants from '@/constants/libraries'
import { accessGuard } from '@/mixins/accessRoleVerifier'

export default {
  mixins: [accessGuard],
  components: {
    ActionsMenu,
    ConfirmDialog,
    draggable,
    NNTable,
    StudyActivityBatchEditForm,
    StudyActivityEditForm,
    StudyActivityForm,
    HistoryTable
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion'
    }),
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}/study-activities`
    },
    activityHistoryTitle () {
      if (this.selectedStudyActivity) {
        return this.$t(
          'StudyActivityTable.study_activity_history_title',
          { studyActivityUid: this.selectedStudyActivity.study_activity_uid })
      }
      return ''
    }
  },
  data () {
    return {
      libConstants: libConstants,
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          condition: () => !this.selectedStudyVersion,
          click: this.editStudyActivity,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          condition: () => !this.selectedStudyVersion,
          click: this.deleteStudyActivity,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openHistory
        }
      ],
      activityHistoryItems: [],
      currentSelection: [],
      selectedStudyActivity: null,
      showActivityEditForm: false,
      showActivityForm: false,
      showBatchEditForm: false,
      showHistory: false,
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: '#', value: 'order', width: '5%' },
        { text: this.$t('_global.library'), value: 'activity.library_name' },
        { text: this.$t('StudyActivity.flowchart_group'), value: 'study_soa_group.soa_group_name' },
        { text: this.$t('StudyActivity.activity_group'), value: 'study_activity_group.activity_group_name', externalFilterSource: 'concepts/activities/activity-groups$name', exludeFromHeader: ['activity.is_data_collected'] },
        { text: this.$t('StudyActivity.activity_sub_group'), value: 'study_activity_subgroup.activity_subgroup_name', externalFilterSource: 'concepts/activities/activity-sub-groups$name', exludeFromHeader: ['activity.is_data_collected'] },
        { text: this.$t('StudyActivity.activity'), value: 'activity.name' },
        { text: this.$t('StudyActivity.data_collection'), value: 'activity.is_data_collected' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.modified_by'), value: 'user_initials' }
      ],
      sortMode: false,
      studyActivities: [],
      options: {},
      total: 0
    }
  },
  methods: {
    getActionsForItem (item) {
      const result = [...this.actions]
      if (item.activity.replaced_by_activity) {
        result.unshift({
          label: this.$t('StudyActivityTable.update_activity_request'),
          icon: 'mdi-bell-outline',
          iconColor: 'red',
          click: this.updateActivityRequest
        })
      }
      return result
    },
    actionsMenuBadge (item) {
      if (item.activity.replaced_by_activity) {
        return {
          color: 'error',
          icon: 'mdi-exclamation'
        }
      }
      return undefined
    },
    closeForm () {
      this.showActivityForm = false
    },
    closeEditForm () {
      this.showActivityEditForm = false
      this.selectedStudyActivity = null
    },
    async deleteStudyActivity (sa) {
      const options = { type: 'warning' }
      const activity = sa.activity.name
      const msg = (!sa.show_activity_group_in_protocol_flowchart || !sa.show_activity_subgroup_in_protocol_flowchart)
        ? this.$t('StudyActivityTable.confirm_delete_side_effect')
        : this.$t('StudyActivityTable.confirm_delete', { activity })
      if (await this.$refs.confirm.open(msg, options)) {
        study.deleteStudyActivity(this.selectedStudy.uid, sa.study_activity_uid).then(() => {
          this.getStudyActivities()
          bus.$emit('notification', { type: 'success', msg: this.$t('StudyActivityTable.delete_success') })
        })
      }
    },
    editStudyActivity (sa) {
      this.selectedStudyActivity = sa
      this.showActivityEditForm = true
    },
    updateActivityRequest (sa) {
      study.updateToApprovedActivity(this.selectedStudy.uid, sa.study_activity_uid).then(() => {
        bus.$emit('notification', { type: 'success', msg: this.$t('StudyActivityTable.update_success') })
        this.getStudyActivities()
      })
    },
    async openHistory (sa) {
      this.selectedStudyActivity = sa
      const resp = await study.getStudyActivityAuditTrail(this.selectedStudy.uid, sa.study_activity_uid)
      this.activityHistoryItems = resp.data
      this.showHistory = true
    },
    closeHistory () {
      this.selectedStudyActivity = null
      this.showHistory = false
    },
    async getStudyActivities (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      if (filters && filters !== undefined && filters !== '{}') {
        const filtersObj = JSON.parse(filters)
        if (filtersObj['study_activity_group.activity_group_name']) {
          params.activity_group_names = []
          filtersObj['study_activity_group.activity_group_name'].v.forEach(value => {
            params.activity_group_names.push(value)
          })
          delete filtersObj['study_activity_group.activity_group_name']
        }
        if (filtersObj['study_activity_subgroup.activity_subgroup_name']) {
          params.activity_subgroup_names = []
          filtersObj['study_activity_subgroup.activity_subgroup_name'].v.forEach(value => {
            params.activity_subgroup_names.push(value)
          })
          delete filtersObj['study_activity_subgroup.activity_subgroup_name']
        }
        if (filtersObj.name) {
          params.activity_names = []
          filtersObj.name.v.forEach(value => {
            params.activity_names.push(value)
          })
          delete filtersObj.name
        }
        if (Object.keys(filtersObj).length) {
          params.filters = JSON.stringify(filtersObj)
        }
      }
      params.studyUid = this.selectedStudy.uid
      params.study_value_version = this.selectedStudyVersion
      const resp = await this.$store.dispatch('studyActivities/fetchStudyActivities', params)
      this.studyActivities = resp.data.items
      this.total = resp.data.total
    },
    modifyFilters (jsonFilter, params) {
      if (jsonFilter['study_activity_group.activity_group_name']) {
        params.activity_group_names = []
        jsonFilter['study_activity_group.activity_group_name'].v.forEach(value => {
          params.activity_group_names.push(value)
        })
        delete jsonFilter['study_activity_group.activity_group_name']
      }
      if (jsonFilter['study_activity_subgroup.activity_subgroup_name']) {
        params.activity_subgroup_names = []
        jsonFilter['study_activity_subgroup.activity_subgroup_name'].v.forEach(value => {
          params.activity_subgroup_names.push(value)
        })
        delete jsonFilter['study_activity_subgroup.activity_subgroup_name']
      }
      if (jsonFilter['activity.name']) {
        params.activity_names = []
        jsonFilter['activity.name'].v.forEach(value => {
          params.activity_names.push(value)
        })
        delete jsonFilter['activity.name']
      }
      return {
        jsonFilter: jsonFilter,
        params: params
      }
    },
    openBatchEditForm (selection) {
      if (!selection.length) {
        bus.$emit('notification', { type: 'warning', msg: this.$t('StudyActivityTable.batch_edit_no_selection') })
        return
      }
      this.currentSelection = selection
      this.showBatchEditForm = true
    },
    closeBatchEditForm () {
      this.currentSelection = []
      this.showBatchEditForm = false
    },
    onOrderChange (event) {
      const studyActivity = event.moved.element
      const replacedStudyActivity = this.studyActivities[event.moved.newIndex]
      study.updateStudyActivityOrder(studyActivity.study_uid, studyActivity.study_activity_uid, replacedStudyActivity.order).then(() => {
        this.getStudyActivities()
      })
    },
    onStudyActivitiesUpdated () {
      this.getStudyActivities()
    },
    unselectItem (item) {
      this.currentSelection = this.currentSelection.filter(sa => sa.study_activity_uid !== item.study_activity_uid)
    },
    async fetchActivitiesHistory () {
      const resp = await study.getStudyActivitiesAuditTrail(this.selectedStudy.uid)
      return resp.data
    },
    getItemRowClass (item) {
      return item.activity.library_name === libConstants.LIBRARY_REQUESTED ? 'tableFontSize warning' : 'tableFontSize'
    }
  },
  mounted () {
    this.getStudyActivities()
  },
  watch: {
    options: {
      handler () {
        this.getStudyActivities()
      },
      deep: true
    }
  }
}
</script>
<style scoped>
.tableFontSize {
  font-size: 14px;
}
</style>
