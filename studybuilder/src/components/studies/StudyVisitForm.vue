<template>
<div>
  <horizontal-stepper-form
    :title="title"
    :steps="steps"
    @close="close"
    @save="submit"
    :form-observer-getter="getObserver"
    ref="stepper"
    data-cy="form-body"
    :help-items="helpItems"
    :editData="form"
    @change="onTabChange"
    >
    <template v-slot:step.visitType="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col>
              <v-radio-group
                v-model="form.visit_class"
                :error-messages="errors"
                >
                <v-radio
                  v-for="visitClass in visitClasses"
                  :key="visitClass.value"
                  :label="visitClass.label"
                  :value="visitClass.value"
                  :data-cy="visitClass.value"
                  />
              </v-radio-group>
            </v-col>
          </v-row>
        </validation-provider>
      </validation-observer>
    </template>
    <template v-slot:step.epoch="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col>
              <v-autocomplete
                v-model="studyEpoch"
                data-cy="study-period"
                :label="$t('StudyVisitForm.period')"
                :items="filteredPeriods"
                item-text="epoch_name"
                item-value="uid"
                :error-messages="errors"
                clearable
                :loading="loading"
                :disabled="studyVisit !== undefined && studyVisit !== null"
                class="required"
                />
            </v-col>
          </v-row>
        </validation-provider>
      </validation-observer>
    </template>
    <template v-slot:step.details="{ step }">
      <v-row>
        <v-col cols="8">
          <validation-observer :ref="`observer_${step}`">
            <div class="sub-title">{{ $t('StudyVisitForm.timing') }}</div>
            <v-row class="mt-2">
              <v-col cols="12" v-if="form.visit_class === visitConstants.CLASS_SINGLE_VISIT">
                <v-radio-group
                  v-model="form.visit_subclass"
                  row
                  hide-details
                  >
                  <v-radio
                    :label="$t('StudyVisitForm.single_visit')"
                    data-cy="single-visit"
                    :value="visitConstants.SUBCLASS_SINGLE_VISIT"
                    ></v-radio>
                  <v-radio
                    :label="$t('StudyVisitForm.anchor_visit_in_group')"
                    data-cy="anchor-visit-in-visit-group"
                    :value="visitConstants.SUBCLASS_ANCHOR_VISIT_IN_GROUP_OF_SUBV"
                    ></v-radio>
                  <v-radio
                    v-if="!displayAnchorVisitFlag && anchorVisitsInSubgroup.length"
                    :label="$t('StudyVisitForm.additional_sub_visit')"
                    :value="visitConstants.SUBCLASS_ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV"
                    ></v-radio>
                </v-radio-group>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="4">
                <validation-provider
                  v-slot="{ errors }"
                  rules="required"
                  >
                  <v-autocomplete
                    v-model="form.visit_type_uid"
                    :label="$t('StudyVisitForm.visit_type')"
                    data-cy="visit-type"
                    :items="visitTypes"
                    item-text="visit_type_name"
                    item-value="visit_type_uid"
                    :error-messages="errors"
                    clearable
                    :disabled="form.visit_class !== visitConstants.CLASS_SINGLE_VISIT && form.visit_class !== visitConstants.CLASS_SPECIAL_VISIT"
                    class="required"
                    />
                </validation-provider>
              </v-col>
              <v-col cols="4">
                <validation-provider
                  v-slot="{ errors }"
                  rules="required"
                  >
                  <v-autocomplete
                    v-model="form.visit_contact_mode_uid"
                    :label="$t('StudyVisitForm.contact_mode')"
                    data-cy="contact-mode"
                    :items="contactModes"
                    item-text="sponsor_preferred_name"
                    item-value="term_uid"
                    :error-messages="errors"
                    @change="getVisitPreview"
                    clearable
                    class="required"
                    />
                </validation-provider>
              </v-col>
              <v-col cols="4" v-if="form.visit_class !== visitConstants.CLASS_SPECIAL_VISIT">
                <div class="d-flex">
                  <v-checkbox
                    v-if="displayAnchorVisitFlag"
                    v-model="form.is_global_anchor_visit"
                    :label="$t('StudyVisitForm.anchor_visit')"
                    data-cy="anchor-visit-checkbox"
                    :hint="$t('StudyVisitForm.anchor_visit_hint')"
                    persistent-hint
                    />
                  <v-text-field
                    :label="$t('StudyVisitForm.current_anchor_visit')"
                    v-model="currentAnchorVisit"
                    readonly
                    filled
                    class="ml-4"
                    />
                </div>
              </v-col>
            </v-row>
            <v-row v-if="form.visit_class === visitConstants.CLASS_SINGLE_VISIT || form.visit_class === visitConstants.CLASS_SPECIAL_VISIT">
              <v-col cols="4">
                <validation-provider
                  v-slot="{ errors }"
                  rules="required"
                  >
                  <v-autocomplete
                    v-if="form.visit_subclass !== visitConstants.SUBCLASS_ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV && form.visit_class !== visitConstants.CLASS_SPECIAL_VISIT"
                    v-model="form.time_reference_uid"
                    :label="$t('StudyVisitForm.time_reference')"
                    data-cy="time-reference"
                    :items="timeReferences"
                    item-text="sponsor_preferred_name"
                    item-value="term_uid"
                    :error-messages="errors"
                    clearable
                    @change="getVisitPreview"
                    class="required"
                    />
                  <v-autocomplete
                    v-else
                    v-model="form.visit_sublabel_reference"
                    :label="$t('StudyVisitForm.time_reference')"
                    data-cy="time-reference"
                    :items="timerefVisits"
                    item-text="visit_name"
                    item-value="uid"
                    :error-messages="errors"
                    clearable
                    />
                </validation-provider>
              </v-col>
              <v-col cols="4" v-if="form.visit_class !== visitConstants.CLASS_SPECIAL_VISIT">
                <validation-provider
                  v-slot="{ errors }"
                  rules="required"
                  >
                  <v-text-field
                    v-model="form.time_value"
                    type="number"
                    :label="$t('StudyVisitForm.time_dist')"
                    data-cy="visit-timing"
                    clearable
                    :error-messages="errors"
                    @change="getVisitPreview"
                    :disabled="disableTimeValue"
                    class="required"
                    />
                </validation-provider>
              </v-col>
              <v-col cols="4" v-if="form.visit_class !== visitConstants.CLASS_SPECIAL_VISIT">
                <validation-provider
                  v-slot="{ errors }"
                  rules="required"
                  >
                  <v-autocomplete
                    v-model="form.time_unit_uid"
                    :label="$t('StudyVisitForm.time_unit_name')"
                    data-cy="time-unit"
                    :items="timeUnits"
                    item-text="name"
                    item-value="uid"
                    :error-messages="errors"
                    clearable
                    @change="getVisitPreview"
                    class="required"
                    />
                </validation-provider>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="3">
                <v-text-field
                  v-model="form.visit_name"
                  :label="$t('StudyVisitForm.visit_name')"
                  data-cy="visit-name"
                  readonly
                  filled
                  :loading="previewLoading"
                  />
              </v-col>
              <v-col cols="3">
                <v-text-field
                  v-model="form.visit_short_name"
                  :label="$t('StudyVisitForm.visit_short_name')"
                  data-cy="visit-short-name"
                  readonly
                  filled
                  :loading="previewLoading"
                  />
              </v-col>
              <v-col cols="3" v-if="form.visit_class === visitConstants.CLASS_SINGLE_VISIT">
                <v-text-field
                  v-model="form.study_day_label"
                  :label="$t('StudyVisitForm.study_day_label')"
                  data-cy="study-day-label"
                  readonly
                  filled
                  :loading="previewLoading"
                  />
              </v-col>
              <v-col cols="3" v-if="form.visit_class === visitConstants.CLASS_SINGLE_VISIT">
                <v-text-field
                  v-model="form.study_week_label"
                  :label="$t('StudyVisitForm.study_week_label')"
                  data-cy="study-week-label"
                  readonly
                  filled
                  :loading="previewLoading"
                  />
              </v-col>
            </v-row>
            <template v-if="form.visit_class === visitConstants.CLASS_SINGLE_VISIT">
              <div class="sub-title">{{ $t('StudyVisitForm.visit_window') }}</div>
              <div class="d-flex align-center">
                <div class="mr-2">
                  <validation-provider
                    v-slot="{ errors }"
                    rules="max_value:0"
                    >
                    <v-row>
                      <v-col>
                        <v-text-field
                          v-model="form.min_visit_window_value"
                          :label="$t('StudyVisitForm.visit_win_min')"
                          data-cy="visit-win-min"
                          clearable
                          :error-messages="errors"
                          type="number"
                          />
                      </v-col>
                    </v-row>
                  </validation-provider>
                </div>
                <div class="mr-2 secondary--text text-h4">/</div>
                <div class="mr-2">
                  <validation-provider
                    v-slot="{ errors }"
                    rules="min_value:0"
                    >
                    <v-row>
                      <v-col>
                        <v-text-field
                          v-model="form.max_visit_window_value"
                          :label="$t('StudyVisitForm.visit_win_max')"
                          data-cy="visit-win-max"
                          clearable
                          :error-messages="errors"
                          type="number"
                          />
                      </v-col>
                    </v-row>
                  </validation-provider>
                </div>
                <div>
                  <validation-provider
                    v-slot="{ errors }"
                    rules="required"
                    >
                    <v-row>
                      <v-col>
                        <v-autocomplete
                          v-model="form.visit_window_unit_uid"
                          :label="$t('StudyVisitForm.visit_win_unit')"
                          data-cy="visit-win-unit"
                          :items="timeUnits"
                          item-text="name"
                          item-value="uid"
                          :error-messages="errors"
                          clearable
                          @change="getVisitPreview"
                          class="required"
                          />
                      </v-col>
                    </v-row>
                  </validation-provider>
                </div>
              </div>
            </template>
            <div class="sub-title mt-8">{{ $t('StudyVisitForm.visit_details') }}</div>
            <v-row>
              <v-col>
                <v-text-field
                  v-model="form.description"
                  :label="$t('StudyVisitForm.visit_description')"
                  data-cy="visit-description"
                  clearable
                  />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="6">
                <v-autocomplete
                  v-model="form.epoch_allocation_uid"
                  :label="$t('StudyVisitForm.epoch_allocation')"
                  data-cy="epoch-allocation-rule"
                  :items="epochAllocations"
                  item-text="sponsor_preferred_name"
                  item-value="term_uid"
                  clearable
                  />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="6">
                <validation-provider
                  v-slot="{ errors }"
                  rules=""
                  >
                  <v-textarea
                    v-model="form.start_rule"
                    :label="$t('StudyVisitForm.visit_start_rule')"
                    data-cy="visit-start-rule"
                    clearable
                    rows="1"
                    :error-messages="errors"
                    auto-grow
                    />
                </validation-provider>
              </v-col>
              <v-col cols="6">
                <v-textarea
                  v-model="form.end_rule"
                  :label="$t('StudyVisitForm.visit_stop_rule')"
                  data-cy="visit-end-rule"
                  clearable
                  rows="1"
                  auto-grow
                  />
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-text-field
                  v-model="form.note"
                  :label="$t('StudyVisitForm.visit_notes')"
                  data-cy="visit-notes"
                  clearable
                  />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="6" class="d-flex align-center">
                <v-checkbox
                  v-model="form.show_visit"
                  default="true"
                  :label="$t('StudyVisitForm.show_visit')"
                  />
              </v-col>
            </v-row>
          </validation-observer>
        </v-col>
        <v-col cols="4" class="d-flex justify-center">
          <v-data-iterator
            :items="epochStudyVisits"
            :no-data-text="$t('StudyVisitForm.no_visit_available')"
            hide-default-footer
            items-per-page="-1"
            >
            <template v-slot:header>
              <div class="sub-title">
                {{ $t('StudyVisitForm.existing_visits') }}<br>{{ $t('StudyVisitForm.names_and_timing') }}
              </div>
            </template>
            <template v-slot:default="props">
              <v-card>
                <v-list>
                  <v-list-item
                    v-for="item in props.items"
                    cols="12"
                    :key="item.uid"
                    >
                    {{ item.visit_name }} - {{ item.study_day_label }}
                  </v-list-item>
                </v-list>
              </v-card>
            </template>
          </v-data-iterator>
        </v-col>
      </v-row>
    </template>
  </horizontal-stepper-form>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import epochs from '@/api/studyEpochs'
