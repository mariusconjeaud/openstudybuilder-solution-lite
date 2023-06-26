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
          <td>{{ item.flowchart_group.sponsor_preferred_name }}</td>
          <td>{{ item.activity.activity_group.name }}</td>
          <td>{{ item.activity.activity_subgroup.name }}</td>
          <td>{{ item.activity.name }}</td>
          <td>{{ item.note }}</td>
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
import NNTable from '@/components/tools/NNTable'
import StudyActivityBatchEditForm from './StudyActivityBatchEditForm'
import StudyActivityEditForm from './StudyActivityEditForm'
import StudyActivityForm from './StudyActivityForm'
import libConstants from '@/constants/libraries'

export default {
  components: {
    ActionsMenu,
    ConfirmDialog,
    draggable,
    NNTable,
    StudyActivityBatchEditForm,
    StudyActivityEditForm,
    StudyActivityForm
  },
  computed: {
    ...mapGetters({
      studyActivities: 'studyActivities/studyActivities',
      selectedStudy: 'studiesGeneral/selectedStudy'
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
          icon: 'mdi-pencil',
          iconColor: 'primary',
          click: this.editStudyActivity
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete',
          iconColor: 'error',
          click: this.deleteStudyActivity
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
        { text: this.$t('StudyActivity.flowchart_group'), value: 'flowchart_group.sponsor_preferred_name' },
        { text: this.$t('StudyActivity.activity_group'), value: 'activity.activity_group.name' },
        { text: this.$t('StudyActivity.activity_sub_group'), value: 'activity.activity_subgroup.name' },
        { text: this.$t('StudyActivity.activity'), value: 'activity.name' },
        { text: this.$t('StudyActivity.footnote'), value: 'note' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.modified_by'), value: 'user_initials' }
      ],
      sortMode: false,
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
          icon: 'mdi-bell',
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
      params.studyUid = this.selectedStudy.uid
      const resp = await this.$store.dispatch('studyActivities/fetchStudyActivities', params)
      this.total = resp.data.total
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
