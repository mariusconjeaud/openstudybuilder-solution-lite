<template>
<div>
  <div id="visjs" class="pa-6">
    <span class="text-h6 ml-2">{{ $t('StudyVisitTable.title') }}</span>
    <v-expansion-panels
      accordion
      tile
      class="mt-2"
      >
      <v-expansion-panel>
        <v-expansion-panel-header>{{ $t('StudyVisitTable.timeline_preview') }}</v-expansion-panel-header>
        <v-expansion-panel-content>
          <div v-if="!loading && studyVisits.length > 0" :key="chartsKey">
            <horizontal-bar-chart
              :chart-data="barChartDatasets"
              :options="barChartOptions"
              :styles="barChartStyles"
              class="pr-3"
              :key="barChartKey"
              />
            <bubble-chart
              :chart-data="lineChartDatasets"
              :options="lineChartOptions"
              :styles="lineChartStyles"
              class="ml-1"
              />
          </div>
          <div v-else-if="loading">
            <v-progress-linear
              class="mt-5"
              indeterminate
              ></v-progress-linear>
          </div>
          <div v-else class="mt-3">
            {{ $t('StudyVisitForm.no_data') }}
          </div>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </div>
  <n-n-table
    ref="table"
    :headers="headers"
    :default-headers="defaultColumns"
    :items="studyVisits"
    item-key="uid"
    class="mt-6"
    :export-data-url="exportDataUrl"
    export-object-label="StudyVisits"
    has-api
    :items-per-page="50"
    :items-per-page-options="[25, 50, 100]"
    @filter="fetchStudyVisits"
    :column-data-resource="`studies/${selectedStudy.uid}/study-visits`"
    :options.sync="options"
    :server-items-length="totalVisits"
    fixed-header
    :history-data-fetcher="fetchVisitsHistory"
    :history-title="$t('StudyVisitTable.global_history_title')"
    >
    <template v-slot:afterSwitches>
      <label class="v-label theme--light mr-4">
        {{ $t('StudyVisitTable.preferred_time_unit') }}
      </label>
      <v-radio-group
        v-model="preferredTimeUnit"
        row
        hide-details
        @change="updatePreferredTimeUnit"
        >
        <v-radio
          :label="$t('_global.day')"
          value="day"
          ></v-radio>
        <v-radio
          :label="$t('_global.week')"
          value="week"
          ></v-radio>
      </v-radio-group>
    </template>
    <template v-slot:headerCenter>
      <v-btn
        small
        color="primary"
        @click.stop="closeEditMode"
        :title="$t('_global.cancel')"
        class="ml-2"
        data-cy="close-edit-mode"
        v-if="editMode"
        >
        {{ $t('StudyVisitTable.close_edit_mode') }}
      </v-btn>
    </template>
    <template v-slot:actions="{ selected, showSelectBoxes }">
      <v-progress-circular
        indeterminate
        color="primary"
        v-show="loading"
        >
      </v-progress-circular>
      <v-btn
        fab
        small
        class="mr-2"
        :title="$t('GroupStudyVisits.title')"
        v-show="!loading && showSelectBoxes"
        @click="groupSelectedVisits(selected)"
        :disabled="!checkPermission($roles.STUDY_WRITE)"
        >
        <v-icon>mdi-arrow-expand-horizontal</v-icon>
      </v-btn>
      <v-btn
        fab
        small
        color="primary"
        @click.stop="openForm"
        v-show="!loading"
        :title="$t('NNTableTooltips.add_content')"
        :disabled="!checkPermission($roles.STUDY_WRITE)"
        data-cy="add-visit"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
      <v-btn
        fab
        small
        color="primary"
        @click.stop="openEditMode"
        :title="$t('_global.edit')"
        data-cy="edit-study-visits"
        class="ml-2"
        v-if="!editMode && !loading"
        :disabled="!checkPermission($roles.STUDY_WRITE)"
        >
        <v-icon dark>
          mdi-pencil-outline
        </v-icon>
      </v-btn>
      <v-progress-circular
        indeterminate
        color="primary"
        v-show="loading"
        class="ml-2"
        >
      </v-progress-circular>
    </template>
    <template v-slot:item.visit_window="{ item }">
      <div v-if="editMode && item.visit_class === 'SINGLE_VISIT'">
        <v-row class="cellWidth">
          <v-col cols="3">
            <v-text-field
              dense
              v-model="item.min_visit_window_value"
              :disabled="item.disabled && itemsDisabled"
              @input="disableOthers(item)"/>
          </v-col>
          <v-col cols="3">
            <v-text-field
              dense
              v-model="item.max_visit_window_value"
              :disabled="item.disabled && itemsDisabled"
              @input="disableOthers(item)"/>
          </v-col>
          <v-col cols="6">
            <v-select
              :items="timeUnits"
              item-text="name"
              item-value="uid"
              dense
              v-model="item.visit_window_unit_uid"
              :disabled="item.disabled && itemsDisabled"
              @change="disableOthers(item)"/>
          </v-col>
        </v-row>
      </div>
      <template v-else-if="item.min_visit_window_value !== null && item.max_visit_window_value !== null">
        {{ item.min_visit_window_value }} / {{ item.max_visit_window_value }} {{ getUnitName(item.visit_window_unit_uid) }}
      </template>
    </template>
    <template v-slot:item.study_epoch_uid="{ item }">
      {{ getStudyEpochName(item.study_epoch_uid) }}
    </template>
    <template v-slot:item.show_visit="{ item }">
      <div v-if="editMode && item.visit_class === 'SINGLE_VISIT'">
        <v-checkbox
          v-model="item.show_visit"
          @change="disableOthers(item)"
          :disabled="item.disabled && itemsDisabled"
          />
      </div>
      <div v-else>
        {{ item.show_visit|yesno}}
      </div>
    </template>
    <template v-slot:item.is_global_anchor_visit="{ item }">
      {{ item.is_global_anchor_visit|yesno}}
    </template>
    <template v-slot:item.visit_subclass="{ item }">
      {{ item.visit_subclass === 'ANCHOR_VISIT_IN_GROUP_OF_SUBV' ? 'Yes' : 'No'}}
    </template>
    <template v-slot:item.visit_subname="{ item }">
      {{ item.visit_subclass === 'ANCHOR_VISIT_IN_GROUP_OF_SUBV' ? item.visit_subname : ''}}
    </template>
    <template v-slot:item.time_value="{ item }">
      <div v-if="editMode && item.visit_class === 'SINGLE_VISIT'">
        <v-row class="cellWidth">
          <v-col cols="4">
            <v-text-field
              dense
              v-model="item.time_value"
              :disabled="item.disabled && itemsDisabled"
              @input="disableOthers(item)"/>
          </v-col>
          <v-col cols="6">
            <v-select
              :items="timeUnits"
              item-text="name"
              item-value="uid"
              dense
              v-model="item.time_unit_uid"
              :disabled="item.disabled && itemsDisabled"
              @change="disableOthers(item)"/>
          </v-col>
        </v-row>
      </div>
      <div v-else>
        {{ item.time_value }} {{ getUnitName(item.time_unit_uid) }}
      </div>
    </template>
    <template v-slot:item.visit_contact_mode_name="{ item }">
      <div v-if="editMode && item.visit_class === 'SINGLE_VISIT'">
        <v-select
        class="cellWidth"
        :items="contactModes"
        item-text="sponsor_preferred_name"
        item-value="term_uid"
        dense
        v-model="item.visit_contact_mode_uid"
        :disabled="item.disabled && itemsDisabled"
        @change="disableOthers(item)"/>
      </div>
      <div v-else>
        {{ item.visit_contact_mode_name }}
      </div>
    </template>
    <template v-slot:item.time_reference_name="{ item }">
      <div v-if="editMode && item.visit_class === 'SINGLE_VISIT'">
        <v-select
        class="cellWidth"
        :items="timeReferences"
        item-text="sponsor_preferred_name"
        item-value="term_uid"
        dense
        v-model="item.time_reference_uid"
        :disabled="item.disabled && itemsDisabled"
        @change="disableOthers(item)"/>
      </div>
      <div v-else-if="item.visit_subclass === visitConstants.SUBCLASS_ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV">
        {{ item.visit_subname }}
      </div>
      <div v-else>
        {{ item.time_reference_name }}
      </div>
    </template>
    <template v-slot:item.description="{ item }">
      <div v-if="editMode && item.visit_class === 'SINGLE_VISIT'">
        <v-row class="cellWidth">
          <v-col>
            <v-text-field
              dense
              v-model="item.description"
              :disabled="item.disabled && itemsDisabled"
              @input="disableOthers(item)"/>
          </v-col>
        </v-row>
      </div>
      <div v-else>
        {{ item.description }}
      </div>
    </template>
    <template v-slot:item.start_rule="{ item }">
      <div v-if="editMode && item.visit_class === 'SINGLE_VISIT'">
        <v-row class="cellWidth">
          <v-col>
            <v-text-field
              dense
              v-model="item.start_rule"
              :disabled="item.disabled && itemsDisabled"
              @input="disableOthers(item)"/>
          </v-col>
        </v-row>
      </div>
      <div v-else>
        {{ item.start_rule }}
      </div>
    </template>
    <template v-slot:item.end_rule="{ item }">
      <div v-if="editMode && item.visit_class === 'SINGLE_VISIT'">
        <v-row class="cellWidth">
          <v-col>
            <v-text-field
              dense
              v-model="item.end_rule"
              :disabled="item.disabled && itemsDisabled"
              @input="disableOthers(item)"/>
          </v-col>
        </v-row>
      </div>
      <div v-else>
        {{ item.end_rule }}
      </div>
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date|date }}
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu
        v-if="!itemsDisabled || item.disabled"
        :actions="actions"
        :item="item"
        />
      <v-btn
        v-if="itemsDisabled && !item.disabled"
        fab
        x-small
        color="success"
        @click="saveVisit(item)"
        >
        <v-icon>mdi-content-save-outline</v-icon>
      </v-btn>
      <v-btn
        v-if="itemsDisabled && !item.disabled"
        fab
        x-small
        @click="cancelVisitEditing"
        >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </template>
  </n-n-table>
  <study-visits-duplicate-form
    :open="duplicateForm"
    @close="closeDuplicateForm"
    :studyVisit="selectedStudyVisit" />
  <v-dialog
    v-model="showForm"
    persistent
    fullscreen
    content-class="fullscreen-dialog"
    >
    <study-visit-form
      :opened="showForm"
      :firstVisit="studyVisits ? (studyVisits.length === 0) : true"
      :studyVisit="selectedStudyVisit"
      @close="closeForm"
      @refresh="fetchStudyVisits"
      class="fullscreen-dialog"
      />
  </v-dialog>
  <v-dialog
    v-model="showVisitHistory"
    @keydown.esc="closeVisitHistory"
    persistent
    :max-width="globalHistoryDialogMaxWidth"
    :fullscreen="globalHistoryDialogFullscreen"
    >
    <history-table
      :title="studyVisitHistoryTitle"
      @close="closeVisitHistory"
      :headers="headers"
      :items="visitHistoryItems"
      />
  </v-dialog>
  <v-dialog
    v-model="showCollapsibleGroupForm"
    persistent
    max-width="1000px"
    >
    <collapsible-visit-group-form
      :open="showCollapsibleGroupForm"
      :visits="visitSelection"
      @close="closeCollapsibleVisitGroupForm"
      @created="collapsibleVisitGroupCreated"
      />
  </v-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import { bus } from '@/main'
