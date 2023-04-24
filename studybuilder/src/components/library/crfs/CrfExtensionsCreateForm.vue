<template>
<simple-form-dialog
  ref="form"
  :title="title"
  :help-items="helpItems"
  @close="cancel"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
      <v-row>
        <v-col cols="6">
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-text-field
              :label="$t('_global.name')"
              v-model="form.name"
              dense
              clearable
              :error-messages="errors"
            />
          </validation-provider>
        </v-col>
        <v-col cols="6">
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-text-field
              :label="$t('CrfExtensions.prefix')"
              v-model="form.prefix"
              dense
              clearable
              :error-messages="errors"
            />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-text-field
              :label="$t('CrfExtensions.url')"
              v-model="form.url"
              dense
              clearable
              :error-messages="errors"
            />
          </validation-provider>
        </v-col>
      </v-row>
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import crfs from '@/api/crfs'

export default {
  components: {
    SimpleFormDialog
  },
  props: {
    open: Boolean,
    editItem: Object
  },
  computed: {
    title () {
      return (this.editItem.uid)
        ? this.$t('CrfExtensions.edit_namespace')
        : this.$t('CrfExtensions.new_namespace')
    }
  },
  data () {
    return {
      form: {},
      helpItems: []
    }
  },
  methods: {
    async cancel () {
      this.close()
    },
    close () {
      this.$refs.observer.reset()
      this.$emit('close')
    },
    async submit () {
      const valid = await this.$refs.observer.validate()
      if (!valid) {
        return
      }
      if (this.editItem.uid) {
        crfs.editNamespace(this.editItem.uid, this.form).then(() => {
          this.close()
        })
      } else {
        crfs.createNamespace(this.form).then(() => {
          this.close()
        })
      }
    },
    initForm (item) {
      this.form = item
    }
  },
  watch: {
    editItem (value) {
      this.initForm(value)
    }
  }
}
</script>
