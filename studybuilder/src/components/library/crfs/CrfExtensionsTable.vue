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
        small
        color="primary"
        @click.stop="openCreateForm"
        :title="$t('CrfExtensions.new_namespace')"
        :disabled="!checkPermission($roles.LIBRARY_WRITE)"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item"/>
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
import CrfExtensionsCreateForm from '@/components/library/crfs/CrfExtensionsCreateForm'
import CrfExtensionsEditForm from '@/components/library/crfs/CrfExtensionsEditForm'
import actions from '@/constants/actions'
import { accessGuard } from '@/mixins/accessRoleVerifier'

export default {
  mixins: [accessGuard],
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
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === actions.EDIT),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.openEditForm
        },
        {
          label: this.$t('CrfExtensions.edit_namespace'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === actions.EDIT),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.openCreateForm
        },
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: (item) => item.possible_actions.find(action => action === actions.APPROVE),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.approve
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === actions.NEW_VERSION),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.newVersion
        },
        {
          label: this.$t('_global.inactivate'),
          icon: 'mdi-close-octagon-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === actions.INACTIVATE),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.inactivate
        },
        {
          label: this.$t('_global.reactivate'),
          icon: 'mdi-undo-variant',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === actions.REACTIVATE),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.reactivate
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          condition: (item) => item.possible_actions.find(action => action === 'delete'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.delete
        }
      ],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('CrfExtensions.prefix'), value: 'prefix' },
        { text: this.$t('CrfExtensions.url'), value: 'url' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
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
    delete (item) {
      crfs.delete('vendor-namespaces', item.uid).then(() => {
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
