<template>
<div>
  <n-n-table
    :headers="returnHeaders()"
    :items="activities"
    export-object-label="Activities"
    :export-data-url="`concepts/activities/${source}`"
    item-key="uid"
    :server-items-length="total"
    :options.sync="options"
    has-api
    @filter="fetchActivities"
    :column-data-resource="`concepts/activities/${source}`"
    @item-expanded="getSubGroups"
    :show-expand="isExpand()"
    :subTables="isExpand()"
    single-expand
    :filters-modify-function="modifyFilters"
    :modifiable-table="!isExpand()"
    class="tableMinWidth"
    >
    <template v-slot:item="{ item, expand, isExpanded }" v-if="isExpand()">
      <tr style="background-color: lightskyblue">
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
            <actions-menu :actions="actions" :item="item"/>{{ item.name }}
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
      {{ groupsDisplay(item) }}
    </template>
    <template v-slot:item.activity_sub_groups="{ item }">
      {{ subGroupsDisplay(item) }}
    </template>
    <template v-slot:item.activities="{ item }">
      {{ activitiesDisplay(item) }}
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
            <tr>
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
                    <actions-menu :actions="actions" :item="item" :source="'activity-sub-groups'"/>{{ item.name }}
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
                          <actions-menu :actions="actions" :item="item" :source="'activities'"/>{{ item.name }}
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
        fab
        dark
        small
        color="primary"
        @click.stop="showForm"
        :title="$t('CodelistCreationForm.title')"
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
    :edited-activity="activeActivity"/>
  <requested-activities-form
    :open="showRequestedActivityForm"
    @close="closeForm"
    :edited-activity="activeActivity"/>
  <v-dialog
      v-model="showGroupsForm"
      persistent
      max-width="800px"
      content-class="top-dialog"
    >
    <activities-groups-form
      @close="closeForm"
      :edited-activity="activeActivity"/>
  </v-dialog>
  <v-dialog
      v-model="showInstantiationsForm"
      persistent
      max-width="800px"
      content-class="top-dialog"
    >
    <activities-instantiations-form
      @close="closeForm"
      :edited-activity="activeActivity"/>
  </v-dialog>
  <v-dialog
      v-model="showSponsorFromRequestedForm"
      persistent
      max-width="1200px"
      content-class="top-dialog"
    >
    <activities-create-sponsor-from-requested-form
      @close="closeForm"
      :edited-activity="activeActivity"/>
  </v-dialog>
</div>
</template>

<script>
import activities from '@/api/activities'
import ActionsMenu from '@/components/tools/ActionsMenu'
import { bus } from '@/main'
import NNTable from '@/components/tools/NNTable'
import StatusChip from '@/components/tools/StatusChip'
import ActivitiesForm from '@/components/library/ActivitiesForm'
import RequestedActivitiesForm from '@/components/library/RequestedActivitiesForm'
import ActivitiesGroupsForm from '@/components/library/ActivitiesGroupsForm'
import ActivitiesInstantiationsForm from '@/components/library/ActivitiesInstantiationsForm'
import ActivitiesCreateSponsorFromRequestedForm from '@/components/library/ActivitiesCreateSponsorFromRequestedForm'
import libConstants from '@/constants/libraries'
import statuses from '@/constants/statuses'

