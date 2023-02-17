<template>
<simple-form-dialog
  ref="form"
  :title="title"
  :help-items="helpItems"
  @close="cancel"
  @submit="submit"
  :open="open"
  max-width="1000px"
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
              :label="$t('CrfExtensions.ele_name')"
              v-model="form.name"
              dense
              clearable
              :error-messages="errors"
            />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="6">
          <v-select
            :disabled="editItem.uid !== undefined"
            v-model="existingAttribute"
            :label="$t('CrfExtensions.related_attr')"
            :items="attributes"
            return-object
            item-text="name"
            item-value="uid"
            dense
            clearable
            />
        </v-col>
        <v-col>
          <v-btn
            class="ml-2"
            dark
            small
            color="primary"
            @click="addExistingAttribute"
            :disabled="editItem.uid !== undefined"
            >
            {{ $t('CrfExtensions.add_existing_attr') }}
          </v-btn>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="5">
          <v-text-field
            :disabled="editItem.uid !== undefined"
            :label="$t('CrfExtensions.attr_name')"
            v-model="newAttribute.name"
            dense
            clearable
          />
        </v-col>
        <v-col cols="4">
          <v-select
            :disabled="editItem.uid !== undefined"
            v-model="newAttribute.data_type"
            :label="$t('CrfExtensions.data_type')"
            :items="dataTypes"
            item-text="code_submission_value"
            item-value="code_submission_value"
            dense
            clearable
            />
        </v-col>
        <v-col cols="3">
          <v-btn
            :disabled="editItem.uid !== undefined"
            class="ml-2"
            dark
            small
            color="primary"
            @click="addNewAttribute"
            >
            {{ $t('CrfExtensions.add_new_attr') }}
          </v-btn>
        </v-col>
      </v-row>
      <v-row v-for="attr in attributesToCreate" :key="attr.name">
        <v-col cols="5">
          <v-text-field
            :disabled="editItem.uid !== undefined"
            :label="$t('CrfExtensions.attr_name')"
            v-model="attr.name"
            dense
            clearable/>
        </v-col>
        <v-col cols="4">
          <v-select
            :disabled="editItem.uid !== undefined"
            v-model="attr.data_type"
            :label="$t('CrfExtensions.data_type')"
            :items="dataTypes"
            item-text="code_submission_value"
            item-value="code_submission_value"
            dense
            clearable
            />
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
    editItem: Object,
    parentUid: String,
    attributes: Array
  },
  computed: {
    title () {
      return (this.editItem.uid)
        ? this.$t('CrfExtensions.edit_ele')
        : this.$t('CrfExtensions.new_ele')
    }
  },
  data () {
    return {
      form: {},
      helpItems: [],
      dataTypes: [],
      existingAttribute: {},
      newAttribute: {},
      attributesToCreate: []
    }
  },
  mounted () {
    terms.getAttributesByCodelist('dataType').then(resp => {
      this.dataTypes = resp.data.items
    })
  },
  methods: {
    addNewAttribute () {
      this.attributesToCreate.push(this.newAttribute)
      this.newAttribute = {}
    },
    addExistingAttribute () {
      this.attributesToCreate.push(this.existingAttribute)
      this.existingAttribute = {}
    },
    async cancel () {
      this.close()
    },
    close () {
      this.$refs.observer.reset()
      this.attributesToCreate = []
      this.form = {}
      this.$emit('close')
    },
    async submit () {
      const valid = await this.$refs.observer.validate()
      if (!valid) {
        return
      }
      this.$set(this.form, 'vendor_namespace_uid', this.parentUid)
      let elementUid = ''
      await crfs.createElement(this.form).then(resp => {
        elementUid = resp.data.uid
      })
      if (this.attributesToCreate.length > 0) {
        for (const attr in this.attributesToCreate) {
          this.attributesToCreate[attr].vendor_element_uid = elementUid
          await crfs.createAttribute(this.attributesToCreate[attr])
        }
      }
      this.close()
    },
    initForm (item) {
      this.form = item
      this.attributes.forEach(attr => {
        if (attr.vendor_element && attr.vendor_element.uid === this.editItem.uid) {
          this.attributesToCreate.push(attr)
        }
      })
    }
  },
  watch: {
    editItem (value) {
      this.initForm(value)
    }
  }
}
</script>
