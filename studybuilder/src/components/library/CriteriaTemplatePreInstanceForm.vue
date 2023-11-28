<template>
<pre-instance-form
  object-type="criteriaTemplates"
  :prepare-payload-function="preparePayload"
  v-bind="$attrs"
  v-on="$listeners"
  >
  <template v-slot:indexingTab="{ form, template, preInstance }">
    <criteria-template-indexing-form
      v-if="template"
      ref="indexingForm"
      :form="form"
      :template="template"
      />
    <criteria-template-indexing-form
      v-else
      ref="indexingForm"
      :form="form"
      :template="preInstance"
      />
  </template>
</pre-instance-form>
</template>

<script>
import CriteriaTemplateIndexingForm from './CriteriaTemplateIndexingForm'
import PreInstanceForm from '@/components/library/PreInstanceForm'

export default {
  components: {
    CriteriaTemplateIndexingForm,
    PreInstanceForm
  },
  props: {
    criteriaType: Object
  },
  methods: {
    preparePayload (payload) {
      payload.type_uid = this.criteriaType.term_uid
      Object.assign(payload, this.$refs.indexingForm.preparePayload(payload))
    }
  }
}
</script>
