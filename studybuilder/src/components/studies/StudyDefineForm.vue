<template>
<simple-form-dialog
  ref="form"
  :title="title"
  :help-items="helpItems"
  :help-text="$t('_help.StudyDefineForm.general')"
  @close="cancel"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
      <v-row class="pr-4">
        <v-col cols="11">
          <validation-provider
            v-slot="{ errors }"
            name="StudyType"
            >
            <v-autocomplete
              data-cy="study-type"
              v-model="form.study_type_code"
              :label="$t('StudyDefineForm.studytype')"
              :items="studyTypes"
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
      <v-row class="pr-4">
        <v-col cols="11">
          <validation-provider
            v-slot="{ errors }"
            name="TrialTypes"
            >
            <multiple-select
              data-cy="trial-type"
              v-model="form.trial_type_codes"
              :label="$t('StudyDefineForm.trialtype')"
              :items="trialTypes"
              item-text="sponsor_preferred_name"
              item-value="term_uid"
              return-object
              :errors="errors"
              />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row class="pr-4">
        <v-col cols="11">
          <validation-provider
            v-slot="{ errors }"
            name="TrialPhase"
            >
            <v-select
              data-cy="study-phase-classification"
              v-model="form.trial_phase_code"
              :label="$t('StudyDefineForm.trialphase')"
              :items="trialPhases"
              item-text="sponsor_preferred_name_sentence_case"
              item-value="term_uid"
              return-object
              :error-messages="errors"
              dense
              clearable
              ></v-select>
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="5">
          <validation-provider
            v-slot="{ errors }"
            name="ExtensionTrial"
            rules="oneselected:@ExtensionTrialNullFlavor"
            >
            <yes-no-field
              data-cy="extension-study"
              v-model="form.is_extension_trial"
              :error-messages="errors"
              :label="$t('StudyDefineForm.extensiontrial')"
              />
          </validation-provider>
        </v-col>
        <v-col cols="5">
          <validation-provider
            v-slot="{ errors }"
            name="AdaptiveDesign"
            >
            <yes-no-field
              data-cy="adaptive-design"
              v-model="form.is_adaptive_design"
              :error-messages="errors"
              :label="$t('StudyDefineForm.adaptivedesign')"
              />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row class="pr-4 mb-4">
        <v-col cols="11">
          <validation-provider
            v-slot="{ errors }"
            name="StudyStopRules"
            >
            <v-text-field
              data-cy="stop-rule"
              v-model="form.study_stop_rules"
              :label="$t('StudyDefineForm.studystoprule')"
              :error-messages="errors"
              dense
              clearable
              :disabled="stopRulesNone"
              ></v-text-field>
          </validation-provider>
        </v-col>
        <v-col cols="1">
          <v-checkbox
            v-model="stopRulesNone"
            :label="$t('StudyDefineForm.none')"
            hide-details
            @change="updateStopRules"
            />
        </v-col>
      </v-row>
      <not-applicable-field
        :label="$t('StudyDefineForm.confirmed_resp_min_duration')"
        data-cy="confirmed-resp-min-dur-field"
        :clean-function="setNullValueConfirmedDuration"
        :checked="form.confirmed_response_minimum_duration_null_value_code ? true : false"
        >
        <template v-slot:mainField="{ notApplicable }">
          <duration-field
            data-cy="confirmed-resp-min-dur"
            v-model="form.confirmed_response_minimum_duration"
            numericFieldName="duration_value"
            unitFieldName="duration_unit_code"
            :disabled="notApplicable"
            />
        </template>
      </not-applicable-field>
      <v-row class="mt-4">
        <v-col cols="9">
          <validation-provider
            v-slot="{ errors }"
            name="PostAuthIndicator"
            >
            <yes-no-field
              data-cy="post-auth-safety-indicator"
              v-model="form.post_auth_indicator"
              :error-messages="errors"
              :label="$t('StudyDefineForm.post_auth_safety_indicator')"
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
import { bus } from '@/main'
import { mapGetters } from 'vuex'
import { studyMetadataFormMixin } from '@/mixins/studyMetadataForm'
import DurationField from '@/components/tools/DurationField'
import MultipleSelect from '@/components/tools/MultipleSelect'
import NotApplicableField from '@/components/tools/NotApplicableField'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import studyConstants from '@/constants/study'
import YesNoField from '@/components/tools/YesNoField'

