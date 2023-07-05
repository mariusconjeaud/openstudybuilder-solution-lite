<template>
<div class="pa-4" style="overflow-x: auto" v-resize="onResize">
  <div class="d-flex align-center mb-4">
    <v-radio-group
      v-model="expandAllRows"
      row
      hide-details
      @change="toggleAllRowState"
      >
      <v-radio
        :label="$t('DetailedFlowchart.expand_all')"
        :value="true"
        />
      <v-radio
        :label="$t('DetailedFlowchart.collapse_all')"
        :value="false"
        />
    </v-radio-group>
    <v-switch
      v-model="hideFlowchartGroups"
      :label="$t('DetailedFlowchart.hide_flowchart_groups')"
      hide-details
      class="ml-2"
      />
    <v-spacer />
    <template v-if="!readOnly">
      <v-btn
        fab
        small
        class="mr-2"
        :title="$t('GroupStudyVisits.title')"
        v-show="selectedVisits.length > 1"
        @click="groupSelectedVisits()"
        >
        <v-icon>mdi-arrow-expand-horizontal</v-icon>
      </v-btn>
      <v-btn
        fab
        small
        @click="toggleActivitySelectionDisplay(false)"
        :title="$t('DetailedFlowchart.hide_activity_selection')"
        >
        <v-icon>
          mdi-eye-off-outline
        </v-icon>
      </v-btn>
      <v-btn
        fab
        small
        color="success"
        @click="toggleActivitySelectionDisplay(true)"
        :title="$t('DetailedFlowchart.show_activity_selection')"
        class="ml-2"
        >
        <v-icon>
          mdi-eye-outline
        </v-icon>
      </v-btn>
      <v-btn
        fab
        small
        color="primary"
        @click="openBatchEditForm"
        :title="$t('DetailedFlowchart.edit_activity_selection')"
        class="ml-2"
        >
        <v-icon>
          mdi-pencil-box-multiple-outline
        </v-icon>
      </v-btn>
    </template>
  </div>
  <div ref="tableContainer" class="sticky-header" :style="`height: ${tableHeight}px`">
  <table :aria-label="$t('DetailedFlowchart.table_caption')">
    <thead>
      <tr ref="firstHeader">
        <th width="2%" rowspan="4" scope="col">
          <v-btn
            icon
            @click="showEditForm = true"
            >
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
        </th>
        <th width="25%" rowspan="4" scope="col">{{ $t('DetailedFlowchart.activities') }}</th>
        <th width="10%" scope="col">{{ $t('DetailedFlowchart.study_epoch') }}</th>
        <template v-if="groupedVisits.length">
          <th v-for="(sv, index) in groupedVisits" :key="`epoch-${index}`" class="text-vertical" scope="col">
            {{ getEpochName(sv, index) }}
          </th>
        </template>
        <template v-else>
          <th colspan="2" scope="col"></th>
        </template>
      </tr>
      <tr>
        <th :style="`top: ${firstHeaderHeight}px`" scope="col">{{ $t('DetailedFlowchart.visit_short_name') }}</th>
        <template v-if="groupedVisits.length">
          <th v-for="(sv, index) in groupedVisits" :key="`shortName-${index}`" :style="`top: ${firstHeaderHeight}px`" scope="col">
            <div class="d-flex align-center">
              {{ sv.visit_short_name }}
              <v-checkbox
                v-if="!sv.isGroup"
                v-model="selectedVisits"
                :value="sv"
                :value-comparator="compareVisits"
                hide-details
                small
                multiple
                />
              <v-btn
                v-else
                icon
                color="error"
                x-small
                :title="$t('GroupStudyVisits.delete_title')"
                @click="deleteVisitGroup(sv.uid)"
                >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </div>
          </th>
        </template>
        <template v-else>
          <th colspan="2" :style="`top: ${firstHeaderHeight}px`" scope="col"></th>
        </template>
      </tr>
      <tr>
        <th :style="`top: ${thirdHeaderRowTop}px`" scope="col">{{ timingHeaderTitle }}</th>
        <template v-if="groupedVisits.length">
          <th v-for="(sv, index) in groupedVisits" :key="`week-${index}`" :style="`top: ${thirdHeaderRowTop}px`" scope="col">
            {{ getVisitTiming(sv) }}
          </th>
        </template>
        <template v-else>
          <th colspan="2" :style="`top: ${thirdHeaderRowTop}px`" scope="col"></th>
        </template>
      </tr>
      <tr>
        <th :style="`top: ${fourthHeaderRowTop}px`" scope="col">{{ $t('DetailedFlowchart.visit_window') }}</th>
        <template v-if="groupedVisits.length">
          <th v-for="(sv, index) in groupedVisits" :key="`window-${index}`" :style="`top: ${fourthHeaderRowTop}px`" scope="col">
            <template v-if="sv.min_visit_window_value !== sv.max_visit_window_value">
              {{ sv.min_visit_window_value }}/+{{ sv.max_visit_window_value }}
            </template>
            <template v-else>
              &plusmn;{{ sv.max_visit_window_value }}
            </template>
          </th>
        </template>
        <template v-else>
          <th colspan="2" :style="`top: ${fourthHeaderRowTop}px`" scope="col"></th>
        </template>
      </tr>
    </thead>
    <tbody>
      <template v-for="(groups, flowchartGroup, flGroupIndex) in sortedStudyActivities">
        <tr v-if="!hideFlowchartGroups" :key="flowchartGroup" class="flowchart text-uppercase">
          <td>
            <v-btn
              v-if="!readOnly"
              icon
              @click="toggleRowState(`flgroup-${flGroupIndex}`)"
              >
              <v-icon>{{ getDisplayButtonIcon(`flgroup-${flGroupIndex}`) }}</v-icon>
            </v-btn>
          </td>
          <td class="text-strong">{{ flowchartGroup }}</td>
          <td></td>
          <td :colspan="groupedVisits.length + 1"></td>
        </tr>
        <template v-for="(subgroups, group, groupIndex) in groups">
          <template v-if="rowsDisplayState[`flgroup-${flGroupIndex}`] || hideFlowchartGroups">
            <tr :key="`${flowchartGroup}-${group}`" class="group">
              <td>
                <v-btn
                  v-if="!readOnly"
                  icon
                  @click="toggleRowState(`group-${flGroupIndex}-${groupIndex}`)"
                  >
                  <v-icon>{{ getDisplayButtonIcon(`group-${flGroupIndex}-${groupIndex}`) }}</v-icon>
                </v-btn>
              </td>
              <td class="text-strong">{{ group }}</td>
              <td>
                <v-btn
                  v-if="!readOnly"
                  icon
                  @click="value => toggleActivityGroupFlowchartDisplay(flowchartGroup, group)"
                  :title="$t('DetailedFlowchart.toggle_group_display')"
                  >
                  <v-icon v-if="getGroupDisplayState(flowchartGroup, group)" color="success">mdi-eye-outline</v-icon>
                  <v-icon v-else>mdi-eye-off-outline</v-icon>
                </v-btn>
              </td>
              <td :colspan="groupedVisits.length + 1"></td>
            </tr>
            <template v-for="(studyActivities, subgroup, subgroupIndex) in subgroups">
              <template v-if="rowsDisplayState[`group-${flGroupIndex}-${groupIndex}`]">
                <tr :key="`${flowchartGroup}-${group}-${subgroup}`">
                  <td>
                    <v-btn
                      v-if="!readOnly"
                      icon
                      @click="toggleRowState(`subgroup-${flGroupIndex}-${groupIndex}-${subgroupIndex}`)"
                      >
                      <v-icon>{{ getDisplayButtonIcon(`subgroup-${flGroupIndex}-${groupIndex}-${subgroupIndex}`) }}</v-icon>
                    </v-btn>
                  </td>
                  <td class="subgroup">
                    <div class="d-flex align-center">
                      <v-checkbox
                        v-if="!readOnly"
                        :key="`cb-subgroup-${flowchartGroup}-${group}-${subgroup}-${update}`"
                        @change="value => toggleSubgroupActivitiesSelection(flowchartGroup, group, subgroup, value)"
                        on-icon="mdi-checkbox-multiple-marked"
                        off-icon="mdi-checkbox-multiple-blank-outline"
                        hide-details
                        />
                      {{ subgroup }}
                    </div>
                  </td>
                  <td>
                    <v-btn
                      v-if="!readOnly"
                      icon
                      @click="value => toggleActivitySubgroupFlowchartDisplay(flowchartGroup, group, subgroup)"
                      :title="$t('DetailedFlowchart.toggle_subgroup_display')"
                      >
                      <v-icon v-if="getSubgroupDisplayState(flowchartGroup, group, subgroup)" color="success">mdi-eye-outline</v-icon>
                      <v-icon v-else>mdi-eye-off-outline</v-icon>
                    </v-btn>
                  </td>
                  <td :colspan="groupedVisits.length + 1"></td>
                </tr>
                <template v-if="rowsDisplayState[`subgroup-${flGroupIndex}-${groupIndex}-${subgroupIndex}`]">
                  <tr v-for="studyActivity in studyActivities" :key="studyActivity.study_activity_uid">
                    <td></td>
                    <td class="activity">
                      <div class="d-flex align-center">
                        <v-checkbox
                          v-if="!readOnly"
                          hide-details
                          @change="value => toggleActivitySelection(studyActivity, value)"
                          :value="studyActivitySelection.findIndex(item => item.study_activity_uid === studyActivity.study_activity_uid) !== -1"
                          />
                        {{ studyActivity.activity.name }}
                      </div>
                    </td>
                    <td>
                      <v-btn
                        v-if="!readOnly"
                        icon
                        @click="toggleActivityFlowchartDisplay(studyActivity, !studyActivity.show_activity_in_protocol_flowchart)"
                        :title="$t('DetailedFlowchart.toggle_activity_display')"
                        >
                        <v-icon v-if="studyActivity.show_activity_in_protocol_flowchart" color="success">mdi-eye-outline</v-icon>
                        <v-icon v-else>mdi-eye-off-outline</v-icon>
                      </v-btn>
                    </td>
                    <td v-for="visit in groupedVisits" :key="`${studyActivity.study_activity_uid}-${visit.uid}`">
                      <v-checkbox
                        v-if="!readOnly && currentSelectionMatrix[studyActivity.study_activity_uid][visit.uid]"
                        v-model="currentSelectionMatrix[studyActivity.study_activity_uid][visit.uid].value"
                        color="success"
                        @change="value => updateSchedule(value, studyActivity.study_activity_uid, visit)"
                        :disabled="isCheckboxDisabled(studyActivity.study_activity_uid, visit.uid)"
                        hide-details
                        on-icon="mdi-checkbox-marked-circle-outline"
                        off-icon="mdi-checkbox-blank-circle-outline"
                        />
                    </td>
                  </tr>
                </template>
              </template>
            </template>
          </template>
        </template>
      </template>
    </tbody>
  </table>
  </div>
  <study-activity-schedule-batch-edit-form
    :open="showBatchEditForm"
    :selection="studyActivitySelection"
    :current-selection-matrix="currentSelectionMatrix"
    @updated="getStudyActivitySchedules"
    @close="showBatchEditForm = false"
    />
  <v-dialog
    v-model="showEditForm"
    @keydown.esc="showEditForm = false"
    persistent
    max-width="600px"
    >
    <v-card color="dfltBackground">
      <v-card-title>
        <span class="dialog-title">{{ $t('DetailedFlowchart.edit_dialog_title') }}</span>
      </v-card-title>
      <v-card-text class="mt-4">
        <div class="white pa-4">
          <validation-observer ref="redirectObserver">
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-radio-group
                v-model="editTarget"
                :error-messages="errors"
                >
                <v-radio
                  :label="$t('DetailedFlowchart.study_activities')"
                  value="activities"
                  />
                <v-radio
                  :label="$t('DetailedFlowchart.study_epochs')"
                  value="epochs"
                  />
                <v-radio
                  :label="$t('DetailedFlowchart.study_visits')"
                  value="visits"
                  />
              </v-radio-group>
            </validation-provider>
          </validation-observer>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          class="secondary-btn"
          color="white"
          @click="showEditForm = false"
          >
          {{ $t('_global.cancel') }}
        </v-btn>
        <v-btn
          color="secondary"
          @click="redirectTo"
          >
          {{ $t('_global.confirm') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
  <v-dialog
    v-model="showCollapsibleGroupForm"
    persistent
    max-width="1000px"
    >
    <collapsible-visit-group-form
      :open="showCollapsibleGroupForm"
      :visits="selectedVisits"
      @close="closeCollapsibleVisitGroupForm"
      @created="collapsibleVisitGroupCreated"
      />
  </v-dialog>
</div>
</template>

<script>
import { bus } from '@/main'
import CollapsibleVisitGroupForm from './CollapsibleVisitGroupForm'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import { mapGetters } from 'vuex'
import study from '@/api/study'
import StudyActivityScheduleBatchEditForm from './StudyActivityScheduleBatchEditForm'
import studyConstants from '@/constants/study.js'
import studyEpochs from '@/api/studyEpochs'
import terms from '@/api/controlledTerminology/terms'
import visitConstants from '@/constants/visits'

export default {
  components: {
    CollapsibleVisitGroupForm,
    ConfirmDialog,
    StudyActivityScheduleBatchEditForm
  },
  props: {
    readOnly: {
      type: Boolean,
      default: false
    },
    update: Number
  },
  computed: {
    ...mapGetters({
      studyActivities: 'studyActivities/studyActivities',
      sortedStudyActivities: 'studyActivities/sortedStudyActivities',
      selectedStudy: 'studiesGeneral/selectedStudy',
      studyPreferredTimeUnit: 'studiesGeneral/studyPreferredTimeUnit'
    }),
    thirdHeaderRowTop () {
      return this.initialFirstHeaderHeight + this.firstHeaderHeight
    },
    fourthHeaderRowTop () {
      return this.firstHeaderHeight + (this.initialFirstHeaderHeight * 2)
    },
    groupedVisits () {
      const result = []
      let currentGroup = null
      let firstVisit = null
      let previousVisit = null

      function createFakeVisit () {
        const fakeVisit = {
          visit_short_name: `${firstVisit.visit_short_name}-${previousVisit.visit_short_name}`,
          epoch_uid: firstVisit.epoch_uid,
          study_day_number: `${firstVisit.study_day_number}-${previousVisit.study_day_number}`,
          study_week_number: `${firstVisit.study_week_number}-${previousVisit.study_week_number}`,
          min_visit_window_value: firstVisit.min_visit_window_value,
          max_visit_window_value: firstVisit.max_visit_window_value,
          consecutive_visit_group: firstVisit.consecutive_visit_group,
          uid: firstVisit.consecutive_visit_group,
          isGroup: true
        }
        result.push(fakeVisit)
      }

      for (const visit of this.studyVisits) {
        if (visit.study_epoch_name === visitConstants.EPOCH_BASIC) {
          continue
        }
        if (visit.consecutive_visit_group) {
          if (visit.consecutive_visit_group !== currentGroup) {
            if (currentGroup) {
              createFakeVisit()
            }
            firstVisit = visit
            currentGroup = visit.consecutive_visit_group
          }
        } else {
          if (currentGroup) {
            createFakeVisit()
          }
          currentGroup = null
          result.push(visit)
        }
        previousVisit = visit
      }
      if (currentGroup) {
        createFakeVisit()
      }
      return result
    },
    timingHeaderTitle () {
      if (!this.studyPreferredTimeUnit || this.studyPreferredTimeUnit.time_unit_name === studyConstants.STUDY_TIME_UNIT_WEEK) {
        return this.$t('_global.week')
      }
      return this.$t('_global.day')
    }
  },
  data () {
    return {
      currentSelectionMatrix: {},
      editTarget: null,
      expandAllRows: false,
      hideFlowchartGroups: false,
      rowsDisplayState: {},
      epochs: [],
      initialFirstHeaderHeight: 0,
      firstHeaderHeight: 0,
      selectedVisits: [],
      showBatchEditForm: false,
      showCollapsibleGroupForm: false,
      showEditForm: false,
      studyActivitySchedules: [],
      studyActivitySelection: [],
      studyVisits: [],
      tableHeight: 500
    }
  },
  methods: {
    getEpochName (studyVisit, index) {
      if (this.epochs.length) {
        if (index === 0 || this.studyVisits[index].epoch_uid !== this.studyVisits[index - 1].epoch_uid) {
          const epoch = this.epochs.find(item => item.term_uid === studyVisit.epoch_uid)
          return epoch.sponsor_preferred_name
        }
      }
      return ''
    },
    isCheckboxDisabled (studyActivityUid, studyVisitUid) {
      const state = this.currentSelectionMatrix[studyActivityUid][studyVisitUid]
      return this.readOnly || (state.value && !state.uid) || (!state.value && state.uid !== null)
    },
    getCurrentDisplayValue (rowKey) {
      const currentValue = this.rowsDisplayState[rowKey]
      if (currentValue === undefined) {
        return false
      }
      return currentValue
    },
    getDisplayButtonIcon (rowKey) {
      return (this.getCurrentDisplayValue(rowKey)) ? 'mdi-chevron-down' : 'mdi-chevron-right'
    },
    getGroupDisplayState (flgroup, group) {
      for (const items of Object.values(this.sortedStudyActivities[flgroup][group])) {
        for (const item of items) {
          if (item.show_activity_group_in_protocol_flowchart) {
            return true
          }
        }
      }
      return false
    },
    getSubgroupDisplayState (flgroup, group, subgroup) {
      for (const item of this.sortedStudyActivities[flgroup][group][subgroup]) {
        if (item.show_activity_subgroup_in_protocol_flowchart) {
          return true
        }
      }
      return false
    },
    toggleRowState (rowKey) {
      const currentValue = this.getCurrentDisplayValue(rowKey)
      this.$set(this.rowsDisplayState, rowKey, !currentValue)
    },
    toggleAllRowState (value) {
      let flgroupIndex = 0
      for (const flgroup in this.sortedStudyActivities) {
        let groupIndex = 0
        this.$set(this.rowsDisplayState, `flgroup-${flgroupIndex}`, value)
        for (const group in this.sortedStudyActivities[flgroup]) {
          let subgroupIndex = 0
          this.$set(this.rowsDisplayState, `group-${flgroupIndex}-${groupIndex}`, value)
          for (const subgroup in this.sortedStudyActivities[flgroup][group]) { // eslint-disable-line no-unused-vars
            this.$set(this.rowsDisplayState, `subgroup-${flgroupIndex}-${groupIndex}-${subgroupIndex}`, value)
            subgroupIndex += 1
          }
          groupIndex += 1
        }
        flgroupIndex += 1
      }
    },
    toggleActivitySelection (studyActivity, value) {
      if (value) {
        this.studyActivitySelection.push(studyActivity)
      } else {
        for (let i = 0; i < this.studyActivitySelection.length; i++) {
          if (this.studyActivitySelection[i].study_activity_uid === studyActivity.study_activity_uid) {
            this.studyActivitySelection.splice(i, 1)
            break
          }
        }
      }
    },
    updateStudyActivity (studyActivity, data) {
      study.updateStudyActivity(this.selectedStudy.uid, studyActivity.study_activity_uid, data).then(resp => {
        const fgroup = studyActivity.flowchart_group.sponsor_preferred_name
        const group = (studyActivity.activity.activity_group)
          ? studyActivity.activity.activity_group.name : ''
        const subgroup = (studyActivity.activity.activity_subgroup)
          ? studyActivity.activity.activity_subgroup.name : ''
        this.sortedStudyActivities[fgroup][group][subgroup].filter((item, index) => {
          this.$store.commit('studyActivities/UPDATE_STUDY_ACTIVITY', resp.data)
        })
      })
    },
    /*
    ** Toggle group display in protocol flowchart.
    ** We need to store this information on each study activity...
    */
    toggleActivityGroupFlowchartDisplay (flgroup, group) {
      for (const items of Object.values(this.sortedStudyActivities[flgroup][group])) {
        if (items.length) {
          items.forEach(studyActivity => {
            const data = {
              show_activity_group_in_protocol_flowchart: !studyActivity.show_activity_group_in_protocol_flowchart
            }
            this.updateStudyActivity(studyActivity, data)
          })
        }
      }
    },
    /*
    ** Toggle subgroup display in protocol flowchart.
    ** We need to store this information on each study activity...
    */
    toggleActivitySubgroupFlowchartDisplay (flgroup, group, subgroup) {
      this.sortedStudyActivities[flgroup][group][subgroup].forEach(studyActivity => {
        const data = {
          show_activity_subgroup_in_protocol_flowchart: !studyActivity.show_activity_subgroup_in_protocol_flowchart
        }
        this.updateStudyActivity(studyActivity, data)
      })
    },
    toggleActivityFlowchartDisplay (studyActivity) {
      const data = {
        show_activity_in_protocol_flowchart: !studyActivity.show_activity_in_protocol_flowchart
      }
      this.updateStudyActivity(studyActivity, data)
    },
    updateGroupedSchedule (value, studyActivityUid, studyVisit) {
      if (value) {
        const data = []
        for (const iterator of this.studyVisits) {
          if (iterator.consecutive_visit_group === studyVisit.consecutive_visit_group) {
            data.push({
              method: 'POST',
              content: {
                study_activity_uid: studyActivityUid,
                study_visit_uid: iterator.uid
              }
            })
          }
        }
        study.studyActivityScheduleBatchOperations(this.selectedStudy.uid, data).then(resp => {
          const scheduleUids = resp.data.map(item => item.content.study_activity_schedule_uid)
          this.currentSelectionMatrix[studyActivityUid][studyVisit.uid].uid = scheduleUids
        })
      } else {
        const data = []
        for (const scheduleUid of this.currentSelectionMatrix[studyActivityUid][studyVisit.uid].uid) {
          data.push({
            method: 'DELETE',
            content: {
              uid: scheduleUid
            }
          })
        }
        study.studyActivityScheduleBatchOperations(this.selectedStudy.uid, data).then(resp => {
          this.currentSelectionMatrix[studyActivityUid][studyVisit.uid].uid = null
        })
      }
    },
    updateSchedule (value, studyActivityUid, studyVisit) {
      if (studyVisit.isGroup) {
        this.updateGroupedSchedule(value, studyActivityUid, studyVisit)
        return
      }
      if (value) {
        const data = {
          study_activity_uid: studyActivityUid,
          study_visit_uid: studyVisit.uid
        }
        study.createStudyActivitySchedule(this.selectedStudy.uid, data).then(resp => {
          this.currentSelectionMatrix[studyActivityUid][studyVisit.uid].uid = resp.data.study_activity_schedule_uid
        })
      } else {
        const scheduleUid = this.currentSelectionMatrix[studyActivityUid][studyVisit.uid].uid
        study.deleteStudyActivitySchedule(this.selectedStudy.uid, scheduleUid).then(resp => {
          this.currentSelectionMatrix[studyActivityUid][studyVisit.uid].uid = null
        })
      }
    },
    openBatchEditForm () {
      if (!this.studyActivitySelection.length) {
        bus.$emit('notification', { type: 'warning', msg: this.$t('DetailedFlowchart.batch_edit_no_selection') })
        return
      }
      this.showBatchEditForm = true
    },
    toggleActivitySelectionDisplay (value) {
      if (!this.studyActivitySelection.length) {
        bus.$emit('notification', { type: 'warning', msg: this.$t('DetailedFlowchart.batch_edit_no_selection') })
        return
      }
      const data = []
      for (const item of this.studyActivitySelection) {
        data.push({
          method: 'PATCH',
          content: {
            study_activity_uid: item.study_activity_uid,
            content: {
              show_activity_in_protocol_flowchart: value
            }
          }
        })
      }
      study.studyActivityBatchOperations(this.selectedStudy.uid, data).then(resp => {
        bus.$emit('notification', {
          type: 'success',
          msg: this.$t('DetailedFlowchart.update_success')
        })
        this.studyActivitySelection.forEach(item => {
          this.$set(item, 'show_activity_in_protocol_flowchart', value)
        })
      })
    },
    toggleSubgroupActivitiesSelection (flgroup, group, subgroup, value) {
      if (value) {
        this.studyActivitySelection = this.studyActivitySelection.concat(this.sortedStudyActivities[flgroup][group][subgroup])
      } else {
        for (const studyActivity of this.sortedStudyActivities[flgroup][group][subgroup]) {
          const index = this.studyActivitySelection.findIndex(item => item.study_activity_uid === studyActivity.study_activity_uid)
          this.studyActivitySelection.splice(index, 1)
        }
      }
    },
    getStudyActivitySchedules () {
      study.getStudyActivitySchedules(this.selectedStudy.uid).then(resp => {
        this.groupedVisits.forEach(visit => {
          Object.keys(this.currentSelectionMatrix).forEach(studyActivity => {
            this.$set(this.currentSelectionMatrix[studyActivity], visit.uid, { value: false, uid: null })
          })
        })
        resp.data.forEach(schedule => {
          const visit = this.studyVisits.find(item => item.uid === schedule.study_visit_uid)
          if (!visit) {
            return
          }
          if (!visit.consecutive_visit_group) {
            if (this.currentSelectionMatrix[schedule.study_activity_uid]) {
              this.$set(
                this.currentSelectionMatrix[schedule.study_activity_uid],
                visit.uid,
                { value: true, uid: schedule.study_activity_schedule_uid }
              )
            } else {
              console.log(`ERROR: found missing activity in current matrix -> ${schedule.study_activity_uid}`)
              console.log(schedule)
            }
          } else {
            const visitUid = visit.consecutive_visit_group
            if (!this.currentSelectionMatrix[schedule.study_activity_uid][visitUid].uid) {
              this.$set(
                this.currentSelectionMatrix[schedule.study_activity_uid],
                visitUid,
                { value: true, uid: [schedule.study_activity_schedule_uid] }
              )
            } else {
              this.currentSelectionMatrix[schedule.study_activity_uid][visitUid].uid.push(
                schedule.study_activity_schedule_uid
              )
            }
          }
        })
      })
    },
    async redirectTo () {
      const valid = await this.$refs.redirectObserver.validate()
      if (!valid) {
        return
      }
      this.showEditForm = false
      if (this.editTarget === 'activities') {
        this.$router.push({ name: 'StudyActivities', params: { tab: 'list' } })
      } else if (this.editTarget === 'epochs') {
        this.$router.push({ name: 'StudyStructure', params: { tab: 'epochs' } })
      } else {
        this.$router.push({ name: 'StudyStructure', params: { tab: 'visits' } })
      }
    },
    async loadActivities () {
      this.studyActivitySelection = []
      await this.$store.dispatch('studyActivities/fetchStudyActivities', { studyUid: this.selectedStudy.uid })
      for (const studyActivity of this.studyActivities) {
        this.$set(this.currentSelectionMatrix, studyActivity.study_activity_uid, {})
      }
      studyEpochs.getStudyVisits(this.selectedStudy.uid, { page_size: 0 }).then(resp => {
        this.studyVisits = resp.data.items
        this.getStudyActivitySchedules()
      })
    },
    onResize () {
      this.tableHeight = window.innerHeight - this.$refs.tableContainer.getBoundingClientRect().y - 60
    },
    compareVisits (a, b) {
      return a.uid === b.uid
    },
    groupSelectedVisits () {
      const visitUids = this.selectedVisits.map(item => item.uid)
      studyEpochs.createCollapsibleVisitGroup(this.selectedStudy.uid, visitUids).then(() => {
        this.collapsibleVisitGroupCreated()
      }).catch(err => {
        if (err.response.status === 400) {
          this.showCollapsibleGroupForm = true
        }
      })
    },
    closeCollapsibleVisitGroupForm () {
      this.showCollapsibleGroupForm = false
    },
    collapsibleVisitGroupCreated () {
      bus.$emit('notification', { msg: this.$t('CollapsibleVisitGroupForm.creation_success') })
      this.loadActivities()
      this.selectedVisits = []
    },
    async deleteVisitGroup (groupName) {
      const message = this.$t('DetailedFlowchart.confirm_group_deletion', { group: groupName })
      const options = { type: 'warning' }
      if (!await this.$refs.confirm.open(message, options)) {
        return
      }
      await studyEpochs.deleteCollapsibleVisitGroup(this.selectedStudy.uid, groupName)
      this.loadActivities()
    },
    getVisitTiming (studyVisit) {
      if (!this.studyPreferredTimeUnit || this.studyPreferredTimeUnit.time_unit_name === 'week') {
        return studyVisit.study_week_number
      }
      return studyVisit.study_day_number
    }
  },
  mounted () {
    terms.getByCodelist('epochs').then(resp => {
      this.epochs = resp.data.items
    })
    this.loadActivities()
    this.onResize()
  },
  watch: {
    update () {
      this.loadActivities()
    }
  },
  updated () {
    this.firstHeaderHeight = this.$refs.firstHeader.clientHeight
    if (!this.initialFirstHeaderHeight) {
      this.initialFirstHeaderHeight = this.firstHeaderHeight
    }
  }
}
</script>

<style scoped lang="scss">
table {
  width: 100%;
  text-align: left;
  border-spacing: 0px;
  border-collapse: collapse;
}
thead {
  background-color: var(--v-greyBackground-base);
  font-weight: 600;
}
tr {
  padding: 4px;
  &.section {
    background-color: var(--v-greyBackground-base);
    font-weight: 600;
  }
}
tbody tr {
  border-bottom: 1px solid var(--v-greyBackground-base);
}
th {
  vertical-align: bottom;
  background-color: var(--v-greyBackground-base);
}
th, td {
  padding: 6px;
  font-size: 14px !important;
}
.sticky-header {
  overflow-y: auto;

  thead th {
    position: sticky;
    top: 0;
    z-index: 3;
  }
}
.flowchart {
  background-color: var(--v-dfltBackgroundLight1-base);

}
.group {
  background-color: var(--v-dfltBackgroundLight2-base);
}
.subgroup {
  font-weight: 600;
  padding-left: 20px;
}
.activity {
  padding-left: 20px;
}
.text-vertical {
  writing-mode: vertical-rl;
  text-orientation: mixed;
}
.text-strong {
  font-weight: 600;
}
</style>
