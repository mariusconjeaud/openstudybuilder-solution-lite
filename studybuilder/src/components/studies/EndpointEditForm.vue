<template>
<study-selection-edit-form
  v-if="studyEndpoint"
  ref="form"
  :title="$t('StudyEndpointEditForm.title')"
  :study-selection="studyEndpoint"
  :template="template"
  :library-name="library.name"
  object-type="endpoint"
  :open="open"
  :get-object-from-selection="selection => selection.endpoint"
  @initForm="initForm"
  @submit="submit"
  @close="close"
  :with-unformatted-version="false"
  >
  <template v-slot:formFields="{ editTemplate, form }">
    <p class="mt-6 secondary--text text-h6">
      {{ $t('StudyEndpointEditForm.units_section') }}
    </p>
    <v-row>
      <v-col cols="11">
        <validation-provider
          v-slot="{ errors }"
          :rules="`requiredIfNotNA:${skipUnits}`"
          >
          <multiple-select
            v-model="form.endpoint_units.units"
            :label="$t('StudyEndpointEditForm.unit')"
            :items="units"
            :errors="errors"
            item-text="name"
            return-object
            :disabled="skipUnits || editTemplate"
            />
        </validation-provider>
      </v-col>
    </v-row>
    <p class="mt-6 secondary--text text-h6">
      {{ $t('StudyEndpointEditForm.timeframe_section') }}
    </p>
    <v-row>
      <v-col cols="11">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-autocomplete
            v-model="timeframeTemplate"
            :label="$t('StudyEndpointEditForm.timeframe')"
            :items="timeframeTemplates"
            item-text="name_plain"
            return-object
            :error-messages="errors"
            :disabled="editTemplate"
            />
        </validation-provider>
      </v-col>
    </v-row>
    <div class="mt-2" v-if="timeframeTemplate">
      <v-progress-circular
        v-if="loadingParameters"
        indeterminate
        color="secondary"
        />

      <template v-else>
        <parameter-value-selector
          ref="timeframeParamSelector"
          :value="timeframeTemplateParameters"
          :template="timeframeTemplate.name"
          color="white"
          stacked
          :disabled="editTemplate"
          :with-unformatted-version="false"
          />
      </template>
    </div>
    <p class="mt-6 secondary--text text-h6">
      {{ $t('StudyEndpointEditForm.unformatted_preview_section') }}
    </p>
    <v-card flat class="parameterBackground">
      <v-card-text>
        <template v-if="$refs.form && $refs.form.$refs.paramSelector">
          {{ $refs.form.$refs.paramSelector.namePlainPreview }} ({{ unitsDisplay(form.endpoint_units.units) }}).
        </template>
        <template v-if="$refs.timeframeParamSelector">
          {{ $t('StudyEndpointEditForm.timeframe') }}: {{ $refs.timeframeParamSelector.namePlainPreview }}.
        </template>
      </v-card-text>
    </v-card>
    <p class="mt-6 secondary--text text-h6">
      {{ $t('StudyEndpointEditForm.level_section') }}
    </p>
    <v-row>
      <v-col cols="6">
        <v-select
          v-model="form.endpoint_level"
          :label="$t('StudyEndpointForm.endpoint_level')"
          :items="endpointLevels"
          item-text="sponsor_preferred_name"
          return-object
          clearable
          :disabled="editTemplate"
          />
      </v-col>
      <v-col cols="6">
        <v-select
          v-model="form.endpoint_sublevel"
          :label="$t('StudyEndpointForm.endpoint_sub_level')"
          :items="endpointSubLevels"
          item-text="sponsor_preferred_name"
          return-object
          clearable
          :disabled="editTemplate"
          />
      </v-col>
    </v-row>
    <p class="mt-6 secondary--text text-h6">
      {{ $t('StudyEndpointEditForm.objective_section') }}
    </p>
    <v-row>
      <v-col cols="11">
        <v-autocomplete
          v-model="form.study_objective"
          :label="$t('StudyEndpointForm.objective')"
          :items="studyObjectives"
          item-text="objective.name_plain"
          return-object
          clearable
          :disabled="editTemplate"
          />
      </v-col>
    </v-row>
  </template>
</study-selection-edit-form>
</template>

<script>
import _isEmpty from 'lodash/isEmpty'
import { bus } from '@/main'
import constants from '@/constants/libraries'
import formUtils from '@/utils/forms'
import instances from '@/utils/instances'
import { mapGetters } from 'vuex'
import MultipleSelect from '@/components/tools/MultipleSelect'
import ParameterValueSelector from '@/components/tools/ParameterValueSelector'
import statuses from '@/constants/statuses'
import study from '@/api/study'
import StudySelectionEditForm from './StudySelectionEditForm'
import timeframes from '@/api/timeframes'
import timeframeTemplates from '@/api/timeframeTemplates'

