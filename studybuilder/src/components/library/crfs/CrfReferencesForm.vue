<template>
<div>
  <simple-form-dialog
    ref="form"
    :title="title"
    :open="open"
    @submit="submit"
    @close="cancel"
    max-width="1200px"
    :no-saving="readOnly">
    <template v-slot:body>
      <v-expansion-panels
        multiple
        v-model="panels">
        <v-expansion-panel>
          <v-expansion-panel-header class="text-h6">{{ $t('CRFForms.standard_attributes') }}</v-expansion-panel-header>
          <v-expansion-panel-content>
            <v-row>
              <v-col>
                <v-switch
                  v-model="form.mandatory"
                  :label="$t('CrfReferencesForm.mandatory')"
                  true-value="Yes"
                  false-value="No"
                  :disabled="readOnly"
                ></v-switch>
              </v-col>
              <v-col>
                <v-switch
                  v-model="form.locked"
                  v-if="form.parentTemplateUid"
                  :label="$t('CrfReferencesForm.locked')"
                  true-value="Yes"
                  false-value="No"
                  :disabled="readOnly"
                ></v-switch>
              </v-col>
          </v-row>
          </v-expansion-panel-content>
        </v-expansion-panel>
        <v-expansion-panel v-if="element.parentFormUid || element.parentGroupUid">
          <v-expansion-panel-header class="text-h6">{{ $t('CRFForms.vendor_extensions_low') }}</v-expansion-panel-header>
          <v-expansion-panel-content>
            <crf-extensions-management-table
              :type="type"
              :edit-extensions="selectedExtensions"
              @setExtensions="setExtensions"
              only-attributes
              :read-only="readOnly"/>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </template>
  </simple-form-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import crfs from '@/api/crfs'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import CrfExtensionsManagementTable from '@/components/library/crfs/CrfExtensionsManagementTable'

export default {
  components: {
    SimpleFormDialog,
    ConfirmDialog,
    CrfExtensionsManagementTable
  },
  props: {
    open: Boolean,
    element: Object,
    readOnly: Boolean
  },
  computed: {
    title () {
      return this.$t('CrfReferencesForm.title') + this.element.name
    }
  },
  data () {
    return {
      form: {},
      elementCopy: {},
      selectedExtensions: [],
      type: '',
      panels: [0]
    }
  },
  methods: {
    setExtensions (extensions) {
      this.selectedExtensions = extensions
    },
    async submit () {
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (this.form.parentTemplateUid) {
        crfs.addFormsToTemplate([this.form], this.form.parentTemplateUid, false).then(resp => {
          this.$emit('close')
        })
      } else if (this.form.parentFormUid) {
        let form = {}
        await crfs.getCrfForms().then(resp => {
          form = resp.data.find(el => el.uid === this.form.parentFormUid)
        })
        this.form.vendor.attributes = this.selectedExtensions
        if (form.parent_uids.length > 1 && !(await this.$refs.confirm.open(this.$t('CrfReferencesForm.warning_1') + (form.parent_uids.length - 1) + this.$t('CrfReferencesForm.warning_templ'), options))) {
          this.$emit('close')
          return
        }
        crfs.addItemGroupsToForm([this.form], this.form.parentFormUid, false).then(resp => {
          this.$emit('close')
        })
      } else {
        let group = {}
        await crfs.getCrfGroups().then(resp => {
          group = resp.data.find(el => el.uid === this.form.parentGroupUid)
        })
        if (group.parent_uids.length === 1) {
          let numberOfParentTemplates = 0
          await crfs.getRelationships(group.parent_uids[0], 'forms').then(async resp => {
            numberOfParentTemplates = resp.data.OdmTemplate.length
          })
          if (numberOfParentTemplates > 1 && !(await this.$refs.confirm.open(this.$t('CrfReferencesForm.templates_warning'), options))) {
            this.$emit('close')
            return
          }
        }
        if (group.parent_uids.length > 1 && !(await this.$refs.confirm.open(this.$t('CrfReferencesForm.warning_1') + (group.parent_uids.length - 1) + this.$t('CrfReferencesForm.warning_forms'), options))) {
          this.$emit('close')
          return
        }
        crfs.addItemsToItemGroup([this.form], this.form.parentGroupUid, false).then(resp => {
          this.$emit('close')
        })
      }
    },
    close () {
      this.$emit('close')
    },
    cancel () {
      this.form = Object.assign(this.form, this.elementCopy)
      this.$emit('close')
    }
  },
  mounted () {
    this.elementCopy = Object.assign(this.elementCopy, this.element)
    this.form = this.element
  },
  watch: {
    element (value) {
      this.elementCopy = Object.assign(this.elementCopy, value)
      this.form = value
      this.selectedExtensions = this.form.vendor ? this.form.vendor.attributes : []
      const params = {}
      if (this.selectedExtensions.length > 0) {
        params.filters = { uid: { v: this.selectedExtensions.map(attr => attr.uid), op: 'co' } }
        crfs.getAllAttributes(params).then(resp => {
          resp.data.items.forEach(el => {
            el.type = 'Attribute'
            el.value = this.selectedExtensions.find(attr => attr.uid === el.uid).value
          })
          this.selectedExtensions = resp.data.items
        })
      }
      this.selectedExtensions.forEach(el => {
        el.type = 'Attribute'
      })
      this.type = this.form.parentFormUid ? 'ItemGroupRef' : 'ItemRef'
    }
  }
}
</script>
