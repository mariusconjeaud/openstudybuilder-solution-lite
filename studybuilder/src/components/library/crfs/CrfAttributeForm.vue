<template>
<simple-form-dialog
  ref="form"
  :title="title"
  :help-items="helpItems"
  @close="cancel"
  @submit="submit"
  :open="open">
  <template v-slot:body>
    <validation-observer ref="observer">
      <v-row>
        <v-col cols="6">
          <validation-provider
            v-slot="{ errors }"
            rules="required">
            <v-text-field
              :label="$t('CrfExtensions.attr_name')"
              v-model="form.name"
              dense
              clearable
              :error-messages="errors"/>
          </validation-provider>
        </v-col>
        <v-col cols="6">
          <validation-provider
            v-slot="{ errors }"
            rules="required">
            <v-select
              v-model="form.data_type"
              :label="$t('CrfExtensions.data_type')"
              :items="dataTypes"
              item-text="code_submission_value"
              item-value="code_submission_value"
              :error-messages="errors"
              dense
              clearable/>
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="6" v-if="parentType === crfTypes.NAMESPACE">
          <v-select
            v-model="form.compatible_types"
            :label="$t('CrfExtensions.compatible_types')"
            :items="compatibleTypes"
            dense
            multiple
            clearable/>
        </v-col>
        <v-col cols="6">
          <v-text-field
            :label="$t('CrfExtensions.regex_expression')"
            v-model="form.value_regex"
            dense
            clearable/>
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
import crfTypes from '@/constants/crfTypes'

export default {
  components: {
    SimpleFormDialog
  },
  props: {
    open: Boolean,
    editItem: Object,
    parentUid: String,
    parentType: String
  },
  computed: {
    title () {
      return (this.editItem.uid)
        ? this.$t('CrfExtensions.edit_attr')
        : this.$t('CrfExtensions.new_attr')
    }
  },
  created () {
    this.crfTypes = crfTypes
  },
  data () {
    return {
      form: {},
      helpItems: [],
      dataTypes: [],
      compatibleTypes: ['FormDef', 'ItemGroupDef', 'ItemDef', 'ItemGroupRef', 'ItemRef']
    }
  },
  mounted () {
    terms.getAttributesByCodelist('dataType').then(resp => {
      this.dataTypes = resp.data.items
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
      if (this.parentType === crfTypes.NAMESPACE) {
        this.$set(this.form, 'vendor_namespace_uid', this.parentUid)
      } else {
        this.$set(this.form, 'vendor_element_uid', this.parentUid)
      }
      if (this.editItem.uid) {
        await crfs.editAttribute(this.editItem.uid, this.form)
      } else {
        await crfs.createAttribute(this.form)
      }
      this.close()
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
