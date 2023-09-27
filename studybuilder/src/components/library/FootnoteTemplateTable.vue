<template>
<studybuilder-template-table
  ref="table"
  :url-prefix="urlPrefix"
  translation-type="FootnoteTemplateTable"
  object-type="footnoteTemplates"
  :headers="headers"
  :extra-filters-func="getExtraFilters"
  has-api
  column-data-resource="footnote-templates"
  :column-data-parameters="columnDataParameters"
  fullscreen-form
  :history-formating-func="formatHistoryItem"
  :history-excluded-headers="historyExcludedHeaders"
  :export-data-url-params="columnDataParameters"
  double-breadcrumb
  :prepare-duplicate-payload-func="prepareDuplicatePayload"
  >
  <template v-slot:editform="{ closeForm, selectedObject, preInstanceMode }">
    <footnote-template-pre-instance-form
      v-if="preInstanceMode"
      :pre-instance="selectedObject"
      :footnote-type="footnoteType"
      @close="closeForm"
      @success="refreshTable"
      />
    <footnote-template-form
      v-else
      :footnote-type="footnoteType"
      @close="closeForm"
      :template="selectedObject"
      @templateAdded="refreshTable"
      @templateUpdated="refreshTable"
      />
  </template>
  <template v-slot:item.activity_groups="{ item }">
    <template v-if="item.activity_groups && item.activity_groups.length">
      {{ displayList(item.activity_groups) }}
    </template>
    <template v-else>
      {{ $t('_global.not_applicable_long') }}
    </template>
  </template>
  <template v-slot:item.activity_subgroups="{ item }">
    <template v-if="item.activity_subgroups && item.activity_subgroups.length">
      {{ displayList(item.activity_subgroups) }}
    </template>
    <template v-else>
      {{ $t('_global.not_applicable_long') }}
    </template>
  </template>
  <template v-slot:item.activities="{ item }">
    <template v-if="item.activities && item.activities.length">
      {{ displayList(item.activities) }}
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
        <footnote-template-indexing-form
          ref="indexingForm"
          :form="form"
          :template="template"
          />
      </template>
    </template-indexing-dialog>
  </template>
  <template v-slot:preInstanceForm="{ closeDialog, template }">
    <footnote-template-pre-instance-form
      :template="template"
      :footnote-type="footnoteType"
      @close="closeDialog"
      @success="refreshTable"
      />
  </template>
</studybuilder-template-table>
</template>

<script>
import FootnoteTemplateForm from './FootnoteTemplateForm'
import FootnoteTemplateIndexingForm from './FootnoteTemplateIndexingForm'
import FootnoteTemplatePreInstanceForm from './FootnoteTemplatePreInstanceForm'
import StudybuilderTemplateTable from '@/components/library/StudybuilderTemplateTable'
import TemplateIndexingDialog from './TemplateIndexingDialog'

export default {
  props: {
    footnoteType: Object
  },
  components: {
    FootnoteTemplateForm,
    FootnoteTemplateIndexingForm,
    FootnoteTemplatePreInstanceForm,
    StudybuilderTemplateTable,
    TemplateIndexingDialog
  },
  data () {
    return {
      columnDataParameters: {
        filters: { 'type.term_uid': { v: [this.footnoteType.term_uid], op: 'eq' } }
      },
      headers: [
        {
          text: '',
          value: 'actions',
          sortable: false,
          width: '5%'
        },
        { text: this.$t('_global.sequence_number'), value: 'sequence_id' },
        { text: this.$t('FootnoteTemplateTable.indications'), value: 'indications.name' },
        { text: this.$t('ActivityTemplateTable.activity_group'), value: 'activity_groups' },
        { text: this.$t('ActivityTemplateTable.activity_subgroup'), value: 'activity_subgroups' },
        { text: this.$t('ActivityTemplateTable.activity_name'), value: 'activities' },
        { text: this.$t('_global.parent_template'), value: 'name', width: '30%', filteringName: 'name_plain' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      historyExcludedHeaders: [
        'indications.name',
        'categories.name.sponsor_preferred_name',
        'sub_categories.name.sponsor_preferred_name',
        'activity_groups',
        'activity_subgroups',
        'activities'
      ],
      types: [],
      urlPrefix: '/footnote-templates'
    }
  },
  methods: {
    displayList (items) {
      return items.map(item => item.name).join(', ')
    },
    getExtraFilters (filters, preInstanceMode) {
      if (!preInstanceMode) {
        filters['type.term_uid'] = { v: [this.footnoteType.term_uid] }
      } else {
        filters.template_type_uid = { v: [this.footnoteType.term_uid] }
      }
    },
    prepareIndexingPayload (form) {
      return this.$refs.indexingForm.preparePayload(form)
    },
    prepareDuplicatePayload (payload, preInstance) {
      if (preInstance.activities && preInstance.activities.length) {
        payload.activity_uids = preInstance.activities.map(item => item.uid)
      } else {
        payload.activity_uids = []
      }
      if (preInstance.activity_groups && preInstance.activity_groups.length) {
        payload.activity_group_uids = preInstance.activity_groups.map(item => item.uid)
      } else {
        payload.activity_group_uids = []
      }
      if (preInstance.activity_subgroups && preInstance.activity_subgroups.length) {
        payload.activity_subgroup_uids = preInstance.activity_subgroups.map(item => item.uid)
      } else {
        payload.activity_subgroup_uids = []
      }
    },
    refreshTable () {
      this.$refs.table.$refs.sponsorTable.filter()
      if (this.$refs.table.$refs.preInstanceTable) {
        this.$refs.table.$refs.preInstanceTable.filter()
      }
    },
    formatHistoryItem (item) {
      if (item.activity_groups) {
        item.activity_groups = this.displayList(item.activity_groups)
      }
      if (item.activity_subgroups) {
        item.activity_subgroups = this.displayList(item.activity_subgroups)
      }
      if (item.activities) {
        item.activities = this.displayList(item.activities)
      }
    }
  },
  created () {
    this.$store.dispatch('studiesGeneral/fetchNullValues')
  }
}
</script>
