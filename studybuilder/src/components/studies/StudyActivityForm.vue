<template>
<div>
  <horizontal-stepper-form
    ref="stepper"
    :title="$t('StudyActivityForm.add_title')"
    :steps="steps"
    @close="cancel"
    @save="submit"
    :form-observer-getter="getObserver"
    :help-text="$t('_help.StudyActivityTable.general')"
    :reset-loading="resetLoading"
    >
    <template v-slot:step.creationMode>
      <v-radio-group
        v-model="creationMode"
        >
        <v-radio :label="$t('StudyActivityForm.select_from_studies')" value="selectFromStudies" data-cy="select-from-studies" />
        <v-radio :label="$t('StudyActivityForm.select_from_library')" value="selectFromLibrary" data-cy="select-from-library"/>
        <v-radio :label="$t('StudyActivityForm.create_placeholder_for_activity')" value="createPlaceholder" data-cy="create-placeholder"/>
      </v-radio-group>
    </template>
    <template v-slot:step.selectStudies="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-select
            v-model="selectedStudies"
            :label="$t('StudySelectionTable.studies')"
            data-cy="select-study-for-activity"
            :items="studies"
            :error-messages="errors"
            item-text="current_metadata.identification_metadata.study_id"
            clearable
            multiple
            return-object
            />
        </validation-provider>
      </validation-observer>
    </template>
    <template v-slot:step.selectFlowchartGroup="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col cols="4">
              <v-autocomplete
                v-model="currentFlowchartGroup"
                :label="$t('StudyActivityForm.flowchart_group')"
                data-cy="flowchart-group"
                :items="flowchartGroups"
                item-text="sponsor_preferred_name"
                return-object
                :error-messages="errors"
                :hint="$t('_help.StudyActivityForm.flowchart_group')"
                persistent-hint
                clearable
                />
            </v-col>
          </v-row>
        </validation-provider>
      </validation-observer>
    </template>
    <template v-slot:step.selectFromStudies>
      <v-data-table
        key="fromStudiesSelection"
        :headers="selectionFromStudiesHeaders"
        :items="selectedActivities"
        >
        <template v-slot:item.name="{ item }">
          {{ item.activity.name }}
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            color="red"
            @click="unselectActivity(item)"
            >
            <v-icon>mdi-delete-outline</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </template>
    <template v-slot:step.selectFromStudies.after>
      <div class="mt-4 mx-4 text-subtitle-1 grey--text font-italic">
        {{ $t('StudyActivityForm.copy_activity_instructions') }}
      </div>
      <v-col cols="12">
        <n-n-table
          key="selectionTable"
          :headers="studyActivityHeaders"
          :items="activities"
          hide-default-switches
          hide-actions-menu
          show-filter-bar-by-default
          :items-per-page="15"
          elevation="0"
          :options.sync="options"
          :server-items-length="activitiesTotal"
          has-api
          @filter="getActivities"
          :column-data-resource="`studies/${selectedStudy.uid}/study-activities`"
          :filters-modify-function="modifyFilters"
          >
          <template v-slot:header.actions>
            <div class="row">
              <v-btn
                icon
                color="primary"
                @click="selectAllStudyActivities()"
                :title="$t('StudyActivityForm.copy_all_activities')">
                <v-icon>mdi-content-copy</v-icon>
              </v-btn>
            </div>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              :color="getCopyButtonColor(item)"
              :disabled="isStudyActivitySelected(item)"
              data-cy="copy-activity"
              @click="selectStudyActivity(item)"
              :title="$t('StudyActivityForm.copy_activity')">
              <v-icon>mdi-content-copy</v-icon>
            </v-btn>
          </template>
          <template v-slot:item.activity.is_data_collected="{ item }">
            <div v-if="item.activity">
              {{ item.activity.is_data_collected|yesno }}
            </div>
          </template>
        </n-n-table>
      </v-col>
    </template>
    <template v-slot:step.selectFromLibrary>
      <v-data-table
        key="fromLibrarySelection"
        :headers="selectionFromLibraryHeaders"
        :items="selectedActivities"
        >
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            color="red"
            @click="unselectActivity(item)"
            >
            <v-icon>mdi-delete-outline</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </template>
    <template v-slot:step.selectFromLibrary.after>
      <div class="mt-4 mx-4 text-subtitle-1 grey--text font-italic">
        {{ $t('StudyActivityForm.copy_activity_instructions') }}
      </div>
      <v-col cols="12">
        <n-n-table
          key="activityTable"
          :headers="activityHeaders"
          :items="activities"
          hide-default-switches
          hide-actions-menu
          show-filter-bar-by-default
          :items-per-page="15"
          elevation="0"
          :options.sync="options"
          :server-items-length="activitiesTotal"
          has-api
          @filter="getActivities"
          :initial-filters="{ status: ['Final'] }"
          column-data-resource="concepts/activities/activities"
          :filters-modify-function="modifyFilters"
          >
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              :color="getCopyButtonColor(item)"
              :disabled="isActivitySelected(item) || isActivityNotFinal(item)"
              data-cy="copy-activity"
              @click="selectActivity(item)"
              :title="$t('StudyActivityForm.copy_activity')">
              <v-icon>mdi-content-copy</v-icon>
            </v-btn>
          </template>
          <template v-slot:header.actions>
            <div class="row">
              <v-btn
                icon
                color="primary"
                @click="selectAllActivities()"
                :title="$t('StudyActivityForm.copy_all_activities')">
                <v-icon>mdi-content-copy</v-icon>
              </v-btn>
            </div>
          </template>
          <template v-slot:item.is_data_collected="{ item }">
            {{ item.is_data_collected|yesno }}
          </template>
        </n-n-table>
      </v-col>
    </template>
    <template v-slot:step.createPlaceholder>
      <validation-observer ref="observer">
        <v-row>
          <v-col cols="5">
            <v-autocomplete
              :label="$t('ActivityForms.activity_group')"
              data-cy="activity-group"
              :items="groups"
              v-model="form.activity_groupings[0].activity_group_uid"
              item-text="name"
              item-value="uid"
              dense
              clearable
              />
            <v-autocomplete
              :label="$t('ActivityForms.activity_subgroup')"
              data-cy="activity-subgroup"
              :items="filteredSubGroups"
              v-model="form.activity_groupings[0].activity_subgroup_uid"
              item-text="name"
              item-value="uid"
              dense
              clearable
              :disabled="form.activity_groupings[0].activity_group_uid ? false : true"
              />
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-text-field
                :label="$t('ActivityFormsRequested.name')"
                data-cy="instance-name"
                v-model="form.name"
                dense
                clearable
                @input="getActivities"
                :error-messages="errors"
                />
            </validation-provider>
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-textarea
                :label="$t('ActivityFormsRequested.rationale_for_request')"
                data-cy="activity-rationale"
                v-model="form.request_rationale"
                dense
                clearable
                auto-grow
                rows="1"
                :error-messages="errors"
                />
            </validation-provider>
            <v-switch
              :label="$t('ActivityFormsRequested.data_collection')"
              v-model="form.is_data_collected"
              />
          </v-col>
          <v-col cols="7">
            <v-data-table
              :headers="activityHeaders"
              :items="activities"
              :options.sync="options"
              :server-items-length="activitiesTotal"
              @pagination="getActivities()"
              :items-per-page="5">
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  :color="getCopyButtonColor(item)"
                  :disabled="isActivitySelected(item) || isActivityNotFinal(item)"
                  data-cy="copy-activity"
                  @click="selectActivityFromPlaceholder(item)"
                  :title="$t('StudyActivityForm.copy_activity')">
                  <v-icon>mdi-content-copy</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-col>
        </v-row>
      </validation-observer>
    </template>
  </horizontal-stepper-form>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import { bus } from '@/main'
