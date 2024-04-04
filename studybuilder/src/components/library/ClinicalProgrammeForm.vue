<template>
<simple-form-dialog
  ref="form"
  :title="$t('ClinicalProgrammeForm.title')"
  :help-text="$t('_help.ClinicalProgrammeForm.general')"
  :help-items="helpItems"
  @close="close"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
      <v-row>
        <v-col cols="12">
          <validation-provider
            v-slot="{ errors }"
            name="Name"
            rules="required"
            >
            <v-text-field
              id="name"
              :label="$t('ClinicalProgrammeForm.name')"
              v-model="form.name"
              :error-messages="errors"
              dense
              clearable
              data-cy="clinical-programme-name"
              />
          </validation-provider>
        </v-col>
      </v-row>
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>
// import { mapGetters } from 'vuex'
import { bus } from '@/main'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import programmes from '@/api/clinicalProgrammes'

export default {
  components: {
    SimpleFormDialog
  },
  props: {
    editedStudy: Object,
    open: Boolean
  },
  data () {
    return {
      form: {},
      helpItems: [
        'ClinicalProgrammeForm.name'
      ]
    }
  },
  methods: {
    async close () {
      if (this.form.name) {
        const options = {
          type: 'warning',
          cancelLabel: this.$t('_global.cancel'),
          agreeLabel: this.$t('_global.continue')
        }
        if (await this.$refs.form.confirm(this.$t('_global.cancel_changes'), options)) {
          this.$emit('close')
        }
      } else {
        this.$emit('close')
      }
    },
    initForm (value) {
      this.form = {
        name: ''
      }
    },
    async addProgramme () {
      const data = JSON.parse(JSON.stringify(this.form))
      const resp = await programmes.create(data)
      bus.$emit('notification', { msg: this.$t('ClinicalProgrammes.add_success') })
      this.$emit('created', resp.data)
    },

    async submit () {
      try {
        await this.addProgramme()
        this.$emit('close')
      } finally {
        this.$refs.form.working = false
      }
    }
  },
  mounted () {
    this.initForm()
  },
  watch: {
  }
}
</script>
