<template>
<div>
  <n-n-table
    :headers="headers"
    :items="items"
    item-key="uid"
    sort-by="name"
    sort-desc
    has-api
    :options.sync="options"
    :server-items-length="total"
    @filter="getItems"
    column-data-resource="concepts/odms/items"
    export-data-url="concepts/odms/items"
    export-object-label="CRFItems"
    >
    <template v-slot:actions="">
      <v-btn
        class="ml-2"
        fab
        dark
        small
        color="primary"
        @click.stop="showForm = true"
        :title="$t('CRFItems.add_title')"
        data-cy="add-crf-item"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:item.name="{ item }">
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <div
            v-bind="attrs"
            v-on="on">
            <n-n-parameter-highlighter :name="item.name.length > 40 ? item.name.substring(0, 40) + '...' : item.name" :show-prefix-and-postfix="false"/></div>
        </template>
        <span>{{item.name}}</span>
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
    <template v-slot:item.activities="{ item }">
      <v-tooltip bottom v-if="item.activity">
        <template v-slot:activator="{ on, attrs }">
          <div v-bind="attrs" v-on="on">
            {{ item.activity.name.length > 40 ? item.activity.name.substring(0, 40) + '...' : item.activity.name }}
          </div>
        </template>
        <span>{{ item.activity.name }}</span>
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
    <crf-item-form
      @close="closeForm"
      @newVersion="newVersion"
      @approve="approve"
      :selectedItem="selectedItem"
      class="fullscreen-dialog"
      :readOnlyProp="selectedItem && selectedItem.status === constants.FINAL"
      />
  </v-dialog>
  <v-dialog
    v-model="showItemHistory"
    @keydown.esc="closeItemHistory"
    persistent
    max-width="1200px"
    >
    <history-table
      :title="itemHistoryTitle"
      @close="closeItemHistory"
      :headers="headers"
      :items="itemHistoryItems"
      />
  </v-dialog>
  <crf-activities-models-link-form
    :open="linkForm"
    @close="closeLinkForm"
    :item-to-link="selectedItem"
    item-type="item" />
  <v-dialog v-model="showRelations"
            @keydown.esc="closeRelationsTree()"
            max-width="800px"
            persistent>
    <odm-references-tree
      :item="selectedItem"
      type="item"
      @close="closeRelationsTree()"/>
  </v-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import NNTable from '@/components/tools/NNTable'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import StatusChip from '@/components/tools/StatusChip'
import ActionsMenu from '@/components/tools/ActionsMenu'
import crfs from '@/api/crfs'
import CrfItemForm from '@/components/library/crfs/CrfItemForm'
import HistoryTable from '@/components/tools/HistoryTable'
import CrfActivitiesModelsLinkForm from '@/components/library/crfs/CrfActivitiesModelsLinkForm'
import constants from '@/constants/statuses'
import filteringParameters from '@/utils/filteringParameters'
import OdmReferencesTree from '@/components/library/crfs/OdmReferencesTree'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import crfTypes from '@/constants/crfTypes'
import parameters from '@/constants/parameters'
import dataFormating from '@/utils/dataFormating'
import { mapGetters } from 'vuex'
import _isEmpty from 'lodash/isEmpty'

