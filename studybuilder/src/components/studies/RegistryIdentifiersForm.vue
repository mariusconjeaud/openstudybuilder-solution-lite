<template>
<simple-form-dialog
  ref="form"
  :title="$t('RegistryIdentifiersForm.title')"
  :help-items="helpItems"
  @close="cancel"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
      <v-container>
        <not-applicable-field
          :clean-function="clearCtGovId"
          :checked="form.ct_gov_id_null_value_code ? true : false">
          <template v-slot:mainField="{ notApplicable }">
            <validation-provider
              v-slot="{ errors }"
              name="CTGovID"
              >
              <v-text-field
                id="ct_gov_id"
                :data-cy="$t('RegistryIdentifiersForm.ctgovid')"
                :label="$t('RegistryIdentifiersForm.ctgovid')"
                v-model="form.ct_gov_id"
                :error-messages="errors"
                dense
                clearable
                :disabled="notApplicable"
                autocomplete="off"
                ></v-text-field>
            </validation-provider>
          </template>
        </not-applicable-field>
        <not-applicable-field
          :clean-function="clearEudractId"
          :checked="form.eudract_id_null_value_code ? true : false">
          <template v-slot:mainField="{ notApplicable }">
            <validation-provider
              v-slot="{ errors }"
              name="EUDRACTID"
              >
              <v-text-field
                id="eudract_id"
                :data-cy="$t('RegistryIdentifiersForm.eudractid')"
                :label="$t('RegistryIdentifiersForm.eudractid')"
                v-model="form.eudract_id"
                :error-messages="errors"
                dense
                clearable
                :disabled="notApplicable"
                autocomplete="off"
                ></v-text-field>
            </validation-provider>
          </template>
        </not-applicable-field>
        <not-applicable-field
          :clean-function="clearUniversalTrialNumberUTN"
          :checked="form.universal_trial_number_utn_null_value_code ? true : false">
          <template v-slot:mainField="{ notApplicable }">
            <validation-provider
              v-slot="{ errors }"
              name="UTN"
              >
              <v-text-field
                id="utn"
                :data-cy="$t('RegistryIdentifiersForm.utn')"
                :label="$t('RegistryIdentifiersForm.utn')"
                v-model="form.universal_trial_number_utn"
                :error-messages="errors"
                dense
                clearable
                :disabled="notApplicable"
                autocomplete="off"
                ></v-text-field>
            </validation-provider>
          </template>
        </not-applicable-field>
        <not-applicable-field
          :clean-function="clearJapaneseTrialRegistryIdJAPIC"
          :checked="form.japanese_trial_registry_id_japic_null_value_code ? true : false">
          <template v-slot:mainField="{ notApplicable }">
            <validation-provider
              v-slot="{ errors }"
              name="Japic"
              >
              <v-text-field
                id="japic"
                :data-cy="$t('RegistryIdentifiersForm.japic')"
                :label="$t('RegistryIdentifiersForm.japic')"
                v-model="form.japanese_trial_registry_id_japic"
                :error-messages="errors"
                dense
                clearable
                :disabled="notApplicable"
                autocomplete="off"
                ></v-text-field>
            </validation-provider>
          </template>
        </not-applicable-field>
        <not-applicable-field
          :clean-function="clearInvestigationalNewDrugApplicationNumberIND"
          :checked="form.investigational_new_drug_application_number_ind_null_value_code ? true : false">
          <template v-slot:mainField="{ notApplicable }">
            <validation-provider
              v-slot="{ errors }"
              name="IND"
              >
              <v-text-field
                id="ind"
                :data-cy="$t('RegistryIdentifiersForm.ind')"
                :label="$t('RegistryIdentifiersForm.ind')"
                v-model="form.investigational_new_drug_application_number_ind"
                :error-messages="errors"
                dense
                clearable
                :disabled="notApplicable"
                autocomplete="off"
                ></v-text-field>
            </validation-provider>
          </template>
        </not-applicable-field>
      </v-container>
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>
import _isEqual from 'lodash/isEqual'
import { mapGetters } from 'vuex'
import { bus } from '@/main'
import NotApplicableField from '@/components/tools/NotApplicableField'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'

