<template>
<horizontal-stepper-form
  ref="stepper"
  :title="title"
  :steps="steps"
  @close="close"
  @save="submit"
  :form-observer-getter="getObserver"
  :editable="studyCompoundDosing !== undefined && studyCompoundDosing !== null"
  :helpItems="helpItems"
  :edit-data="form"
  >
  <template v-slot:step.element="{ step }">
    <validation-observer :ref="`observer_${step}`">
      <v-row>
        <v-col cols="12">
          <validation-provider
            rules="required"
            v-slot="{ errors }"
            >
            <v-autocomplete
              v-model="form.study_element"
              :label="$t('StudyCompoundDosingForm.element')"
              :items="studyElements"
              item-text="name"
              return-object
              :error-messages="errors"
              dense
              clearable
              />
          </validation-provider>
        </v-col>
      </v-row>
      <template v-if="form.study_element">
        <v-row>
          <v-col cols="6">
            <v-text-field
              v-model="form.study_element.order"
              :label="$t('StudyCompoundDosingForm.element_order')"
              row
              disabled
              hide-details
              />
          </v-col>
          <v-col cols="6">
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="6">
            <v-text-field
              v-model="elementType"
              :label="$t('StudyCompoundDosingForm.element_type')"
              row
              disabled
              hide-details
              />
          </v-col>
          <v-col cols="6">
            <v-text-field
              v-model="form.study_element.element_subtype.sponsor_preferred_name"
              :label="$t('StudyCompoundDosingForm.element_subtype')"
              row
              disabled
              hide-details
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="6">
            <v-text-field
              v-model="form.study_element.name"
              :label="$t('StudyCompoundDosingForm.element_name')"
              row
              disabled
              hide-details
              />
          </v-col>
          <v-col cols="6">
            <v-text-field
              v-model="form.study_element.short_name"
              :label="$t('StudyCompoundDosingForm.element_short_name')"
              row
              disabled
              hide-details
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="form.study_element.description"
              :label="$t('StudyCompoundDosingForm.element_description')"
              row
              disabled
              hide-details
              />
          </v-col>
        </v-row>
      </template>
    </validation-observer>
  </template>
  <template v-slot:step.compound="{ step }">
    <validation-observer :ref="`observer_${step}`">
      <v-row>
        <v-col cols="12">
          <validation-provider
            rules="required"
            v-slot="{ errors }"
            >
            <v-autocomplete
              v-model="form.study_compound"
              :label="$t('StudyCompoundDosingForm.compound')"
              :items="studyCompounds"
              item-text="compound_alias.name"
              return-object
              :error-messages="errors"
              dense
              clearable
              />
          </validation-provider>
        </v-col>
      </v-row>
    </validation-observer>
    <template v-if="form.study_compound">
      <v-row>
        <v-col cols="6">
          <v-text-field
            v-model="form.study_compound.order"
            :label="$t('StudyCompoundDosingForm.compound_order')"
            row
            disabled
            hide-details
            />
        </v-col>
        <v-col cols="6">
          <v-text-field
            v-model="form.study_compound.type_of_treatment.name"
            :label="$t('StudyCompoundDosingForm.type_of_treatment')"
            row
            disabled
            hide-details
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="6">
            <v-text-field
              v-model="form.study_compound.compound.name"
              :label="$t('StudyCompoundDosingForm.compound_name')"
              row
              disabled
              hide-details
              />
          </v-col>
          <v-col cols="6">
            <v-text-field
              v-model="form.study_compound.compound_alias.name"
              :label="$t('StudyCompoundDosingForm.compound_alias_name')"
              row
              disabled
              hide-details
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="6">
            <yes-no-field
              v-model="form.study_compound.compound_alias.is_preferred_synonym"
              :label="$t('StudyCompoundForm.is_preferred_synonym')"
              row
              disabled
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
  </template>
  <template v-slot:step.compound_dosing="{ step }">
    <validation-observer :ref="`observer_${step}`">
      <v-row>
        <v-col>
          <v-autocomplete
            v-if="form.study_compound"
            v-model="form.dose_value_uid"
            :label="$t('StudyCompoundDosingForm.dose_value')"
            :items="form.study_compound.compound.dose_values"
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
            v-if="form.study_compound"
            :data-cy="$t('StudyCompoundDosingForm.dose_frequency')"
            v-model="form.dose_frequency_uid"
            :label="$t('StudyCompoundDosingForm.dose_frequency')"
            :items="form.study_compound.compound.dose_frequencies"
            item-text="name"
            item-value="term_uid"
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
import arms from '@/api/arms'
import terms from '@/api/controlledTerminology/terms'
import { bus } from '@/main'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import { mapGetters } from 'vuex'
import YesNoField from '@/components/tools/YesNoField'

