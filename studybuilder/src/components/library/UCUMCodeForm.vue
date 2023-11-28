<template>
<simple-form-dialog
  ref="form"
  :title="$t('UCUMCodeForm.title')"
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
            rules="required"
            >
            <v-text-field
              v-model="form.name"
              :label="$t('_global.name')"
              :error-messages="errors"
              dense
              clearable/>
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <validation-provider
            v-slot="{ errors }"
            rules=""
            >
            <v-textarea
              v-model="form.definition"
              :label="$t('UCUM.description')"
              :error-messages="errors"
              dense
              clearable
              auto-grow
              rows="1"
              />
          </validation-provider>
        </v-col>
      </v-row>
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>
import { bus } from '@/main'
import dictionaries from '@/api/dictionaries'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'

export default {
  components: {
    SimpleFormDialog
  },
  props: {
    codelistUid: String,
    open: Boolean
  },
  data () {
    return {
      helpItems: [
        'UCUM.code',
        'UCUM.description'
      ],
      form: {}
    }
  },
  methods: {
    close () {
      this.$refs.form.working = false
      this.form = {}
      this.$emit('close')
    },
    async submit () {
      this.$set(this.form, 'library_name', 'UCUM')
      this.$set(this.form, 'name_sentence_case', this.form.name)
      this.$set(this.form, 'dictionary_id', this.form.name)
      dictionaries.create(this.form).then(resp => {
        bus.$emit('notification', { msg: this.$t('DictionaryTermForm.create_success') })
        this.$emit('save')
        this.close()
      }, _err => {
        this.$refs.form.working = false
      })
    }
  },
  watch: {
    codelistUid () {
      this.form.codelist_uid = this.codelistUid
    }
  }
}
</script>
