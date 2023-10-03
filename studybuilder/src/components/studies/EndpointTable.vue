<template>
<div>
  <n-n-table
    key="endpointTable1"
    :headers="headers"
    :items="formatedStudyEndpoints"
    item-key="study_endpoint_uid"
    has-api
    :column-data-resource="`studies/${selectedStudy.uid}/study-endpoints`"
    :export-data-url="exportDataUrl"
    export-object-label="StudyEndpoints"
    :options.sync="options"
    :server-items-length="total"
    @filter="fetchEndpoints"
    :history-data-fetcher="fetchEndpointsHistory"
    :history-title="$t('StudyEndpointsTable.global_history_title')"
    :history-html-fields="historyHtmlFields"
    >
    <template v-slot:afterSwitches>
      <div :title="$t('NNTableTooltips.reorder_content')">
        <v-switch
          v-model="sortMode"
          :label="$t('NNTable.reorder_content')"
          hide-details
          class="mr-6"
          />
      </div>
    </template>
    <template v-slot:actions="">
      <slot name="extraActions"></slot>
      <v-btn
        fab
        small
        color="primary"
        @click.stop="showForm = true"
        :title="$t('StudyEndpointsTable.add_endpoint')"
        :disabled="!checkPermission($roles.STUDY_WRITE)"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:body="props" v-if="sortMode">
      <draggable
        :list="props.items"
        tag="tbody"
        :move="checkEndpointLevel"
        @change="onChange($event)"
        >
        <tr
          v-for="(item, index) in props.items"
          :key="index"
          >
          <td width="3%">
            <actions-menu
              :actions="actions"
              :item="item"
              :badge="actionsMenuBadge(item)"
              />
          </td>
          <td width="5%">
            <v-icon
              small
              class="page__grab-icon">
              mdi-sort
            </v-icon>
            {{ item.order }}
          </td>
          <td>
            <template v-if="item.endpoint_level">{{ item.endpoint_level.sponsor_preferred_name }}</template>
          </td>
          <td>
            <template v-if="item.endpoint_sublevel">{{ item.endpoint_sublevel.sponsor_preferred_name }}</template>
          </td>
          <td width="25%">
            <n-n-parameter-highlighter
              v-if="item.endpoint"
              :name="item.endpoint.name"
              :show-prefix-and-postfix="false"
              />
          </td>
          <td width="10%">{{ item.units }}</td>
          <td width="25%">
            <n-n-parameter-highlighter
              v-if="item.timeframe"
              :name="item.timeframe.name"
              :show-prefix-and-postfix="false"
              />
            <span v-else>{{ $t('StudyEndpointForm.select_later') }}</span>
          </td>
          <td width="25%">
            <n-n-parameter-highlighter
              v-if="item.study_objective"
              :name="item.study_objective.objective.name"
              :show-prefix-and-postfix="false"
              />
            <span v-else>{{ $t('StudyEndpointForm.select_later') }}</span>
          </td>
          <td width="10%">{{ item.start_date | date }}</td>
          <td width="10%">{{ item.user_initials }}</td>
        </tr>
      </draggable>
    </template>
    <template v-slot:item.name="{ item }">
      <template v-if="item.endpoint_template">
        <n-n-parameter-highlighter
          :name="item.endpoint_template.name"
          default-color="orange"
          />
      </template>
      <template v-else-if="item.endpoint">
        <n-n-parameter-highlighter
          :name="item.endpoint.name"
          :show-prefix-and-postfix="false"
          />
      </template>
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu
        :actions="actions"
        :item="item"
        :badge="actionsMenuBadge(item)"
        />
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date | date }}
    </template>
    <template v-slot:item.endpoint.name="{ item }">
    <div class="d-flex">
      <n-n-parameter-highlighter
        v-if="item.endpoint"
        :name="item.endpoint.name"
        :show-prefix-and-postfix="false"
        />
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-icon
            v-if="item.endpoint && item.endpoint.name.length > 254"
            class="mb-2 ml-1"
            v-bind="attrs"
            v-on="on"
            color="red">
            mdi-alert-circle-outline
          </v-icon>
        </template>
        <span>{{ $t('StudyEndpointForm.endpoint_title_warning') }}</span>
      </v-tooltip>
    </div>
    </template>
    <template v-slot:item.study_objective.objective.name="{ item }">
      <n-n-parameter-highlighter
        v-if="item.study_objective"
        :name="item.study_objective.objective.name"
        :show-prefix-and-postfix="false"
        />
      <span v-else>{{ $t('StudyEndpointForm.select_later') }}</span>
    </template>
    <template v-slot:item.timeframe.name="{ item }">
      <n-n-parameter-highlighter
        v-if="item.timeframe"
        :name="item.timeframe.name"
        :show-prefix-and-postfix="false"
        />
      <span v-else>{{ $t('StudyEndpointForm.select_later') }}</span>
    </template>
  </n-n-table>
  <v-dialog v-model="showForm"
            persistent
            fullscreen
            hide-overlay
            content-class="fullscreen-dialog"
            >
    <endpoint-form
      :study-endpoint="selectedStudyEndpoint"
      :current-study-endpoints="studyEndpoints"
      @close="closeForm"
      class="fullscreen-dialog"
      @added="fetchEndpoints"
      />
  </v-dialog>
  <endpoint-edit-form
    :open="showEditForm"
    @close="closeEditForm"
    :study-endpoint="selectedStudyEndpoint"
    @updated="fetchEndpoints"
    />
  <v-dialog v-model="showHistory"
            @keydown.esc="closeHistory"
            persistent
            :max-width="globalHistoryDialogMaxWidth"
            :fullscreen="globalHistoryDialogFullscreen">
    <history-table
      :title="studyEndpointHistoryTitle"
      @close="closeHistory"
      :headers="headers"
      :items="endpointHistoryItems"
      :html-fields="historyHtmlFields"
      />
  </v-dialog>
  <confirm-dialog ref="confirm" width="600"/>
  <v-snackbar
    v-model="snackbar"
    color="error"
    top
    >
    <v-icon class="mr-2">mdi-alert</v-icon>
    {{ $t('StudyEndpointsTable.sort_help_msg') }}
  </v-snackbar>
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import { bus } from '@/main'
import study from '@/api/study'
import ActionsMenu from '@/components/tools/ActionsMenu'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import EndpointEditForm from '@/components/studies/EndpointEditForm'
import EndpointForm from '@/components/studies/EndpointForm'
import HistoryTable from '@/components/tools/HistoryTable'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import statuses from '@/constants/statuses'
import NNTable from '@/components/tools/NNTable'
import draggable from 'vuedraggable'
import filteringParameters from '@/utils/filteringParameters'
import { accessGuard } from '@/mixins/accessRoleVerifier'