export default {
  components: {
    NotApplicableField,
    SimpleFormDialog
  },
  props: {
    identifiers: Object,
    open: Boolean
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    })
  },
  data () {
    return {
      form: JSON.parse(JSON.stringify(this.identifiers)),
      helpItems: [
        'NullFlavorSelect.label',
        'RegistryIdentifiersForm.ctgovid',
        'RegistryIdentifiersForm.eudractid',
        'RegistryIdentifiersForm.utn',
        'RegistryIdentifiersForm.japic'
      ]
    }
  },
  watch: {
    identifiers (value) {
      this.form = JSON.parse(JSON.stringify(value))
    }
  },
  methods: {
    clearCtGovId () {
      this.$set(this.form, 'ct_gov_id', null)
      if (this.form.ct_gov_id_null_value_code) {
        this.$set(this.form, 'ct_gov_id_null_value_code', null)
      } else {
        this.$set(this.form, 'ct_gov_id_null_value_code', { term_uid: this.$t('_global.na_uid'), name: this.$t('_global.not_applicable_full_name') })
      }
    },
    clearEudractId () {
      this.$set(this.form, 'eudract_id', null)
      if (this.form.eudract_id_null_value_code) {
        this.$set(this.form, 'eudract_id_null_value_code', null)
      } else {
        this.$set(this.form, 'eudract_id_null_value_code', { term_uid: this.$t('_global.na_uid'), name: this.$t('_global.not_applicable_full_name') })
      }
    },
    clearUniversalTrialNumberUTN () {
      this.$set(this.form, 'universal_trial_number_utn', null)
      if (this.form.universal_trial_number_utn_null_value_code) {
        this.$set(this.form, 'universal_trial_number_utn_null_value_code', null)
      } else {
        this.$set(this.form, 'universal_trial_number_utn_null_value_code', { term_uid: this.$t('_global.na_uid'), name: this.$t('_global.not_applicable_full_name') })
      }
    },
    clearJapaneseTrialRegistryIdJAPIC () {
      this.$set(this.form, 'japanese_trial_registry_id_japic', null)
      if (this.form.japanese_trial_registry_id_japic_null_value_code) {
        this.$set(this.form, 'japanese_trial_registry_id_japic_null_value_code', null)
      } else {
        this.$set(this.form, 'japanese_trial_registry_id_japic_null_value_code', { term_uid: this.$t('_global.na_uid'), name: this.$t('_global.not_applicable_full_name') })
      }
    },
    clearInvestigationalNewDrugApplicationNumberIND () {
      this.$set(this.form, 'investigational_new_drug_application_number_ind', null)
      if (this.form.investigational_new_drug_application_number_ind_null_value_code) {
        this.$set(this.form, 'investigational_new_drug_application_number_ind_null_value_code', null)
      } else {
        this.$set(this.form, 'investigational_new_drug_application_number_ind_null_value_code', { term_uid: this.$t('_global.na_uid'), name: this.$t('_global.not_applicable_full_name') })
      }
    },
    close () {
      this.$emit('close')
      this.$refs.observer.reset()
    },
    async cancel () {
      if (_isEqual(this.identifiers, this.form)) {
        this.close()
        return
      }
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (await this.$refs.form.confirm(this.$t('_global.cancel_changes'), options)) {
        this.close()
      }
    },
    unsetValues () {
      this.$set(this.form, 'ct_gov_id', null)
      this.$set(this.form, 'eudract_id', null)
      this.$set(this.form, 'universal_trial_number_utn', null)
      this.$set(this.form, 'japanese_trial_registry_id_japic', null)
      this.$set(this.form, 'investigational_new_drug_application_number_ind', null)
    },
    async submit () {
      if (_isEqual(this.identifiers, this.form)) {
        bus.$emit('notification', { msg: this.$t('_global.no_changes'), type: 'info' })
        this.close()
        return
      }
      const valid = await this.$refs.observer.validate()
      if (!valid) {
        return
      }
      const data = {
        registry_identifiers: this.form
      }
      this.$refs.form.working = true
      try {
        await this.$store.dispatch('manageStudies/editStudyIdentification', [this.selectedStudy.uid, data])
        this.$emit('updated', this.form)
        bus.$emit('notification', { msg: this.$t('RegistryIdentifiersForm.update_success') })
        this.close()
      } finally {
        this.$refs.form.working = false
      }
    }
  }
}
</script>
