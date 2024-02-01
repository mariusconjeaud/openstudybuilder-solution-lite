<template>
<simple-form-dialog
  ref="form"
  :title="title"
  :help-items="helpItems"
  @close="close"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <div class="d-flex align-center">
      <div class="secondary--text text-h6">
        {{ $t('_global.template') }}
      </div>
      <v-btn
        v-if="!editTemplate"
        icon
        :title="$t('StudySelectionEditForm.edit_syntax')"
        @click="editTemplate = true" class="ml-4"
        >
        <v-icon color="primary">mdi-pencil-outline</v-icon>
      </v-btn>
      <v-btn
        v-if="editTemplate"
        icon
        color="success"
        class="ml-4"
        @click="saveTemplate"
        :loading="savingTemplate"
        :title="$t('StudySelectionEditForm.save_syntax')"
        >
        <v-icon>mdi-content-save-outline</v-icon>
      </v-btn>
      <v-btn
        v-if="editTemplate"
        icon
        @click="editTemplate = false"
        :loading="savingTemplate"
        :title="$t('StudySelectionEditForm.cancel_modifications')"
        >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </div>
    <validation-observer v-if="editTemplate" ref="observer_1">
      <v-alert
        dense
        type="info"
        >
        {{ templateEditWarning }}
      </v-alert>
      <validation-provider
        v-slot="{ errors }"
        rules="required"
        >
        <n-n-template-input-field
          v-model="templateForm.name"
          :label="$t('ObjectiveTemplateForm.name')"
          :items="parameterTypes"
          :error-messages="errors"
          :show-drop-down-early="true"
          />
      </validation-provider>
    </validation-observer>
    <v-card v-else flat class="parameterBackground">
      <v-card-text>
        <n-n-parameter-highlighter
          :name="templateForm.name"
          default-color="orange"
          :tooltip="false"
          />
      </v-card-text>
    </v-card>
    <validation-observer ref="observer_2">
      <div class="mt-6">
        <v-progress-circular
          v-if="loadingParameters"
          indeterminate
          color="secondary"
          />

        <template v-else>
          <parameter-value-selector
            ref="paramSelector"
            :value="parameters"
            :template="templateName"
            color="white"
            stacked
            :disabled="editTemplate"
            :with-unformatted-version="withUnformattedVersion"
            :unformatted-label="$t('StudySelectionEditForm.unformatted_text')"
            />
        </template>
      </div>
    </validation-observer>
    <slot name="formFields" v-bind:editTemplate="editTemplate" v-bind:form="form" />
  </template>
</simple-form-dialog>
</template>

<script>
import constants from '@/constants/libraries'
import statuses from '@/constants/statuses'
import libraryObjects from '@/api/libraryObjects'
import { mapGetters } from 'vuex'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import NNTemplateInputField from '@/components/tools/NNTemplateInputField'
import { objectManagerMixin } from '@/mixins/objectManager'
import ParameterValueSelector from '@/components/tools/ParameterValueSelector'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import templateParameters from '@/utils/templateParameters'
import templateParameterTypes from '@/api/templateParameterTypes'
import templates from '@/api/templates'