import { mapGetters } from 'vuex'
import units from '@/api/units'
import terms from '@/api/controlledTerminology/terms'
import ActionsMenu from '@/components/tools/ActionsMenu'
import NNTable from '@/components/tools/NNTable'
import StudyVisitForm from './StudyVisitForm'
import HorizontalBarChart from '@/components/tools/HorizontalBarChart'
import BubbleChart from '@/components/tools/BubbleChart'
import CollapsibleVisitGroupForm from './CollapsibleVisitGroupForm'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import visitConstants from '@/constants/visits'
import filteringParameters from '@/utils/filteringParameters'
import studyConstants from '@/constants/study'
import StudyVisitsDuplicateForm from './StudyVisitsDuplicateForm'
import unitConstants from '@/constants/units'
import studyEpochs from '@/api/studyEpochs'
import dataFormating from '@/utils/dataFormating'
import { accessGuard } from '@/mixins/accessRoleVerifier'
import HistoryTable from '@/components/tools/HistoryTable'

export default {
  mixins: [accessGuard],
  components: {
    ConfirmDialog,
    CollapsibleVisitGroupForm,
    ActionsMenu,
    NNTable,
    StudyVisitForm,
    HorizontalBarChart,
    BubbleChart,
    HistoryTable,
    StudyVisitsDuplicateForm
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      studyPreferredTimeUnit: 'studiesGeneral/studyPreferredTimeUnit',
      studyEpochs: 'studyEpochs/studyEpochs',
      studyVisits: 'studyEpochs/studyVisits',
      totalVisits: 'studyEpochs/totalVisits'
    }),
    barChartStyles () {
      return {
        position: 'relative',
        height: '200px'
      }
    },
    lineChartStyles () {
      return {
        position: 'relative',
        height: '90px'
      }
    },
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}/study-visits`
    },
    singleStudyVisits () {
      return this.studyVisits.filter(visit => visit.visit_class === visitConstants.CLASS_SINGLE_VISIT)
    },
    studyVisitHistoryTitle () {
      if (this.selectedStudyVisit) {
        return this.$t(
          'StudyVisitTable.study_visit_history_title',
          { visitUid: this.selectedStudyVisit.uid })
      }
      return ''
    }
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'edit') && !this.editMode,
          click: this.editVisit,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          condition: (item) => item.possible_actions.find(action => action === 'delete') && !this.editMode,
          click: this.deleteVisit,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('StudyVisitTable.duplicate'),
          icon: 'mdi-plus-box-multiple-outline',
          iconColor: 'primary',
          click: this.openDuplicateForm,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          condition: (item) => item.visit_class === 'SINGLE_VISIT' && !this.editMode,
          click: this.openVisitHistory
        }
      ],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('StudyVisitForm.study_epoch'), value: 'study_epoch_uid' },
        { text: this.$t('StudyVisitForm.visit_type'), value: 'visit_type_name' },
        { text: this.$t('StudyVisitForm.visit_class'), value: 'visit_class' },
        { text: this.$t('StudyVisitForm.anchor_visit_in_group'), value: 'visit_subclass' },
        { text: this.$t('StudyVisitForm.visit_group'), value: 'visit_subname' },
        { text: this.$t('StudyVisitForm.global_anchor_visit'), value: 'is_global_anchor_visit' },
        { text: this.$t('StudyVisitForm.contact_mode'), value: 'visit_contact_mode_name' },
        { text: this.$t('StudyVisitForm.time_reference'), value: 'time_reference_name' },
        { text: this.$t('StudyVisitForm.time_value'), value: 'time_value' },
        { text: this.$t('StudyVisitForm.visit_number'), value: 'order' },
        { text: this.$t('StudyVisitForm.unique_visit_number'), value: 'unique_visit_number' },
        { text: this.$t('StudyVisitForm.visit_name'), value: 'visit_name' },
        { text: this.$t('StudyVisitForm.visit_short_name'), value: 'visit_short_name' },
        { text: this.$t('StudyVisitForm.study_duration_days'), value: 'study_duration_days_label' },
        { text: this.$t('StudyVisitForm.study_duration_weeks'), value: 'study_duration_weeks_label' },
        { text: this.$t('StudyVisitForm.visit_window'), value: 'visit_window' },
        { text: this.$t('StudyVisitForm.collapsible_visit'), value: 'consecutive_visit_group' },
        { text: this.$t('StudyVisitForm.show_wisit'), value: 'show_visit' },
        { text: this.$t('StudyVisitForm.visit_description'), value: 'description' },
        { text: this.$t('StudyVisitForm.epoch_allocation'), value: 'epoch_allocation_name' },
        { text: this.$t('StudyVisitForm.visit_start_rule'), value: 'start_rule' },
        { text: this.$t('StudyVisitForm.visit_stop_rule'), value: 'end_rule' },
        { text: this.$t('StudyVisitForm.study_day_label'), value: 'study_day_label' },
        { text: this.$t('StudyVisitForm.study_week_label'), value: 'study_week_label' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('StudyVisitForm.modified_user'), value: 'user_initials' }
      ],
      defaultColumns: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('StudyVisitForm.study_epoch'), value: 'study_epoch_uid' },
        { text: this.$t('StudyVisitForm.visit_type'), value: 'visit_type_name' },
        { text: this.$t('StudyVisitForm.visit_class'), value: 'visit_class' },
        { text: this.$t('StudyVisitForm.anchor_visit_in_group'), value: 'visit_subclass' },
        { text: this.$t('StudyVisitForm.visit_group'), value: 'visit_subname' },
        { text: this.$t('StudyVisitForm.global_anchor_visit'), value: 'is_global_anchor_visit' },
        { text: this.$t('StudyVisitForm.contact_mode'), value: 'visit_contact_mode_name' },
        { text: this.$t('StudyVisitForm.time_reference'), value: 'time_reference_name' },
        { text: this.$t('StudyVisitForm.time_value'), value: 'time_value' },
        { text: this.$t('StudyVisitForm.visit_number'), value: 'order' },
        { text: this.$t('StudyVisitForm.unique_visit_number'), value: 'unique_visit_number' },
        { text: this.$t('StudyVisitForm.visit_name'), value: 'visit_name' },
        { text: this.$t('StudyVisitForm.visit_short_name'), value: 'visit_short_name' },
        { text: this.$t('StudyVisitForm.study_duration_days'), value: 'study_duration_days_label' },
        { text: this.$t('StudyVisitForm.study_duration_weeks'), value: 'study_duration_weeks_label' },
        { text: this.$t('StudyVisitForm.visit_window'), value: 'visit_window' },
        { text: this.$t('StudyVisitForm.collapsible_visit'), value: 'consecutive_visit_group' },
        { text: this.$t('StudyVisitForm.show_wisit'), value: 'show_visit' },
        { text: this.$t('StudyVisitForm.visit_description'), value: 'description' },
        { text: this.$t('StudyVisitForm.epoch_allocation'), value: 'epoch_allocation_name' },
        { text: this.$t('StudyVisitForm.visit_start_rule'), value: 'start_rule' },
        { text: this.$t('StudyVisitForm.visit_stop_rule'), value: 'end_rule' },
        { text: this.$t('StudyVisitForm.study_day_label'), value: 'study_day_label' },
        { text: this.$t('StudyVisitForm.study_week_label'), value: 'study_week_label' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('StudyVisitForm.modified_user'), value: 'user_initials' }
      ],
      editHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('StudyVisitForm.visit_type'), value: 'visit_type_name' },
        { text: this.$t('StudyVisitForm.global_anchor_visit'), value: 'is_global_anchor_visit' },
        { text: this.$t('StudyVisitForm.contact_mode'), value: 'visit_contact_mode_name' },
        { text: this.$t('StudyVisitForm.time_reference'), value: 'time_reference_name' },
        { text: this.$t('StudyVisitForm.time_value'), value: 'time_value' },
        { text: this.$t('StudyVisitForm.visit_name'), value: 'visit_name' },
        { text: this.$t('StudyVisitForm.visit_window'), value: 'visit_window' },
        { text: this.$t('StudyVisitForm.show_wisit'), value: 'show_visit' },
        { text: this.$t('StudyVisitForm.visit_description'), value: 'description' },
        { text: this.$t('StudyVisitForm.visit_start_rule'), value: 'start_rule' },
        { text: this.$t('StudyVisitForm.visit_stop_rule'), value: 'end_rule' }
      ],
      preferredTimeUnit: studyConstants.STUDY_TIME_UNIT_DAY,
      preferredTimeUnits: [],
      selectedStudyVisit: null,
      showForm: false,
      showVisitHistory: false,
      timeUnits: [],
      loading: true,
      barChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        tooltips: {
          enabled: false
        },
        interaction: {
          intersect: false
        },
        scales: {
          xAxes: [{
            ticks: {
              display: false,
              max: 0,
              min: 0
            },
            gridLines: {
              display: false,
              color: '#fff',
              zeroLineColor: '#fff',
              zeroLineWidth: 0
            },
            stacked: false
          }],
          yAxes: [{
            stacked: true
          }]
        },
        indexAxis: 'y'
      },
      lineChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          display: false
        },
        tooltips: {
          callbacks: {
            label: function (tooltipItem, data) {
              return [[data.datasets[tooltipItem.datasetIndex].label, ` ${data.datasets[tooltipItem.datasetIndex].contact_mode}`], [data.datasets[tooltipItem.datasetIndex].visit_type, ` Day ${data.datasets[tooltipItem.datasetIndex].study_day}`, ` ${data.datasets[tooltipItem.datasetIndex].week}`]]
            }
          },
          backgroundColor: 'rgba(226, 230, 240, 0.8)',
          bodyFontColor: '#000',
          displayColors: false,
          bodyFontSize: 15
        },
        interaction: {
          mode: 'dataset'
        },
        scales: {
          yAxes: [{
            gridLines: {
              display: false,
              color: '#fff',
              zeroLineColor: '#fff',
              zeroLineWidth: 0
            },
            ticks: {
              display: false
            }
          }],
          xAxes: [{
            ticks: {
              max: 0,
              min: 1,
              stepSize: 7,
              precision: 0
            },
            scaleLabel: {
              display: true,
              labelString: this.$t('StudyVisitTable.study_day')
            }
          }]
        },
        indexAxis: 'y'
      },
      barChartDatasets: {
        datasets: []
      },
      lineChartDatasets: {
        datasets: []
      },
      chartsKey: 0,
      barChartKey: 0,
      options: {},
      duplicateForm: false,
      editMode: false,
      contactModes: [],
      itemsDisabled: false,
      visitClasses: [
        { label: this.$t('StudyVisitForm.scheduled_visit'), value: visitConstants.CLASS_SINGLE_VISIT },
        { label: this.$t('StudyVisitForm.unscheduled_visit'), value: visitConstants.CLASS_UNSCHEDULED_VISIT },
        { label: this.$t('StudyVisitForm.non_visit'), value: visitConstants.CLASS_NON_VISIT }
      ],
      timeReferences: [],
      showCollapsibleGroupForm: false,
      showStudyVisitsHistory: false,
      visitHistoryItems: [],
      visitSelection: []
    }
  },
  methods: {
    async fetchVisitsHistory () {
      const resp = await studyEpochs.getStudyVisitsVersions(this.selectedStudy.uid)
      return this.transformItems(resp.data)
    },
    transformItems (items) {
      const result = []
      for (const item of items) {
        const newItem = { ...item }
        newItem.study_epoch_uid = this.getStudyEpochName(newItem.study_epoch_uid)
        newItem.is_global_anchor_visit = dataFormating.yesno(newItem.is_global_anchor_visit)
        newItem.show_visit = dataFormating.yesno(newItem.show_visit)
        result.push(newItem)
      }
      return result
    },
    openEditMode () {
      this.headers = this.editHeaders
      this.editMode = true
    },
    closeEditMode () {
      this.fetchStudyVisits()
      this.editMode = false
      this.headers = this.defaultColumns
    },
    disableOthers (item) {
      if (item.min_visit_window_value > 0) {
        item.min_visit_window_value = item.min_visit_window_value * -1
      }
      if (!this.itemsDisabled) {
        this.studyVisits.forEach(visit => {
          this.$set(visit, 'disabled', visit.uid !== item.uid)
        })
        this.itemsDisabled = true
      }
    },
    saveVisit (item) {
      return this.$store.dispatch('studyEpochs/updateStudyVisit', { studyUid: this.selectedStudy.uid, studyVisitUid: item.uid, input: item }).then(resp => {
        this.fetchStudyVisits()
        bus.$emit('notification', { msg: this.$t('StudyVisitForm.update_success') })
        this.itemsDisabled = false
      })
    },
    cancelVisitEditing () {
      this.fetchStudyVisits()
      this.itemsDisabled = false
    },
    edit () {
      this.editMode = true
    },
    openDuplicateForm (item) {
      this.selectedStudyVisit = item
      this.duplicateForm = true
    },
    closeDuplicateForm () {
      this.selectedStudyVisit = null
      this.duplicateForm = false
    },
    fetchStudyVisits (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      params.studyUid = this.selectedStudy.uid
      this.$store.dispatch('studyEpochs/fetchFilteredStudyVisits', params)
    },
    getDisplay (item, name) {
      if (name in this.calculatedItems) {
        return this.calculatedItems[name][item[name]]._displayValue
      } else {
        return item[name]
      }
    },
    createMapping (codelist, param, displayValue) {
      const returnValue = {}
      codelist.forEach(item => {
        item._displayValue = item[displayValue]
        returnValue[item[param]] = item
      })
      return returnValue
    },
    editVisit (item) {
      this.selectedStudyVisit = item
      this.showForm = true
    },
    async openForm () {
      if (this.studyEpochs.length === 0) {
        const options = {
          type: 'warning',
          cancelLabel: this.$t('_global.cancel'),
          agreeLabel: this.$t('StudyVisitForm.add_epoch'),
          redirect: 'epochs'
        }
        if (!await this.$refs.confirm.open(this.$t('StudyVisitForm.create_epoch'), options)) {
          return
        }
      }
      this.showForm = true
    },
    closeForm () {
      this.selectedStudyVisit = null
      this.showForm = false
    },
    async deleteVisit (item) {
      await this.$store.dispatch('studyEpochs/deleteStudyVisit', { studyUid: this.selectedStudy.uid, studyVisitUid: item.uid })
      bus.$emit('notification', { msg: this.$t('StudyVisitTable.delete_success') })
      this.fetchStudyVisits()
    },
    async openVisitHistory (visit) {
      this.selectedStudyVisit = visit
      const resp = await studyEpochs.getStudyVisitVersions(this.selectedStudy.uid, visit.uid)
      this.visitHistoryItems = this.transformItems(resp.data)
      this.showVisitHistory = true
    },
    closeVisitHistory () {
      this.selectedStudyVisit = null
      this.showVisitHistory = false
    },
    getStudyEpochName (studyEpochUid) {
      if (this.studyEpochs) {
        const epoch = this.studyEpochs.find(item => item.uid === studyEpochUid)
        return epoch.epoch_name
      }
      return ''
    },
    getUnitName (unitUid) {
      const unit = this.timeUnits.find(item => item.uid === unitUid)
      if (unit) {
        return unit.name
      }
      return ''
    },
    buildChart () {
      this.loading = true
      this.barChartDatasets.datasets = []
      this.lineChartDatasets.datasets = []
      const negativeDaysEpochs = []
      let maxXvalue = 0
      for (const d of this.studyEpochs) {
        if (d.start_day >= 0) {
          break
        } else {
          negativeDaysEpochs.push(d)
        }
      }
      this.studyEpochs.splice(0, negativeDaysEpochs.length) // Reordering of the epochs with visit with the negative day number
      negativeDaysEpochs.forEach(el => { //  needed for correct timeline display
        this.studyEpochs.unshift(el)
      })
      let startField
      let endField
      if (this.preferredTimeUnit === studyConstants.STUDY_TIME_UNIT_DAY) {
        startField = 'start_day'
        endField = 'end_day'
      } else {
        startField = 'start_week'
        endField = 'end_week'
      }
      this.studyEpochs.forEach(el => {
        if (el.epoch_name !== visitConstants.EPOCH_BASIC) {
          if (el[endField] > maxXvalue) {
            maxXvalue = el[endField]
          }
          this.barChartDatasets.datasets.push(
            {
              data: [[el[startField], el[endField]]],
              backgroundColor: el.color_hash, // and for the rest we need to just provide duration of epoch, but if the first epoch has positive first day number than we need to build
              label: el.epoch_name // such array just for the first epoch
            }
          )
        }
      })
      this.singleStudyVisits.forEach(el => {
        const value = this.preferredTimeUnit === studyConstants.STUDY_TIME_UNIT_DAY ? el.study_day_number : el.study_week_number
        this.lineChartDatasets.datasets.push(
          {
            data: [{
              x: value,
              y: 0,
              r: 7
            }],
            study_day: el.study_day_label,
            label: el.visit_name,
            backgroundColor: 'rgb(6, 57, 112)',
            contact_mode: el.visit_contact_mode_name,
            visit_type: el.visit_type_name,
            week: el.study_week_label
          }
        )
      })
      if (this.singleStudyVisits.length > 0) {
        const lastVisitDay = this.singleStudyVisits[this.singleStudyVisits.length - 1].study_day_number
        let minXvalue
        let label
        let stepSize
        if (this.preferredTimeUnit === studyConstants.STUDY_TIME_UNIT_DAY) {
          minXvalue = this.singleStudyVisits[0].study_day_number
          label = this.$t('StudyVisitTable.study_day')
          stepSize = 7 * Math.ceil(lastVisitDay / 100)
        } else {
          minXvalue = this.singleStudyVisits[0].study_week_number
          label = this.$t('StudyVisitTable.study_week')
          stepSize = 1
        }
        this.lineChartOptions.scales.xAxes[0].scaleLabel.labelString = label
        this.barChartOptions.scales.xAxes[0].ticks.max = Math.round(maxXvalue)
        this.lineChartOptions.scales.xAxes[0].ticks.max = Math.round(maxXvalue)
        this.barChartOptions.scales.xAxes[0].ticks.min = (minXvalue < 0) ? Math.round(minXvalue) - 1 : Math.round(minXvalue)
        this.lineChartOptions.scales.xAxes[0].ticks.min = (minXvalue < 0) ? Math.round(minXvalue) - 1 : Math.round(minXvalue)
        this.lineChartOptions.scales.xAxes[0].ticks.stepSize = stepSize
      }
      this.loading = false
      this.chartsKey += 1
      this.barChartKey += 1
    },
    groupSelectedVisits (selection) {
      if (!selection.length) {
        bus.$emit('notification', { msg: this.$t('GroupStudyVisits.no_selection'), type: 'warning' })
        return
      }
      const visitUids = selection.map(item => item.uid)
      studyEpochs.createCollapsibleVisitGroup(this.selectedStudy.uid, visitUids).then(() => {
        this.collapsibleVisitGroupCreated()
      }).catch(err => {
        if (err.response.status === 400) {
          this.visitSelection = selection
          this.showCollapsibleGroupForm = true
        }
      })
    },
    closeCollapsibleVisitGroupForm () {
      this.showCollapsibleGroupForm = false
      this.visitSelection = []
    },
    collapsibleVisitGroupCreated () {
      bus.$emit('notification', { msg: this.$t('CollapsibleVisitGroupForm.creation_success') })
      this.fetchStudyVisits()
    },
    updatePreferredTimeUnit (value) {
      for (const timeUnit of this.preferredTimeUnits) {
        if (timeUnit.name === value) {
          this.$store.dispatch('studiesGeneral/setStudyPreferredTimeUnit', timeUnit.uid)
          this.fetchStudyVisits()
          break
        }
      }
    }
  },
  created () {
    this.visitConstants = visitConstants
  },
  mounted () {
    this.calculatedItems = {}
    terms.getByCodelist('timepointReferences').then(resp => {
      this.calculatedItems.time_reference_uid = this.createMapping(resp.data.items, 'term_uid', 'sponsor_preferred_name')
      terms.getByCodelist('epochs').then(resp => {
        this.calculatedItems.epoch_uid = this.createMapping(resp.data.items, 'term_uid', 'sponsor_preferred_name')
      })
    })
    this.$store.dispatch('studyEpochs/fetchStudyEpochs', this.selectedStudy.uid).then(() => {
      const params = {
        page_number: 1,
        total_count: true,
        page_size: this.$refs.table.computedItemsPerPage,
        studyUid: this.selectedStudy.uid
      }
      this.$store.dispatch('studyEpochs/fetchFilteredStudyVisits', params)
    })
    units.getBySubset(unitConstants.TIME_UNIT_SUBSET_STUDY_TIME).then(resp => {
      this.timeUnits = resp.data.items
    })
    units.getBySubset(unitConstants.TIME_UNIT_SUBSET_STUDY_PREFERRED_TIME_UNIT).then(resp => {
      this.preferredTimeUnits = resp.data.items
    })
    terms.getByCodelist('contactModes').then(resp => {
      this.contactModes = resp.data.items
    })
    terms.getByCodelist('timepointReferences').then(resp => {
      this.timeReferences = resp.data.items
    })
    if (this.studyPreferredTimeUnit) {
      this.preferredTimeUnit = this.studyPreferredTimeUnit.time_unit_name
    }
  },
  watch: {
    studyVisits () {
      this.buildChart()
    }
  }
}
</script>

<style scoped>
  .cellWidth {
    width: 200px;
  }
</style>
