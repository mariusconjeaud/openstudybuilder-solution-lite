<template>
<base-template-form
  object-type="activity-instruction"
  :template="template"
  :prepare-payload-function="preparePayload"
  :help-items="helpItems"
  v-bind="$attrs"
  v-on="$listeners"
  >
  <template v-slot:indexingTab="{ form }">
    <activity-template-indexing-form
      ref="indexingForm"
      :form="form"
      :template="template"
      />
  </template>
</base-template-form>
</template>

<script>
import ActivityTemplateIndexingForm from './ActivityTemplateIndexingForm'
import BaseTemplateForm from './BaseTemplateForm'

export default {
  components: {
    ActivityTemplateIndexingForm,
    BaseTemplateForm
  },
  props: {
    template: Object
  },
  data () {
    return {
      activities: [],
      helpItems: [
        'ActivityDescriptionTemplateForm.indications',
        'ActivityDescriptionTemplateForm.group',
        'ActivityDescriptionTemplateForm.sub_group',
        'ActivityDescriptionTemplateForm.activity'
      ],
      libraries: [],
      parameterTypes: []
    }
  },
  methods: {
    preparePayload (data) {
      Object.assign(data, this.$refs.indexingForm.preparePayload(data))
    }
  }
}
</script>
