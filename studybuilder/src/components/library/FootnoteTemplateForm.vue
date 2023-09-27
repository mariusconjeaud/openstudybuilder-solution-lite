<template data-cy="template-text-part">
<base-template-form
  object-type="footnote"
  :template="template"
  :prepare-payload-function="preparePayload"
  :help-items="helpItems"
  :title-context="{ type: footnoteType.sponsor_preferred_name }"
  data-cy="template-text"
  v-bind="$attrs"
  v-on="$listeners"
  >
  <template v-slot:indexingTab="{ form }">
    <footnote-template-indexing-form
      ref="indexingForm"
      :form="form"
      :template="template"
      />
  </template>
</base-template-form>
</template>

<script>
import BaseTemplateForm from './BaseTemplateForm'
import FootnoteTemplateIndexingForm from './FootnoteTemplateIndexingForm'

export default {
  components: {
    BaseTemplateForm,
    FootnoteTemplateIndexingForm
  },
  props: {
    template: Object,
    footnoteType: Object
  },
  data () {
    return {
      helpItems: [
        'FootnoteTemplateForm.indications',
        'FootnoteTemplateForm.group',
        'FootnoteTemplateForm.sub_group',
        'FootnoteTemplateForm.activity'
      ]
    }
  },
  methods: {
    preparePayload (payload) {
      payload.type_uid = this.footnoteType.term_uid
      Object.assign(payload, this.$refs.indexingForm.preparePayload(payload))
    }
  }
}
</script>
