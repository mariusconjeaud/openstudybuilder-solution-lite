<template>
<div>
  <horizontal-stepper-form
    ref="stepper"
    :title="title"
    :steps="steps"
    @close="close"
    @save="submit"
    :form-observer-getter="getObserver"
    :editable="studyObjective !== undefined && studyObjective !== null"
    :extra-step-validation="createTemplate"
    :helpItems="helpItems"
    :editData="form"
    >
    <template v-if="!studyObjective" v-slot:step.creationMode>
      <v-radio-group
        v-model="creationMode"
        >
        <v-radio data-cy="objective-from-select" :label="$t('StudyObjectiveForm.select_mode')" value="select" />
        <v-radio data-cy="objective-from-template" :label="$t('StudyObjectiveForm.template_mode')" value="template" />
        <v-radio data-cy="objective-from-scratch" :label="$t('StudyObjectiveForm.scratch_mode')" value="scratch" />
      </v-radio-group>
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
            :label="$t('StudySelectionTable.studies')"
            :items="studies"
            :error-messages="errors"
            item-text="study_id"
            clearable
            multiple
            return-object
            />
        </validation-provider>
      </validation-observer>
    </template>
    <template v-slot:step.selectObjective>
      <p class="grey--text text-subtitle-1 font-weight-bold">{{ $t('StudyObjectiveForm.selected_objectives') }}</p>
      <v-data-table
        data-cy="selected-objectives-table"
        :headers="selectedObjectiveHeaders"
        :items="selectedStudyObjectives"
        >
        <template v-slot:item.objective.name="{ item }">
          <n-n-parameter-highlighter :name="item.objective.name" />
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            color="red"
            @click="unselectStudyObjective(item)"
            >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </template>
    <template v-slot:step.selectObjective.after>
      <p class="grey--text text-subtitle-1 font-weight-bold mb-0 ml-3">{{ $t('StudyObjectiveForm.copy_instructions') }}</p>
      <v-col cols="12" flat class="pt-0 mt-0">
        <study-selection-table
          :headers="objectiveHeaders"
          data-fetcher-name="getAllStudyObjectives"
          :extra-data-fetcher-filters="extraStudyObjectiveFilters"
          @item-selected="selectStudyObjective"
          :studies="selectedStudies"
          >
          <template v-slot:item.objective.name="{ item }">
            <n-n-parameter-highlighter :name="item.objective.name" />
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn
              :data-cy="$t('StudySelectionTable.copy_item')"
              icon
              :color="getCopyButtonColor(item)"
              :disabled="isStudyObjectiveSelected(item)"
              @click="selectStudyObjective(item)"
              :title="$t('StudySelectionTable.copy_item')">
              <v-icon>mdi-content-copy</v-icon>
            </v-btn>
          </template>
        </study-selection-table>
      </v-col>
    </template>
    <template v-slot:step.selectTemplate>
      <v-card flat class="parameterBackground">
        <v-card-text>
          <n-n-parameter-highlighter
            :name="selectedTemplateName"
            default-color="orange"
            :default-parameter-values="selectedDefaultParameterValues"
            />
        </v-card-text>
      </v-card>
    </template>
    <template v-slot:step.selectTemplate.after>
      <p class="grey--text text-subtitle-1 font-weight-bold mb-0 ml-3 mt-2">{{ $t('StudyObjectiveForm.copy_instructions') }}</p>
      <v-col cols="12" class="pt-0">
        <n-n-table
          key="templatesTable"
          :headers="tplHeaders"
          :items="expandedTemplates"
          hide-default-switches
          hide-actions-menu
          show-filter-bar-by-default
          :items-per-page="15"
          elevation="0"
          :options.sync="options"
          :server-items-length="total"
          has-api
          :column-data-resource="`objective-templates`"
          @filter="getObjectiveTemplates"
          >
          <template v-slot:item.categories="{ item }">
            <template v-if="item.defaultParameterValuesSet === undefined">
              <template v-if="item.categories">
                {{ item.categories|terms }}
              </template>
              <template v-else>
                {{ $t('_global.not_applicable_long') }}
              </template>
            </template>
          </template>
          <template v-slot:item.confirmatoryTesting="{ item }">
            <template v-if="item.defaultParameterValuesSet === undefined">
              <template v-if="item.confirmatoryTesting !== null">
                {{ item.confirmatoryTesting|yesno }}
              </template>
              <template v-else>
                {{ $t('_global.not_applicable_long') }}
              </template>
            </template>
          </template>
          <template v-slot:item.indications="{ item }">
            <template v-if="item.defaultParameterValuesSet === undefined">
              <template v-if="item.indications">
                {{ item.indications|names }}
              </template>
              <template v-else>
                {{ $t('_global.not_applicable_long') }}
              </template>
            </template>
          </template>
          <template v-slot:item.name="{ item }">
            <n-n-parameter-highlighter
              v-if="item.defaultParameterValuesSet === undefined"
              :name="item.name"
              default-color="orange"
              />
            <n-n-parameter-highlighter
              v-else
              :name="item.name"
              default-color="orange"
              :default-parameter-values="item.defaultParameterValues"
              />
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn
              :data-cy="$t('StudyObjectiveForm.copy_template')"
              icon
              color="primary"
              @click="selectObjectiveTemplate(item)"
              :title="$t('StudyObjectiveForm.copy_template')">
              <v-icon>mdi-content-copy</v-icon>
            </v-btn>
          </template>
        </n-n-table>
      </v-col>
    </template>
    <template v-slot:step.editObjective="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <v-progress-circular
          v-if="loadingParameters"
          indeterminate
          color="secondary"
          />

        <parameter-value-selector
          ref="paramSelector"
          v-model="parameters"
          :template="studyObjective ? studyObjective.objective.objective_template.name : form.objective_template.name"
          :preview-text="$t('ParameterValueSelector.preview')"
          color="white"
          />
      </validation-observer>
    </template>
    <template v-slot:step.createTemplate="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <n-n-template-input-field
            :data-cy="$t('ObjectiveTemplateForm.name')"
            v-model="templateForm.name"
            :label="$t('ObjectiveTemplateForm.name')"
            :items="parameterTypes"
            :error-messages="errors"
            :show-drop-down-early="true"
            />
        </validation-provider>
      </validation-observer>
    </template>
    <template v-slot:step.createObjective="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <v-progress-circular
          v-if="loadingParameters"
          indeterminate
          color="secondary"
          />

        <template v-if="form.objective_template !== undefined">
          <parameter-value-selector
            ref="paramSelector"
            :value="parameters"
            :template="form.objective_template.name"
            color="white"
            preview-text=" "
            />
        </template>
      </validation-observer>
    </template>

    <template v-slot:step.objectiveLevel>
      <v-row>
        <v-col cols="11">
          <v-select
            :data-cy="$t('StudyObjectiveForm.objective_level')"
            v-model="form.objective_level"
            :label="$t('StudyObjectiveForm.objective_level')"
            :items="objectiveLevels"
            item-text="sponsor_preferred_name"
            return-object
            dense
            clearable
            style="max-width: 400px"
            />
        </v-col>
      </v-row>
    </template>
  </horizontal-stepper-form>
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import _isEqual from 'lodash/isEqual'
import { bus } from '@/main'
import { objectManagerMixin } from '@/mixins/objectManager'
import instances from '@/utils/instances'
import statuses from '@/constants/statuses'
import objectives from '@/api/objectives'
import objectiveTemplates from '@/api/objectiveTemplates'
import templateParameterTypes from '@/api/templateParameterTypes'
import defaultParameterValues from '@/utils/defaultParameterValues'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import NNTable from '@/components/tools/NNTable'
import NNTemplateInputField from '@/components/tools/NNTemplateInputField'
import ParameterValueSelector from '@/components/tools/ParameterValueSelector'
import study from '@/api/study'
import StudySelectionTable from './StudySelectionTable'
import filteringParameters from '@/utils/filteringParameters'
import constants from '@/constants/libraries'

