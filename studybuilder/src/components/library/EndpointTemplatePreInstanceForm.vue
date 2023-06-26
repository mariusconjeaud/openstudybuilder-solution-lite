<template>
<pre-instance-form
  object-type="endpointTemplates"
  :prepare-payload-function="preparePayload"
  v-bind="$attrs"
  v-on="$listeners"
  >
  <template v-slot:indexingTab="{ form, template }">
    <endpoint-template-indexing-form
      ref="indexingForm"
      :form="form"
      :template="template"
      />
  </template>
</pre-instance-form>
</template>

<script>
import EndpointTemplateIndexingForm from './EndpointTemplateIndexingForm'
import PreInstanceForm from '@/components/library/PreInstanceForm'

export default {
  components: {
    EndpointTemplateIndexingForm,
    PreInstanceForm
  },
  methods: {
    preparePayload (payload) {
      Object.assign(payload, this.$refs.indexingForm.preparePayload(payload))
    }
  }
}
</script>