export default {
  mixins: [studyMetadataFormMixin],
  components: {
    DurationField,
    MultipleSelect,
    NotApplicableField,
    SimpleFormDialog,
    YesNoField
  },
  props: {
    metadata: Object,
    open: Boolean
  },
  data () {
    return {
      form: {},
      helpItems: [
        'StudyDefineForm.studytype',
        'StudyDefineForm.studyintent',
        'StudyDefineForm.trialtype',
        'StudyDefineForm.trialphase',
        'StudyDefineForm.extensiontrial',
        'StudyDefineForm.adaptivedesign',
        'StudyDefineForm.studystoprule',
        'StudyDefineForm.confirmed_resp_min_duration',
        'StudyDefineForm.post_auth_safety_indicator'
      ],
      data: this.metadata,
      stopRulesNone: false
    }
  },
  computed: {
    title () {
      return this.$t('StudyDefineForm.title')
    },
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      studyTypes: 'studiesGeneral/studyTypes',
      trialIntentTypes: 'studiesGeneral/trialIntentTypes',
      trialTypes: 'studiesGeneral/trialTypes',
      trialPhases: 'studiesGeneral/trialPhases'
    })
  },
  methods: {
    setNullValueConfirmedDuration () {
      this.$set(this.form, 'confirmed_response_minimum_duration', {})
      if (this.form.confirmed_response_minimum_duration_null_value_code) {
        this.$set(this.form, 'confirmed_response_minimum_duration_null_value_code', null)
      } else {
        this.$set(this.form, 'confirmed_response_minimum_duration_null_value_code', { term_uid: this.$t('_global.na_uid'), name: this.$t('_global.not_applicable_full_name') })
      }
    },
    close () {
      this.$emit('close')
      this.$refs.observer.reset()
    },
    prepareRequestPayload () {
      const data = { ...this.form }
      if (!data.confirmed_response_minimum_duration.duration_value) {
        data.confirmed_response_minimum_duration = null
      }
      data.study_type_code = this.getTermPayload('study_type_code')
      data.trial_intent_types_codes = this.getTermsPayload('trial_intent_types_codes')
      data.trial_type_codes = this.getTermsPayload('trial_type_codes')
      data.trial_phase_code = this.getTermPayload('trial_phase_code')
      if (this.stopRulesNone) {
        data.studyStopRules = studyConstants.STOP_RULE_NONE
      }
      return data
    },
    async cancel () {
      if (_isEqual(this.metadata, this.prepareRequestPayload())) {
        this.close()
        return
      }
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (await this.$refs.form.confirm(this.$t('_global.cancel_changes'), options)) {
        this.data = {}
        this.data = this.metadata
        this.close()
      }
    },
    async submit () {
      const valid = await this.$refs.observer.validate()
      if (!valid) {
        return
      }
      this.$refs.form.working = true
      const data = this.prepareRequestPayload()
      try {
        await this.$store.dispatch('manageStudies/editStudyType', [this.selectedStudy.uid, data])
        this.$emit('updated', data)
        bus.$emit('notification', { msg: this.$t('StudyDefineForm.update_success') })
        this.close()
      } finally {
        this.$refs.form.working = false
      }
    },
    updateStopRules (value) {
      if (value) {
        this.$set(this.form, 'study_stop_rules', null)
      }
    }
  },
  watch: {
    data: {
      handler: function (value) {
        this.form = JSON.parse(JSON.stringify(value))
        if (!this.form.confirmed_response_minimum_duration) {
          this.form.confirmed_response_minimum_duration = {}
        }
        if (!this.metadata.confirmed_response_minimum_duration) {
          this.metadata.confirmed_response_minimum_duration = null
        }
        if (this.metadata.study_stop_rules === studyConstants.STOP_RULE_NONE) {
          this.stopRulesNone = true
        }
      },
      immediate: true
    },
    metadata (value) {
      this.data = value
    }
  }
}
</script>
