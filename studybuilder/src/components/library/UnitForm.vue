<template>
<simple-form-dialog
  ref="form"
  :title="title"
  :help-items="helpItems"
  :help-text="$t('HelpMessages.units')"
  @close="cancel"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
      <validation-provider
        v-if="!Object.keys(unit).length"
        v-slot="{ errors }"
        name="Library"
        rules="required"
        >
        <v-row>
          <v-col>
            <v-select
              v-model="form.library_name"
              :label="$t('_global.library')"
              data-cy="unit-library"
              :items="libraries"
              item-text="name"
              item-value="name"
              :error-messages="errors"
              dense
              clearable
              ></v-select>
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        rules="required"
        >
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="form.name"
              autocomplete="off"
              :label="$t('_global.name')"
              data-cy="unit-name"
              :error-messages="errors"
              dense
              clearable
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        rules="required"
        >
        <v-row>
          <v-col cols="12">
            <v-autocomplete
              v-model="form.ct_units"
              :label="$t('UnitForm.ct_term')"
              data-cy="unit-codelist-term"
              :items="unitTerms"
              item-text="sponsor_preferred_name"
              item-value="term_uid"
              single-line
              multiple
              :error-messages="errors"
              dense
              clearable
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        rules=""
        >
        <v-row>
          <v-col>
            <v-select
              v-model="form.unit_subsets"
              label="Unit Subset"
              data-cy="unit-subset"
              :items="unitSubsets"
              item-text="sponsor_preferred_name"
              item-value="term_uid"
              single-line
              multiple
              :error-messages="errors"
              dense
              clearable
              />
          </v-col>
        </v-row>
      </validation-provider>
      <v-row>
        <v-col cols="6">
          <v-switch
            v-model="form.convertible_unit"
            :label="$t('UnitForm.convertible_unit')"
            data-cy="convertible-unit"
            />
          <v-switch
            v-model="form.display_unit"
            :label="$t('UnitForm.display_unit')"
            data-cy="display-unit"
            />
          <v-switch
            v-model="form.master_unit"
            :label="$t('UnitForm.master_unit')"
            data-cy="master-unit"
            />
          <v-switch
            v-model="form.si_unit"
            :label="$t('UnitForm.si_unit')"
            data-cy="si-unit"
            />
          <v-switch
            v-model="form.us_conventional_unit"
            :label="$t('UnitForm.us_unit')"
            data-cy="us-unit"
            />
        </v-col>
        <v-col>
          <validation-provider
            v-slot="{ errors }"
            rules=""
            >
            <ucum-unit-field v-model="form.ucum" :error-messages="errors" />
          </validation-provider>
        </v-col>
      </v-row>
      <validation-provider
        v-slot="{ errors }"
        rules=""
        >
        <v-row>
          <v-col>
            <v-autocomplete
              v-model="form.unit_dimension"
              :label="$t('UnitForm.dimension')"
              data-cy="unit-dimension"
              :items="unitDimensions"
              item-text="sponsor_preferred_name"
              item-value="term_uid"
              :error-messages="errors"
              clearable
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        rules=""
        >
        <v-row>
          <v-col>
            <v-text-field
              v-model="form.legacy_code"
              :label="$t('UnitForm.legacy_code')"
              data-cy="unit-legacy-code"
              :error-messages="errors"
              dense
              clearable
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        rules=""
        >
        <v-row>
          <v-col>
            <v-text-field
              v-model="form.molecular_weight_conv_expon"
              :label="$t('UnitForm.molecular_weight')"
              data-cy="unit-molecular-weight"
              :error-messages="errors"
              dense
              clearable
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        rules=""
        >
        <v-row>
          <v-col>
            <v-text-field
              v-model="form.conversion_factor_to_master"
              :label="$t('UnitForm.conversion_factor')"
              data-cy="unit-conversion-factor"
              :error-messages="errors"
              dense
              clearable
              />
          </v-col>
        </v-row>
      </validation-provider>
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>
import { bus } from '@/main'
import terms from '@/api/controlledTerminology/terms'
import libraries from '@/api/libraries'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import StudybuilderUCUMField from '@/components/tools/StudybuilderUCUMField'