export default {
  mixins: [accessGuard],
  components: {
    ActionsMenu,
    NNParameterHighlighter,
    EndpointEditForm,
    EndpointForm,
    HistoryTable,
    ConfirmDialog,
    NNTable,
    draggable
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      studyEndpoints: 'studyEndpoints/studyEndpoints',
      total: 'studyEndpoints/total'
    }),
    filteredHeaders () {
      return this.headers.filter(header => header.show === true || header.show === undefined)
    },
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}/study-endpoints`
    },
    formatedStudyEndpoints () {
      return this.transformItems(this.studyEndpoints)
    },
    studyEndpointHistoryTitle () {
      if (this.selectedStudyEndpoint) {
        return this.$t(
          'StudyEndpointsTable.study_endpoint_history_title',
          { studyEndpointUid: this.selectedStudyEndpoint.study_endpoint_uid })
      }
      return ''
    }
  },
  data () {
    return {
      abortConfirm: false,
      actions: [
        {
          label: this.$t('StudyEndpointsTable.update_timeframe_version_retired'),
          icon: 'mdi-alert-outline',
          iconColor: 'orange',
          condition: this.isTimeframeRetired,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('StudyEndpointsTable.update_timeframe_version'),
          icon: 'mdi-bell-ring-outline',
          iconColorFunc: this.itemUpdateAborted,
          condition: this.timeframeNeedsUpdate,
          click: this.updateTimeframeVersion,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('StudyEndpointsTable.update_endpoint_version_retired'),
          icon: 'mdi-alert-outline',
          iconColor: 'orange',
          condition: this.isEndpointRetired,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('StudyEndpointsTable.update_endpoint_version'),
          icon: 'mdi-bell-ring-outline',
          iconColorFunc: this.itemUpdateAborted,
          condition: this.endpointNeedsUpdate,
          click: this.updateEndpointVersion,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          click: this.editStudyEndpoint,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          click: this.deleteStudyEndpoint,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openEndpointHistory
        }
      ],
      actionsMenu: false,
      endpointHistoryItems: [],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('StudyEndpointsTable.order'), value: 'order', width: '5%' },
        { text: this.$t('StudyEndpointsTable.endpoint_level'), value: 'endpoint_level.sponsor_preferred_name' },
        { text: this.$t('StudyEndpointsTable.endpoint_sub_level'), value: 'endpoint_sublevel.sponsor_preferred_name' },
        { text: this.$t('StudyEndpointsTable.endpoint_title'), value: 'name', width: '25%' },
        { text: this.$t('StudyEndpointsTable.units'), value: 'units', width: '10%' },
        { text: this.$t('StudyEndpointsTable.time_frame'), value: 'timeframe.name', width: '25%' },
        { text: this.$t('StudyEndpointsTable.objective'), value: 'study_objective.objective.name', filteringName: 'study_objective.objective.name', width: '25%' },
        { text: this.$t('_global.modified'), value: 'start_date', width: '10%' },
        { text: this.$t('_global.modified_by'), value: 'user_initials', width: '10%' }
      ],
      historyHtmlFields: ['endpoint.name', 'timeframe.name', 'study_objective.objective.name'],
      selectedStudyEndpoint: null,
      showEditForm: false,
      showForm: false,
      showHistory: false,
      snackbar: false,
      sortBy: 'start_date',
      sortMode: false,
      endpoints: [],
      options: {}
    }
  },
  methods: {
    fetchEndpoints (filters, sort, filtersUpdated) {
      if (this.options.sortBy.length > 0) {
        const filterName = this.headers.find(header => header.value === this.options.sortBy[0]).filteringName
        if (filterName) {
          this.options.sortBy[0] = filterName
        }
      }
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      params.studyUid = this.selectedStudy.uid
      this.$store.dispatch('studyEndpoints/fetchStudyEndpoints', params)
    },
    async fetchEndpointsHistory () {
      const resp = await study.getStudyEndpointsAuditTrail(this.selectedStudy.uid)
      return this.transformItems(resp.data)
    },
    actionsMenuBadge (item) {
      if (this.endpointNeedsUpdate(item) || this.timeframeNeedsUpdate(item)) {
        return {
          color: 'error',
          icon: 'mdi-bell-outline'
        }
      }
      if (!item.endpoint && item.endpoint_template && item.endpoint_template.parameters.length > 0) {
        return {
          color: 'error',
          icon: 'mdi-exclamation'
        }
      }
      return null
    },
    timeframeNeedsUpdate (item) {
      if (item.latest_timeframe) {
        if (!this.isTimeframeRetired(item)) {
          return item.timeframe.version !== item.latest_timeframe.version
        }
      }
      return false
    },
    isTimeframeRetired (item) {
      if (item.latest_timeframe) {
        return item.latest_timeframe.status === statuses.RETIRED
      }
      return false
    },
    async updateTimeframeVersion (item) {
      const options = {
        type: 'warning',
        width: 1000,
        cancelLabel: this.$t('StudyObjectivesTable.keep_old_version'),
        agreeLabel: this.$t('StudyObjectivesTable.use_new_version')
      }
      const message = this.$t('StudyEndpointsTable.update_timeframe_version_alert') + ' ' +
            this.$t('StudyEndpointsTable.previous_version') +
            ' ' + item.timeframe.name_plain +
            ' ' + this.$t('StudyEndpointsTable.new_version') +
            ' ' + item.latest_timeframe.name_plain

      if (await this.$refs.confirm.open(message, options)) {
        const args = {
          studyUid: item.study_uid,
          studyEndpointUid: item.study_endpoint_uid
        }
        this.$store.dispatch('studyEndpoints/updateStudyEndpointTimeframeLatestVersion', args).then(resp => {
          bus.$emit('notification', { msg: this.$t('StudyObjectivesTable.update_version_successful') })
        })
      } else {
        this.abortConfirm = true
        const args = {
          studyUid: item.study_uid,
          studyEndpointUid: item.study_endpoint_uid
        }
        this.$store.dispatch('studyEndpoints/updateStudyEndpointAcceptVersion', args).then(resp => {
        })
      }
    },
    endpointNeedsUpdate (item) {
      if (item.latest_endpoint) {
        if (!this.isEndpointRetired(item)) {
          return item.endpoint.version !== item.latest_endpoint.version
        }
      }
      return false
    },
    isEndpointRetired (item) {
      if (item.latest_endpoint) {
        return item.latest_endpoint.status === statuses.RETIRED
      }
      return false
    },
    itemUpdateAborted (item) {
      return item.acceptedVersion ? '' : 'error'
    },
    async updateEndpointVersion (item) {
      const options = {
        type: 'warning',
        width: 1200,
        cancelLabel: this.$t('StudyObjectivesTable.keep_old_version'),
        agreeLabel: this.$t('StudyObjectivesTable.use_new_version')
      }
      const message = this.$t('StudyEndpointsTable.update_endpoint_version_alert') + ' ' + this.$t('StudyEndpointsTable.previous_version') +
      ' ' + item.endpoint.name_plain + ' ' + this.$t('StudyEndpointsTable.new_version') + ' ' + item.latest_endpoint.name_plain

      if (await this.$refs.confirm.open(message, options)) {
        const args = {
          studyUid: item.study_uid,
          studyEndpointUid: item.study_endpoint_uid
        }
        this.$store.dispatch('studyEndpoints/updateStudyEndpointEndpointLatestVersion', args).then(() => {
          bus.$emit('notification', { msg: this.$t('StudyEndpointsTable.update_version_successful') })
        })
      } else {
        this.abortConfirm = true
        const args = {
          studyUid: item.study_uid,
          studyEndpointUid: item.study_endpoint_uid
        }
        await this.$store.dispatch('studyEndpoints/updateStudyEndpointAcceptVersion', args)
      }
    },
    closeForm () {
      this.showForm = false
      this.selectedStudyEndpoint = null
      this.fetchEndpoints()
    },
    closeEditForm () {
      this.showEditForm = false
      this.selectedStudyEndpoint = null
    },
    getHeaderLabel (value) {
      return this.headers.filter(item => item.value === value)[0].text
    },
    editStudyEndpoint (studyEndpoint) {
      this.selectedStudyEndpoint = studyEndpoint
      this.showEditForm = true
    },
    displayUnits (units) {
      const unitNames = units.units.map(unit => unit.name)
      if (unitNames.length > 1) {
        return unitNames.join(` ${units.separator} `)
      }
      return unitNames[0]
    },
    async deleteStudyEndpoint (studyEndpoint) {
      const options = { type: 'warning' }
      const endpoint = studyEndpoint.endpoint ? studyEndpoint.endpoint.name_plain : '(unnamed)'

      if (await this.$refs.confirm.open(this.$t('StudyEndpointsTable.confirm_delete', { endpoint }), options)) {
        // Make sure to set current studyObjective so the list of
        // endpoints is updated after deletion
        this.$store.dispatch('studyEndpoints/deleteStudyEndpoint', {
          studyUid: this.selectedStudy.uid,
          studyEndpointUid: studyEndpoint.study_endpoint_uid
        }).then(resp => {
          bus.$emit('notification', { msg: this.$t('StudyEndpointsTable.delete_success') })
          this.fetchEndpoints()
        })
      }
    },
    closeHistory () {
      this.selectedStudyEndpoint = null
      this.showHistory = false
    },
    async openEndpointHistory (studyEndpoint) {
      this.selectedStudyEndpoint = studyEndpoint
      const resp = await study.getStudyEndpointAuditTrail(this.selectedStudy.uid, studyEndpoint.study_endpoint_uid)
      this.endpointHistoryItems = this.transformItems(resp.data)
      this.showHistory = true
    },
    /*
    ** Prevent dragging between different endpoint levels
    */
    checkEndpointLevel (event) {
      const leftOrder = event.draggedContext.element.endpoint_level ? event.draggedContext.element.endpoint_level.order : null
      const rightOrder = event.relatedContext.element.endpoint_level ? event.relatedContext.element.endpoint_level.order : null
      const result = leftOrder === rightOrder
      this.snackbar = !result
      return result
    },
    onChange (event) {
      const studyEndpoint = event.moved.element
      const newOrder = this.studyEndpoints[event.moved.newIndex].order
      study.updateStudyEndpointOrder(studyEndpoint.study_uid, studyEndpoint.study_endpoint_uid, newOrder).then(resp => {
      })
    },
    transformItems (items) {
      const result = []
      for (const item of items) {
        const newItem = { ...item }
        if (item.endpoint_units && item.endpoint_units.units) {
          newItem.units = this.displayUnits(item.endpoint_units)
        }
        result.push(newItem)
      }
      return result
    }
  },
  mounted () {
    this.$store.dispatch('studiesGeneral/fetchAllUnits')
    this.$store.dispatch('studiesGeneral/fetchEndpointLevels')
    this.$store.dispatch('studiesGeneral/fetchEndpointSubLevels')
    this.fetchEndpoints()
  },
  watch: {
    sortMode (value) {
      this.$set(this.headers[0], 'show', value)
      this.headers.forEach(header => {
        this.$set(header, 'sortable', !value)
      })
      this.sortBy = (value) ? 'order' : 'start_date'
    },
    options () {
      this.fetchEndpoints()
    }
  }
}
</script>
<style scoped>
.roundChip {
  width: 25px;
  justify-content: space-evenly;
}
</style>
