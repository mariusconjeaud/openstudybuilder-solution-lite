<template>
<div>
  <n-n-table
    :headers="returnHeaders()"
    :items="activities"
    export-object-label="Activities"
    :hide-export-button="source === 'activities-by-grouping'"
    :hide-default-switches="source === 'activities-by-grouping'"
    :export-data-url="`concepts/activities/${source}`"
    item-key="item_key"
    :server-items-length="total"
    :options.sync="options"
    has-api
    :show-filter-bar-by-default="['activities', 'activity-instances'].includes(source) && !requested"
    @filter="fetchActivities"
    :column-data-resource="`concepts/activities/${source}`"
    @item-expanded="getSubGroups"
    :show-expand="isExpand()"
    :subTables="isExpand()"
    single-expand
    :filters-modify-function="modifyFilters"
    :modifiable-table="!isExpand()"
    :disable-filtering="source === 'activities-by-grouping'"
    :history-title="$t('_global.audit_trail')"
    :history-data-fetcher="source !== 'activities-by-grouping' ? fetchGlobalAuditTrail : null"
    history-change-field="change_description"
    :history-excluded-headers="historyExcludedHeaders"
    :initial-filters="requested ? { status: ['Draft', 'Final'] } : { status: ['Final'] }"
    :default-filters="[{ text: this.$t('_global.status'), value: 'status' }]"
    >
    <template v-slot:item="{ item, expand, isExpanded }" v-if="isExpand()">
      <tr style="background-color: var(--v-dfltBackgroundLight1-base)">
        <td width="1%">
          <v-btn @click="expand(!isExpanded)" v-if="isExpanded" icon>
            <v-icon dark>
              mdi-chevron-down
            </v-icon>
          </v-btn>
          <v-btn @click="expand(!isExpanded)" v-else icon>
            <v-icon dark>
              mdi-chevron-right
            </v-icon>
          </v-btn>
        </td>
        <td width="40%" :class="'font-weight-bold'">
          <v-row class="mt-2">
            {{ item.name }}
          </v-row>
        </td>
        <td width="25%">{{ item.start_date | date }}</td>
        <td width="15%"><status-chip :status="item.status" /></td>
        <td width="10%">{{ item.version }}</td>
      </tr>
    </template>
    <template v-slot:item.possible_actions="{ item }">
      <div class="pr-0 mr-0">
        <actions-menu :actions="actions" :item="item"/>
      </div>
    </template>
    <template v-slot:item.name="{ item }">
      <template v-if="source === 'activity-instances'">
        <router-link :to="{ name: 'ActivityInstanceOverview', params: { id: item.uid } }">
          {{ item.name }}
        </router-link>
      </template>
      <template v-else-if="source === 'activities'">
        <router-link :to="{ name: 'ActivityOverview', params: { id: item.uid } }">
          {{ item.name }}
        </router-link>
      </template>
      <div v-else :class="isExpand() ? 'font-weight-bold' : ''"> {{ item.name }} </div>
    </template>
    <template v-slot:item.status="{ item }">
      <status-chip :status="item.status" />
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date | date }}
    </template>
    <template v-slot:item.activity_groups="{ item }">
      {{ item.activity_groups | names }}
    </template>
    <template v-slot:item.activity_group.name="{ item }">
      <div v-html="groupsDisplay(item)" />
    </template>
    <template v-slot:item.activity_subgroup.name="{ item }">
      <div v-html="subGroupsDisplay(item)" />
    </template>
    <template v-slot:item.activities.name="{ item }">
      {{ activitiesDisplay(item) }}
    </template>
    <template v-slot:item.is_data_collected="{ item }">
      {{ item.is_data_collected|yesno }}
    </template>
    <template v-slot:item.is_required_for_activity="{ item }">
      {{ item.is_required_for_activity|yesno }}
    </template>
    <template v-slot:item.is_default_selected_for_activity="{ item }">
      {{ item.is_default_selected_for_activity|yesno }}
    </template>
    <template v-slot:item.is_data_sharing="{ item }">
      {{ item.is_data_sharing|yesno }}
    </template>
    <template v-slot:item.is_legacy_usage="{ item }">
      {{ item.is_legacy_usage|yesno }}
    </template>
    <template v-slot:expanded-item="{ headers }">
      <td :colspan="headers.length" class="pa-0">
        <v-data-table
          class="elevation-0"
          :headers="groupsHeaders"
          :items="subgroups"
          item-key="uid"
          hide-default-footer
          hide-default-header
          light
          :items-per-page="-1"
          :loading="loading"
          :show-expand="true"
          @item-expanded="getSubgroupActivities"
          single-expand
          >
          <template v-slot:item="{ item, expand, isExpanded }">
            <tr style="background-color: var(--v-dfltBackgroundLight2-base);">
              <td width="1%">
                <v-btn @click="expand(!isExpanded)" v-if="isExpanded" icon>
                  <v-icon dark>
                    mdi-chevron-down
                  </v-icon>
                </v-btn>
                <v-btn @click="expand(!isExpanded)" v-else icon>
                  <v-icon dark>
                    mdi-chevron-right
                  </v-icon>
                </v-btn>
              </td>
              <td width="40%" class="font-weight-bold">
                <div class="ml-6">
                  <v-row class="mt-2">
                    {{ item.name }}
                  </v-row>
                </div>
              </td>
              <td width="25%">{{ item.start_date | date }}</td>
              <td width="15%"><status-chip :status="item.status" /></td>
              <td width="10%">{{ item.version }}</td>
            </tr>
          </template>
          <template v-slot:expanded-item="{ headers }">
            <td :colspan="headers.length" class="pa-0">
              <v-data-table
                class="elevation-0"
                :headers="groupsHeaders"
                :items="subgroupActivities"
                item-key="uid"
                hide-default-footer
                hide-default-header
                light
                :items-per-page="-1"
                :loading="subLoading"
                :show-expand="true"
                >
                <template v-slot:item="{ item }">
                  <tr>
                    <td width="1%">
                      <v-btn icon>
                      </v-btn>
                    </td>
                    <td width="40%">
                      <div class="ml-12">
                        <v-row class="mt-2">
                          {{ item.name }}
                        </v-row>
                      </div>
                    </td>
                    <td width="25%">{{ item.start_date | date }}</td>
                    <td width="15%"><status-chip :status="item.status" /></td>
                    <td width="10%">{{ item.version }}</td>
                  </tr>
                </template>
              </v-data-table>
            </td>
          </template>
        </v-data-table>
      </td>
    </template>
    <template v-slot:actions="">
      <slot name="extraActions"></slot>
      <v-btn
        v-if="source !== 'activities-by-grouping'"
        fab
        dark
        small
        color="primary"
        @click.stop="showForm"
        :title="itemCreationTitle"
        :disabled="!checkPermission($roles.LIBRARY_WRITE)"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
  </n-n-table>
  <activities-form
    :open="showActivityForm"
    @close="closeForm"
    :edited-activity="activeItem"/>
  <requested-activities-form
    :open="showRequestedActivityForm"
    @close="closeForm"
    :edited-activity="activeItem"/>
  <v-dialog
      v-model="showGroupsForm"
      persistent
      max-width="800px"
      content-class="top-dialog"
    >
    <activities-groups-form
      ref="groupform"
      :open="showGroupsForm"
      :subgroup="!groupMode"
      @close="closeForm"
      :edited-group-or-subgroup="activeItem"
      />
  </v-dialog>
  <v-dialog
      v-model="showInstantiationsForm"
      persistent
      fullscreen
      content-class="fullscreen-dialog"
    >
    <activities-instantiations-form
      class="fullscreen-dialog"
      @close="closeForm"
      :edited-activity="activeItem"/>
  </v-dialog>
  <v-dialog
      v-model="showSponsorFromRequestedForm"
      persistent
      max-width="1200px"
      content-class="top-dialog"
    >
    <activities-create-sponsor-from-requested-form
      @close="closeForm"
      :edited-activity="activeItem"/>
  </v-dialog>
  <v-dialog
    v-model="showHistory"
    @keydown.esc="closeHistory"
    persistent
    :max-width="globalHistoryDialogMaxWidth"
    :fullscreen="globalHistoryDialogFullscreen"
    >
    <history-table
      :title="itemHistoryTitle"
      @close="closeHistory"
      :headers="returnHeaders()"
      :items="historyItems"
      :excluded-headers="historyExcludedHeaders"
      />
  </v-dialog>
