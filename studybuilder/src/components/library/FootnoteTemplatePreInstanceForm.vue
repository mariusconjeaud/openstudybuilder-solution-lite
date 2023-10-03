<template>
<pre-instance-form
  object-type="footnoteTemplates"
  :prepare-payload-function="preparePayload"
  v-bind="$attrs"
  v-on="$listeners"
  >
  <template v-slot:indexingTab="{ form, template }">
    <footnote-template-indexing-form
      ref="indexingForm"
      :form="form"
      :template="template"
      />
  </template>
</pre-instance-form>
</template>

<script>
import FootnoteTemplateIndexingForm from './FootnoteTemplateIndexingForm'
import PreInstanceForm from '@/components/library/PreInstanceForm'

export default {
  components: {
    FootnoteTemplateIndexingForm,
    PreInstanceForm
  },
  props: {
    footnoteType: Object
  },
  methods: {
    preparePayload (payload) {
      payload.type_uid = this.footnoteType.term_uid
      Object.assign(payload, this.$refs.indexingForm.preparePayload(payload))
    }
  }
}
</script>
