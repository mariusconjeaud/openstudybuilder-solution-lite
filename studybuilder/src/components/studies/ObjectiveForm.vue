<template>
<div>
  <horizontal-stepper-form
    ref="stepper"
    :title="title"
    :steps="steps"
    @close="close"
    @save="submit"
    :form-observer-getter="getObserver"
    :extra-step-validation="extraStepValidation"
    :helpItems="helpItems"
    :editData="form"
    >
    <template v-slot:step.creationMode>
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
          <v-autocomplete
            :data-cy="$t('StudySelectionTable.select_studies')"
            v-model="selectedStudies"
            :label="$t('StudySelectionTable.studies')"
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
          column-data-resource="study-objectives"
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
            />
        </v-card-text>
      </v-card>
    </template>
    <template v-slot:step.selectTemplate.after>
      <div class="d-flex align-center">
        <p class="grey--text text-subtitle-1 font-weight-bold mb-0 ml-3">{{ $t('StudyObjectiveForm.copy_instructions') }}</p>
        <v-switch
          v-model="preInstanceMode"
          :label="$t('StudyObjectiveForm.show_pre_instances')"
          hide-details
          class="ml-4"
          />
      </div>
      <v-col cols="12" class="pt-0">
        <n-n-table
          key="templatesTable"
          :headers="tplHeaders"
          :items="templates"
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
          <template v-slot:item.categories.name.sponsor_preferred_name="{ item }">
            <template v-if="item.categories">
              {{ item.categories|terms }}
            </template>
            <template v-else>
              {{ $t('_global.not_applicable_long') }}
            </template>
          </template>
          <template v-slot:item.is_confirmatory_testing="{ item }">
            <template v-if="item.is_confirmatory_testing !== null">
              {{ item.is_confirmatory_testing|yesno }}
            </template>
            <template v-else>
              {{ $t('_global.not_applicable_long') }}
            </template>
          </template>
          <template v-slot:item.indications="{ item }">
            <template v-if="item.indications">
              {{ item.indications|names }}
            </template>
            <template v-else>
              {{ $t('_global.not_applicable_long') }}
            </template>
          </template>
          <template v-slot:item.name="{ item }">
            <n-n-parameter-highlighter
              :name="item.name"
              default-color="orange"
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
import { bus } from '@/main'
import { objectManagerMixin } from '@/mixins/objectManager'
import instances from '@/utils/instances'
import statuses from '@/constants/statuses'
import objectiveTemplates from '@/api/objectiveTemplates'
import templatePreInstances from '@/api/templatePreInstances'
import templateParameterTypes from '@/api/templateParameterTypes'
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
    currentStudyObjectives: Array
  },
  computed: {
    ...mapGetters({
      objectiveLevels: 'studiesGeneral/objectiveLevels',
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    title () {
      return this.$t('StudyObjectiveForm.add_title')
    },
    selectedTemplateName () {
      return (this.form.objective_template) ? this.form.objective_template.name : ''
    }
  },
  data () {
    return {
      apiEndpoint: null,
      helpItems: [
        'StudyObjectiveForm.add_title',
        'StudyObjectiveForm.select_mode',
        'StudyObjectiveForm.template_mode',
        'StudyObjectiveForm.scratch_mode',
        'StudyObjectiveForm.select_objective_tpl',
        'StudyObjectiveForm.select_tpl_parameters_label',
        'StudyObjectiveForm.select_studies',
        'StudyObjectiveForm.study_objective',
        'StudyObjectiveForm.objective_level'
      ],
      creationMode: 'select',
      extraStudyObjectiveFilters: {
        'objective.library.name': { v: [constants.LIBRARY_SPONSOR] }
      },
      form: {},
      templateForm: {},
      loadingParameters: false,
      parameters: [],
      parameterTypes: [],
      alternateSteps: [
        { name: 'creationMode', title: this.$t('StudyObjectiveForm.creation_mode_label') },
        { name: 'selectTemplate', title: this.$t('StudyObjectiveForm.select_tpl_title') },
        { name: 'createObjective', title: this.$t('StudyObjectiveForm.step2_title') },
        { name: 'objectiveLevel', title: this.$t('StudyObjectiveForm.step3_title') }
      ],
      scratchModeSteps: [
        { name: 'creationMode', title: this.$t('StudyObjectiveForm.creation_mode_label') },
        { name: 'createTemplate', title: this.$t('StudyObjectiveForm.create_template_title') },
        { name: 'createObjective', title: this.$t('StudyObjectiveForm.step2_title') },
        { name: 'objectiveLevel', title: this.$t('StudyObjectiveForm.step3_title') }
      ],
      preInstanceMode: true,
      selectedStudies: [],
      selectedStudyObjectives: [],
      steps: this.getInitialSteps(),
      studies: [],
      templates: [],
      tplHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.sequence_number'), value: 'sequence_id' },
        { text: this.$t('_global.indications'), value: 'indications', filteringName: 'indications.name' },
        { text: this.$t('ObjectiveTemplateTable.objective_cat'), value: 'categories.name.sponsor_preferred_name' },
        { text: this.$t('ObjectiveTemplateTable.confirmatory_testing'), value: 'is_confirmatory_testing' },
        {
          text: this.$t('_global.template'),
          value: 'name',
          width: '30%',
          filteringName: 'name_plain'
        }
      ],
      objectiveHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('Study.study_id'), value: 'study_id', noFilter: true },
        { text: this.$t('StudyObjectiveForm.study_objective'), value: 'objective.name', filteringName: 'objective.name_plain' },
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
      this.apiEndpoint = this.preInstanceApi
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
      this.apiEndpoint.get(params).then(resp => {
        this.templates = resp.data.items
        this.total = resp.data.total
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
        const templateUid = (this.creationMode !== 'scratch' && this.preInstanceMode) ? template.template_uid : template.uid
        const resp = await this.apiEndpoint.getParameters(templateUid, { study_uid: this.selectedStudy.uid })
        this.parameters = resp.data
        this.loadingParameters = false
      } else {
        this.parameters = []
      }
    },
    async selectObjectiveTemplate (template) {
      await this.loadParameters(template)
      if (this.preInstanceMode) {
        instances.loadParameterValues(template.parameter_terms, this.parameters)
      }
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
    async extraStepValidation (step) {
      if (this.creationMode === 'template' && step === 2) {
        if (this.form.objective_template === undefined || this.form.objective_template === null) {
          bus.$emit('notification', { msg: this.$t('StudyObjectiveForm.template_not_selected'), type: 'error' })
          return false
        }
        return true
      }
      if ((this.creationMode !== 'scratch' || step !== 2) &&
          (this.creationMode !== 'clone' || step !== 1)) {
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
        parameter_terms: await instances.formatParameterValues(this.parameters),
        library_name: this.form.objective_template ? this.form.objective_template.library.name : this.form.objective.library.name
      }
      const resp = await study.getStudyObjectivePreview(this.selectedStudy.uid, { objective_data: objectiveData })
      return resp.data.objective.name
    },
    async submit () {
      let action = null
      let notification = null
      let args = null

      if (this.creationMode === 'template' || this.creationMode === 'scratch') {
        const data = JSON.parse(JSON.stringify(this.form))
        if (this.preInstanceMode && this.creationMode !== 'scratch') {
          data.objective_template.uid = data.objective_template.template_uid
        }
        args = {
          studyUid: this.selectedStudy.uid,
          form: data,
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
      this.$store.dispatch(action, args).then(resp => {
        bus.$emit('notification', { msg: this.$t(`StudyObjectiveForm.${notification}`) })
        this.close()
      }).catch(() => {
        this.$refs.stepper.loading = false
      })
    }
  },
  created () {
    this.preInstanceApi = templatePreInstances('objective')
    this.apiEndpoint = this.preInstanceApi
  },
  mounted () {
    templateParameterTypes.getTypes().then(resp => {
      this.parameterTypes = resp.data
    })
    study.get({ has_study_objective: true, page_size: 0 }).then(resp => {
      this.studies = resp.data.items.filter(study => study.uid !== this.selectedStudy.uid)
    })
  },
  watch: {
    creationMode (value) {
      if (value === 'template') {
        this.steps = this.alternateSteps
        this.getObjectiveTemplates()
      } else if (value === 'select') {
        this.steps = this.getInitialSteps()
      } else {
        this.steps = this.scratchModeSteps
      }
    },
    preInstanceMode (value) {
      this.apiEndpoint = value ? this.preInstanceApi : objectiveTemplates
      this.getObjectiveTemplates()
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
