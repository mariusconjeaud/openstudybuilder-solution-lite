<template>
<v-card color="dfltBackground">
  <v-card-title>
    <span class="dialog-title">{{ $t('CodelistTermNamesForm.title') }}</span>
    <help-button-with-panels :title="$t('_global.help')" :items="helpItems" />
  </v-card-title>
  <v-card-text class="mt-4">
    <div class="white pa-4">
      <validation-observer ref="observer">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-text-field
            v-model="form.name_submission_value"
            :label="$t('CodelistTermCreationForm.name_submission_value')"
            :error-messages="errors"
            clearable
            />
        </validation-provider>
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-text-field
            v-model="form.code_submission_value"
            :label="$t('CodelistTermCreationForm.code_submission_value')"
            :error-messages="errors"
            clearable
            />
        </validation-provider>
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-text-field
            v-model="form.nci_preferred_name"
            :label="$t('CodelistTermCreationForm.nci_pref_name')"
            :error-messages="errors"
            clearable
            />
        </validation-provider>
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-textarea
            v-model="form.definition"
            :label="$t('CodelistTermCreationForm.definition')"
            :error-messages="errors"
            clearable
            rows="1"
            auto-grow
            />
        </validation-provider>
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-textarea
            v-model="form.change_description"
            :label="$t('HistoryTable.change_description')"
            :error-messages="errors"
            :rows="1"
            class="white py-2"
            auto-grow
            />
        </validation-provider>
      </validation-observer>
    </div>
  </v-card-text>
  <v-card-actions>
    <v-spacer></v-spacer>
    <v-btn
      class="secondary-btn"
      color="white"
      @click="cancel"
      >
      {{ $t('_global.cancel') }}
    </v-btn>
    <v-btn
      color="secondary"
      :loading="working"
      @click="submit"
      >
      {{ $t('_global.save') }}
    </v-btn>
  </v-card-actions>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</v-card>
</template>

<script>
import { bus } from '@/main'
import controlledTerminology from '@/api/controlledTerminology'
import HelpButtonWithPanels from '@/components/tools/HelpButtonWithPanels'
import _isEqual from 'lodash/isEqual'
import ConfirmDialog from '@/components/tools/ConfirmDialog'

export default {
  props: ['value'],
  components: {
    HelpButtonWithPanels,
    ConfirmDialog
  },
  data () {
    return {
      form: {},
      helpItems: [
        'CodelistTermCreationForm.name_submission_value',
        'CodelistTermCreationForm.code_submission_value',
        'CodelistTermCreationForm.nci_pref_name',
        'CodelistTermCreationForm.definition'
      ],
      working: false
    }
  },
  methods: {
    async cancel () {
      if (this.$store.getters['form/form'] === '' || _isEqual(this.$store.getters['form/form'], JSON.stringify(this.form))) {
        this.close()
      } else {
        const options = {
          type: 'warning',
          cancelLabel: this.$t('_global.cancel'),
          agreeLabel: this.$t('_global.continue')
        }
        if (await this.$refs.confirm.open(this.$t('_global.cancel_changes'), options)) {
          this.close()
        }
      }
    },
    close () {
      this.$emit('close')
      this.$store.commit('form/CLEAR_FORM')
      this.form.change_description = ''
    },
    async submit () {
      const isValid = await this.$refs.observer.validate()
      if (!isValid) return
      this.working = true
      try {
        const resp = await controlledTerminology.updateCodelistTermAttributes(this.value.term_uid, this.form)
        this.$emit('input', resp.data)
        bus.$emit('notification', { msg: this.$t('CodelistTermNamesForm.update_success') })
        this.close()
      } finally {
        this.working = false
      }
    }
  },
  watch: {
    value: {
      handler (val) {
        if (val) {
          this.form = {
            name_submission_value: val.name_submission_value,
            code_submission_value: val.code_submission_value,
            nci_preferred_name: val.nci_preferred_name,
            definition: val.definition
          }
          this.$store.commit('form/SET_FORM', this.form)
        }
      },
      immediate: true
    }
  }
}
</script>
