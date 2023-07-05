<template>
<pre-instance-form
  object-type="objectiveTemplates"
  :prepare-payload-function="preparePayload"
  v-bind="$attrs"
  v-on="$listeners"
  >
  <template v-slot:indexingTab="{ form, template, preInstance }">
    <objective-template-indexing-form
      v-if="template"
      ref="indexingForm"
      :form="form"
      :template="template"
      />
    <objective-template-indexing-form
      v-else
      ref="indexingForm"
      :form="form"
      :template="preInstance"
      />
  </template>
</pre-instance-form>
</template>

<script>
import ObjectiveTemplateIndexingForm from './ObjectiveTemplateIndexingForm'
import PreInstanceForm from '@/components/library/PreInstanceForm'

export default {
  components: {
    ObjectiveTemplateIndexingForm,
    PreInstanceForm
  },
  methods: {
    preparePayload (payload) {
      Object.assign(payload, this.$refs.indexingForm.preparePayload(payload))
    }
  }
}
</script>
