<template data-cy="template-text-part">
<base-template-form
  object-type="criteria"
  :template="template"
  :load-form-function="loadForm"
  :prepare-payload-function="preparePayload"
  :help-items="helpItems"
  :title-context="{ type: criteriaType.sponsor_preferred_name }"
  data-cy="template-text"
  v-bind="$attrs"
  v-on="$listeners"
  >
  <template v-slot:extraFields="{ form }">
    <validation-observer ref="observer">
      <v-row>
        <v-col cols="11">
          <vue-editor
            ref="editor"
            id="editor"
            data-cy="template-guidance-text"
            v-model="form.guidance_text"
            :editor-toolbar="customToolbar"
            :placeholder="$t('CriteriaTemplateForm.guidance_text')"
            class="pt-4"
            />
        </v-col>
      </v-row>
    </validation-observer>
  </template>
  <template v-slot:indexingTab="{ form }">
    <criteria-template-indexing-form
      ref="indexingForm"
      :form="form"
      :template="template"
      />
  </template>
</base-template-form>
</template>

<script>
import BaseTemplateForm from './BaseTemplateForm'
import CriteriaTemplateIndexingForm from './CriteriaTemplateIndexingForm'
import { VueEditor } from 'vue2-editor'

export default {
  components: {
    BaseTemplateForm,
    CriteriaTemplateIndexingForm,
    VueEditor
  },
  props: {
    template: Object,
    criteriaType: Object
  },
  data () {
    return {
      customToolbar: [
        ['bold', 'italic', 'underline'],
        [{ script: 'sub' }, { script: 'super' }],
        [{ list: 'ordered' }, { list: 'bullet' }]
      ],
      helpItems: [
        'CriteriaTemplateForm.guidance_text',
        'CriteriaTemplateForm.indication',
        'CriteriaTemplateForm.criterion_cat',
        'CriteriaTemplateForm.criterion_sub_cat'
      ]
    }
  },
  methods: {
    loadForm (form) {
      form.guidance_text = this.template.guidance_text
      if (this.template.categories && this.template.categories.length) {
        this.$set(form, 'categories', this.template.categories)
      }
      if (this.template.sub_categories && this.template.sub_categories.length) {
        this.$set(form, 'sub_categories', this.template.sub_categories)
      }
      this.$store.commit('form/SET_FORM', form)
    },
    preparePayload (payload) {
      payload.type_uid = this.criteriaType.term_uid
      Object.assign(payload, this.$refs.indexingForm.preparePayload(payload))
    }
  }
}
</script>
