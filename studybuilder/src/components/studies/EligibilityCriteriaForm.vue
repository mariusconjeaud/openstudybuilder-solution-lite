<template>
<div>
  <horizontal-stepper-form
    ref="stepper"
    :title="title"
    :steps="steps"
    @close="close"
    @save="submit"
    :form-observer-getter="getObserver"
    :help-items="helpItems"
    :extra-step-validation="createTemplate"
    >
    <template v-slot:step.creation_mode>
      <v-radio-group
        v-model="creationMode"
        >
        <v-radio data-cy="criteria-from-study" :label="$t('EligibilityCriteriaForm.select_from_studies')" value="select" />
        <v-radio data-cy="criteria-from-template" :label="$t('EligibilityCriteriaForm.create_from_template')" value="template" />
        <v-radio data-cy="criteria-from-scratch" :label="$t('EligibilityCriteriaForm.create_from_scratch')" value="scratch" />
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
    <template v-slot:step.select>
      <p class="grey--text text-subtitle-1 font-weight-bold">{{ $t('EligibilityCriteriaForm.selected_criteria') }}</p>
      <v-data-table
        :headers="selectionHeaders"
        :items="selectedCriteria"
        >
        <template v-slot:item.name="{ item }">
          <template v-if="item.criteria_template">
            <n-n-parameter-highlighter
              :name="item.criteria_template.name"
              default-color="orange"
              />
          </template>
          <template v-else>
            <n-n-parameter-highlighter
              :name="item.criteria.name"
              :show-prefix-and-postfix="false"
              />
          </template>
        </template>
        <template v-slot:item.guidance_text="{ item }">
          <template v-if="item.criteria_template">
            <span v-html="item.criteria_template.guidance_text" />
          </template>
          <template v-else>
            <span v-html="item.criteria.criteria_template.guidance_text" />
          </template>
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            color="red"
            @click="unselectStudyCriteria(item)"
            >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </template>
    <template v-slot:step.select.after>
      <p class="grey--text text-subtitle-1 font-weight-bold mb-0 ml-3">{{ $t('StudyObjectiveForm.copy_instructions') }}</p>
      <v-col cols="12">
        <study-selection-table
          :headers="stdHeaders"
          data-fetcher-name="getAllStudyCriteria"
          @item-selected="selectTemplate"
          :studies="selectedStudies"
          :extra-data-fetcher-filters="extraDataFetcherFilters"
          column-data-resource="study-criteria"
          >
          <template v-slot:item.name="{ item }">
            <template v-if="item.criteria_template">
              <n-n-parameter-highlighter
                :name="item.criteria_template.name"
                default-color="orange"
                />
            </template>
            <template v-else>
              <n-n-parameter-highlighter
                :name="item.criteria.name"
                :show-prefix-and-postfix="false"
                />
            </template>
          </template>
          <template v-slot:item.guidance_text="{ item }">
            <template v-if="item.criteria_template">
              <span v-html="item.criteria_template.guidance_text" />
            </template>
            <template v-else>
              <span v-html="item.criteria.guidance_text" />
            </template>
          </template>
        </study-selection-table>
      </v-col>
    </template>
    <template v-slot:step.createFromTemplate>
      <v-data-table
        :headers="selectionHeaders"
        :items="selectedCriteria"
        >
        <template v-slot:item.name="{ item }">
          <n-n-parameter-highlighter
            :name="item.name"
            default-color="orange"
            />
        </template>
        <template v-slot:item.guidance_text="{ item }">
          <span v-html="item.guidance_text" />
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            color="red"
            @click="unselectTemplate(item)"
            >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </template>
    <template v-slot:step.createFromTemplate.after>
      <div class="d-flex align-center">
        <p class="grey--text text-subtitle-1 font-weight-bold mb-0 ml-3">{{ $t('StudyObjectiveForm.copy_instructions') }}</p>
        <v-switch
          v-model="preInstanceMode"
          :label="$t('StudyObjectiveForm.show_pre_instances')"
          hide-details
          class="ml-4"
          />
      </div>
      <v-col cols="12">
        <n-n-table
          key="criteriaTemplateTable"
          :headers="tplHeaders"
          :items="criteriaTemplates"
          :items-per-page="15"
          hide-default-switches
          hide-actions-menu
          elevation="0"
          :options.sync="options"
          :server-items-length="total"
          has-api
          column-data-resource="criteria-templates"
          @filter="getCriteriaTemplates"
          >
          <template v-slot:item.indications="{ item }">
            <template v-if="item.indications">
              {{ item.indications|names }}
            </template>
             <template v-else>
              {{ $t('_global.not_applicable_long') }}
             </template>
          </template>
          <template v-slot:item.categories="{ item }">
            <template v-if="item.categories">
              {{ item.categories|terms }}
            </template>
            <template v-else>
              {{ $t('_global.not_applicable_long') }}
            </template>
          </template>
          <template v-slot:item.subCategories="{ item }">
            <template v-if="item.subCategories">
              {{ item.subCategories|terms }}
            </template>
            <template v-else>
              {{ $t('_global.not_applicable_long') }}
            </template>
          </template>
          <template v-slot:item.name="{ item }">
            <n-n-parameter-highlighter :name="item.name" default-color="orange" />
          </template>
          <template v-slot:item.guidance_text="{ item }">
            <span v-html="item.guidance_text" />
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn
              :data-cy="$t('StudyObjectiveForm.copy_template')"
              icon
              color="primary"
              @click="selectTemplate(item)"
              :title="$t('StudyObjectiveForm.copy_template')">
              <v-icon>mdi-content-copy</v-icon>
            </v-btn>
          </template>
        </n-n-table>
      </v-col>
    </template>
    <template v-slot:step.createFromScratch="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col>
              <n-n-template-input-field
                :data-cy="$t('EligibilityCriteriaForm.criteria_template')"
                v-model="form.name"
                :label="$t('EligibilityCriteriaForm.criteria_template')"
                :items="parameterTypes"
                :error-messages="errors"
                :show-drop-down-early="true"
                />
            </v-col>
          </v-row>
        </validation-provider>
      </validation-observer>
      <v-row>
        <v-col>
          <vue-editor
            ref="editor"
            id="editor"
            v-model="form.guidance_text"
            :editor-toolbar="customToolbar"
            :placeholder="$t('CriteriaTemplateForm.guidance_text')"
            class="pt-4"
            />
        </v-col>
      </v-row>
    </template>
    <template v-slot:step.createCriteria="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <parameter-value-selector
          v-if="form.criteria_template"
          :value="parameters"
          :template="form.criteria_template.name"
          color="white"
          />
      </validation-observer>
    </template>
  </horizontal-stepper-form>