export default {
  mixins: [objectManagerMixin],
  components: {
    HorizontalStepperForm,
    NNParameterHighlighter,
    NNTable,
    NNTemplateInputField,
    ParameterValueSelector,
    StudySelectionTable
  },
  props: {
    studyObjective: {
      type: Object,
      required: false
    },
    currentStudyObjectives: Array,
    cloneMode: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    ...mapGetters({
      objectiveLevels: 'studiesGeneral/objectiveLevels',
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    title () {
      if (this.studyObjective) {
        return this.$t('StudyObjectiveForm.edit_title')
      }
      return this.$t('StudyObjectiveForm.add_title')
    },
    selectedTemplateName () {
      return (this.form.objective_template) ? this.form.objective_template.name : ''
    },
    selectedDefaultParameterValues () {
      if (this.form.objective_template) {
        if (Array.isArray(this.form.objective_template.default_parameter_values)) {
          return this.form.objective_template.default_parameter_values
        }
      }
      return []
    },
    expandedTemplates () {
      const result = []
      for (const template of this.templates) {
        result.push(template)
        if (defaultParameterValues.hasDefaultParameterValues(template)) {
          for (const setNumber in template.defaultParameterValues) {
            const fakeTemplate = {
              uid: template.uid,
              name: template.name,
              defaultParameterValuesSet: setNumber,
              library: template.library
            }
            fakeTemplate.defaultParameterValues = template.defaultParameterValues[setNumber]
            result.push(fakeTemplate)
          }
        }
      }
      return result
    }
  },
  data () {
    return {
      helpItems: [
        'StudyObjectiveForm.add_title',
        'StudyObjectiveForm.select_mode',
        'StudyObjectiveForm.template_mode',
        'StudyObjectiveForm.scratch_mode',
        'StudyObjectiveForm.select_objective_tpl',
        'StudyObjectiveForm.select_tpl_parameters_label',
        'StudyObjectiveForm.select_studies',
        'StudyObjectiveForm.study_objective',
        'StudyObjectiveForm.objective_level',
        'StudyObjectiveForm.step_edit_title'
      ],
      creationMode: 'select',
      extraStudyObjectiveFilters: {
        'objective.library.name': { v: [constants.LIBRARY_SPONSOR] }
      },
      form: {},
      templateForm: {},
      loadingParameters: false,
      parameters: [],
      apiEndpoint: objectives,
      apiTemplateEndpoint: objectiveTemplates,
      parameterTypes: [],
      alternateSteps: [
        { name: 'creationMode', title: this.$t('StudyObjectiveForm.creation_mode_label') },
        { name: 'selectTemplate', title: this.$t('StudyObjectiveForm.select_tpl_title') },
        { name: 'createObjective', title: this.$t('StudyObjectiveForm.step2_title') },
        { name: 'objectiveLevel', title: this.$t('StudyObjectiveForm.step3_title') }
      ],
      editModeSteps: [
        { name: 'editObjective', title: this.$t('StudyObjectiveForm.step_edit_title') },
        { name: 'objectiveLevel', title: this.$t('StudyObjectiveForm.step3_title') }
      ],
      scratchModeSteps: [
        { name: 'creationMode', title: this.$t('StudyObjectiveForm.creation_mode_label') },
        { name: 'createTemplate', title: this.$t('StudyObjectiveForm.create_template_title') },
        { name: 'createObjective', title: this.$t('StudyObjectiveForm.step2_title') },
        { name: 'objectiveLevel', title: this.$t('StudyObjectiveForm.step3_title') }
      ],
      cloneModeSteps: [
        { name: 'createTemplate', title: this.$t('StudyObjectiveForm.edit_template_title') },
        { name: 'createObjective', title: this.$t('StudyObjectiveForm.step2_title') }
      ],
      selectedStudies: [],
      selectedStudyObjectives: [],
      steps: this.getInitialSteps(),
      studies: [],
      templates: [],
      tplHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.indications'), value: 'indications', filteringName: 'indications.name' },
        { text: this.$t('ObjectiveTemplateTable.objective_cat'), value: 'categories' },
        { text: this.$t('ObjectiveTemplateTable.confirmatory_testing'), value: 'confirmatory_testing' },
        { text: this.$t('_global.template'), value: 'name', width: '30%' }
      ],
      objectiveHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('Study.study_id'), value: 'study_uid' },
        { text: this.$t('StudyObjectiveForm.study_objective'), value: 'objective.name' },
        { text: this.$t('StudyObjectiveForm.objective_level'), value: 'objective_level.sponsor_preferred_name' }
      ],
      selectedObjectiveHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('Study.study_id'), value: 'study_id' },
        { text: this.$t('StudyObjectiveForm.study_objective'), value: 'objective.name' },
        { text: this.$t('StudyObjectiveForm.objective_level'), value: 'objective_level.sponsor_preferred_name' }
      ],
      options: {},
      total: 0
    }
  },
  methods: {
    close () {
      this.creationMode = 'select'
      this.form = {}
      this.templateForm = {}
      this.parameters = []
      this.$refs.stepper.reset()
      this.selectedStudyObjectives = []
      this.selectedStudies = []
      this.$emit('close')
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    getInitialSteps () {
      return [
        { name: 'creationMode', title: this.$t('StudyObjectiveForm.creation_mode_label') },
        { name: 'selectStudies', title: this.$t('StudyObjectiveForm.select_studies') },
        { name: 'selectObjective', title: this.$t('StudyObjectiveForm.select_objective') }
      ]
    },
    getObjectiveTemplates (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      params.status = statuses.FINAL
      if (params.filters) {
        params.filters = JSON.parse(params.filters)
      } else {
        params.filters = {}
      }
      Object.assign(params.filters, { 'library.name': { v: [constants.LIBRARY_SPONSOR] } })
      objectiveTemplates.get(params).then(resp => {
        this.templates = resp.data.items
        this.total = resp.data.total
        if (this.studyObjective) {
          this.initFromStudyObjective(this.studyObjective)
        }
      })
    },
    async loadParameters (template) {
      if (template) {
        if (this.cloneMode) {
          const parameters = this.$refs.paramSelector.getTemplateParametersFromTemplate(template.name_plain)
          if (parameters.length === this.parameters.length) {
            let differ = false
            for (let index = 0; index < parameters.length; index++) {
              if (parameters[index] !== this.parameters[index].name) {
                differ = true
                break
              }
            }
            if (!differ) {
              return
            }
          }
        }
        this.loadingParameters = true
        const resp = await objectiveTemplates.getParameters(template.uid, { study_uid: this.selectedStudy.uid })
        this.parameters = resp.data
        if (template.default_parameter_values.length) {
          instances.loadParameterValues(template.default_parameter_values, this.parameters, true)
        }
        this.loadingParameters = false
      } else {
        this.parameters = []
      }
    },
    initFromStudyObjective (studyObjective) {
      this.form = JSON.parse(JSON.stringify(studyObjective))
      this.showParametersFromObject(studyObjective.objective)
      if (!this.cloneMode) {
        this.creationMode = 'template'
        this.steps = this.editModeSteps
        if (this.templates.length !== 0) {
          this.$set(this.form, 'objective_template', this.templates.find(
            item => item.uid === this.form.objective.objective_template.uid))
        }
        this.originalForm = { ...this.form }
      } else {
        this.creationMode = 'clone'
        this.steps = this.cloneModeSteps
        this.templateForm = { ...studyObjective.objective.objective_template }
        this.$set(this.form, 'objective_template', studyObjective.objective.objective_template)
      }
    },
    async selectObjectiveTemplate (template) {
      await this.loadParameters(template)
      this.$set(this.form, 'objective_template', {})
      this.$set(this.form, 'objective_template', template)
    },
    selectStudyObjective (studyObjective) {
      this.selectedStudyObjectives.push(studyObjective)
      this.$set(this.form, 'objective_level', studyObjective.objective_level)
    },
    unselectStudyObjective (studyObjective) {
      this.selectedStudyObjectives = this.selectedStudyObjectives.filter(item => item.objective.name !== studyObjective.objective.name)
    },
    isStudyObjectiveSelected (studyObjective) {
      let selected = this.selectedStudyObjectives.find(item => item.objective.uid === studyObjective.objective.uid)
      if (!selected && this.currentStudyObjectives.length) {
        selected = this.currentStudyObjectives.find(item => item.objective.uid === studyObjective.objective.uid)
      }
      return selected !== undefined
    },
    getCopyButtonColor (item) {
      return (!this.isStudyObjectiveSelected(item) ? 'primary' : '')
    },
    async createTemplate (step) {
      if ((this.creationMode !== 'scratch' || step !== 2) && (this.creationMode !== 'clone' || step !== 1)) {
        return true
      }
      if (this.form.objective_template && this.form.objective_template.name === this.templateForm.name) {
        return true
      }
      const data = { ...this.templateForm, studyUid: this.selectedStudy.uid }
      data.library_name = constants.LIBRARY_USER_DEFINED
      try {
        const resp = await objectiveTemplates.create(data)
        await objectiveTemplates.approve(resp.data.uid)
        this.$set(this.form, 'objective_template', resp.data)
      } catch (error) {
        return false
      }
      this.loadParameters(this.form.objective_template)
      return true
    },
    async getStudyObjectiveNamePreview () {
      const objectiveData = {
        objective_template_uid: this.form.objective.objective_template.uid,
        parameter_values: await instances.formatParameterValues(this.parameters),
        library_name: this.form.objective_template ? this.form.objective_template.library.name : this.form.objective.library.name
      }
      const resp = await study.getStudyObjectivePreview(this.selectedStudy.uid, { objective_data: objectiveData })
      return resp.data.objective.name
    },
    async submit () {
      let action = null
      let notification = null
      let args = null

      if (this.studyObjective) {
        if (!this.cloneMode) {
          args = {
            studyUid: this.selectedStudy.uid,
            studyObjectiveUid: this.studyObjective.study_objective_uid,
            form: JSON.parse(JSON.stringify(this.form))
          }
          const namePreview = await this.getStudyObjectiveNamePreview()
          if (namePreview !== this.studyObjective.objective.name) {
            args.form.parameters = this.parameters
          }
          action = 'studyObjectives/updateStudyObjective'
          notification = 'objective_updated'
        } else {
          this.$store.dispatch('studyObjectives/addStudyObjectiveFromTemplate', {
            studyUid: this.selectedStudy.uid,
            form: JSON.parse(JSON.stringify(this.form)),
            parameters: this.parameters
          })
          action = 'studyObjectives/deleteStudyObjective'
          args = {
            studyUid: this.selectedStudy.uid,
            studyObjectiveUid: this.studyObjective.study_objective_uid
          }
          notification = 'objective_updated'
        }
      } else if (this.creationMode === 'template' || this.creationMode === 'scratch') {
        args = {
          studyUid: this.selectedStudy.uid,
          form: JSON.parse(JSON.stringify(this.form)),
          parameters: this.parameters
        }
        action = 'studyObjectives/addStudyObjectiveFromTemplate'
        notification = 'objective_added'
      } else {
        for (const item of this.selectedStudyObjectives) {
          args = {
            studyUid: this.selectedStudy.uid,
            objectiveUid: item.objective.uid
          }
          if (this.form.objective_level) {
            args.objectiveLevelUid = this.form.objective_level.term_uid
          }
          await this.$store.dispatch('studyObjectives/addStudyObjective', args)
        }
        bus.$emit('notification', { msg: this.$t('StudyObjectiveForm.objective_added') })
        this.close()
        return
      }
      if (this.studyObjective && !this.cloneMode && _isEqual(this.originalForm, args.form)) {
        bus.$emit('notification', { msg: this.$t('_global.no_changes'), type: 'info' })
        this.close()
        return
      }
      this.$store.dispatch(action, args).then(resp => {
        bus.$emit('notification', { msg: this.$t(`StudyObjectiveForm.${notification}`) })
        this.close()
      }).catch(() => {
        this.$refs.stepper.loading = false
      })
    }
  },
  mounted () {
    templateParameterTypes.getTypes().then(resp => {
      this.parameterTypes = resp.data
    })
    study.get({ hasStudyObjective: true }).then(resp => {
      this.studies = resp.data.items.filter(study => study.uid !== this.selectedStudy.uid)
    })
  },
  watch: {
    studyObjective: {
      handler (val) {
        if (val) {
          this.initFromStudyObjective(val)
        }
      },
      immediate: true
    },
    creationMode (value) {
      if (!this.studyObjective) {
        if (value === 'template') {
          this.steps = this.alternateSteps
          this.getObjectiveTemplates()
        } else if (value === 'select') {
          this.steps = this.getInitialSteps()
        } else {
          this.steps = this.scratchModeSteps
        }
      }
    }
  }
}
</script>
<style scoped>
.header-title {
  color: var(--v-secondary-base) !important;
  font-size: large;
}
</style>
