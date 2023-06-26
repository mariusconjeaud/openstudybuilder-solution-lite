<template>
<pre-instance-form
  object-type="activityTemplates"
  :prepare-payload-function="preparePayload"
  v-bind="$attrs"
  v-on="$listeners"
  >
  <template v-slot:indexingTab="{ form, template }">
    <activity-template-indexing-form
      ref="indexingForm"
      :form="form"
      :template="template"
      />
  </template>
</pre-instance-form>
</template>

<script>
import ActivityTemplateIndexingForm from './ActivityTemplateIndexingForm'
import PreInstanceForm from '@/components/library/PreInstanceForm'

export default {
  components: {
    ActivityTemplateIndexingForm,
    PreInstanceForm
  },
  props: {
    activityType: Object
  },
  methods: {
    preparePayload (payload) {
      Object.assign(payload, this.$refs.indexingForm.preparePayload(payload))
    }
  }
}
</script>
