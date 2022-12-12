<template>
<div>
  <horizontal-stepper-form
    ref="stepper"
    :title="$t('EligibilityCriteriaEditForm.title')"
    :steps="steps"
    @close="close"
    @save="submit"
    :form-observer-getter="getObserver"
    editable
    :helpText="$t('_help.StudyObjectiveTable.general')"
    >
    <template v-slot:step.editCriteria="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <parameter-value-selector
          :value="parameters"
          :template="template.name"
          color="white"
          preview-text=" "
          />
      </validation-observer>
    </template>
  </horizontal-stepper-form>
</div>
</template>

<script>
import { bus } from '@/main'
import criteria from '@/api/criteria'
import criteriaTemplates from '@/api/criteriaTemplates'
import instances from '@/utils/instances'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import { mapGetters } from 'vuex'
import { objectManagerMixin } from '@/mixins/objectManager'
import ParameterValueSelector from '@/components/tools/ParameterValueSelector'
import study from '@/api/study'

export default {
  mixins: [objectManagerMixin],
  props: {
    studyCriteria: Object
  },
  components: {
    ParameterValueSelector,
    HorizontalStepperForm
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    template () {
      if (this.studyCriteria.criteria_template) {
        return this.studyCriteria.criteria_template
      }
      return this.studyCriteria.criteria.criteria_template
    },
    library () {
      if (this.studyCriteria.criteria_template) {
        return this.studyCriteria.criteria_template.library
      }
      return this.studyCriteria.criteria.library
    }
  },
  data () {
    return {
      apiEndpoint: criteria,
      helpItems: [],
      loadingParameters: false,
      parameters: [],
      steps: [
        { name: 'editCriteria', title: this.$t('EligibilityCriteriaEditForm.step_title') }
      ]
    }
  },
  methods: {
    close () {
      this.$refs.observer_1.reset()
      this.working = false
      this.$refs.stepper.loading = false
      this.$emit('close')
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    loadTemplateParameters () {
      this.parameters = []
      this.loadingParameters = true
      criteriaTemplates.getParameters(this.template.uid).then(resp => {
        this.parameters = resp.data
        this.loadingParameters = false
        if (this.studyCriteria.criteria) {
          this.showParametersFromObject(this.studyCriteria.criteria)
        }
      })
    },
    async getStudyCriteriaNamePreview () {
      const criteriaData = {
        criteria_template_uid: this.studyCriteria.criteria.criteria_template.uid,
        parameter_values: await instances.formatParameterValues(this.parameters),
        library_name: this.studyCriteria.criteria.library.name
      }
      const resp = await study.getStudyCriteriaPreview(this.selectedStudy.uid, { criteria_data: criteriaData })
      return resp.data.criteria.name
    },
    async submit () {
      const valid = await this.$refs.observer_1.validate()
      if (!valid) {
        return
      }
      if (this.studyCriteria.criteria) {
        const namePreview = await this.getStudyCriteriaNamePreview()
        if (namePreview === this.studyCriteria.criteria.name) {
          bus.$emit('notification', { msg: this.$t('_global.no_changes'), type: 'info' })
          this.close()
          return
        }
      }
      const parameterValues = await instances.formatParameterValues(this.parameters)
      const data = {
        criteria_template_uid: this.template.uid,
        parameter_values: parameterValues,
        library_name: this.library.name
      }
      await study.patchStudyCriteria(this.selectedStudy.uid, this.studyCriteria.study_criteria_uid, data)
      bus.$emit('notification', { msg: this.$t('EligibilityCriteriaEditForm.update_success') })
      this.$emit('updated')
      this.close()
    }
  },
  mounted () {
    this.loadTemplateParameters()
  },
  watch: {
    studyCriteria (value) {
      if (value) {
        this.loadTemplateParameters()
      }
    },
    parameters () {
      this.parameters.forEach(el => {
        if (el.name === 'TextValue' && el.selected_values && el.selected_values.length) {
          this.parameters[this.parameters.indexOf(el)].selected_values = el.selected_values[0].name
        }
      })
    }
  }
}
</script>
