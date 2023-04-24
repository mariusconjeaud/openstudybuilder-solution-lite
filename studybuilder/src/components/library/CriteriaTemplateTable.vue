<template>
<studybuilder-template-table
  ref="table"
  :url-prefix="urlPrefix"
  translation-type="CriteriaTemplateTable"
  object-type="criteriaTemplates"
  :headers="headers"
  :extra-filters-func="getExtraFilters"
  has-api
  column-data-resource="criteria-templates"
  :column-data-parameters="columnDataParameters"
  fullscreen-form
  :history-formating-func="formatHistoryItem"
  :export-data-url-params="columnDataParameters"
  double-breadcrumb
  >
  <template v-slot:editform="{ closeForm, selectedObject, filter, updateTemplate }">
    <criteria-template-form
      :criteria-type="criteriaType"
      @close="closeForm"
      :template="selectedObject"
      @templateAdded="filter()"
      @templateUpdated="updateTemplate(arguments[0], 'Draft')"
      />
  </template>
  <template v-slot:item.guidance_text="{ item }">
    <div v-html="item.guidance_text" />
  </template>
  <template v-slot:item.categories.name.sponsor_preferred_name="{ item }">
    <template v-if="item.categories">
      {{ item.categories|terms }}
    </template>
    <template v-else>
      {{ $t('_global.not_applicable_long') }}
    </template>
  </template>
  <template v-slot:item.sub_categories.name.sponsor_preferred_name="{ item }">
    <template v-if="item.sub_categories">
      {{ item.sub_categories|terms }}
    </template>
    <template v-else>
      {{ $t('_global.not_applicable_long') }}
    </template>
  </template>
  <template v-slot:indexingDialog="{ closeDialog, template, show }">
    <template-indexing-dialog
      @close="closeDialog"
      @updated="refreshTable"
      :show="show"
      :template="template"
      :prepare-payload-func="prepareIndexingPayload"
      :url-prefix="urlPrefix"
      >
      <template v-slot:form="{ form }">
        <criteria-template-indexing-form
          ref="indexingForm"
          :form="form"
          :template="template"
          />
      </template>
    </template-indexing-dialog>
  </template>
</studybuilder-template-table>
</template>

<script>
import CriteriaTemplateForm from './CriteriaTemplateForm'
import CriteriaTemplateIndexingForm from './CriteriaTemplateIndexingForm'
import dataFormating from '@/utils/dataFormating'
import StudybuilderTemplateTable from '@/components/library/StudybuilderTemplateTable'
import TemplateIndexingDialog from './TemplateIndexingDialog'

export default {
  props: {
    criteriaType: Object
  },
  components: {
    CriteriaTemplateForm,
    CriteriaTemplateIndexingForm,
    StudybuilderTemplateTable,
    TemplateIndexingDialog
  },
  data () {
    return {
      columnDataParameters: {
        filters: { 'type.term_uid': { v: [this.criteriaType.term_uid], op: 'eq' } }
      },
      headers: [
        {
          text: '',
          value: 'actions',
          sortable: false,
          width: '5%'
        },
        { text: this.$t('CriteriaTemplateTable.indications'), value: 'indications.name' },
        { text: this.$t('CriteriaTemplateTable.criterion_cat'), value: 'categories.name.sponsor_preferred_name' },
        { text: this.$t('CriteriaTemplateTable.criterion_sub_cat'), value: 'sub_categories.name.sponsor_preferred_name' },
        { text: this.$t('CriteriaTemplateTable.criterion_tpl'), value: 'name', width: '30%', filteringName: 'name_plain' },
        { text: this.$t('CriteriaTemplateTable.guidance_text'), value: 'guidance_text', width: '30%' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      types: [],
      urlPrefix: '/criteria-templates'
    }
  },
  methods: {
    getExtraFilters (filters) {
      filters['type.term_uid'] = { v: [this.criteriaType.term_uid] }
    },
    prepareIndexingPayload (form) {
      return this.$refs.indexingForm.preparePayload(form)
    },
    refreshTable () {
      this.$refs.table.$refs.sponsorTable.filter()
    },
    formatHistoryItem (item) {
      if (item.categories) {
        item.categories = { name: { sponsor_preferred_name: dataFormating.terms(item.categories) } }
      } else {
        item.categories = { name: { sponsor_preferred_name: this.$t('_global.not_applicable_long') } }
      }
      if (item.sub_categories) {
        item.sub_categories = { name: { sponsor_preferred_name: dataFormating.terms(item.sub_categories) } }
      } else {
        item.sub_categories = { name: { sponsor_preferred_name: this.$t('_global.not_applicable_long') } }
      }
    }
  },
  created () {
    this.$store.dispatch('studiesGeneral/fetchNullValues')
  }
}
</script>