export default {
  mixins: [objectManagerMixin],
  components: {
    NNParameterHighlighter,
    NNTemplateInputField,
    ParameterValueSelector,
    SimpleFormDialog
  },
  props: {
    title: String,
    studySelection: Object,
    template: Object,
    libraryName: String,
    objectType: String,
    getObjectFromSelection: Function,
    open: Boolean,
    withUnformattedVersion: {
      type: Boolean,
      default: true
    },
    prepareTemplatePayloadFunc: {
      type: Function,
      required: false
    }
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    templateName () {
      return this.newTemplate
        ? this.newTemplate.name
        : this.studySelection ? this.template.name : ''
    },
    apiEndpoint () {
      if (this.objectType !== 'criteria') {
        return libraryObjects(`/${this.objectType}s`)
      }
      return libraryObjects(`/${this.objectType}`)
    },
    templateApi () {
      return templates(`/${this.objectType}-templates`)
    },
    templateEditWarning () {
      if (this.newTemplate) {
        return this.$t('StudySelectionEditForm.edit_user_tpl_warning')
      }
      if (this.studySelection && this.libraryName === constants.LIBRARY_USER_DEFINED) {
        return this.$t('StudySelectionEditForm.edit_user_tpl_warning')
      }
      return this.$t('StudySelectionEditForm.edit_parent_tpl_warning')
    }
  },
  data () {
    return {
      editTemplate: false,
      form: { template: {} },
      helpItems: [],
      loadingParameters: false,
      newTemplate: null,
      parameters: [],
      parameterTypes: [],
      savingTemplate: false,
      steps: [
        { name: 'editSyntax', title: this.$t('StudySelectionEditForm.edit_syntax') },
        { name: 'editValues', title: this.$t('StudySelectionEditForm.edit_values') }
      ],
      templateForm: {}
    }
  },
  methods: {
    close () {
      this.form = { template: {} }
      this.templateForm = {}
      this.parameters = []
      if (this.$refs.observer_1) {
        this.$refs.observer_1.reset()
      }
      this.$refs.observer_2.reset()
      this.editTemplate = false
      this.$refs.form.working = false
      this.$emit('close')
    },
    compareParameters (oldTemplate, newTemplate) {
      const oldParams = templateParameters.getTemplateParametersFromTemplate(oldTemplate)
      const newParams = templateParameters.getTemplateParametersFromTemplate(newTemplate)
      if (oldParams.length === newParams.length) {
        let differ = false
        for (let index = 0; index < oldParams.length; index++) {
          if (oldParams[index] !== newParams[index]) {
            differ = true
            break
          }
        }
        if (!differ) {
          return true
        }
      }
      return false
    },
    cleanName (value) {
      const result = value.replace(/^<p>/, '')
      return result.replace(/<\/p>$/, '')
    },
    async saveTemplate () {
      const valid = await this.$refs.observer_1.validate()
      if (!valid) {
        return
      }
      this.savingTemplate = true
      const cleanedName = this.cleanName(this.templateForm.name)
      const cleanedOriginalName = this.cleanName(this.template.name)
      if ((!this.newTemplate && cleanedName !== cleanedOriginalName) ||
          (this.newTemplate && this.templateForm.name !== this.newTemplate.name)) {
        const data = { ...this.templateForm, studyUid: this.selectedStudy.uid }
        data.library_name = constants.LIBRARY_USER_DEFINED
        if (this.prepareTemplatePayloadFunc) {
          this.prepareTemplatePayloadFunc(data)
        }
        try {
          const resp = await this.templateApi.create(data)
          if (resp.data.status === statuses.DRAFT) await this.templateApi.approve(resp.data.uid)
          this.newTemplate = resp.data
          if (
            !this.compareParameters(
              this.template.name_plain,
              this.newTemplate.name_plain)
          ) {
            this.loadParameters(true)
          }
        } catch (error) {
          return
        } finally {
          this.savingTemplate = false
        }
      }
      this.editTemplate = false
    },
    loadParameters (forceLoading) {
      if (this.parameters.length && !forceLoading) {
        return
      }
      this.loadingParameters = true
      const templateUid = this.newTemplate ? this.newTemplate.uid : this.template.uid
      this.templateApi.getParameters(templateUid, { study_uid: this.selectedStudy.uid }).then(resp => {
        this.parameters = resp.data
        this.loadingParameters = false
        const instance = this.getObjectFromSelection(this.studySelection)
        if (!forceLoading && instance) {
          this.showParametersFromObject(instance)
        }
      })
    },
    async submit () {
      const valid = await this.$refs.observer_2.validate()
      if (!valid) {
        return
      }
      this.$refs.working = true
      this.$emit('submit', this.newTemplate, this.form, this.parameters)
    }
  },
  mounted () {
    templateParameterTypes.getTypes().then(resp => {
      this.parameterTypes = resp.data
    })
  },
  watch: {
    template: {
      handler (newValue) {
        if (newValue) {
          this.templateForm = { ...newValue }
          this.$emit('initForm', this.form)
          this.loadParameters()
        } else {
          this.templateForm = {}
        }
      },
      immediate: true
    },
    editTemplate (value) {
      if (value) {
        this.$refs.form.disableActions()
      } else {
        this.$refs.form.enableActions()
      }
    }
  }
}
</script>
