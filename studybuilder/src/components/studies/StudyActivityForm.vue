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
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </template>
    <template v-slot:step.selectFromStudies.after>
      <div class="mt-4 mx-4 text-subtitle-1 grey--text font-italic">
        {{ $t('StudyActivityForm.copy_activity_instructions') }}
      </div>
      <v-col cols="12">
        <study-selection-table
          ref="selectionTable"
          key="selectFromStudiesTable"
          :headers="studyActivityHeaders"
          data-fetcher-name="getAllStudyActivities"
          :extra-data-fetcher-filters="extraDataFetcherFilters"
          :studies="selectedStudies"
          :column-data-resource="`studies/${selectedStudy.uid}/study-activities`"
          show-filter-bar-by-default
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
        </study-selection-table>
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
            <v-icon>mdi-delete</v-icon>
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
          column-data-resource="concepts/activities/activities"
          :filters-modify-function="modifyFilters"
          >
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              :color="getCopyButtonColor(item)"
              :disabled="isActivitySelected(item)"
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
        </n-n-table>
      </v-col>
    </template>
    <template v-slot:step.createPlaceholder>
      <v-row>
        <v-col cols="5">
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-autocomplete
              :label="$t('ActivityForms.activity_group')"
              data-cy="activity-group"
              :items="groups"
              v-model="form.activity_group"
              item-text="name"
              item-value="uid"
              dense
              clearable
              return-object
              :error-messages="errors"
              />
          </validation-provider>
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-autocomplete
              :label="$t('ActivityForms.activity_subgroup')"
              data-cy="activity-subgroup"
              :items="filteredSubGroups"
              v-model="form.activity_subgroup"
              item-text="name"
              item-value="uid"
              dense
              clearable
              :disabled="form.activity_group ? false : true"
              :error-messages="errors"
              />
          </validation-provider>
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-text-field
              :label="$t('ActivityForms.name')"
              data-cy="instance-name"
              v-model="form.name"
              dense
              clearable
              @input="getActivities"
              :error-messages="errors"
              />
          </validation-provider>
          <v-text-field
            :label="$t('ActivityFormsRequested.abbreviation')"
            data-cy="activity-abbreviation"
            v-model="form.abbreviation"
            dense
            clearable
            />
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-textarea
              :label="$t('ActivityFormsRequested.definition')"
              data-cy="activity-definition"
              v-model="form.definition"
              dense
              clearable
              auto-grow
              rows="1"
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
                :disabled="isActivitySelected(item)"
                data-cy="copy-activity"
                @click="selectActivityFromPlaceholder(item)"
                :title="$t('StudyActivityForm.copy_activity')">
                <v-icon>mdi-content-copy</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
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
import StudySelectionTable from '@/components/studies/StudySelectionTable'
import _isEmpty from 'lodash/isEmpty'
import _isEqual from 'lodash/isEqual'
import libConstants from '@/constants/libraries'

