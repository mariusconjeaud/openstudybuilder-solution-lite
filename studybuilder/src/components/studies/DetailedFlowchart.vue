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
      v-model="hideFlowchartGroups"
      :label="$t('DetailedFlowchart.hide_flowchart_groups')"
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
        v-show="selectedVisits.length > 1"
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
        <template v-if="groupedVisits.length">
          <th v-for="(sv, index) in groupedVisits" :key="`epoch-${index}`" class="text-vertical" scope="col">
            <v-badge
              color="secondary--text"
              :content="getEpochName(sv, index) !== '' ? getElementFootnotes(sv.study_epoch_uid) : ''"
              class="mt-3"
            >
              {{ getEpochName(sv, index) }}
            </v-badge>
            <v-btn
              v-if="footnoteMode && getEpochName(sv, index) !== '' && !checkIfElementHasFootnote(sv.study_epoch_uid)"
              x-small
              icon
              class="mx-0 px-0"
              color="primary"
              @click="addElementForFootnote(sv.study_epoch_uid, 'StudyEpoch')">
              <v-icon x-small>
                mdi-plus
              </v-icon>
            </v-btn>
            <v-btn
              v-else-if="footnoteMode && getEpochName(sv, index) !== '' && checkIfElementHasFootnote(sv.study_epoch_uid)"
              x-small
              icon
              class="mx-0 px-0"
              @click="removeElementForFootnote(sv.study_epoch_uid)"
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
        <template v-if="groupedVisits.length">
          <th v-for="(sv, index) in groupedVisits" :key="`shortName-${index}`" :style="`top: ${firstHeaderHeight}px`" scope="col">
            <div class="d-flex align-center">
              <v-badge
                color="secondary--text"
                :content="getElementFootnotes(sv.visitsUids ? sv.visitsUids : sv.uid)"
                class="visitFootnote"
              >
                {{ sv.visit_short_name }}
              </v-badge>
              <v-btn
                v-if="footnoteMode && !checkIfElementHasFootnote(sv.visitsUids ? sv.visitsUids : sv.uid)"
                x-small
                icon
                class="mx-0 px-0"
                @click="addElementForFootnote(sv.visitsUids ? sv.visitsUids : sv.uid, 'StudyVisit')">
                <v-icon x-small>
                  mdi-plus
                </v-icon>
              </v-btn>
              <v-btn
                v-else-if="footnoteMode && checkIfElementHasFootnote(sv.visitsUids ? sv.visitsUids : sv.uid)"
                x-small
                icon
                class="mx-0 px-0"
                @click="removeElementForFootnote(sv.visitsUids ? sv.visitsUids : sv.uid)"
                color="red">
                <v-icon x-small>
                  mdi-close
                </v-icon>
              </v-btn>
              <v-checkbox
                v-if="!sv.isGroup && !footnoteMode"
                v-model="selectedVisits"
                :value="sv"
                :value-comparator="compareVisits"
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
                @click="deleteVisitGroup(sv.uid)"
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
          <td class="text-strong">
            <v-badge
              color="secondary--text"
              :content="getElementFootnotes(Object.values(Object.values(sortedStudyActivities[flowchartGroup])[0])[0][0].study_soa_group.study_soa_group_uid)"
            >
              {{ flowchartGroup }}
            </v-badge>
            <v-btn
              v-if="footnoteMode && !checkIfElementHasFootnote(Object.values(Object.values(sortedStudyActivities[flowchartGroup])[0])[0][0].study_soa_group.study_soa_group_uid)"
              x-small
              icon
              class="mx-0 px-0"
              @click="addSoAGroupForFootnote(flowchartGroup)">
              <v-icon x-small>
                mdi-plus
              </v-icon>
            </v-btn>
            <v-btn
              v-else-if="footnoteMode && checkIfElementHasFootnote(Object.values(Object.values(sortedStudyActivities[flowchartGroup])[0])[0][0].study_soa_group.study_soa_group_uid)"
              x-small
              icon
              class="mx-0 px-0"
              @click="removeSoAGroupForFootnote(flowchartGroup)"
              color="red">
              <v-icon x-small>
                mdi-close
              </v-icon>
            </v-btn>
          </td>
          <td>
            <v-btn
              v-if="!readOnly"
              icon
              @click="() => toggleSoaGroupDisplay(flowchartGroup)"
              :title="$t('DetailedFlowchart.toggle_soa_group_display')"
              :disabled="footnoteMode"
              >
              <v-icon v-if="getFlGroupDisplayState(flowchartGroup)" color="success">mdi-eye-outline</v-icon>
              <v-icon v-else>mdi-eye-off-outline</v-icon>
            </v-btn>
          </td>
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
              <td class="text-strong">
                <v-badge
                  color="secondary--text"
                  :content="getElementFootnotes(Object.values(sortedStudyActivities[flowchartGroup][group])[0][0].study_activity_group.study_activity_group_uid)"
                >
                  {{ group }}
                </v-badge>
              <v-btn
                v-if="footnoteMode && !checkIfElementHasFootnote(Object.values(sortedStudyActivities[flowchartGroup][group])[0][0].study_activity_group.study_activity_group_uid)"
                x-small
                icon
                class="mx-0 px-0"
                @click="addGroupForFootnote(flowchartGroup, group)">
                <v-icon x-small>
                  mdi-plus
                </v-icon>
              </v-btn>
              <v-btn
                v-else-if="footnoteMode && checkIfElementHasFootnote(Object.values(sortedStudyActivities[flowchartGroup][group])[0][0].study_activity_group.study_activity_group_uid)"
                x-small
                icon
                class="mx-0 px-0"
                @click="removeGroupForFootnote(flowchartGroup, group)"
                color="red">
                <v-icon x-small>
                  mdi-close
                </v-icon>
              </v-btn>
              </td>
              <td>
                <v-btn
                  v-if="!readOnly"
                  icon
                  @click="value => toggleActivityGroupFlowchartDisplay(flowchartGroup, group)"
                  :title="$t('DetailedFlowchart.toggle_group_display')"
                  :disabled="footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
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
                        v-if="!readOnly && !footnoteMode"
                        :key="`cb-subgroup-${flowchartGroup}-${group}-${subgroup}-${update}`"
                        @change="value => toggleSubgroupActivitiesSelection(flowchartGroup, group, subgroup, value)"
                        on-icon="mdi-checkbox-multiple-marked-outline"
                        off-icon="mdi-checkbox-multiple-blank-outline"
                        hide-details
                        :disabled="!checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
                        />
                      <v-badge
                        color="secondary--text"
                        :content="getElementFootnotes(sortedStudyActivities[flowchartGroup][group][subgroup][0].study_activity_subgroup.study_activity_subgroup_uid)"
                      >
                        {{ subgroup }}
                      </v-badge>
                      <v-btn
                        v-if="footnoteMode && !checkIfElementHasFootnote(sortedStudyActivities[flowchartGroup][group][subgroup][0].study_activity_subgroup.study_activity_subgroup_uid)"
                        x-small
                        icon
                        class="mx-0 px-0"
                        @click="addSubgroupForFootnote(flowchartGroup, group, subgroup)">
                        <v-icon x-small>
                          mdi-plus
                        </v-icon>
                      </v-btn>
                      <v-btn
                        v-else-if="footnoteMode && checkIfElementHasFootnote(sortedStudyActivities[flowchartGroup][group][subgroup][0].study_activity_subgroup.study_activity_subgroup_uid)"
                        x-small
                        icon
                        class="mx-0 px-0"
                        @click="removeSubgroupForFootnote(flowchartGroup, group, subgroup)"
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
                      @click="value => toggleActivitySubgroupFlowchartDisplay(flowchartGroup, group, subgroup)"
                      :title="$t('DetailedFlowchart.toggle_subgroup_display')"
                      :disabled="footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
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
                          v-if="!readOnly && !footnoteMode"
                          hide-details
                          @change="value => toggleActivitySelection(studyActivity, value)"
                          :value="studyActivitySelection.findIndex(item => item.study_activity_uid === studyActivity.study_activity_uid) !== -1"
                          :disabled="!checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
                          />
                        <v-badge
                          color="secondary--text"
                          :content="getElementFootnotes(studyActivity.study_activity_uid)"
                        >
                          {{ studyActivity.activity.name }}
                        </v-badge>
                        <v-btn
                          v-if="footnoteMode && !checkIfElementHasFootnote(studyActivity.study_activity_uid)"
                          x-small
                          icon
                          class="mx-0 px-0"
                          @click="addElementForFootnote(studyActivity.study_activity_uid, 'StudyActivity')">
                          <v-icon x-small>
                            mdi-plus
                          </v-icon>
                        </v-btn>
                        <v-btn
                          v-else-if="footnoteMode && checkIfElementHasFootnote(studyActivity.study_activity_uid)"
                          x-small
                          icon
                          class="mx-0 px-0"
                          @click="removeElementForFootnote(studyActivity.study_activity_uid)"
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
                        @click="toggleActivityFlowchartDisplay(studyActivity, !studyActivity.show_activity_in_protocol_flowchart)"
                        :title="$t('DetailedFlowchart.toggle_activity_display')"
                        :disabled="footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
                        >
                        <v-icon v-if="studyActivity.show_activity_in_protocol_flowchart" color="success">mdi-eye-outline</v-icon>
                        <v-icon v-else>mdi-eye-off-outline</v-icon>
                      </v-btn>
                    </td>
                    <td v-for="visit in groupedVisits" :key="`${studyActivity.study_activity_uid}-${visit.uid}`">
                      <v-row>
                        <v-badge
                          color="secondary--text"
                          :content="getElementFootnotes(currentSelectionMatrix[studyActivity.study_activity_uid][visit.uid] ? currentSelectionMatrix[studyActivity.study_activity_uid][visit.uid].uid : '')"
                          overlap
                        >
                          <v-checkbox
                            v-if="!readOnly && currentSelectionMatrix[studyActivity.study_activity_uid][visit.uid]"
                            v-model="currentSelectionMatrix[studyActivity.study_activity_uid][visit.uid].value"
                            color="success"
                            @change="value => updateSchedule(value, studyActivity.study_activity_uid, visit)"
                            :disabled="isCheckboxDisabled(studyActivity.study_activity_uid, visit.uid) || footnoteMode || !checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
                            hide-details
                            on-icon="mdi-checkbox-marked-circle-outline"
                            off-icon="mdi-checkbox-blank-circle-outline"
                            class="mx-0 px-0"
                            />
                          </v-badge>
                        <v-btn
                          v-if="footnoteMode && currentSelectionMatrix[studyActivity.study_activity_uid][visit.uid].uid && !checkIfElementHasFootnote(currentSelectionMatrix[studyActivity.study_activity_uid][visit.uid].uid)"
                          x-small
                          icon
                          class="mx-0 px-0"
                          @click="addScheduleForFootnote(studyActivity.study_activity_uid, visit)">
                          <v-icon x-small>
                            mdi-plus
                          </v-icon>
                        </v-btn>
                        <v-btn
                          v-if="footnoteMode && currentSelectionMatrix[studyActivity.study_activity_uid][visit.uid].uid && checkIfElementHasFootnote(currentSelectionMatrix[studyActivity.study_activity_uid][visit.uid].uid)"
                          x-small
                          icon
                          class="mx-0 px-0"
                          @click="removeElementForFootnote(currentSelectionMatrix[studyActivity.study_activity_uid][visit.uid].uid)"
                          color="red">
                          <v-icon x-small>
                            mdi-close
                          </v-icon>
                        </v-btn>
                      </v-row>
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
    :selection="studyActivitySelection"
    :current-selection-matrix="currentSelectionMatrix"
    @updated="getStudyActivitySchedules"
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
      sortedStudyActivities: 'studyActivities/sortedStudyActivities',
      selectedStudy: 'studiesGeneral/selectedStudy',
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion',
      studyPreferredTimeUnit: 'studiesGeneral/studyPreferredTimeUnit',
      studyFootnotes: 'studyFootnotes/studyFootnotes'
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
          isGroup: true,
          visitsUids: [firstVisit.uid, previousVisit.uid],
          study_epoch_uid: firstVisit.study_epoch_uid
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
      footnoteUpdateLoading: false,
      soaGroupsUpdate: false
    }
  },
  methods: {
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
    addSubgroupForFootnote (flgroup, group, subgroup) {
      this.sortedStudyActivities[flgroup][group][subgroup].forEach(activity => {
        this.elementsForFootnote.referenced_items.push({ item_uid: activity.study_activity_subgroup.study_activity_subgroup_uid, item_type: 'StudyActivitySubGroup' })
      })
    },
    addGroupForFootnote (flgroup, group) {
      for (const key in this.sortedStudyActivities[flgroup][group]) {
        this.sortedStudyActivities[flgroup][group][key].forEach(activity => {
          this.elementsForFootnote.referenced_items.push({ item_uid: activity.study_activity_group.study_activity_group_uid, item_type: 'StudyActivityGroup' })
        })
      }
    },
    addSoAGroupForFootnote (flgroup) {
      for (const group in this.sortedStudyActivities[flgroup]) {
        for (const key in this.sortedStudyActivities[flgroup][group]) {
          this.sortedStudyActivities[flgroup][group][key].forEach(activity => {
            this.elementsForFootnote.referenced_items.push({ item_uid: activity.study_soa_group.study_soa_group_uid, item_type: 'StudySoAGroup' })
          })
        }
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
    removeSubgroupForFootnote (flgroup, group, subgroup) {
      this.sortedStudyActivities[flgroup][group][subgroup].forEach(activity => {
        this.removeFootnote(activity.study_activity_subgroup.study_activity_subgroup_uid)
      })
    },
    removeGroupForFootnote (flgroup, group) {
      for (const key in this.sortedStudyActivities[flgroup][group]) {
        this.sortedStudyActivities[flgroup][group][key].forEach(activity => {
          this.removeFootnote(activity.study_activity_group.study_activity_group_uid)
        })
      }
    },
    removeSoAGroupForFootnote (flgroup) {
      for (const group in this.sortedStudyActivities[flgroup]) {
        for (const key in this.sortedStudyActivities[flgroup][group]) {
          this.sortedStudyActivities[flgroup][group][key].forEach(activity => {
            this.removeFootnote(activity.study_soa_group.study_soa_group_uid)
          })
        }
      }
    },
    addScheduleForFootnote (studyActivityUid, studyVisit) {
      const scheduleUid = this.currentSelectionMatrix[studyActivityUid][studyVisit.uid].uid
      if (typeof scheduleUid !== 'string') {
        scheduleUid.forEach(uid => {
          this.elementsForFootnote.referenced_items.push({ item_uid: uid, item_type: 'StudyActivitySchedule' })
        })
      } else {
        this.elementsForFootnote.referenced_items.push({ item_uid: scheduleUid, item_type: 'StudyActivitySchedule' })
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
    getFlGroupDisplayState (flgroup) {
      for (const group of Object.keys(this.sortedStudyActivities[flgroup])) {
        for (const items of Object.values(this.sortedStudyActivities[flgroup][group])) {
          for (const item of items) {
            if (item.show_soa_group_in_protocol_flowchart) {
              return true
            }
          }
        }
      }
      return false
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
        const fgroup = studyActivity.study_soa_group.soa_group_name
        const group = (studyActivity.study_activity_group)
          ? studyActivity.study_activity_group.activity_group_name : '(not selected)'
        const subgroup = (studyActivity.study_activity_subgroup)
          ? studyActivity.study_activity_subgroup.activity_subgroup_name : '(not selected)'
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
      const params = {
        study_value_version: this.selectedStudyVersion
      }
      study.getStudyActivitySchedules(this.selectedStudy.uid, params).then(resp => {
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
    async redirectTo (value) {
      this.showEditForm = false
      if (['activities', 'footnotes', 'instructions'].indexOf(value) > -1) {
        this.$router.push({ name: 'StudyActivities', params: { tab: value } })
      } else if (['epochs', 'visits'].indexOf(value) > -1) {
        this.$router.push({ name: 'StudyStructure', params: { tab: value } })
      }
    },
    async loadActivities () {
      this.studyActivitySelection = []
      const resp = await this.$store.dispatch('studyActivities/fetchStudyActivities', { studyUid: this.selectedStudy.uid, study_value_version: this.selectedStudyVersion })
      this.studyActivities = resp.data.items
      for (const studyActivity of this.studyActivities) {
        this.$set(this.currentSelectionMatrix, studyActivity.study_activity_uid, {})
      }
      studyEpochs.getStudyVisits(this.selectedStudy.uid, { page_size: 0, study_value_version: this.selectedStudyVersion }).then(resp => {
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
    },
    toggleSoaGroupDisplay (soaGroupName) {
      const payload = []
      for (const group in this.sortedStudyActivities[soaGroupName]) {
        for (const subGroup in this.sortedStudyActivities[soaGroupName][group]) {
          for (const studyActivity of this.sortedStudyActivities[soaGroupName][group][subGroup]) {
            payload.push({
              method: 'PATCH',
              content: {
                study_activity_uid: studyActivity.study_activity_uid,
                content: {
                  show_soa_group_in_protocol_flowchart: !studyActivity.show_soa_group_in_protocol_flowchart
                }
              }
            })
          }
        }
      }
      study.studyActivityBatchOperations(this.selectedStudy.uid, payload).then(() => {
        this.loadActivities()
      })
    }
  },
  mounted () {
    terms.getByCodelist('epochs').then(resp => {
      this.epochs = resp.data.items
    })
    this.loadActivities()
    this.onResize()
    this.fetchFootnotes()
    if (this.redirectFootnote && !_isEmpty(this.redirectFootnote)) {
      this.enableFootnoteMode(this.redirectFootnote)
    }
  },
  watch: {
    update () {
      this.loadActivities()
    },
    redirectFootnote (value) {
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
