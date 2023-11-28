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
      <v-row v-if="editItem.uid === undefined">
        <v-col cols="6">
          <v-select
            v-model="attribute"
            :label="$t('CrfExtensions.add_existing_attr')"
            :items="existingAttributes"
            return-object
            item-text="name"
            item-value="uid"
            dense
            clearable
            @change="addExistingAttribute"
            />
        </v-col>
        <div class="mt-6">
          {{ $t('_global.or') }}
        </div>
        <v-col cols="3">
          <v-btn
            dark
            small
            class="mt-2"
            color="primary"
            @click="addNewAttribute"
            >
            {{ $t('CrfExtensions.add_new_attr') }}
          </v-btn>
        </v-col>
      </v-row>
      <v-row v-for="attr in attributesToCreate" :key="attr.key">
        <v-col cols="3">
          <v-text-field
            :disabled="editItem.uid !== undefined"
            :label="$t('CrfExtensions.attr_name')"
            v-model="attr.name"
            dense
            clearable/>
        </v-col>
        <v-col cols="3">
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
        <v-col cols="3">
          <v-btn
            :disabled="editItem.uid !== undefined"
            class="ml-2"
            dark
            small
            color="primary"
            @click="removeAttribute(attr)"
            icon
            >
            <v-icon>mdi-delete-outline</v-icon>
          </v-btn>
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
      attribute: {},
      attributesKeyIndex: 0,
      existingAttributes: [],
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
      if (!this.attributesToCreate.find(attr => attr.name === '')) {
        this.attributesToCreate.push({ key: this.attributesKeyIndex, name: '', data_type: '' })
        this.attributesKeyIndex += 1
      }
    },
    addExistingAttribute (attribute) {
      if (attribute) {
        this.attributesToCreate.push(attribute)
        this.existingAttributes = this.existingAttributes.filter(attr => attr.uid !== attribute.uid)
        this.attribute = {}
      }
    },
    removeAttribute (attribute) {
      this.attributesToCreate = this.attributesToCreate.filter(attr => attr.key !== attribute.key)
      if (attribute.uid) {
        this.existingAttributes.push(attribute)
      }
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
      this.$set(this.form, 'vendor_namespace_uid', this.parentUid)
      if (this.form.uid) {
        this.$set(this.form, 'change_description', this.$t('_global.change_description'))
        await crfs.editElement(this.form.uid, this.form)
      } else {
        let elementUid = ''
        await crfs.createElement(this.form).then(resp => {
          elementUid = resp.data.uid
        })
        if (this.attributesToCreate.length > 0 && elementUid !== '') {
          for (const attr of this.attributesToCreate) {
            delete attr.compatible_types
            attr.vendor_element_uid = elementUid
            await crfs.createAttribute(attr)
          }
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
    },
    attributes () {
      this.existingAttributes = this.attributes
    }
  }
}
</script>
