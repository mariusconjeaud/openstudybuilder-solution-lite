<template>
<div class="fullscreen-dialog">
  <horizontal-stepper-form
    ref="stepper"
    :title="title"
    :steps="steps"
    @close="close"
    @save="submit"
    :form-observer-getter="getObserver"
    :helpItems="helpItems"
    :editable="preInstance !== undefined"
    >
    <template v-slot:step.setValues="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <parameter-value-selector
          v-if="template"
          v-model="parameters"
          :template="template.name"
          preview-text=" "
          />
        <parameter-value-selector
          v-else-if="preInstance"
          v-model="parameters"
          :template="preInstance.name"
          preview-text=" "
          />
      </validation-observer>
    </template>
    <template v-slot:step.indexing="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <slot name="indexingTab"
              v-bind:form="form"
              v-bind:template="template"
              v-bind:preInstance="preInstance"
              >
        </slot>
      </validation-observer>
    </template>
    <template v-slot:step.change="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <validation-provider
          v-slot="{ errors }"
          name="ChangeDescription"
          rules="required"
          >
          <v-textarea
            v-model="form.change_description"
            :label="$t('HistoryTable.change_description')"
            :error-messages="errors"
            :rows="1"
            dense
            clearable
            auto-grow
            class="white pa-5"
            ></v-textarea>
        </validation-provider>
      </validation-observer>
    </template>
  </horizontal-stepper-form>
</div>
</template>

<script>
import _isEqual from 'lodash/isEqual'
import { bus } from '@/main'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import instances from '@/utils/instances'
import ParameterValueSelector from '@/components/tools/ParameterValueSelector'
import templatesApi from '@/api/templates'
import templatePreInstancesApi from '@/api/templatePreInstances'

export default {
  props: {
    objectType: String,
    template: {
      type: Object,
      required: false
    },
    preInstance: {
      type: Object,
      required: false
    },
    preparePayloadFunction: {
      type: Function,
      required: false
    }
  },
  components: {
    HorizontalStepperForm,
    ParameterValueSelector
  },
  computed: {
    translationKey () {
      const parts = this.objectType.split('-')
      return parts.map(part => part.charAt(0).toUpperCase() + part.slice(1)).join('')
    },
    title () {
      const context = {}
      if (this.template) {
        return this.$t(`${this.translationKey}PreInstanceForm.add_title`, context)
      }
      return this.$t(`${this.translationKey}PreInstanceForm.edit_title`, context)
    }
  },
  created () {
    let result = this.objectType.replace('Templates', '')
    if (result === 'activity') {
      result = 'activity-instruction'
    }
    if (this.template) {
      this.api = templatesApi(`/${result}-templates`)
    } else {
      this.api = templatePreInstancesApi(result)
    }
  },
  data () {
    return {
      form: {},
      helpItems: [],
      originalParameters: [],
      parameters: [],
      steps: [
        { name: 'setValues', title: this.$t('PreInstanceForm.step1_title') },
        { name: 'indexing', title: this.$t('PreInstanceForm.step2_title') }
      ]
    }
  },
  methods: {
    close () {
      this.parameters = []
      this.form = {}
      this.$refs.stepper.reset()
      this.$emit('close')
    },
    async loadParameters (template) {
      if (!this.api) {
        let result = this.objectType.replace('Templates', '')
        if (result === 'activity') {
          result = 'activity-instruction'
        }
        this.api = templatesApi(`/${result}-templates`)
      }
      this.loadingParameters = true
      const resp = await this.api.getParameters(template.uid)
      this.parameters = resp.data
      this.loadingParameters = false
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    async preparePayload (data) {
      if (data.indications && data.indications.length > 0) {
        data.indication_uids = data.indications.map(item => item.term_uid)
      } else {
        data.indication_uids = []
      }
      if (this.preparePayloadFunction) {
        this.preparePayloadFunction(data)
      }
      data.parameter_terms = await instances.formatParameterValues(this.parameters)
      if (this.template) {
        data.library_name = this.template.library.name
      }
    },
    async submit () {
      const data = { ...this.form }
      await this.preparePayload(data)
      if (this.template) {
        await this.api.addPreInstance(this.template.uid, data)
        this.$emit('success')
        bus.$emit('notification', { msg: this.$t(`${this.translationKey}PreInstanceForm.add_success`) })
      } else {
        let updated = false
        if (!_isEqual(this.originalParameters, this.parameters)) {
          await this.api.update(this.preInstance.uid, data)
          updated = true
        }
        if (!_isEqual(this.originalForm, this.form)) {
          await this.api.updateIndexings(this.preInstance.uid, data)
          updated = true
        }
        if (updated) {
          this.$emit('success')
          bus.$emit('notification', { msg: this.$t(`${this.translationKey}PreInstanceForm.update_success`) })
        } else {
          bus.$emit('notification', { type: 'info', msg: this.$t('_global.no_changes') })
        }
      }
      this.close()
    }
  },
  mounted () {
    if (this.preInstance) {
      this.api.getParameters(this.preInstance.template_uid).then(resp => {
        this.parameters = resp.data
        instances.loadParameterValues(this.preInstance.parameter_terms, this.parameters)
        this.originalParameters = JSON.parse(JSON.stringify(this.parameters))
      })
    }
  },
  watch: {
    template: {
      handler (value) {
        if (value) {
          this.form = { ...value }
          this.loadParameters(value)
        }
      },
      immediate: true
    },
    preInstance: {
      handler (value) {
        if (value) {
          this.form = { ...value }
          this.$set(this.form, 'change_description', this.$t('_global.work_in_progress'))
          this.originalForm = JSON.parse(JSON.stringify(this.form))
          this.steps.push(
            { name: 'change', title: this.$t('GenericTemplateForm.step4_title') }
          )
        }
      },
      immediate: true
    }
  }
}
</script>
