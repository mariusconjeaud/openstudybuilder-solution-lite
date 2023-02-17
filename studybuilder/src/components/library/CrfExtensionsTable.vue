<template>
<div>
  <n-n-table
    :headers="headers"
    :items="namespaces"
    item-key="uid"
    sort-by="name"
    sort-desc
    :options.sync="options"
    :server-items-length="total"
    @filter="getNamespaces"
    has-api
    column-data-resource="concepts/odms/namespaces"
    export-data-url="concepts/odms/namespaces"
    export-object-label="CRFNamespaces">
    <template v-slot:actions="">
      <v-btn
        class="ml-2"
        fab
        dark
        small
        color="primary"
        @click.stop="openCreateForm"
        :title="$t('CrfExtensions.new_namespace')"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
    <template v-slot:item.status="{ item }">
      <status-chip :status="item.status" />
    </template>
  </n-n-table>
  <crf-extensions-create-form
    :editItem="editItem"
    :open="showCreateForm"
    @close="closeCreateForm"
    />
  <crf-extensions-edit-form
    :editItem="editItem"
    :open="showEditForm"
    @close="closeEditForm"
    fullscreen-form
    />
</div>
</template>

<script>
import NNTable from '@/components/tools/NNTable'
import crfs from '@/api/crfs'
import filteringParameters from '@/utils/filteringParameters'
import ActionsMenu from '@/components/tools/ActionsMenu'
import StatusChip from '@/components/tools/StatusChip'
import CrfExtensionsCreateForm from '@/components/library/CrfExtensionsCreateForm'
import CrfExtensionsEditForm from '@/components/library/CrfExtensionsEditForm'
import actions from '@/constants/actions'

export default {
  components: {
    NNTable,
    ActionsMenu,
    StatusChip,
    CrfExtensionsCreateForm,
    CrfExtensionsEditForm
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('CrfExtensions.edit_extension'),
          icon: 'mdi-pencil',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === actions.EDIT),
          click: this.openEditForm
        },
        {
          label: this.$t('CrfExtensions.edit_namespace'),
          icon: 'mdi-pencil',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === actions.EDIT),
          click: this.openCreateForm
        },
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: (item) => item.possible_actions.find(action => action === actions.APPROVE),
          click: this.approve
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === actions.NEW_VERSION),
          click: this.newVersion
        },
        {
          label: this.$t('_global.inactivate'),
          icon: 'mdi-close-octagon-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === actions.INACTIVATE),
          click: this.inactivate
        },
        {
          label: this.$t('_global.reactivate'),
          icon: 'mdi-undo-variant',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === actions.REACTIVATE),
          click: this.reactivate
        }
      ],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('CrfExtensions.prefix'), value: 'prefix' },
        { text: this.$t('CrfExtensions.url'), value: 'url' },
        { text: this.$t('_global.status'), value: 'status' }
      ],
      options: {},
      filters: '',
      total: 0,
      namespaces: [],
      showCreateForm: false,
      showEditForm: false,
      editItem: {}
    }
  },
  methods: {
    getNamespaces (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      crfs.getAllNamespaces(params).then((resp) => {
        this.namespaces = resp.data.items
        this.total = resp.data.total
      })
    },
    approve (item) {
      crfs.approve('vendor-namespaces', item.uid).then(() => {
        this.getNamespaces()
      })
    },
    inactivate (item) {
      crfs.inactivate('vendor-namespaces', item.uid).then(() => {
        this.getNamespaces()
      })
    },
    reactivate (item) {
      crfs.reactivate('vendor-namespaces', item.uid).then(() => {
        this.getNamespaces()
      })
    },
    newVersion (item) {
      crfs.newVersion('vendor-namespaces', item.uid).then(() => {
        this.getNamespaces()
      })
    },
    openCreateForm (item) {
      this.editItem = item.uid ? item : {}
      this.showCreateForm = true
    },
    closeCreateForm () {
      this.editItem = {}
      this.showCreateForm = false
      this.getNamespaces()
    },
    openEditForm (item) {
      this.editItem = item
      this.showEditForm = true
    },
    closeEditForm () {
      this.editItem = {}
      this.showEditForm = false
      this.getNamespaces()
    }
  },
  watch: {
    options: {
      handler () {
        this.getNamespaces()
      },
      deep: true
    }
  }
}
</script>
