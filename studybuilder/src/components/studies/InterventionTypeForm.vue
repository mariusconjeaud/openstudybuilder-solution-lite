<template>
<simple-form-dialog
  ref="form"
  :title="$t('StudyInterventionTypeForm.title')"
  :help-items="helpItems"
  :help-text="$t('_help.StudyInterventionTypeForm.general')"
  @close="cancel"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
      <v-row>
        <v-col cols="11">
          <validation-provider
            v-slot="{ errors }"
            name="InterventionType"
            >
            <v-autocomplete
              :data-cy="$t('StudyInterventionTypeForm.intervention_type')"
              v-model="form.intervention_type_code"
              :label="$t('StudyInterventionTypeForm.intervention_type')"
              :items="interventionTypes"
              item-text="sponsor_preferred_name"
              item-value="term_uid"
              return-object
              :error-messages="errors"
              dense
              clearable
              ></v-autocomplete>
          </validation-provider>
        </v-col>
      </v-row>
      <not-applicable-field
        :clean-function="setNullValueTrialIntentTypesCodes"
        :checked="form.trial_intent_types_null_value_code ? true : false"
        >
        <template v-slot:mainField="{ notApplicable }">
          <multiple-select
            :data-cy="$t('StudyDefineForm.studyintent')"
            v-model="form.trial_intent_types_codes"
            :label="$t('StudyDefineForm.studyintent')"
            :items="trialIntentTypes"
            item-text="sponsor_preferred_name"
            item-value="term_uid"
            return-object
            :disabled="notApplicable"
            dense
            clearable
            />
        </template>
      </not-applicable-field>
      <v-row>
        <v-col cols="11">
          <validation-provider
            v-slot="{ errors }"
            name="ControlType"
            >
            <v-autocomplete
              :data-cy="$t('StudyInterventionTypeForm.control_type')"
              v-model="form.control_type_code"
              :label="$t('StudyInterventionTypeForm.control_type')"
              :items="controlTypes"
              item-text="sponsor_preferred_name"
              item-value="term_uid"
              return-object
              :error-messages="errors"
              dense
              clearable
              ></v-autocomplete>
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="11">
          <validation-provider
            v-slot="{ errors }"
            name="InterventionModel"
            >
            <v-autocomplete
              :data-cy="$t('StudyInterventionTypeForm.intervention_model')"
              v-model="form.intervention_model_code"
              :label="$t('StudyInterventionTypeForm.intervention_model')"
              :items="interventionModels"
              item-text="sponsor_preferred_name"
              item-value="term_uid"
              return-object
              :error-messages="errors"
              dense
              clearable
              ></v-autocomplete>
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="5">
          <validation-provider
            v-slot="{ errors }"
            name="Randomised"
            >
            <yes-no-field
              :data-cy="$t('StudyInterventionTypeForm.randomised')"
              v-model="form.is_trial_randomised"
              :error-messages="errors"
              :label="$t('StudyInterventionTypeForm.randomised')"
              />
          </validation-provider>
        </v-col>
        <v-col cols="5">
          <validation-provider
            v-slot="{ errors }"
            name="AddedToExistingTreatments"
            >
            <yes-no-field
              :data-cy="$t('StudyInterventionTypeForm.added_to_et')"
              v-model="form.add_on_to_existing_treatments"
              :error-messages="errors"
              :label="$t('StudyInterventionTypeForm.added_to_et')"
              />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="11">
          <validation-provider
            v-slot="{ errors }"
            name="BlindingSchema"
            >
            <v-autocomplete
              :data-cy="$t('StudyInterventionTypeForm.blinding_schema')"
              v-model="form.trial_blinding_schema_code"
              :label="$t('StudyInterventionTypeForm.blinding_schema')"
              :items="trialBlindingSchemas"
              item-text="sponsor_preferred_name"
              item-value="term_uid"
              return-object
              :error-messages="errors"
              dense
              clearable
              ></v-autocomplete>
          </validation-provider>
        </v-col>
      </v-row>
      <not-applicable-field
        :clean-function="setNullValueStratificationFactor"
        :checked="form.stratification_factor_null_value_code ? true : false"
        >
        <template v-slot:mainField="{ notApplicable }">
          <v-text-field
            :data-cy="$t('StudyInterventionTypeForm.strfactor')"
            :label="$t('StudyInterventionTypeForm.strfactor')"
            :disabled="notApplicable"
            v-model="form.stratification_factor"
            dense
            clearable
            ></v-text-field>
        </template>
      </not-applicable-field>
      <v-row>
        <v-col cols="10">
          <label class="v-label theme--light">{{ $t('StudyInterventionTypeForm.planned_st_length') }}</label>
          <validation-provider
            v-slot="{ errors }"
            name="planned_study_length"
            >
            <duration-field
              data-cy="planned-study-length"
              v-model="form.planned_study_length"
              :errors="errors"
              numericFieldName="duration_value"
              unitFieldName="duration_unit_code"
              :max="1000"
              />
          </validation-provider>
        </v-col>
      </v-row>
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>
import _isEqual from 'lodash/isEqual'
import { mapGetters } from 'vuex'
import { bus } from '@/main'
import { studyMetadataFormMixin } from '@/mixins/studyMetadataForm'
import DurationField from '@/components/tools/DurationField'
import MultipleSelect from '@/components/tools/MultipleSelect'
import NotApplicableField from '@/components/tools/NotApplicableField'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import YesNoField from '@/components/tools/YesNoField'