import units from '@/api/units'
import codelists from '@/api/controlledTerminology/terms'
import { mapGetters } from 'vuex'
import { bus } from '@/main'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import unitConstants from '@/constants/units'
import visitConstants from '@/constants/visits'

export default {
  components: {
    ConfirmDialog,
    HorizontalStepperForm
  },
  props: {
    studyVisit: Object,
    firstVisit: Boolean,
    opened: Boolean
  },
  computed: {
    displayAnchorVisitFlag () {
      return this.globalAnchorVisit === null || (this.studyVisit && this.studyVisit.uid === this.globalAnchorVisit.uid)
    },
    title () {
      return (this.studyVisit) ? this.$t('StudyVisitForm.edit_title') : this.$t('StudyVisitForm.add_title')
    },
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      groups: 'studyEpochs/allowedConfigs'
    }),
    filteredPeriods () {
      if (this.form.visit_class === visitConstants.CLASS_SPECIAL_VISIT || this.form.visit_class === visitConstants.CLASS_SINGLE_VISIT) {
        return this.periods.filter(item => item.epoch_name !== visitConstants.EPOCH_BASIC)
      }
      if (this.periods) {
        return this.periods.filter(item => item.epoch_name === visitConstants.EPOCH_BASIC)
      }
      return []
    },
    timerefVisits () {
      if (this.form.visit_subclass === visitConstants.SUBCLASS_ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV) {
        return this.anchorVisitsInSubgroup
      } else if (this.form.visit_class === visitConstants.CLASS_SPECIAL_VISIT) {
        return this.anchorVisitsForSpecialVisit
      }
      return this.studyVisits
    },
    epochStudyVisits () {
      return this.studyVisits.filter(item => item.study_epoch_uid === this.studyEpoch)
    }
  },
  data () {
    return {
      anchorVisitsInSubgroup: [],
      anchorVisitsForSpecialVisit: [],
      currentAnchorVisit: null,
      disableTimeValue: false,
      form: this.getInitialFormContent(this.studyVisit),
      helpItems: [
        'StudyVisitForm.vtype_step_label',
        'StudyVisitForm.period',
        'StudyVisitForm.single_visit',
        'StudyVisitForm.anchor_visit_in_group',
        'StudyVisitForm.visit_type',
        'StudyVisitForm.contact_mode',
        'StudyVisitForm.anchor_visit',
        'StudyVisitForm.current_anchor_visit',
        'StudyVisitForm.time_reference',
        'StudyVisitForm.time_value',
        'StudyVisitForm.time_unit',
        'StudyVisitForm.visit_name',
        'StudyVisitForm.visit_short_name',
        'StudyVisitForm.study_day_label',
        'StudyVisitForm.study_week_label',
        'StudyVisitForm.visit_win_min',
        'StudyVisitForm.visit_win_max',
        'StudyVisitForm.visit_win_unit',
        'StudyVisitForm.visit_description',
        'StudyVisitForm.epoch_allocation',
        'StudyVisitForm.visit_start_rule',
        'StudyVisitForm.visit_stop_rule',
        'StudyVisitForm.visit_notes',
        'StudyVisitForm.consecutive_visit',
        'StudyVisitForm.duplicate_visit'
      ],
      globalAnchorVisit: null,
      periods: [],
      steps: [
        { name: 'visitType', title: this.$t('StudyVisitForm.vtype_step_label') },
        { name: 'epoch', title: this.$t('StudyVisitForm.epoch_step_label') },
        { name: 'details', title: this.$t('StudyVisitForm.details_step_label'), belowDisplay: true }
      ],
      timeReferences: [],
      timeUnits: [],
      visitTypes: [],
      loading: false,
      previewLoading: false,
      contactModes: [],
      epochAllocations: [],
      studyEpoch: '',
      studyVisits: [],
      visitCount: 1,
      visitClasses: [
        { label: this.$t('StudyVisitForm.scheduled_visit'), value: visitConstants.CLASS_SINGLE_VISIT },
        { label: this.$t('StudyVisitForm.unscheduled_visit'), value: visitConstants.CLASS_UNSCHEDULED_VISIT },
        { label: this.$t('StudyVisitForm.non_visit'), value: visitConstants.CLASS_NON_VISIT },
        { label: this.$t('StudyVisitForm.special_visit'), value: visitConstants.CLASS_SPECIAL_VISIT }
      ],
      visitSubClasses: [
        { label: this.$t('StudyVisitForm.single_visit'), value: visitConstants.SUBCLASS_SINGLE_VISIT },
        { label: this.$t('StudyVisitForm.anchor_visit_in_group'), value: visitConstants.SUBCLASS_ANCHOR_VISIT_IN_GROUP_OF_SUBV },
        {
          label: this.$t('StudyVisitForm.additional_sub_visit'),
          value: visitConstants.SUBCLASS_ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV
        }
      ]
    }
  },
  methods: {
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    close () {
      this.$emit('close')
      this.form = this.getInitialFormContent()
      this.$refs.stepper.reset()
    },
    getInitialFormContent (item) {
      if (item) {
        return item
      }
      this.studyEpoch = ''
      return {
        is_global_anchor_visit: false,
        visit_class: visitConstants.CLASS_SINGLE_VISIT,
        show_visit: true,
        min_visit_window_value: 0,
        max_visit_window_value: 0,
        visit_subclass: visitConstants.CLASS_SINGLE_VISIT
      }
    },
    async submit () {
      const valid1 = await this.$refs.observer_1.validate()
      if (!valid1) {
        return
      }
      const valid2 = await this.$refs.observer_2.validate()
      if (!valid2) {
        return
      }
      try {
        if (!this.studyVisit) {
          await this.addObject()
        } else {
          await this.updateObject()
        }
        this.close()
      } finally {
        this.$refs.stepper.reset()
        this.$refs.stepper.loading = false
      }
    },
    async addObject () {
      const data = JSON.parse(JSON.stringify(this.form))
      if (data.visit_class === visitConstants.CLASS_SPECIAL_VISIT || data.visit_subclass === visitConstants.SUBCLASS_ADDITIONAL_SUBVISIT_IN_A_GROUP_OF_SUBV) {
        data.time_reference_uid = this.timeReferences.find(item => item.sponsor_preferred_name === visitConstants.TIMEREF_ANCHOR_VISIT_IN_VISIT_GROUP).term_uid
      } else if (data.visit_class !== visitConstants.CLASS_SINGLE_VISIT) {
        delete data.time_value
        delete data.time_reference_uid
        delete data.min_visit_window_value
        delete data.max_visit_window_value
        delete data.time_unit_uid
      }
      await this.$store.dispatch('studyEpochs/addStudyVisit', { studyUid: this.selectedStudy.uid, input: data })
      this.$emit('refresh')
      bus.$emit('notification', { msg: this.$t('StudyVisitForm.add_success') })
    },
    updateObject () {
      const data = JSON.parse(JSON.stringify(this.form))
      return this.$store.dispatch('studyEpochs/updateStudyVisit', { studyUid: this.selectedStudy.uid, studyVisitUid: this.studyVisit.uid, input: data }).then(resp => {
        this.$emit('refresh')
        bus.$emit('notification', { msg: this.$t('StudyVisitForm.update_success') })
      })
    },
    getVisitPreview () {
      if (this.studyVisit) {
        return
      }
      const mandatoryFields = ['visit_type_uid', 'visit_contact_mode_uid']
      if (this.form.visit_class === visitConstants.CLASS_SINGLE_VISIT) {
        mandatoryFields.push('time_reference_uid', 'time_value')
      }
      for (const field of mandatoryFields) {
        if (this.form[field] === undefined || this.form[field] === null) {
          return
        }
      }
      const payload = { ...this.form }
      if (payload.visit_class !== visitConstants.CLASS_SINGLE_VISIT) {
        payload.time_reference_uid = this.timeReferences.find(item => item.sponsor_preferred_name === visitConstants.TIMEREF_GLOBAL_ANCHOR_VISIT).term_uid
        payload.time_value = 0
      }
      payload.is_global_anchor_visit = false
      this.previewLoading = true
      epochs.getStudyVisitPreview(this.selectedStudy.uid, payload).then(resp => {
        for (const field of ['visit_name', 'visit_short_name', 'study_day_label', 'study_week_label']) {
          this.$set(this.form, field, resp.data[field])
        }
      }).finally(() => {
        this.previewLoading = false
      })
    },
    callbacks () {
      this.$store.dispatch('studyEpochs/fetchAllowedConfigs')
      epochs.getGlobalAnchorVisit(this.selectedStudy.uid).then(resp => {
        this.globalAnchorVisit = resp.data
        if (this.globalAnchorVisit) {
          this.currentAnchorVisit = this.globalAnchorVisit.visit_type_name
        }
      })
      epochs.getAnchorVisitsInGroupOfSubvisits(this.selectedStudy.uid).then(resp => {
        this.anchorVisitsInSubgroup = resp.data
      })
      epochs.getAnchorVisitsForSpecialVisit(this.selectedStudy.uid).then(resp => {
        this.anchorVisitsForSpecialVisit = resp.data
      })
      codelists.getByCodelist('epochs').then(resp => {
        this.loading = true
        this.epochsData = resp.data.items
        epochs.getStudyEpochs(this.selectedStudy.uid).then(resp => {
          this.periods = resp.data.items
          this.periods.forEach(item => {
            this.epochsData.forEach(epochDef => {
              if (epochDef.term_uid === item.epoch) {
                item.epoch_name = epochDef.sponsor_preferred_name
              }
            })
          })
          if (this.studyVisit) {
            this.studyEpoch = this.studyVisit.study_epoch_uid
          }
          this.loading = false
        })
      })
      codelists.getByCodelist('contactModes').then(resp => {
        this.contactModes = resp.data.items
      })
      units.getBySubset(unitConstants.TIME_UNIT_SUBSET_STUDY_TIME).then(resp => {
        this.timeUnits = resp.data.items
        if (!this.studyVisit) {
          const defaultUnit = this.timeUnits.find(unit => unit.name === 'days')
          this.form.time_unit_uid = defaultUnit.uid
          this.form.visit_window_unit_uid = defaultUnit.uid
        }
      })
      codelists.getByCodelist('epochAllocations').then(resp => {
        this.epochAllocations = resp.data.items
      })
      epochs.getStudyVisits(this.selectedStudy.uid, { page_size: 0 }).then(resp => {
        this.studyVisits = resp.data.items
      })
    },
    onTabChange (number) {
      if (number === 3 && this.globalAnchorVisit === null) {
        bus.$emit('notification', { msg: this.$t('StudyVisitForm.no_anchor_visit'), type: 'warning' })
      }
    },
    setVisitType (value) {
      if (this.visitTypes.length) {
        this.$set(this.form, 'visit_type_uid', this.visitTypes.find(item => item.visit_type_name === value).visit_type_uid)
        this.getVisitPreview()
      }
    },
    setEpochAllocationRule (value) {
      if (this.epochAllocations.length) {
        this.$set(this.form, 'epoch_allocation_uid', this.epochAllocations.find(item => item.sponsor_preferred_name === value).term_uid)
      }
    },
    setStudyEpochToBasic () {
      if (this.loading) {
        return
      }
      if (this.periods.length) {
        this.studyEpoch = this.periods.find(item => item.epoch_name === visitConstants.EPOCH_BASIC)
        if (this.studyEpoch) {
          this.studyEpoch = this.studyEpoch.uid
        }
      }
      if (!this.studyEpoch) {
        const subType = this.groups.find(item => item.subtype_name === visitConstants.EPOCH_BASIC)
        const payload = { epoch_subtype: subType.subtype, study_uid: this.selectedStudy.uid }
        epochs.getPreviewEpoch(this.selectedStudy.uid, payload).then(resp => {
          const data = {
            study_uid: this.selectedStudy.uid,
            epoch: resp.epoch,
            epoch_type: subType.type,
            epoch_subtype: subType.subtype,
            color_hash: '#FFFFFF'
          }
          epochs.addStudyEpoch(this.selectedStudy.uid, data).then(resp => {
            epochs.getStudyEpochs(this.selectedStudy.uid).then(resp => {
              this.periods = resp.data.items
              this.studyEpoch = this.periods.find(item => item.epoch_name === visitConstants.EPOCH_BASIC).uid
            })
          })
        })
      }
    }
  },
  created () {
    this.visitConstants = visitConstants
  },
  mounted () {
    this.callbacks()
  },
  watch: {
    studyVisit (value) {
      if (value) {
        this.form = value
      }
    },
    opened (value) {
      if (value) {
        this.callbacks()
      }
    },
    studyEpoch (value) {
      if (!value) {
        return
      }
      this.$set(this.form, 'study_epoch_uid', value)
      const data = {
        epoch_type_uid: this.periods.find(el => el.uid === value).epoch_type
      }
      epochs.getAllowedVisitTypes(this.selectedStudy.uid, data).then(resp => {
        this.visitTypes = resp.data
        codelists.getByCodelist('timepointReferences').then(resp => {
          this.timeReferences = resp.data.items
          if (this.form.visit_class === visitConstants.CLASS_UNSCHEDULED_VISIT && this.visitTypes.length) {
            this.setVisitType(visitConstants.VISIT_TYPE_UNSCHEDULED)
          }
          if (this.form.visit_class === visitConstants.CLASS_NON_VISIT && this.visitTypes.length) {
            this.setVisitType(visitConstants.VISIT_TYPE_NON_VISIT)
          }
        })
      })
      if (this.form.visit_class === visitConstants.CLASS_NON_VISIT || this.form.visit_class === visitConstants.CLASS_UNSCHEDULED_VISIT) {
        this.setEpochAllocationRule(visitConstants.DATE_CURRENT_VISIT)
      } else {
        const studyEpoch = this.periods.find(item => item.uid === value)
        if (studyEpoch.epoch_name === visitConstants.EPOCH_TREATMENT || studyEpoch.epoch_name === visitConstants.EPOCH_TREATMENT_1) {
          epochs.getAmountOfVisitsInStudyEpoch(this.selectedStudy.uid, studyEpoch.uid).then(resp => {
            const amountOfVisitsInTreatment = resp.data
            if (amountOfVisitsInTreatment === 0) {
              this.setEpochAllocationRule(visitConstants.PREVIOUS_VISIT)
            } else {
              this.setEpochAllocationRule(visitConstants.CURRENT_VISIT)
            }
          })
        } else {
          this.setEpochAllocationRule(visitConstants.CURRENT_VISIT)
        }
      }
    },
    'form.is_global_anchor_visit' (value) {
      if (value) {
        this.$set(this.form, 'time_value', 0)
        this.disableTimeValue = true
      } else {
        this.$set(this.form, 'time_value', null)
        this.disableTimeValue = false
      }
    },
    'form.visit_class' (value) {
      if (value !== visitConstants.CLASS_SINGLE_VISIT && value !== visitConstants.CLASS_SPECIAL_VISIT) {
        this.setStudyEpochToBasic()
        const contactMode = this.contactModes.find(item => item.sponsor_preferred_name === visitConstants.CONTACT_MODE_VIRTUAL_VISIT)
        if (contactMode) {
          this.$set(this.form, 'visit_contact_mode_uid', contactMode.term_uid)
        }
      }
      if (value === visitConstants.CLASS_UNSCHEDULED_VISIT && this.visitTypes.length) {
        this.setVisitType(visitConstants.VISIT_TYPE_UNSCHEDULED)
      }
      if (value === visitConstants.CLASS_NON_VISIT && this.visitTypes.length) {
        this.setVisitType(visitConstants.VISIT_TYPE_NON_VISIT)
      }
    },
    periods (value) {
      if (value && value.length && this.form.visit_class !== visitConstants.CLASS_SINGLE_VISIT) {
        this.setStudyEpochToBasic()
      }
    }
  }
}
</script>

<style scoped lang="scss">
.sub-title {
  color: var(--v-secondary-base);
  font-weight: 600;
  margin: 10px 0;
  font-size: 1.1em;
}
</style>