import activities from '@/api/activities'
import statuses from '@/constants/statuses'
import study from '@/api/study'
import terms from '@/api/controlledTerminology/terms'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import NNTable from '@/components/tools/NNTable'
import _isEmpty from 'lodash/isEmpty'
import _isEqual from 'lodash/isEqual'
import libConstants from '@/constants/libraries'

export default {
  components: {
    ConfirmDialog,
    HorizontalStepperForm,
    NNTable
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    filteredSubGroups () {
      if (!this.form.activity_groupings[0].activity_group_uid) {
        return []
      }
      return this.subGroups.filter(el => el.activity_groups.find(o => o.uid === this.form.activity_groupings[0].activity_group_uid) !== undefined)
    }
  },
  data () {
    return {
      creationMode: 'selectFromLibrary',
      activities: [],
      options: {},
      activitiesTotal: 0,
      activityHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('StudyActivity.activity_group'), value: 'activity_group.name', externalFilterSource: 'concepts/activities/activity-groups$name', exludeFromHeader: ['is_data_collected'] },
        { text: this.$t('StudyActivity.activity_sub_group'), value: 'activity_subgroup.name', externalFilterSource: 'concepts/activities/activity-sub-groups$name', exludeFromHeader: ['is_data_collected'] },
        { text: this.$t('StudyActivity.activity'), value: 'name' },
        { text: this.$t('StudyActivity.data_collection'), value: 'is_data_collected' },
        { text: this.$t('_global.status'), value: 'status' }
      ],
      currentFlowchartGroup: null,
      flowchartGroups: [],
      selectedStudies: [],
      steps: [],
      studies: [],
      selectFromStudiesSteps: [
        { name: 'creationMode', title: this.$t('StudyActivityForm.creation_mode_title') },
        { name: 'selectStudies', title: this.$t('StudyActivityForm.select_studies') },
        { name: 'selectFromStudies', title: this.$t('StudyActivityForm.select_from_studies_title') }
      ],
      selectFromLibrarySteps: [
        { name: 'creationMode', title: this.$t('StudyActivityForm.creation_mode_title') },
        { name: 'selectFlowchartGroup', title: this.$t('StudyActivityForm.flowchart_group_title') },
        { name: 'selectFromLibrary', title: this.$t('StudyActivityForm.select_from_library_title') }
      ],
      createPlaceholderSteps: [
        { name: 'creationMode', title: this.$t('StudyActivityForm.creation_mode_title') },
        { name: 'selectFlowchartGroup', title: this.$t('StudyActivityForm.flowchart_group_title') },
        { name: 'createPlaceholder', title: this.$t('StudyActivityForm.create_placeholder'), belowDisplay: true }
      ],
      selectionFromLibraryHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('StudyActivityForm.flowchart_group'), value: 'flowchart_group.sponsor_preferred_name' },
        { text: this.$t('StudyActivity.activity_group'), value: 'activity_group.name' },
        { text: this.$t('StudyActivity.activity_sub_group'), value: 'activity_subgroup.name' },
        { text: this.$t('StudyActivity.activity'), value: 'name' }
      ],
      selectionFromStudiesHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.library'), value: 'activity.library_name' },
        { text: this.$t('StudyActivityForm.flowchart_group'), value: 'study_soa_group.soa_group_name' },
        { text: this.$t('StudyActivity.activity_group'), value: 'study_activity_group.activity_group_name' },
        { text: this.$t('StudyActivity.activity_sub_group'), value: 'study_activity_subgroup.activity_subgroup_name' },
        { text: this.$t('StudyActivity.activity'), value: 'name' }
      ],
      selectedActivities: [],
      studyActivities: [],
      studyActivityHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('StudyActivityForm.study_id'), value: 'study_id', noFilter: true },
        { text: this.$t('_global.library'), value: 'activity.library_name' },
        { text: this.$t('StudyActivityForm.flowchart_group'), value: 'study_soa_group.soa_group_name' },
        { text: this.$t('StudyActivity.activity_group'), value: 'study_activity_group.activity_group_name', externalFilterSource: 'concepts/activities/activity-groups$name', disableColumnFilters: true },
        { text: this.$t('StudyActivity.activity_sub_group'), value: 'study_activity_subgroup.activity_subgroup_name', externalFilterSource: 'concepts/activities/activity-sub-groups$name', disableColumnFilters: true },
        { text: this.$t('StudyActivity.activity'), value: 'activity.name' },
        { text: this.$t('StudyActivity.data_collection'), value: 'activity.is_data_collected' }
      ],
      filters: '',
      form: {
        name: '',
        activity_groupings: [{}],
        is_data_collected: false
      },
      groups: [],
      subgroups: [],
      resetLoading: 0
    }
  },
  methods: {
    async cancel () {
      if (!_isEmpty(this.selectedActivities)) {
        const options = {
          type: 'warning',
          cancelLabel: this.$t('_global.cancel'),
          agreeLabel: this.$t('_global.continue')
        }
        if (await this.$refs.confirm.open(this.$t('_global.cancel_changes'), options)) {
          this.close()
        }
      } else {
        this.close()
      }
    },
    close () {
      this.$emit('close')
      this.selectedActivities = []
      this.currentFlowchartGroup = null
      this.creationMode = 'selectFromLibrary'
      this.steps = this.selectFromLibrarySteps
      this.selectedStudies = []
      this.form = {
        name: '',
        activity_groupings: [{}]
      }
      this.$refs.stepper.reset()
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    selectActivityFromPlaceholder (activity) {
      this.creationMode = 'selectFromLibrary'
      if (!this.currentFlowchartGroup) {
        return
      }
      const activityCopy = { ...activity }
      activityCopy.flowchart_group = { ...this.currentFlowchartGroup }
      this.selectedActivities.push(activityCopy)
    },
    getActivities (filters, sort) {
      if (this.creationMode === 'createPlaceholder') {
        const params = {
          page_number: (this.options.page),
          page_size: this.options.itemsPerPage,
          total_count: true,
          library: libConstants.LIBRARY_SPONSOR,
          filters: `{"*":{"v":["${this.form.name}"]}}`
        }
        activities.get(params, 'activities').then(resp => {
          const activities = []
          for (const item of resp.data.items) {
            if (item.activity_groupings.length > 0) {
              for (const grouping of item.activity_groupings) {
                activities.push({
                  activity_group: { name: grouping.activity_group_name, uid: grouping.activity_group_uid },
                  activity_subgroup: { name: grouping.activity_subgroup_name, uid: grouping.activity_subgroup_uid },
                  item_key: item.uid + grouping.activity_group_uid + grouping.activity_subgroup_uid,
                  ...item
                })
              }
            } else {
              activities.push({
                activity_group: { name: '', uid: '' },
                activity_subgroup: { name: '', uid: '' },
                item_key: item.uid,
                ...item
              })
            }
          }
          this.activities = activities
          this.total = resp.data.total
        })
        return
      } else if (this.creationMode === 'selectFromStudies') {
        const params = {
          page_number: (this.options.page),
          page_size: this.options.itemsPerPage,
          total_count: true
        }
        if (filters) {
          params.filters = JSON.parse(filters)
        } else {
          params.filters = {}
        }
        const studiesUids = []
        this.selectedStudies.forEach(el => {
          studiesUids.push(el.uid)
        })
        params.filters.study_uid = { v: studiesUids }
        study.getAllStudyActivities(params).then(
          resp => {
            const items = resp.data.items
            items.forEach(el => {
              el.study_id = this.studies[this.studies.findIndex((study) => study.uid === el.study_uid)].current_metadata.identification_metadata.study_id
            })
            const activities = []
            for (const item of items) {
              let grouping = null
              if (item.activity.activity_groupings.length > 0) {
                if (item.study_activity_group && item.study_activity_subgroup) {
                  grouping = item.activity.activity_groupings.find(
                    o => o.activity_group_uid === item.study_activity_group.activity_group_uid && o.activity_subgroup_uid === item.study_activity_subgroup.activity_subgroup_uid
                  )
                }
              }
              if (grouping) {
                activities.push({
                  ...item,
                  activity: {
                    activity_group: { name: grouping.activity_group_name, uid: grouping.activity_group_uid },
                    activity_subgroup: { name: grouping.activity_subgroup_name, uid: grouping.activity_subgroup_uid },
                    ...item.activity
                  },
                  item_key: item.activity.uid + grouping.activity_group_uid + grouping.activity_subgroup_uid
                })
              } else {
                activities.push({
                  ...item,
                  activity: {
                    ...item.activity,
                    activity_group: { name: '', uid: '' },
                    activity_subgroup: { name: '', uid: '' }
                  },
                  item_key: item.activity.uid
                })
              }
            }
            this.activities = activities
            this.activitiesTotal = resp.data.total
          }
        )
        return
      }
      if (filters !== undefined && !_isEqual(filters, this.filters)) {
        // New filters, also reset current page
        this.filters = filters
        this.options.page = 1
      }
      const params = {
        page_number: (this.options.page),
        page_size: this.options.itemsPerPage,
        total_count: true
      }
      if (this.filters && this.filters !== undefined) {
        const filtersObj = JSON.parse(this.filters)
        if (filtersObj['activity_group.name']) {
          params.activity_group_names = []
          filtersObj['activity_group.name'].v.forEach(value => {
            params.activity_group_names.push(value)
          })
          delete filtersObj['activity_group.name']
        }
        if (filtersObj['activity_subgroup.name']) {
          params.activity_subgroup_names = []
          filtersObj['activity_subgroup.name'].v.forEach(value => {
            params.activity_subgroup_names.push(value)
          })
          delete filtersObj['activity_subgroup.name']
        }
        if (filtersObj.name) {
          params.activity_names = []
          filtersObj.name.v.forEach(value => {
            params.activity_names.push(value)
          })
          delete filtersObj.name
        }
        if (Object.keys(filtersObj).length !== 0 && filtersObj.constructor === Object) {
          params.filters = JSON.stringify(filtersObj)
        }
      }
      if (this.options.sortBy && this.options.sortBy.length !== 0 && sort !== undefined) {
        params.sort_by = `{"${this.options.sortBy[0]}":${!sort}}`
      }
      activities.get(params, 'activities').then(resp => {
        const activities = []
        for (const item of resp.data.items) {
          if (item.activity_groupings.length > 0) {
            for (const grouping of item.activity_groupings) {
              activities.push({
                activity_group: { name: grouping.activity_group_name, uid: grouping.activity_group_uid },
                activity_subgroup: { name: grouping.activity_subgroup_name, uid: grouping.activity_subgroup_uid },
                item_key: item.uid + grouping.activity_group_uid + grouping.activity_subgroup_uid,
                ...item
              })
            }
          } else {
            activities.push({
              activity_group: { name: '', uid: '' },
              activity_subgroup: { name: '', uid: '' },
              item_key: item.uid,
              ...item
            })
          }
        }
        this.activities = activities
        this.activitiesTotal = resp.data.total
      })
    },
    modifyFilters (jsonFilter, params) {
      if (jsonFilter['activity_group.name']) {
        params.activity_group_names = []
        jsonFilter['activity_group.name'].v.forEach(value => {
          params.activity_group_names.push(value)
        })
        delete jsonFilter['activity_group.name']
      }
      if (jsonFilter['activity_subgroup.name']) {
        params.activity_subgroup_names = []
        jsonFilter['activity_subgroup.name'].v.forEach(value => {
          params.activity_subgroup_names.push(value)
        })
        delete jsonFilter['activity_subgroup.name']
      }
      if (jsonFilter.name) {
        params.activity_names = []
        jsonFilter.name.v.forEach(value => {
          params.activity_names.push(value)
        })
        delete jsonFilter.name
      }
      const filters = {
        jsonFilter: jsonFilter,
        params: params
      }
      return filters
    },
    selectActivity (activity) {
      if (!this.currentFlowchartGroup) {
        return
      }
      const activityCopy = { ...activity }
      activityCopy.flowchart_group = { ...this.currentFlowchartGroup }
      this.selectedActivities.push(activityCopy)
    },
    selectAllActivities () {
      if (!this.currentFlowchartGroup) {
        return
      }
      for (const activity of this.activities) {
        if (!this.selectedActivities.find(item => item.uid === activity.uid)) {
          const activityCopy = { ...activity }
          activityCopy.flowchart_group = { ...this.currentFlowchartGroup }
          this.selectedActivities.push(activityCopy)
        }
      }
    },
    selectStudyActivity (studyActivity) {
      const copy = { ...studyActivity }
      this.selectedActivities.push(copy)
    },
    selectAllStudyActivities () {
      for (const studyActivity of this.$refs.selectionTable.studySelectionItems) {
        if (!this.isStudyActivitySelected(studyActivity)) {
          const copy = { ...studyActivity }
          this.selectedActivities.push(copy)
        }
      }
    },
    unselectActivity (activity) {
      if (this.creationMode === 'selectFromLibrary') {
        this.selectedActivities = this.selectedActivities.filter(
          item => !(item.uid === activity.uid && item.activity_group.uid === activity.activity_group.uid && item.activity_subgroup.uid === activity.activity_subgroup.uid)
        )
      } else {
        this.selectedActivities = this.selectedActivities.filter(
          item => !(item.activity.uid === activity.activity.uid && item.study_activity_group.activity_group_uid === activity.study_activity_group.activity_group_uid && item.study_activity_subgroup.activity_subgroup_uid === activity.study_activity_subgroup.activity_subgroup_uid)
        )
      }
    },
    getCopyButtonColor (activity) {
      let selected = false
      if (this.creationMode === 'selectFromLibrary') {
        selected = this.selectedActivities.find(
          item => item.uid === activity.uid && item.activity_group.uid === activity.activity_group.uid && item.activity_subgroup.uid === activity.activity_subgroup.uid
        )
      } else {
        selected = this.selectedActivities.find(
          item => item.uid === activity.activity.uid && item.activity_group.uid === activity.activity_group.uid && item.activity_subgroup.uid === activity.activity_subgroup.uid
        )
      }
      return (!selected) ? 'primary' : ''
    },
    isActivitySelected (activity) {
      if (this.studyActivities) {
        let selected = this.selectedActivities.find(
          item => item.uid === activity.uid && item.activity_group.uid === activity.activity_group.uid && item.activity_subgroup.uid === activity.activity_subgroup.uid
        )
        if (!selected && this.studyActivities.length) {
          selected = this.studyActivities.find(
            item => item.activity.uid === activity.uid && item.study_activity_group.activity_group_uid === activity.activity_group.uid && item.study_activity_subgroup.activity_subgroup_uid === activity.activity_subgroup.uid
          )
        }
        return !this.currentFlowchartGroup || selected !== undefined
      }
      return false
    },
    isActivityNotFinal (activity) {
      return activity.status !== statuses.FINAL
    },
    isStudyActivitySelected (studyActivity) {
      let selected = this.selectedActivities.find(item => item.activity.uid === studyActivity.activity.uid)
      if (!selected && this.studyActivities.length) {
        selected = this.studyActivities.find(item => item.activity.uid === studyActivity.uid)
      }
      return selected !== undefined
    },
    async submit () {
      if (this.creationMode !== 'selectFromLibrary' && this.creationMode !== 'selectFromStudies') {
        this.form.library_name = libConstants.LIBRARY_REQUESTED
        this.form.name_sentence_case = this.form.name.toLowerCase()
        const isValid = await this.$refs.observer.validate()
        if (!isValid) {
          this.resetLoading += 1
          return
        }
        if (_isEmpty(this.form.activity_groupings[0])) {
          delete this.form.activity_groupings
        }
        const createdActivity = await activities.create(this.form, 'activities')
        await activities.approve(createdActivity.data.uid, 'activities').then(resp => {
          const activity = {
            ...resp.data,
            item_key: resp.data.uid
          }
          if (resp.data.activity_groupings.length > 0) {
            activity.activity_group = { uid: resp.data.activity_groupings[0].activity_group_uid }
            activity.activity_subgroup = { uid: resp.data.activity_groupings[0].activity_subgroup_uid }
            activity.item_key = resp.data.uid + resp.data.activity_groupings[0].activity_group_uid + resp.data.activity_groupings[0].activity_subgroup_uid
          }
          this.selectActivity(activity)
        })
      }
      if (!this.selectedActivities.length) {
        bus.$emit('notification', { type: 'info', msg: this.$t('StudyActivityForm.select_activities_info') })
        this.resetLoading += 1
        return
      }
      for (let cpt = 0; cpt < this.selectedActivities.length; cpt++) {
        const item = this.selectedActivities[cpt]
        let payload
        if (this.creationMode === 'selectFromLibrary' || this.creationMode === 'createPlaceholder') {
          payload = {
            soa_group_term_uid: item.flowchart_group.term_uid,
            activity_uid: item.uid
          }
          if (this.form.activity_groupings) {
            payload.activity_group_uid = item.activity_group.uid
            payload.activity_subgroup_uid = item.activity_subgroup.uid
          }
        } else {
          payload = {
            soa_group_term_uid: item.study_soa_group.soa_group_term_uid,
            activity_uid: item.activity.uid,
            activity_group_uid: item.study_activity_group.activity_group_uid,
            activity_subgroup_uid: item.study_activity_subgroup.activity_subgroup_uid
          }
        }
        await study.createStudyActivity(this.selectedStudy.uid, payload)
      }
      bus.$emit('notification', { type: 'success', msg: this.$t('StudyActivityForm.add_success') })
      this.$emit('added')
      this.close()
    },
    getGroups () {
      activities.get({ page_size: 0 }, 'activity-groups').then(resp => {
        this.groups = resp.data.items
      })
      activities.get({ page_size: 0 }, 'activity-sub-groups').then(resp => {
        this.subGroups = resp.data.items
      })
    }
  },
  created () {
    this.steps = this.selectFromLibrarySteps
  },
  mounted () {
    terms.getByCodelist('flowchartGroups').then(resp => {
      this.flowchartGroups = resp.data.items
    })
    study.get({ has_study_activity: true }).then(resp => {
      this.studies = resp.data.items.filter(study => study.uid !== this.selectedStudy.uid)
    })
    this.getGroups()
    study.getStudyActivities(this.selectedStudy.uid, { page_size: 0 }).then(resp => {
      this.studyActivities = resp.data.items
    })
  },
  watch: {
    selectedStudies (val) {
      if (val) {
        this.getActivities()
      }
    },
    creationMode (value) {
      if (value === 'selectFromStudies') {
        this.steps = this.selectFromStudiesSteps
      } else if (value === 'selectFromLibrary') {
        this.steps = this.selectFromLibrarySteps
      } else {
        this.steps = this.createPlaceholderSteps
        this.options.itemsPerPage = 5
      }
    },
    options () {
      this.getActivities()
    }
  }
}
</script>

<style scoped lang="scss">
.v-stepper {
  background-color: var(--v-dfltBackground-base) !important;
  box-shadow: none;
}

.step-title {
  color: var(--v-secondary-base) !important;
}
</style>
