<template>
<simple-form-dialog
  ref="form"
  :title="$t('StudyPopulationForm.title')"
  :help-items="helpItems"
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
            name="TherapeuticArea"
            rules=""
            >
            <multiple-select
              v-model="form.therapeutic_areas_codes"
              :data-cy="$t('StudyPopulationForm.therapeuticarea')"
              :label="$t('StudyPopulationForm.therapeuticarea')"
              :items="snomedTerms"
              item-text="name"
              item-value="term_uid"
              return-object
              :errors="errors"
              />
          </validation-provider>
        </v-col>
      </v-row>
      <not-applicable-field
        :clean-function="setNullValueStudyDisease"
        :checked="form.disease_conditions_or_indications_null_value_code ? true : false"
        >
        <template v-slot:mainField="{ notApplicable }">
          <multiple-select
            :data-cy="$t('StudyPopulationForm.disease_condition')"
            :label="$t('StudyPopulationForm.disease_condition')"
            :disabled="notApplicable"
            v-model="form.disease_conditions_or_indications_codes"
            :items="snomedTerms"
            item-value="term_uid"
            item-text="name"
            return-object
            />
        </template>
      </not-applicable-field>
      <not-applicable-field
        :label=" $t('StudyPopulationForm.stable_disease_min_duration')"
        :clean-function="setNullValueDiseaseDuration"
        :checked="form.stable_disease_minimum_duration_null_value_code ? true : false"
        >
        <template v-slot:mainField="{ notApplicable }">
          <duration-field
            data-cy="stable-disease-min-duration"
            class="unit-select"
            v-model="form.stable_disease_minimum_duration"
            :disabled="notApplicable"
            :max="undefined"
            />
        </template>
      </not-applicable-field>
      <validation-provider
        v-slot="{ errors }"
        >
        <v-row class="pr-4">
          <v-col cols="11">
            <multiple-select
              :data-cy="$t('StudyPopulationForm.diagnosis_group')"
              v-model="form.diagnosis_groups_codes"
              :label="$t('StudyPopulationForm.diagnosis_group')"
              :items="snomedTerms"
              item-value="term_uid"
              item-text="name"
              :errors="errors"
              return-object
              />
          </v-col>
        </v-row>
      </validation-provider>
      <not-applicable-field
        :clean-function="setNullValueRelapseCriteria"
        :checked="form.relapse_criteria_null_value_code ? true : false"
        >
        <template v-slot:mainField="{ notApplicable }">
          <v-text-field
            :data-cy="$t('StudyPopulationForm.relapse_criteria')"
            v-model="form.relapse_criteria"
            :label="$t('StudyPopulationForm.relapse_criteria')"
            class="pt-0 my-0"
            :disabled="notApplicable"
            />
        </template>
      </not-applicable-field>
      <v-row>
        <v-col cols="4">
          <v-text-field
            :data-cy="$t('StudyPopulationForm.number_of_expected_subjects')"
            v-model="form.number_of_expected_subjects"
            :label="$t('StudyPopulationForm.number_of_expected_subjects')"
            :hint="$t('StudyPopulationForm.number_of_expected_subjects_hint')"
            class="pt-0 my-0"
            type="number"
            />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="4">
          <validation-provider
            v-slot="{ errors }"
            name="HealthySubjects"
            rules=""
            >
            <yes-no-field
              :data-cy="$t('StudyPopulationForm.healthy_subjects')"
              v-model="form.healthy_subject_indicator"
              :error-messages="errors"
              :label="$t('StudyPopulationForm.healthy_subjects')"
              />
          </validation-provider>
        </v-col>
        <v-col cols="5">
          <validation-provider
            v-slot="{ errors }"
            name="RareDiseaseIndicator"
            rules=""
            >
            <yes-no-field
              :data-cy="$t('StudyPopulationForm.rare_disease_indicator')"
              v-model="form.rare_disease_indicator"
              :error-messages="errors"
              :label="$t('StudyPopulationForm.rare_disease_indicator')"
              />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row class="pr-4">
        <v-col cols="11">
          <validation-provider
            v-slot="{ errors }"
            >
            <v-select
              :data-cy="$t('StudyPopulationForm.sex_of_study_participants')"
              v-model="form.sex_of_participants_code"
              :label="$t('StudyPopulationForm.sex_of_study_participants')"
              :items="sexOfParticipants"
              item-value="term_uid"
              item-text="sponsor_preferred_name"
              return-object
              dense
              :errors="errors"
              clearable
              hide-details="auto"
              />
          </validation-provider>
        </v-col>
      </v-row>
      <div class="mt-10">
        <label class="v-label">
          {{ $t('StudyPopulationForm.planned_min_max_age') }}
        </label>
      </div>
      <not-applicable-field
        :na-label="$t('StudyPopulationForm.pinf')"
        :clean-function="setPositiveInfinity"
        :checked="form.planned_maximum_age_of_subjects_null_value_code ? true : false"
        >
        <template v-slot:mainField="{ notApplicable }">
          <v-row>
            <v-col cols="6">
              <validation-provider
                v-slot="{ errors }"
                name="PlannedMinAge"
                rules=""
                >
                <duration-field
                  data-cy="planned-minimum-age"
                  v-model="form.planned_minimum_age_of_subjects"
                  :errors="errors"
                  numeric-field-name="duration_value"
                  unit-field-name="duration_unit_code"
                  :hint="$t('StudyPopulationForm.planned_min_age')"
                  />
              </validation-provider>
            </v-col>
            <v-col cols="6">
              <validation-provider
                v-slot="{ errors }"
                name="PlannedMaxAge"
                rules=""
                >
                <duration-field
                  data-cy="planned-maximum-age"
                  v-model="form.planned_maximum_age_of_subjects"
                  :errors="errors"
                  numeric-field-name="duration_value"
                  unit-field-name="duration_unit_code"
                  :disabled="notApplicable"
                  :hint="$t('StudyPopulationForm.planned_max_age')"
                  />
              </validation-provider>
            </v-col>
          </v-row>
        </template>
      </not-applicable-field>
      <v-row>
        <v-col cols="4">
          <validation-provider
            v-slot="{ errors }"
            name="pediatric_study_indicator"
            rules=""
            >
            <yes-no-field
              :data-cy="$t('StudyPopulationForm.pediatric_study_indicator')"
              v-model="form.pediatric_study_indicator"
              :error-messages="errors"
              :label="$t('StudyPopulationForm.pediatric_study_indicator')"
              />
          </validation-provider>
        </v-col>
        <v-col cols="5">
          <validation-provider
            v-slot="{ errors }"
            name="pediatric_investigation_plan_indicator"
            rules=""
            >
            <yes-no-field
              :data-cy="$t('StudyPopulationForm.pediatric_investigation_plan_indicator')"
              v-model="form.pediatric_investigation_plan_indicator"
              :error-messages="errors"
              :label="$t('StudyPopulationForm.pediatric_investigation_plan_indicator')"
              />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="9">
          <validation-provider
            v-slot="{ errors }"
            name="pediatric_postmarket_study_indicator"
            rules=""
            >
            <yes-no-field
              :data-cy="$t('StudyPopulationForm.pediatric_postmarket_study_indicator')"
              v-model="form.pediatric_postmarket_study_indicator"
              :error-messages="errors"
              :label="$t('StudyPopulationForm.pediatric_postmarket_study_indicator')"
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
    MultipleSelect,
    NotApplicableField,
    SimpleFormDialog,
    YesNoField
  },
  props: {
    metadata: Object,
    open: Boolean
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      snomedTerms: 'studiesGeneral/snomedTerms',
      sexOfParticipants: 'studiesGeneral/sexOfParticipants',
      units: 'studiesGeneral/units',
      nullValues: 'studiesGeneral/nullValues'
    })
  },
  data () {
    return {
      form: {
        planned_minimum_age_of_subjects: {},
        planned_maximum_age_of_subjects: {},
        stable_disease_minimum_duration: {}
      },
      helpItems: [
        'StudyPopulationForm.therapeuticarea',
        'StudyPopulationForm.disease_condition',
        'StudyPopulationForm.diagnosis_group',
        'StudyPopulationForm.rare_disease_indicator',
        'StudyPopulationForm.healthy_subjects',
        'StudyPopulationForm.planned_min_max_age',
        'StudyPopulationForm.pediatric_study_indicator',
        'StudyPopulationForm.pediatric_postmarket_study_indicator',
        'StudyPopulationForm.stable_disease_min_duration',
        'StudyPopulationForm.relapse_criteria',
        'StudyPopulationForm.number_of_expected_subjects',
        'StudyPopulationForm.sex_of_study_participants'
      ],
      minimumDurationCheckbox: false,
      data: this.metadata
    }
  },
  mounted () {
    this.$store.dispatch('studiesGeneral/fetchNullValues')
  },
  methods: {
    setNullValueStudyDisease () {
      this.$set(this.form, 'disease_conditions_or_indications_codes', [])
      if (this.form.disease_conditions_or_indications_null_value_code) {
        this.$set(this.form, 'disease_conditions_or_indications_null_value_code', null)
      } else {
        this.$set(this.form, 'disease_conditions_or_indications_null_value_code', { term_uid: this.$t('_global.na_uid'), name: this.$t('_global.not_applicable_full_name') })
      }
    },
    setNullValueDiseaseDuration () {
      this.$set(this.form, 'stable_disease_minimum_duration', {})
      if (this.form.stable_disease_minimum_duration_null_value_code) {
        this.$set(this.form, 'stable_disease_minimum_duration_null_value_code', null)
      } else {
        this.$set(this.form, 'stable_disease_minimum_duration_null_value_code', { term_uid: this.$t('_global.na_uid'), name: this.$t('_global.not_applicable_full_name') })
      }
    },
    setNullValueRelapseCriteria () {
      this.$set(this.form, 'relapse_criteria', '')
      if (this.form.relapse_criteria_null_value_code) {
        this.$set(this.form, 'relapse_criteria_null_value_code', null)
      } else {
        this.$set(this.form, 'relapse_criteria_null_value_code', { term_uid: this.$t('_global.na_uid'), name: this.$t('_global.not_applicable_full_name') })
      }
    },
    setNullValueNumberOfExpectedSubjects () {
      this.$set(this.form, 'number_of_expected_subjects', '')
      if (this.form.number_of_expected_subjects_null_value_code) {
        this.$set(this.form, 'number_of_expected_subjects_null_value_code', null)
      } else {
        this.$set(this.form, 'number_of_expected_subjects_null_value_code', { term_uid: this.$t('_global.na_uid'), name: this.$t('_global.not_applicable_full_name') })
      }
    },
    setPositiveInfinity () {
      this.$set(this.form, 'planned_maximum_age_of_subjects', {})
      if (this.form.planned_maximum_age_of_subjects_null_value_code) {
        this.$set(this.form, 'planned_maximum_age_of_subjects_null_value_code', null)
      } else {
        this.$set(this.form, 'planned_maximum_age_of_subjects_null_value_code', { term_uid: this.nullValues.find(el => el.sponsor_preferred_name === 'Positive infinity').term_uid, name: this.$t('_global.positive_infinity_full_name') })
      }
    },
    close () {
      this.$emit('close')
      this.$refs.observer.reset()
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
    prepareRequestPayload () {
      const data = JSON.parse(JSON.stringify(this.form))
      if (Object.keys(data.planned_minimum_age_of_subjects).length === 0 || !data.planned_minimum_age_of_subjects.duration_value) {
        data.planned_minimum_age_of_subjects = null
      }
      if (Object.keys(data.planned_maximum_age_of_subjects).length === 0 || !data.planned_maximum_age_of_subjects.duration_value) {
        data.planned_maximum_age_of_subjects = null
      }
      if (Object.keys(data.stable_disease_minimum_duration).length === 0 || !data.stable_disease_minimum_duration.duration_value) {
        data.stable_disease_minimum_duration = null
      }
      if (!data.number_of_expected_subjects) {
        data.number_of_expected_subjects = null
      }
      data.sex_of_participants_code = this.getTermPayload('sex_of_participants_code')
      data.therapeutic_areas_codes = this.getTermsPayload('therapeutic_areas_codes')
      data.disease_conditions_or_indications_codes = this.getTermsPayload('disease_conditions_or_indications_codes')
      data.diagnosis_groups_codes = this.getTermsPayload('diagnosis_groups_codes')
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
        await this.$store.dispatch('manageStudies/editStudyPopulation', [this.selectedStudy.uid, data])
        this.$emit('updated', data)
        bus.$emit('notification', { msg: this.$t('StudyPopulationForm.update_success') })
        this.close()
      } finally {
        this.$refs.form.working = false
      }
    }
  },
  watch: {
    minimumDurationCheckbox: function () {
      this.form.stable_disease_minimum_duration = {}
    },
    data: {
      handler: function (value) {
        this.form = JSON.parse(JSON.stringify(value))
        if (!this.form.planned_minimum_age_of_subjects) {
          this.form.planned_minimum_age_of_subjects = {}
        }
        if (!this.form.planned_maximum_age_of_subjects) {
          this.form.planned_maximum_age_of_subjects = {}
        }
        if (!this.form.stable_disease_minimum_duration) {
          this.form.stable_disease_minimum_duration = {}
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
