<template>
<template-indexing-form
  :form="form"
  :template="template"
  >
  <template v-slot:templateIndexFields>
    <not-applicable-field
      class="mt-4"
      :checked="template && !template.categories"
      :clean-function="value => $set(form, 'categories', null)"
      >
      <template v-slot:mainField="{ notApplicable }">
        <validation-provider
          v-slot="{ errors }"
          name="categories"
          :rules="`requiredIfNotNA:${notApplicable}`"
          >
          <multiple-select
            v-model="form.categories"
            :label="$t('CriteriaTemplateForm.criterion_cat')"
            data-cy="template-criterion-category"
            :items="categories"
            item-text="sponsor_preferred_name"
            item-value="term_uid"
            :disabled="notApplicable"
            :errors="errors"
            />
        </validation-provider>
      </template>
    </not-applicable-field>
    <not-applicable-field
      class="mt-4"
      :checked="template && !template.sub_categories"
      :clean-function="value => $set(form, 'sub_categories', null)"
      >
      <template v-slot:mainField="{ notApplicable }">
        <validation-provider
          v-slot="{ errors }"
          name="subCategories"
          :rules="`requiredIfNotNA:${notApplicable}`"
          >
          <multiple-select
            v-model="form.sub_categories"
            :label="$t('CriteriaTemplateForm.criterion_sub_cat')"
            data-cy="template-criterion-sub-category"
            :items="subCategories"
            item-text="sponsor_preferred_name"
            item-value="term_uid"
            :disabled="notApplicable"
            :errors="errors"
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

export default {
  components: {
    MultipleSelect,
    NotApplicableField,
    TemplateIndexingForm
  },
  props: {
    form: Object,
    template: Object
  },
  data () {
    return {
      categories: [],
      subCategories: []
    }
  },
  methods: {
    preparePayload (form) {
      const result = {
        category_uids: [],
        sub_category_uids: []
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
      if (form.sub_categories) {
        for (const subcategory of form.sub_categories) {
          if (typeof subcategory === 'string') {
            result.sub_category_uids.push(subcategory)
          } else {
            result.sub_category_uids.push(subcategory.term_uid)
          }
        }
      }
      return result
    }
  },
  mounted () {
    terms.getByCodelist('criteriaCategories').then(resp => {
      this.categories = resp.data.items
    })
    terms.getByCodelist('criteriaSubCategories').then(resp => {
      this.subCategories = resp.data.items
    })
  }
}
</script>
