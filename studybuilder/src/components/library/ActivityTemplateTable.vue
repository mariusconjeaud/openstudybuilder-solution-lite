<template>
<studybuilder-template-table
  ref="table"
  :url-prefix="urlPrefix"
  translation-type="ActivityTemplateTable"
  object-type="activityTemplates"
  :headers="headers"
  fullscreen-form
  :history-formating-func="formatHistoryItem"
  :history-excluded-headers="historyExcludedHeaders"
  :prepare-duplicate-payload-func="prepareDuplicatePayload"
  >
  <template v-slot:editform="{ closeForm, selectedObject, preInstanceMode }">
    <activity-template-pre-instantiation-form
      v-if="preInstanceMode"
      :pre-instance="selectedObject"
      @close="closeForm"
      @success="refreshTable"
      />
    <activity-template-form
      @close="closeForm"
      @templateAdded="refreshTable"
      @templateUpdated="refreshTable"
      :template="selectedObject"
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
      :template="template"
      :prepare-payload-func="prepareIndexingPayload"
      :url-prefix="urlPrefix"
      :show="show"
      :pre-instance-mode="preInstanceMode"
      >
      <template v-slot:form="{ form }">
        <activity-template-indexing-form
          ref="indexingForm"
          :form="form"
          :template="template"
          />
      </template>
    </template-indexing-dialog>
  </template>
  <template v-slot:preInstanceForm="{ closeDialog, template }">
    <activity-template-pre-instance-form
      :template="template"
      @close="closeDialog"
      @success="refreshTable"
      />
  </template>
</studybuilder-template-table>
</template>

<script>
import ActivityTemplateForm from './ActivityTemplateForm'
import ActivityTemplateIndexingForm from './ActivityTemplateIndexingForm'
import ActivityTemplatePreInstanceForm from './ActivityTemplatePreInstanceForm'
import StudybuilderTemplateTable from '@/components/library/StudybuilderTemplateTable'
import TemplateIndexingDialog from './TemplateIndexingDialog'

export default {
  components: {
    ActivityTemplateForm,
    ActivityTemplateIndexingForm,
    ActivityTemplatePreInstanceForm,
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
        { text: this.$t('ActivityTemplateTable.indications'), value: 'indications.name' },
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
        'activities',
        'activity_groups',
        'activity_subgroups'
      ],
      test: true,
      urlPrefix: '/activity-instruction-templates'
    }
  },
  methods: {
    displayList (items) {
      return items.map(item => item.name).join(', ')
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
  mounted () {
    this.$store.dispatch('studiesGeneral/fetchNullValues')
  }
}
</script>
