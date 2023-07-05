<template>
<div>
  <n-n-table
    :headers="headers"
    :items="instances"
    item-key="uid"
    sort-by="start_date"
    sort-desc
    has-api
    @filter="fetchInstances"
    :options.sync="options"
    :export-data-url="baseUrl"
    v-bind="$attrs"
    v-on="$listeners"
    >
    <template v-slot:item.name="{ item }">
      <n-n-parameter-highlighter :name="item.name" :show-prefix-and-postfix="false" />
    </template>
    <template v-slot:[`item.${type}_template.name`]="{ item }">
      <n-n-parameter-highlighter :name="item[`${type}_template`].name" default-color="orange" />
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date | date }}
    </template>
    <template v-slot:item.status="{ item }">
      <status-chip :status="item.status" />
    </template>
    <template v-slot:item.study_count="{ item }">
      <v-chip small color="primary">{{ item.study_count }}</v-chip>
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
  </n-n-table>
  <v-dialog v-model="showHistory"
            persistent
            @keydown.esc="closeHistory"
            :max-width="globalHistoryDialogMaxWidth"
            :fullscreen="globalHistoryDialogFullscreen"
            >
    <history-table
      :title="historyTitle"
      @close="closeHistory"
      :headers="headers"
      :items="historyItems"
      :html-fields="historyHtmlFields"
      />
  </v-dialog>
  <v-dialog v-model="showStudies"
            persistent
            @keydown.esc="closeInstanceStudies"
            max-width="1200px">
    <instance-studies-dialog
      v-if="selectedInstance"
      :template="selectedInstance[`${type}_template`].name"
      :text="selectedInstance.name"
      :type="type"
      :studies="studies"
      @close="closeInstanceStudies"
      />
  </v-dialog>
</div>
</template>

<script>
import ActionsMenu from '@/components/tools/ActionsMenu'
import filteringParameters from '@/utils/filteringParameters'
import HistoryTable from '@/components/tools/HistoryTable'
import InstanceStudiesDialog from './InstanceStudiesDialog'
import libraryObjects from '@/api/libraryObjects'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import NNTable from '@/components/tools/NNTable'
import StatusChip from '@/components/tools/StatusChip'

export default {
  components: {
    ActionsMenu,
    HistoryTable,
    InstanceStudiesDialog,
    NNParameterHighlighter,
    NNTable,
    StatusChip
  },
  props: {
    instances: Array,
    fetchInstancesActionName: String,
    fetchInstancesExtraFilters: {
      type: Object,
      required: false
    },
    type: String,
    baseUrl: String
  },
  computed: {
    historyTitle () {
      if (this.selectedInstance) {
        return this.$t('InstanceTable.item_history_title', { type: this.type, instance: this.selectedInstance.uid })
      }
      return ''
    }
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openHistory
        },
        {
          label: this.$t('InstanceTable.show_studies', { type: this.type }),
          icon: 'mdi-dots-horizontal-circle',
          click: this.showInstanceStudies
        }
      ],
      headers: [
        {
          text: '',
          value: 'actions',
          sortable: false,
          width: '5%'
        },
        { text: this.$t('_global.library'), value: 'library.name' },
        { text: this.$t('_global.template'), value: `${this.type}_template.name`, width: '30%', filteringName: `${this.type}_template.name_plain` },
        { text: this.$t(`_global.${this.type}`), value: 'name', filteringName: 'name_plain' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' },
        { text: this.$t('ObjectiveTable.studies_count'), value: 'study_count' }
      ],
      historyItems: [],
      historyHtmlFields: [`${this.type}_template.name`, 'name'],
      studies: [],
      showStudies: false,
      showHistory: false,
      selectedInstance: null,
      options: {}
    }
  },
  methods: {
    closeHistory () {
      this.showHistory = false
    },
    closeInstanceStudies () {
      this.showStudies = false
    },
    fetchInstances (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      if (this.fetchInstancesExtraFilters) {
        if (params.filters) {
          params.filters = { ...JSON.parse(params.filters), ...this.fetchInstancesExtraFilters }
        } else {
          params.filters = this.fetchInstancesExtraFilters
        }
      }
      this.$store.dispatch(this.fetchInstancesActionName, params)
    },
    async openHistory (instance) {
      this.selectedInstance = instance
      const resp = await this.api.getVersions(instance.uid)
      this.historyItems = resp.data
      this.showHistory = true
    },
    async showInstanceStudies (instance) {
      this.selectedInstance = instance
      const resp = await this.api.getStudies(instance.uid)
      this.studies = resp.data
      this.showStudies = true
    }
  },
  mounted () {
    this.api = libraryObjects(this.baseUrl)
    this.fetchInstances()
  }
}
</script>
