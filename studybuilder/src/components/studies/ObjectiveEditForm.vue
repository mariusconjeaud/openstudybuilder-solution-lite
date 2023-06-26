<template>
<simple-form-dialog
  ref="form"
  :title="$t('StudyObjectiveEditForm.title')"
  :help-items="helpItems"
  @close="close"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <div class="d-flex align-center">
      <div class="secondary--text text-subtitle-1 font-weight-bold">
        {{ templateLabel }}
      </div>
      <v-btn
        v-if="!editTemplate"
        icon
        :title="$t('StudyObjectiveEditForm.edit_syntax')"
        @click="editTemplate = true" class="ml-4"
        >
        <v-icon color="primary">mdi-pencil</v-icon>
      </v-btn>
      <v-btn
        v-if="editTemplate"
        icon
        color="success"
        class="ml-4"
        @click="saveTemplate"
        :title="$t('StudyObjectiveEditForm.save_syntax')"
        >
        <v-icon>mdi-content-save</v-icon>
      </v-btn>
      <v-btn
        v-if="editTemplate"
        icon
        @click="editTemplate = false"
        :title="$t('StudyObjectiveEditForm.cancel_modifications')"
        >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </div>
    <validation-observer v-if="editTemplate" ref="observer_1">
      <v-alert
        dense
        type="info"
        >
        {{ $t('StudyObjectiveEditForm.edit_warning') }}
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
            />
        </template>
      </div>
    </validation-observer>
    <p class="mt-6 secondary--text text-subtitle-1 font-weight-bold">
      {{ $t('StudyObjectiveEditForm.select_level') }}
    </p>
    <v-row>
      <v-col cols="11">
        <v-select
          v-model="form.objective_level"
          :label="$t('StudyObjectiveForm.objective_level')"
          :items="objectiveLevels"
          item-text="sponsor_preferred_name"
          return-object
          dense
          clearable
          style="max-width: 400px"
          :disabled="editTemplate"
          />
      </v-col>
    </v-row>
  </template>
</simple-form-dialog>
</template>

<script>
import { bus } from '@/main'
import constants from '@/constants/libraries'
import templateParameters from '@/utils/templateParameters'
import instances from '@/utils/instances'
import { mapGetters } from 'vuex'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import NNTemplateInputField from '@/components/tools/NNTemplateInputField'
import objectives from '@/api/objectives'
import objectiveTemplates from '@/api/objectiveTemplates'
import { objectManagerMixin } from '@/mixins/objectManager'
import ParameterValueSelector from '@/components/tools/ParameterValueSelector'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import study from '@/api/study'
import templateParameterTypes from '@/api/templateParameterTypes'

