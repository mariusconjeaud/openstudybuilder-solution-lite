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
  :history-excluded-headers="historyExcludedHeaders"
  :export-data-url-params="columnDataParameters"
  double-breadcrumb
  :prepare-duplicate-payload-func="prepareDuplicatePayload"
  @refresh="refreshTable"
  >
  <template v-slot:editform="{ closeForm, selectedObject, preInstanceMode }">
    <criteria-template-pre-instance-form
      v-if="preInstanceMode"
      :pre-instance="selectedObject"
      :criteria-type="criteriaType"
      @close="closeForm"
      @success="refreshTable"
      />
    <criteria-template-form
      v-else
      :criteria-type="criteriaType"
      @close="closeForm"
      :template="selectedObject"
      @templateAdded="refreshTable"
      @templateUpdated="refreshTable"
      />
  </template>
  <template v-slot:item.guidance_text="{ item }">
    <div v-html="item.guidance_text" />
  </template>
  <template v-slot:item.categories.name.sponsor_preferred_name="{ item }">
    <template v-if="item.categories && item.categories.length">
      {{ item.categories|terms }}
    </template>
    <template v-else>
      {{ $t('_global.not_applicable_long') }}
    </template>
  </template>
  <template v-slot:item.sub_categories.name.sponsor_preferred_name="{ item }">
    <template v-if="item.sub_categories && item.sub_categories.length">
      {{ item.sub_categories|terms }}
    </template>
    <template v-else>
      {{ $t('_global.not_applicable_long') }}
    </template>
  </template>
  <template v-slot:indexingDialog="{ closeDialog, template, show, preInstanceMode }">
    <template-indexing-dialog
      @close="closeDialog"
      @updated="refreshTable"
      :show="show"
      :template="template"
      :prepare-payload-func="prepareIndexingPayload"
      :url-prefix="urlPrefix"
      :pre-instance-mode="preInstanceMode"
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
  <template v-slot:preInstanceForm="{ closeDialog, template }">
    <criteria-template-pre-instance-form
      :template="template"
      :criteria-type="criteriaType"
      @close="closeDialog"
      @success="refreshTable"
      />
  </template>
</studybuilder-template-table>
</template>

<script>
import CriteriaTemplateForm from './CriteriaTemplateForm'
import CriteriaTemplateIndexingForm from './CriteriaTemplateIndexingForm'
import CriteriaTemplatePreInstanceForm from './CriteriaTemplatePreInstanceForm'
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
    CriteriaTemplatePreInstanceForm,
    StudybuilderTemplateTable,
    TemplateIndexingDialog
  },
  computed: {
    columnDataParameters () {
      const keyName = (this.$route.params && this.$route.params.tab === 'pre-instances') ? 'template_type_uid' : 'type.term_uid'
      const filters = {}
      filters[keyName] = { v: [this.criteriaType.term_uid], op: 'eq' }
      return { filters }
    }
  },
  data () {
    return {
      headers: [
        {
          text: '',
          value: 'actions',
          sortable: false,
          width: '5%'
        },
        { text: this.$t('_global.sequence_number'), value: 'sequence_id' },
        { text: this.$t('CriteriaTemplateTable.indications'), value: 'indications.name' },
        { text: this.$t('CriteriaTemplateTable.criterion_cat'), value: 'categories.name.sponsor_preferred_name' },
        { text: this.$t('CriteriaTemplateTable.criterion_sub_cat'), value: 'sub_categories.name.sponsor_preferred_name' },
        { text: this.$t('_global.parent_template'), value: 'name', width: '30%', filteringName: 'name_plain' },
        { text: this.$t('CriteriaTemplateTable.guidance_text'), value: 'guidance_text', width: '30%' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      historyExcludedHeaders: [
        'indications.name',
        'categories.name.sponsor_preferred_name',
        'sub_categories.name.sponsor_preferred_name'
      ],
      types: [],
      urlPrefix: '/criteria-templates'
    }
  },
  methods: {
    getExtraFilters (filters, preInstanceMode) {
      if (!preInstanceMode) {
        filters['type.term_uid'] = { v: [this.criteriaType.term_uid] }
      } else {
        filters.template_type_uid = { v: [this.criteriaType.term_uid] }
      }
    },
    prepareIndexingPayload (form) {
      return this.$refs.indexingForm.preparePayload(form)
    },
    prepareDuplicatePayload (payload, preInstance) {
      if (preInstance.categories && preInstance.categories.length) {
        payload.category_uids = preInstance.categories.map(item => item.term_uid)
      } else {
        payload.category_uids = []
      }
      if (preInstance.sub_categories && preInstance.sub_categories.length) {
        payload.sub_category_uids = preInstance.sub_categories.map(item => item.term_uid)
      } else {
        payload.sub_category_uids = []
      }
    },
    refreshTable () {
      if (this.$refs.table.$refs.sponsorTable) {
        this.$refs.table.$refs.sponsorTable.filter()
      }
      if (this.$refs.table.$refs.preInstanceTable) {
        this.$refs.table.$refs.preInstanceTable.filter()
      }
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
