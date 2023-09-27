<template>
<studybuilder-template-table
  ref="table"
  :url-prefix="urlPrefix"
  translation-type="ObjectiveTemplateTable"
  object-type="objectiveTemplates"
  :headers="headers"
  has-api
  column-data-resource="objective-templates"
  :history-formating-func="formatHistoryItem"
  :history-excluded-headers="historyExcludedHeaders"
  fullscreen-form
  :prepare-duplicate-payload-func="prepareDuplicatePayload"
  @refresh="refreshTable"
  >
  <template v-slot:editform="{ closeForm, selectedObject, preInstanceMode }">
    <objective-template-pre-instance-form
      v-if="preInstanceMode"
      :pre-instance="selectedObject"
      @close="closeForm"
      @success="refreshTable()"
      />
    <objective-template-form
      v-else
      @close="closeForm"
      @templateAdded="refreshTable()"
      @templateUpdated="refreshTable()"
      :template="selectedObject"
      />
  </template>
  <template v-slot:item.is_confirmatory_testing="{ item }">
    <template v-if="item.is_confirmatory_testing !== null">
      {{ item.is_confirmatory_testing|yesno }}
    </template>
    <template v-else>
      {{ $t('_global.not_applicable_long') }}
    </template>
  </template>
  <template v-slot:item.categories.name.sponsor_preferred_name="{ item }">
    <template v-if="item.categories && item.categories.length">
      {{ item.categories|terms }}
    </template>
    <template v-else>
      {{ $t('_global.not_applicable_long') }}
    </template>
  </template>
  <template v-slot:indexingDialog="{ closeDialog, template, show, preInstanceMode }">
    <template-indexing-dialog
      @close="closeDialog"
      @updated="refreshTable"
      :template="template"
      :prepare-payload-func="prepareIndexingPayload"
      :url-prefix="urlPrefix"
      :show="show"
      :pre-instance-mode="preInstanceMode"
      >
      <template v-slot:form="{ form }">
        <objective-template-indexing-form
          ref="indexingForm"
          :form="form"
          :template="template"
          />
      </template>
    </template-indexing-dialog>
  </template>
  <template v-slot:preInstanceForm="{ closeDialog, template }">
    <objective-template-pre-instance-form
      :template="template"
      @close="closeDialog"
      @success="refreshTable()"
      />
  </template>
</studybuilder-template-table>
</template>

<script>
import dataFormating from '@/utils/dataFormating'
import ObjectiveTemplateForm from '@/components/library/ObjectiveTemplateForm'
import ObjectiveTemplateIndexingForm from './ObjectiveTemplateIndexingForm'
import ObjectiveTemplatePreInstanceForm from './ObjectiveTemplatePreInstanceForm'
import StudybuilderTemplateTable from '@/components/library/StudybuilderTemplateTable'
import TemplateIndexingDialog from './TemplateIndexingDialog'

export default {
  components: {
    ObjectiveTemplateForm,
    ObjectiveTemplateIndexingForm,
    ObjectiveTemplatePreInstanceForm,
    StudybuilderTemplateTable,
    TemplateIndexingDialog
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
        { text: this.$t('_global.indications'), value: 'indications.name' },
        { text: this.$t('ObjectiveTemplateTable.objective_cat'), value: 'categories.name.sponsor_preferred_name' },
        { text: this.$t('ObjectiveTemplateTable.confirmatory_testing'), value: 'is_confirmatory_testing' },
        { text: this.$t('_global.parent_template'), value: 'name', width: '30%', filteringName: 'name_plain' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      historyExcludedHeaders: [
        'indications.name',
        'categories.name.sponsor_preferred_name',
        'is_confirmatory_testing'
      ],
      urlPrefix: '/objective-templates'
    }
  },
  methods: {
    prepareIndexingPayload (form) {
      return this.$refs.indexingForm.preparePayload(form)
    },
    prepareDuplicatePayload (payload, preInstance) {
      if (preInstance.categories && preInstance.categories.length) {
        payload.category_uids = preInstance.categories.map(item => item.term_uid)
      } else {
        payload.category_uids = []
      }
    },
    refreshTable () {
      this.$refs.table.$refs.sponsorTable.filter()
      if (this.$refs.table.$refs.preInstanceTable) {
        this.$refs.table.$refs.preInstanceTable.filter()
      }
    },
    formatHistoryItem (item) {
      if (item.is_confirmatory_testing !== null) {
        item.is_confirmatory_testing = dataFormating.yesno(item.is_confirmatory_testing)
      }
      if (item.categories && item.categories.length) {
        item.categories = { name: { sponsor_preferred_name: dataFormating.terms(item.categories) } }
      } else {
        item.categories = { name: { sponsor_preferred_name: this.$t('_global.not_applicable_long') } }
      }
    }
  }
}
</script>