export default {
  mixins: [objectManagerMixin],
  components: {
    NNParameterHighlighter,
    NNTemplateInputField,
    ParameterValueSelector,
    SimpleFormDialog
  },
  props: {
    studyObjective: Object,
    open: Boolean
  },
  computed: {
    ...mapGetters({
      objectiveLevels: 'studiesGeneral/objectiveLevels',
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    templateName () {
      return this.newTemplate
        ? this.newTemplate.name
        : this.studyObjective ? this.studyObjective.objective.objective_template.name : ''
    },
    templateLabel () {
      if (this.newTemplate) {
        return this.$t('_global.user_defined_template')
      }
      if (this.studyObjective && this.studyObjective.objective.library.name === constants.LIBRARY_USER_DEFINED) {
        return this.$t('_global.user_defined_template')
      }
      return this.$t('_global.parent_template')
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
      steps: [
        { name: 'editSyntax', title: this.$t('StudyObjectiveEditForm.edit_syntax') },
        { name: 'editValues', title: this.$t('StudyObjectiveEditForm.edit_values') }
      ],
      templateForm: {}
    }
  },
  methods: {
    close () {
      this.form = { template: {} }
      this.templateForm = {}
      if (this.$refs.observer_1) {
        this.$refs.observer_1.reset()
      }
      this.$refs.observer_2.reset()
      this.editTemplate = false
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
      const cleanedName = this.cleanName(this.templateForm.name)
      const cleanedOriginalName = this.cleanName(this.studyObjective.objective.objective_template.name)
      if ((!this.newTemplate && cleanedName !== cleanedOriginalName) ||
          (this.newTemplate && this.templateForm.name !== this.newTemplate.name)) {
        const data = { ...this.templateForm, studyUid: this.selectedStudy.uid }
        data.library_name = constants.LIBRARY_USER_DEFINED
        try {
          const resp = await objectiveTemplates.create(data)
          await objectiveTemplates.approve(resp.data.uid)
          this.newTemplate = resp.data
          if (
            !this.compareParameters(
              this.studyObjective.objective.objective_template.name_plain,
              this.newTemplate.name_plain)
          ) {
            this.loadParameters(true)
          }
        } catch (error) {
          return
        }
      }
      this.editTemplate = false
    },
    loadParameters (forceLoading) {
      if (this.parameters.length && !forceLoading) {
        return
      }
      this.loadingParameters = true
      const templateUid = this.newTemplate ? this.newTemplate.uid : this.form.template.uid
      objectiveTemplates.getParameters(templateUid, { study_uid: this.selectedStudy.uid }).then(resp => {
        this.parameters = resp.data
        this.loadingParameters = false
        if (!forceLoading) {
          this.showParametersFromObject(this.studyObjective.objective)
        }
      })
    },
    async getStudyObjectiveNamePreview () {
      const objectiveData = {
        objective_template_uid: this.studyObjective.objective.objective_template.uid,
        parameter_terms: await instances.formatParameterValues(this.parameters),
        library_name: this.studyObjective.objective.library.name
      }
      const resp = await study.getStudyObjectivePreview(this.selectedStudy.uid, { objective_data: objectiveData })
      return resp.data.objective.name
    },
    async submit () {
      const valid = await this.$refs.observer_2.validate()
      if (!valid) {
        return
      }
      let action = null
      let args = null
      if (this.newTemplate) {
        this.$store.dispatch('studyObjectives/addStudyObjectiveFromTemplate', {
          studyUid: this.selectedStudy.uid,
          form: {
            ...this.studyObjective,
            objective_template: this.newTemplate,
            objective_level: this.form.objective_level
          },
          parameters: this.parameters
        })
        action = 'studyObjectives/deleteStudyObjective'
        args = {
          studyUid: this.selectedStudy.uid,
          studyObjectiveUid: this.studyObjective.study_objective_uid
        }
      } else {
        const namePreview = await this.getStudyObjectiveNamePreview()
        const oldLevel = this.studyObjective.objective_level ? this.studyObjective.objective_level.term_uid : null
        const newLevel = this.form.objective_level ? this.form.objective_level.term_uid : null
        if (namePreview === this.studyObjective.objective.name && oldLevel === newLevel) {
          bus.$emit('notification', { msg: this.$t('_global.no_changes'), type: 'info' })
          this.close()
          return
        }
        args = {
          studyUid: this.selectedStudy.uid,
          studyObjectiveUid: this.studyObjective.study_objective_uid,
          form: {
            ...this.studyObjective,
            objective_level: this.form.objective_level
          }
        }
        args.form.parameters = this.parameters
        action = 'studyObjectives/updateStudyObjective'
      }
      this.$store.dispatch(action, args).then(() => {
        bus.$emit('notification', { msg: this.$t('StudyObjectiveEditForm.objective_updated') })
        this.close()
      }).catch((err) => {
        console.log(err)
        this.$refs.stepper.loading = false
      })
    }
  },
  mounted () {
    templateParameterTypes.getTypes().then(resp => {
      this.parameterTypes = resp.data
    })
  },
  watch: {
    studyObjective: {
      handler (newValue) {
        if (newValue) {
          this.apiEndpoint = objectives
          this.templateForm = { ...newValue.objective.objective_template }
          this.$set(this.form, 'objective_level', newValue.objective_level)
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