</div>
</template>

<script>
import activities from '@/api/activities'
import ActionsMenu from '@/components/tools/ActionsMenu'
import { bus } from '@/main'
import HistoryTable from '@/components/tools/HistoryTable'
import NNTable from '@/components/tools/NNTable'
import StatusChip from '@/components/tools/StatusChip'
import ActivitiesForm from '@/components/library/ActivitiesForm'
import RequestedActivitiesForm from '@/components/library/RequestedActivitiesForm'
import ActivitiesGroupsForm from '@/components/library/ActivitiesGroupsForm'
import ActivitiesInstantiationsForm from '@/components/library/ActivitiesInstantiationsForm'
import ActivitiesCreateSponsorFromRequestedForm from '@/components/library/ActivitiesCreateSponsorFromRequestedForm'
import libConstants from '@/constants/libraries'
import { accessGuard } from '@/mixins/accessRoleVerifier'

export default {
  mixins: [accessGuard],
  components: {
    ActionsMenu,
    HistoryTable,
    NNTable,
    StatusChip,
    ActivitiesForm,
    RequestedActivitiesForm,
    ActivitiesGroupsForm,
    ActivitiesInstantiationsForm,
    ActivitiesCreateSponsorFromRequestedForm
  },
  computed: {
    itemCreationTitle () {
      if (this.source === 'activities') {
        return this.$t('ActivityForms.add_activity')
      } else if (this.source === 'activity-instances') {
        return this.$t('ActivityForms.addInstance')
      } else if (this.source === 'activity-groups') {
        return this.$t('ActivityForms.add_group')
      } else if (this.source === 'activity-sub-groups') {
        return this.$t('ActivityForms.add_subgroup')
      }
      return ''
    },
    itemHistoryTitle () {
      if (this.activeItem) {
        let type
        switch (this.source) {
          case 'activities':
            type = this.$t('ActivitiesTable.activity')
            break
          case 'activity-groups':
            type = this.$t('ActivitiesTable.activity_group')
            break
          case 'activity-sub-groups':
            type = this.$t('ActivitiesTable.activity_subgroup')
            break
          case 'activity-instances':
            type = this.$t('ActivitiesTable.activity_instance')
            break
        }
        return this.$t(
          'ActivitiesTable.item_history_title',
          { uid: this.activeItem.uid, type })
      }
      return ''
    }
  },
  props: {
    source: String,
    requested: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('ActivityTable.create_sponsor_from_request'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          condition: (item) => item.status === 'Final' && this.requested,
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.createSponsorFromRequested
        },
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: (item) => item.possible_actions.find(action => action === 'approve'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.approveItem
        },
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'edit'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.editItem
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'new_version'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.newItemVersion
        },
        {
          label: this.$t('_global.inactivate'),
          icon: 'mdi-close-octagon-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'inactivate'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.inactivateItem
        },
        {
          label: this.$t('_global.reactivate'),
          icon: 'mdi-undo-variant',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'reactivate'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.reactivateItem
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          condition: (item) => item.possible_actions.find(action => action === 'delete'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.deleteItem
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          accessRole: this.$roles.LIBRARY_READ,
          click: this.openItemHistory
        }
      ],
      activities: [],
      activitiesHeaders: [
        { text: '', value: 'possible_actions', width: '5%', noFilter: true },
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('ActivityTable.activity_group'), value: 'activity_group.name', externalFilterSource: 'concepts/activities/activity-groups$name', width: '15%', exludeFromHeader: ['is_data_collected'] },
        { text: this.$t('ActivityTable.activity_subgroup'), value: 'activity_subgroup.name', externalFilterSource: 'concepts/activities/activity-sub-groups$name', width: '15%', exludeFromHeader: ['is_data_collected'] },
        { text: this.$t('ActivityTable.activity_name'), value: 'name', externalFilterSource: 'concepts/activities/activities$name' },
        { text: this.$t('ActivityTable.sentence_case_name'), value: 'name_sentence_case' },
        { text: this.$t('ActivityTable.nci_concept_id'), value: 'nci_concept_id' },
        { text: this.$t('ActivityTable.abbreviation'), value: 'abbreviation' },
        { text: this.$t('ActivityTable.is_data_collected'), value: 'is_data_collected' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      instantiationsHeaders: [
        { text: '', value: 'possible_actions', width: '5%', noFilter: true },
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('ActivityTable.type'), value: 'activity_instance_class.name' },
        { text: this.$t('ActivityTable.activity'), value: 'activities.name', externalFilterSource: 'concepts/activities/activities$name', disableColumnFilters: true },
        { text: this.$t('ActivityTable.instance'), value: 'name' },
        { text: this.$t('_global.definition'), value: 'definition' },
        { text: this.$t('ActivityTable.nci_concept_id'), value: 'nci_concept_id' },
        { text: this.$t('ActivityTable.topic_code'), value: 'topic_code' },
        { text: this.$t('ActivityTable.adam_code'), value: 'adam_param_code' },
        { text: this.$t('ActivityTable.is_required_for_activity'), value: 'is_required_for_activity' },
        { text: this.$t('ActivityTable.is_default_selected_for_activity'), value: 'is_default_selected_for_activity' },
        { text: this.$t('ActivityTable.is_data_sharing'), value: 'is_data_sharing' },
        { text: this.$t('ActivityTable.is_legacy_usage'), value: 'is_legacy_usage' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.modified_by'), value: 'user_initials' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      groupsHeaders: [
        { text: this.$t('ActivityTable.group_or_subgroup'), value: 'name' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      requestedHeaders: [
        { text: '', value: 'possible_actions', width: '5%' },
        { text: this.$t('ActivityTable.activity_group'), value: 'activity_group.name', externalFilterSource: 'concepts/activities/activity-groups$name' },
        { text: this.$t('ActivityTable.activity_subgroup'), value: 'activity_subgroup.name', externalFilterSource: 'concepts/activities/activity-sub-groups$name' },
        { text: this.$t('ActivityTable.activity'), value: 'name', externalFilterSource: 'concepts/activities/activities$name' },
        { text: this.$t('ActivityTable.sentence_case_name'), value: 'name_sentence_case' },
        { text: this.$t('ActivityTable.abbreviation'), value: 'abbreviation' },
        { text: this.$t('ActivityTable.definition'), value: 'definition' },
        { text: this.$t('ActivityTable.rationale_for_request'), value: 'request_rationale' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.modified_by'), value: 'user_initials' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      activityGroupHeaders: [
        { text: '', value: 'possible_actions', width: '5%' },
        { text: this.$t('ActivityTable.activity_group'), value: 'name' },
        { text: this.$t('ActivityTable.sentence_case_name'), value: 'name_sentence_case' },
        { text: this.$t('ActivityTable.abbreviation'), value: 'abbreviation' },
        { text: this.$t('_global.definition'), value: 'definition' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      activitySubgroupHeaders: [
        { text: '', value: 'possible_actions', width: '5%' },
        { text: this.$t('ActivityTable.activity_group'), value: 'activity_groups', externalFilterSource: 'concepts/activities/activity-groups$name' },
        { text: this.$t('ActivityTable.activity_subgroup'), value: 'name' },
        { text: this.$t('ActivityTable.sentence_case_name'), value: 'name_sentence_case' },
        { text: this.$t('ActivityTable.abbreviation'), value: 'abbreviation' },
        { text: this.$t('_global.definition'), value: 'definition' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      groupMode: false,
      historyItems: [],
      historyExcludedHeaders: [
        'possible_actions'
      ],
      total: 0,
      options: {},
      filters: '',
      subgroups: [],
      currentGroup: '',
      currentSubGroup: '',
      showActivityForm: false,
      showRequestedActivityForm: false,
      showGroupsForm: false,
      showHistory: false,
      showInstantiationsForm: false,
      showSponsorFromRequestedForm: false,
      activeItem: null,
      loading: false,
      subLoading: false,
      subgroupActivities: []
    }
  },
  methods: {
    transformItems (items) {
      const activities = []
      if (this.source === 'activities') {
        for (const item of items) {
          if (item.activity_groupings.length > 0) {
            const groups = []
            const subgroups = []
            for (const grouping of item.activity_groupings) {
              groups.push(grouping.activity_group_name)
              subgroups.push(grouping.activity_subgroup_name)
            }
            activities.push({
              activity_group: { name: groups },
              activity_subgroup: { name: subgroups },
              item_key: item.uid,
              ...item
            })
          } else {
            activities.push({
              activity_group: { name: '' },
              activity_subgroup: { name: '' },
              item_key: item.uid,
              ...item
            })
          }
        }
      } else if (this.source === 'activity-instances') {
        for (const item of items) {
          if (item.activity_groupings.length > 0) {
            item.activities = [item.activity_groupings[0].activity]
            item.activity_group = item.activity_groupings[0].activity_group
            item.activity_subgroup = item.activity_groupings[0].activity_subgroup
          } else {
            item.activities = []
          }
          item.item_key = item.uid
          activities.push(
            item
          )
        }
      } else {
        for (const item of items) {
          item.item_key = item.uid
          activities.push(
            item
          )
        }
      }
      return activities
    },
    fetchActivities (filters, sort, filtersUpdated) {
      if (filtersUpdated) {
        /* Filters changed, reset page number */
        this.options.page = 1
      }
      if (filters !== undefined) {
        this.filters = filters
      }
      const params = {
        page_number: (this.options.page),
        page_size: this.options.itemsPerPage,
        total_count: true,
        sort_by: { name: true }
      }
      if (this.requested) {
        params.library = libConstants.LIBRARY_REQUESTED
      }
      if (this.filters && this.filters !== undefined && this.filters !== '{}' && this.source === 'activities') {
        const filtersObj = JSON.parse(this.filters)
        if (filtersObj['activity_group.name']) {
          params.activity_group_names = []
          filtersObj['activity_group.name'].v.forEach(value => {
            params.activity_group_names.push(value)
          })
          delete filtersObj['activity_group.name']
        }
        if (filtersObj['activity_subgroup.name']) {
          params.activity_subgroup_names = []
          filtersObj['activity_subgroup.name'].v.forEach(value => {
            params.activity_subgroup_names.push(value)
          })
          delete filtersObj['activity_subgroup.name']
        }
        if (filtersObj.name) {
          params.activity_names = []
          filtersObj.name.v.forEach(value => {
            params.activity_names.push(value)
          })
          delete filtersObj.name
        }
        if (Object.keys(filtersObj).length !== 0 && filtersObj.constructor === Object) {
          params.filters = JSON.stringify(filtersObj)
        }
      } else if (this.filters && this.filters !== undefined && this.filters !== '{}' && this.source === 'activity-instances') {
        const filtersObj = JSON.parse(this.filters)
        if (filtersObj['activities.name']) {
          params.activity_names = []
          filtersObj['activities.name'].v.forEach(value => {
            params.activity_names.push(value)
          })
          delete filtersObj['activities.name']
        }
        if (filtersObj.specimen) {
          params.specimen_names = []
          filtersObj.specimen.v.forEach(value => {
            params.specimen_names.push(value)
          })
          delete filtersObj.specimen
        }
        if (Object.keys(filtersObj).length !== 0 && filtersObj.constructor === Object) {
          params.filters = JSON.stringify(filtersObj)
        }
      } else if (filters !== undefined && filters !== '{}') {
        params.filters = filters
      }
      if (this.requested) {
        if (!params.filters) {
          params.filters = {}
        }
      }
      if (this.options.sortBy.length !== 0 && sort !== undefined) {
        params.sort_by = `{"${this.options.sortBy[0]}":${!sort}}`
      }
      const source = this.source !== 'activities-by-grouping' ? this.source : 'activity-groups'
      activities.get(params, source).then(resp => {
        this.activities = this.transformItems(resp.data.items)
        this.total = resp.data.total
      })
      activities.getSubGroups(this.currentGroup).then(resp => {
        this.subgroups = resp.data.items
      })
      activities.getSubGroupActivities(this.currentSubGroup).then(resp => {
        this.subgroupActivities = resp.data.items
      })
      if (this.$refs.groupform) {
        this.$refs.groupform.getGroups()
      }
    },
    async fetchGlobalAuditTrail (options) {
      const resp = await activities.getAuditTrail(this.source, options)
      return this.transformItems(resp.data.items)
    },
    modifyFilters (jsonFilter, params) {
      if (jsonFilter['activity_group.name']) {
        params.activity_group_names = []
        jsonFilter['activity_group.name'].v.forEach(value => {
          params.activity_group_names.push(value)
        })
        delete jsonFilter['activity_group.name']
      }
      if (jsonFilter['activity_subgroup.name']) {
        params.activity_subgroup_names = []
        jsonFilter['activity_subgroup.name'].v.forEach(value => {
          params.activity_subgroup_names.push(value)
        })
        delete jsonFilter['activity_subgroup.name']
      }
      if (jsonFilter.name) {
        params.activity_names = []
        jsonFilter.name.v.forEach(value => {
          params.activity_names.push(value)
        })
        delete jsonFilter.name
      }
      if (jsonFilter['activities.name']) {
        params.activity_names = []
        jsonFilter['activities.name'].v.forEach(value => {
          params.activity_names.push(value)
        })
        delete jsonFilter['activities.name']
      }
      if (jsonFilter.specimen) {
        params.specimen_names = []
        jsonFilter.activities.v.forEach(value => {
          params.specimen_names.push(value)
        })
        delete jsonFilter.specimen
      }
      return {
        jsonFilter: jsonFilter,
        params: params
      }
    },
    isExpand () {
      return this.source === 'activities-by-grouping'
    },
    subGroupsDisplay (item) {
      let display = ''
      if (item.activity_subgroup.name === '') {
        return ''
      } else {
        item.activity_subgroup.name.forEach(element => {
          display += '&#9679; ' + element + '</br>'
        })
        return display
      }
    },
    groupsDisplay (item) {
      let display = ''
      if (item.activity_group.name === '') {
        return ''
      } else {
        item.activity_group.name.forEach(element => {
          display += '&#9679; ' + element + '</br>'
        })
        return display
      }
    },
    activitiesDisplay (item) {
      let display = ''
      item.activities.forEach(element => {
        display += element.name + ', '
      })
      return display.slice(0, -2)
    },
    returnHeaders () {
      switch (this.source) {
        case 'activities':
          return this.requested ? this.requestedHeaders : this.activitiesHeaders
        case 'activity-groups':
          return this.activityGroupHeaders
        case 'activity-sub-groups':
          return this.activitySubgroupHeaders
        case 'activities-by-grouping':
          return this.groupsHeaders
        case 'activity-instances':
          return this.instantiationsHeaders
      }
    },
    inactivateItem (item, source) {
      source = (source === undefined) ? this.source : source
      activities.inactivate(item.uid, source).then(() => {
        bus.$emit('notification', { msg: this.$t(`ActivitiesTable.inactivate_${this.source}_success`), type: 'success' })
        this.fetchActivities()
      })
    },
    reactivateItem (item, source) {
      source = (source === undefined) ? this.source : source
      activities.reactivate(item.uid, source).then(() => {
        bus.$emit('notification', { msg: this.$t(`ActivitiesTable.reactivate_${this.source}_success`), type: 'success' })
        this.fetchActivities()
      })
    },
    deleteItem (item, source) {
      source = (source === undefined) ? this.source : source
      activities.delete(item.uid, source).then(() => {
        bus.$emit('notification', { msg: this.$t(`ActivitiesTable.delete_${this.source}_success`), type: 'success' })
        this.fetchActivities()
      })
    },
    approveItem (item, source) {
      source = (source === undefined) ? this.source : source
      activities.approve(item.uid, source).then(() => {
        bus.$emit('notification', { msg: this.$t(`ActivitiesTable.approve_${this.source}_success`), type: 'success' })
        this.fetchActivities()
      })
    },
    newItemVersion (item, source) {
      source = (source === undefined) ? this.source : source
      activities.newVersion(item.uid, source).then(() => {
        bus.$emit('notification', { msg: this.$t('_global.new_version_success'), type: 'success' })
        this.fetchActivities()
      })
    },
    showForm () {
      switch (this.source) {
        case 'activities':
          if (this.requested) {
            this.showRequestedActivityForm = true
          } else {
            this.showActivityForm = true
          }
          return
        case 'activity-groups':
          this.groupMode = true
          this.showGroupsForm = true
          return
        case 'activity-sub-groups':
          this.groupMode = false
          this.showGroupsForm = true
          return
        case 'activity-instances':
          this.showInstantiationsForm = true
      }
    },
    editItem (item) {
      this.activeItem = item
      switch (this.source) {
        case 'activities':
          if (this.requested) {
            this.showRequestedActivityForm = true
          } else {
            this.showActivityForm = true
          }
          return
        case 'activity-groups':
          this.groupMode = true
          this.showGroupsForm = true
          return
        case 'activity-sub-groups':
          this.groupMode = false
          this.showGroupsForm = true
          return
        case 'activity-instances':
          this.showInstantiationsForm = true
      }
    },
    async openItemHistory (item) {
      this.activeItem = item
      const resp = await activities.getVersions(this.source, item.uid)
      this.historyItems = this.transformItems(resp.data)
      this.showHistory = true
    },
    closeHistory () {
      this.activeItem = null
      this.showHistory = false
    },
    createSponsorFromRequested (item) {
      this.activeItem = item
      this.showSponsorFromRequestedForm = true
    },
    getSubGroups ({ item }) {
      this.subgroups = []
      this.loading = true
      this.currentGroup = item.uid
      activities.getSubGroups(item.uid).then(resp => {
        this.subgroups = resp.data.items
        this.loading = false
      })
    },
    getSubgroupActivities ({ item }) {
      this.subgroupActivities = []
      this.subLoading = true
      this.currentSubGroup = item.uid
      activities.getSubGroupActivities(item.uid).then(resp => {
        this.subgroupActivities = resp.data.items
        this.subLoading = false
      })
    },
    closeForm () {
      this.showActivityForm = false
      this.showRequestedActivityForm = false
      this.showGroupsForm = false
      this.showInstantiationsForm = false
      this.showSponsorFromRequestedForm = false
      this.activeItem = null
      this.fetchActivities()
    }
  },
  mounted () {
    this.fetchActivities()
  },
  watch: {
    options: {
      handler () {
        this.fetchActivities()
      },
      deep: true
    }
  }
}
</script>
