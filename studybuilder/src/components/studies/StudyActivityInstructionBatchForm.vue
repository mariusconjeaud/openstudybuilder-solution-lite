<template>
<div>
  <horizontal-stepper-form
    ref="stepper"
    :title="$t('StudyActivityInstructionBatchForm.add_title')"
    :steps="steps"
    @close="close"
    @save="submit"
    :form-observer-getter="getObserver"
    :help-text="$t('_help.StudyActivityInstructionBatchForm.general')"
    @stepLoaded="onStepLoaded"
    :extra-step-validation="extraStepValidation"
    >
    <template v-slot:step.creationMode>
      <v-radio-group
        data-cy="objective-method-radio"
        v-model="creationMode"
        >
        <v-radio :label="$t('StudyActivityInstructionBatchForm.select_mode')" value="select" />
        <v-radio :label="$t('StudyActivityInstructionBatchForm.template_mode')" value="template" />
        <v-radio :label="$t('StudyActivityInstructionBatchForm.scratch_mode')" value="scratch" />
      </v-radio-group>
    </template>
    <template v-slot:step.creationMode.after>
      <study-activity-selection-table
        class="ma-4"
        :selection="studyActivities"
        :title="$t('StudyActivityInstructionBatchForm.batch_table_title')"
        />
    </template>
    <template v-slot:step.selectStudies="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-select
            :data-cy="$t('StudySelectionTable.select_studies')"
            v-model="selectedStudies"
            :label="$t('StudySelectionTable.select_studies')"
            :items="studies"
            :error-messages="errors"
            item-text="current_metadata.identification_metadata.study_id"
            clearable
            multiple
            class="pt-10"
            return-object
            />
        </validation-provider>
      </validation-observer>
    </template>
    <template v-slot:step.selectFromStudies>
      <p class="grey--text text-subtitle-1 font-weight-bold">{{ $t('StudyActivityInstructionBatchForm.selected_items') }}</p>
      <v-data-table
        data-cy="selected-instructions-table"
        :headers="selectedInstructionsHeaders"
        :items="selectedInstructions"
        >
        <template v-slot:item.activity_instruction_name="{ item }">
          <n-n-parameter-highlighter
            :name="item.activity_instruction_name"
            :show-prefix-and-postfix="false"
            />
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            color="red"
            @click="unselectStudyActivityInstruction(item)"
            >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </template>
    <template v-slot:step.selectFromStudies.after>
      <p class="grey--text text-subtitle-1 font-weight-bold mb-0 ml-3">{{ $t('StudyObjectiveForm.copy_instructions') }}</p>
      <v-col cols="12" flat class="pt-0 mt-0">
        <study-selection-table
          :headers="activityInstructionHeaders"
          data-fetcher-name="getAllStudyActivityInstructions"
          :extra-data-fetcher-filters="extraStudyActivityInstructionFilters"
          @item-selected="selectStudyActivityInstruction"
          :studies="selectedStudies"
          >
          <template v-slot:item.activity_instruction_name="{ item }">
            <n-n-parameter-highlighter
              :name="item.activity_instruction_name"
              :show-prefix-and-postfix="false"
              />
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn
              :data-cy="$t('StudySelectionTable.copy_item')"
              icon
              :color="getCopyButtonColor(item)"
              :disabled="isStudyActivityInstructionSelected(item)"
              @click="selectStudyActivityInstruction(item)"
              :title="$t('StudySelectionTable.copy_item')">
              <v-icon>mdi-content-copy</v-icon>
            </v-btn>
          </template>
        </study-selection-table>
      </v-col>
    </template>

    <template v-slot:step.selectTemplate>
      <p class="grey--text text-subtitle-1 font-weight-bold">{{ $t('StudyActivityInstructionBatchForm.select_template_title') }}</p>
        <v-card flat class="parameterBackground">
          <v-card-text>
            <n-n-parameter-highlighter :name="selectedTemplateName" default-color="orange"/>
          </v-card-text>
        </v-card>
    </template>
    <template v-slot:step.selectTemplate.after>
      <p class="grey--text text-subtitle-1 font-weight-bold mb-0 ml-3">{{ $t('StudyActivityInstructionBatchForm.copy_instructions') }}</p>
      <v-col cols="12" class="pt-0">
        <n-n-table
          ref="templateTable"
          key="templatesTable"
          :headers="tplHeaders"
          :items="templates"
          hide-default-switches
          hide-actions-menu
          :items-per-page="15"
          elevation="0"
          :options.sync="templatesOptions"
          :server-items-length="templatesTotal"
          show-filter-bar-by-default
          has-api
          column-data-resource="activity-instruction-templates"
          :initial-column-data="prefilteredTplHeaders"
          @filter="getTemplates"
          >
          <template v-slot:item.indications.name="{ item }">
            <template v-if="item.indications">
              {{ item.indications|names }}
            </template>
            <template v-else>
              {{ $t('_global.not_applicable_long') }}
            </template>
          </template>
          <template v-slot:item.activity_groups.name="{ item }">
            <template v-if="item.activity_groups.length">
              {{ item.activity_groups[0].name }}
            </template>
          </template>
          <template v-slot:item.activity_subgroups.name="{ item }">
            <template v-if="item.activity_subgroups.length">
              {{ item.activity_subgroups[0].name }}
            </template>
          </template>
          <template v-slot:item.activities.name="{ item }">
            <template v-if="item.activities && item.activities.length">
              {{ item.activities[0].name }}
            </template>
            <template v-else>
              {{ $t('_global.not_applicable_long') }}
            </template>
          </template>
          <template v-slot:item.name="{ item }">
            <n-n-parameter-highlighter :name="item.name" default-color="orange" />
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn
              :data-cy="$t('StudyActivityInstructionBatchForm.copy_template')"
              icon
              color="primary"
              @click="selectTemplate(item)"
              :title="$t('StudyActivityInstructionBatchForm.copy_template')">
              <v-icon>mdi-content-copy</v-icon>
            </v-btn>
          </template>
        </n-n-table>
      </v-col>
    </template>
    <template v-slot:step.createTemplate="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <n-n-template-input-field
            :data-cy="$t('StudyActivityInstructionBatchForm.name')"
            v-model="templateForm.name"
            :label="$t('StudyActivityInstructionBatchForm.name')"
            :items="parameterTypes"
            :error-messages="errors"
            show-drop-down-early
            />
          <div class="dialog-sub-title">{{ $t('_global.indexing') }}</div>
          <activity-template-indexing-form
            :form="templateForm"
            />
        </validation-provider>
      </validation-observer>
    </template>
    <template v-slot:step.createInstructionText="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <v-progress-circular
          v-if="loadingParameters"
          indeterminate
          color="secondary"
          />

        <template v-if="form.activity_instruction_template !== undefined">
          <parameter-value-selector
            ref="paramSelector"
            :value="parameters"
            :template="form.activity_instruction_template.name"
            color="white"
            />
        </template>
      </validation-observer>
    </template>
  </horizontal-stepper-form>
