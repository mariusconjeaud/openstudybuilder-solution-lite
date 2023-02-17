<template>
<horizontal-stepper-form
  ref="stepper"
  :title="title"
  :steps="steps"
  @close="close"
  @save="submit"
  :form-observer-getter="getObserver"
  :editable="studyCompound !== undefined && studyCompound !== null"
  :helpItems="helpItems"
  :edit-data="form"
  >
  <template v-slot:step.type_of_treatment="{ step }">
    <validation-observer :ref="`observer_${step}`">
      <not-applicable-field
        ref="naField"
        :clean-function="cleanTypeOfTreatment"
        :disabled="typeOfTreatment_uidNADisabled"
        :checked="studyCompound && !studyCompound.compound"
        >
        <template v-slot:mainField="{ notApplicable }">
          <validation-provider
            v-slot="{ errors }"
            name="activity"
            :rules="`requiredIfNotNA:${notApplicable}`"
            >
            <v-autocomplete
              v-model="form.type_of_treatment"
              :data-cy="$t('StudyCompoundForm.type_of_treatment')"
              :label="$t('StudyCompoundForm.type_of_treatment')"
              :items="typeOfTreatments"
              item-text="sponsor_preferred_name"
              item-value="term_uid"
              return-object
              :error-messages="errors"
              dense
              clearable
              class="required"
              />
          </validation-provider>
        </template>
      </not-applicable-field>
    </validation-observer>
  </template>
  <template v-slot:step.compoundAlias="{ step }">
    <validation-observer :ref="`observer_${step}`">
      <v-row>
        <v-col cols="6">
          <validation-provider
            rules="required"
            v-slot="{ errors }"
            >
            <v-autocomplete
              v-model="form.compoundSimple"
              :label="$t('StudyCompoundForm.compound')"
              :items="compounds"
              item-text="name"
              item-value="uid"
              return-object
              :error-messages="errors"
              dense
              clearable
              class="required"
              />
          </validation-provider>
        </v-col>
        <v-col cols="6">
          <validation-provider
            rules="required"
            v-slot="{ errors }"
            >
            <v-autocomplete
              v-model="form.compound_alias"
              :label="$t('StudyCompoundForm.compound_alias')"
              :items="compoundAliases"
              item-text="name"
              item-value="uid"
              return-object
              :error-messages="errors"
              dense
              clearable
              class="required"
              />
          </validation-provider>
        </v-col>
      </v-row>
      <template v-if="form.compound">
        <v-row>
          <v-col cols="6">
            <yes-no-field
              v-model="form.compound.is_sponsor_compound"
              :label="$t('StudyCompoundForm.sponsor_compound')"
              row
              disabled
              hide-details
              />
          </v-col>
          <v-col cols="6" v-if="form.compound_alias">
            <yes-no-field
              v-model="form.compound_alias.is_preferred_synonym"
              :label="$t('StudyCompoundForm.is_preferred_synonym')"
              row
              disabled
              hide-details
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="6">
            <v-text-field
              v-model="form.compound.nnc_long_number"
              :label="$t('CompoundForm.long_number')"
              dense
              disabled
              filled
              hide-details
              />
          </v-col>
          <v-col cols="6">
            <v-text-field
              v-model="form.compound.nnc_short_number"
              :label="$t('CompoundForm.short_number')"
              dense
              disabled
              filled
              hide-details
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="6">
            <v-textarea
              :label="$t('StudyCompoundForm.compound_definition')"
              v-model="form.compound.definition"
              dense
              auto-grow
              rows="1"
              disabled
              filled
              hide-details
              />
          </v-col>
          <v-col cols="6" v-if="form.compound_alias">
            <v-textarea
              :label="$t('StudyCompoundForm.alias_definition')"
              v-model="form.compound_alias.definition"
              dense
              auto-grow
              rows="1"
              disabled
              filled
              hide-details
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <v-text-field
              :value="substances"
              :label="$t('CompoundAliasForm.substance')"
              dense
              disabled
              filled
              hide-details
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <v-text-field
              :value="pharmacologicalClass"
              :label="$t('CompoundAliasForm.pharmacological_class')"
              dense
              disabled
              filled
              hide-details
              />
          </v-col>
        </v-row>
      </template>
    </validation-observer>
  </template>
  <template v-slot:step.compound="{ step }">
    <validation-observer v-if="form.compound" :ref="`observer_${step}`">
      <v-row>
        <v-col>
          <v-autocomplete
            v-model="form.dosage_form_uid"
            :label="$t('StudyCompoundForm.dosage_form')"
            :items="form.compound.dosage_forms"
            item-text="name"
            item-value="term_uid"
            dense
            clearable
            />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-autocomplete
            v-model="form.strength_value_uid"
            :label="$t('StudyCompoundForm.compound_strength_value')"
            :items="form.compound.strength_values"
            :item-text="(item) => `${item.value} ${item.unit_label}`"
            item-value="uid"
            dense
            clearable
            />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-autocomplete
            :data-cy="$t('StudyCompoundForm.route_of_admin')"
            v-model="form.route_of_administration_uid"
            :label="$t('StudyCompoundForm.route_of_admin')"
            :items="form.compound.routes_of_administration"
            item-text="name"
            item-value="term_uid"
            dense
            clearable
            />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-autocomplete
            :data-cy="$t('StudyCompoundForm.dispensed_in')"
            v-model="form.dispensed_in_uid"
            :label="$t('StudyCompoundForm.dispensed_in')"
            :items="form.compound.dispensers"
            item-text="name"
            item-value="term_uid"
            dense
            clearable
            />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-autocomplete
            :data-cy="$t('StudyCompoundForm.device')"
            v-model="form.device_uid"
            :label="$t('StudyCompoundForm.device')"
            :items="form.compound.delivery_devices"
            item-text="name"
            item-value="term_uid"
            dense
            clearable
            />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-textarea
            :data-cy="$t('StudyCompoundForm.other')"
            v-model="form.other_info"
            :label="$t('StudyCompoundForm.other')"
            auto-grow
            rows="1"
            dense
            clearable
            />
        </v-col>
      </v-row>
    </validation-observer>
  </template>