export default {
  components: {
    NNTable,
    NNParameterHighlighter,
    StatusChip,
    ActionsMenu,
    CrfItemForm,
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
      items: 'crfs/items',
      total: 'crfs/totalItems'
    }),
    itemHistoryTitle () {
      if (this.selectedItem) {
        return this.$t(
          'CRFItems.item_history_title',
          { itemUid: this.selectedItem.uid })
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
          label: this.$t('CrfLinikingForm.link_activities'),
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
          click: this.openItemHistory
        }
      ],
      headers: [
        { text: '', value: 'actions', width: '1%' },
        { text: this.$t('CRFItems.oid'), value: 'oid' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('_global.description'), value: 'description' },
        { text: this.$t('CRFItems.impl_notes'), value: 'notes' },
        { text: this.$t('CRFItems.type'), value: 'datatype', width: '1%' },
        { text: this.$t('CRFItems.length'), value: 'length', width: '1%' },
        { text: this.$t('CRFItems.sds_name'), value: 'sdsVarName' },
        { text: this.$t('_global.links'), value: 'activities' },
        { text: this.$t('_global.version'), value: 'version', width: '1%' },
        { text: this.$t('_global.status'), value: 'status', width: '1%' }
      ],
      showForm: false,
      options: {},
      filters: '',
      selectedItem: null,
      showItemHistory: false,
      linkForm: false,
      showRelations: false,
      itemHistoryItems: []
    }
  },
  mounted () {
    this.getItems()
    if (this.elementProp.tab === 'items' && this.elementProp.type === crfTypes.ITEM && this.elementProp.uid) {
      this.edit(this.elementProp)
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
      this.selectedItem = item
    },
    closeRelationsTree () {
      this.selectedItem = null
      this.showRelations = false
    },
    openForm () {
      this.showForm = true
    },
    closeForm () {
      if (!_isEmpty(this.selectedItem)) {
        crfs.getItem(this.selectedItem.uid).then((resp) => {
          this.$emit('updateItem', { type: crfTypes.ITEM, element: resp.data })
        })
      }
      this.showForm = false
      this.selectedItem = null
      this.getItems()
    },
    approve (item) {
      crfs.approve('items', item.uid).then((resp) => {
        this.$emit('updateItem', { type: crfTypes.ITEM, element: resp.data })
        this.getItems()
      })
    },
    async delete (item) {
      let relationships = 0
      await crfs.getRelationships(item.uid, 'items').then(resp => {
        if (resp.data.OdmItemGroup && resp.data.OdmItemGroup.length > 0) {
          relationships = resp.data.OdmItemGroup.length
        }
      })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (relationships > 0 && await this.$refs.confirm.open(`${this.$t('CRFItems.delete_warning_1')} ${relationships} ${this.$t('CRFItems.delete_warning_2')}`, options)) {
        crfs.delete('items', item.uid).then((resp) => {
          this.getItems()
        })
      } else if (relationships === 0) {
        crfs.delete('items', item.uid).then((resp) => {
          this.getItems()
        })
      }
    },
    inactivate (item) {
      crfs.inactivate('items', item.uid).then((resp) => {
        this.$emit('updateItem', { type: crfTypes.ITEM, element: resp.data })
        this.getItems()
      })
    },
    reactivate (item) {
      crfs.reactivate('items', item.uid).then((resp) => {
        this.$emit('updateItem', { type: crfTypes.ITEM, element: resp.data })
        this.getItems()
      })
    },
    async newVersion (item) {
      let relationships = 0
      await crfs.getRelationships(item.uid, 'items').then(resp => {
        if (resp.data.OdmItemGroup && resp.data.OdmItemGroup.length > 0) {
          relationships = resp.data.OdmItemGroup.length
        }
      })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (relationships > 1 && await this.$refs.confirm.open(`${this.$t('CRFForms.new_version_warning')}`, options)) {
        crfs.newVersion('items', item.uid).then((resp) => {
          this.$emit('updateItem', { type: crfTypes.ITEM, element: resp.data })
          this.getItems()
        })
      } else if (relationships <= 1) {
        crfs.newVersion('items', item.uid).then((resp) => {
          this.$emit('updateItem', { type: crfTypes.ITEM, element: resp.data })
          this.getItems()
        })
      }
    },
    edit (item) {
      crfs.getItem(item.uid).then((resp) => {
        this.selectedItem = resp.data
        this.showForm = true
        this.$emit('clearUid')
      })
    },
    view (item) {
      crfs.getItem(item.uid).then((resp) => {
        this.selectedItem = resp.data
        this.showForm = true
      })
    },
    async openItemHistory (item) {
      this.selectedItem = item
      const resp = await crfs.getItemAuditTrail(item.uid)
      this.itemHistoryItems = this.transformItems(resp.data)
      this.showItemHistory = true
    },
    closeItemHistory () {
      this.selectedItem = null
      this.showItemHistory = false
    },
    transformItems (items) {
      const result = []
      for (const item of items) {
        const newItem = { ...item }
        if (newItem.activities) {
          newItem.activities = dataFormating.names(newItem.activities)
        } else {
          newItem.activities = ''
        }
        result.push(newItem)
      }
      return result
    },
    openLinkForm (item) {
      this.selectedItem = item
      this.linkForm = true
    },
    closeLinkForm () {
      this.linkForm = false
      this.selectedItem = null
      this.getItems()
    },
    getItems (filters, sort, filtersUpdated) {
      if (filters) {
        this.filters = filters
      }
      const params = filteringParameters.prepareParameters(
        this.options, this.filters, sort, filtersUpdated)
      this.$store.dispatch('crfs/fetchItems', params)
    }
  },
  watch: {
    options: {
      handler () {
        this.getItems()
      },
      deep: true
    },
    elementProp (value) {
      if (value.tab === 'items' && value.type === crfTypes.ITEM && value.uid) {
        this.edit(value)
      }
    }
  }
}
</script>