export default {
  components: {
    SimpleFormDialog,
    'ucum-unit-field': StudybuilderUCUMField
  },
  props: {
    unit: Object,
    open: Boolean
  },
  computed: {
    title () {
      return (this.objective)
        ? this.$t('UnitForm.edit_title')
        : this.$t('UnitForm.add_title')
    }
  },
  data () {
    return {
      form: this.getInitialForm(),
      helpItems: [
        'UnitForm.ct_term',
        'UnitForm.convertible_unit',
        'UnitForm.display_unit',
        'UnitForm.master_unit',
        'UnitForm.si_unit',
        'UnitForm.us_unit',
        'UnitForm.dimension',
        'UnitForm.legacy_code',
        'UnitForm.add_success',
        'UnitForm.molecular_weight',
        'UnitForm.conversion_factor'
      ],
      libraries: [],
      unitTerms: [],
      ucumUnits: [],
      unitDimensions: [],
      unitSubsets: []
    }
  },
  methods: {
    getInitialForm () {
      return {
        convertible_unit: false,
        display_unit: false,
        master_unit: false,
        si_unit: false,
        us_conventional_unit: false
      }
    },
    async cancel () {
      if (this.form.library_name === undefined) {
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
    close () {
      this.$emit('close')
      this.form = this.getInitialForm()
      this.$refs.observer.reset()
    },
    async submit () {
      const isValid = await this.$refs.observer.validate()
      if (!isValid) return
      this.$refs.form.working = true
      if (this.form.ucum && this.form.ucum.term_uid) {
        this.$set(this.form, 'ucum', this.form.ucum.term_uid)
      }
      if (Object.keys(this.unit).length !== 0) {
        try {
          const args = {
            uid: this.unit.uid,
            data: this.form
          }
          await this.$store.dispatch('units/updateUnit', args)
          bus.$emit('notification', { msg: 'update success' })
          this.close()
        } finally {
          this.$refs.form.working = false
        }
      } else {
        try {
          await this.$store.dispatch('units/addUnit', this.form)
          bus.$emit('notification', { msg: this.$t('UnitForm.add_success') })
          this.close()
        } finally {
          this.$refs.form.working = false
        }
      }
    }
  },
  mounted () {
    terms.getByCodelist('units', true).then(resp => {
      this.unitTerms = resp.data.items
    })
    terms.getByCodelist('unitDimensions').then(resp => {
      this.unitDimensions = resp.data.items
    })
    terms.getByCodelist('unitSubsets').then(resp => {
      this.unitSubsets = resp.data.items
    })
    libraries.get(1).then(resp => {
      this.libraries = resp.data
    })
    if (Object.keys(this.unit).length !== 0) {
      this.form = JSON.parse(JSON.stringify(this.unit))
      this.$set(this.form, 'ct_units', this.unit.ct_units.map(el => el.term_uid))
      this.$set(this.form, 'unit_subsets', this.unit.unit_subsets.map(el => el.term_uid))
      this.$set(this.form, 'ucum', this.unit.ucum.term_uid)
      this.$set(this.form, 'unit_dimension', this.unit.unit_dimension.term_uid)
    }
  },
  watch: {
    unit (value) {
      if (Object.keys(value).length !== 0) {
        this.form = JSON.parse(JSON.stringify(value))
        this.$set(this.form, 'ct_units', this.unit.ct_units.map(el => el.term_uid))
        this.$set(this.form, 'unit_subsets', this.unit.unit_subsets.map(el => el.term_uid))
        this.$set(this.form, 'ucum', this.unit.ucum.term_uid)
        this.$set(this.form, 'unit_dimension', this.unit.unit_dimension.term_uid)
      }
    }
  }
}
</script>
