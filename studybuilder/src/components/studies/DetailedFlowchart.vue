<template>
<div class="pa-4" style="overflow-x: auto" v-resize="onResize">
  <v-menu
    v-if="footnoteMode"
    :close-on-click="false"
    :close-on-content-click="false"
    max-height="800px"
    width="1500px"
    offset-y
    v-model="footnoteMode"
    content-class="center">
    <v-card width="1000px" min-height="150px">
      <v-card-title class="dialog-title">{{$t('StudyFootnoteEditForm.select_footnote_items')}}
        <v-spacer/>
        <v-btn
          color="success"
          icon
          @click="saveElementsForFootnote"
          :loading="footnoteUpdateLoading"
          >
          <v-icon>mdi-content-save-outline</v-icon>
        </v-btn>
        <v-btn
          color="primary"
          icon
          @click="disableFootnoteMode"
          >
          <v-icon>mdi-close</v-icon>
      </v-btn>
      </v-card-title>
      <v-divider/>
      <v-card flat class="parameterBackground mx-3 mt-3">
        <v-card-text>
          <v-row>
            <n-n-parameter-highlighter
              :name="activeFootnote.footnote ? activeFootnote.footnote.name : activeFootnote.footnote_template.name"
              />
          </v-row>
        </v-card-text>
      </v-card>
    </v-card>
  </v-menu>
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
      v-model="showFlowchartGroups"
      :label="$t('DetailedFlowchart.show_flowchart_groups')"
      hide-details
      class="ml-2"
      :loading="soaGroupsUpdate"
      :disabled="soaGroupsUpdate || selectedStudyVersion !== null"
      />
    <v-spacer />
    <template v-if="!readOnly">
      <v-btn
        fab
        small
        class="mr-2"
        :title="$t('GroupStudyVisits.title')"
        v-show="multipleConsecutiveVisitsSelected()"
        @click="groupSelectedVisits()"
        :disabled="footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
        >
        <v-icon>mdi-arrow-expand-horizontal</v-icon>
      </v-btn>
      <v-menu
        :close-on-content-click="false"
        max-height="800px"
        max-width="500px"
        offset-y
        v-model="showEditForm"
        content-class="mt-4">
        <template v-slot:activator="{ on, attrs }">
          <div>
            <v-btn
              color="primary"
              fab
              small
              class="mr-2"
              v-bind="attrs"
              v-on="on"
              :disabled="footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
              >
              <v-icon>mdi-pencil-outline</v-icon>
            </v-btn>
          </div>
        </template>
        <v-card color="dfltBackground">
          <v-card-text>
            <v-btn block class="mb-2" @click="redirectTo('epochs')">
              <v-icon left>mdi-arrow-top-right-bold-box-outline</v-icon>
              {{ $t('DetailedFlowchart.study_epochs') }}
            </v-btn>
            <v-btn block class="mb-2" @click="redirectTo('visits')">
              <v-icon left>mdi-arrow-top-right-bold-box-outline</v-icon>
              {{ $t('DetailedFlowchart.study_visits') }}
            </v-btn>
            <v-btn block class="mb-2" @click="redirectTo('activities')">
              <v-icon left>mdi-arrow-top-right-bold-box-outline</v-icon>
              {{ $t('DetailedFlowchart.study_activities') }}
            </v-btn>
            <v-btn block class="mb-2" @click="redirectTo('footnotes')">
              <v-icon left>mdi-arrow-top-right-bold-box-outline</v-icon>
              {{ $t('DetailedFlowchart.soa_footnotes') }}
            </v-btn>
            <v-btn block class="mb-2" @click="redirectTo('instructions')">
              <v-icon left>mdi-arrow-top-right-bold-box-outline</v-icon>
              {{ $t('DetailedFlowchart.activity_instructions') }}
            </v-btn>
          </v-card-text>
        </v-card>
      </v-menu>
      <v-btn
        fab
        small
        @click="toggleActivitySelectionDisplay(false)"
        :title="$t('DetailedFlowchart.hide_activity_selection')"
        :disabled="footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
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
        :disabled="footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
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
        :disabled="footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
        >
        <v-icon>
          mdi-pencil-box-multiple-outline
        </v-icon>
      </v-btn>
      <v-menu rounded offset-y>
        <template v-slot:activator="{ attrs, on }">
          <v-btn
            fab
            small
            color="nnGreen1"
            class="ml-2 white--text"
            v-bind="attrs"
            v-on="on"
            :title="$t('DataTableExportButton.export')"
            >
            <v-icon>mdi-download-outline</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item
            link
            @click="downloadCSV"
            >
            <v-list-item-title>CSV</v-list-item-title>
          </v-list-item>
          <v-list-item
            link
            @click="downloadDOCX"
            >
            <v-list-item-title>DOCX</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
      <v-btn
        class="mr-2"
        color="secondary"
        fab
        small
        :title="$t('NNTableTooltips.history')"
        @click="openHistory"
        >
        <v-icon>mdi-history</v-icon>
      </v-btn>
    </template>
  </div>
  <div ref="tableContainer" class="sticky-header" :style="`height: ${tableHeight}px`">
  <table :aria-label="$t('DetailedFlowchart.table_caption')">
    <thead>
      <tr ref="firstHeader">
        <th width="2%" rowspan="4" scope="col">
        </th>
        <th width="25%" rowspan="4" scope="col">{{ $t('DetailedFlowchart.activities') }}</th>
        <th width="10%" scope="col">{{ $t('DetailedFlowchart.study_epoch') }}</th>
        <template v-if="soaContent">
          <th v-for="(cell, index) in soaEpochRow" :key="`epoch-${index}`" class="text-vertical" scope="col">
            <v-badge
              color="secondary--text"
              :content="cell.footnotes && cell.refs.length ? getElementFootnotes(cell.refs[0].uid) : ''"
              class="mt-3"
            >
              {{ cell.text }}
            </v-badge>
            <v-btn
              v-if="footnoteMode && cell.text !== '' && cell.refs.length && !checkIfElementHasFootnote(cell.refs[0].uid)"
              x-small
              icon
              class="mx-0 px-0"
              color="primary"
              @click="cell.refs.length && addElementForFootnote(cell.refs[0].uid, 'StudyEpoch')">
              <v-icon x-small>
                mdi-plus
              </v-icon>
            </v-btn>
            <v-btn
              v-else-if="footnoteMode && cell.text !== '' && cell.refs.length && checkIfElementHasFootnote(cell.refs[0].uid)"
              x-small
              icon
              class="mx-0 px-0"
              @click="cell.refs.length && removeElementForFootnote(cell.refs[0].uid)"
              color="red">
              <v-icon x-small>
                mdi-close
              </v-icon>
            </v-btn>
          </th>
        </template>
        <template v-else>
          <th colspan="2" scope="col"></th>
        </template>
      </tr>
      <tr>
        <th :style="`top: ${firstHeaderHeight}px`" scope="col">{{ $t('DetailedFlowchart.visit_short_name') }}</th>
        <template v-if="soaContent">
          <th v-for="(cell, index) in soaVisitRow" :key="`shortName-${index}`" :style="`top: ${firstHeaderHeight}px`" scope="col">
            <div class="d-flex align-center">
              <v-badge
                color="secondary--text"
                :content="cell.refs.length ? getElementFootnotes(cell.refs[0].uid) : ''"
                class="visitFootnote"
              >
                {{ cell.text }}
              </v-badge>
              <v-btn
                v-if="footnoteMode && cell.refs.length && !checkIfElementHasFootnote(cell.refs[0].uid)"
                x-small
                icon
                class="mx-0 px-0"
                @click="cell.refs.length && addElementForFootnote(cell.refs[0].uid, 'StudyVisit')">
                <v-icon x-small>
                  mdi-plus
                </v-icon>
              </v-btn>
              <v-btn
                v-else-if="footnoteMode && cell.refs.length && checkIfElementHasFootnote(cell.refs[0].uid)"
                x-small
                icon
                class="mx-0 px-0"
                @click="cell.refs.length && removeElementForFootnote(cell.refs[0].uid)"
                color="red">
                <v-icon x-small>
                  mdi-close
                </v-icon>
              </v-btn>
              <v-checkbox
                v-if="cell.refs.length === 1 && !footnoteMode"
                v-model="selectedVisitIndexes"
                :value="index"
                hide-details
                small
                multiple
                :disabled="footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
                />
              <v-btn
                v-else-if="!footnoteMode"
                icon
                color="error"
                x-small
                :title="$t('GroupStudyVisits.delete_title')"
                @click="deleteVisitGroup(cell.text)"
                :disabled="footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
                >
                <v-icon>mdi-delete-outline</v-icon>
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
        <template v-if="soaContent">
          <th v-for="(cell, index) in soaDayRow" :key="`week-${index}`" :style="`top: ${thirdHeaderRowTop}px`" scope="col">
            {{ cell.text }}
          </th>
        </template>
        <template v-else>
          <th colspan="2" :style="`top: ${thirdHeaderRowTop}px`" scope="col"></th>
        </template>
      </tr>
      <tr>
        <th :style="`top: ${fourthHeaderRowTop}px`" scope="col">{{ $t('DetailedFlowchart.visit_window') }}</th>
        <template v-if="soaContent">
          <th v-for="(cell, index) in soaWindowRow" :key="`window-${index}`" :style="`top: ${fourthHeaderRowTop}px`" scope="col">
            {{ cell.text }}
          </th>
        </template>
        <template v-else>
          <th colspan="2" :style="`top: ${fourthHeaderRowTop}px`" scope="col"></th>
        </template>
      </tr>
    </thead>
    <tbody>
      <template v-for="(row, index) in soaRows">
        <tr v-if="showSoaRow(index, row)" :class="getSoaRowClasses(row)" :key="`row-${index}`">
          <td>
            <v-btn
              v-if="!readOnly && getSoaRowType(row) !== 'activity'"
              icon
              @click="toggleRowState(`row-${index}`)"
              >
              <v-icon>{{ getDisplayButtonIcon(`row-${index}`) }}</v-icon>
            </v-btn>
          </td>
          <td :class="getSoaFirstCellClasses(row.cells[0])">
            <div class="d-flex align-center">
              <v-checkbox
                v-if="!readOnly && !footnoteMode && getSoaRowType(row) === 'activity'"
                hide-details
                @change="value => toggleActivitySelection(row, value)"
                :value="studyActivitySelection.findIndex(cell => cell.refs.length && cell.refs[0].uid === row.cells[0].refs[0].uid) !== -1"
                :disabled="!checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
                />
              <v-checkbox
                v-if="!readOnly && !footnoteMode && getSoaRowType(row) === 'subGroup'"
                @change="value => toggleSubgroupActivitiesSelection(row, value)"
                on-icon="mdi-checkbox-multiple-marked-outline"
                off-icon="mdi-checkbox-multiple-blank-outline"
                hide-details
                :disabled="!checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
                />
              <v-badge
                color="secondary--text"
                :content="row.cells[0].refs.length ? getElementFootnotes(row.cells[0].refs[0].uid) : ''"
                >
                {{ row.cells[0].text }}
              </v-badge>
              <v-btn
                v-if="footnoteMode && row.cells[0].refs.length && !checkIfElementHasFootnote(row.cells[0].refs[0].uid)"
                x-small
                icon
                class="mx-0 px-0"
                @click="row.cells[0].refs.length && addElementForFootnote(row.cells[0].refs[0].uid, row.cells[0].refs[0].type)">
                <v-icon x-small>
                  mdi-plus
                </v-icon>
              </v-btn>
              <v-btn
                v-else-if="footnoteMode && row.cells[0].refs.length && checkIfElementHasFootnote(row.cells[0].refs[0].uid)"
                x-small
                icon
                class="mx-0 px-0"
                @click="row.cells[0].refs.length && removeElementForFootnote(row.cells[0].refs[0].uid)"
                color="red">
                <v-icon x-small>
                  mdi-close
                </v-icon>
              </v-btn>
            </div>
          </td>
          <td>
            <v-btn
              v-if="!readOnly"
              icon
              @click="toggleLevelDisplay(row)"
              :title="$t('DetailedFlowchart.toggle_soa_group_display')"
              :disabled="footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
              >
              <v-icon v-if="getLevelDisplayState(row)" color="success">mdi-eye-outline</v-icon>
              <v-icon v-else>mdi-eye-off-outline</v-icon>
            </v-btn>
          </td>
          <td v-if="getSoaRowType(row) !== 'activity'" :colspan="row.cells.length - 1"></td>
          <td v-else v-for="(visitCell, visitIndex) in soaVisitRow" :key="`row-${index}-cell-${visitIndex}`">
            <v-row>
              <v-badge
                color="secondary--text"
                :content="row.cells[visitIndex + 1].refs.length ? getElementFootnotes(row.cells[visitIndex + 1].refs[0].uid) : ''"
                overlap
                >
                <v-checkbox
                  v-if="!readOnly && row.cells[0].refs.length && visitCell.refs.length && currentSelectionMatrix[row.cells[0].refs[0].uid][visitCell.refs[0].uid]"
                  v-model="currentSelectionMatrix[row.cells[0].refs[0].uid][visitCell.refs[0].uid].value"
                  color="success"
                  @change="value => row.cells[0].refs.length && updateSchedule(value, row.cells[0].refs[0].uid, visitCell)"
                  :disabled="row.cells[0].refs.length && visitCell.refs.length && isCheckboxDisabled(row.cells[0].refs[0].uid, visitCell.refs[0].uid) || footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
                  hide-details
                  on-icon="mdi-checkbox-marked-circle-outline"
                  off-icon="mdi-checkbox-blank-circle-outline"
                  class="mx-0 px-0"
                  />
              </v-badge>
              <v-btn
                v-if="footnoteMode && row.cells[0].refs.length && visitCell.refs.length && row.cells[visitIndex + 1].refs.length && currentSelectionMatrix[row.cells[0].refs[0].uid][visitCell.refs[0].uid].uid && !checkIfElementHasFootnote(row.cells[visitIndex + 1].refs[0].uid)"
                x-small
                icon
                class="mx-0 px-0"
                @click="row.cells[visitIndex + 1].refs.length && addElementForFootnote(row.cells[visitIndex + 1].refs[0].uid, row.cells[visitIndex + 1].refs[0].type)">
                <v-icon x-small>
                  mdi-plus
                </v-icon>
              </v-btn>
              <v-btn
                v-if="footnoteMode && row.cells[0].refs.length && visitCell.refs.length && row.cells[visitIndex + 1].refs.length && currentSelectionMatrix[row.cells[0].refs[0].uid][visitCell.refs[0].uid].uid && checkIfElementHasFootnote(row.cells[visitIndex + 1].refs[0].uid)"
                x-small
                icon
                class="mx-0 px-0"
                @click="row.cells[visitIndex + 1].refs.length && removeElementForFootnote(row.cells[visitIndex + 1].refs[0].uid)"
                color="red">
                <v-icon x-small>
                  mdi-close
                </v-icon>
              </v-btn>
            </v-row>
          </td>
        </tr>
      </template>
    </tbody>
  </table>
  </div>
  <v-expansion-panels class="mt-4">
    <v-expansion-panel>
      <v-expansion-panel-header>
        <div class="secondary--text text-h5"><v-icon color="secondary" class="mr-2">mdi-map-marker-outline</v-icon>SoA Footnotes</div>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <div v-for="footnote of studyFootnotes" :key="footnote.uid" class="my-1">
          <v-card flat class="parameterBackground">
            <v-card-text>
              <v-row>
                <div class="secondary--text mt-2 ml-1">{{ footnote.order | letteredOrder }}: &nbsp;</div>
                <n-n-parameter-highlighter
                  :name="footnote.footnote ? footnote.footnote.name : footnote.footnote_template.name"
                  class="mt-2"
                  />
                <v-spacer/>
                <v-btn
                  icon
                  color="primary"
                  @click="editStudyFootnote(footnote)"
                  :disabled="footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
                  >
                  <v-icon>mdi-pencil-outline</v-icon>
                </v-btn>
                <v-btn
                  icon
                  color="primary"
                  @click="enableFootnoteMode(footnote)"
                  :disabled="footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
                  >
                  <v-icon>mdi-table-plus</v-icon>
                </v-btn>
              </v-row>
            </v-card-text>
          </v-card>
        </div>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>
  <study-activity-schedule-batch-edit-form
    :open="showBatchEditForm"
    :selection="formattedStudyActivitySelection"
    :current-selection-matrix="currentSelectionMatrix"
    @updated="() => loadSoaContent(true)"
    @close="showBatchEditForm = false"
    />
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
  <study-footnote-edit-form
    :open="showFootnoteEditForm"
    :study-footnote="selectedFootnote"
    @close="closeEditForm"
    @updated="fetchFootnotes"
    @enableFootnoteMode="enableFootnoteMode"
    />
  <v-dialog
    v-model="showHistory"
    @keydown.esc="closeHistory"
    :max-width="globalHistoryDialogMaxWidth"
    :fullscreen="globalHistoryDialogFullscreen"
    persistent
    >
    <history-table
      :headers="historyHeaders"
      :items="historyItems"
      :items-total="historyItemsTotal"
      @close="closeHistory"
      :title="historyTitle"
      change-field="action"
      @refresh="options => getHistoryData(options)"
      />
  </v-dialog>
