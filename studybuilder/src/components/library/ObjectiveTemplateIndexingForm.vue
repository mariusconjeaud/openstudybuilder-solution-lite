<template>
<template-indexing-form
  :form="form"
  :template="template"
  >
  <template v-slot:templateIndexFields>
    <not-applicable-field
      :checked="template && !template.categories"
      :clean-function="(value) => cleanObjectiveCategories(form, value)"
      >
      <template v-slot:mainField="{ notApplicable }">
        <validation-provider
          v-slot="{ errors }"
          name="categories"
          :rules="`requiredIfNotNA:${notApplicable}`"
          >
          <multiple-select
            v-model="form.categories"
            :label="$t('ObjectiveTemplateForm.objective_category')"
            data-cy="template-objective-category"
            :items="objectiveCategories"
            item-text="sponsor_preferred_name"
            item-value="term_uid"
            :disabled="notApplicable"
            :errors="errors"
            />
        </validation-provider>
      </template>
    </not-applicable-field>
    <not-applicable-field
      :checked="template && (template.is_confirmatory_testing === null || template.is_confirmatory_testing === undefined)"
      :clean-function="(value) => cleanConfirmatoryTesting(form, value)"
      >
      <template v-slot:mainField="{ notApplicable }">
        <validation-provider
          v-slot="{ errors }"
          name="confirmatoryTesting"
          :rules="`requiredIfNotNA:${notApplicable}`"
          >
          <yes-no-field
            v-model="form.is_confirmatory_testing"
            :label="$t('ObjectiveTemplateForm.confirmatory_testing')"
            data-cy="template-confirmatory-testing"
            :disabled="notApplicable"
            :error-messages="errors"
            />
        </validation-provider>
      </template>
    </not-applicable-field>
  </template>
</template-indexing-form>
</template>

<script>
import MultipleSelect from '@/components/tools/MultipleSelect'
import NotApplicableField from '@/components/tools/NotApplicableField'
import TemplateIndexingForm from './TemplateIndexingForm'
import terms from '@/api/controlledTerminology/terms'
import YesNoField from '@/components/tools/YesNoField'

export default {
  components: {
    MultipleSelect,
    NotApplicableField,
    TemplateIndexingForm,
    YesNoField
  },
  props: {
    form: Object,
    template: Object
  },
  data () {
    return {
      objectiveCategories: []
    }
  },
  methods: {
    cleanObjectiveCategories (form, value) {
      if (value) {
        this.$set(form, 'categories', [])
      }
    },
    cleanConfirmatoryTesting (form, value) {
      if (value) {
        this.$set(form, 'is_confirmatory_testing', null)
      }
    },
    preparePayload (form) {
      const result = {
        is_confirmatory_testing: form.is_confirmatory_testing,
        category_uids: []
      }
      if (form.categories) {
        for (const category of form.categories) {
          if (typeof category === 'string') {
            result.category_uids.push(category)
          } else {
            result.category_uids.push(category.term_uid)
          }
        }
      }
      return result
    }
  },
  mounted () {
    terms.getByCodelist('objectiveCategories').then(resp => {
      this.objectiveCategories = resp.data.items
    })
  }
}
</script>