</div>
</template>

<script>
import activityInstructionTemplates from '@/api/activityInstructionTemplates'
import ActivityTemplateIndexingForm from '@/components/library/ActivityTemplateIndexingForm'
import { bus } from '@/main'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import instances from '@/utils/instances'
import libraryConstants from '@/constants/libraries'
import { mapGetters } from 'vuex'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import NNTable from '@/components/tools/NNTable'
import NNTemplateInputField from '@/components/tools/NNTemplateInputField'
import ParameterValueSelector from '@/components/tools/ParameterValueSelector'
import filteringParameters from '@/utils/filteringParameters'
import statuses from '@/constants/statuses'
import study from '@/api/study'
import StudyActivitySelectionTable from './StudyActivitySelectionTable'
import StudySelectionTable from './StudySelectionTable'
import templateParameterTypes from '@/api/templateParameterTypes'

export default {
  components: {
    ActivityTemplateIndexingForm,
    HorizontalStepperForm,
    NNParameterHighlighter,
    NNTable,
    NNTemplateInputField,
    ParameterValueSelector,
    StudyActivitySelectionTable,
    StudySelectionTable
  },
  props: {
    studyActivities: Array,
    currentStudyActivityInstructions: Array
  },
  created () {
    this.steps = this.selectFromStudiesSteps
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    selectedTemplateName () {
      return (this.form.activity_instruction_template) ? this.form.activity_instruction_template.name : ''
    },
    selectedActivityGroups () {
      const result = []
      if (!this.noTemplateAvailableAtAll) {
        for (const studyActivity of this.studyActivities) {
          result.push(studyActivity.activity.activity_group)
        }
      }
      return result
    },
    selectedActivitySubGroups () {
      const result = []
      if (!this.noTemplateAvailableAtAll) {
        for (const studyActivity of this.studyActivities) {
          result.push(studyActivity.activity.activity_subgroup)
        }
      }
      return result
    },
    prefilteredTplHeaders () {
      return {
        'activity_groups.name': this.selectedActivityGroups.map(item => item.name),
        'activity_subgroups.name': this.selectedActivitySubGroups.map(item => item.name)
      }
    }
  },
  data () {
    return {
      activityInstructionHeaders: [
        { text: this.$t('Study.study_id'), value: 'study_uid' },
        { text: this.$t('StudyActivityInstructionBatchForm.instruction_text'), value: 'activity_instruction_name' },
        { text: this.$t('_global.actions'), value: 'actions', width: '5%' }
      ],
      creationMode: 'select',
      extraStudyActivityInstructionFilters: {

      },
      form: {},
      loadingParameters: false,
      noTemplateAvailableAtAll: false,
      parameters: [],
      parameterTypes: [],
      selectedInstructions: [],
      selectedInstructionsHeaders: [
        { text: this.$t('Study.study_id'), value: 'study_uid' },
        { text: this.$t('StudyActivityInstructionBatchForm.instruction_text'), value: 'activity_instruction_name' },
        { text: this.$t('_global.actions'), value: 'actions', width: '5%' }
      ],
      selectedStudies: [],
      selectFromStudiesSteps: [
        { name: 'creationMode', title: this.$t('StudyActivityInstructionBatchForm.creation_mode_title') },
        { name: 'selectStudies', title: this.$t('StudyActivityInstructionBatchForm.select_studies') },
        { name: 'selectFromStudies', title: this.$t('StudyActivityInstructionBatchForm.select_from_studies_title') }
      ],
      createFromTemplateSteps: [
        { name: 'creationMode', title: this.$t('StudyActivityInstructionBatchForm.creation_mode_title') },
        { name: 'selectTemplate', title: this.$t('StudyActivityInstructionBatchForm.select_tpl_title') },
        { name: 'createInstructionText', title: this.$t('StudyActivityInstructionBatchForm.create_text_title') }
      ],
      scratchModeSteps: [
        { name: 'creationMode', title: this.$t('StudyActivityInstructionBatchForm.creation_mode_title') },
        { name: 'createTemplate', title: this.$t('StudyActivityInstructionBatchForm.create_template_title') },
        { name: 'createInstructionText', title: this.$t('StudyActivityInstructionBatchForm.create_text_title') }
      ],
      steps: [],
      studies: [],
      templateForm: {},
      templatesFetched: false,
      templates: [],
      templatesTotal: 0,
      templatesFilters: {},
      templatesOptions: {},
      tplHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.indications'), value: 'indications.name' },
        { text: this.$t('StudyActivity.activity_group'), value: 'activity_groups.name' },
        { text: this.$t('StudyActivity.activity_sub_group'), value: 'activity_subgroups.name' },
        { text: this.$t('StudyActivity.activity'), value: 'activities.name' },
        { text: this.$t('_global.template'), value: 'name', filteringName: 'name_plain', width: '30%' }
      ]
    }
  },
  methods: {
    close () {
      this.creationMode = 'select'
      this.$refs.stepper.reset()
      this.$emit('close')
      this.templateForm = {}
      this.form = {}
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    async loadParameters (template) {
      if (template) {
        this.loadingParameters = true
        const resp = await activityInstructionTemplates.getObjectTemplateParameters(template.uid)
        this.parameters = resp.data
        /* Filter received parameters based on current study activity selection */
        for (const parameterValues of this.parameters) {
          if (parameterValues.name === 'ActivityGroup') {
            const activityGroupUids = this.selectedActivityGroups.map(item => item.uid)
            parameterValues.values = parameterValues.values.filter(item => activityGroupUids.indexOf(item.uid) !== -1)
          } else if (parameterValues.name === 'ActivitySubGroup') {
            const activitySubGroupUids = this.selectedActivitySubGroups.map(item => item.uid)
            parameterValues.values = parameterValues.values.filter(item => activitySubGroupUids.indexOf(item.uid) !== -1)
          }
        }
        this.loadingParameters = false
      } else {
        this.parameters = []
      }
    },
    getTemplates (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.templatesOptions, filters, sort, filtersUpdated)
      params.status = statuses.FINAL
      const newFilters = (filters) ? JSON.parse(filters) : {}
      newFilters['activity_groups.uid'] = { v: this.selectedActivityGroups.map(item => item.uid) }
      newFilters['activity_subgroups.uid'] = { v: this.selectedActivitySubGroups.map(item => item.uid) }
      params.filters = JSON.stringify(newFilters)
      params.operator = 'or'
      return activityInstructionTemplates.get(params).then(resp => {
        // Apply filtering on library here because we cannot mix operators in API queries...
        this.templates = resp.data.items.filter(item => item.library.name === libraryConstants.LIBRARY_SPONSOR)
        this.templatesTotal = resp.data.total
        if (!this.templatesFetched) {
          // It was the first time we fetched templates, if there is
          // no result we empty pre-defined filters to avoid confusion
          if (this.templates.length === 0) {
            this.noTemplateAvailableAtAll = true
          }
          this.templatesFetched = true
        }
      })
    },
    async selectTemplate (template) {
      await this.loadParameters(template)
      this.$set(this.form, 'activity_instruction_template', {})
      this.$set(this.form, 'activity_instruction_template', template)
    },
    selectStudyActivityInstruction (studyActivityInstruction) {
      this.selectedInstructions.push(studyActivityInstruction)
    },
    unselectStudyActivityInstruction (studyActivityInstruction) {
      this.selectedInstructions = this.selectedInstructions.filter(item => item.activy_instruction_name !== studyActivityInstruction.activy_instruction_name)
    },
    isStudyActivityInstructionSelected (studyActivityInstruction) {
      let selected = this.selectedInstructions.find(item => item.activity_instruction_uid === studyActivityInstruction.activity_instruction_uid)
      if (!selected && this.currentStudyActivityInstructions.length) {
        selected = this.currentStudyActivityInstructions.find(item => item.activy_instruction_uid === studyActivityInstruction.activy_instruction_uid)
      }
      return selected !== undefined
    },
    getCopyButtonColor (item) {
      return (!this.isStudyActivityInstructionSelected(item) ? 'primary' : '')
    },
    async extraStepValidation (step) {
      if (this.creationMode !== 'scratch' || step !== 2) {
        return true
      }
      if (this.form.activity_instruction_template && this.form.activity_instruction_template.name === this.templateForm.name) {
        return true
      }
      const data = { ...this.templateForm, study_uid: this.selectedStudy.uid }
      data.library_name = libraryConstants.LIBRARY_USER_DEFINED
      if (data.indications) {
        data.indication_uids = data.indications.map(indication => indication.term_uid)
        delete data.indications
      }
      if (data.activity_group) {
        data.activity_group_uids = [data.activity_group]
        delete data.activity_group
      }
      if (data.activity_subgroups) {
        data.activity_subgroup_uids = data.activity_subgroups
        delete data.activity_subgroups
      }
      if (data.activities) {
        data.activity_uids = data.activities.map(activity => activity.uid)
        delete data.activities
      }
      try {
        const resp = await activityInstructionTemplates.create(data)
        await activityInstructionTemplates.approve(resp.data.uid)
        this.$set(this.form, 'activity_instruction_template', resp.data)
      } catch (error) {
        return false
      }
      this.loadParameters(this.form.activity_instruction_template)
      return true
    },
    async submit () {
      const operations = []
      if (this.creationMode === 'template' || this.creationMode === 'scratch') {
        for (const studyActivity of this.studyActivities) {
          operations.push({
            method: 'POST',
            content: {
              activity_instruction_data: {
                activity_instruction_template_uid: this.form.activity_instruction_template.uid,
                parameter_terms: await instances.formatParameterValues(this.parameters),
                library_name: this.form.activity_instruction_template.library.name
              },
              study_activity_uid: studyActivity.study_activity_uid
            }
          })
        }
      } else if (this.creationMode === 'select') {
        for (const studyActivity of this.studyActivities) {
          for (const studyActivityInstruction of this.selectedInstructions) {
            operations.push({
              method: 'POST',
              content: {
                activity_instruction_uid: studyActivityInstruction.activity_instruction_uid,
                study_activity_uid: studyActivity.study_activity_uid
              }
            })
          }
        }
      }
      if (operations.length === 0) {
        return
      }
      await study.studyActivityInstructionBatchOperations(this.selectedStudy.uid, operations)
      this.$emit('added')
      bus.$emit('notification', { msg: this.$t('StudyActivityInstructionBatchForm.add_success') })
      this.close()
    },
    onStepLoaded (step) {
      if (this.creationMode === 'template' && step === 2) {
        this.$refs.templateTable.loading = false
      }
    }
  },
  mounted () {
    this.getTemplates()
    study.get({ has_study_activity_instruction: true, page_size: 0 }).then(resp => {
      this.studies = resp.data.items.filter(study => study.uid !== this.selectedStudy.uid)
    })
    templateParameterTypes.getTypes().then(resp => {
      this.parameterTypes = resp.data
    })
  },
  watch: {
    creationMode (value) {
      if (value === 'template') {
        this.steps = this.createFromTemplateSteps
      } else if (value === 'select') {
        this.steps = this.selectFromStudiesSteps
      } else {
        this.steps = this.scratchModeSteps
      }
    }
  }
}
</script>
