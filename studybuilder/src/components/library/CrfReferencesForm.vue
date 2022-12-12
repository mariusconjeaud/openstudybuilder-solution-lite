<template>
<div>
  <simple-form-dialog
    ref="form"
    :title="title"
    :open="open"
    @submit="submit"
    @close="cancel">
      <template v-slot:body>
        <validation-observer ref="observer">
          <v-row>
            <v-col>
              <v-switch
                v-model="form.locked"
                :label="$t('CrfReferencesForm.locked')"
                true-value="Yes"
                false-value="No"
              ></v-switch>
            </v-col>
            <v-col>
              <v-switch
                v-model="form.mandatory"
                :label="$t('CrfReferencesForm.mandatory')"
                true-value="Yes"
                false-value="No"
              ></v-switch>
            </v-col>
            <v-col>
              <v-switch
                v-model="form.sdv"
                v-if="form.parentGroupUid"
                :label="$t('CrfReferencesForm.sdv')"
                true-value="Yes"
                false-value="No"
              ></v-switch>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-switch
                v-model="form.data_entry_required"
                v-if="form.parentGroupUid"
                :label="$t('CrfReferencesForm.data_entry')"
                true-value="Yes"
                false-value="No"
              ></v-switch>
            </v-col>
          </v-row>
        </validation-observer>
      </template>
  </simple-form-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import crfs from '@/api/crfs'
import ConfirmDialog from '@/components/tools/ConfirmDialog'

export default {
  components: {
    SimpleFormDialog,
    ConfirmDialog
  },
  props: {
    open: Boolean,
    element: Object
  },
  computed: {
    title () {
      return this.$t('CrfReferencesForm.title') + this.element.name
    }
  },
  data () {
    return {
      form: {},
      elementCopy: {}
    }
  },
  methods: {
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
    }
  }
}
</script>
