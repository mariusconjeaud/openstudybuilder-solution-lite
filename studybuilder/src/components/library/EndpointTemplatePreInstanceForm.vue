<template>
<pre-instance-form
  object-type="endpointTemplates"
  :prepare-payload-function="preparePayload"
  v-bind="$attrs"
  v-on="$listeners"
  >
  <template v-slot:indexingTab="{ form, template, preInstance }">
    <endpoint-template-indexing-form
      v-if="template"
      ref="indexingForm"
      :form="form"
      :template="template"
      />
    <endpoint-template-indexing-form
      v-else
      ref="indexingForm"
      :form="form"
      :template="preInstance"
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
