<template>
<div>
  <n-n-table
    v-model="selected"
    :headers="updatedHeaders"
    :items="templates"
    item-key="uid"
    :export-object-label="exportFileLabel"
    :export-data-url="urlPrefix"
    :export-data-url-params="exportDataUrlParams"
    :server-items-length="total"
    sort-by="start_date"
    sort-desc
    :options.sync="options"
    :has-api="hasApi"
    :column-data-resource="urlPrefix"
    :column-data-parameters="extendedColumnDataParameters"
    @filter="filter"
    :history-title="$t('_global.audit_trail')"
    :history-data-fetcher="fetchGlobalAuditTrail"
    :history-html-fields="['template_name', 'name', 'guidance_text']"
    history-change-field="change_description"
    :history-change-field-label="$t('_global.change_description')"
    :history-excluded-headers="historyExcludedHeaders"
    :default-filters="defaultFilters"
    >
    <template v-slot:actions="">
      <v-btn
        v-if="!preInstanceMode"
        fab
        small
        color="primary"
        data-cy="add-template"
        @click="createTemplate()"
        :title="$t(`${translationType}.add`)"
        :disabled="!checkPermission($roles.LIBRARY_WRITE)"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-for="(_, slot) of $scopedSlots" v-slot:[slot]="scope">
      <slot :name="slot" v-bind="scope" />
    </template>
    <template v-slot:item.indications.name="{ item }">
      <template v-if="item.indications && item.indications.length">
        {{ item.indications|names }}
      </template>
      <template v-else>
        {{ $t('_global.not_applicable_long') }}
      </template>
    </template>
    <template v-slot:item.template_name="{ item }">
      <n-n-parameter-highlighter
        :name="item.template_name"
        default-color="orange"
        />
    </template>
    <template v-slot:item.name="{ item }">
      <n-n-parameter-highlighter
        :name="item.name"
        default-color="green"
        :show-prefix-and-postfix="false"
        />
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date | date }}
    </template>
    <template v-slot:item.status="{ item }">
      <status-chip :status="item.status" />
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu
        :actions="actions"
        :item="item"
        />
    </template>
  </n-n-table>
  <v-dialog v-model="showForm"
            @keydown.esc="closeForm"
            persistent
            :fullscreen="fullscreenForm"
            :max-width="fullscreenForm ? null : '800px'"
            :content-class="fullscreenForm ? 'fullscreen-dialog' : 'top-dialog'"
            :key="key"
            >
    <slot
      name="editform"
      v-bind:closeForm="closeForm"
      v-bind:selectedObject="selectedObject"
      v-bind:filter="filter"
      v-bind:updateTemplate="updateTemplate"
      v-bind:preInstanceMode="preInstanceMode"
      >
    </slot>
  </v-dialog>
  <v-dialog
    v-model="showHistory"
    @keydown.esc="closeHistory"
    persistent
    :max-width="globalHistoryDialogMaxWidth"
    :fullscreen="globalHistoryDialogFullscreen"
    >
    <history-table
      :title="historyTitle"
      @close="closeHistory"
      :headers="headers"
      :items="historyItems"
      :html-fields="historyHtmlFields"
      :excluded-headers="historyExcludedHeaders"
      />
  </v-dialog>
  <confirm-dialog ref="confirm" :action-cols="5" :text-cols="6" />
  <v-dialog v-model="showIndexingForm"
            persistent
            max-width="800px"
            >
    <slot name="indexingDialog"
          v-bind:closeDialog="() => showIndexingForm = false"
          v-bind:template="selectedObject"
          v-bind:show="showIndexingForm"
          v-bind:preInstanceMode="preInstanceMode"
          />
  </v-dialog>
  <v-dialog
    v-model="showPreInstanceForm"
    @keydown.esc="closeForm"
    persistent
    fullscreen
    content-class="fullscreen-dialog"
    >
    <slot name="preInstanceForm"
          v-bind:closeDialog="closePreInstanceForm"
          v-bind:template="selectedObject"
          />
  </v-dialog>
</div>
</template>

