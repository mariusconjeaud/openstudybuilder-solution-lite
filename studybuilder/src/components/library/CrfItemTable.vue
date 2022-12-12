<template>
<div>
  <n-n-table
    :headers="headers"
    :items="items"
    item-key="uid"
    sort-desc
    has-api
    column-data-resource="concepts/odms/items"
    export-data-url="concepts/odms/items"
    export-object-label="CRFItems"
    :options.sync="options"
    :server-items-length="total"
    @filter="getItems"
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
      <n-n-parameter-highlighter :name="item.name" :show-prefix-and-postfix="false" />
    </template>
    <template v-slot:item.description="{ item }">
      <div v-html="getDescription(item)" />
    </template>
    <template v-slot:item.notes="{ item }">
      <div v-html="getNotes(item)" />
    </template>
    <template v-slot:item.activities="{ item }">
      {{ item.activities | names }}
    </template>
    <template v-slot:item.status="{ item }">
      <status-chip :status="item.status" />
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
    <template v-slot:item.relations="{ item }">
      <v-btn
        fab
        dark
        small
        color="primary"
        icon
        @click="openRelationsTree(item)"
        >
        <v-icon dark>
          mdi-family-tree
        </v-icon>
      </v-btn>
    </template>
  </n-n-table>
  <v-dialog
    v-model="showForm"
    persistent
    content-class="fullscreen-dialog"
    >
    <crf-item-form
      @close="closeForm"
      :editItem="editItem"
      class="fullscreen-dialog"
      :readOnlyProp="editItem.status === 'Final'"
      />
  </v-dialog>
  <v-dialog
    v-model="showItemHistory"
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
import CrfItemForm from '@/components/library/CrfItemForm'
import HistoryTable from '@/components/tools/HistoryTable'
import CrfActivitiesModelsLinkForm from '@/components/library/CrfActivitiesModelsLinkForm'
import constants from '@/constants/statuses'
import filteringParameters from '@/utils/filteringParameters'
import OdmReferencesTree from '@/components/library/OdmReferencesTree.vue'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import crfTypes from '@/constants/crfTypes'
import parameters from '@/constants/parameters'
import dataFormating from '@/utils/dataFormating'

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
          condition: (item) => item.status === constants.FINAL,
          click: this.openLinkForm
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openItemHistory
        }
      ],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('CRFItems.oid'), value: 'oid' },
        { text: this.$t('_global.relations'), value: 'relations' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('_global.description'), value: 'description' },
        { text: this.$t('CRFItems.impl_notes'), value: 'notes' },
        { text: this.$t('CRFItems.type'), value: 'datatype' },
        { text: this.$t('CRFItems.length'), value: 'length' },
        { text: this.$t('CRFItems.sds_name'), value: 'sdsVarName' },
        { text: this.$t('_global.links'), value: 'activities' },
        { text: this.$t('_global.version'), value: 'version' },
        { text: this.$t('_global.status'), value: 'status' }
      ],
      showForm: false,
      options: {},
      filters: '',
      total: 0,
      items: [],
      selectedItem: null,
      showItemHistory: false,
      editItem: {},
      linkForm: false,
      showRelations: false,
      itemHistoryItems: []
    }
  },
  mounted () {
    if (this.elementProp.tab === 'items' && this.elementProp.type === crfTypes.ITEM && this.elementProp.uid) {
      this.edit(this.elementProp)
    }
  },
  methods: {
    getDescription (item) {
      const engDesc = item.descriptions.find(el => el.language === parameters.ENG)
      if (engDesc) {
        return engDesc.description
      }
      return ''
    },
    getNotes (item) {
      const engDesc = item.descriptions.find(el => el.language === parameters.ENG)
      if (engDesc) {
        return engDesc.sponsor_instruction
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
      this.showForm = false
      this.editItem = {}
      this.getItems()
    },
    approve (item) {
      crfs.approve('items', item.uid).then((resp) => {
        this.getItems()
      })
    },
    async delete (item) {
      let relationships = 0
      await crfs.getItemRelationship(item.uid).then(resp => {
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
        this.getItems()
      })
    },
    reactivate (item) {
      crfs.reactivate('items', item.uid).then((resp) => {
        this.getItems()
      })
    },
    newVersion (item) {
      crfs.newVersion('items', item.uid).then((resp) => {
        this.getItems()
      })
    },
    edit (item) {
      crfs.getItem(item.uid).then((resp) => {
        this.editItem = resp.data
        this.showForm = true
        this.$emit('clearUid')
      })
    },
    view (item) {
      crfs.getItem(item.uid).then((resp) => {
        this.editItem = resp.data
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
      this.selectedItem = {}
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
      this.selectedItem = {}
      this.getItems()
    },
    getItems (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      crfs.get('items', { params }).then((resp) => {
        this.items = resp.data.items
        this.total = resp.data.total
      })
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
