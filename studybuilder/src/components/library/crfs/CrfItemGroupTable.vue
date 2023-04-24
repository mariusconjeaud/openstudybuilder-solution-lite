<template>
<div>
  <n-n-table
    :headers="headers"
    :items="itemGroups"
    item-key="uid"
    sort-by="name"
    sort-desc
    has-api
    :options.sync="options"
    :server-items-length="total"
    @filter="getItemGroups"
    column-data-resource="concepts/odms/item-groups"
    export-data-url="concepts/odms/item-groups"
    export-object-label="CRFItemGroups"
    >
    <template v-slot:actions="">
      <v-btn
        class="ml-2"
        fab
        dark
        small
        color="primary"
        @click.stop="openForm"
        :title="$t('CRFItemGroups.add_group')"
        data-cy="add-crf-item-group"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:item.name="{ item }">
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <div v-bind="attrs" v-on="on">{{ item.name.length > 40 ? item.name.substring(0, 40) + '...' : item.name }}</div>
        </template>
        <span>{{ item.name }}</span>
      </v-tooltip>
    </template>
    <template v-slot:item.repeating="{ item }">
      {{ item.repeating }}
    </template>
    <template v-slot:item.activity_subgroups="{ item }">
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <div v-bind="attrs" v-on="on">
            {{ item.activity_subgroups[0] ? (item.activity_subgroups.length > 1 ? item.activity_subgroups[0].name + '...' : item.activity_subgroups[0].name) : '' }}
          </div>
        </template>
        <span>{{ item.activity_subgroups | names }}</span>
      </v-tooltip>
    </template>
    <template v-slot:item.description="{ item }">
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <div v-html="getDescription(item, true)" v-bind="attrs" v-on="on"/>
        </template>
        <span>{{getDescription(item, false)}}</span>
      </v-tooltip>
    </template>
    <template v-slot:item.notes="{ item }">
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <div v-html="getNotes(item, true)" v-bind="attrs" v-on="on"/>
        </template>
      <span>{{getNotes(item, false)}}</span>
      </v-tooltip>
    </template>
    <template v-slot:item.status="{ item }">
      <status-chip :status="item.status" />
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
  </n-n-table>
  <v-dialog
    v-model="showForm"
    persistent
    content-class="fullscreen-dialog"
    >
    <crf-item-group-form
      @close="closeForm"
      @newVersion="newVersion"
      @approve="approve"
      :selectedGroup="selectedGroup"
      class="fullscreen-dialog"
      :readOnlyProp="selectedGroup && selectedGroup.status === constants.FINAL"
      />
  </v-dialog>
  <v-dialog
    v-model="showGroupHistory"
    @keydown.esc="closeGroupHistory"
    persistent
    max-width="1200px"
    >
    <history-table
      :title="groupHistoryTitle"
      @close="closeGroupHistory"
      :headers="headers"
      :items="groupHistoryItems"
      />
  </v-dialog>
  <crf-activities-models-link-form
    :open="linkForm"
    @close="closeLinkForm"
    :item-to-link="selectedGroup"
    item-type="itemGroup" />
  <v-dialog v-model="showRelations"
            @keydown.esc="closeRelationsTree()"
            max-width="800px"
            persistent>
    <odm-references-tree
      :item="selectedGroup"
      type="group"
      @close="closeRelationsTree()"/>
  </v-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import NNTable from '@/components/tools/NNTable'
import StatusChip from '@/components/tools/StatusChip'
import ActionsMenu from '@/components/tools/ActionsMenu'
import crfs from '@/api/crfs'
import CrfItemGroupForm from '@/components/library/crfs/CrfItemGroupForm'
import HistoryTable from '@/components/tools/HistoryTable'
import CrfActivitiesModelsLinkForm from '@/components/library/crfs/CrfActivitiesModelsLinkForm'
import constants from '@/constants/statuses'
import filteringParameters from '@/utils/filteringParameters'
import OdmReferencesTree from '@/components/library/crfs/OdmReferencesTree'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import crfTypes from '@/constants/crfTypes'
import parameters from '@/constants/parameters'
import { mapGetters } from 'vuex'
import _isEmpty from 'lodash/isEmpty'

