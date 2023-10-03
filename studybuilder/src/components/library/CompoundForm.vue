<template>
<horizontal-stepper-form
  ref="stepper"
  :title="title"
  :steps="steps"
  @close="close"
  @save="submit"
  :form-observer-getter="getObserver"
  :editable="compound !== undefined && compound !== null"
  :helpItems="helpItems"
  :edit-data="form"
  >
  <template v-slot:step.identifiers="{ step }">
    <validation-observer :ref="`observer_${step}`">
      <v-row>
        <v-col cols="12">
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <yes-no-field
              v-model="form.is_sponsor_compound"
              :label="$t('CompoundForm.sponsor_compound')"
              row
              :error-messages="errors"
              class="required"
              />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="4">
          <validation-provider
            v-slot="{ errors }"
            rules=""
            >
            <v-text-field
              v-model="form.analyte_number"
              :label="$t('CompoundForm.analyte_number')"
              dense
              :error-messages="errors"
              />
          </validation-provider>
         </v-col>
        <v-col cols="4">
          <validation-provider
            v-slot="{ errors }"
            rules=""
            >
            <v-text-field
              v-model="form.nnc_long_number"
              :label="$t('CompoundForm.long_number')"
              dense
              :error-messages="errors"
              />
          </validation-provider>
        </v-col>
        <v-col cols="4">
          <validation-provider
            v-slot="{ errors }"
            rules=""
            >
            <v-text-field
              v-model="form.nnc_short_number"
              :label="$t('CompoundForm.short_number')"
              dense
              :error-messages="errors"
              />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="6">
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-text-field
              v-model="form.name"
              :label="$t('CompoundForm.name')"
              dense
              :error-messages="errors"
              class="required"
              />
          </validation-provider>
        </v-col>
        <v-col cols="6">
           <yes-no-field
             v-model="form.is_name_inn"
             :label="$t('CompoundForm.is_inn')"
             row
             />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <v-textarea
            :label="$t('_global.definition')"
            v-model="form.definition"
            dense
            clearable
            auto-grow
            rows="1"
            />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <multiple-select
            v-model="form.brands"
            :label="$t('CompoundForm.brand_name')"
            :items="brands"
            return-object
            item-text="name"
            />
        </v-col>
      </v-row>
      <v-card style="position: relative">
        <v-card-title style="position: relative">
          {{$t('CompoundForm.substances')}}
        </v-card-title>
        <v-btn
            color="primary"
            absolute
            top
            right
            fab
            x-small
            @click="addSubstance"
            >
            <v-icon>mdi-plus</v-icon>
        </v-btn>
        <v-card-text>
          <v-card v-for="(substance, index) in form.substances" :key="index" class="sub-v-card">
            <v-card-text style="position: relative">
              <substance-field v-model="form.substances[index]" />
            </v-card-text>
            <v-btn
              color="error"
              absolute
              top
              right
              fab
              x-small
              @click="removeSubstance(index)"
              >
              <v-icon>mdi-delete-outline</v-icon>
            </v-btn>
          </v-card>
        </v-card-text>
      </v-card>
    </validation-observer>
  </template>
  <template v-slot:step.dosingDetails="{ step }">
    <validation-observer :ref="`observer_${step}`">
      <v-row>
        <v-col cols="6">
          <v-card style="position: relative">
            <v-card-title style="position: relative">
              {{$t('CompoundForm.doses')}}
            </v-card-title>
            <v-btn
                color="primary"
                absolute
                top
                right
                fab
                x-small
                @click="addDoseValue"
                >
                <v-icon>mdi-plus</v-icon>
            </v-btn>
            <v-card-text>
              <v-card v-for="(doseValue, index) in form.dose_values" :key="index" class="sub-v-card">
                <v-card-text style="position: relative">
                  <numeric-value-with-unit-field
                    v-model="form.dose_values[index]"
                    :label="$t('CompoundForm.dose')"
                    subset="Dose Unit"
                    :initial-value="form.dose_values[index]"
                    />
                </v-card-text>
                <v-btn
                  color="error"
                  absolute
                  top
                  right
                  fab
                  x-small
                  @click="removeDoseValue(index)"
                  >
                  <v-icon>mdi-delete-outline</v-icon>
                </v-btn>
              </v-card>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6">
          <v-card style="position: relative">
            <v-card-title style="position: relative">
              {{$t('CompoundForm.strengths')}}
            </v-card-title>
            <v-btn
                color="primary"
                absolute
                top
                right
                fab
                x-small
                @click="addStrengthValue"
                >
                <v-icon>mdi-plus</v-icon>
            </v-btn>
            <v-card-text>
              <v-card v-for="(strengthValue, index) in form.strength_values" :key="index" class="sub-v-card">
                <v-card-text style="position: relative">
                  <numeric-value-with-unit-field
                    v-model="form.strength_values[index]"
                    :label="$t('CompoundForm.strength')"
                    subset="Strength Unit"
                    :initial-value="form.strength_values[index]"
                    />
                </v-card-text>
                <v-btn
                  color="error"
                  absolute
                  top
                  right
                  fab
                  x-small
                  @click="removeStrengthValue(index)"
                  >
                  <v-icon>mdi-delete-outline</v-icon>
                </v-btn>
              </v-card>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <multiple-select
            v-model="form.dose_frequency_uids"
            :label="$t('CompoundForm.dosing_frequency')"
            :items="frequencies"
            item-text="sponsor_preferred_name"
            item-value="term_uid"
            />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <multiple-select
            v-model="form.route_of_administration_uids"
            :label="$t('CompoundForm.route_of_administration')"
            :items="routesOfAdmin"
            item-text="sponsor_preferred_name"
            item-value="term_uid"
            />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <multiple-select
            v-model="form.dosage_form_uids"
            :label="$t('CompoundForm.dosage_form')"
            :items="dosageForms"
            item-text="sponsor_preferred_name"
            item-value="term_uid"
            />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <multiple-select
            v-model="form.dispensers_uids"
            :label="$t('CompoundForm.dispensed_in')"
            :items="dispensers"
            item-text="sponsor_preferred_name"
            item-value="term_uid"
            />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <multiple-select
            v-model="form.delivery_devices_uids"
            :label="$t('CompoundForm.device')"
            :items="devices"
            item-text="sponsor_preferred_name"
            item-value="term_uid"
            />
        </v-col>
      </v-row>
    </validation-observer>
  </template>
  <template v-slot:step.halfLife="{ step }">
    <validation-observer :ref="`observer_${step}`">
      <v-row>
        <v-col cols="12">
          <numeric-value-with-unit-field
            v-model="form.half_life"
            :label="$t('CompoundForm.half_life')"
            subset="Time Unit"
            :initial-value="form.half_life"
            />
        </v-col>
      </v-row>
      <v-card style="position: relative">
        <v-card-title style="position: relative">
          {{$t('CompoundForm.lag_times')}}
        </v-card-title>
        <v-btn
          color="primary"
          absolute
          top
          right
          fab
          x-small
          @click="addLagTime"
          >
          <v-icon>mdi-plus</v-icon>
        </v-btn>
        <v-card-text>
          <v-card v-for="(lag_time, index) in form.lag_times" :key="index" class="sub-v-card">
            <v-card-text style="position: relative;">
              <v-row>
                <v-col cols="6">
                  <v-autocomplete
                    v-model="form.sdtm_domains[index].uid"
                    :label="$t('CompoundForm.sdtm_domain')"
                    :items="adverseEvents"
                    item-text="sponsor_preferred_name"
                    item-value="term_uid"
                    dense
                    clearable
                    />
                </v-col>
                <v-col cols="6">
                  <numeric-value-with-unit-field
                    v-model="form.lag_times[index]"
                    :label="$t('CompoundForm.lag_time')"
                    subset="Time Unit"
                    :initial-value="form.lag_times[index]"
                    />
                </v-col>
              </v-row>
            </v-card-text>
            <v-btn
              color="error"
              absolute
              top
              right
              fab
              x-small
              @click="removeLagTime(index)"
              >
              <v-icon>mdi-delete-outline</v-icon>
            </v-btn>
          </v-card>
        </v-card-text>
      </v-card>
    </validation-observer>
  </template>
   <template v-slot:step.alias="{ step }">
    <template v-if="compoundUid == null">
      <validation-observer :ref="`observer_${step}`">
        <v-row>
          <v-col cols="12">
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-text-field
                v-model="form.alias_name"
                :label="$t('CompoundAliasForm.name')"
                dense
                clearable
                :error-messages="errors"
                class="required"
                />
            </validation-provider>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-text-field
                v-model="form.alias_name_sentence_case"
                :label="$t('CompoundAliasForm.sentence_case_name')"
                dense
                clearable
                :error-messages="errors"
                class="required"
                />
            </validation-provider>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <yes-no-field
                v-model="form.aliasIsPreferredSynonym"
                :label="$t('CompoundAliasForm.is_preferred_synonym')"
                :error-messages="errors"
                class="required"
                />
            </validation-provider>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <v-textarea
              :label="$t('_global.definition')"
              v-model="form.aliasDefinition"
              dense
              clearable
              auto-grow
              rows="1"
              />
          </v-col>
        </v-row>
      </validation-observer>
    </template>
    <v-row v-else>
      <v-col cols="12">
        <v-simple-table>
          <template v-slot:default>
            <thead>
              <tr class="text-left">
                <th scope="col">{{ $t('CompoundOverview.compound_alias') }}</th>
                <th scope="col">{{ $t('_global.definition') }}</th>
                <th scope="col">{{ $t('CompoundOverview.preferred_alias') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="alias in compoundAliases" :key="alias.uid">
                <td>{{ alias.name }}</td>
                <td>{{ alias.definition }}</td>
                <td>{{ alias.is_preferred_synonym|yesno }}</td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </v-col>
    </v-row>
  </template>
</horizontal-stepper-form>
</template>

<script>
import _isEqual from 'lodash/isEqual'
import brands from '@/api/brands'
import { bus } from '@/main'
import compounds from '@/api/concepts/compounds'
import compoundAliases from '@/api/concepts/compoundAliases'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import lagTimes from '@/api/concepts/lagTimes'
import libConstants from '@/constants/libraries'
import { mapGetters } from 'vuex'
import MultipleSelect from '@/components/tools/MultipleSelect'
import NumericValueWithUnitField from '@/components/tools/NumericValueWithUnitField'
import numericValuesWithUnit from '@/api/concepts/numericValuesWithUnit'
import SubstanceField from './SubstanceField'
import terms from '@/api/controlledTerminology/terms'
import YesNoField from '@/components/tools/YesNoField'

export default {
  components: {
    HorizontalStepperForm,
    MultipleSelect,
    NumericValueWithUnitField,
    SubstanceField,
    YesNoField
  },
  props: {
    compoundUid: String,
    formShown: Boolean
  },
  data () {
    return {
      compound: null,
      adverseEvents: [],
      brands: [],
      devices: [],
      dispensers: [],
      dosageForms: [],
      form: this.getInitialForm(),
      frequencies: [],
      helpItems: [
        'CompoundForm.sponsor_compound',
        'CompoundForm.analyte_number',
        'CompoundForm.long_number',
        'CompoundForm.short_number',
        'CompoundForm.name',
        'CompoundForm.is_inn',
        'CompoundForm.definition',
        'CompoundForm.brand_name',
        'CompoundForm.substance_name',
        'CompoundForm.pharmacological_class',
        'CompoundForm.medrt',
        'CompoundForm.dose',
        'CompoundForm.strength',
        'CompoundForm.dosing_frequency',
        'CompoundForm.route_of_administration',
        'CompoundForm.dosage_form',
        'CompoundForm.dispensed_in',
        'CompoundForm.device',
        'CompoundForm.formulation',
        'CompoundForm.formulation_details',
        'CompoundForm.manufacturing_place',
        'CompoundForm.manufacturing_process',
        'CompoundForm.half_life',
        'CompoundForm.lag_time',
        'CompoundForm.sdtm_domain',
        'CompoundAliasForm.name',
        'CompoundAliasForm.sentence_case_name',
        'CompoundAliasForm.is_preferred_synonym'
      ],
      routesOfAdmin: [],
      compoundAliases: [],
      steps: [
        { name: 'identifiers', title: this.$t('CompoundForm.step1_title') },
        { name: 'dosingDetails', title: this.$t('CompoundForm.step2_title') },
        { name: 'halfLife', title: this.$t('CompoundForm.step4_title') },
        { name: 'alias', title: this.$t('CompoundForm.step5_title') }
      ]
    }
  },
  computed: {
    ...mapGetters({
      substances: 'compounds/substances'
    }),
    title () {
      return (this.compound) ? this.$t('CompoundForm.edit_title') : this.$t('CompoundForm.add_title')
    }
  },
  methods: {
    addDoseValue () {
      this.form.dose_values.push({})
    },
    removeDoseValue (index) {
      this.form.dose_values.splice(index, 1)
    },
    addLagTime () {
      this.form.lag_times.push({})
      this.form.sdtm_domains.push({})
    },
    removeLagTime (index) {
      this.form.lag_times.splice(index, 1)
      this.form.sdtm_domains.splice(index, 1)
    },
    addStrengthValue () {
      this.form.strength_values.push({})
    },
    removeStrengthValue (index) {
      this.form.strength_values.splice(index, 1)
    },
    addSubstance () {
      this.form.substances.push({})
    },
    removeSubstance (index) {
      this.form.substances.splice(index, 1)
    },
    close () {
      this.$emit('close')
      this.form = this.getInitialForm()
      this.$refs.stepper.reset()
      this.$store.commit('form/CLEAR_FORM')
    },
    getInitialForm () {
      return {
        is_sponsor_compound: true,
        dose_values: [{}],
        half_life: {},
        lag_times: [{}],
        sdtm_domains: [{}],
        strength_values: [{}],
        substances: [{}],
        alias: {}
      }
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    async addCompound (data) {
      data.library_name = libConstants.LIBRARY_SPONSOR
      const createdCompound = await compounds.create(data)

      try {
        // Add alias
        data.alias.compound_uid = createdCompound.data.uid
        data.alias.name = data.alias_name
        data.alias.name_sentence_case = data.alias_name_sentence_case
        data.alias.isPreferredSynonym = data.alias_is_preferred_ynonym
        data.alias.library_name = data.library_name
        data.alias.abbreviation = null
        await compoundAliases.create(data.alias)
      } catch (error) {
        // If creation of alias fails, delete the newly created compound
        await compounds.deleteObject(createdCompound.data.uid)
        throw error
      }

      this.$emit('created')
      bus.$emit('notification', { msg: this.$t('CompoundForm.add_success'), type: 'success' })
    },
    async updateCompound (data) {
      data.change_description = this.$t('_global.work_in_progress')
      await compounds.update(this.compound.uid, data)
      this.$emit('updated')
      bus.$emit('notification', { msg: this.$t('CompoundForm.update_success'), type: 'success' })
    },
    async createNumericValue (item) {
      item.library_name = libConstants.LIBRARY_SPONSOR
      const resp = await numericValuesWithUnit.create(item)
      return resp.data.uid
    },
    async createNumericValues (items) {
      const result = []
      for (const item of items) {
        if (item.value && item.unit_definition_uid) {
          result.push(await this.createNumericValue(item))
        }
      }
      return result
    },
    async createLagTime (item) {
      item.library_name = libConstants.LIBRARY_SPONSOR
      const resp = await lagTimes.create(item)
      return resp.data.uid
    },
    async submit () {
      if (this.$store.getters['form/form'] === '' || _isEqual(this.$store.getters['form/form'], JSON.stringify(this.form))) {
        this.close()
        bus.$emit('notification', { type: 'info', msg: this.$t('_global.no_changes') })
        return
      }
      const data = { ...this.form }
      data.name_sentence_case = data.name.toLowerCase()
      data.substance_terms_uids = []
      for (const substance of data.substances) {
        if (substance && substance.term_uid) {
          data.substance_terms_uids.push(substance.term_uid)
        }
      }
      delete data.substances
      data.dose_values_uids = await this.createNumericValues(data.dose_values)
      delete data.dose_values
      data.strength_values_uids = await this.createNumericValues(data.strength_values)
      delete data.strength_values
      if (data.half_life) {
        if (data.half_life.value && data.half_life.unit_definition_uid) {
          data.half_life_uid = await this.createNumericValue(data.half_life)
        }
        delete data.half_life
      }
      data.lag_times_uids = []
      for (const [index, item] of data.lag_times.entries()) {
        if (item.value && item.unit_definition_uid && this.form.sdtm_domains[index].uid) {
          item.sdtm_domain_uid = this.form.sdtm_domains[index].uid
          data.lag_times_uids.push(await this.createLagTime(item))
        }
      }
      delete data.lag_times
      if (data.brands) {
        data.brands_uids = data.brands.map(item => item.uid)
        delete data.brands
      }
      try {
        if (!this.compoundUid) {
          await this.addCompound(data)
        } else {
          await this.updateCompound(data)
        }
        this.close()
      } catch (error) {
        this.$refs.stepper.loading = false
      }
    },
    transformSubstances () {
      this.$set(this.form, 'substances', this.form.substances.map(substance => {
        return this.substances.find(item => item.term_uid === substance.substance_term_uid)
      }))
    }
  },
  mounted () {
    if (this.compoundUid !== null) {
      compounds.getObject(this.compoundUid).then(resp => {
        this.compound = resp.data
      })
    }
    this.$store.dispatch('compounds/fetchSubstances').then(() => {
      this.transformSubstances()
    })
    terms.getByCodelist('frequency', true).then(resp => {
      this.frequencies = resp.data.items
    })
    terms.getByCodelist('routeOfAdministration', true).then(resp => {
      this.routesOfAdmin = resp.data.items
    })
    terms.getByCodelist('dosageForm', true).then(resp => {
      this.dosageForms = resp.data.items
    })
    terms.getByCodelist('dispensedIn', true).then(resp => {
      this.dispensers = resp.data.items
    })
    terms.getByCodelist('deliveryDevice', true).then(resp => {
      this.devices = resp.data.items
    })
    terms.getByCodelist('adverseEvents', true).then(resp => {
      this.adverseEvents = resp.data.items
    })
    brands.getAll().then(resp => {
      this.brands = resp.data
    })
  },
  watch: {
    formShown (value) {
      if (value && this.compoundUid !== null) {
        compounds.getObject(this.compoundUid).then(resp => {
          this.compound = resp.data
        })
      } else {
        this.compound = null
      }
    },
    compound: {
      handler: function (value) {
        if (value) {
          this.form = { ...value }
          this.form.dosage_form_uids = this.form.dosage_forms.map(item => item.term_uid)
          this.form.dose_frequency_uids = this.form.dose_frequencies.map(item => item.term_uid)
          this.form.route_of_administration_uids = this.form.routes_of_administration.map(item => item.term_uid)
          this.form.dispensers_uids = this.form.dispensers.map(item => item.term_uid)
          this.form.delivery_devices_uids = this.form.delivery_devices.map(item => item.term_uid)
          for (const field of ['dose_values', 'strength_values', 'lag_times']) {
            if (!this.form[field].length) {
              this.form[field] = [{}]
            }
          }
          this.form.sdtm_domains = []
          if (this.form.lag_times.length) {
            for (const lagTime of this.form.lag_times) {
              this.form.sdtm_domains.push({ uid: lagTime.sdtm_domain_uid })
            }
          } else {
            this.form.sdtm_domains.push({})
          }
          if (!this.form.substances || !this.form.substances.length) {
            this.$set(this.form, 'substances', [{}])
          }
          if (this.substances.length) {
            this.transformSubstances()
          }

          const params = {
            filters: {
              compound_uid: { v: [value.uid] }
            }
          }
          compoundAliases.getFiltered(params).then(resp => {
            this.compoundAliases = resp.data.items
          })
        }
      },
      immediate: true
    },
    'form.name' (value) {
      if (value && !this.compound) {
        this.$set(this.form, 'alias_name', value)
      }
    },
    'form.alias_name' (value) {
      if (value) {
        this.$set(this.form, 'alias_name_sentence_case', value.toLowerCase())
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.v-btn {
  &--right {
    right: -16px;
  }
}

.sub-v-card {
  margin-bottom: 25px;
}
</style>