export default {
  components: {
    ActionsMenu,
    NNTable,
    StatusChip,
    ActivitiesForm,
    RequestedActivitiesForm,
    ActivitiesGroupsForm,
    ActivitiesInstantiationsForm,
    ActivitiesCreateSponsorFromRequestedForm
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
          icon: 'mdi-pencil',
          iconColor: 'primary',
          condition: (item) => item.status === 'Final' && this.requested,
          click: this.createSponsorFromRequested
        },
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: (item) => item.possible_actions.find(action => action === 'approve'),
          click: this.approveActivity
        },
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'edit'),
          click: this.editActivity
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'new_version'),
          click: this.newActivityVersion
        },
        {
          label: this.$t('_global.inactivate'),
          icon: 'mdi-close-octagon-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'inactivate'),
          click: this.inactivateActivity
        },
        {
          label: this.$t('_global.reactivate'),
          icon: 'mdi-undo-variant',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'reactivate'),
          click: this.reactivateActivity
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete',
          iconColor: 'error',
          condition: (item) => item.possible_actions.find(action => action === 'delete'),
          click: this.deleteActivity
        }
      ],
      activities: [],
      activitiesHeaders: [
        { text: '', value: 'possible_actions', width: '5%' },
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('ActivityTable.activity_group'), value: 'activity_group.name', externalFilterSource: 'concepts/activities/activity-groups$name' },
        { text: this.$t('ActivityTable.activity_subgroup'), value: 'activity_subgroup.name', externalFilterSource: 'concepts/activities/activity-sub-groups$name' },
        { text: this.$t('ActivityTable.activity_name'), value: 'name', externalFilterSource: 'concepts/activities/activities$name' },
        { text: this.$t('ActivityTable.sentence_case_name'), value: 'name_sentence_case' },
        { text: this.$t('ActivityTable.abbreviation'), value: 'abbreviation' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      instantiationsHeaders: [
        { text: '', value: 'possible_actions', width: '5%' },
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('ActivityTable.type'), value: 'activity_instance_class.name' },
        { text: this.$t('ActivityTable.activity'), value: 'activities', externalFilterSource: 'concepts/activities/activities$name' },
        { text: this.$t('ActivityTable.instance'), value: 'name' },
        { text: this.$t('_global.definition'), value: 'definition' },
        { text: this.$t('ActivityTable.topic_code'), value: 'topic_code' },
        { text: this.$t('ActivityTable.adam_code'), value: 'adam_param_code' },
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
      total: 0,
      options: {},
      filters: '',
      subgroups: [],
      currentGroup: '',
      currentSubGroup: '',
      showActivityForm: false,
      showRequestedActivityForm: false,
      showGroupsForm: false,
      showInstantiationsForm: false,
      showSponsorFromRequestedForm: false,
      activeActivity: null,
      loading: false,
      subLoading: false,
      subgroupActivities: []
    }
  },
  methods: {
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
        if (filtersObj.activity_groups) {
          params.activity_group_names = []
          filtersObj.activity_groups.v.forEach(value => {
            params.activity_group_names.push(value)
          })
          delete filtersObj.activity_groups
        }
        if (filtersObj.activity_sub_groups) {
          params.activity_sub_group_names = []
          filtersObj.activity_sub_groups.v.forEach(value => {
            params.activity_sub_group_names.push(value)
          })
          delete filtersObj.activity_sub_groups
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
        if (filtersObj.activities) {
          params.activity_names = []
          filtersObj.activities.v.forEach(value => {
            params.activity_names.push(value)
          })
          delete filtersObj.activities
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
        params.filters.status = { v: [statuses.FINAL], op: 'eq' }
      }
      if (this.options.sortBy.length !== 0 && sort !== undefined) {
        params.sort_by = `{"${this.options.sortBy[0]}":${!sort}}`
      }
      activities.get(params, this.source === 'requested-activities' ? 'activities' : this.source).then(resp => {
        this.activities = resp.data.items
        this.total = resp.data.total
      })
      activities.getSubGroups(this.currentGroup).then(resp => {
        this.subgroups = resp.data.items
      })
      activities.getSubGroupActivities(this.currentSubGroup).then(resp => {
        this.subgroupActivities = resp.data.items
      })
    },
    modifyFilters (jsonFilter, params) {
      if (jsonFilter.activity_groups) {
        params.activity_group_names = []
        jsonFilter.activity_groups.v.forEach(value => {
          params.activity_group_names.push(value)
        })
        delete jsonFilter.activity_groups
      }
      if (jsonFilter.activity_sub_groups) {
        params.activity_sub_group_names = []
        jsonFilter.activity_sub_groups.v.forEach(value => {
          params.activity_sub_group_names.push(value)
        })
        delete jsonFilter.activity_sub_groups
      }
      if (jsonFilter.name) {
        params.activity_names = []
        jsonFilter.name.v.forEach(value => {
          params.activity_names.push(value)
        })
        delete jsonFilter.name
      }
      if (jsonFilter.activities) {
        params.activity_names = []
        jsonFilter.activities.v.forEach(value => {
          params.activity_names.push(value)
        })
        delete jsonFilter.activities
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
      return this.source === 'activity-groups'
    },
    subGroupsDisplay (item) {
      let display = ''
      item.activity_sub_groups.forEach(element => {
        display += element.name + ', '
      })
      return display.slice(0, -2)
    },
    groupsDisplay (item) {
      let display = ''
      item.activity_groups.forEach(element => {
        display += element.name + ', '
      })
      return display.slice(0, -2)
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
          return this.groupsHeaders
        case 'activity-instances':
          return this.instantiationsHeaders
      }
    },
    inactivateActivity (item, source) {
      source = (source === undefined) ? this.source : source
      activities.inactivate(item.uid, source).then(() => {
        bus.$emit('notification', { msg: this.$t(`ActivitiesTable.inactivate_${this.source}_success`), type: 'success' })
        this.fetchActivities()
      })
    },
    reactivateActivity (item, source) {
      source = (source === undefined) ? this.source : source
      activities.reactivate(item.uid, source).then(() => {
        bus.$emit('notification', { msg: this.$t(`ActivitiesTable.reactivate_${this.source}_success`), type: 'success' })
        this.fetchActivities()
      })
    },
    deleteActivity (item, source) {
      source = (source === undefined) ? this.source : source
      activities.delete(item.uid, source).then(() => {
        bus.$emit('notification', { msg: this.$t(`ActivitiesTable.delete_${this.source}_success`), type: 'success' })
        this.fetchActivities()
      })
    },
    approveActivity (item, source) {
      source = (source === undefined) ? this.source : source
      activities.approve(item.uid, source).then(() => {
        bus.$emit('notification', { msg: this.$t(`ActivitiesTable.approve_${this.source}_success`), type: 'success' })
        this.fetchActivities()
      })
    },
    newActivityVersion (item, source) {
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
          this.showGroupsForm = true
          return
        case 'activity-instances':
          this.showInstantiationsForm = true
      }
    },
    editActivity (item) {
      this.activeActivity = item
      switch (this.source) {
        case 'activities':
          if (this.requested) {
            this.showRequestedActivityForm = true
          } else {
            this.showActivityForm = true
          }
          return
        case 'activity-groups':
          this.showGroupsForm = true
          return
        case 'activity-instances':
          this.showInstantiationsForm = true
      }
    },
    createSponsorFromRequested (item) {
      this.activeActivity = item
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
      this.activeActivity = null
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
<style scoped>
.tableMinWidth {
  min-width: 1440px !important;
}
</style>