export default {
  components: {
    NNTable,
    StatusChip,
    ActionsMenu,
    CrfItemGroupForm,
    HistoryTable,
    CrfActivitiesModelsLinkForm,
    OdmReferencesTree,
    ConfirmDialog
  },
  props: {
    elementProp: Object
  },
  computed: {
    ...mapGetters({
      itemGroups: 'crfs/itemGroups',
      total: 'crfs/totalItemGroups'
    }),
    groupHistoryTitle () {
      if (this.selectedGroup) {
        return this.$t(
          'CRFItemGroups.group_history_title',
          { groupUid: this.selectedGroup.uid })
      }
      return ''
    }
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: (item) => item.possible_actions.find(action => action === 'approve'),
          click: this.approve
        },
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'edit'),
          click: this.edit
        },
        {
          label: this.$t('_global.view'),
          icon: 'mdi-eye-outline',
          iconColor: 'primary',
          condition: (item) => item.status === constants.FINAL,
          click: this.view
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'new_version'),
          click: this.newVersion
        },
        {
          label: this.$t('_global.inactivate'),
          icon: 'mdi-close-octagon-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'inactivate'),
          click: this.inactivate
        },
        {
          label: this.$t('_global.reactivate'),
          icon: 'mdi-undo-variant',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'reactivate'),
          click: this.reactivate
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete',
          iconColor: 'error',
          condition: (item) => item.possible_actions.find(action => action === 'delete'),
          click: this.delete
        },
        {
          label: this.$t('CrfLinikingForm.link_activity_sub_groups'),
          icon: 'mdi-plus',
          iconColor: 'primary',
          condition: (item) => item.status === constants.DRAFT,
          click: this.openLinkForm
        },
        {
          label: this.$t('_global.relations'),
          icon: 'mdi-family-tree',
          click: this.openRelationsTree
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openGroupHistory
        }
      ],
      headers: [
        { text: '', value: 'actions', width: '1%' },
        { text: this.$t('CRFItemGroups.oid'), value: 'oid' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('_global.description'), value: 'description' },
        { text: this.$t('CRFItems.impl_notes'), value: 'notes' },
        { text: this.$t('CRFItemGroups.repeating'), value: 'repeating', width: '1%' },
        { text: this.$t('_global.links'), value: 'activity_subgroups' },
        { text: this.$t('_global.version'), value: 'version', width: '1%' },
        { text: this.$t('_global.status'), value: 'status', width: '1%' }
      ],
      showForm: false,
      showHistory: false,
      selectedGroup: null,
      options: {},
      filters: '',
      showGroupHistory: false,
      linkForm: false,
      showRelations: false,
      groupHistoryItems: []
    }
  },
  mounted () {
    this.getItemGroups()
    if (this.elementProp.tab === 'item-groups' && this.elementProp.type === crfTypes.ITEM_GROUP && this.elementProp.uid) {
      this.edit({ uid: this.elementProp.uid })
    }
  },
  created () {
    this.constants = constants
  },
  methods: {
    getDescription (item, short) {
      const engDesc = item.descriptions.find(el => el.language === parameters.ENG)
      if (engDesc) {
        return short ? (engDesc.description.length > 40 ? engDesc.description.substring(0, 40) + '...' : engDesc.description) : engDesc.description
      }
      return ''
    },
    getNotes (item, short) {
      const engDesc = item.descriptions.find(el => el.language === parameters.ENG)
      if (engDesc) {
        return short ? (engDesc.sponsor_instruction.length > 40 ? engDesc.sponsor_instruction.substring(0, 40) + '...' : engDesc.sponsor_instruction) : engDesc.sponsor_instruction
      }
      return ''
    },
    openRelationsTree (item) {
      this.showRelations = true
      this.selectedGroup = item
    },
    closeRelationsTree () {
      this.selectedGroup = null
      this.showRelations = false
    },
    async delete (item) {
      let relationships = 0
      await crfs.getRelationships(item.uid, 'item-groups').then(resp => {
        if (resp.data.OdmForm && resp.data.OdmForm.length > 0) {
          relationships = resp.data.OdmForm.length
        }
      })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (relationships > 0 && await this.$refs.confirm.open(`${this.$t('CRFItemGroups.delete_warning_1')} ${relationships} ${this.$t('CRFItemGroups.delete_warning_2')}`, options)) {
        crfs.delete('item-groups', item.uid).then((resp) => {
          this.getItemGroups()
        })
      } else if (relationships === 0) {
        crfs.delete('item-groups', item.uid).then((resp) => {
          this.getItemGroups()
        })
      }
    },
    approve (item) {
      crfs.approve('item-groups', item.uid).then((resp) => {
        this.$emit('updateItemGroup', { type: crfTypes.GROUP, element: resp.data })
        this.getItemGroups()
      })
    },
    inactivate (item) {
      crfs.inactivate('item-groups', item.uid).then((resp) => {
        this.$emit('updateItemGroup', { type: crfTypes.GROUP, element: resp.data })
        this.getItemGroups()
      })
    },
    reactivate (item) {
      crfs.reactivate('item-groups', item.uid).then((resp) => {
        this.$emit('updateItemGroup', { type: crfTypes.GROUP, element: resp.data })
        this.getItemGroups()
      })
    },
    async newVersion (item) {
      let relationships = 0
      await crfs.getRelationships(item.uid, 'item-groups').then(resp => {
        if (resp.data.OdmForm && resp.data.OdmForm.length > 0) {
          relationships = resp.data.OdmForm.length
        }
      })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (relationships > 1 && await this.$refs.confirm.open(`${this.$t('CRFForms.new_version_warning')}`, options)) {
        crfs.newVersion('item-groups', item.uid).then((resp) => {
          this.$emit('updateItemGroup', { type: crfTypes.GROUP, element: resp.data })
          this.getItemGroups()
        })
      } else if (relationships <= 1) {
        crfs.newVersion('item-groups', item.uid).then((resp) => {
          this.$emit('updateItemGroup', { type: crfTypes.GROUP, element: resp.data })
          this.getItemGroups()
        })
      }
    },
    edit (item) {
      crfs.getItemGroup(item.uid).then((resp) => {
        this.selectedGroup = resp.data
        this.showForm = true
        this.$emit('clearUid')
      })
    },
    view (item) {
      crfs.getItemGroup(item.uid).then((resp) => {
        this.selectedGroup = resp.data
        this.showForm = true
      })
    },
    openForm () {
      this.showForm = true
    },
    async openGroupHistory (group) {
      this.selectedGroup = group
      const resp = await crfs.getGroupAuditTrail(group.uid)
      this.groupHistoryItems = resp.data
      this.showGroupHistory = true
    },
    closeGroupHistory () {
      this.selectedGroup = null
      this.showGroupHistory = false
    },
    async closeForm () {
      if (!_isEmpty(this.selectedGroup)) {
        await crfs.getItemGroup(this.selectedGroup.uid).then((resp) => {
          this.$emit('updateItemGroup', { type: crfTypes.GROUP, element: resp.data })
        })
      }
      this.showForm = false
      this.selectedGroup = null
      this.getItemGroups()
    },
    openLinkForm (item) {
      this.selectedGroup = item
      this.linkForm = true
    },
    closeLinkForm () {
      this.linkForm = false
      this.selectedGroup = null
      this.getItemGroups()
    },
    getItemGroups (filters, sort, filtersUpdated) {
      if (filters) {
        this.filters = filters
      }
      const params = filteringParameters.prepareParameters(
        this.options, this.filters, sort, filtersUpdated)
      this.$store.dispatch('crfs/fetchItemGroups', params)
    }
  },
  watch: {
    options: {
      handler () {
        this.getItemGroups()
      },
      deep: true
    },
    elementProp (value) {
      if (value.tab === 'item-groups' && value.type === crfTypes.ITEM_GROUP && value.uid) {
        this.edit({ uid: value.uid })
      }
    }
  }
}
</script>
