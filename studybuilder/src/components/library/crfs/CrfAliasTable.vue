<template>
<div>
  <n-n-table
    :headers="headers"
    :items="aliases"
    item-key="uid"
    sort-by="name"
    sort-desc
    :options.sync="options"
    :server-items-length="total"
    @filter="getAliases"
    has-api
    column-data-resource="concepts/odms/aliases"
    export-data-url="concepts/odms/aliases"
    export-object-label="CRFAliases"
    >
    <template v-slot:actions="">
      <v-btn
        class="ml-2"
        fab
        small
        color="primary"
        @click.stop="openForm"
        :title="$t('CrfAliases.add_alias')"
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
  </n-n-table>
  <crf-alias-form
    :open="showForm"
    @close="closeForm"
    :editedItem="editItem"
    />
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import NNTable from '@/components/tools/NNTable'
import ActionsMenu from '@/components/tools/ActionsMenu'
import crfs from '@/api/crfs'
import CrfAliasForm from '@/components/library/crfs/CrfAliasForm'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import { bus } from '@/main'
import filteringParameters from '@/utils/filteringParameters'
import { accessGuard } from '@/mixins/accessRoleVerifier'

export default {
  mixins: [accessGuard],
  components: {
    NNTable,
    CrfAliasForm,
    ActionsMenu,
    ConfirmDialog
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'edit'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.edit
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
        { text: '', value: 'actions' },
        { text: this.$t('CrfAliases.context'), value: 'context' },
        { text: this.$t('_global.name'), value: 'name' }
      ],
      showForm: false,
      options: {},
      filters: '',
      total: 0,
      aliases: [],
      editItem: {}
    }
  },
  methods: {
    async delete (item) {
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (await this.$refs.confirm.open(this.$t('CrfAliases.delete_approve'), options)) {
        crfs.deleteAlias(item.uid).then(() => {
          bus.$emit('notification', { msg: this.$t('CrfAliases.alias_deleted') })
          this.getAliases()
        })
      }
    },
    edit (item) {
      this.editItem = item
      this.showForm = true
    },
    openForm () {
      this.showForm = true
    },
    closeForm () {
      this.showForm = false
      this.editItem = {}
      this.getAliases()
    },
    getAliases (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      crfs.getAllAliases(params).then((resp) => {
        this.aliases = resp.data.items
        this.total = resp.data.total
      })
    }
  },
  watch: {
    options: {
      handler () {
        this.getAliases()
      },
      deep: true
    }
  }
}
</script>