</div>
</template>

<script>
import { bus } from '@/main'
import CollapsibleVisitGroupForm from './CollapsibleVisitGroupForm'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import exportLoader from '@/utils/exportLoader'
import HistoryTable from '@/components/tools/HistoryTable'
import { mapGetters } from 'vuex'
import study from '@/api/study'
import StudyActivityScheduleBatchEditForm from './StudyActivityScheduleBatchEditForm'
import studyConstants from '@/constants/study.js'
import studyEpochs from '@/api/studyEpochs'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import StudyFootnoteEditForm from '@/components/studies/StudyFootnoteEditForm'
import dataFormating from '@/utils/dataFormating'
import _isEmpty from 'lodash/isEmpty'
import { accessGuard } from '@/mixins/accessRoleVerifier'

export default {
  mixins: [accessGuard],
  components: {
    CollapsibleVisitGroupForm,
    ConfirmDialog,
    HistoryTable,
    StudyActivityScheduleBatchEditForm,
    NNParameterHighlighter,
    StudyFootnoteEditForm
  },
  props: {
    readOnly: {
      type: Boolean,
      default: false
    },
    update: Number,
    redirectFootnote: Object
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion',
      studyPreferredTimeUnit: 'studiesGeneral/studyPreferredTimeUnit',
      studyFootnotes: 'studyFootnotes/studyFootnotes'
    }),
    soaEpochRow () {
      if (this.soaContent) {
        return this.soaContent.rows[0].cells.slice(1)
      }
      return []
    },
    soaVisitRow () {
      if (this.soaContent) {
        return this.soaContent.rows[1].cells.slice(1)
      }
      return []
    },
    soaDayRow () {
      if (this.soaContent) {
        return this.soaContent.rows[2].cells.slice(1)
      }
      return []
    },
    soaWindowRow () {
      if (this.soaContent) {
        return this.soaContent.rows[3].cells.slice(1)
      }
      return []
    },
    soaRows () {
      if (this.soaContent) {
        return this.soaContent.rows.slice(4)
      }
      return []
    },
    thirdHeaderRowTop () {
      return this.initialFirstHeaderHeight + this.firstHeaderHeight
    },
    fourthHeaderRowTop () {
      return this.firstHeaderHeight + (this.initialFirstHeaderHeight * 2)
    },
    formattedStudyActivitySelection () {
      return this.studyActivitySelection.map(cell => {
        return { study_activity_uid: cell.refs?.[0]?.uid, activity: { name: cell.text } }
      })
    },
    timingHeaderTitle () {
      if (!this.studyPreferredTimeUnit || this.studyPreferredTimeUnit.time_unit_name === studyConstants.STUDY_TIME_UNIT_WEEK) {
        return this.$t('_global.week')
      }
      return this.$t('_global.day')
    },
    historyTitle () {
      return this.$t('DetailedFlowchart.history_title', { study: this.selectedStudy.uid })
    },
    selectedVisits () {
      return this.selectedVisitIndexes.map(cell => this.soaVisitRow[cell])
    }
  },
  data () {
    return {
      currentSelectionMatrix: {},
      expandAllRows: false,
      showFlowchartGroups: false,
      rowsDisplayState: {},
      initialFirstHeaderHeight: 0,
      firstHeaderHeight: 0,
      selectedVisitIndexes: [],
      showBatchEditForm: false,
      showCollapsibleGroupForm: false,
      showEditForm: false,
      studyActivities: [],
      studyActivitySchedules: [],
      studyActivitySelection: [],
      studyVisits: [],
      tableHeight: 500,
      activeFootnote: {},
      footnoteMode: false,
      elementsForFootnote: {
        referenced_items: []
      },
      selectedFootnote: null,
      showFootnoteEditForm: false,
      showHistory: false,
      footnoteUpdateLoading: false,
      soaGroupsUpdate: false,
      historyHeaders: [
        { text: this.$t('DetailedFlowchart.history_object_type'), value: 'object_type' },
        { text: this.$t('_global.description'), value: 'description' },
        { text: this.$t('_global.modified_by'), value: 'user_initials' }
      ],
      historyItems: [],
      historyItemsTotal: 0,
      soaContent: null
    }
  },
  methods: {
    showSoaRow (index, row) {
      let key = `row-${index}`
      let result = true
      while (true) {
        if (this.rowsDisplayState[key].parent !== undefined && this.rowsDisplayState[key].parent !== null) {
          const parentIndex = this.rowsDisplayState[key].parent
          key = `row-${parentIndex}`
          if (this.rowsDisplayState[key]) {
            // We want to check if parent is an soaGroup or not (not parent === soaGroup)
            const parentHasParent = this.rowsDisplayState[key].parent !== undefined && this.rowsDisplayState[key].parent !== null
            if ((this.showFlowchartGroups || (!this.showFlowchartGroups && parentHasParent)) && !this.rowsDisplayState[key].value) {
              result = false
              break
            }
          } else {
            console.log(`Warning: key ${key} not found in displayState!!`)
          }
          continue
        }
        break
      }
      if (row.cells && row.cells.length) {
        if (row.cells[0].style === 'soaGroup') {
          return this.showFlowchartGroups
        }
        if (row.cells[0].style === 'group') {
          return !this.showFlowchartGroups || result
        }
      }
      return result
    },
    getSoaRowType (row) {
      return row.cells[0].style
    },
    getSoaRowClasses (row) {
      if (row.cells && row.cells.length) {
        if (row.cells[0].style === 'soaGroup') {
          return 'flowchart text-uppercase'
        }
        if (row.cells[0].style === 'group') {
          return 'group'
        }
      }
      return ''
    },
    getSoaFirstCellClasses (cell) {
      if (cell.style === 'soaGroup' || cell.style === 'group') {
        return 'text-strong'
      }
      if (cell.style === 'subGroup') {
        return 'subgroup'
      }
      return 'activity'
    },
    getStudyActivitiesForSoaGroup (soaGroupUid) {
      let groupFound = false
      const result = []
      for (const row of this.soaRows) {
        if (row.cells[0].style === 'soaGroup' && row.cells[0].refs?.[0]?.uid === soaGroupUid) {
          groupFound = true
        } else if (groupFound) {
          if (row.cells[0].style === 'activity') {
            result.push(row.cells[0])
          } else if (row.cells[0].style === 'soaGroup') {
            break
          }
        }
      }
      return result
    },
    getStudyActivitiesForGroup (groupUid) {
      let groupFound = false
      const result = []
      for (const row of this.soaRows) {
        if (row.cells[0].style === 'group' && row.cells[0].refs?.[0]?.uid === groupUid) {
          groupFound = true
        } else if (groupFound) {
          if (row.cells[0].style === 'activity') {
            result.push(row.cells[0])
          } else if (row.cells[0].style === 'group') {
            break
          }
        }
      }
      return result
    },
    getStudyActivitiesForSubgroup (subgroupUid) {
      let subgroupFound = false
      const result = []
      for (const row of this.soaRows) {
        if (row.cells[0].style === 'subGroup' && row.cells[0].refs?.[0]?.uid === subgroupUid) {
          subgroupFound = true
        } else if (subgroupFound) {
          if (row.cells[0].style === 'activity') {
            result.push(row.cells[0])
          } else {
            break
          }
        }
      }
      return result
    },
    getElementFootnotes (uid) {
      let footnotesLetters = ''
      this.studyFootnotes.forEach(footnote => {
        footnote.referenced_items.forEach(item => {
          if (item.item_uid === uid) {
            footnotesLetters += dataFormating.letteredOrder(footnote.order)
          } else if (uid && typeof uid !== 'string' && uid.includes(item.item_uid)) {
            footnotesLetters += dataFormating.letteredOrder(footnote.order)
          }
        })
      })
      return Array.from(new Set(footnotesLetters.split(''))).toString()
    },
    enableFootnoteMode (footnote) {
      this.activeFootnote = footnote
      this.elementsForFootnote.referenced_items = footnote.referenced_items
      this.footnoteMode = true
    },
    disableFootnoteMode () {
      if (this.$route.params.footnote) {
        this.$router.push({ name: 'StudyActivities', params: { tab: 'footnotes' } })
        this.$route.params.footnote = null
      }
      this.activeFootnote = {}
      this.elementsForFootnote.referenced_items = []
      this.footnoteMode = false
      this.fetchFootnotes()
    },
    addElementForFootnote (uid, type) {
      if (typeof uid !== 'string') {
        uid.forEach(u => {
          this.elementsForFootnote.referenced_items.push({ item_uid: u, item_type: type })
        })
      } else {
        this.elementsForFootnote.referenced_items.push({ item_uid: uid, item_type: type })
      }
    },
    removeFootnote (uid) {
      const indexToRemove = this.elementsForFootnote.referenced_items.findIndex(item => item.item_uid === uid)
      if (indexToRemove !== -1) {
        this.elementsForFootnote.referenced_items.splice(indexToRemove, 1)
      }
    },
    removeElementForFootnote (uid) {
      if (typeof uid !== 'string') {
        uid.forEach(u => {
          this.removeFootnote(u)
        })
      } else {
        this.removeFootnote(uid)
      }
    },
    saveElementsForFootnote () {
      this.footnoteUpdateLoading = true
      study.updateStudyFootnote(this.selectedStudy.uid, this.activeFootnote.uid, this.elementsForFootnote).then(() => {
        this.footnoteUpdateLoading = false
        this.disableFootnoteMode()
        bus.$emit('notification', { msg: this.$t('StudyFootnoteEditForm.update_success') })
      })
    },
    checkIfElementHasFootnote (elUid) {
      if (elUid && typeof elUid === 'string') {
        return this.elementsForFootnote.referenced_items.find(item => item.item_uid === elUid)
      } else if (elUid) {
        return this.elementsForFootnote.referenced_items.find(item => item.item_uid === elUid[0])
      }
    },
    editStudyFootnote (studyFootnote) {
      this.selectedFootnote = studyFootnote
      this.showFootnoteEditForm = true
    },
    closeEditForm () {
      this.showFootnoteEditForm = false
      this.selectedFootnote = null
    },
    fetchFootnotes () {
      const params = {
        page_number: 1,
        page_size: 0,
        total_count: true,
        studyUid: this.selectedStudy.uid,
        study_value_version: this.selectedStudyVersion
      }
      this.$store.dispatch('studyFootnotes/fetchStudyFootnotes', params)
    },
    isCheckboxDisabled (studyActivityUid, studyVisitUid) {
      const state = this.currentSelectionMatrix[studyActivityUid][studyVisitUid]
      return this.readOnly || (state.value && !state.uid) || (!state.value && state.uid !== null)
    },
    getCurrentDisplayValue (rowKey) {
      const currentValue = this.rowsDisplayState[rowKey].value
      if (currentValue === undefined) {
        return false
      }
      return currentValue
    },
    getDisplayButtonIcon (rowKey) {
      return (this.getCurrentDisplayValue(rowKey)) ? 'mdi-chevron-down' : 'mdi-chevron-right'
    },
    getLevelDisplayState (row) {
      return !row.hide
    },
    toggleRowState (rowKey) {
      const currentValue = this.getCurrentDisplayValue(rowKey)
      this.$set(this.rowsDisplayState[rowKey], 'value', !currentValue)
    },
    toggleAllRowState (value) {
      for (const key in this.rowsDisplayState) {
        this.$set(this.rowsDisplayState[key], 'value', value)
      }
    },
    toggleActivitySelection (row, value) {
      const activityCell = row.cells[0]
      if (value) {
        this.studyActivitySelection.push(activityCell)
      } else {
        for (let i = 0; i < this.studyActivitySelection.length; i++) {
          if (this.studyActivitySelection[i].refs?.[0]?.uid === activityCell.refs?.[0]?.uid) {
            this.studyActivitySelection.splice(i, 1)
            break
          }
        }
      }
    },
    async updateStudyActivity (studyActivityCell, data) {
      await study.updateStudyActivity(this.selectedStudy.uid, studyActivityCell.refs?.[0]?.uid, data)
    },
    async toggleLevelDisplay (row) {
      const firstCell = row.cells[0]
      let activityCells
      let field

      if (firstCell.style === 'activity') {
        activityCells = [firstCell]
        field = 'show_activity_in_protocol_flowchart'
      } else if (firstCell.style === 'subGroup') {
        activityCells = this.getStudyActivitiesForSubgroup(firstCell.refs?.[0]?.uid)
        field = 'show_activity_subgroup_in_protocol_flowchart'
      } else if (firstCell.style === 'group') {
        activityCells = this.getStudyActivitiesForGroup(firstCell.refs?.[0]?.uid)
        field = 'show_activity_group_in_protocol_flowchart'
      } else if (firstCell.style === 'soaGroup') {
        activityCells = this.getStudyActivitiesForSoaGroup(firstCell.refs?.[0]?.uid)
        field = 'show_soa_group_in_protocol_flowchart'
      }
      const payload = []
      for (const cell of activityCells) {
        const operation = {
          method: 'PATCH',
          content: {
            study_activity_uid: cell.refs?.[0]?.uid,
            content: {
            }
          }
        }
        operation.content.content[field] = row.hide
        payload.push(operation)
      }
      await study.studyActivityBatchOperations(this.selectedStudy.uid, payload)
      row.hide = !row.hide
    },
    updateGroupedSchedule (value, studyActivityUid, studyVisitCell) {
      if (value) {
        const data = []
        for (const visitRef of studyVisitCell.refs.length ? studyVisitCell.refs : []) {
          data.push({
            method: 'POST',
            content: {
              study_activity_uid: studyActivityUid,
              study_visit_uid: visitRef.uid
            }
          })
        }
        study.studyActivityScheduleBatchOperations(this.selectedStudy.uid, data).then(resp => {
          const scheduleUids = resp.data.map(item => item.content.study_activity_schedule_uid)
          this.currentSelectionMatrix[studyActivityUid][studyVisitCell.refs?.[0]?.uid].uid = scheduleUids
        })
      } else {
        const data = []
        for (const scheduleUid of this.currentSelectionMatrix[studyActivityUid][studyVisitCell.refs?.[0]?.uid].uid) {
          data.push({
            method: 'DELETE',
            content: {
              uid: scheduleUid
            }
          })
        }
        study.studyActivityScheduleBatchOperations(this.selectedStudy.uid, data).then(() => {
          this.currentSelectionMatrix[studyActivityUid][studyVisitCell.refs?.[0]?.uid].uid = null
        })
      }
    },
    updateSchedule (value, studyActivityUid, studyVisitCell) {
      if (studyVisitCell.refs?.length > 1) {
        this.updateGroupedSchedule(value, studyActivityUid, studyVisitCell)
        return
      }
      if (value) {
        const data = {
          study_activity_uid: studyActivityUid,
          study_visit_uid: studyVisitCell.refs?.[0]?.uid
        }
        study.createStudyActivitySchedule(this.selectedStudy.uid, data).then(resp => {
          this.currentSelectionMatrix[studyActivityUid][studyVisitCell.refs?.[0]?.uid].uid = resp.data.study_activity_schedule_uid
        })
      } else {
        const scheduleUid = this.currentSelectionMatrix[studyActivityUid][studyVisitCell.refs?.[0]?.uid].uid
        study.deleteStudyActivitySchedule(this.selectedStudy.uid, scheduleUid).then(() => {
          this.currentSelectionMatrix[studyActivityUid][studyVisitCell.refs?.[0]?.uid].uid = null
        })
      }
    },
    async openBatchEditForm () {
      if (!this.studyActivitySelection.length) {
        bus.$emit('notification', { type: 'warning', msg: this.$t('DetailedFlowchart.batch_edit_no_selection') })
        return
      }
      const message = this.$t('DetailedFlowchart.batch_edit_warning')
      const options = { type: 'warning' }
      if (!await this.$refs.confirm.open(message, options)) {
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
      for (const cell of this.studyActivitySelection) {
        data.push({
          method: 'PATCH',
          content: {
            study_activity_uid: cell.refs?.[0]?.uid,
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
        this.loadSoaContent(true)
      })
    },
    toggleSubgroupActivitiesSelection (subgroupRow, value) {
      const activityCells = this.getStudyActivitiesForSubgroup(subgroupRow.cells[0].refs?.[0]?.uid)
      if (value) {
        this.studyActivitySelection = this.studyActivitySelection.concat(activityCells)
      } else {
        for (const activityCell of activityCells) {
          const index = this.studyActivitySelection.findIndex(cell => cell.refs?.[0]?.uid === activityCell.refs?.[0]?.uid)
          this.studyActivitySelection.splice(index, 1)
        }
      }
    },
    async redirectTo (value) {
      this.showEditForm = false
      if (['activities', 'footnotes', 'instructions'].indexOf(value) > -1) {
        this.$router.push({ name: 'StudyActivities', params: { tab: value } })
      } else if (['epochs', 'visits'].indexOf(value) > -1) {
        this.$router.push({ name: 'StudyStructure', params: { tab: value } })
      }
    },
    async loadSoaContent (keepDisplayState) {
      const resp = await study.getStudyProtocolFlowchart(this.selectedStudy.uid, this.selectedStudyVersion)
      let currentSoaGroup
      let currentGroup
      let currentSubGroup

      this.soaContent = resp.data

      this.soaContent.rows.forEach(row => row.cells.forEach(cell => { if (!cell.refs) { cell.refs = [] } }))

      if (!keepDisplayState) {
        this.rowsDisplayState = {}
        this.expandAllRows = false
      }
      for (const [index, row] of this.soaRows.entries()) {
        const key = `row-${index}`
        if (row.cells && row.cells.length) {
          if (row.cells[0].style === 'soaGroup') {
            this.$set(this.rowsDisplayState, key, { value: false })
            currentGroup = null
            currentSubGroup = null
            currentSoaGroup = index
          } else if (row.cells[0].style === 'group') {
            if (!keepDisplayState) {
              this.$set(this.rowsDisplayState, key, { value: false, parent: currentSoaGroup })
            }
            currentSubGroup = null
            currentGroup = index
          } else if (row.cells[0].style === 'subGroup') {
            if (!keepDisplayState) {
              this.$set(this.rowsDisplayState, key, { value: false, parent: currentGroup })
            }
            currentSubGroup = index
          } else if (row.cells[0].style === 'activity') {
            const scheduleCells = row.cells.slice(1)
            if (!keepDisplayState) {
              this.$set(this.rowsDisplayState, key, { value: false, parent: currentSubGroup })
            }
            this.$set(this.currentSelectionMatrix, row.cells[0].refs?.[0]?.uid, {})
            for (const [visitIndex, cell] of this.soaVisitRow.entries()) {
              let props = { value: false, uid: null }
              if ((scheduleCells[visitIndex].refs.length)) {
                if (cell.refs.length === 1) {
                  props = { value: true, uid: scheduleCells[visitIndex].refs?.[0]?.uid }
                } else if (scheduleCells[visitIndex].refs) {
                  props = { value: true, uid: scheduleCells[visitIndex].refs.map(ref => ref.uid) }
                }
              }
              this.$set(this.currentSelectionMatrix[row.cells[0].refs?.[0]?.uid], cell.refs?.[0]?.uid, props)
            }
          }
        }
      }
    },
    onResize () {
      this.tableHeight = window.innerHeight - this.$refs.tableContainer.getBoundingClientRect().y - 60
    },
    groupSelectedVisits () {
      const visitUids = this.selectedVisitIndexes.map(cell => this.soaVisitRow[cell].refs?.[0]?.uid)
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
      this.loadSoaContent(true)
      this.selectedVisitIndexes = []
    },
    async deleteVisitGroup (groupName) {
      const message = this.$t('DetailedFlowchart.confirm_group_deletion', { group: groupName })
      const options = { type: 'warning' }
      if (!await this.$refs.confirm.open(message, options)) {
        return
      }
      await studyEpochs.deleteCollapsibleVisitGroup(this.selectedStudy.uid, groupName)
      this.loadSoaContent(true)
    },
    async getHistoryData (options) {
      const params = {
        total_count: true
      }
      if (options) {
        params.page_number = options.page ? options.page : 1
        params.page_size = options.itemsPerPage ? options.itemsPerPage : 10
      }
      const resp = await study.getStudySoAHistory(this.selectedStudy.uid, params)
      this.historyItems = resp.data.items
      this.historyItemsTotal = resp.data.total
    },
    async openHistory () {
      await this.getHistoryData()
      this.showHistory = true
    },
    closeHistory () {
      this.showHistory = false
    },
    downloadCSV () {
      study.exportStudyDetailedSoa(this.selectedStudy.uid, this.selectedStudyVersion).then(response => {
        const filename = this.selectedStudy.current_metadata.identification_metadata.study_id + ' detailed SoA.csv'
        exportLoader.downloadFile(response.data, response.headers['content-type'], filename)
      })
    },
    downloadDOCX () {
      study.getStudyProtocolFlowchartDocx(this.selectedStudy.uid, this.selectedStudyVersion, true).then(response => {
        const filename = this.selectedStudy.current_metadata.identification_metadata.study_id + ' detailed SoA.docx'
        exportLoader.downloadFile(response.data, response.headers['content-type'], filename)
      })
    },
    multipleConsecutiveVisitsSelected () {
      // Check if more than one visit is selected,
      // and that they are in consecutive order without gaps.
      if (this.selectedVisitIndexes.length > 1) {
        const minIndex = this.selectedVisitIndexes.reduce((a, b) => Math.min(a, b))
        const maxIndex = this.selectedVisitIndexes.reduce((a, b) => Math.max(a, b))
        return (this.selectedVisitIndexes.length - 1) === (maxIndex - minIndex)
      }
      return false
    }
  },
  mounted () {
    this.loadSoaContent()
    this.onResize()
    this.fetchFootnotes()
    if (this.$route.params.footnote && !_isEmpty(this.$route.params.footnote)) {
      this.enableFootnoteMode(this.$route.params.footnote)
    }
  },
  watch: {
    update () {
      this.loadSoaContent()
    },
    '$route.params.footnote' (value) {
      if (value && !_isEmpty(value)) {
        this.enableFootnoteMode(value)
      }
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
  background-color: var(--v-tableGray-base);
  font-weight: 600;
}
tr {
  padding: 4px;
  &.section {
    background-color: var(--v-tableGray-base);
    font-weight: 600;
  }
}
tbody tr {
  border-bottom: 1px solid var(--v-greyBackground-base);
}
th {
  vertical-align: bottom;
  background-color: var(--v-tableGray-base);
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
  writing-mode: sideways-lr;
  text-orientation: mixed;
}
.text-strong {
  font-weight: 600;
}
.center {
  left: auto !important;
  right: 25%;
  top: 80px !important;
  position: fixed;
}
.visitFootnote {
  margin-bottom: 8px;
}

</style>