export default {
  components: {
    HorizontalStepperForm,
    YesNoField
  },
  props: {
    studyCompoundDosing: Object
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      studyCompounds: 'studyCompounds/studyCompounds',
      studyCompoundDosings: 'studyCompounds/studyCompoundDosings'
    }),
    title () {
      if (this.studyCompoundDosing !== undefined && this.studyCompoundDosing !== null) {
        return this.$t('StudyCompoundDosingForm.edit_title')
      }
      return this.$t('StudyCompoundDosingForm.add_title')
    },
    substances () {
      if (!this.form.study_compound) {
        return ''
      }
      const compound = this.form.study_compound.compound
      if (compound && compound.substances && compound.substances.length) {
        return compound.substances.map(item => `${item.substance_name} (${item.substance_unii})`).join(', ')
      }
      return ''
    },
    pharmacologicalClass () {
      if (!this.form.study_compound) {
        return ''
      }
      const compound = this.form.study_compound.compound
      if (compound && compound.substances && compound.substances.length) {
        return compound.substances.map(item => item.pclass_name).filter(pclass => pclass !== undefined && pclass !== null).join(', ')
      }
      return ''
    },
    elementType () {
      if (!this.form.study_element) {
        return ''
      }
      return this.getElementType(this.form.study_element)
    }
  },
  data () {
    return {
      helpItems: [
        'StudyCompoundDosingForm.element',
        'StudyCompoundDosingForm.compound',
        'StudyCompoundDosingForm.dose_value',
        'StudyCompoundDosingForm.dose_frequency'
      ],
      form: {
      },
      steps: this.getInitialSteps(),
      studyElements: [],
      studyElementTypes: []
    }
  },
  methods: {
    close () {
      this.$emit('close')
      this.form = {}
      this.$refs.stepper.reset()
    },
    getInitialSteps () {
      return [
        { name: 'element', title: this.$t('StudyCompoundDosingForm.step1_title') },
        { name: 'compound', title: this.$t('StudyCompoundDosingForm.step2_title') },
        { name: 'compound_dosing', title: this.$t('StudyCompoundDosingForm.step3_title') }
      ]
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    getElementType (item) {
      const type = this.studyElementTypes.filter(el => el.term_uid === item.code)[0]
      if (item.code && type) {
        return type.sponsor_preferred_name
      }
    },
    async submit () {
      const data = { ...this.form }
      data.study_element_uid = data.study_element.element_uid
      delete data.study_element
      data.study_compound_uid = data.study_compound.study_compound_uid

      let action = null
      let notification = null
      let args = null
      if (!this.studyCompoundDosing) {
        action = 'addStudyCompoundDosing'
        notification = 'add_success'
        args = { studyUid: this.selectedStudy.uid, data }
      } else {
        action = 'updateStudyCompoundDosing'
        notification = 'update_success'
        args = {
          studyUid: this.selectedStudy.uid,
          studyCompoundDosingUid: this.studyCompoundDosing.study_compound_dosing_uid,
          data
        }
      }
      try {
        await this.$store.dispatch(`studyCompounds/${action}`, args)
        bus.$emit('notification', { msg: this.$t(`StudyCompoundDosingForm.${notification}`) })
        this.close()
      } finally {
        this.$refs.stepper.loading = false
      }
    }
  },
  mounted () {
    this.$store.dispatch('studyCompounds/fetchStudyCompounds', { studyUid: this.selectedStudy.uid, page_size: 0 })
    arms.getStudyElements(this.selectedStudy.uid, { page_size: 0 }).then(resp => {
      this.studyElements = resp.data.items
    })
    terms.getByCodelist('elementTypes').then(resp => {
      this.studyElementTypes = resp.data.items
    })
  },
  watch: {
    studyCompoundDosing: {
      handler: function (value) {
        if (value) {
          this.form = { ...value }
          if (value.dose_value) {
            this.$set(this.form, 'dose_value_uid', value.dose_value.uid)
          }
          if (value.dose_frequency) {
            this.$set(this.form, 'dose_frequency_uid', value.dose_frequency.term_uid)
          }
        }
      },
      immediate: true
    }
  }
}
</script>