</horizontal-stepper-form>
</template>

<script>
import { bus } from '@/main'
import compoundAliases from '@/api/concepts/compoundAliases'
import compounds from '@/api/concepts/compounds'
import compoundsSimple from '@/api/concepts/compoundsSimple'
import constants from '@/constants/studyCompounds'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import { mapGetters } from 'vuex'
import NotApplicableField from '@/components/tools/NotApplicableField'
import statuses from '@/constants/statuses'
import studyConstants from '@/constants/study'
import terms from '@/api/controlledTerminology/terms'
import YesNoField from '@/components/tools/YesNoField'

export default {
  components: {
    HorizontalStepperForm,
    NotApplicableField,
    YesNoField
  },
  props: ['studyCompound'],
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      studyCompounds: 'studyCompounds/studyCompounds',
      getStudyCompoundsByTypeOfTreatment: 'studyCompounds/getStudyCompoundsByTypeOfTreatment',
      getNAStudyCompoundsByTypeOfTreatment: 'studyCompounds/getNAStudyCompoundsByTypeOfTreatment'
    }),
    substances () {
      if (this.form.compound && this.form.compound.substances && this.form.compound.substances.length) {
        return this.form.compound.substances.map(item => `${item.substance_name} (${item.substance_unii})`).join(', ')
      }
      return ''
    },
    pharmacologicalClass () {
      if (this.form.compound && this.form.compound.substances && this.form.compound.substances.length) {
        return this.form.compound.substances.map(item => item.pclass_name).filter(pclass => pclass !== undefined && pclass !== null).join(', ')
      }
      return ''
    },
    title () {
      if (this.studyCompound !== undefined) {
        return this.$t('StudyCompoundForm.edit_title')
      }
      return this.$t('StudyCompoundForm.add_title')
    },
    typeOfTreatment_uidNADisabled () {
      if ((this.$refs.naField && this.$refs.naField.notApplicable) || (this.studyCompound && !this.studyCompound.compound)) {
        return false
      }
      if (!this.form.type_of_treatment) {
        return true
      }
      const types = [
        constants.TYPE_OF_TREATMENT_INVESTIGATIONAL_PRODUCT,
        constants.TYPE_OF_TREATMENT_CURRENT_TREATMENT,
        constants.TYPE_OF_TREATMENT_COMPARATIVE_TREATMENT
      ]
      if (!types.find(item => item === this.form.type_of_treatment.sponsor_preferred_name)) {
        return true
      }
      const studyCompounds = this.getStudyCompoundsByTypeOfTreatment(this.form.type_of_treatment.term_uid)
      if (studyCompounds.length) {
        return true
      }
      const NAstudyCompounds = this.getNAStudyCompoundsByTypeOfTreatment(this.form.type_of_treatment.term_uid)
      if (NAstudyCompounds.length) {
        return true
      }
      return false
    }
  },
  data () {
    return {
      compoundAliases: [],
      compounds: [],
      helpItems: [
        'StudyCompoundForm.type_of_treatment',
        'StudyCompoundForm.compound',
        'StudyCompoundForm.compound_alias',
        'StudyCompoundForm.pharma_class',
        'StudyCompoundForm.substance',
        'StudyCompoundForm.unii',
        'StudyCompoundForm.route_of_admin',
        'StudyCompoundForm.dosage_form',
        'StudyCompoundForm.dispensed_in',
        'StudyCompoundForm.device',
        'StudyCompoundForm.formulation',
        'StudyCompoundForm.other'
      ],
      form: this.getInitialForm(),
      typeOfTreatments: [],
      steps: this.getInitialSteps()
    }
  },
  methods: {
    close () {
      this.$emit('close')
      this.form = this.getInitialForm()
      this.$refs.stepper.reset()
      this.$refs.naField.reset()
    },
    getInitialForm () {
      return {
        compound: {},
        compoundSimple: {},
        compound_alias: {},
        type_of_treatment: {},
        dosage_form_uid: null,
        strength_value_uid: null,
        route_of_administration_uid: null,
        dispensed_in_uid: null,
        device_uid: null,
        other_info: null
      }
    },
    getInitialSteps () {
      return [
        { name: 'type_of_treatment', title: this.$t('StudyCompoundForm.step1_title') },
        { name: 'compoundAlias', title: this.$t('StudyCompoundForm.step2_title') },
        { name: 'compound', title: this.$t('StudyCompoundForm.step3_title') }
      ]
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    cleanTypeOfTreatment (value) {
      if (value) {
        this.steps = [
          { name: 'type_of_treatment', title: this.$t('StudyCompoundForm.step1_title') }
        ]
      } else {
        this.steps = this.getInitialSteps()
      }
    },
    async submit () {
      const data = JSON.parse(JSON.stringify(this.form))
      data.type_of_treatment_uid = data.type_of_treatment.term_uid
      delete data.type_of_treatment
      delete data.compound
      if (data.compound_alias) {
        data.compound_alias_uid = data.compound_alias.uid || null
      } else {
        data.reason_for_missing_null_value_uid = studyConstants.TERM_NOT_APPLICABLE
      }

      let action = null
      let notification = null
      let args = null
      if (!this.studyCompound) {
        action = 'addStudyCompound'
        notification = 'add_success'
        args = { studyUid: this.selectedStudy.uid, data }
      } else {
        action = 'updateStudyCompound'
        notification = 'update_success'
        args = {
          studyUid: this.selectedStudy.uid,
          studyCompoundUid: this.studyCompound.study_compound_uid,
          data
        }
      }
      try {
        await this.$store.dispatch(`studyCompounds/${action}`, args)
        bus.$emit('notification', { msg: this.$t(`StudyCompoundForm.${notification}`) })
        this.close()
      } finally {
        this.$refs.stepper.loading = false
      }
    }
  },
  mounted () {
    const filters = {
      status: { v: [statuses.FINAL] }
    }
    compoundsSimple.getFiltered({ filters }).then(resp => {
      this.compounds = resp.data.items
    })
    terms.getByCodelist('typeOfTreatment').then(resp => {
      this.typeOfTreatments = resp.data.items
    })
  },
  watch: {
    studyCompound: {
      handler: function (val) {
        if (val) {
          this.form.type_of_treatment = val.type_of_treatment
          this.form.other_info = val.other_info
          if (val.compound) {
            this.form.compound = val.compound
            this.$set(this.form, 'compoundSimple', {
              uid: val.compound.uid,
              name: val.compound.name
            })
            const filters = {
              compound_uid: { v: [val.compound.uid] },
              status: { v: [statuses.FINAL] }
            }
            compoundAliases.getFiltered({ filters }).then(resp => {
              this.compoundAliases = resp.data.items
            })
          } else {
            this.steps = [
              { name: 'type_of_treatment', title: this.$t('StudyCompoundForm.step1_title') }
            ]
          }
          if (val.compound_alias) {
            this.form.compound_alias = val.compound_alias
          }
          if (val.dosage_form) {
            this.form.dosage_form_uid = val.dosage_form.term_uid
          }
          if (val.route_of_administration) {
            this.form.route_of_administration_uid = val.route_of_administration.term_uid
          }
          if (val.dispensed_in) {
            this.form.dispensed_in_uid = val.dispensed_in.term_uid
          }
          if (val.device) {
            this.form.device_uid = val.device.term_uid
          }
          if (val.strength_value) {
            this.form.strength_value_uid = val.strength_value.uid
          }
        }
      },
      immediate: true
    },
    'form.compoundSimple' (newValue, oldValue) {
      if (newValue) {
        if (!this.studyCompound || this.studyCompound.compound.uid !== newValue.uid) {
          this.$set(this.form, 'compound_alias', null)
        }
        const filters = {
          compound_uid: { v: [newValue.uid] },
          status: { v: [statuses.FINAL] }
        }
        compoundAliases.getFiltered({ filters }).then(resp => {
          this.compoundAliases = resp.data.items
        })
        if (newValue.uid) {
          compounds.getObject(newValue.uid).then(resp => {
            this.$set(this.form, 'compound', resp.data)
          })
        }
      }
    }
  }
}
</script>
