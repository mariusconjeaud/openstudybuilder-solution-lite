<template>
<div>
  <v-tabs v-model="tab">
    <v-tab href="#html">{{ $t('_global.overview') }}</v-tab>
    <v-tab href="#yaml">{{ $t('ActivityOverview.osb_yaml') }}</v-tab>
    <v-tab v-if="cosmosVersion" href="#cosmos">{{ $t('ActivityOverview.cosmos_yaml') }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="html">
      <v-card elevation="0" class="rounded-0">
        <v-card-title>
          <v-spacer />
          <template
            v-for="(action, pos) in actions"
            >
            <v-btn
              :key="pos"
              v-if="action.condition && (!action.accessRole || checkPermission(action.accessRole))"
              fab
              small
              @click="action.click"
              :title="action.label"
              class="ml-2"
              :color="action.iconColor"
              >
              <v-icon>{{ action.icon }}</v-icon>
            </v-btn>
          </template>
        </v-card-title>
        <v-card-text>
          <slot
            name="htmlContent"
            v-bind:itemOverview="itemOverview"
            v-bind:item="item"
            >
          </slot>
        </v-card-text>
      </v-card>
    </v-tab-item>
    <v-tab-item id="yaml">
      <v-card elevation="0" class="rounded-0">
        <v-card-title>
          <v-spacer />
          <v-btn
            fab
            small
            color="nnGreen1"
            class="white--text"
            :title="$t('YamlViewer.download')"
            @click="downloadYamlContent"
            >
            <v-icon>mdi-download-outline</v-icon>
          </v-btn>
          <v-btn
            fab
            small
            :title="$t('YamlViewer.close_tab')"
            @click="closeYamlTab"
            class="ml-2"
            >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <yaml-viewer :content="yamlVersion" />
        </v-card-text>
      </v-card>
    </v-tab-item>
    <v-tab-item v-if="cosmosVersion" id="cosmos">
      <v-card elevation="0" class="rounded-0">
        <v-card-title>
          <v-spacer />
          <v-btn
            fab
            small
            color="nnGreen1"
            class="white--text"
            :title="$t('YamlViewer.download')"
            @click="downloadCosmosContent"
            >
            <v-icon>mdi-download-outline</v-icon>
          </v-btn>
          <v-btn
            fab
            small
            :title="$t('YamlViewer.close_tab')"
            @click="closeYamlTab"
            class="ml-2"
            >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <yaml-viewer :content="cosmosVersion" />
        </v-card-text>
      </v-card>
    </v-tab-item>
  </v-tabs-items>
  <slot
    name="itemForm"
    v-bind:show="showForm"
    v-bind:item="item"
    v-bind:close="closeForm"
    >
  </slot>
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
      :headers="historyHeaders"
      :items="historyItems"
      />
  </v-dialog>
</div>
</template>

<script>
import { accessGuard } from '@/mixins/accessRoleVerifier'
import activities from '@/api/activities'
import { bus } from '@/main'
import exportLoader from '@/utils/exportLoader'
import HistoryTable from '@/components/tools/HistoryTable'
import YamlViewer from '@/components/tools/YamlViewer'

export default {
  mixins: [accessGuard],
  components: {
    HistoryTable,
    YamlViewer
  },
  props: {
    itemUid: String,
    source: String,
    itemOverview: Object,
    yamlVersion: String,
    transformFunc: Function,
    historyHeaders: Array,
    cosmosVersion: {
      type: String,
      required: false
    }
  },
  computed: {
    actions () {
      return [
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: this.item && this.item.possible_actions.find(action => action === 'approve'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.approveItem
        },
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          condition: this.item && this.item.possible_actions.find(action => action === 'edit'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.editItem
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: this.item && this.item.possible_actions.find(action => action === 'new_version'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.newItemVersion
        },
        {
          label: this.$t('_global.inactivate'),
          icon: 'mdi-close-octagon-outline',
          iconColor: 'primary',
          condition: this.item && this.item.possible_actions.find(action => action === 'inactivate'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.inactivateItem
        },
        {
          label: this.$t('_global.reactivate'),
          icon: 'mdi-undo-variant',
          iconColor: 'primary',
          condition: this.item && this.item.possible_actions.find(action => action === 'reactivate'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.reactivateItem
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          condition: this.item && this.item.possible_actions.find(action => action === 'delete'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.deleteItem
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          condition: true,
          accessRole: this.$roles.LIBRARY_READ,
          click: this.openHistory
        },
        {
          label: this.$t('_global.close'),
          icon: 'mdi-close',
          condition: true,
          accessRole: this.$roles.LIBRARY_READ,
          click: this.closePage
        }
      ]
    },
    historyTitle () {
      return this.source === 'activities' ? this.$t('ActivityOverview.history_title', { uid: this.itemUid }) : this.$t('ActivityInstanceOverview.history_title', { uid: this.itemUid })
    }
  },
  data () {
    return {
      item: null,
      historyItems: [],
      showForm: false,
      showHistory: false,
      tab: null
    }
  },
  methods: {
    closeForm () {
      this.showForm = false
      this.fetchItem()
    },
    closePage () {
      this.$emit('closePage')
    },
    closeYamlTab () {
      this.tab = 'html'
    },
    fetchItem () {
      activities.getObject(this.source, this.itemUid).then(resp => {
        this.item = resp.data
        this.transformFunc(this.item)
        this.$emit('refresh')
      })
    },
    editItem () {
      this.showForm = true
    },
    inactivateItem () {
      activities.inactivate(this.itemUid, this.source).then(() => {
        bus.$emit('notification', { msg: this.$t(`ActivitiesTable.inactivate_${this.source}_success`), type: 'success' })
        this.fetchItem()
      })
    },
    reactivateItem () {
      activities.reactivate(this.itemUid, this.source).then(() => {
        bus.$emit('notification', { msg: this.$t(`ActivitiesTable.reactivate_${this.source}_success`), type: 'success' })
        this.fetchItem()
      })
    },
    deleteItem () {
      activities.delete(this.itemUid, this.source).then(() => {
        bus.$emit('notification', { msg: this.$t(`ActivitiesTable.delete_${this.source}_success`), type: 'success' })
        this.$router.push({ name: 'Activities', params: { tab: this.source } })
      })
    },
    approveItem () {
      activities.approve(this.itemUid, this.source).then(() => {
        bus.$emit('notification', { msg: this.$t(`ActivitiesTable.approve_${this.source}_success`), type: 'success' })
        this.fetchItem()
      })
    },
    newItemVersion () {
      activities.newVersion(this.itemUid, this.source).then(() => {
        bus.$emit('notification', { msg: this.$t('_global.new_version_success'), type: 'success' })
        this.fetchItem()
      })
    },
    async openHistory () {
      const resp = await activities.getVersions(this.source, this.itemUid)
      this.historyItems = this.transformItems(resp.data)
      this.showHistory = true
    },
    closeHistory () {
      this.showHistory = false
    },
    transformItems (items) {
      const result = []
      for (const item of items) {
        if (item.activity_groupings.length > 0) {
          this.transformFunc(item)
          result.push(item)
        }
      }
      return result
    },
    downloadYamlContent () {
      exportLoader.downloadFile(this.yamlVersion, 'application/yaml', 'overview.yml')
    },
    downloadCosmosContent () {
      exportLoader.downloadFile(this.cosmosVersion, 'application/yaml', 'COSMoS-overview.yml')
    }
  },
  mounted () {
    this.fetchItem()
  }
}
</script>
