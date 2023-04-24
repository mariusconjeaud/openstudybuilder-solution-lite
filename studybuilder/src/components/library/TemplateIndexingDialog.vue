<template>
<simple-form-dialog
  ref="form"
  :title="$t('TemplateIndexingDialog.title')"
  :open="show"
  @submit="submit"
  @close="close"
  v-bind="$attrs"
  v-on="$listeners"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
      <slot
        name="form"
        v-bind:form="form"
        v-bind:template="template"
        />
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>
import { bus } from '@/main'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import templates from '@/api/templates'

export default {
  components: {
    SimpleFormDialog
  },
  props: {
    preparePayloadFunc: Function,
    template: Object,
    urlPrefix: String,
    show: Boolean
  },
  data () {
    return {
      form: {}
    }
  },
  methods: {
    close () {
      this.$refs.observer.reset()
      this.$emit('close')
    },
    async submit () {
      const isValid = await this.$refs.observer.validate()
      if (!isValid) {
        return
      }
      const data = {
        indication_uids: (this.form.indications) ? this.form.indications.map(item => item.term_uid) : [],
        ...this.preparePayloadFunc(this.form)
      }
      const api = templates(this.urlPrefix)
      api.updateIndexings(this.template.uid, data).then(() => {
        this.$emit('updated')
        this.$emit('close')
        bus.$emit('notification', { msg: this.$t('TemplateIndexingDialog.update_success'), type: 'success' })
      })
    }
  },
  watch: {
    template: {
      handler: function (value) {
        if (value) {
          this.form = { ...value }
        }
      },
      immediate: true
    }
  }
}
</script>