export default {
  mixins: [studyMetadataFormMixin],
  components: {
    DurationField,
    NotApplicableField,
    SimpleFormDialog,
    YesNoField,
    MultipleSelect
  },
  props: {
    metadata: Object,
    open: Boolean
  },
  computed: {
    ...mapGetters({
      controlTypes: 'studiesGeneral/controlTypes',
      interventionModels: 'studiesGeneral/interventionModels',
      selectedStudy: 'studiesGeneral/selectedStudy',
      trialBlindingSchemas: 'studiesGeneral/trialBlindingSchemas',
      interventionTypes: 'studiesGeneral/interventionTypes',
      trialIntentTypes: 'studiesGeneral/trialIntentTypes'
    })
  },
  data () {
    return {
      form: {},
      helpItems: [
        'StudyInterventionTypeForm.intervention_type',
        'StudyInterventionTypeForm.study_intent_type',
        'StudyInterventionTypeForm.added_to_et',
        'StudyInterventionTypeForm.control_type',
        'StudyInterventionTypeForm.intervention_model',
        'StudyInterventionTypeForm.randomised',
        'StudyInterventionTypeForm.strfactor',
        'StudyInterventionTypeForm.blinding_schema',
        'StudyInterventionTypeForm.planned_st_length'
      ],
      data: this.metadata
    }
  },
  methods: {
    setNullValueTrialIntentTypesCodes () {
      this.$set(this.form, 'trial_intent_types_codes', [])
      if (this.form.trial_intent_types_null_value_code) {
        this.$set(this.form, 'trial_intent_types_null_value_code', null)
      } else {
        this.$set(this.form, 'trial_intent_types_null_value_code', { term_uid: this.$t('_global.na_uid'), name: this.$t('_global.not_applicable_full_name') })
      }
    },
    setNullValueStratificationFactor () {
      this.$set(this.form, 'stratification_factor', '')
      if (this.form.stratification_factor_null_value_code) {
        this.$set(this.form, 'stratification_factor_null_value_code', null)
      } else {
        this.$set(this.form, 'stratification_factor_null_value_code', { term_uid: this.$t('_global.na_uid'), name: this.$t('_global.not_applicable_full_name') })
      }
    },
    close () {
      this.$emit('close')
      this.$store.commit('form/CLEAR_FORM')
      this.$refs.observer.reset()
    },
    async cancel () {
      if (this.$store.getters['form/form'] === '' || _isEqual(this.$store.getters['form/form'], JSON.stringify(this.form))) {
        this.close()
      } else {
        const options = {
          type: 'warning',
          cancelLabel: this.$t('_global.cancel'),
          agreeLabel: this.$t('_global.continue')
        }
        if (await this.$refs.form.confirm(this.$t('_global.cancel_changes'), options)) {
          this.close()
        }
      }
    },
    prepareRequestPayload () {
      const data = JSON.parse(JSON.stringify(this.form))
      if (data.planned_study_length.duration_value === undefined) {
        data.planned_study_length = null
      }
      data.control_type_code = this.getTermPayload('control_type_code')
      data.intervention_model_code = this.getTermPayload('intervention_model_code')
      data.trial_blinding_schema_code = this.getTermPayload('trial_blinding_schema_code')
      data.intervention_type_code = this.getTermPayload('intervention_type_code')
      data.trial_intent_types_codes = this.getTermsPayload('trial_intent_types_codes')
      return data
    },
    async submit () {
      const valid = await this.$refs.observer.validate()
      if (!valid) {
        return
      }
      const data = this.prepareRequestPayload()
      this.$refs.form.working = true
      try {
        await this.$store.dispatch('manageStudies/updateStudyIntervention', [this.selectedStudy.uid, data])
        this.$emit('updated', data)
        bus.$emit('notification', { msg: this.$t('StudyInterventionTypeForm.update_success') })
        this.close()
      } finally {
        this.$refs.form.working = false
      }
    }
  },
  watch: {
    data: {
      handler: function (value) {
        this.form = JSON.parse(JSON.stringify(value))
        if (!this.form.planned_study_length) {
          this.form.planned_study_length = {}
        }
        if (!this.metadata.planned_study_length) {
          this.metadata.planned_study_length = null
        }
        this.$store.commit('form/SET_FORM', this.form)
      },
      immediate: true
    },
    metadata (value) {
      this.data = value
    }
  }
}
</script>