export default {
  components: {
    ConfirmDialog,
    HorizontalStepperForm,
    NNTable,
    StudySelectionTable
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      studyActivities: 'studyActivities/studyActivities'
    }),
    filteredSubGroups () {
      if (!this.form.activity_group) {
        return []
      }
      return this.subGroups.filter(el => el.activity_group.uid === this.form.activity_group.uid)
    }
  },
  data () {
    return {
      creationMode: 'selectFromLibrary',
      activities: [],
      extraDataFetcherFilters: {
        'activity.status': { v: [statuses.FINAL] }
      },
      options: {},
      activitiesTotal: 0,
      activityHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('StudyActivity.activity_group'), value: 'activity_group.name' },
        { text: this.$t('StudyActivity.activity_sub_group'), value: 'activity_subgroup.name' },
        { text: this.$t('StudyActivity.activity'), value: 'name' }
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
        { text: this.$t('StudyActivityForm.flowchart_group'), value: 'flowchart_group.sponsor_preferred_name' },
        { text: this.$t('StudyActivity.activity_group'), value: 'activity.activity_group.name' },
        { text: this.$t('StudyActivity.activity_sub_group'), value: 'activity.activity_subgroup.name' },
        { text: this.$t('StudyActivity.activity'), value: 'name' }
      ],
      selectedActivities: [],
      studyActivityHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('StudyActivityForm.study_id'), value: 'study_id' },
        { text: this.$t('_global.library'), value: 'activity.library_name' },
        { text: this.$t('StudyActivityForm.flowchart_group'), value: 'flowchart_group.sponsor_preferred_name' },
        { text: this.$t('StudyActivity.activity_group'), value: 'activity.activity_group.name' },
        { text: this.$t('StudyActivity.activity_sub_group'), value: 'activity.activity_subgroup.name' },
        { text: this.$t('StudyActivity.activity'), value: 'activity.name' }
      ],
      filters: '',
      form: {
        name: ''
      },
      groups: [],
      subgroups: []
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
        name: ''
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
          this.activities = resp.data.items
          this.total = resp.data.total
        })
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
        if (filtersObj.activity_group) {
          params.activity_group_names = []
          filtersObj.activity_group.v.forEach(value => {
            params.activity_group_names.push(value)
          })
          delete filtersObj.activity_group
        }
        if (filtersObj.activity_subgroup) {
          params.activity_subgroup_names = []
          filtersObj.activity_subgroup.v.forEach(value => {
            params.activity_subgroup_names.push(value)
          })
          delete filtersObj.activity_subgroup
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
        this.activities = resp.data.items
        this.activitiesTotal = resp.data.total
      })
    },
    modifyFilters (jsonFilter, params) {
      if (jsonFilter.activity_group) {
        params.activity_group_names = []
        jsonFilter.activity_group.v.forEach(value => {
          params.activity_group_names.push(value)
        })
        delete jsonFilter.activity_group
      }
      if (jsonFilter.activity_subgroup) {
        params.activity_subgroup_names = []
        jsonFilter.activity_subgroup.v.forEach(value => {
          params.activity_subgroup_names.push(value)
        })
        delete jsonFilter.activity_subgroup
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
      this.selectedActivities = this.selectedActivities.filter(item => item.uid !== activity.uid)
    },
    getCopyButtonColor (activity) {
      const selected = this.selectedActivities.find(item => item.uid === activity.uid)
      return (!selected) ? 'primary' : ''
    },
    isActivitySelected (activity) {
      if (this.studyActivities) {
        let selected = this.selectedActivities.find(item => item.uid === activity.uid)
        if (!selected && this.studyActivities.length) {
          selected = this.studyActivities.find(item => item.activity.uid === activity.uid)
        }
        return !this.currentFlowchartGroup || selected !== undefined
      }
      return false
    },
    isStudyActivitySelected (studyActivity) {
      let selected = this.selectedActivities.find(item => item.activity.uid === studyActivity.activity.uid)
      if (!selected && this.studyActivities.length) {
        selected = this.studyActivities.find(item => item.activity.uid === studyActivity.activity.uid)
      }
      return selected !== undefined
    },
    async submit () {
      if (this.creationMode !== 'selectFromLibrary' && this.creationMode !== 'selectFromStudies') {
        this.form.library_name = libConstants.LIBRARY_REQUESTED
        this.form.name_sentence_case = this.form.name.charAt(0).toUpperCase() + this.form.name.slice(1)
        await activities.create(this.form, 'activities').then(resp => {
          this.selectActivity(resp.data)
        })
      }
      if (!this.selectedActivities.length) {
        return
      }
      for (let cpt = 0; cpt < this.selectedActivities.length; cpt++) {
        const item = this.selectedActivities[cpt]
        let payload
        if (this.creationMode === 'selectFromLibrary' || this.creationMode === 'createPlaceholder') {
          payload = {
            flowchart_group_uid: item.flowchart_group.term_uid,
            activity_uid: item.uid
          }
        } else {
          payload = {
            flowchart_group_uid: item.flowchart_group.term_uid,
            activity_uid: item.activity.uid
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
    study.get({ hasStudyActivity: true }).then(resp => {
      this.studies = resp.data.items.filter(study => study.uid !== this.selectedStudy.uid)
    })
    this.getGroups()
  },
  watch: {
    studyEndpoint (val) {
      if (val) {
        this.initFromStudyEndpoint(val)
      } else {
        this.form = this.getInitialForm()
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