</div>
</template>

<script>
import { bus } from '@/main'
import templateParameterTypes from '@/api/templateParameterTypes'
import criteriaTemplates from '@/api/criteriaTemplates'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import instances from '@/utils/instances'
import libraries from '@/constants/libraries'
import { mapGetters } from 'vuex'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import NNTable from '@/components/tools/NNTable'
import NNTemplateInputField from '@/components/tools/NNTemplateInputField'
import ParameterValueSelector from '@/components/tools/ParameterValueSelector'
import study from '@/api/study'
import StudySelectionTable from './StudySelectionTable'
import templatePreInstances from '@/api/templatePreInstances'
import filteringParameters from '@/utils/filteringParameters'
import statuses from '@/constants/statuses'
import { VueEditor } from 'vue2-editor'

export default {
  components: {
    HorizontalStepperForm,
    NNParameterHighlighter,
    NNTable,
    NNTemplateInputField,
    ParameterValueSelector,
    StudySelectionTable,
    VueEditor
  },
  props: {
    criteriaType: Object
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    title () {
      return this.$t('_global.add') + ' ' + this.criteriaType.sponsor_preferred_name_sentence_case
    }
  },
  data () {
    return {
      customToolbar: [
        ['bold', 'italic', 'underline'],
        [{ script: 'sub' }, { script: 'super' }],
        [{ list: 'ordered' }, { list: 'bullet' }]
      ],
      helpItems: [
        'EligibilityCriteriaForm.add_criteria',
        'EligibilityCriteriaForm.select_from_studies',
        'EligibilityCriteriaForm.create_from_template',
        'EligibilityCriteriaForm.create_from_scratch',
        'EligibilityCriteriaForm.select_criteria_templates'
      ],
      creationMode: 'select',
      extraDataFetcherFilters: {
        'criteria.library.name': { v: [libraries.LIBRARY_SPONSOR] },
        'criteria_type.sponsor_preferred_name': { v: [this.criteriaType.sponsor_preferred_name] }
      },
      tplHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.sequence_number'), value: 'sequence_id' },
        { text: this.$t('_global.indications'), value: 'indications', filteringName: 'indications.name' },
        { text: this.$t('EligibilityCriteriaForm.criterion_cat'), value: 'categories', filteringName: 'categories.name.sponsor_preferred_name' },
        { text: this.$t('EligibilityCriteriaForm.criterion_sub_cat'), value: 'subCategories', filteringName: 'subCategories.name.sponsor_preferred_name' },
        { text: this.$t('EligibilityCriteriaForm.criteria_template'), value: 'name' },
        { text: this.$t('EligibilityCriteriaForm.guidance_text'), value: 'guidance_text' }
      ],
      criteriaTemplates: [],
      form: {},
      loadingParameters: false,
      parameters: [],
      parameterTypes: [],
      preInstanceMode: true,
      selectedCriteria: [],
      selectedStudies: [],
      steps: this.getInitialSteps(),
      studies: [],
      createFromTemplateSteps: [
        { name: 'creation_mode', title: this.$t('EligibilityCriteriaForm.creation_mode_label') },
        { name: 'createFromTemplate', title: this.$t('EligibilityCriteriaForm.select_criteria_templates') }
      ],
      createFromScratchSteps: [
        { name: 'creation_mode', title: this.$t('EligibilityCriteriaForm.creation_mode_label') },
        { name: 'createFromScratch', title: this.$t('EligibilityCriteriaForm.create_from_scratch'), noStyle: true },
        { name: 'createCriteria', title: this.$t('EligibilityCriteriaForm.create_criteria') }
      ],
      selectionHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('EligibilityCriteriaForm.criteria_text'), value: 'name', class: 'text-center' },
        { text: this.$t('EligibilityCriteriaForm.guidance_text'), value: 'guidance_text' }
      ],
      stdHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('Study.study_id'), value: 'studyUid' },
        { text: this.$t('EligibilityCriteriaForm.criteria_text'), value: 'name' },
        { text: this.$t('EligibilityCriteriaForm.guidance_text'), value: 'guidance_text' }
      ],
      options: {},
      total: 0
    }
  },
  created () {
    this.preInstanceApi = templatePreInstances('criteria')
    if (!this.studyCriteria) {
      this.apiEndpoint = this.preInstanceApi
    }
  },
  mounted () {
    templateParameterTypes.getTypes().then(resp => {
      this.parameterTypes = resp.data
    })
    study.get({ has_study_criteria: true, page_size: 0 }).then(resp => {
      this.studies = resp.data.items.filter(study => study.uid !== this.selectedStudy.uid)
    })
  },
  methods: {
    close () {
      this.$emit('close')
      this.$refs.stepper.reset()
      this.steps = this.getInitialSteps()
      this.creationMode = 'select'
      this.form = {}
      this.selectedStudies = []
      this.selectedCriteria = []
      this.preInstanceMode = true
      this.apiEndpoint = this.preInstanceApi
    },
    getInitialSteps () {
      return [
        { name: 'creation_mode', title: this.$t('EligibilityCriteriaForm.creation_mode_label') },
        { name: 'selectStudies', title: this.$t('EligibilityCriteriaForm.select_studies') },
        { name: 'select', title: this.$t('EligibilityCriteriaForm.select_criteria') }
      ]
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    getCriteriaTemplates (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      params.status = statuses.FINAL
      if (params.filters) {
        params.filters = JSON.parse(params.filters)
      } else {
        params.filters = {}
      }
      if (!this.preInstanceMode) {
        Object.assign(params.filters, { 'type.name.sponsor_preferred_name_sentence_case': { v: [this.criteriaType.sponsor_preferred_name_sentence_case] } })
      } else {
        Object.assign(params.filters, {
          template_type_uid: {
            v: [this.criteriaType.term_uid]
          }
        })
      }
      this.apiEndpoint.get(params).then(resp => {
        this.criteriaTemplates = resp.data.items
        this.total = resp.data.total
      })
    },
    selectTemplate (template) {
      this.selectedCriteria.push(template)
    },
    unselectTemplate (template) {
      this.selectedCriteria = this.selectedCriteria.filter(item => item.name !== template.name)
    },
    unselectStudyCriteria (studyCriteria) {
      this.selectedCriteria = this.selectedCriteria.filter(item => item.study_criteria_uid !== studyCriteria.study_criteria_uid)
    },
    async loadParameters (template) {
      if (template) {
        this.loadingParameters = true
        const resp = await criteriaTemplates.getObjectTemplateParameters(template.uid)
        this.parameters = resp.data
        this.loadingParameters = false
      } else {
        this.parameters = []
      }
    },
    async createTemplate (step) {
      if (this.creationMode !== 'scratch' || step !== 2) {
        return true
      }
      const data = {
        ...this.form,
        library_name: 'User Defined',
        type_uid: this.criteriaType.term_uid,
        study_uid: this.selectedStudy.uid
      }
      try {
        const resp = await criteriaTemplates.create(data)
        await criteriaTemplates.approve(resp.data.uid)
        this.$set(this.form, 'criteria_template', resp.data)
      } catch (error) {
        return false
      }
      this.loadParameters(this.form.criteria_template)
      return true
    },
    async submit () {
      if (this.creationMode !== 'scratch') {
        if (this.creationMode === 'template') {
          if (!this.selectedCriteria.length) {
            bus.$emit('notification', { msg: this.$t('EligibilityCriteriaForm.no_template_error'), type: 'error' })
            this.$refs.stepper.loading = false
            return
          }
          const data = []
          for (const criteria of this.selectedCriteria) {
            data.push({
              criteria_template_uid: this.preInstanceMode ? criteria.template_uid : criteria.uid,
              parameter_terms: this.preInstanceMode ? criteria.parameter_terms : undefined,
              library_name: criteria.library.name
            })
          }
          await study.batchCreateStudyCriteria(this.selectedStudy.uid, data)
        } else {
          if (!this.selectedCriteria.length) {
            bus.$emit('notification', { msg: this.$t('EligibilityCriteriaForm.no_criteria_error'), type: 'error' })
            this.$refs.stepper.loading = false
            return
          }
          const data = []
          for (const studyCriteria of this.selectedCriteria) {
            if (studyCriteria.criteria_template) {
              data.push({
                criteria_template_uid: studyCriteria.criteria_template.uid,
                library_name: studyCriteria.criteria_template.library.name
              })
            } else {
              const payload = {
                criteria_data: {
                  parameter_terms: studyCriteria.criteria.parameter_terms,
                  criteria_template_uid: studyCriteria.criteria.criteria_template.uid,
                  library_name: studyCriteria.criteria.library.name
                }
              }
              await study.createStudyCriteria(this.selectedStudy.uid, payload)
            }
          }
          await study.batchCreateStudyCriteria(this.selectedStudy.uid, data)
        }
      } else {
        const data = {
          criteria_data: {
            criteria_template_uid: this.form.criteria_template.uid,
            parameter_terms: await instances.formatParameterValues(this.parameters),
            library_name: libraries.LIBRARY_SPONSOR
          }
        }
        await study.createStudyCriteria(this.selectedStudy.uid, data)
      }
      bus.$emit('notification', { type: 'success', msg: this.$t('EligibilityCriteriaForm.add_success') })
      this.$emit('added')
      this.close()
    }
  },
  watch: {
    creationMode (value) {
      if (value === 'select') {
        this.steps = this.getInitialSteps()
      } else if (value === 'template') {
        this.steps = this.createFromTemplateSteps
        this.getCriteriaTemplates()
      } else {
        this.steps = this.createFromScratchSteps
      }
    },
    preInstanceMode (value) {
      this.apiEndpoint = value ? this.preInstanceApi : criteriaTemplates
      this.getCriteriaTemplates()
    }
  }
}
</script>