export default {
  components: {
    MultipleSelect,
    ParameterValueSelector,
    StudySelectionEditForm
  },
  props: {
    studyEndpoint: Object,
    open: Boolean
  },
  computed: {
    ...mapGetters({
      endpointLevels: 'studiesGeneral/endpointLevels',
      endpointSubLevels: 'studiesGeneral/endpointSubLevels',
      selectedStudy: 'studiesGeneral/selectedStudy',
      units: 'studiesGeneral/allUnits'
    }),
    template () {
      return this.studyEndpoint.endpoint ? this.studyEndpoint.endpoint.endpoint_template : this.studyEndpoint.endpoint_template
    },
    library () {
      return this.studyEndpoint.endpoint ? this.studyEndpoint.endpoint.library : this.studyEndpoint.endpoint_template.library
    }
  },
  data () {
    return {
      loadingParameters: false,
      skipUnits: false,
      studyObjectives: [],
      timeframeTemplate: null,
      timeframeTemplates: [],
      timeframeTemplateParameters: []
    }
  },
  methods: {
    close () {
      this.timeframeTemplate = null
      this.$emit('close')
    },
    initForm (form) {
      this.$set(form, 'endpoint_units', this.studyEndpoint.endpoint_units)
      this.$set(form, 'endpoint_level', this.studyEndpoint.endpoint_level)
      this.$set(form, 'endpoint_sublevel', this.studyEndpoint.endpoint_sublevel)
      if (this.studyEndpoint.timeframe) {
        this.timeframeTemplate = this.studyEndpoint.timeframe.timeframe_template
        timeframes.getObjectParameters(this.studyEndpoint.timeframe.uid, { study_uid: this.selectedStudy.uid }).then(resp => {
          this.timeframeTemplateParameters = resp.data
          instances.loadParameterValues(this.studyEndpoint.timeframe.parameter_terms, this.timeframeTemplateParameters)
        })
      }
      if (this.studyEndpoint.study_objective) {
        this.$set(form, 'study_objective', this.studyEndpoint.study_objective)
      }
      this.originalForm = JSON.parse(JSON.stringify(form))
    },
    async getStudyEndpointNamePreview (parameters) {
      const endpointData = {
        endpoint_template_uid: this.studyEndpoint.endpoint.endpoint_template.uid,
        parameter_terms: await instances.formatParameterValues(parameters),
        library_name: this.studyEndpoint.endpoint.library.name
      }
      const resp = await study.getStudyEndpointPreview(this.selectedStudy.uid, { endpoint_data: endpointData })
      return resp.data.endpoint.name
    },
    async getTimeframeNamePreview (parameters) {
      const data = {
        timeframe_template_uid: this.studyEndpoint.timeframe.timeframe_template.uid,
        parameter_terms: await instances.formatParameterValues(parameters),
        library_name: this.studyEndpoint.timeframe.library.name
      }
      const resp = await timeframes.getPreview(data)
      return resp.data.name
    },
    getTimeframeTemplates () {
      const params = {
        filters: { 'library.name': { v: [constants.LIBRARY_SPONSOR] } },
        page_size: 0,
        status: statuses.FINAL
      }
      timeframeTemplates.get(params).then(resp => {
        this.timeframeTemplates = resp.data.items
      })
    },
    unitsDisplay (units) {
      let result = ''
      if (units) {
        units.forEach(unit => {
          result += this.units.find(u => u.uid === unit.uid).name + ', '
        })
      }
      return result.slice(0, -2)
    },
    async submit (newTemplate, form, parameters) {
      const data = formUtils.getDifferences(this.originalForm, form)

      if (newTemplate) {
        data.endpoint_template = newTemplate
        data.endpoint_parameters = parameters
      } else if (!this.studyEndpoint.endpoint) {
        data.endpoint_template = this.studyEndpoint.endpoint_template
        data.endpoint_parameters = parameters
      } else {
        const namePreview = await this.getStudyEndpointNamePreview(parameters)
        if (namePreview !== this.studyEndpoint.endpoint.name) {
          data.endpoint_template = this.studyEndpoint.endpoint.endpoint_template
          // Hotfix because we don't have the template library here...
          data.endpoint_template.library = {
            name: constants.LIBRARY_SPONSOR
          }
          data.endpoint_parameters = parameters
        }
      }
      if (!this.studyEndpoint.timeframe) {
        if (this.timeframeTemplate) {
          data.timeframe_template = this.timeframeTemplate
          data.timeframe_parameters = this.timeframeTemplateParameters
        }
      } else {
        const namePreview = await this.getTimeframeNamePreview(this.timeframeTemplateParameters)
        if (namePreview !== this.studyEndpoint.timeframe.name) {
          data.timeframe_template = this.timeframeTemplate
          // Hotfix because we don't have the template library here...
          data.timeframe_template.library = {
            name: constants.LIBRARY_SPONSOR
          }
          data.timeframe_parameters = this.timeframeTemplateParameters
        }
      }
      if (_isEmpty(data)) {
        bus.$emit('notification', { msg: this.$t('_global.no_changes'), type: 'info' })
        this.$refs.form.close()
        return
      }
      const args = {
        studyUid: this.selectedStudy.uid,
        studyEndpointUid: this.studyEndpoint.study_endpoint_uid,
        form: data
      }
      this.$store.dispatch('studyEndpoints/updateStudyEndpoint', args).then(() => {
        bus.$emit('notification', { msg: this.$t('StudyEndpointEditForm.endpoint_updated') })
        this.$emit('updated')
        this.$refs.form.close()
      }).catch((err) => {
        console.log(err)
      })
    }
  },
  mounted () {
    this.getTimeframeTemplates()
    study.getStudyObjectives(this.selectedStudy.uid).then(resp => {
      this.studyObjectives = resp.data.items
    })
  },
  watch: {
    timeframeTemplate (value) {
      if (!value) {
        return
      }
      if (this.studyEndpoint.timeframe && this.studyEndpoint.timeframe.timeframe_template.uid === value.uid) {
        return
      }
      this.loadingParameters = true
      timeframeTemplates.getParameters(value.uid, { study_uid: this.selectedStudy.uid }).then(resp => {
        this.timeframeTemplateParameters = resp.data
        this.loadingParameters = false
      })
    }
  }
}
</script>
