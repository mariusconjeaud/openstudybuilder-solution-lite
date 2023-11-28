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
    :loadingContinue="loadingContinue"
    >
    <template v-slot:step.creationMode>
      <v-radio-group
        v-model="creationMode"
        >
        <v-radio data-cy="footnote-from-template" :label="$t('StudyFootnoteForm.template_mode')" value="template" />
        <v-radio data-cy="footnote-from-select" :label="$t('StudyFootnoteForm.select_mode')" value="select" />
        <v-radio data-cy="footnote-from-scratch" :label="$t('StudyFootnoteForm.scratch_mode')" value="scratch" />
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
    <template v-slot:step.selectFootnote>
      <p class="grey--text text-subtitle-1 font-weight-bold">{{ $t('StudyFootnoteForm.selected_footnotes') }}</p>
      <v-data-table
        data-cy="selected-footnotes-table"
        :headers="selectedFootnoteHeaders"
        :items="selectedStudyFootnotes"
        >
        <template v-slot:item.footnote.name="{ item }">
          <n-n-parameter-highlighter :name="item.footnote.name" />
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            color="red"
            @click="unselectStudyFootnote(item)"
           >
            <v-icon>mdi-delete-outline</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </template>
    <template v-slot:step.selectFootnote.after>
      <p class="grey--text text-subtitle-1 font-weight-bold mb-0 ml-3">{{ $t('StudyFootnoteForm.copy_instructions') }}</p>
      <v-col cols="12" flat class="pt-0 mt-0">
        <study-selection-table
          :headers="footnoteHeaders"
          data-fetcher-name="getAllStudyFootnotes"
          :extra-data-fetcher-filters="extraStudyFootnoteFilters"
          @item-selected="selectStudyFootnote"
          :studies="selectedStudies"
          column-data-resource="study-soa-footnotes"
          >
          <template v-slot:item.footnote.name="{ item }">
            <n-n-parameter-highlighter :name="item.footnote.name" />
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn
              :data-cy="$t('StudySelectionTable.copy_item')"
              icon
              :color="getCopyButtonColor(item)"
              :disabled="isStudyFootnoteselected(item)"
              @click="selectStudyFootnote(item)"
              :title="$t('StudySelectionTable.copy_item')">
              <v-icon>mdi-content-copy</v-icon>
            </v-btn>
          </template>
        </study-selection-table>
      </v-col>
    </template>
    <template v-slot:step.selectTemplates>
       <v-data-table
         :headers="selectionHeaders"
         :items="selectedTemplates"
         >
         <template v-slot:item.name="{ item }">
           <n-n-parameter-highlighter
             :name="item.name"
             default-color="orange"
             />
         </template>
         <template v-slot:item.actions="{ item }">
           <v-btn
             icon
             color="red"
             @click="unselectTemplate(item)"
             >
             <v-icon>mdi-delete-outline</v-icon>
           </v-btn>
         </template>
       </v-data-table>
    </template>
    <template v-slot:step.selectTemplates.after>
      <div class="d-flex align-center">
        <p class="grey--text text-subtitle-1 font-weight-bold mb-0 ml-3">{{ $t('StudyFootnoteForm.copy_instructions') }}</p>
        <v-switch
          v-model="preInstanceMode"
          :label="$t('StudyFootnoteForm.show_pre_instances')"
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
          :default-filters="defaultTplFilters"
          :items-per-page="15"
          elevation="0"
          :options.sync="options"
          :server-items-length="total"
          has-api
          :column-data-resource="`footnote-templates`"
          @filter="getFootnoteTemplates"
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
            <template v-if="item.indications && item.indications.length">
              {{ item.indications | names }}
            </template>
            <template v-else>
              {{ $t('_global.not_applicable_long') }}
            </template>
          </template>
          <template v-slot:item.activity_groups="{ item }">
            <template v-if="item.activity_groups && item.activity_groups.length">
              {{ item.activity_groups | names }}
            </template>
            <template v-else>
              {{ $t('_global.not_applicable_long') }}
            </template>
          </template>
          <template v-slot:item.activity_subgroups="{ item }">
            <template v-if="item.activity_subgroups && item.activity_subgroups.length">
              {{ item.activity_subgroups | names }}
            </template>
            <template v-else>
              {{ $t('_global.not_applicable_long') }}
            </template>
          </template>
          <template v-slot:item.activities="{ item }">
            <template v-if="item.activities && item.activities.length">
              {{ item.activities | names }}
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
              :data-cy="$t('StudyFootnoteForm.copy_template')"
              icon
              color="primary"
              @click="selectFootnoteTemplate(item)"
              :title="$t('StudyFootnoteForm.copy_template')">
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
            :data-cy="$t('FootnoteTemplateForm.name')"
            v-model="templateForm.name"
            :label="$t('FootnoteTemplateForm.name')"
            :items="parameterTypes"
            :error-messages="errors"
            :show-drop-down-early="true"
            />
        </validation-provider>
      </validation-observer>
    </template>
    <template v-slot:step.createFootnote="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <v-progress-circular
          v-if="loadingParameters"
          indeterminate
          color="secondary"
          />

        <template v-if="form.footnote_template !== undefined">
          <parameter-value-selector
            ref="paramSelector"
            :value="parameters"
            :template="form.footnote_template.name"
            color="white"
            preview-text=" "
            />
        </template>
      </validation-observer>
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
import footnoteConstants from '@/constants/footnotes'
import footnoteTemplates from '@/api/footnoteTemplates'
import templatePreInstances from '@/api/templatePreInstances'
import templateParameterTypes from '@/api/templateParameterTypes'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import NNTable from '@/components/tools/NNTable'
import NNTemplateInputField from '@/components/tools/NNTemplateInputField'
import ParameterValueSelector from '@/components/tools/ParameterValueSelector'
import study from '@/api/study'
import StudySelectionTable from './StudySelectionTable'
import terms from '@/api/controlledTerminology/terms'
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
    currentStudyFootnotes: Array
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    title () {
      return this.$t('StudyFootnoteForm.add_title')
    },
    selectedTemplateName () {
      return (this.form.footnote_template) ? this.form.footnote_template.name : ''
    }
  },
  data () {
    return {
      apiEndpoint: null,
      helpItems: [],
      creationMode: 'template',
      extraStudyFootnoteFilters: {
        'footnote.library.name': { v: [constants.LIBRARY_SPONSOR] }
      },
      footnoteType: null,
      form: {},
      templateForm: {},
      loadingParameters: false,
      parameters: [],
      parameterTypes: [],
      alternateSteps: [
        { name: 'creationMode', title: this.$t('StudyFootnoteForm.creation_mode_label') },
        { name: 'selectStudies', title: this.$t('StudyFootnoteForm.select_studies') },
        { name: 'selectFootnote', title: this.$t('StudyFootnoteForm.select_footnote') }
      ],
      scratchModeSteps: [
        { name: 'creationMode', title: this.$t('StudyFootnoteForm.creation_mode_label') },
        { name: 'createTemplate', title: this.$t('StudyFootnoteForm.create_template_title') },
        { name: 'createFootnote', title: this.$t('StudyFootnoteForm.step2_title') }
      ],
      preInstanceMode: true,
      selectionHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.template'), value: 'name', class: 'text-center' }
      ],
      selectedStudies: [],
      selectedStudyFootnotes: [],
      selectedTemplates: [],
      steps: this.getInitialSteps(),
      studies: [],
      templates: [],
      tplHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.order_short'), value: 'sequence_id', width: '5%' },
        { text: this.$t('_global.template'), value: 'name', filteringName: 'name_plain' },
        { text: this.$t('FootnoteTemplateTable.indications'), value: 'indications' },
        { text: this.$t('ActivityTemplateTable.activity_group'), value: 'activity_groups' },
        { text: this.$t('ActivityTemplateTable.activity_subgroup'), value: 'activity_subgroups' },
        { text: this.$t('ActivityTemplateTable.activity_name'), value: 'activities' }
      ],
      defaultTplFilters: [
        { text: this.$t('_global.sequence_number_short'), value: 'sequence_id' },
        { text: this.$t('_global.indications'), value: 'indications', filteringName: 'indications.name' },
        { text: this.$t('StudyActivity.activity_group'), value: 'activity.activity_group.name' },
        { text: this.$t('StudyActivity.activity_sub_group'), value: 'activity.activity_subgroup.name' },
        { text: this.$t('StudyActivity.activity'), value: 'activity.name' }
      ],
      footnoteHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('Study.study_id'), value: 'study_id', noFilter: true },
        { text: this.$t('StudyFootnoteForm.study_footnote'), value: 'footnote.name', filteringName: 'footnote.name_plain' }
      ],
      selectedFootnoteHeaders: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('Study.study_id'), value: 'study_id' },
        { text: this.$t('StudyFootnoteForm.study_footnote'), value: 'footnote.name' }
      ],
      loadingContinue: false,
      options: {},
      total: 0
    }
  },
  methods: {
    close () {
      this.creationMode = 'template'
      this.form = {}
      this.templateForm = {}
      this.parameters = []
      this.selectedStudyFootnotes = []
      this.selectedStudies = []
      this.apiEndpoint = this.preInstanceApi
      this.$emit('close')
      this.$refs.stepper.reset()
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    getInitialSteps () {
      return [
        { name: 'creationMode', title: this.$t('StudyFootnoteForm.creation_mode_label') },
        { name: 'selectTemplates', title: this.$t('StudyFootnoteForm.select_tpl_title') }
      ]
    },
    getFootnoteTemplates (filters, sort, filtersUpdated) {
      if (this.footnoteType) {
        const params = filteringParameters.prepareParameters(
          this.options, filters, sort, filtersUpdated)
        params.status = statuses.FINAL
        if (params.filters) {
          params.filters = JSON.parse(params.filters)
        } else {
          params.filters = {}
        }
        Object.assign(params.filters, {
          'library.name': { v: [constants.LIBRARY_SPONSOR] }
        })
        if (this.preInstanceMode) {
          params.filters.template_type_uid = {
            v: [this.footnoteType.term_uid]
          }
        } else {
          params.filters['type.name.sponsor_preferred_name'] = {
            v: [this.footnoteType.sponsor_preferred_name]
          }
        }
        this.apiEndpoint.get(params).then(resp => {
          this.templates = resp.data.items
          this.total = resp.data.total
        })
      }
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
    selectFootnoteTemplate (template) {
      this.selectedTemplates.push(template)
    },
    unselectTemplate (template) {
      this.selectedTemplates = this.selectedTemplates.filter(item => item.name !== template.name)
    },
    selectStudyFootnote (studyFootnote) {
      this.selectedStudyFootnotes.push(studyFootnote)
    },
    unselectStudyFootnote (studyFootnote) {
      this.selectedStudyFootnotes = this.selectedStudyFootnotes.filter(item => item.footnote.name !== studyFootnote.footnote.name)
    },
    isStudyFootnoteselected (studyFootnote) {
      let selected = this.selectedStudyFootnotes.find(item => item.footnote.uid === studyFootnote.footnote.uid)
      if (!selected && this.currentStudyFootnotes.length) {
        selected = this.currentStudyFootnotes.find(item => item.footnote.uid === studyFootnote.footnote.uid)
      }
      return selected !== undefined
    },
    getCopyButtonColor (item) {
      return (!this.isStudyFootnoteselected(item) ? 'primary' : '')
    },
    async extraStepValidation (step) {
      if (this.creationMode === 'template' && step === 1) {
        this.getFootnoteTemplates()
      }
      if (this.creationMode === 'template' && step === 2) {
        if (this.form.footnote_template === undefined || this.form.footnote_template === null) {
          bus.$emit('notification', { msg: this.$t('StudyFootnoteForm.template_not_selected'), type: 'error' })
          return false
        }
        return true
      }
      if (this.creationMode !== 'scratch' || step !== 2) {
        return true
      }
      if (this.form.footnote_template && this.form.footnote_template.name === this.templateForm.name) {
        return true
      }
      const data = {
        ...this.templateForm,
        studyUid: this.selectedStudy.uid,
        library_name: constants.LIBRARY_USER_DEFINED,
        type_uid: this.footnoteType.term_uid
      }
      try {
        this.loadingContinue = true
        const resp = await footnoteTemplates.create(data)
        if (resp.data.status === statuses.DRAFT) await footnoteTemplates.approve(resp.data.uid)
        this.$set(this.form, 'footnote_template', resp.data)
        this.loadingContinue = false
      } catch (error) {
        this.loadingContinue = false
        return false
      }
      this.loadParameters(this.form.footnote_template)
      return true
    },
    async getStudyFootnoteNamePreview () {
      const footnoteData = {
        footnote_template_uid: this.form.footnote.footnote_template.uid,
        parameter_terms: await instances.formatParameterValues(this.parameters),
        library_name: this.form.footnote_template ? this.form.footnote_template.library.name : this.form.footnote.library.name
      }
      const resp = await study.getStudyFootnotePreview(this.selectedStudy.uid, { footnote_data: footnoteData })
      return resp.data.footnote.name
    },
    async submit () {
      let args = null

      if (this.creationMode === 'template') {
        if (!this.selectedTemplates.length) {
          bus.$emit('notification', { msg: this.$t('EligibilityCriteriaForm.no_template_error'), type: 'error' })
          this.$refs.stepper.loading = false
          return
        }
        const data = []
        for (const template of this.selectedTemplates) {
          data.push({
            footnote_data: {
              footnote_template_uid: this.preInstanceMode ? template.template_uid : template.uid,
              parameter_terms: this.preInstanceMode ? template.parameter_terms : [],
              library_name: template.library.name
            }
          })
        }
        await study.batchCreateStudyFootnotes(this.selectedStudy.uid, data)
      } else if (this.creationMode === 'scratch') {
        const data = JSON.parse(JSON.stringify(this.form))
        if (this.preInstanceMode && this.creationMode !== 'scratch') {
          data.footnote_template.uid = data.footnote_template.template_uid
        }
        args = {
          studyUid: this.selectedStudy.uid,
          form: data,
          parameters: this.parameters
        }
        await this.$store.dispatch('studyFootnotes/addStudyFootnoteFromTemplate', args)
      } else {
        for (const item of this.selectedStudyFootnotes) {
          args = {
            studyUid: this.selectedStudy.uid,
            footnoteUid: item.footnote.uid
          }
          await this.$store.dispatch('studyFootnotes/addStudyFootnote', args)
        }
      }
      this.$emit('added')
      bus.$emit('notification', { msg: this.$t('StudyFootnoteForm.footnote_added') })
      this.close()
    }
  },
  created () {
    this.preInstanceApi = templatePreInstances('footnote')
    this.apiEndpoint = this.preInstanceApi
  },
  mounted () {
    templateParameterTypes.getTypes().then(resp => {
      this.parameterTypes = resp.data
    })
    study.get({ has_study_footnote: true, page_size: 0 }).then(resp => {
      this.studies = resp.data.items.filter(study => study.uid !== this.selectedStudy.uid)
    })
    terms.getByCodelist('footnoteTypes').then(resp => {
      for (const type of resp.data.items) {
        if (type.sponsor_preferred_name === footnoteConstants.FOOTNOTE_TYPE_SOA) {
          this.footnoteType = type
          break
        }
      }
    })
  },
  watch: {
    creationMode (value) {
      if (value === 'template') {
        this.steps = this.getInitialSteps()
        this.getFootnoteTemplates()
      } else if (value === 'select') {
        this.steps = this.alternateSteps
      } else {
        this.steps = this.scratchModeSteps
      }
    },
    preInstanceMode (value) {
      this.apiEndpoint = value ? this.preInstanceApi : footnoteTemplates
      this.getFootnoteTemplates()
      this.selectedTemplates = []
    },
    footnoteType () {
      this.getFootnoteTemplates()
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