<script>
import Vue from 'vue'
import { bus } from '@/main'
import templatePreInstances from '@/api/templatePreInstances'
import templates from '@/api/templates'
import ActionsMenu from '@/components/tools/ActionsMenu'
import dataFormating from '@/utils/dataFormating'
import HistoryTable from '@/components/tools/HistoryTable'
import libraryConstants from '@/constants/libraries'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import NNTable from '@/components/tools/NNTable'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import StatusChip from '@/components/tools/StatusChip'
import statuses from '@/constants/statuses'
import filteringParameters from '@/utils/filteringParameters'
import { accessGuard } from '@/mixins/accessRoleVerifier'

export default Vue.extend({
  mixins: [accessGuard],
  name: 'studybuilder-template-table',
  props: {
    urlPrefix: {
      type: String,
      default: ''
    },
    translationType: {
      type: String,
      default: ''
    },
    objectType: {
      type: String,
      default: ''
    },
    hasApi: {
      type: Boolean,
      default: false
    },
    columnDataResource: {
      type: String,
      default: ''
    },
    columnDataParameters: {
      type: Object,
      required: false
    },
    headers: {
      type: Array,
      default: function () {
        return [
          {
            text: '',
            value: 'actions',
            sortable: false,
            width: '5%'
          },
          { text: this.$t('_global.library'), value: 'library.name' },
          { text: this.$t('_global.template'), value: 'name', width: '30%' },
          { text: this.$t('_global.modified'), value: 'start_date' },
          { text: this.$t('_global.modified_by'), value: 'fixme' },
          { text: this.$t('_global.status'), value: 'status' },
          { text: this.$t('_global.version'), value: 'version' }
        ]
      }
    },
    extraFiltersFunc: {
      type: Function,
      required: false
    },
    fullscreenForm: {
      type: Boolean,
      default: false
    },
    withIndexingProperties: {
      type: Boolean,
      default: true
    },
    historyFormatingFunc: {
      type: Function,
      required: false
    },
    historyExcludedHeaders: {
      type: Array,
      required: false
    },
    exportObjectLabel: {
      type: String,
      required: false
    },
    exportDataUrlParams: {
      type: Object,
      required: false
    },
    preInstanceMode: {
      type: Boolean,
      default: false
    },
    prepareDuplicatePayloadFunc: {
      type: Function,
      required: false
    },
    defaultFilters: {
      type: Array,
      required: false
    }
  },
  components: {
    ActionsMenu,
    HistoryTable,
    NNParameterHighlighter,
    ConfirmDialog,
    NNTable,
    StatusChip
  },
  data () {
    const actions = [
      {
        label: this.$t('_global.add_pre_instance'),
        icon: 'mdi-plus-circle-outline',
        iconColor: 'primary',
        condition: (item) => this.objectType !== 'timeframeTemplates' && !this.preInstanceMode && item.status === statuses.FINAL,
        click: this.openPreInstanceForm,
        accessRole: this.$roles.LIBRARY_WRITE
      },
      {
        label: this.$t('_global.edit'),
        icon: 'mdi-pencil-outline',
        iconColor: 'primary',
        condition: (item) => item.possible_actions.find(action => action === 'edit'),
        click: this.editTemplate,
        accessRole: this.$roles.LIBRARY_WRITE
      },
      {
        label: this.$t('_global.approve'),
        icon: 'mdi-check-decagram',
        iconColor: 'success',
        condition: (item) => item.possible_actions.find(action => action === 'approve'),
        click: this.approveTemplate,
        accessRole: this.$roles.LIBRARY_WRITE
      },
      {
        label: this.$t('_global.new_version'),
        icon: 'mdi-plus-circle-outline',
        iconColor: 'primary',
        condition: (item) => item.possible_actions.find(action => action === 'new_version'),
        click: this.createNewVersion,
        accessRole: this.$roles.LIBRARY_WRITE
      },
      {
        label: this.$t('_global.duplicate'),
        icon: 'mdi-content-copy',
        iconColor: 'primary',
        condition: (item) => this.preInstanceMode && item.status === statuses.FINAL,
        click: this.duplicatePreInstance,
        accessRole: this.$roles.LIBRARY_WRITE
      },
      {
        label: this.$t('_global.inactivate'),
        icon: 'mdi-close-octagon-outline',
        iconColor: 'primary',
        condition: (item) => item.possible_actions.find(action => action === 'inactivate'),
        click: this.inactivateTemplate,
        accessRole: this.$roles.LIBRARY_WRITE
      },
      {
        label: this.$t('_global.reactivate'),
        icon: 'mdi-undo-variant',
        iconColor: 'primary',
        condition: (item) => item.possible_actions.find(action => action === 'reactivate'),
        click: this.reactivateTemplate,
        accessRole: this.$roles.LIBRARY_WRITE
      },
      {
        label: this.$t('_global.delete'),
        icon: 'mdi-delete-outline',
        iconColor: 'error',
        condition: (item) => item.possible_actions.find(action => action === 'delete'),
        click: this.deleteTemplate,
        accessRole: this.$roles.LIBRARY_WRITE
      },
      {
        label: this.$t('_global.history'),
        icon: 'mdi-history',
        click: this.openTemplateHistory
      }
    ]
    if (this.withIndexingProperties) {
      actions.unshift({
        label: this.$t('_global.edit_indexing'),
        icon: 'mdi-pencil-outline',
        iconColor: 'primary',
        condition: (item) => item.status === statuses.FINAL,
        click: this.editTemplateIndexing,
        accessRole: this.$roles.LIBRARY_WRITE
      })
    }
    return {
      actions,
      api: null,
      historyHtmlFields: ['name', 'guidance_text'],
      historyItems: [],
      showForm: false,
      showIndexingForm: false,
      showHistory: false,
      showPreInstanceForm: false,
      selectedObject: null,
      appLabel: this.$t(this.translationType + '.singular_title'),
      selected: [],
      templates: [],
      options: {},
      total: 0,
      key: 0
    }
  },
  computed: {
    updatedHeaders () {
      const result = JSON.parse(JSON.stringify(this.headers))
      if (this.preInstanceMode) {
        const index = result.findIndex(header => header.value === 'name')
        if (index !== -1) {
          result[index].text = this.$t('_global.pre_instance_template')
          result.splice(index, 0, {
            text: this.$t('_global.parent_template'), value: 'template_name'
          })
        }
      }
      return result
    },
    historyTitle () {
      if (this.selectedObject) {
        return this.$t(
          'GenericTemplateTable.template_history_title',
          { templateUid: this.selectedObject.uid })
      }
      return ''
    },
    extendedColumnDataParameters () {
      const result = this.columnDataParameters ? { ...this.columnDataParameters } : { filters: {} }
      result.filters['library.name'] = { v: [libraryConstants.LIBRARY_SPONSOR] }
      return result
    },
    exportFileLabel () {
      return this.exportObjectLabel ? this.exportObjectLabel : this.objectType
    }
  },
  created () {
    if (!this.preInstanceMode) {
      this.api = templates(this.urlPrefix)
    } else {
      this.api = templatePreInstances(this.getBaseObjectType())
    }
  },
  methods: {
    createTemplate () {
      this.selectedObject = null
      this.showForm = true
    },
    editTemplate (template) {
      this.selectedObject = template
      this.showForm = true
    },
    updateTemplate (template, status) {
      this.templates.filter((item, pos) => {
        if (item.uid === template.uid && item.status === status) {
          this.$set(this.templates, pos, template)
          return true
        }
        return false
      })
    },
    async approveTemplate (template) {
      if (template.uid.includes('ActivityInstructionTemplate')) { // Temporary workaround for Activity Templates, will be deleted after backend instantiations activities implement
        const resp = await this.api.approveCascade(template.uid, false)
        this.updateTemplate(resp.data, template.status)
        bus.$emit('notification', { msg: this.$t(this.translationType + '.approve_success') })
      } else {
        const resp = await this.api.approveCascade(template.uid, true)
        this.updateTemplate(resp.data, template.status)
        const msg = this.$t(
          this.translationType +
            ((this.preInstanceMode) ? '.approve_pre_instance_success' : '.approve_success')
        )
        bus.$emit('notification', { msg })
      }
      this.$emit('refresh')
    },
    inactivateTemplate (template) {
      this.api.inactivate(template.uid).then(resp => {
        this.updateTemplate(resp.data, template.status)
        bus.$emit('notification', { msg: this.$t(this.translationType + ((this.preInstanceMode) ? '.inactivate_pre_instance_success' : '.inactivate_success')) })
        this.$emit('refresh')
      })
    },
    reactivateTemplate (template) {
      this.api.reactivate(template.uid).then(resp => {
        this.updateTemplate(resp.data, template.status)
        bus.$emit('notification', { msg: this.$t(this.translationType + ((this.preInstanceMode) ? '.reactivate_pre_instance_success' : '.approve_success')) })
        this.$emit('refresh')
      })
    },
    deleteTemplate (template) {
      this.api.delete(template.uid).then(() => {
        this.filter()
        const key = this.preInstanceMode
          ? `${this.translationType}.delete_pre_instance_success`
          : `${this.translationType}.delete_success`
        bus.$emit('notification', { msg: this.$t(key) })
      })
    },
    editTemplateIndexing (template) {
      this.selectedObject = template
      this.showIndexingForm = true
    },
    async fetchGlobalAuditTrail (options) {
      const resp = await this.api.getAuditTrail(options)
      if (this.historyFormatingFunc) {
        for (const item of resp.data.items) {
          this.historyFormatingFunc(item)
        }
      }
      return resp.data
    },
    async openTemplateHistory (template) {
      this.selectedObject = template
      const resp = await this.api.getVersions(template.uid)
      this.historyItems = this.transformItems(resp.data)
      this.showHistory = true
    },
    closeHistory () {
      this.selectedObject = null
      this.showHistory = false
    },
    openPreInstanceForm (template) {
      this.selectedObject = template
      this.showPreInstanceForm = true
    },
    closePreInstanceForm () {
      this.selectedObject = null
      this.showPreInstanceForm = false
    },
    async createNewVersion (template) {
      if (template.studyCount > 0) {
        const options = {
          cancelLabel: this.$t('_global.cancel_cascade_update'),
          agreeLabel: this.$t('_global.create_new_version'),
          type: 'warning',
          width: 1000
        }
        if (!await this.$refs.confirm.open(this.$tc('_global.cascade_update_warning', template.studyCount, { count: template.studyCount }), options)) {
          return
        }
      }
      const data = {
        name: template.name,
        change_description: this.$t(this.translationType + '.new_version_default_description')
      }
      this.api.createNewVersion(template.uid, data).then(resp => {
        this.updateTemplate(resp.data, template.status)
        bus.$emit('notification', { msg: this.$t(this.translationType + '.new_version_success') })
      })
    },
    duplicatePreInstance (item) {
      const data = {
        library_name: item.library.name,
        parameter_terms: item.parameter_terms,
        indication_uids: []
      }
      if (item.indications) {
        data.indication_uids = item.indications.map(ind => ind.term_uid)
      }
      if (this.prepareDuplicatePayloadFunc) {
        this.prepareDuplicatePayloadFunc(data, item)
      }
      this.api.create(item.template_uid, data).then(() => {
        bus.$emit('notification', { msg: this.$t(this.translationType + '.duplicate_success') })
        this.filter()
      })
    },
    closeForm () {
      this.selectedObject = null
      this.showForm = false
      this.key += 1
    },
    filter (filters, sort, filtersUpdated) {
      filters = (filters) ? JSON.parse(filters) : {}
      filters['library.name'] = { v: [libraryConstants.LIBRARY_SPONSOR] }
      if (this.extraFiltersFunc) {
        this.extraFiltersFunc(filters, this.preInstanceMode)
      }
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      this.api.get(params).then(resp => {
        if (resp.data.items !== undefined) {
          this.templates = resp.data.items
          this.total = resp.data.total
        } else {
          this.templates = resp.data
          this.total = this.templates.length
        }
      })
    },
    getBaseObjectType () {
      let result = this.objectType.replace('Templates', '')
      if (result === 'activity') {
        result = 'activity-instruction'
      }
      return result
    },
    transformItems (items) {
      const result = []
      for (const item of items) {
        const newItem = { ...item }
        if (item.indications) {
          if (item.indications.length) {
            newItem.indications.name = dataFormating.names(item.indications)
          } else {
            newItem.indications.name = this.$t('_global.not_applicable_long')
          }
        }
        if (this.historyFormatingFunc) {
          this.historyFormatingFunc(newItem)
        }
        result.push(newItem)
      }
      return result
    }
  },
  watch: {
    options: {
      handler () {
        this.filter()
      },
      deep: true
    }
  }
})
</script>
