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
              :label="$t('CrfExtensions.attr_name')"
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
            <v-select
              v-model="form.data_type"
              :label="$t('CrfExtensions.data_type')"
              :items="dataTypes"
              item-text="code_submission_value"
              item-value="code_submission_value"
              :error-messages="errors"
              dense
              clearable
              />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="6">
          <v-text-field
              :label="$t('CrfExtensions.regex_expression')"
              v-model="form.value_regex"
              dense
              clearable
            />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-select
              :disabled="editItem.uid !== undefined"
              v-model="form.parent"
              :label="$t('CrfExtensions.parent')"
              :items="parents"
              return-object
              item-text="name"
              item-value="uid"
              :error-messages="errors"
              dense
              clearable
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
import terms from '@/api/controlledTerminology/terms'

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
        ? this.$t('CrfExtensions.new_attr')
        : this.$t('CrfExtensions.edit_attr')
    }
  },
  data () {
    return {
      form: {},
      helpItems: [],
      dataTypes: [],
      parents: []
    }
  },
  mounted () {
    terms.getAttributesByCodelist('dataType').then(resp => {
      this.dataTypes = resp.data.items
    })
    const params = {
      page_size: 0
    }
    crfs.getAllNamespaces(params).then((resp) => {
      this.parents = this.parents.concat(resp.data.items)
    })
    crfs.getAllElements(params).then((resp) => {
      this.parents = this.parents.concat(resp.data.items)
    })
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
      if (this.form.parent.url) {
        this.$set(this.form, 'vendor_namespace_uid', this.form.parent.uid)
        delete this.form.vendor_element_uid
      } else {
        this.$set(this.form, 'vendor_element_uid', this.form.parent.uid)
        delete this.form.vendor_namespace_uid
      }
      if (this.editItem.uid) {
        crfs.editAttribute(this.editItem.uid, this.form).then(() => {
          this.close()
        })
      } else {
        crfs.createAttribute(this.form).then(() => {
          this.close()
        })
      }
    },
    initForm (item) {
      this.form = item
      this.$set(this.form, 'parent', item.vendor_namespace ? item.vendor_namespace : item.vendor_element)
    }
  },
  watch: {
    editItem (value) {
      this.initForm(value)
    }
  }
}
</script>
